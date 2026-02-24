"""Machine-learning utility helpers used by examples and tests.

Includes simple train/test split, k-fold index generation, cross-validation
harness, and a few common scoring functions. These helpers accept numpy
arrays or pandas objects where convenient.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

import importlib

np = None
try:
    np = importlib.import_module("numpy")
except Exception:
    np = None  # type: ignore

import pandas as pd  # type: ignore


def _to_numpy(x: Any) -> Any:
    if isinstance(x, pd.DataFrame) or isinstance(x, pd.Series):
        return x.values
    return np.asarray(x) if np is not None else x


def train_test_split(x: Any, y: Any, test_size: float = 0.2, random_state: int | None = None) -> tuple[Any, Any, Any, Any]:
    """Split arrays or pandas objects into train and test subsets.

    Args:
        x: Features (array-like or pandas object).
        y: Targets (array-like or pandas object).
        test_size: Fraction of data to reserve for the test set.
        random_state: Seed for reproducible shuffling.

    Returns:
        x_train, x_test, y_train, y_test
    """
    rng = np.random.default_rng(random_state) if np is not None else None
    y_arr = _to_numpy(y)
    n = len(y_arr)
    idx = (np.arange(n) if np is not None else list(range(n)))
    if rng is not None:
        rng.shuffle(idx)
    else:
        import random

        random.shuffle(idx)
    split = int(n * (1 - test_size))
    train_idx, test_idx = idx[:split], idx[split:]

    def _slice(a: Any, i: Any) -> Any:
        if isinstance(a, (pd.DataFrame, pd.Series)):
            return a.iloc[i]
        return a[i]

    return _slice(x, train_idx), _slice(x, test_idx), _slice(y, train_idx), _slice(y, test_idx)


def k_fold_indices(
    n_samples: int, k: int = 5, random_state: int | None = None
) -> Iterable[tuple["np.ndarray", "np.ndarray"]]:
    """Yield (train_idx, val_idx) pairs for k-fold cross-validation.

    Args:
        n_samples: Number of samples in the dataset.
        k: Number of folds (must be >=1 and <= n_samples).
        random_state: Optional seed for shuffling.

    Yields:
        Tuples of (train_indices, val_indices) as numpy arrays.

    Raises:
        ValueError: if k is not in the valid range.
    """
    if k <= 0:
        raise ValueError("k must be >= 1")
    if k > n_samples:
        raise ValueError("k cannot be greater than the number of samples")
    rng = np.random.default_rng(random_state) if np is not None else None
    idx = (np.arange(n_samples) if np is not None else list(range(n_samples)))
    if rng is not None:
        rng.shuffle(idx)
    else:
        import random

        random.shuffle(idx)
    if np is not None:
        folds = np.array_split(idx, k)
        for i in range(k):
            val = folds[i]
            train = np.concatenate([f for j, f in enumerate(folds) if j != i])
            yield train, val
    else:
        # Fallback to list-based splits
        folds = [idx[i::k] for i in range(k)]
        for i in range(k):
            val = folds[i]
            train = [x for j, f in enumerate(folds) if j != i for x in f]
            yield train, val


def cross_validate_estimator(
    estimator_factory: Callable[[], Any],
    x: Any,
    y: Any,
    k: int = 5,
    scorer: Callable[[Any, Any], float] | None = None,
) -> list[float]:
    """Basic cross-validation harness.

    Trains an estimator produced by ``estimator_factory`` on k-1 folds and
    evaluates it on the held-out fold. The optional ``scorer`` should accept
    (y_true, y_pred_or_score) and return a float.
    """
    x_arr = _to_numpy(x)
    y_arr = _to_numpy(y)
    n = len(y_arr)
    scores: list[float] = []
    for train_idx, val_idx in k_fold_indices(n, k=k):
        est = estimator_factory()
        x_train = x_arr[train_idx]
        y_train = y_arr[train_idx]
        x_val = x_arr[val_idx]
        y_val = y_arr[val_idx]
        # estimator_factory should return an object with fit/predict methods
        est.fit(x_train, y_train)
        if scorer is None:
            y_pred = est.predict(x_val)
            score = accuracy_score(y_val, y_pred)
        else:
            # scorer must accept y_true and either y_pred or y_score depending on implementation
            # we try to use predict_proba if scorer expects scores (e.g., roc_auc_score)
            try:
                y_score = est.predict_proba(x_val)[:, 1]
                score = scorer(y_val, y_score)
            except Exception:
                y_pred = est.predict(x_val)
                score = scorer(y_val, y_pred)
        scores.append(float(score))
    return scores


def accuracy_score(y_true: Any, y_pred: Any) -> float:
    y_true = _to_numpy(y_true)
    y_pred = _to_numpy(y_pred)
    return float((y_true == y_pred).mean())


def precision_score(y_true: Any, y_pred: Any) -> float:
    y_true = _to_numpy(y_true)
    y_pred = _to_numpy(y_pred)
    tp = int(((y_pred == 1) & (y_true == 1)).sum())
    fp = int(((y_pred == 1) & (y_true == 0)).sum())
    return float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0


def recall_score(y_true: Any, y_pred: Any) -> float:
    y_true = _to_numpy(y_true)
    y_pred = _to_numpy(y_pred)
    tp = int(((y_pred == 1) & (y_true == 1)).sum())
    fn = int(((y_pred == 0) & (y_true == 1)).sum())
    return float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0


def f1_score(y_true: Any, y_pred: Any) -> float:
    p = precision_score(y_true, y_pred)
    r = recall_score(y_true, y_pred)
    return float(2 * p * r / (p + r)) if (p + r) > 0 else 0.0


def mse_score(y_true: Any, y_pred: Any) -> float:
    y_true = _to_numpy(y_true).astype(float)
    y_pred = _to_numpy(y_pred).astype(float)
    return float(((y_true - y_pred) ** 2).mean())


def roc_auc_score(y_true: Any, y_score: Any) -> float:
    y_true = _to_numpy(y_true)
    y_score = _to_numpy(y_score)
    if len(y_true) == 0:
        return 0.0
    pos = y_true == 1
    neg = y_true == 0
    n_pos = int(pos.sum())
    n_neg = int(neg.sum())
    if n_pos == 0 or n_neg == 0:
        return 0.0
    # ranks (1-based)
    order = np.argsort(y_score)
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.arange(len(y_score)) + 1
    sum_ranks_pos = ranks[pos].sum()
    auc = (sum_ranks_pos - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)
    return float(auc)


__all__ = [
    "train_test_split",
    "k_fold_indices",
    "cross_validate_estimator",
    "accuracy_score",
    "precision_score",
    "recall_score",
    "f1_score",
    "mse_score",
    "roc_auc_score",
]
