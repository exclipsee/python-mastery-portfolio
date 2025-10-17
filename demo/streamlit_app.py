from __future__ import annotations

import json
from dataclasses import dataclass

import requests
import streamlit as st

API_URL = st.secrets.get("API_URL", "http://localhost:8000")


@dataclass
class FibResult:
    n: int
    value: int


st.title("Python Mastery Demo")
st.write("Call the FastAPI Fibonacci and VIN endpoints")

st.header("Fibonacci")
n = st.number_input("n", min_value=0, value=10, step=1)
if st.button("Compute Fibonacci"):
    r = requests.get(f"{API_URL}/fib/{n}")
    st.code(json.dumps(r.json(), indent=2))

st.header("VIN Validate")
vin = st.text_input("VIN", "1HGCM82633A004352")
if st.button("Validate VIN"):
    r = requests.post(f"{API_URL}/vin/validate", json={"vin": vin})
    st.code(json.dumps(r.json(), indent=2))

st.caption("Set API_URL in .streamlit/secrets.toml to point to a deployed API")
