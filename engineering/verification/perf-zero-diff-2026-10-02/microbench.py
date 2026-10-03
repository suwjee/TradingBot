import time
from decimal import Decimal

t0 = time.perf_counter()
s = Decimal("0")
for i in range(300000):
    s += Decimal(str(i % 1000)) * Decimal("1.001")
t1 = time.perf_counter()
print(f"decimal_loop_300k {t1-t0:.4f}s result={s}")

t0 = time.perf_counter()
class P:
    __slots__ = ("x", "y")
    def __init__(self):
        self.x = 1
        self.y = 2
p = P()
acc = 0
for i in range(500000):
    acc += p.x + p.y
t1 = time.perf_counter()
print(f"slot_access_500k {t1-t0:.4f}s acc={acc}")
