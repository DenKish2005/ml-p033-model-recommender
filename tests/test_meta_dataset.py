import json

import pandas as pd
import pytest

from model_recommender.meta_dataset import META_TARGET, build_meta_dataset, meta_feature_columns


def result(name, family, gap, *, research_valid=True):
    return {
        "research_valid": research_valid,
        "dataset": {
            "name": name,
            "openml_id": 1,
            "version": 1,
            "family": family,
            "clinical": False,
        },
        "aggregate": {
            "mean_balanced_accuracy_gbdt": 0.7,
            "mean_balanced_accuracy_mlp": 0.7 + gap,
            "performance_gap_mlp_minus_gbdt": gap,
            "actual_best_pipeline": "DNN" if gap > 0 else "GBDT",
            "near_tie_within_margin": abs(gap) <= 0.01,
            "meta_features_mean_over_outer_training_partitions": {
                "n_samples": 100.0,
                "missing_fraction": 0.1,
            },
        },
    }


def test_build_meta_dataset(tmp_path):
    paths = []
    for index, payload in enumerate((result("a", "fa", 0.03), result("b", "fb", -0.02))):
        path = tmp_path / f"{index}.json"
        path.write_text(json.dumps(payload))
        paths.append(path)
    frame = build_meta_dataset(paths)
    assert frame["dataset"].tolist() == ["a", "b"]
    assert META_TARGET in frame
    assert meta_feature_columns(frame) == ["n_samples", "missing_fraction"]


def test_reject_nonresearch_smoke_result(tmp_path):
    path = tmp_path / "smoke.json"
    path.write_text(json.dumps(result("a", "fa", 0.01, research_valid=False)))
    with pytest.raises(ValueError, match="not a successful full-protocol"):
        build_meta_dataset([path])


def test_meta_features_must_be_numeric():
    frame = pd.DataFrame(
        {
            "dataset": ["a"],
            "family": ["fa"],
            META_TARGET: [0.1],
            "mean_balanced_accuracy_gbdt": [0.7],
            "mean_balanced_accuracy_mlp": [0.8],
            "actual_best_pipeline": ["DNN"],
            "near_tie_within_margin": [False],
            "clinical": [False],
            "openml_id": [1],
            "version": [1],
            "bad_feature": ["x"],
        }
    )
    with pytest.raises(ValueError, match="must be numeric"):
        meta_feature_columns(frame)
