from __future__ import annotations

import pytest
from typer.testing import CliRunner

from python_mastery_portfolio.cli import app
from python_mastery_portfolio.vin import (
    compute_check_digit,
    is_valid_vin,
    normalize_vin,
)


def test_normalize_vin() -> None:
    assert normalize_vin(" 1hgcm82633a004352 ") == "1HGCM82633A004352"


def test_compute_check_digit_known() -> None:
    # Known valid VIN
    vin = "1HGCM82633A004352"
    assert compute_check_digit(vin) == vin[8]


@pytest.mark.parametrize(
    "vin,valid",
    [
        ("1HGCM82633A004352", True),
        ("1hgcm82633a004352", True),  # lowercased ok after normalization
        ("1HGCM82633A004353", False),  # wrong check digit
        ("1HGCM82633A00435", False),  # too short
        ("1HGCM82633A0043520", False),  # too long
        ("1HGCM82633I004352", False),  # illegal letter I
    ],
)
def test_is_valid_vin(vin: str, valid: bool) -> None:
    assert is_valid_vin(vin) is valid


def test_cli_vin_validate_and_check() -> None:
    runner = CliRunner()
    vin = "1HGCM82633A004352"
    res1 = runner.invoke(app, ["vin-validate", vin])
    assert res1.exit_code == 0
    assert res1.output.strip() == "valid"

    res2 = runner.invoke(app, ["vin-check", vin])
    assert res2.exit_code == 0
    assert res2.output.strip() == vin[8]
