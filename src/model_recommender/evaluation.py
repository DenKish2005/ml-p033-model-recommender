"""Held-out-dataset-family evaluation and recommendation regret metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.model_selection import LeaveOneGroupOut

from model_recommender.meta_dataset import META_TARGET
from model_recommender.recommender import train_recommender


def recommendation_regret(row: pd.Series, selected: str) -> float:
    gbdt = float(row["mean_balanced_accuracy_gbdt"])
    dnn = float(row["mean_balanced_accuracy_mlp"])
    selected_score = dnn if selected == "DNN" else gbdt
    return max(gbdt, dnn) - selected_score


def evaluate_recommender(
    frame: pd.DataFrame,
    *,
    model_name: str = "ridge",
    random_state: int = 42,
    margin: float = 0.01,
) -> tuple[pd.DataFrame, dict[str, object]]:
    required = {
        "dataset",
        "family",
        META_TARGET,
        "mean_balanced_accuracy_gbdt",
        "mean_balanced_accuracy_mlp",
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Meta-dataset is missing columns: {sorted(missing)}")
    if frame["family"].nunique() < 2:
        raise ValueError("Need at least two held-out dataset families for evaluation.")

    splitter = LeaveOneGroupOut()
    rows: list[dict[str, object]] = []
    for train_index, test_index in splitter.split(frame, groups=frame["family"]):
        train = frame.iloc[train_index]
        test = frame.iloc[test_index]
        recommender = train_recommender(
            train,
            name=model_name,
            random_state=random_state,
            margin=margin,
        )
        predicted_gaps = recommender.predict_gap(test)
        recommendations = ["DNN" if value > margin else "GBDT" for value in predicted_gaps]

        training_mean_gbdt = float(train["mean_balanced_accuracy_gbdt"].mean())
        training_mean_dnn = float(train["mean_balanced_accuracy_mlp"].mean())
        best_fixed = "DNN" if training_mean_dnn > training_mean_gbdt else "GBDT"

        for position, (_, item) in enumerate(test.iterrows()):
            recommendation = recommendations[position]
            actual_gap = float(item[META_TARGET])
            oracle = "DNN" if actual_gap > 0 else "GBDT"
            rows.append(
                {
                    "dataset": item["dataset"],
                    "family": item["family"],
                    "actual_gap": actual_gap,
                    "predicted_gap": float(predicted_gaps[position]),
                    "recommendation": recommendation,
                    "actual_best_pipeline": oracle,
                    "correct_best_pipeline": recommendation == oracle,
                    "regret": recommendation_regret(item, recommendation),
                    "regret_always_gbdt": recommendation_regret(item, "GBDT"),
                    "regret_always_dnn": recommendation_regret(item, "DNN"),
                    "best_fixed_from_training": best_fixed,
                    "regret_best_fixed": recommendation_regret(item, best_fixed),
                    "regret_oracle": 0.0,
                }
            )

    predictions = pd.DataFrame(rows).sort_values("dataset").reset_index(drop=True)
    summary = {
        "model": model_name,
        "margin": margin,
        "n_datasets": len(predictions),
        "n_families": int(frame["family"].nunique()),
        "best_pipeline_accuracy": float(predictions["correct_best_pipeline"].mean()),
        "mean_regret": float(predictions["regret"].mean()),
        "mean_regret_always_gbdt": float(predictions["regret_always_gbdt"].mean()),
        "mean_regret_always_dnn": float(predictions["regret_always_dnn"].mean()),
        "mean_regret_best_fixed": float(predictions["regret_best_fixed"].mean()),
        "rmse_gap": float(
            np.sqrt(np.mean((predictions["predicted_gap"] - predictions["actual_gap"]) ** 2))
        ),
    }
    return predictions, summary
