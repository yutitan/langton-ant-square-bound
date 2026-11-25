# Provenance

本仓库是“大模型的小练习”系列第三篇，是一份可复现的个人 AI 使用记录，
不作优先权主张。

## 时间线

- 2026-11-25 至 2026-11-26：@yutitan 与 GPT 6.2 Astra（OpenAI Codex，模型
  gpt-6.2-astra）讨论朗顿蚂蚁在正方形棋盘上的逃逸时间，得到本记录的证明思路
  与两个验证程序。交付文件在磁盘上的时间戳为 2026-11-26 02:38（WSL）。
- 2026-11-26：DeepSeek Harness 对结果做独立审计（verify/audit.py），并整理
  本仓库、补写完整证明 note/note.md 与说明文档。

## 交付文件与改动

- verify/verify_ant_square_clock.py：原样复制自交付文件。
  SHA-256：3a82965639d2aed9de11aaa500598eb344184094e14c1b828c2dad5718c62323。
- verify/replay_ant_square_clock.py：交付文件只改了一行 import 路径。
  原行：sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "outputs"))
  改为：sys.path.insert(0, str(Path(__file__).resolve().parent))
  其余内容不变。原始文件 SHA-256：4ecca5ce818b5293bb780219879db2ffa7364000645be808c05925c375f1b9ff；
  仓库内文件 SHA-256：b7b9e7e0c1049b7bb001d7ce03815aa00a03f31208822d5cd6758551313ec379。
- verify/audit.py、verify/run_all.sh、note/note.md、README.md、PROVENANCE.md、
  CITATION.cff、.zenodo.json、literature/notes.md：为存档而新写。

## 独立审计

verify/audit.py 不导入主验证程序，独立完成：

- 从主程序源码抽取 20 个禁行片段与 108 个 g 值，用另一份判定逻辑重新确认
  每个禁行片段在两种首轴下都不可实现；对长度不超过 10 的片段另做全部染色的
  穷举交叉验证。
- 独立重推 108 个状态、171 条允许转移、最小归一化增益 109/10000、
  max|g| = 7651/2000。
- 独立验证恒等式 209/8、最终常数不等式（n = 1…400）与范围求和恒等式
  （n = 1…40）。
- 在 n = 4,5,6,8,10 的随机轨迹上逐步重算势函数，核验每步至少增加 1/50、
  增益分解恒等式，以及 F 的变程不超过 (209/8)·r^(n−1)。
- 对 n = 1,2,3 独立全枚举，得到 0/248/41376 次盘内转移和最大步数 1/6/17。

审计结论：未发现证明或程序的漏洞。输出见 verify/results.txt。

## 声明

- 证明未经同行评审；文献对照（Etse，MFCS 2026；Ke 的预印本）按题述引用，
  未独立核实。
- 不主张优先权：模型与工具足够强，相同或更强的结果可能已被他人独立得到。
