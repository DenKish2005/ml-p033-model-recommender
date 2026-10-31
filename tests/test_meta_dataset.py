import json

import pandas as pd
import pytest
from benchmark_artifacts import complete_result

from model_recommender.meta_dataset import META_TARGET, build_meta_dataset, meta_feature_columns


def test_build_meta_dataset(tmp_path):
    paths = []
    for index, payload in enumerate(
        (complete_result("test:a", 900001), complete_result("test:b", 900002))
    ):
        path = tmp_path / f"{index}.json"
        path.write_text(json.dumps(payload))
        paths.append(path)
    frame = build_meta_dataset(paths)
    assert frame["dataset"].tolist() == ["test:a", "test:b"]
    assert META_TARGET in frame
    assert meta_feature_columns(frame) == list(
        payload["aggregate"]["meta_features_mean_over_outer_training_partitions"]
    )
    assert frame["n_samples"].tolist() == [60.0, 60.0]
    assert frame[META_TARGET].tolist() == pytest.approx([0.03, 0.03])


def test_reject_nonresearch_smoke_result(tmp_path):
    path = tmp_path / "smoke.json"
    path.write_text(json.dumps(complete_result(smoke=True)))
    with pytest.raises(ValueError, match="protocol"):
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
