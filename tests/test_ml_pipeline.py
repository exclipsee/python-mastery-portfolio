from __future__ import annotations

from pathlib import Path

from python_mastery_portfolio.ml_pipeline import (
    add_bias_feature,
    load_model,
    predict,
    save_model,
    train_linear_regression,
)


def test_train_and_predict() -> None:
    x_data = [[1.0, 2.0], [2.0, 4.0], [3.0, 6.0]]
    y = [3.0, 6.0, 9.0]
    tm = train_linear_regression(x_data, y)
    preds = predict(tm, x_data)
    assert len(preds) == 3
    # should roughly match y
    assert all(abs(a - b) < 1e-6 for a, b in zip(preds, y, strict=True))


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    x = [[0.0, 1.0], [1.0, 2.0], [2.0, 3.0]]
    y = [1.0, 3.0, 5.0]
    tm = train_linear_regression(x, y)
    f = tmp_path / "model.joblib"
    save_model(tm, f)
    tm2 = load_model(f)
    preds = predict(tm2, x)
    assert len(preds) == len(x)


def test_add_bias_feature() -> None:
    rows = [[2.0, 3.0], [4.0, 5.0]]
    augmented = add_bias_feature(rows)
    assert augmented == [[1.0, 2.0, 3.0], [1.0, 4.0, 5.0]]