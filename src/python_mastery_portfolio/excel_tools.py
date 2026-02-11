from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import cast

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.worksheet.worksheet import Worksheet


def write_rows_to_excel(rows: Iterable[Iterable[str]], output_path: str | Path) -> Path:
    path = Path(output_path)
    wb = Workbook()
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
        cell.font = Font(bold=True)
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
