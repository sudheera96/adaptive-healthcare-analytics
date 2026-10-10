import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from adaptation import recommend_views, choose_layout, log_interaction

class TestAdaptation(unittest.TestCase):
    def test_role_defaults_for_admin(self):
        self.assertEqual(recommend_views("Hospital Administrator")[0], "KPI summary")

    def test_role_defaults_for_analyst(self):
        self.assertEqual(recommend_views("Healthcare Data Analyst")[0], "Measure trends")

    def test_interaction_frequency_prioritized(self):
        recs = recommend_views("Hospital Administrator", ["Detailed data table"] * 3)
        self.assertEqual(recs[0], "Detailed data table")

    def test_simplified_layout_hides_table(self):
        layout = choose_layout("Healthcare Data Analyst", simplified=True)
        self.assertFalse(layout["show_table"])
        self.assertEqual(layout["columns"], 1)

    def test_history_is_bounded(self):
        result = log_interaction(["a", "b"], "c", max_items=2)
        self.assertEqual(result, ["b", "c"])

if __name__ == "__main__":
    unittest.main()
