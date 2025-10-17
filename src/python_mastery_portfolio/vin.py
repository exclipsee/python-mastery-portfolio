from __future__ import annotations

import re
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
    """Return VIN uppercased and stripped of spaces."""
    return vin.replace(" ", "").upper()


def compute_check_digit(vin: str) -> str:
    """Compute the ISO 3779 check digit (position 9).

    Returns "X" if result is 10, else a single digit string.
    Assumes vin has length 17 and contains allowed characters.
    """
    total = 0
    for i, ch in enumerate(vin):
        value = TRANSLITERATION[ch]
        total += value * WEIGHTS[i]
    remainder = total % 11
    return "X" if remainder == 10 else str(remainder)


def is_valid_vin(vin: str) -> bool:
    """Validate a VIN by length, charset, and check digit.

    The 9th character is the check digit which must match ISO 3779.
    """
    v = normalize_vin(vin)
    if len(v) != 17:
        return False
    if not _VIN_ALLOWED_RE.match(v):
        return False
    expected = compute_check_digit(v)
    return v[8] == expected
