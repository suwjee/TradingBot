#!/usr/bin/env bash
set -euo pipefail
W=/mnt/data/V9_work
O="$W/golden/github_engine_commit_01d54ecf/engine"
N="$W/v81/engine"
X='/mnt/data/RAW FOREXCOM_XAUUSD 5S FROM 2026-10-08 19-35-30 TO 2026-10-09 18-14-25.json'
U='/mnt/data/RAW FXCM_USOIL 5S FROM 2026-10-22 19-25-25 TO 2026-10-23 19-25-25.json'
for which in XAU OIL; do
 if [[ "$which" = XAU ]];then raw="$X";from=1791475530;to=1791557065;else raw="$U";from=1792684525;to=1792770925;fi
 python -B "$W/v81/tests/check_e_internal_trace.py" --baseline "$O" --candidate "$N" --raw "$raw" --timeframe 30 --raw-timeframe 5 --from-time "$from" --to-time "$to" --direction both --out "$W/output/V9_E_INTERNAL_${which}.json"
 python -B "$W/v81/tests/check_native_stage_trace.py" --baseline "$O" --candidate "$N" --raw "$raw" --timeframe 30 --raw-timeframe 5 --from-time "$from" --to-time "$to" --direction both --out "$W/output/V9_NATIVE_STAGES_${which}.json"
done
echo DEEP_V9_PASS
