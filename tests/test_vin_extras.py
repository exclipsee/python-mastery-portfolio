from __future__ import annotations

from fastapi.testclient import TestClient

from python_mastery_portfolio.api import app
from python_mastery_portfolio.vin import (
    decode_vin,
    generate_vin,
    get_model_year,
    get_year_code,
    is_valid_vin,
)


def test_year_code_roundtrip() -> None:
    # Year codes repeat; ensure that the decoded year matches the same cycle or +/-30y
    for y in [1980, 1999, 2000, 2001, 2009, 2010, 2025, 2029, 2030, 2035, 2039]:
        code = get_year_code(y)
        assert code is not None
        back = get_model_year(code)
        assert back in {y, y - 30, y + 30}


def test_generate_and_validate_vin() -> None:
    vin = generate_vin("1HG", "CM826", 2003, "A", "004352")
    assert len(vin) == 17
    assert is_valid_vin(vin)
    dec = decode_vin(vin)
    assert dec.valid is True
    assert dec.wmi == "1HG"
    assert dec.model_year == 2003


def test_api_vin_decode_and_generate() -> None:
    client = TestClient(app)
    # Generate
    r = client.post(
        "/vin/generate",
        json={"wmi": "1HG", "vds": "CM826", "year": 2003, "plant_code": "A", "serial": "004352"},
    )
    assert r.status_code == 200
    vin = r.json()["vin"]
    assert is_valid_vin(vin)

    # Decode
    r2 = client.post("/vin/decode", json={"vin": vin})
    assert r2.status_code == 200
    data = r2.json()
    assert data["valid"] is True
    assert data["wmi"] == "1HG"
    assert data["model_year"] == 2003
