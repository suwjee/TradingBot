"""Negative controls for the explicit-notification prototype (no runtime integration)."""
from datetime import datetime,timedelta
from decimal import Decimal
from types import SimpleNamespace
from pathlib import Path
import hashlib,sys,pytest
from v10_carried_index_probe import ExplicitRowIndex,SHA

def test_missing_notification_is_not_safe_for_runtime():
    # Exact reference function from frozen source; caller supplies the path in pytest environment.
    import os
    root=os.getenv('TRADINGBOT_V81_ENGINE')
    if not root:pytest.skip('Requires isolated pinned V8.1 source; never import product HEAD')
    source=Path(root)/'pipeline/order_audit_engine.py'
    assert hashlib.sha256(source.read_bytes()).hexdigest()==SHA
    sys.path.insert(0,str(source.parent.resolve()))
    try:
        from order_audit_engine import OrderAuditEngineMixin
        assert hashlib.sha256(Path(sys.modules['order_audit_engine'].__file__).read_bytes()).hexdigest()==SHA
        validate=lambda rows:OrderAuditEngineMixin._validated_carried_creation_index(None,rows)
        t=datetime(2026,1,1); t2=t+timedelta(seconds=5)
        row=dict(reaction_number=1,reaction=SimpleNamespace(first_idx=0,break_idx=1),confirmation_time=t,stop_level=Decimal('12.3400'),stop_source_index=0,stop_source_time=t,stop_cross=(0,t,t2),causes={('parent-stop','E1','red',t,t)},order_b_causes=[])
        ledger={(0,1):row}; idx=ExplicitRowIndex(ledger,validate)
        assert idx.index==validate([row])
        row['causes'].clear()
        row['causes'].add(('parent-stop','E1','red',t2,t))
        # This is a deliberately demonstrated limitation, not a runtime pass.
        assert idx.index!=validate([row])
        idx.notify((0,1),'replace')
        assert idx.index==validate([row])
        with pytest.raises(ValueError):idx.notify((9,10),'replace')
        with pytest.raises(ValueError):idx.notify((0,1),'append')
    finally:
        sys.path.pop(0)
