"""Helpers for writing tabular data to Excel using openpyxl."""

from __future__ import annotations

from collections.abc import Iterable
from importlib import import_module
from pathlib import Path
from typing import Any, cast

# Dynamically import openpyxl to avoid static analysis errors when the
# optional dependency is not installed in the edit environment.
try:
    _openpyxl = import_module("openpyxl")
    Workbook = getattr(_openpyxl, "Workbook")
    styles = getattr(_openpyxl, "styles")
    Alignment = getattr(styles, "Alignment")
    Font = getattr(styles, "Font")
    Worksheet = getattr(getattr(_openpyxl, "worksheet"), "worksheet").Worksheet
except Exception:
    # Fallback definitions when import fails; write_rows_to_excel will raise
    Workbook = None  # type: ignore
    Alignment: Any = None
    Font: Any = None
    Worksheet = object


def write_rows_to_excel(rows: Iterable[Iterable[str]], output_path: str | Path) -> Path:
    """Write rows (iterable of iterables) to an Excel workbook.

    The first row is treated as a header and bolded. Column widths are
    estimated from the longest cell in each column. The output directory
    will be created if it does not exist.
    """
    if Workbook is None:
        raise ImportError("openpyxl is required for write_rows_to_excel; please install it (pip install openpyxl)")

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    wb = cast(Any, Workbook)()
    ws = cast(Worksheet, wb.active)
    ws.title = "Data"

    rows_iter = iter(rows)
    try:
        header = next(rows_iter)
    except StopIteration:
        wb.save(path)
        return path

    ws.append(list(header))
    for cell in ws[1]:
        if Font is not None:
            cell.font = Font(bold=True)
        if Alignment is not None:
            cell.alignment = Alignment(horizontal="center")

    for row in rows_iter:
        ws.append(list(row))

    for col in ws.columns:
        col_cells = list(col)
        if not col_cells:
            continue
        max_len = max(len(str(c.value)) if c.value is not None else 0 for c in col_cells)
        first = col_cells[0]
        letter = getattr(first, "column_letter", None)
        if letter is None:
            coord = getattr(first, "coordinate", "A1")
            letter = "".join(ch for ch in str(coord) if ch.isalpha()) or "A"
        ws.column_dimensions[letter].width = max(10, min(max_len + 2, 40))

    wb.save(path)
    return path
