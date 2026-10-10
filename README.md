# Adaptive Healthcare Analytics

A Streamlit educational prototype for exploring CMS Timely and Effective Care hospital measures, with role-aware dashboard recommendations and user-controlled accessibility settings.

## Features
- Hospital Administrator and Healthcare Data Analyst views.
- Accessibility controls for larger text, high contrast, and simplified presentation.
- Session-scoped interaction history and adaptive view recommendations.
- CMS CSV upload and local file support.
- Unit tests and screenshot evidence.

## Data source
CMS Timely and Effective Care - Hospital: https://data.cms.gov/provider-data/dataset/yv7e-xc69

If a local CMS CSV is not supplied, the application uses clearly labeled synthetic demo rows. These are examples only, not real hospital observations.

## Run locally (Windows PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

## Tests
```powershell
python -m unittest discover -s tests -v
```

## Privacy and limitations
The prototype uses public provider-level measures; interaction history remains in the current Streamlit session. It is not a clinical decision-support system. Compare scores only within the same measure and review CMS footnotes.

## AI assistance disclosure
ChatGPT assisted with project planning, code drafting, test design, documentation, and report drafting. The developer should run the application and tests and review all results before submission.
