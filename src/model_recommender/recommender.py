"""Regression meta-models that predict MLP-minus-GBDT performance advantage."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor

from model_recommender.meta_dataset import META_TARGET, meta_feature_columns


@dataclass
class TrainedRecommender:
    name: str
    estimator: object
    features: list[str]
    margin: float = 0.01

    def predict_gap(self, frame: pd.DataFrame) -> np.ndarray:
        values = np.asarray(self.estimator.predict(frame[self.features]), dtype=float)
        if not np.isfinite(values).all():
            raise ValueError("Recommender produced non-finite predictions.")
        return values

    def recommend(self, frame: pd.DataFrame) -> list[str]:
        return ["DNN" if value > self.margin else "GBDT" for value in self.predict_gap(frame)]


def make_meta_estimator(name: str, *, random_state: int = 42):
    if name == "dummy_mean":
        return DummyRegressor(strategy="mean")
    if name == "ridge":
        return make_pipeline(StandardScaler(), Ridge(alpha=1.0))
    if name == "decision_tree":
        return DecisionTreeRegressor(max_depth=3, min_samples_leaf=2, random_state=random_state)
    if name == "random_forest":
        return RandomForestRegressor(
            n_estimators=300,
            max_depth=5,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=1,
        )
    raise ValueError(f"Unknown recommender model: {name!r}")


def train_recommender(
    frame: pd.DataFrame,
    *,
    name: str = "ridge",
    random_state: int = 42,
    margin: float = 0.01,
) -> TrainedRecommender:
    if META_TARGET not in frame:
        raise ValueError(f"Meta-dataset is missing target column {META_TARGET!r}.")
    features = meta_feature_columns(frame)
    if len(frame) < 2:
        raise ValueError("Need at least two datasets to fit a recommender.")
    X = frame[features]
    y = frame[META_TARGET]
    if X.isna().any().any() or y.isna().any():
        raise ValueError("Meta-dataset contains missing values.")
    estimator = make_meta_estimator(name, random_state=random_state)
    estimator.fit(X, y)
    return TrainedRecommender(name=name, estimator=estimator, features=features, margin=margin)
