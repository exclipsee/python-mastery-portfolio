# Demo: Streamlit App

This folder contains a lightweight Streamlit demo (`streamlit_app.py`) that
demonstrates a few features from the project:

- Local Fibonacci computation and an API-backed fallback
- VIN validation and decoding (local fallback available)
- Lightweight CSV → downloadable file export
- (Planned) WebSocket-based system metrics

Quick start (local):

```powershell
# create and activate venv (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e .[demo]
streamlit run demo/streamlit_app.py
```

Notes
- The demo can operate fully offline using local fallbacks (no API required).
- To use the API-backed flows, start the FastAPI app in another terminal:

```powershell
uvicorn python_mastery_portfolio.api:app --reload
```

Feedback welcome — open an issue or PR to propose demo enhancements.
# Demo

This folder contains a Streamlit demo app (`streamlit_app.py`) that demonstrates
some of the project's features (Fibonacci, VIN validation, Excel export, and
monitoring). To run the demo locally:

```powershell
# from the repository root
python -m pip install -e .[demo]
streamlit run demo/streamlit_app.py
```

Use the sidebar controls in the app to toggle between local fallbacks and
calling the API server.
