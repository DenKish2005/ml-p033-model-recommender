import pandas as pd

from model_recommender.meta_dataset import META_TARGET
from model_recommender.recommender import train_recommender


def test_train_and_recommend_gap_regressor():
    frame = pd.DataFrame(
        {
            "dataset": ["a", "b", "c", "d"],
            "family": ["fa", "fb", "fc", "fd"],
            "openml_id": [1, 2, 3, 4],
            "version": [1, 1, 1, 1],
            "clinical": [False] * 4,
            "n_samples": [100.0, 200.0, 300.0, 400.0],
            "missing_fraction": [0.0, 0.1, 0.2, 0.3],
            "mean_balanced_accuracy_gbdt": [0.70, 0.71, 0.72, 0.73],
            "mean_balanced_accuracy_mlp": [0.68, 0.72, 0.76, 0.78],
            META_TARGET: [-0.02, 0.01, 0.04, 0.05],
            "actual_best_pipeline": ["GBDT", "DNN", "DNN", "DNN"],
            "near_tie_within_margin": [False, True, False, False],
        }
    )
    trained = train_recommender(frame, name="ridge")
    gaps = trained.predict_gap(frame)
    assert len(gaps) == 4
    assert set(trained.recommend(frame)) <= {"GBDT", "DNN"}
