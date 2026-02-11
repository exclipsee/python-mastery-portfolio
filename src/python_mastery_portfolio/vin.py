from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final

# Transliteration map per ISO 3779 (letters to numbers)
TRANSLITERATION: Final[dict[str, int]] = {
    **{str(i): i for i in range(10)},
    "A": 1,
    "B": 2,
    "C": 3,
    "D": 4,
    "E": 5,
    "F": 6,
    "G": 7,
    "H": 8,
    # I is not allowed
    "J": 1,
    "K": 2,
    "L": 3,
    "M": 4,
    "N": 5,
    # O is not allowed
    "P": 7,
    # Q is not allowed
    "R": 9,
    "S": 2,
    "T": 3,
    "U": 4,
    "V": 5,
    "W": 6,
    "X": 7,
    "Y": 8,
    "Z": 9,
}

# Position weights per ISO 3779 for positions 1..17
WEIGHTS: Final[list[int]] = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]

_VIN_ALLOWED_RE = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$")  # Exclude I, O, Q


def normalize_vin(vin: str) -> str:
    return vin.replace(" ", "").upper()


def compute_check_digit(vin: str) -> str:
    total = 0
    for i, ch in enumerate(vin):
        value = TRANSLITERATION[ch]
        total += value * WEIGHTS[i]
    r = total % 11
    return "X" if r == 10 else str(r)


def is_valid_vin(vin: str) -> bool:
    v = normalize_vin(vin)
    if len(v) != 17 or not _VIN_ALLOWED_RE.match(v):
        return False
    return v[8] == compute_check_digit(v)


# --- VIN decoding helpers ---

_YEAR_LETTERS: Final[list[str]] = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "J",
    "K",
    "L",
    "M",
    "N",
    "P",
    "R",
    "S",
    "T",
    "V",
    "W",
    "X",
    "Y",
]


def get_model_year(code: str) -> int | None:
    if not code:
        return None
    c = code.upper()
    if c.isdigit() and c in {"1","2","3","4","5","6","7","8","9"}:
        return 2000 + int(c)
    if c in _YEAR_LETTERS:
        return 2010 + _YEAR_LETTERS.index(c)
    return None


def get_year_code(year: int) -> str | None:
    if 2001 <= year <= 2009:
        return str(year - 2000)
    if 2010 <= year <= 2030:
        return _YEAR_LETTERS[year - 2010]
    if 2031 <= year <= 2039:
        return str(year - 2030)
    if 1980 <= year <= 2000:
        return _YEAR_LETTERS[year - 1980]
    return None


_REGION_MAP: Final[dict[str, str]] = {
    # First character region overview (coarse)
    "1": "North America",
    "2": "North America",
    "3": "North America",
    "4": "North America",
    "5": "North America",
    "J": "Asia (Japan)",
    "K": "Asia (Korea)",
    "L": "Asia (China)",
    "M": "Asia (India)",
    "S": "Europe (UK)",
    "T": "Europe (Switzerland)",
    "V": "Europe (France/Spain)",
    "W": "Europe (Germany)",
    "Y": "Europe (Nordic)",
    "Z": "Europe (Italy)",
}

_WMI_BRANDS: Final[dict[str, str]] = {
    "1HG": "Honda USA",
    "1FA": "Ford USA",
    "JHM": "Honda Japan",
    "WVW": "Volkswagen Germany",
    "ZFA": "Fiat Italy",
    "ZAR": "Alfa Romeo Italy",
    "ZFF": "Ferrari Italy",
}


@dataclass(frozen=True)
class VinDecoded:
    vin: str
    valid: bool
    wmi: str
    vds: str
    vis: str
    check_digit: str
    check_digit_valid: bool | None
    model_year_code: str | None
    model_year: int | None
    model_year_candidates: list[int] | None
    plant_code: str | None
    serial_number: str | None
    region: str | None
    brand: str | None
    notes: list[str] | None


def decode_vin(vin: str) -> VinDecoded:
    v = normalize_vin(vin)
    format_ok = len(v) == 17 and bool(_VIN_ALLOWED_RE.match(v))
    check_digit_valid: bool | None = None
    if format_ok:
        try:
            check_digit_valid = v[8] == compute_check_digit(v)
        except Exception:
            check_digit_valid = None
    wmi = v[0:3] if len(v) >= 3 else ""
    vds = v[3:8] if len(v) >= 8 else ""
    check_digit = v[8] if len(v) >= 9 else ""
    model_year_code = v[9] if len(v) >= 10 else None
    model_year = get_model_year(model_year_code) if model_year_code else None

    def _candidates(code: str | None) -> list[int] | None:
        if not code:
            return None
        c = code.upper()
        if c in {"1","2","3","4","5","6","7","8","9"}:
            base = 2000 + int(c)
            return [base] + ([base + 30] if base <= 2009 else [])
        if c in _YEAR_LETTERS:
            idx = _YEAR_LETTERS.index(c)
            return [1980 + idx, 2010 + idx]
        return None

    my_cand = _candidates(model_year_code)
    plant_code = v[10] if len(v) >= 11 else None
    vis = v[9:17] if len(v) >= 17 else v[9:]
    serial_number = v[11:17] if len(v) >= 17 else None
    region = _REGION_MAP.get(v[0]) if v else None
    brand = _WMI_BRANDS.get(wmi) if wmi else None
    notes: list[str] | None = None
    if brand and brand.startswith("Fiat") and (model_year is None):
        notes = [
            "Model year not encoded in position 10 for some EU-market Fiat VINs; manual lookup required.",
        ]
    return VinDecoded(vin=v, valid=format_ok, wmi=wmi, vds=vds, vis=vis, check_digit=check_digit, check_digit_valid=check_digit_valid, model_year_code=model_year_code, model_year=model_year, model_year_candidates=my_cand, plant_code=plant_code, serial_number=serial_number, region=region, brand=brand, notes=notes)


def _ensure_allowed_chars(s: str, length: int, pad: str = "0") -> str:
    s_u = normalize_vin(s)
    s_u = re.sub(r"[^A-HJ-NPR-Z0-9]", pad, s_u)
    if len(s_u) < length:
        s_u = s_u + pad * (length - len(s_u))
    return s_u[:length]


def generate_vin(wmi: str, vds: str, year: int, plant_code: str, serial: str) -> str:
    """Generate a valid VIN from components by computing the check digit.

    - wmi: 3 chars
    - vds: 5 chars (positions 4-8)
    - year: e.g., 2003
    - plant_code: 1 char (position 11)
    - serial: 6 chars (positions 12-17)
    """
    wmi3 = _ensure_allowed_chars(wmi, 3, pad="A")
    vds5 = _ensure_allowed_chars(vds, 5, pad="A")
    yc = get_year_code(year)
    if yc is None:
        raise ValueError(f"Unsupported year: {year}")
    plant1 = _ensure_allowed_chars(plant_code, 1, pad="A")
    serial6 = _ensure_allowed_chars(serial, 6, pad="0")
    # placeholder 'X' at position 9 for computing the check digit
    partial = wmi3 + vds5 + "X" + yc + plant1 + serial6
    check = compute_check_digit(partial)
    return partial[:8] + check + partial[9:]
