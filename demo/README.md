# Demo: Streamlit app

Run `demo/streamlit_app.py` to explore CLI and API-backed features.

Quick start:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[demo]
streamlit run demo/streamlit_app.py
```

The demo works offline (local fallbacks) or can call the project's API.

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
