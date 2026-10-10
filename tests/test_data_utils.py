import unittest
from pathlib import Path
import sys
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from data_utils import clean_cms_data, demo_data

class TestDataUtils(unittest.TestCase):
    def test_demo_data_is_labeled_synthetic(self):
        df = demo_data()
        self.assertTrue(df.attrs.get("demo_data", False))
        self.assertGreater(len(df), 0)

    def test_cleaning_handles_non_numeric_scores(self):
        raw = pd.DataFrame({
            "Facility ID": ["001", "002"],
            "Facility Name": ["Hospital A", "Hospital B"],
            "State": ["mi", "oh"],
            "Condition": ["Emergency Department", "Preventive Care"],
            "Measure Name": ["Measure 1", "Measure 2"],
            "Score": ["123", "Not Available"],
            "Sample": ["100", "Not Available"]
        })
        clean = clean_cms_data(raw)
        self.assertEqual(clean.loc[0, "state"], "MI")
        self.assertEqual(clean.loc[0, "score_numeric"], 123)
        self.assertTrue(pd.isna(clean.loc[1, "score_numeric"]))

if __name__ == "__main__":
    unittest.main()
