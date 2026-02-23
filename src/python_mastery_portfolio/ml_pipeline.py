"""Small ML pipeline helpers used by examples and tests.

Includes training/prediction helpers for a simple LinearRegression pipeline
with optional feature scaling and utilities to save/load models.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import numpy as np
from joblib import dump, load
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler


@dataclass
class TrainedModel:
    scaler: StandardScaler | None
    model: LinearRegression


def train_linear_regression(x: Sequence[Sequence[float]], y: Sequence[float], normalize: bool = True) -> TrainedModel:
    """Train a linear regression model.

    Args:
        x: Sequence of feature rows.
        y: Sequence of target values.
        normalize: If True, scale features with StandardScaler before training.

    Returns:
        TrainedModel containing the fitted scaler (or None) and the model.
    """
    xa = np.asarray(x, dtype=float)
    ya = np.asarray(y, dtype=float)
    scaler: StandardScaler | None = None
    if normalize:
        scaler = StandardScaler()
        model = LinearRegression()
        model.fit(scaler.fit_transform(xa), ya)
    else:
        model = LinearRegression()
        model.fit(xa, ya)
    return TrainedModel(scaler=scaler, model=model)


def predict(trained: TrainedModel, rows: Iterable[Sequence[float]]) -> list[float]:
    """Predict numeric values for given feature rows using a trained model."""
    xm = np.asarray(list(rows), dtype=float)
    if trained.scaler is not None:
        preds = trained.model.predict(trained.scaler.transform(xm))
    else:
        preds = trained.model.predict(xm)
    return [float(v) for v in preds.tolist()]


def save_model(tm: TrainedModel, path: str | Path) -> Path:
    """Persist the trained model to disk using joblib.dump.

    Ensures the parent directory exists before writing.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    dump(tm, p)
    return p


def load_model(path: str | Path) -> TrainedModel:
    """Load a TrainedModel previously saved with :func:`save_model`."""
    return cast(TrainedModel, load(Path(path)))


def add_bias_feature(rows: Iterable[Sequence[float]]) -> list[list[float]]:
    """Prepend a bias (1.0) feature to each input row."""
    return [[1.0, *[float(v) for v in row]] for row in rows]
