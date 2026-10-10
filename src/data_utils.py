"""CMS healthcare data loading and cleaning utilities."""
from __future__ import annotations
import pandas as pd
from pathlib import Path

COLUMN_ALIASES = {
    "Facility ID": "facility_id",
    "Facility Name": "facility_name",
    "State": "state",
    "City/Town": "city",
    "Condition": "condition",
    "Measure ID": "measure_id",
    "Measure Name": "measure_name",
    "Score": "score",
    "Sample": "sample",
    "Footnote": "footnote",
    "Start Date": "start_date",
    "End Date": "end_date",
}

def demo_data() -> pd.DataFrame:
    """Small synthetic demonstration data; not real hospital performance data."""
    rows = [
        ("DEMO001","Example Regional Hospital","MI","Detroit","Emergency Department","OP_18a",
         "Median emergency department time before leaving (minutes)",145,"380","", "2024-10-01","2025-09-30"),
        ("DEMO002","Example Community Hospital","MI","Canton","Emergency Department","OP_18a",
         "Median emergency department time before leaving (minutes)",172,"290","", "2024-10-01","2025-09-30"),
        ("DEMO003","Example University Hospital","OH","Toledo","Emergency Department","OP_18a",
         "Median emergency department time before leaving (minutes)",128,"410","", "2024-10-01","2025-09-30"),
        ("DEMO001","Example Regional Hospital","MI","Detroit","Preventive Care","IMM_3",
         "Influenza vaccination for selected surgery patients (percent)",94,"160","", "2024-10-01","2025-09-30"),
        ("DEMO002","Example Community Hospital","MI","Canton","Preventive Care","IMM_3",
         "Influenza vaccination for selected surgery patients (percent)",88,"120","", "2024-10-01","2025-09-30"),
        ("DEMO003","Example University Hospital","OH","Toledo","Preventive Care","IMM_3",
         "Influenza vaccination for selected surgery patients (percent)",96,"190","", "2024-10-01","2025-09-30"),
        ("DEMO004","Example Lakeside Hospital","MI","Ann Arbor","Emergency Department","OP_18a",
         "Median emergency department time before leaving (minutes)",156,"350","", "2024-10-01","2025-09-30"),
        ("DEMO004","Example Lakeside Hospital","MI","Ann Arbor","Preventive Care","IMM_3",
         "Influenza vaccination for selected surgery patients (percent)",91,"145","", "2024-10-01","2025-09-30"),
    ]
    cols = ["facility_id","facility_name","state","city","condition","measure_id",
            "measure_name","score","sample","footnote","start_date","end_date"]
    df = pd.DataFrame(rows, columns=cols)
    df.attrs["demo_data"] = True
    return df

def clean_cms_data(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize CMS-style headers and derive a numeric score where possible."""
    out = df.copy()
    rename = {}
    for c in out.columns:
        stripped = str(c).strip()
        rename[c] = COLUMN_ALIASES.get(stripped, stripped.lower().replace(" ", "_").replace("/", "_"))
    out = out.rename(columns=rename)
    for c in ["facility_id","facility_name","state","city","condition","measure_id","measure_name","score","sample","footnote"]:
        if c not in out.columns:
            out[c] = ""
    out["score_raw"] = out["score"].fillna("").astype(str).str.strip()
    out["score_numeric"] = pd.to_numeric(
        out["score_raw"].str.replace(",", "", regex=False).str.replace("%", "", regex=False),
        errors="coerce"
    )
    out["sample_numeric"] = pd.to_numeric(
        out["sample"].fillna("").astype(str).str.replace(",", "", regex=False),
        errors="coerce"
    )
    for c in ["facility_id","facility_name","state","city","condition","measure_id","measure_name"]:
        out[c] = out[c].fillna("").astype(str).str.strip()
    out["state"] = out["state"].str.upper()
    out["condition"] = out["condition"].replace("", "Unspecified")
    out["measure_name"] = out["measure_name"].replace("", "Unnamed measure")
    return out

def load_dataset(path: str | Path | None = None) -> tuple[pd.DataFrame, str]:
    """Load local CSV when available; otherwise return clearly labeled synthetic demo data."""
    if path:
        p = Path(path)
        if p.exists():
            return clean_cms_data(pd.read_csv(p, low_memory=False)), f"Local CMS CSV: {p.name}"
    default_path = Path(__file__).resolve().parents[1] / "data" / "cms_hospital_raw.csv"
    if default_path.exists():
        return clean_cms_data(pd.read_csv(default_path, low_memory=False)), f"Local CMS CSV: {default_path.name}"
    df = demo_data()
    return clean_cms_data(df), "Synthetic demo data (not actual CMS observations)"
