from __future__ import annotations

from fastapi.testclient import TestClient

from python_mastery_portfolio.api import app


def test_ml_predict_endpoint() -> None:
    client = TestClient(app)
    rows = [[1.0, 2.0], [3.0, 4.0]]
    r = client.post("/ml/predict", json={"rows": rows})
    assert r.status_code == 200
    data = r.json()
    preds = data.get("predictions")
    assert isinstance(preds, list)
    assert len(preds) == len(rows)
    assert all(isinstance(p, float) for p in preds)


def test_ml_train_and_predict() -> None:
    client = TestClient(app)
    # Train a model with a simple pattern y = 2*x1 - x2
    x = [[1.0, 2.0], [2.0, 1.0], [3.0, 1.0], [4.0, 3.0]]
    y = [0.0, 3.0, 5.0, 5.0]
    r = client.post("/ml/train", json={"x": x, "y": y, "set_default": True})
    assert r.status_code == 200
    # Predict using the updated default model
    r2 = client.post("/ml/predict", json={"rows": [[5.0, 2.0]]})
    assert r2.status_code == 200
    pred = r2.json()["predictions"][0]
    assert isinstance(pred, float)
