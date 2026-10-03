from pathlib import Path
import hashlib

src = Path("engine/pipeline/order_audit_engine.py").read_text(encoding="utf-8")
src_b = src.encode("utf-8")
ref = Path(
    "engine/algorithms/TradingBot_Bullish_Algorithm_Reference_V5.4.21_Source_Synchronized.md"
).read_text(encoding="utf-8")
begin = "<!-- EXACT-SOURCE-BEGIN:pipeline/order_audit_engine.py -->"
end = "<!-- EXACT-SOURCE-END:pipeline/order_audit_engine.py -->"
b = ref.find(begin)
e = ref.find(end)
print("markers", b, e)
after = ref.find("\n", b) + 1
fence_end = ref.find("\n", after) + 1
close = ref.rfind("\n" + "````", fence_end, e)
# rfind('\n````') lands on the newline that belongs to the Source when the
# Source already ends with a newline; include it.
embedded = ref[fence_end : close + 1]
print("emb len", len(embedded.encode("utf-8")), "src len", len(src_b))
print("equal", embedded.encode("utf-8") == src_b)
print("equal_plus_nl", embedded.encode("utf-8") + b"\n" == src_b)
print("src sha", hashlib.sha256(src_b).hexdigest())
print("emb sha", hashlib.sha256(embedded.encode("utf-8")).hexdigest())
print("src tail", repr(src[-15:]))
print("emb tail", repr(embedded[-15:]))
