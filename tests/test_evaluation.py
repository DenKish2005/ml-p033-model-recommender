import pandas as pd

from model_recommender.evaluation import evaluate_recommender, recommendation_regret
from model_recommender.meta_dataset import META_TARGET


def make_frame():
    return pd.DataFrame(
        {
            "dataset": ["a", "b", "c", "d", "e"],
            "family": ["fa", "fb", "fc", "fd", "fe"],
            "openml_id": [1, 2, 3, 4, 5],
            "version": [1] * 5,
            "clinical": [False] * 5,
            "n_samples": [100.0, 180.0, 250.0, 400.0, 700.0],
            "missing_fraction": [0.0, 0.05, 0.1, 0.2, 0.3],
            "mean_balanced_accuracy_gbdt": [0.72, 0.73, 0.70, 0.69, 0.68],
            "mean_balanced_accuracy_mlp": [0.68, 0.72, 0.72, 0.73, 0.75],
            META_TARGET: [-0.04, -0.01, 0.02, 0.04, 0.07],
            "actual_best_pipeline": ["GBDT", "GBDT", "DNN", "DNN", "DNN"],
            "near_tie_within_margin": [False, True, False, False, False],
        }
    )


def test_regret():
    row = make_frame().iloc[0]
    assert recommendation_regret(row, "GBDT") == 0
    assert recommendation_regret(row, "DNN") > 0


def test_leave_one_family_out_evaluation():
    predictions, summary = evaluate_recommender(make_frame(), model_name="ridge")
    assert len(predictions) == 5
    assert summary["n_families"] == 5
    assert summary["mean_regret"] >= 0
