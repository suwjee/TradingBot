import importlib.util
from pathlib import Path
import sys
import unittest


MODULE_PATH = Path(__file__).with_name("trading_pipeline.py")
SPEC = importlib.util.spec_from_file_location("trading_pipeline_under_test", MODULE_PATH)
TRADING_PIPELINE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = TRADING_PIPELINE
SPEC.loader.exec_module(TRADING_PIPELINE)


class HumanReportSerializationTests(unittest.TestCase):
    def test_order_audit_category_uses_canonical_reaction_mode(self):
        category = TRADING_PIPELINE._report_category(
            "orderAudit",
            {
                "causes": [{"kind": "parent-stop"}],
                "reactionMode": "B",
            },
            "bullish",
        )

        self.assertEqual(category["label"], "Order_B")
        self.assertEqual(category["key"], "order:order_b")

    def test_order_audit_category_combines_merged_order_causes(self):
        category = TRADING_PIPELINE._report_category(
            "orderAudit",
            {
                "causes": [
                    {"kind": "parent-stop"},
                    {"kind": "reset-leg"},
                ],
                "reactionMode": "B",
            },
            "bullish",
        )

        self.assertEqual(category["label"], "Order_A | Order_B")
        self.assertEqual(category["key"], "order:order_a|order_b")


if __name__ == "__main__":
    unittest.main()
