#!/bin/bash
set -uo pipefail
while kill -0 "$(cat /mnt/data/V9_work/output/full_real_run.pid)" 2>/dev/null; do
  if [ "$(wc -l < /mnt/data/V9_work/output/full_real_run.log)" -ge 7 ]; then break; fi
  sleep 3
done
python -u /mnt/data/V9_work/tooling/run_synthetic.py > /mnt/data/V9_work/output/full_synthetic_run.log 2>&1
