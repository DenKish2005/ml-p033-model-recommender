from dataclasses import asdict, replace
from pathlib import Path
from tomllib import loads

import numpy as np
import pandas as pd
import pytest
from sklearn.model_selection import StratifiedKFold, train_test_split

from model_recommender import runner
from model_recommender.datasets import LoadedDataset, read_registry
from model_recommender.model_families import ModelCandidate, candidates_for_family
from model_recommender.preprocessing import DensePreprocessor
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


@pytest.mark.parametrize("mode", ["full", "smoke"])
@pytest.mark.parametrize("outer_favourite", [0, 1])
def test_inner_selection_paired_rows_seed_reuse_and_refit(monkeypatch, mode, outer_favourite):
    """Real splits/preprocessing, stub fits/scores; full means 360+6 cheap calls.

    No benchmark artifact is written or admitted. The full stub result exercises
    orchestration only, not the P033-006 research-validity/admission boundary.
    """
    loaded = make_loaded()
    # Non-positional, shuffled row identities catch iloc/loc and accidental reordering.
    row_ids = np.random.default_rng(91).permutation(80) * 11 + 1001
    loaded.X.index = row_ids
    loaded.y.index = row_ids
    protocol = protocol_by_name(mode)
    expected = {}
    for seed in protocol.outer_seeds:
        train, test, y_train, _ = train_test_split(
            loaded.X, loaded.y, test_size=0.25, random_state=seed, stratify=loaded.y
        )
        folds = [
            (tuple(train.iloc[fit].index), tuple(train.iloc[valid].index))
            for fit, valid in StratifiedKFold(
                protocol.inner_folds, shuffle=True, random_state=seed
            ).split(train, y_train)
        ]
        expected[seed] = (tuple(train.index), tuple(test.index), folds)

    samples, preprocessing_fits, model_fits, scores, descriptors = [], [], [], [], []
    # Retain arrays so Python cannot recycle their ids during this test.
    matrices = {}
    original_fit = runner.fit_transform_checked
    original_transform = runner.transform_checked
    original_characterize = runner.characterize

    def sample(family, *, count, seed):
        candidates = candidates_for_family(family, count=count, seed=seed)
        samples.append((family, count, seed, candidates))
        return candidates

    def spy_preprocessing(method):
        original = getattr(DensePreprocessor, method)

        def fit(self, X):
            preprocessing_fits.append((method, self.scale_numeric, tuple(X.index)))
            return original(self, X)

        monkeypatch.setattr(DensePreprocessor, method, fit)

    def checked(operation, original):
        def transform(pre, X, *, limit_bytes):
            assert limit_bytes == 536_870_912
            matrix = original(pre, X, limit_bytes=limit_bytes)
            matrices[id(matrix)] = (matrix, pre, tuple(X.index), operation)
            return matrix

        return transform

    def characterize(X, y):
        pd.testing.assert_frame_equal(X, loaded.X.loc[X.index])
        pd.testing.assert_series_equal(y, loaded.y.loc[X.index])
        descriptors.append(tuple(X.index))
        return original_characterize(X, y)

    class Estimator:
        def __init__(self, candidate, seed):
            self.candidate, self.seed = candidate, seed

        def fit(self, X, y):
            _, self.pre, self.rows, operation = matrices[id(X)]
            assert operation == "fit"
            assert tuple(y.index) == self.rows
            pd.testing.assert_series_equal(y, loaded.y.loc[list(self.rows)])
            assert self.pre.scale_numeric is (self.candidate.family == "DNN")
            model_fits.append((self.candidate, self.seed, self.rows))
            return self

    def score(estimator, X, y):
        _, pre, rows, operation = matrices[id(X)]
        assert operation == "score" and pre is estimator.pre
        assert tuple(y.index) == rows
        pd.testing.assert_series_equal(y, loaded.y.loc[list(rows)])
        train, test, folds = expected[estimator.seed]
        order = estimator.candidate.order
        scores.append((estimator.candidate, estimator.seed, rows))
        if estimator.rows == train:
            assert rows == test
            # The baseline would dominate outer scoring in one scenario, but
            # inner selection must still choose a non-baseline configuration.
            balanced = float(order == outer_favourite)
        else:
            fold = [fit_rows for fit_rows, _ in folds].index(estimator.rows)
            assert rows == folds[fold][1]
            winner = 2 if mode == "full" and estimator.seed == 137 else 1
            balanced = (
                0.625 if order == winner else (0.875, 0.125, 0.75)[fold] if order == 0 else 0.25
            )
        # ROC-AUC deliberately favours the baseline, never the inner-BA winner.
        return {"balanced_accuracy": balanced, "roc_auc": float(order == 0)}

    monkeypatch.setattr(runner, "candidates_for_family", sample)
    spy_preprocessing("fit_structure")
    spy_preprocessing("fit_scaler")
    monkeypatch.setattr(runner, "fit_transform_checked", checked("fit", original_fit))
    monkeypatch.setattr(runner, "transform_checked", checked("score", original_transform))
    monkeypatch.setattr(runner, "characterize", characterize)
    monkeypatch.setattr(
        runner,
        "build_estimator",
        lambda candidate, *, random_state: Estimator(candidate, random_state),
    )
    monkeypatch.setattr(runner, "_prediction_scores", score)
    result = run_benchmark(loaded, protocol=protocol)
    assert result["status"] == "success"
    if mode == "smoke":
        assert result["research_valid"] is False
        assert result["status_note"] == "Smoke mode is development-only."

    expected_fits, expected_scores, expected_preprocessing, expected_samples = [], [], [], []
    for outer, seed in zip(result["outer_splits"], protocol.outer_seeds, strict=True):
        train, test, folds = expected[seed]
        assert set(train).isdisjoint(test)
        assert set(train) | set(test) == set(row_ids)
        assert outer["outer_seed"] == seed
        assert (outer["train_rows"], outer["test_rows"]) == (60, 20)
        for family in ("GBDT", "DNN"):
            candidates = candidates_for_family(family, count=protocol.candidate_count, seed=42)
            expected_samples.append((family, protocol.candidate_count, 42, candidates))
            winner = 2 if mode == "full" and seed == 137 else 1
            family_result = outer["families"][family]
            assert family_result["selected_candidate_order"] == winner
            assert family_result["best_params"] == candidates[winner].params
            assert family_result["inner_balanced_accuracy"] == 0.625
            assert family_result["outer_scores"] == {
                "balanced_accuracy": float(winner == outer_favourite),
                "roc_auc": 0.0,
            }
            assert [t["candidate_order"] for t in family_result["trials"]] == list(
                range(protocol.candidate_count)
            )
            for trial in family_result["trials"]:
                order = trial["candidate_order"]
                expected_ba = (
                    [0.625] * protocol.inner_folds
                    if order == winner
                    else [0.875, 0.125, 0.75][: protocol.inner_folds]
                    if order == 0
                    else [0.25] * protocol.inner_folds
                )
                assert trial["params"] == candidates[order].params
                assert trial["folds"] == [
                    {"fold": fold, "balanced_accuracy": value, "roc_auc": float(order == 0)}
                    for fold, value in enumerate(expected_ba)
                ]
                assert trial["mean_balanced_accuracy"] == pytest.approx(np.mean(expected_ba))
            for fit_rows, valid_rows in folds:
                assert set(fit_rows).isdisjoint(valid_rows)
                assert set(fit_rows) | set(valid_rows) == set(train)
                for rows in (fit_rows, valid_rows):
                    assert set(loaded.y.loc[list(rows)]) == {0, 1}
                for method in ("fit_structure", "fit_scaler"):
                    expected_preprocessing.append((method, family == "DNN", fit_rows))
                expected_fits.extend((c, seed, fit_rows) for c in candidates)
                expected_scores.extend((c, seed, valid_rows) for c in candidates)
            for method in ("fit_structure", "fit_scaler"):
                expected_preprocessing.append((method, family == "DNN", train))
            expected_fits.append((candidates[winner], seed, train))
            expected_scores.append((candidates[winner], seed, test))
    assert samples == expected_samples  # tuning seed, params and order reused across outer seeds
    assert descriptors == [expected[seed][0] for seed in protocol.outer_seeds]
    assert preprocessing_fits == expected_preprocessing
    assert model_fits == expected_fits  # every candidate sees exactly the same paired fold rows
    assert scores == expected_scores  # only selected candidates score on outer test rows
    assert len(model_fits) == len(scores) == (366 if mode == "full" else 10)
    refits = [entry for entry in model_fits if entry[2] == expected[entry[1]][0]]
    assert len(refits) == (6 if mode == "full" else 2)
    assert len(model_fits) - len(refits) == (360 if mode == "full" else 8)


@pytest.mark.parametrize("family", ["GBDT", "DNN"])
def test_exact_inner_tie_uses_candidate_order_even_if_list_order_differs(monkeypatch, family):
    candidates = [ModelCandidate(family, "stub", order, {"marker": order}) for order in (7, 2, 5)]
    monkeypatch.setattr(runner, "candidates_for_family", lambda *args, **kwargs: candidates)

    def fit(candidate, trial, *args, fold, **kwargs):
        # Dyadic fractions have an exact 0.5 mean in either order; AUC disagrees.
        values = {7: (0.25, 0.75), 2: (0.75, 0.25), 5: (0.5, 0.5)}
        trial["folds"].append(
            {
                "fold": fold,
                "balanced_accuracy": values[candidate.order][fold],
                "roc_auc": float(candidate.order == 7),
            }
        )

    monkeypatch.setattr(runner, "_fit_candidate", fit)
    loaded = make_loaded()
    result = runner._tune_family(
        loaded.X,
        loaded.y,
        family=family,
        outer_seed=137,
        protocol=replace(BenchmarkProtocol.smoke(), candidate_count=3),
    )
    assert [trial["mean_balanced_accuracy"] for trial in result["trials"]] == [0.5] * 3
    assert result["selected_candidate_order"] == 2
    assert result["best_params"] == {"marker": 2}


def test_prediction_scores_use_balanced_accuracy_and_positive_class_auc():
    class Predictions:
        def predict(self, X):
            return [0, 0, 0, 1, 1, 0]

        def predict_proba(self, X):
            positive = np.array([0.1, 0.2, 0.3, 0.9, 0.8, 0.4])
            return np.column_stack([1 - positive, positive])

    # Four negatives, two positives: specificity=3/4, sensitivity=1/2.
    # Each positive beats three of four negatives: AUC=6/8, using proba[:, 1].
    result = runner._prediction_scores(
        Predictions(), np.zeros((6, 1)), pd.Series([0, 0, 0, 0, 1, 1])
    )
    assert result == {"balanced_accuracy": 0.625, "roc_auc": 0.75}
