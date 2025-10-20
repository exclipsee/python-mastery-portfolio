from __future__ import annotations

import json
import os
from collections.abc import Callable
from dataclasses import dataclass
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


st.title("Python Mastery Demo")
st.write("Call the FastAPI Fibonacci and VIN endpoints")
st.caption(f"Using API base URL: {API_URL}")


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

st.header("Fibonacci")
n = st.number_input("n", min_value=0, value=10, step=1)
if st.button("Compute Fibonacci"):
    data = _handle_request(requests.get, f"{API_URL}/fib/{n}")
    if data is not None:
        st.code(json.dumps(data, indent=2))

st.header("VIN Validate")
vin = st.text_input("VIN", "1HGCM82633A004352")
if st.button("Validate VIN"):
    data = _handle_request(requests.post, f"{API_URL}/vin/validate", json={"vin": vin})
    if data is not None:
        st.code(json.dumps(data, indent=2))

st.caption("Set API_URL in .streamlit/secrets.toml to point to a deployed API")

st.header("VIN Decode")
vin_dec = st.text_input("VIN to decode", "1HGCM82633A004352")
if st.button("Decode VIN"):
    data = _handle_request(requests.post, f"{API_URL}/vin/decode", json={"vin": vin_dec})
    if data is not None:
        # Show selected fields prominently
        cols = st.columns(4)
        cols[0].metric("Valid", str(data.get("valid")))
        cols[1].metric("WMI", data.get("wmi", ""))
        cols[2].metric("Brand", data.get("brand", ""))
        cols[3].metric("Year", str(data.get("model_year", "")))

        cdv = data.get("check_digit_valid")
        if cdv is False:
            st.warning(
                "Check digit did not validate. Some regions/manufacturers "
                "(including certain EU VINs) do not use ISO 3779 check digits "
                "consistently. The VIN can still be structurally valid."
            )
        cands = data.get("model_year_candidates") or []
        if not data.get("model_year") and cands:
            st.info(
                "Possible model years based on standard cycles: "
                + ", ".join(map(str, cands))
            )
        notes = data.get("notes") or []
        for n in notes:
            st.info(n)
        st.subheader("Full JSON")
        st.code(json.dumps(data, indent=2))
