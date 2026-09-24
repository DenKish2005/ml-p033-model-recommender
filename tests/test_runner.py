from dataclasses import replace

import numpy as np
import pandas as pd

from model_recommender.datasets import LoadedDataset, read_registry
from model_recommender.runner import BenchmarkProtocol, run_benchmark


def make_loaded() -> LoadedDataset:
    rng = np.random.default_rng(7)
    n = 80
    x1 = rng.normal(size=n)
    x2 = rng.normal(size=n)
    category = np.where(x1 > 0, "a", "b").astype(object)
    category[::17] = None
    y = pd.Series((x1 + 0.4 * x2 + rng.normal(scale=0.5, size=n) > 0).astype(int), name="class")
    X = pd.DataFrame({"x1": x1, "x2": x2, "category": pd.Categorical(category)})
    spec = replace(
        read_registry()["credit-g"],
        name="synthetic",
        openml_id=999999,
        md5_checksum="0" * 32,
        source_url="https://example.test",
        original_source_url="https://example.test",
        family="synthetic-family",
        target="class",
        positive_class="1",
        class_labels=["0", "1"],
        expected_rows=n,
        numeric_features=["x1", "x2"],
        categorical_features=["category"],
        excluded_features=[],
    )
    return LoadedDataset(spec=spec, X=X, y=y)


def test_smoke_benchmark_runs_end_to_end():
    loaded = make_loaded()
    protocol = BenchmarkProtocol(
        name="smoke",
        outer_seeds=(42,),
        test_size=0.25,
        inner_folds=2,
        candidate_count=2,
    )
    result = run_benchmark(loaded, protocol=protocol)
    assert result["status"] == "success"
    assert result["research_valid"] is False
    assert result["aggregate"] is not None
    assert len(result["outer_splits"]) == 1
    assert result["outer_splits"][0]["families"]["GBDT"]["all_trials_completed"]
    assert result["outer_splits"][0]["families"]["DNN"]["all_trials_completed"]
    assert len(result["outer_splits"][0]["families"]["GBDT"]["trials"]) == 2
