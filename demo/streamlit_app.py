from __future__ import annotations

import io
import json
import os
from collections.abc import Callable
from dataclasses import asdict, dataclass
from typing import Any

import requests
import streamlit as st


def _resolve_api_url() -> str:
    """Return API base URL using env > secrets > default.

    Avoids crashing when no secrets.toml exists by guarding access to st.secrets.
    """
    # Highest precedence: environment variable
    env_url = os.getenv("API_URL")
    if env_url:
        return env_url
    # Next: Streamlit secrets (guarded)
    try:
        secrets_url = st.secrets.get("API_URL")  # type: ignore[assignment]
    except Exception:
        secrets_url = None
    if secrets_url:
        return str(secrets_url)
    # Fallback default for local dev
    return "http://localhost:8000"


API_URL = _resolve_api_url()


@dataclass
class FibResult:
    n: int
    value: int


# Try to import local VIN helpers for offline/demo fallback
try:
    from python_mastery_portfolio.vin import decode_vin, is_valid_vin  # type: ignore
except Exception:
    decode_vin = None  # type: ignore
    is_valid_vin = None  # type: ignore


st.set_page_config(page_title="Python Mastery Demo", layout="wide")
st.title("Python Mastery Demo")
st.write(
    "Call the FastAPI Fibonacci and VIN endpoints — or use local fallbacks for an offline demo."
)
st.caption(f"Using API base URL: {API_URL}")

# Sidebar controls
with st.sidebar:
    st.header("Demo Controls")
    use_local = st.checkbox("Use local fallback (no API)", value=True)
    st.markdown("---")
    st.markdown("**Sample data**")
    sample_vin = st.selectbox(
        "Example VIN",
        (
            "1HGCM82633A004352",
            "JHMFA16586S000000",
            "WVWZZZ1JZXW000000",
        ),
    )
    sample_csv = st.selectbox("Example CSV", ("Small scores", "Products sample", "Empty"))
    st.markdown("---")
    st.write("Project: python-mastery-portfolio")


def _handle_request(
    func: Callable[..., requests.Response], url: str, **kwargs: Any
) -> dict[str, Any] | None:
    """Perform a requests call and safely return JSON or display errors.

    Returns parsed JSON on success, otherwise shows an error in the UI and returns None.
    """
    try:
        r = func(url, timeout=10, **kwargs)
    except requests.RequestException as e:
        st.error(f"Request failed: {e}")
        return None
    # Non-2xx
    if not (200 <= r.status_code < 300):
        # Try to extract JSON error; fall back to text
        try:
            body = r.json()
        except Exception:
            body = r.text
        st.error(f"HTTP {r.status_code} calling {url}: {body}")
        return None
    # Parse JSON
    try:
        return r.json()
    except Exception as e:  # noqa: BLE001
        st.error(f"Invalid JSON response from {url}: {e}")
        return None


def _download_request(
    func: Callable[..., requests.Response], url: str, **kwargs: Any
) -> bytes | None:
    """Perform a requests call that expects binary content.

    Shows a UI error on failure and returns None.
    """
    try:
        r = func(url, timeout=20, **kwargs)
    except requests.RequestException as e:
        st.error(f"Request failed: {e}")
        return None
    if not (200 <= r.status_code < 300):
        st.error(f"HTTP {r.status_code} calling {url}")
        return None
    return r.content


def _local_fib(n: int) -> dict[str, int]:
    """Compute Fibonacci locally as a fallback for demo purposes."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return {"n": n, "value": a}


def _local_excel_bytes(rows: list[list[str]]) -> bytes:
    """Return CSV bytes for download as a lightweight local fallback.

    This keeps the demo dependency-free while still allowing a file download.
    """
    sio = io.StringIO()
    for r in rows:
        sio.write(",".join(map(str, r)) + "\n")
    return sio.getvalue().encode("utf-8")


st.header("Fibonacci")
col_left, col_right = st.columns([1, 2])
with col_left:
    n = st.number_input("n", min_value=0, value=10, step=1)
    if st.button("Compute Fibonacci", key="fib_compute"):
        if use_local:
            data = _local_fib(int(n))
        else:
            data = _handle_request(requests.get, f"{API_URL}/fib/{n}")
        if data is not None:
            st.success(f"F({data.get('n')}) = {data.get('value')}")
            with st.expander("Full JSON"):
                st.code(json.dumps(data, indent=2))


with col_right:
    st.markdown("**Quick notes**")
    st.write(
        "This demo computes Fibonacci either by calling the project's API or using a local fallback. "
        "Use the sidebar to toggle the behavior and select sample data."
    )


st.header("VIN Validate & Decode")
vin_default = sample_vin or "1HGCM82633A004352"
vin = st.text_input("VIN", vin_default)
col_v1, col_v2 = st.columns(2)
with col_v1:
    if st.button("Validate VIN", key="vin_validate"):
        if use_local and is_valid_vin is not None:
            valid = is_valid_vin(vin)
            st.write("Valid:" , valid)
            st.code(json.dumps({"vin": vin, "valid": valid}, indent=2))
        else:
            data = _handle_request(requests.post, f"{API_URL}/vin/validate", json={"vin": vin})
            if data is not None:
                st.code(json.dumps(data, indent=2))

with col_v2:
    if st.button("Decode VIN", key="vin_decode"):
        if use_local and decode_vin is not None:
            dec = decode_vin(vin)
            # dataclass -> dict
            try:
                decd = asdict(dec)
            except Exception:
                # Fallback to __dict__ if asdict not applicable
                decd = getattr(dec, "__dict__", {})
            cols = st.columns(4)
            cols[0].metric("Valid", str(decd.get("valid")))
            cols[1].metric("WMI", decd.get("wmi", ""))
            cols[2].metric("Brand", decd.get("brand", ""))
            cols[3].metric("Year", str(decd.get("model_year", "")))
            with st.expander("Full JSON"):
                st.code(json.dumps(decd, indent=2))
        else:
            data = _handle_request(requests.post, f"{API_URL}/vin/decode", json={"vin": vin})
            if data is not None:
                cols = st.columns(4)
                cols[0].metric("Valid", str(data.get("valid")))
                cols[1].metric("WMI", data.get("wmi", ""))
                cols[2].metric("Brand", data.get("brand", ""))
                cols[3].metric("Year", str(data.get("model_year", "")))
                with st.expander("Full JSON"):
                    st.code(json.dumps(data, indent=2))


st.header("Export to Excel (lightweight)")
st.write("Paste CSV data (comma-separated) or small table. We'll generate a downloadable file.")
if sample_csv == "Small scores":
    default_csv = "Name,Score\nAlice,95\nBob,90"
elif sample_csv == "Products sample":
    default_csv = "Product,Price,Stock\nWidget,19.99,10\nGadget,29.99,5"
else:
    default_csv = ""

csv_text = st.text_area("CSV input", default_csv, height=140)
col1, col2 = st.columns([1, 1])
download_fname = col1.text_input("File name", value="export.csv")
delimiter = col2.text_input("Delimiter", value=",")

if st.button("Generate File", key="gen_file"):
    # Parse CSV text into rows of strings
    rows: list[list[str]] = []
    for line in csv_text.splitlines():
        if not line.strip():
            continue
        rows.append([c.strip() for c in line.split(delimiter)])
    if not rows:
        st.warning("No rows to export.")
    else:
        if use_local:
            data = _local_excel_bytes(rows)
            mime = "text/csv"
        else:
            data = _download_request(
                requests.post, f"{API_URL}/excel/export", json={"rows": rows}
            )
            mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        if data is not None:
            st.download_button(
                label="Download file",
                data=data,
                file_name=download_fname or "export.csv",
                mime=mime,
            )


st.header("Real-Time System Monitoring")
st.write("Live system metrics from the API server via WebSocket (coming soon).")

# Simple monitoring section with basic metrics display
if st.button("Get Current WebSocket Connections", key="get_ws"):
    try:
        if use_local:
            st.info("Local demo: start the API to view live WebSocket metrics.")
        else:
            data = _handle_request(requests.get, f"{API_URL}/monitor/connections")
            if data is not None:
                st.metric("Active WebSocket Connections", data.get("active_connections", 0))
    except Exception as e:
        st.error(f"Failed to get connection count: {e}")

st.info(
    "📊 **Coming Soon**: Real-time charts with live CPU, memory, and disk usage "
    "via WebSocket streaming!"
)

st.write("""
To see the real-time monitoring in action:
1. Start the API server: `uvicorn python_mastery_portfolio.api:app --port 8000`
2. Open WebSocket connection to: `ws://localhost:8000/ws/metrics`
3. You'll receive JSON messages every 2 seconds with system metrics like:
   ```json
   {
     "type": "system_metrics",
     "data": {
       "timestamp": 1635724800.0,
       "cpu_percent": 25.5,
       "memory_percent": 60.0,
       "disk_usage_percent": 45.2,
       "active_connections": 3
     }
   }
   ```
""")
