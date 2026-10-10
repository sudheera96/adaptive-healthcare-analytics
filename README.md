# Adaptive Healthcare Analytics

A Streamlit educational prototype that explores CMS Timely and Effective Care hospital measures and adapts its workspace based on role, user-selected accessibility preferences, and in-session interaction history.

## Features
- Role-aware defaults for hospital administrators and healthcare data analysts.
- User-controlled larger text, high contrast, and simplified layout.
- Explainable content-based view recommendations using TF-IDF, cosine similarity, role context, and repeated view selections.
- CMS CSV upload support and local CSV loading.
- Numeric-score cleaning, filters, charts, detailed table, and filtered CSV download.
- Synthetic demo data fallback clearly labeled as synthetic.
- Unit tests for cleaning and adaptive recommendation logic.

## Data source
Centers for Medicare & Medicaid Services (CMS), *Timely and Effective Care - Hospital*, dataset identifier `yv7e-xc69`:
https://data.cms.gov/provider-data/dataset/yv7e-xc69

Scores may be numeric, categorical, or unavailable. Do not compare different measures as if they share a unit or direction.

## Quick start (Windows PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

## Use the full CMS dataset
Place the downloaded CSV at `data/cms_hospital_raw.csv`, or upload a CSV from the sidebar. Do not commit a large data file unless the course requires it and licensing/privacy review permits it. If the full CSV is absent, the app uses synthetic demo rows; those rows are examples only, not actual hospital performance.

## Run tests
```powershell
python -m unittest discover -s tests -v
```

## Adaptation design
The recommendation component is a lightweight content-based model: TF-IDF vectors represent descriptions of available views, cosine similarity compares a profile built from the selected role and viewed topics with candidate views, and interaction frequency plus role defaults influence the ranking. This is not a generative AI system or a clinically validated model. Accessibility settings are user-directed, and the user can manually choose any available view. The simplified layout removes the densest detailed-table view from the view selector.

## Privacy and safety
This prototype uses public provider-level data and does not require patient-level data. It does not send interaction history to an external AI service or persist it beyond the Streamlit session. It is not a clinical decision-support system and must not be used to make clinical decisions.

## AI assistance disclosure
ChatGPT assisted with planning, code drafting, test design, project documentation, and report drafting. The developer should run the application, review all code, execute tests, and revise the report to reflect observed behavior before submission.

## Screenshots of the running application
The screenshots below show the local app with synthetic demo data. The example values are illustrative and are not actual CMS hospital observations.

### 1. Administrator dashboard — default view
![Administrator dashboard default view](screenshots/01_admin_default_dashboard.jpg)

### 2. Accessibility — high-contrast mode
![Accessibility high-contrast mode](screenshots/02_accessibility_high_contrast.jpg)

### 3. Simplified layout setting
![Simplified layout setting](screenshots/03_simplified_layout.jpg)

### 4. Analyst role — detailed data table
![Analyst detailed data table](screenshots/04_analyst_detailed_table.jpg)

These screenshots document observed UI states; the simplified-view behavior was subsequently clarified in the code to hide the detailed-table option.

## Repository
https://github.com/sudheera96/adaptive-healthcare-analytics

## References
- CMS Provider Data Catalog: https://data.cms.gov/provider-data/dataset/yv7e-xc69
- Streamlit Session State documentation: https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state
- scikit-learn pairwise metrics documentation: https://scikit-learn.org/stable/modules/metrics.html
