from __future__ import annotations

from io import BytesIO

from fastapi.testclient import TestClient
from openpyxl import load_workbook

from python_mastery_portfolio.api import app


def test_excel_export_endpoint() -> None:
    client = TestClient(app)
    rows = [["Name", "Score"], ["Alice", "90"], ["Bob", "88"]]
    r = client.post("/excel/export", json={"rows": rows})
    assert r.status_code == 200
    assert (
        r.headers.get("content-type")
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert "attachment; filename=\"export.xlsx\"" in r.headers.get(
        "content-disposition", ""
    )
    # Load workbook from bytes and verify contents
    wb = load_workbook(BytesIO(r.content))
    ws = wb.active
    assert ws is not None, "Active worksheet should not be None"
    assert ws["A1"].value == "Name"
    assert ws["B2"].value == "90"
