from pathlib import Path
import hashlib
import re

src = Path("engine/pipeline/order_audit_engine.py").read_bytes()
sha = hashlib.sha256(src).hexdigest()
needle = "pipeline/order_audit_engine.py` | Order / OrderAudit | `"
for name in [
    "TradingBot_Bullish_Algorithm_Reference_V5.4.21_Source_Synchronized.md",
    "TradingBot_Bearish_Algorithm_Reference_V5.4.21_Source_Synchronized.md",
]:
    text = Path("engine/algorithms", name).read_text(encoding="utf-8")
    i = text.find(needle)
    print(name)
    if i < 0:
        print("  MANIFEST MISSING")
        continue
    line_start = text.rfind("\n", 0, i) + 1
    line_end = text.find("\n", i)
    print("  row:", text[line_start:line_end])
    print("  sha in row:", sha in text[line_start:line_end])
