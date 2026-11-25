# Reproduce the limited verification

The migrated partial_reference.py and run_partial_checks.py are the original partial implementation and test runner. The additional prepare_oracle.py is a convenience script for reproducing the original isolated setup from a checked-out baseline. It is newly written and has not yet been executed against a complete checkout in this publication session.

Use a fresh report destination, the exact seven external RAW files identified in Audit/Verification_Report.json, and a baseline checkout pinned to 466eb875070f02cd0dbfb105033422bbe2fd8c70. For example, from this directory:

```bash
python prepare_oracle.py --repo /path/to/pinned/TradingBot --output /tmp/tb-oracle
python run_partial_checks.py --oracle /tmp/tb-oracle --raw /path/to/raw --report /tmp/tb-new-report.json
```

Confirm the new report contains all three expected seeds and all seven datasets, each with three timeframe results. Check all source and RAW hashes against the historical report. A PASS with missing input files is not acceptable; the original runner's completion rule alone does not guarantee the expected dataset inventory. Do not overwrite historical evidence. For clean-room implementation, exclude the oracle, source and audit symbol mapping. Full indicator and Live/Batch differential testing are separate, outstanding acceptance gates. No production code has been replaced.
