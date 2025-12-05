import numpy as np

from python_mastery_portfolio.ml_utils import (
    accuracy_score,
    cross_validate_estimator,
    f1_score,
    mse_score,
    precision_score,
    recall_score,
    roc_auc_score,
    train_test_split,
)


def test_train_test_split_shapes():
    x = np.arange(20).reshape(10, 2)
    y = np.arange(10)
    xtr, xte, ytr, yte = train_test_split(x, y, test_size=0.3, random_state=42)
    assert len(ytr) == 7
    assert len(yte) == 3


def test_basic_metrics():
    y_true = np.array([0, 1, 1, 0, 1, 0])
    y_pred = np.array([0, 1, 0, 0, 1, 1])
    assert accuracy_score(y_true, y_pred) == (y_true == y_pred).mean()
    assert precision_score(y_true, y_pred) == 2 / 3
    assert recall_score(y_true, y_pred) == 2 / 3
    assert f1_score(y_true, y_pred) == 2 * (2 / 3) * (2 / 3) / ((2 / 3) + (2 / 3))
    assert mse_score(y_true, y_pred) == float(((y_true - y_pred) ** 2).mean())


def test_roc_auc_simple():
    # perfect ranking: positives have higher scores
    y_true = np.array([0, 1, 0, 1])
    scores = np.array([0.1, 0.9, 0.2, 0.8])
    auc = roc_auc_score(y_true, scores)
    assert 0.99 < auc <= 1.0


def test_cross_validate_dummy():
    # simple dummy estimator that predicts majority class
    class Dummy:
        def fit(self, x, y):
            vals, counts = np.unique(y, return_counts=True)
            self.pred = vals[np.argmax(counts)]

        def predict(self, x):
            return np.full(shape=(len(x),), fill_value=self.pred)

    x = np.arange(20).reshape(10, 2)
    y = np.array([0, 1] * 5)
    scores = cross_validate_estimator(lambda: Dummy(), x, y, k=5)
    assert len(scores) == 5
