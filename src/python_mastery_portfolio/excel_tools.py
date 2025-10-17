from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font


def write_rows_to_excel(rows: Iterable[Iterable[str]], output_path: str | Path) -> Path:
    """Write rows of strings to an Excel file with a simple header style.

    Args:
        rows: An iterable of rows, each a sequence of string values. The first row is treated
              as a header and styled bold.
        output_path: Target .xlsx file path.

    Returns:
        The path to the written Excel file.
    """
    path = Path(output_path)
    wb = Workbook()
    ws = wb.active
    ws.title = "Data"

    rows_iter = iter(rows)
    try:
        header = next(rows_iter)
    except StopIteration:
        # No data, create an empty sheet
        wb.save(path)
        return path

    ws.append(list(header))
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    for row in rows_iter:
        ws.append(list(row))

    # Auto-fit approximate widths
    for col in ws.columns:
        max_len = max(len(str(c.value)) if c.value is not None else 0 for c in col)
        ws.column_dimensions[col[0].column_letter].width = max(10, min(max_len + 2, 40))

    wb.save(path)
    return path
