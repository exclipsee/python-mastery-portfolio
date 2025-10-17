from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from joblib import dump, load
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from typing import cast


@dataclass
class TrainedModel:
    scaler: StandardScaler
    model: LinearRegression


def train_linear_regression(x: Sequence[Sequence[float]], y: Sequence[float]) -> TrainedModel:
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x_arr)
    model = LinearRegression()
    model.fit(x_scaled, y_arr)
    return TrainedModel(scaler=scaler, model=model)


def predict(trained: TrainedModel, rows: Iterable[Sequence[float]]) -> list[float]:
    x_mat = np.asarray(list(rows), dtype=float)
    x_scaled = trained.scaler.transform(x_mat)
    preds = trained.model.predict(x_scaled)
    # ensure precise typing for mypy
    return [float(v) for v in preds.tolist()]


def save_model(tm: TrainedModel, path: str | Path) -> Path:
    p = Path(path)
    dump(tm, p)
    return p


def load_model(path: str | Path) -> TrainedModel:
    return cast(TrainedModel, load(Path(path)))


def add_bias_feature(rows: Iterable[Sequence[float]]) -> list[list[float]]:
    """Simple feature engineering: prepend bias term 1.0 to each row."""
    return [[1.0, *[float(v) for v in row]] for row in rows]
