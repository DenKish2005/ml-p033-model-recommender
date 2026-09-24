"""Model candidates used by the first P033 benchmark protocol."""

from __future__ import annotations

import random
from dataclasses import dataclass
from itertools import product

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.neural_network import MLPClassifier


@dataclass(frozen=True)
class ModelCandidate:
    family: str
    model: str
    order: int
    params: dict[str, object]


GBDT_BASELINE = {
    "learning_rate": 0.1,
    "max_leaf_nodes": 31,
    "l2_regularization": 0.0,
    "min_samples_leaf": 20,
}
MLP_BASELINE = {
    "hidden_layer_sizes": (32, 16),
    "alpha": 0.0001,
    "learning_rate_init": 0.001,
}


def _sample_with_baseline(
    grid: list[dict[str, object]],
    baseline: dict[str, object],
    *,
    count: int,
    seed: int,
) -> list[dict[str, object]]:
    if count < 1 or count > len(grid):
        raise ValueError(f"candidate count must be between 1 and {len(grid)}")
    remainder = [params for params in grid if params != baseline]
    rng = random.Random(seed)
    sampled = rng.sample(remainder, count - 1)
    return [baseline.copy(), *[item.copy() for item in sampled]]


def gbdt_candidates(*, count: int = 20, seed: int = 42) -> list[ModelCandidate]:
    grid = [
        {
            "learning_rate": learning_rate,
            "max_leaf_nodes": max_leaf_nodes,
            "l2_regularization": l2,
            "min_samples_leaf": min_samples_leaf,
        }
        for learning_rate, max_leaf_nodes, l2, min_samples_leaf in product(
            (0.03, 0.1),
            (15, 31, 63),
            (0.0, 1.0, 10.0),
            (10, 20, 40),
        )
    ]
    selected = _sample_with_baseline(grid, GBDT_BASELINE, count=count, seed=seed)
    return [
        ModelCandidate("GBDT", "hist_gradient_boosting", order, params)
        for order, params in enumerate(selected)
    ]


def mlp_candidates(*, count: int = 20, seed: int = 42) -> list[ModelCandidate]:
    grid = [
        {
            "hidden_layer_sizes": hidden,
            "alpha": alpha,
            "learning_rate_init": learning_rate,
        }
        for hidden, alpha, learning_rate in product(
            ((32, 16), (64, 32), (128, 64)),
            (0.0001, 0.001, 0.01),
            (0.0003, 0.001, 0.003),
        )
    ]
    selected = _sample_with_baseline(grid, MLP_BASELINE, count=count, seed=seed)
    return [ModelCandidate("DNN", "mlp", order, params) for order, params in enumerate(selected)]


def candidates_for_family(
    family: str,
    *,
    count: int = 20,
    seed: int = 42,
) -> list[ModelCandidate]:
    if family == "GBDT":
        return gbdt_candidates(count=count, seed=seed)
    if family == "DNN":
        return mlp_candidates(count=count, seed=seed)
    raise ValueError(f"Unknown model family: {family!r}")


def build_estimator(candidate: ModelCandidate, *, random_state: int):
    if candidate.family == "GBDT":
        return HistGradientBoostingClassifier(
            **candidate.params,
            max_iter=200,
            early_stopping=False,
            random_state=random_state,
        )
    if candidate.family == "DNN":
        return MLPClassifier(
            **candidate.params,
            max_iter=500,
            solver="adam",
            activation="relu",
            early_stopping=False,
            random_state=random_state,
        )
    raise ValueError(f"Unsupported candidate family: {candidate.family!r}")


def needs_numeric_scaling(family: str) -> bool:
    if family == "DNN":
        return True
    if family == "GBDT":
        return False
    raise ValueError(f"Unknown model family: {family!r}")
