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
    xm = np.asarray(list(rows), dtype=float)
    if trained.scaler is not None:
        preds = trained.model.predict(trained.scaler.transform(xm))
    else:
        preds = trained.model.predict(xm)
    return [float(v) for v in preds.tolist()]


def save_model(tm: TrainedModel, path: str | Path) -> Path:
    p = Path(path)
    dump(tm, p)
    return p


def load_model(path: str | Path) -> TrainedModel:
    return cast(TrainedModel, load(Path(path)))


def add_bias_feature(rows: Iterable[Sequence[float]]) -> list[list[float]]:
    return [[1.0, *[float(v) for v in row]] for row in rows]
