from dataclasses import asdict, replace
from pathlib import Path
from tomllib import loads

import numpy as np
import pandas as pd
import pytest

from model_recommender.datasets import LoadedDataset, read_registry
from model_recommender.runner import BenchmarkProtocol, protocol_by_name, run_benchmark


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


@pytest.mark.parametrize(
    "name,seeds,folds,candidates,inner_fits,refits",
    [("full", (42, 137, 2026), 3, 20, 360, 6), ("smoke", (42,), 2, 2, 8, 2)],
)
def test_frozen_protocol_signature_and_toml(name, seeds, folds, candidates, inner_fits, refits):
    protocol = protocol_by_name(name)
    assert protocol == (BenchmarkProtocol.full() if name == "full" else BenchmarkProtocol.smoke())
    assert asdict(protocol) == {
        "name": name,
        "outer_seeds": seeds,
        "test_size": 0.25,
        "inner_folds": folds,
        "candidate_count": candidates,
        "tuning_seed": 42,
        "matrix_limit_bytes": 536_870_912,
        "recommendation_margin": 0.01,
    }
    assert len(seeds) * 2 * folds * candidates == inner_fits
    assert len(seeds) * 2 == refits
    root = Path(__file__).resolve().parents[1]
    config = loads(
        (root / "configs/experiments/general_benchmark.toml").read_text(encoding="utf-8")
    )
    full = config["experiment"]
    assert full["test_size"] == protocol.test_size
    assert full["tuning_seed"] == protocol.tuning_seed
    assert full["task_type"] == "binary_classification"
    assert full["primary_metric"] == "balanced_accuracy"
    assert full["secondary_metrics"] == ["roc_auc", "search_seconds", "refit_seconds"]
    assert full["protocol"] == "docs/experiment-protocol.md"
    assert full["implementation"] == "src/model_recommender/runner.py"
    section = full if name == "full" else config["development_smoke"]
    assert tuple(section["outer_seeds"]) == seeds
    assert section["inner_folds"] == folds
    assert section["candidate_count_per_model"] == candidates
    if name == "smoke":
        assert section["research_valid"] is False


@pytest.mark.parametrize("name", ["unknown", "Full", "", "development_smoke"])
def test_unknown_protocol_name_is_rejected(name):
    with pytest.raises(ValueError, match="mode must be 'smoke' or 'full'"):
        protocol_by_name(name)
