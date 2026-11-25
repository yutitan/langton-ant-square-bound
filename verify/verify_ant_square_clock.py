"""朗顿蚂蚁在正方形内的逃逸时间：S(n) <= 730*(9/5)**n。

本文件给出上界的证明和有限证书。直接用 Python 3.8+ 运行，无需第三方库。
取向东为 x 正向，向北为 y 正向。蚂蚁在白格右转，黑格左转，翻色后移动。
S(n) 对所有初始格色、内部起点和朝向取最大值，并计入走出棋盘的一步。

证明
----
把东、北航向记作 e=+1，西、南记作 e=-1。它是朝向对坐标和的增量。
把正负号写作 1 和 0。物理可行的一段符号串必须满足：固定起始轴之后，
横纵轴交替，各步位置与转向完全确定；同一格相邻两次被读时必须反向转弯。
函数 realizable 从两种起始轴分别检验此必要条件。下面 20 个串均不可行。

状态 u 取迄今航向串的最长后缀，使该后缀为某个禁串的非空真前缀。
0 和 1 都是真前缀，故初态就是首个航向位。追加位后用相同规则取后缀。
只需检查 u 加新位：更长的匹配若存在，删除新位就会违反 u 的最长性。
因任何真实轨迹均不出现禁串，所有实际转移都包含在证书中。

令 r=9/5，s(x,y)=x+y-(n-1)，棋盘坐标从 0 到 n-1。设 eta 在竖向
航向取 +1，在横向取 -1；chi(q)=(-1)**(x+y)；sigma=eta*chi(p)，其中
p 是头所在格。每步同时翻转 eta 和 chi(p)，故 sigma 沿轨迹恒定。
用 B 表示盘内黑格集合，定义

  F_+ = -sigma * sum(chi(q)*r**s(q) for q in B) + r**s(p)*g(u).

设旧、新航向符号为 e、t。白格记 delta=+1（右转），黑格记 delta=-1。
八种情形均有 eta*delta=e*t。翻色仅改变当前格，故场项变化为
-e*t*r**s(p)。新位置的 s 为旧 s 加 t。一步的势增量除以 r**s(p) 恰为

  -e*t + r**t*g(v) - g(u).

程序从下列整数恢复 g，并逐条证明上式至少为 1/100，同时 |g|<4。
将所有航向符号反号，并以 -s 取代 s，得 F_-。航向反号相当于平面
转 180 度，所得符号串也可行，且 e*t 不变。F=F_+ + F_- 的增量
至少为 (r**s + r**(-s))/100 >= 1/50。

固定 sigma 时，F 的黑格项取值范围的长度至多为所有格权的绝对值之和。
用 r**s 在两个坐标方向分别求和，正负指数项由对称性相等，得到

  sum(r**s(q) + r**(-s(q))) = 2*r**(n-1)*(sum(r**(-j), j=0,...,n-1))**2
                            <= (81/8)*r**(n-1).

两项头部修正之和的绝对值至多为 8*r**(n-1)，其取值范围长度至多
16*r**(n-1)。因此 F 的总范围长度至多为 (209/8)*r**(n-1)。若首次
出界需要 T 步，前 T-1 步的首末均在棋盘内。累加增量得

  T <= 1 + (5225/4)*r**(n-1) <= 730*r**n     (n>=1).

同一不等式亦排除永不逃逸。有限核验涵盖所有尺寸和所有染色所需的
局部不等式；此处没有对 n 做统计外推。

背景：Etse, MFCS 2026, https://doi.org/10.4230/LIPIcs.MFCS.2026.49 。
Ke 的对角线势函数：https://www.kehao.me/papers/langtons-ant-clock/ 。
本证书在头部修正中加入可行转向的有限记忆。
"""

from fractions import Fraction


BASE = Fraction(9, 5)
FORBIDDEN = """
000111 001100 010010 100110 101101 110011 111000
0010011100 0101100010 1000110110 1011100101 1101100011 1110110000 1111001000
00111011000100 11101110010000 11110010110000 11110110001000
111100101110010000 111101100010110000
""".split()

# Values of 10000*g, ordered by prefix length and then alphabetically.
COEFFICIENTS = [
    -22747, -18132, -22747, -18132, -22747, -4457, -22747, -18132, -22747,
    -22747, -15055, -25824, 5800, -18132, -22747, -4457, -22747, -15055,
    -22747, -18132, -2747, -22747, -19841, -7363, 12637, -4457, -22747,
    -25824, 3141, -18132, -2747, -2747, -4457, -22747, 5462, -2747, -5406,
    4945, -6508, 4945, 4022, -12149, -22747, 4774, -7970, -27534, 2001,
    27099, -2747, 7851, -5406, -22747, -9209, 3851, -31363, -14200, 7889,
    9560, 4090, 9978, 2613, -22747, -10611, -2747, -38255, -7363, -3602,
    -593, -10440, 159, -13099, -1516, -278, -22747, -2747, 4945, 11714,
    17130, -5824, -593, -5380, 1013, 2381, 17130, 10484, -15978, -13516,
    6939, 4022, 330, -10563, -6132, -5311, -10563, -17209, 4945, 7160,
    8637, -815, -11363, -696, -696, -19055, -19055, -16101, -16101, 4945, 7160,
]

EAST, NORTH, WEST, SOUTH = range(4)
VECTORS = ((1, 0), (0, 1), (-1, 0), (0, -1))


def sign(bit):
    return 1 if bit == "1" else -1


def realizable(word, first_horizontal):
    """Replay headings geometrically, assigning colors only on first visits."""
    headings = []
    horizontal = first_horizontal
    for bit in word:
        if horizontal:
            headings.append(EAST if bit == "1" else WEST)
        else:
            headings.append(NORTH if bit == "1" else SOUTH)
        horizontal = not horizontal
    colors = {}
    x = y = 0
    for before, after in zip(headings, headings[1:]):
        is_black = (after - before) % 4 == 1  # Counterclockwise = left.
        if (x, y) in colors and colors[x, y] != is_black:
            return False
        colors[x, y] = not is_black
        dx, dy = VECTORS[after]
        x += dx
        y += dy
    return True


def checked_clock():
    for word in FORBIDDEN:
        if any(realizable(word, axis) for axis in (False, True)):
            raise ValueError(f"Possible trajectory declared forbidden: {word}")

    prefixes = {word[:k] for word in FORBIDDEN for k in range(1, len(word))}
    states = sorted(prefixes, key=lambda s: (len(s), s))
    if len(states) != len(COEFFICIENTS) or not {"0", "1"} <= prefixes:
        raise ValueError("Incomplete state table")
    g = dict(zip(states, (Fraction(i, 10000) for i in COEFFICIENTS)))
    magnitude = max(abs(value) for value in g.values())
    if magnitude >= 4:
        raise ValueError("Head correction exceeds claimed magnitude")
    edges = {}
    gains = []
    for state in states:
        for bit in "01":
            extended = state + bit
            if any(extended.endswith(w) for w in FORBIDDEN):
                continue
            dest = max((u for u in states if extended.endswith(u)), key=len)
            old, new = sign(state[-1]), sign(bit)
            gain = -old * new + BASE**new * g[dest] - g[state]
            if gain < Fraction(1, 100):
                raise ValueError(f"Small gain at {state} + {bit}: {gain}")
            edges[state, bit] = dest
            gains.append(gain)
    print(f"Forbidden words: {len(FORBIDDEN)}; states: {len(states)}; edges: {len(edges)}")
    print(f"Minimum normalized gain: {min(gains)}; max abs(g): {magnitude}")
    return g, edges


def check_physical_signs():
    for h in range(4):
        old = sum(VECTORS[h])
        axis = 1 if h in (NORTH, SOUTH) else -1
        for is_black in (False, True):
            delta = -1 if is_black else 1
            new_h = (h - delta) % 4
            if delta * axis != old * sum(VECTORS[new_h]):
                raise ValueError("Field increment has wrong sign")
    range_factor = 2 / (1 - 1/BASE)**2 + 16
    if range_factor != Fraction(209, 8) or (1 + 50*range_factor) > 730*BASE:
        raise ValueError("Incorrect range or final constant")


if __name__ == "__main__":
    checked_clock()
    check_physical_signs()
    print("PASS: S(n) <= 730*(9/5)^n for every positive n, by the range proof above.")
