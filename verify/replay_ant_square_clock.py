"""Cross-check the certificate by recomputing its global value on actual boards."""
from pathlib import Path
from fractions import Fraction
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_ant_square_clock import BASE, checked_clock


def replay(n, g):
    # Headings N,E,S,W in clockwise order.  Use the full history to identify
    # its suffix, independently of the certificate checker's transition table.
    vectors = ((0, 1), (1, 0), (0, -1), (-1, 0))
    cells = [(x, y) for x in range(n) for y in range(n)]
    checker = {q: (-1)**(q[0]+q[1]) for q in cells}
    weights = {q: BASE**(sum(q)-n+1) for q in cells}
    scale = 10000 * 45**(n-1)
    def integer(x):
        if x.denominator != 1:
            raise ValueError(f"Inexact value: {x}")
        return int(x)
    plus = {q: integer(scale*w/10000) for q,w in weights.items()}
    minus = {q: integer(scale/w/10000) for q,w in weights.items()}
    raw_g = {s: integer(v*10000) for s,v in g.items()}
    ordered = sorted(g,key=len,reverse=True)
    def state(history):
        return next(s for s in ordered if history.endswith(s))

    checked = 0
    observed_max = 0
    for layout in range(1 << len(cells)):
        black = {q for i,q in enumerate(cells) if (layout >> i)&1}
        for initial in cells:
            for start_heading in range(4):
                board = black.copy()
                q,h = initial,start_heading
                sig = checker[q] * (1 if h in (0,2) else -1)
                history = "1" if h in (0,1) else "0"
                opposite = "0" if history=="1" else "1"
                previous = None
                steps = 0
                while q in weights:
                    total = (-sig * 10000 * sum(checker[z]*(plus[z]+minus[z]) for z in board)
                             + plus[q]*raw_g[state(history)] + minus[q]*raw_g[state(opposite)])
                    if previous is not None:
                        if 50*(total-previous) < scale:
                            raise AssertionError((n,layout,initial,start_heading,steps))
                        checked += 1
                    previous = total
                    h = (h + (-1 if q in board else 1)) % 4
                    board.symmetric_difference_update([q])
                    dx,dy = vectors[h]
                    q = (q[0]+dx,q[1]+dy)
                    history += "1" if h in (0,1) else "0"
                    opposite += "0" if h in (0,1) else "1"
                    steps += 1
                observed_max=max(observed_max,steps)
    return checked, observed_max


if __name__ == "__main__":
    g,_=checked_clock()
    for n in range(1,4):
        print(n, replay(n,g))
