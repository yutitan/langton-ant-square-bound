#!/usr/bin/env bash
# 在仓库根目录运行：bash verify/run_all.sh
set -euo pipefail

echo "== verify_ant_square_clock.py"
python3 verify/verify_ant_square_clock.py
echo
echo "== replay_ant_square_clock.py"
python3 verify/replay_ant_square_clock.py
echo
echo "== audit.py"
python3 verify/audit.py
