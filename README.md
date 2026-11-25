# 大模型的小练习（三）：朗顿蚂蚁在 n×n 棋盘上的逃逸时间上界

**LLM Exercises III — an explicit escape-time bound for Langton's ant on n×n boards**

**Author:** [@yutitan](https://github.com/yutitan) · **Date:** 2026-11-26
· **Derived with:** GPT 6.2 Astra (OpenAI Codex, model gpt-6.2-astra),
independently verified with DeepSeek Harness — see [Provenance](#provenance)

> 本仓库是“大模型的小练习”系列的第三篇，是一份个人 AI 使用记录，不是论文，
> 不作优先权主张。系列第一篇：
> [Counterexamples to *Written on the Wall II* conjecture #138](https://github.com/yutitan/wowii-conjecture-138)
> — [DOI 10.5281/zenodo.24540807](https://doi.org/10.5281/zenodo.24540807)；
> 系列第二篇：
> [Exact escape time of Langton's ant on three-row boards](https://github.com/yutitan/langton-ant-three-rows)
> — [DOI 10.5281/zenodo.24540968](https://doi.org/10.5281/zenodo.24540968)。

> **Abstract (EN).** We record a computer-assisted proof that Langton's ant on
> any n×n board escapes within 730·(9/5)^n steps, uniformly over all initial
> colourings, starting cells and headings. The proof combines 20 forbidden
> heading fragments, a 108-state memory automaton, 171 exactly checked rational
> gain inequalities, and an analytic range bound. All claims are checked by the
> programs in this repository.

## 结果

朗顿蚂蚁：白格右转、黑格左转，翻转脚下格子，向前走一格。设 S(n) 为在
n×n 棋盘上，对所有初始染色、起点和朝向取最大值时，蚂蚁第一次走出棋盘
所需的最多步数（计入走出那一步）。本记录给出

    S(n) ≤ 730·(9/5)^n,    n ≥ 1.

n = 1, 2, 3 的精确值（全枚举）为 S(1) = 1, S(2) = 6, S(3) = 17。

作为对照：按题述，Etse（MFCS 2026）给出 (n+1)! 的上界，Ke 的预印本把它
降到 O(3^n)。在 n = 100 时，本记录给出 730·(9/5)^100 ≈ 2.458×10^28；
按题述中 Ke 的显式公式读出的约 1.12×10^48 相比，小约 4.6×10^19 倍。
（这两条文献对照本仓库没有独立复核，见 [文献笔记](literature/notes.md)。）

## 证明思路

1. **禁行片段。** 20 个局部不可实现的朝向片段（长度 6、10、14、18）。
   例如 111000：从朝东起画，六步的朝向依次是东、北、东、南、西、南，
   第四步回到起点；该格第一次要求右转、第二次要求左转，而颜色已被翻过，
   矛盾。任何初始棋盘都走不出这段路。
2. **记忆自动机。** 把历史压成“禁行片段的非空真前缀的最长后缀”，共 108 个
   状态、171 条允许转移。交付的程序对每条转移用一个有理数 g 值核验
   势函数的局部增益不等式。
3. **势函数。** 取 r = 9/5，s(q) = x + y − (n−1)，chi(q) = (−1)^(x+y)，
   sigma = eta·chi(p)（eta 在竖、横航向上分别取 +1、−1；sigma 沿轨迹不变）。
   令 B 为黑格集合、p 为头所在格、u 为记忆状态，
   F₊ = −sigma·Σ_{q∈B} chi(q)·r^s(q) + r^s(p)·g(u)。
   对 180° 旋转再取一份 F₋，则每走一步（首尾都在盘内）势函数至少增加
   (r^s(p) + r^−s(p))/100 ≥ 1/50。
4. **范围。** 固定 sigma 时，势函数的取值范围长度至多为
   (209/8)·(9/5)^(n−1)。
5. **结论。** 设 T 为逃逸步数，则 T−1 ≤ 50·(209/8)·(9/5)^(n−1)，即
   T ≤ 1 + (5225/4)·(9/5)^(n−1) ≤ 730·(9/5)^n（n ≥ 1）。

完整证明见 [note/note.md](note/note.md)。

## 验证

在仓库根目录运行：

    bash verify/run_all.sh

| 文件 | 作用 |
| --- | --- |
| [verify/verify_ant_square_clock.py](verify/verify_ant_square_clock.py) | 交付的主验证程序：20 个禁行片段、108 个状态、171 条转移的精确（有理数）核验 |
| [verify/replay_ant_square_clock.py](verify/replay_ant_square_clock.py) | 逐步重演：在 n ≤ 3 的全部棋盘（全部染色 × 起点 × 朝向）上直接重算势函数，核验 41,624 次盘内转移 |
| [verify/audit.py](verify/audit.py) | 本仓库新增的独立审计：不导入主程序，重推状态表与增益不等式、重推范围常数，并在 n = 4,5,6,8,10 的随机轨迹上复核 |
| [verify/results.txt](verify/results.txt) | 运行输出 |

主验证程序的输出应为：

    Forbidden words: 20; states: 108; edges: 171
    Minimum normalized gain: 109/10000; max abs(g): 7651/2000
    PASS: S(n) <= 730*(9/5)^n for every positive n, by the range proof above.

（replay 程序只把一行 import 路径从 ../outputs 改成同目录，其余与交付版一致；
原始文件的 SHA-256 见 [PROVENANCE.md](PROVENANCE.md)。）

## 本记录是什么，不是什么

- 由 GPT 6.2 Astra 在 2026-11-26 推导并给出程序；由 DeepSeek Harness 同日
  独立审计（重写验证逻辑，不导入被审计的代码）。
- 有限证书由程序做精确有理数核验；范围与常数部分是解析证明，[note](note/note.md)
  给出完整推导。
- 未经过同行评审；不作优先权主张。与 Etse、Ke 的文献对照仅按题述引用，
  未独立核实。
- 常数未优化：用本论证，727 也足够（见 note 第 6 节）。
- 开放问题：S(n) 是否被某个多项式控制？任意固定高度的长条是否有线性上界？

## Citation

    @software{yutitan_llm_exercises_iii,
      author  = {yutitan},
      title   = {大模型的小练习（三）：朗顿蚂蚁在 n×n 棋盘上的逃逸时间上界},
      year    = {2026},
      note    = {Series: 大模型的小练习 (LLM Exercises III); derived with GPT 6.2 Astra, independently verified with DeepSeek Harness},
      url     = {https://github.com/yutitan/langton-ant-square-bound}
    }

Zenodo 版本 DOI 在 release v1.0.0 归档后补入。

## Provenance

见 [PROVENANCE.md](PROVENANCE.md)：推导与验证的时间线、文件哈希与审计记录。
