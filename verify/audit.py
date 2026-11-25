"""Independent audit of verify_ant_square_clock.py.

Standalone (standard library only).  Re-derives the finite certificate and the
global constants from scratch, and replays the potential on random longer
trajectories, without importing or copying the verifier's logic.
"""
import ast
import itertools
import random
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / 'verify_ant_square_clock.py'

tree = ast.parse(SRC.read_text(encoding='utf-8'))
C = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        if node.targets[0].id in ('FORBIDDEN', 'COEFFICIENTS'):
            val = node.value
            if isinstance(val, ast.Call) and isinstance(val.func, ast.Attribute) and val.func.attr == 'split':
                C[node.targets[0].id] = ast.literal_eval(val.func.value)
            else:
                C[node.targets[0].id] = ast.literal_eval(val)
FORB = C['FORBIDDEN'].split()
COEF = C['COEFFICIENTS']
R = Fraction(9, 5)

VEC = {0: (1, 0), 1: (0, 1), 2: (-1, 0), 3: (0, -1)}  # 0=E,1=N,2=W,3=S (CCW)

def signh(h):
    return 1 if h in (0, 1) else -1

def etah(h):
    return 1 if h in (1, 3) else -1

def headings(word, first_horizontal):
    hs, horiz = [], first_horizontal
    for b in word:
        hs.append((0 if b == '1' else 2) if horiz else (1 if b == '1' else 3))
        horiz = not horiz
    return hs

def feasible(word, first_horizontal):
    """Fresh deterministic feasibility check: per-cell turns must alternate."""
    hs = headings(word, first_horizontal)
    x = y = 0
    visits = {}
    for i in range(len(hs) - 1):
        turn = (hs[i + 1] - hs[i]) % 4
        left = 1 if turn == 1 else 0
        prev = visits.get((x, y))
        if prev is None:
            visits[(x, y)] = (left, 1)
        else:
            left0, cnt = prev
            if left != (left0 + cnt) % 2:
                return False
            visits[(x, y)] = (left0, cnt + 1)
        dx, dy = VEC[hs[i + 1]]
        x += dx
        y += dy
    return True

def brute_realizable(word, first_horizontal):
    """Brute force over all colorings of the visited cells (small words only)."""
    hs = headings(word, first_horizontal)
    cells = []
    x = y = 0
    for i in range(len(hs) - 1):
        cells.append((x, y))
        dx, dy = VEC[hs[i + 1]]
        x += dx
        y += dy
    cells.append((x, y))
    distinct = sorted(set(cells))
    idx = {c: i for i, c in enumerate(distinct)}
    for mask in range(1 << len(distinct)):
        B = {c for c in distinct if (mask >> idx[c]) & 1}
        x = y = 0
        h = hs[0]
        ok = True
        for i in range(len(hs) - 1):
            black = (x, y) in B
            h = (h + 1) % 4 if black else (h - 1) % 4
            if h != hs[i + 1]:
                ok = False
                break
            if black:
                B.discard((x, y))
            else:
                B.add((x, y))
            dx, dy = VEC[h]
            x += dx
            y += dy
        if ok:
            return True
    return False

print('source:', SRC)
print('forbidden words:', len(FORB), 'lengths:', sorted({len(w) for w in FORB}))
assert len(FORB) == 20 and len(set(FORB)) == 20
for w in FORB:
    assert not feasible(w, True) and not feasible(w, False), w
    if len(w) <= 10:
        assert not brute_realizable(w, True) and not brute_realizable(w, False), w
print('forbidden words infeasible under both starting axes: OK (brute force validates lengths <= 10)')

prefixes = {w[:k] for w in FORB for k in range(1, len(w))}
assert all(p not in set(FORB) for p in prefixes)
states = sorted(prefixes, key=lambda s: (len(s), s))
assert len(states) == 108, len(states)
assert len(COEF) == len(states)
g = {s: Fraction(c, 10000) for s, c in zip(states, COEF)}
assert max(abs(v) for v in g.values()) == Fraction(7651, 2000)

edges = {}
gains = []
for u in states:
    for bit in '01':
        ext = u + bit
        if any(ext.endswith(w) for w in FORB):
            continue
        cand = [s for s in states if ext.endswith(s)]
        assert cand
        v = max(cand, key=len)
        e, t = (1 if u[-1] == '1' else -1), (1 if bit == '1' else -1)
        gain = -e * t + R ** t * g[v] - g[u]
        assert gain >= Fraction(1, 100), (u, bit, gain)
        edges[(u, bit)] = v
        gains.append(gain)
assert len(edges) == 171, len(edges)
assert min(gains) == Fraction(109, 10000), min(gains)
print('states: 108; allowed transitions: 171; min normalized gain:', min(gains), '; max |g|:', max(abs(v) for v in g.values()))

for h in range(4):
    for black in (0, 1):
        delta = -1 if black else 1
        h2 = (h - delta) % 4
        assert etah(h) * delta == signh(h) * signh(h2), (h, black)
print('physical sign relation eta*delta = e*t: OK for all 8 cases')

assert 2 / (1 - 1 / R) ** 2 + 16 == Fraction(209, 8)
for n in range(1, 401):
    assert 1 + Fraction(5225, 4) * R ** (n - 1) <= 730 * R ** n, n
for n in range(1, 41):
    tot = sum(R ** (x + y - (n - 1)) + R ** (-(x + y - (n - 1))) for x in range(n) for y in range(n))
    rhs = 2 * R ** (n - 1) * sum(R ** (-j) for j in range(n)) ** 2
    assert tot == rhs
    assert tot <= Fraction(81, 8) * R ** (n - 1)
print('constants: 209/8 identity OK; 1+(5225/4)r^(n-1) <= 730 r^n for n=1..400; range sum n=1..40: OK')

order = sorted(states, key=len, reverse=True)

def state(hist):
    for s in order:
        if hist.endswith(s):
            return s
    raise AssertionError('no state for history: ' + hist)

coef = {s: Fraction(c, 10000) for s, c in zip(states, COEF)}

def dynamic():
    total = 0
    min_slack = None
    for n in (4, 5, 6, 8, 10):
        M = 10000 * 9 ** (n - 1) * 5 ** (n - 1)
        def val(s):
            return 9 ** (n - 1 + s) * 5 ** (n - 1 - s)
        def W(s):
            return 10000 * val(s)
        for trial in range(20):
            random.seed(1000 * n + trial)
            bits = [random.getrandbits(1) for _ in range(n * n)]
            B = {(x, y) for x in range(n) for y in range(n) if bits[x * n + y]}
            x, y = random.randrange(n), random.randrange(n)
            h = random.randrange(4)
            hist = '1' if signh(h) == 1 else '0'
            opp = '0' if hist == '1' else '1'
            sig = etah(h) * ((-1) ** (x + y))
            def F(B, x, y, hist, opp):
                u, u2 = state(hist), state(opp)
                s = x + y - (n - 1)
                field = 0
                for (qx, qy) in B:
                    sq = qx + qy - (n - 1)
                    field += ((-1) ** (qx + qy)) * (W(sq) + W(-sq))
                return -sig * field + val(s) * COEF[states.index(u)] + val(-s) * COEF[states.index(u2)]
            prev = F(B, x, y, hist, opp)
            fmin = fmax = prev
            steps = 0
            while 0 <= x < n and 0 <= y < n and steps < 400:
                h_old = h
                black = (x, y) in B
                if black:
                    h = (h + 1) % 4
                    B.discard((x, y))
                else:
                    h = (h - 1) % 4
                    B.add((x, y))
                dx, dy = VEC[h]
                nx, ny = x + dx, y + dy
                nb = '1' if signh(h) == 1 else '0'
                nhist, nopp = hist + nb, opp + ('0' if nb == '1' else '1')
                u, v = state(hist), state(nhist)
                u2, v2 = state(opp), state(nopp)
                cb = '0' if nb == '1' else '1'
                assert edges[(u, nb)] == v
                assert edges[(u2, cb)] == v2
                if 0 <= nx < n and 0 <= ny < n:
                    newF = F(B, nx, ny, nhist, nopp)
                    d = newF - prev
                    assert 50 * d >= M, (n, trial, steps, d, M)
                    e, t = signh(h_old), signh(h)
                    gain = -e * t + R ** t * g[v] - g[u]
                    gainr = -e * t + R ** (-t) * g[v2] - g[u2]
                    sp = x + y - (n - 1)
                    assert d == W(sp) * gain + W(-sp) * gainr
                    assert etah(h) * ((-1) ** (nx + ny)) == sig
                    prev = newF
                    fmin = min(fmin, newF)
                    fmax = max(fmax, newF)
                    total += 1
                    slack = 50 * d - M
                    min_slack = slack if min_slack is None else min(min_slack, slack)
                hist, opp = nhist, nopp
                x, y = nx, ny
                steps += 1
            assert fmax - fmin <= 261250 * 81 ** (n - 1), (n, trial)
    return total, min_slack

total, min_slack = dynamic()
print('dynamic replay on random n=4,5,6,8,10 trajectories: %d in-board steps OK' % total)
print('  min (50*dF - M):', min_slack, '(>= 0)')
print('  observed F range stays inside 209/8*r^(n-1) bound: OK')

def sim_steps(n, mask, start, h0):
    B = {(i % n, i // n) for i in range(n * n) if (mask >> i) & 1}
    x, y = start
    h = h0
    steps = 0
    while 0 <= x < n and 0 <= y < n:
        steps += 1
        black = (x, y) in B
        if black:
            h = (h + 1) % 4
            B.discard((x, y))
        else:
            h = (h - 1) % 4
            B.add((x, y))
        dx, dy = VEC[h]
        x += dx
        y += dy
    return steps

for n, total_exp, max_exp in ((1, 0, 1), (2, 248, 6), (3, 41376, 17)):
    tot = 0
    mx = 0
    for mask in range(1 << (n * n)):
        for sx in range(n):
            for sy in range(n):
                for h in range(4):
                    st = sim_steps(n, mask, (sx, sy), h)
                    tot += st - 1
                    if st > mx:
                        mx = st
    assert (tot, mx) == (total_exp, max_exp), (n, tot, mx)
    assert mx <= 730 * R ** n
    print('exhaustive n=%d: in-board transitions %d, max steps %d (<= 730*(9/5)^n: %s)' % (n, tot, mx, mx <= 730 * R ** n))

print('PASS: independent audit of the S(n) <= 730*(9/5)^n certificate')
