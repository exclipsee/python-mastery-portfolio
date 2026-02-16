from __future__ import annotations

from python_mastery_portfolio.ml_pipeline import train_linear_regression, predict


def test_train_without_normalization():
    x = [[1.0, 2.0], [2.0, 3.0], [3.0, 4.0]]
    y = [3.0, 5.0, 7.0]
    tm = train_linear_regression(x, y, normalize=False)
    preds = predict(tm, x)
    assert len(preds) == 3
    assert all(abs(a - b) < 1e-6 for a, b in zip(preds, y, strict=True))

