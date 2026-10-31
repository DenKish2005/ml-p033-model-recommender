"""Validate existing v1 result evidence without repairing artifacts or claiming provenance."""

from dataclasses import asdict
from math import ceil, isclose, isfinite

import numpy as np

from model_recommender.model_families import candidates_for_family
from model_recommender.runner import BenchmarkProtocol

# JSON float round trips preserve doubles. This allows only accumulated arithmetic
# noise (at most 60 scores), not rounded published scores or protocol/param drift.
ARITHMETIC_ATOL = 1e-12
V1_META_KEYS = {
    "n_samples",
    "n_features",
    "n_classes",
    "samples_per_feature",
    "categorical_fraction",
    "missing_fraction",
    "rows_with_missing_fraction",
    "constant_feature_fraction",
    "minority_class_fraction",
    "imbalance_ratio",
}


def _require(condition, path, reason):
    if not condition:
        raise ValueError(f"{path}: {reason}")


def _object(value, path):
    _require(isinstance(value, dict), path, "required object")
    return value


def _number(value, path, low=0, high=float("inf")):
    _require(type(value) in (int, float), path, "required numeric value (not bool)")
    try:
        valid = isfinite(value) and low <= value <= high
    except OverflowError:
        valid = False
    _require(valid, path, f"required finite value in [{low}, {high}]")
    return value


def _integer(value, path, low=0):
    _require(type(value) is int and value >= low, path, f"required integer >= {low}")
    return value


def _same(actual, expected, path):
    """Exact typed identity, with only tuple/JSON-array normalization."""
    if isinstance(expected, dict):
        _object(actual, path)
        _require(actual.keys() == expected.keys(), path, "identity keys mismatch")
        for key, value in expected.items():
            _same(actual[key], value, f"{path}.{key}")
    elif isinstance(expected, (list, tuple)):
        _require(isinstance(actual, (list, tuple)), path, "required array")
        _require(len(actual) == len(expected), path, "identity length mismatch")
        for index, value in enumerate(expected):
            _same(actual[index], value, f"{path}[{index}]")
    else:
        if type(expected) in (int, float):
            _number(actual, path, -float("inf"))
            if type(expected) is int:
                _integer(actual, path)
        else:
            _require(type(actual) is type(expected), path, "identity type mismatch")
        _require(actual == expected, path, f"expected {expected!r}")


def _mean(values):
    # Match the runner's arithmetic, including exact-tie selection semantics.
    return float(np.mean(values))


def _arithmetic(actual, expected, path, low=0, high=float("inf")):
    _number(actual, path, low, high)
    _require(
        isclose(actual, expected, rel_tol=0, abs_tol=ARITHMETIC_ATOL), path, "arithmetic mismatch"
    )


def _warnings(value, path):
    _require(
        isinstance(value, list) and all(isinstance(x, str) for x in value),
        path,
        "required array of warning strings",
    )


def _ordered(value, count, key, path):
    _require(
        isinstance(value, list) and len(value) == count,
        path,
        f"required complete array of {count} entries",
    )
    for index, item in enumerate(value):
        _object(item, f"{path}[{index}]")
        _same(item.get(key), index, f"{path}[{index}].{key}")
    return value


def _matrix(value, row_counts, limit, path):
    value = _object(value, path)
    width = _integer(value.get("n_encoded_features"), f"{path}.n_encoded_features", 1)
    for key, rows in row_counts.items():
        size = _integer(value.get(key), f"{path}.{key}", 1)
        _require(
            size == rows * width * 8 and size <= limit,
            f"{path}.{key}",
            "dense float64 matrix size/limit mismatch",
        )


def _meta(value, train_rows, path):
    value = _object(value, path)
    _require(V1_META_KEYS <= value.keys(), path, "missing v1 outer-training descriptors")
    # v1 permits additional numeric descriptors. Predictor allowlisting is P033-007.
    for key, number in value.items():
        _require(isinstance(key, str) and bool(key), path, "descriptor keys must be strings")
        _number(number, f"{path}.{key}")
    for key in ("n_samples", "n_features", "n_classes"):
        _integer(value[key], f"{path}.{key}", 1)
    _same(value["n_samples"], train_rows, f"{path}.n_samples")
    _same(value["n_classes"], 2, f"{path}.n_classes")
    _arithmetic(
        value["samples_per_feature"],
        train_rows / value["n_features"],
        f"{path}.samples_per_feature",
    )
    for key in V1_META_KEYS:
        if key.endswith("_fraction"):
            _number(value[key], f"{path}.{key}", 0, 1)
    minority = _number(value["minority_class_fraction"], f"{path}.minority_class_fraction", 0, 0.5)
    _require(minority > 0, path, "binary minority fraction must be positive")
    _arithmetic(value["imbalance_ratio"], (1 - minority) / minority, f"{path}.imbalance_ratio", 1)
    return value


def _family(value, family, protocol, train_rows, test_rows, path):
    value = _object(value, path)
    candidates = candidates_for_family(
        family, count=protocol.candidate_count, seed=protocol.tuning_seed
    )
    _same(value.get("family"), family, f"{path}.family")
    _same(value.get("model"), candidates[0].model, f"{path}.model")
    _same(value.get("all_trials_completed"), True, f"{path}.all_trials_completed")
    _require(
        "error" in value and value["error"] is None,
        f"{path}.error",
        "successful family requires null error",
    )
    _number(value.get("search_seconds"), f"{path}.search_seconds")
    _number(value.get("refit_seconds"), f"{path}.refit_seconds")
    _warnings(value.get("refit_convergence_warnings"), f"{path}.refit_convergence_warnings")
    preprocessing = _ordered(
        value.get("preprocessing_folds"),
        protocol.inner_folds,
        "fold",
        f"{path}.preprocessing_folds",
    )
    for fold, evidence in enumerate(preprocessing):
        valid_rows = train_rows // protocol.inner_folds + (fold < train_rows % protocol.inner_folds)
        _matrix(
            evidence,
            {"train_dense_bytes": train_rows - valid_rows, "validation_dense_bytes": valid_rows},
            protocol.matrix_limit_bytes,
            f"{path}.preprocessing_folds[{fold}]",
        )
    trials = _ordered(
        value.get("trials"), protocol.candidate_count, "candidate_order", f"{path}.trials"
    )
    means = []
    for index, (trial, candidate) in enumerate(zip(trials, candidates, strict=True)):
        where = f"{path}.trials[{index}]"
        _same(trial.get("params"), candidate.params, f"{where}.params")
        _same(trial.get("status"), "success", f"{where}.status")
        _require(
            "error" in trial and trial["error"] is None,
            f"{where}.error",
            "successful trial requires null error",
        )
        _number(trial.get("fit_seconds"), f"{where}.fit_seconds")
        _warnings(trial.get("convergence_warnings"), f"{where}.convergence_warnings")
        folds = _ordered(trial.get("folds"), protocol.inner_folds, "fold", f"{where}.folds")
        trial_means = {}
        for metric in ("balanced_accuracy", "roc_auc"):
            scores = [
                _number(item.get(metric), f"{where}.folds[{i}].{metric}", 0, 1)
                for i, item in enumerate(folds)
            ]
            trial_means[metric] = _mean(scores)
            _arithmetic(
                trial.get(f"mean_{metric}"), trial_means[metric], f"{where}.mean_{metric}", 0, 1
            )
        means.append(trial_means["balanced_accuracy"])
    selected = max(range(len(means)), key=lambda index: (means[index], -index))
    _same(value.get("selected_candidate_order"), selected, f"{path}.selected_candidate_order")
    _same(value.get("best_params"), candidates[selected].params, f"{path}.best_params")
    _arithmetic(
        value.get("inner_balanced_accuracy"),
        means[selected],
        f"{path}.inner_balanced_accuracy",
        0,
        1,
    )
    _matrix(
        value.get("final_preprocessing"),
        {"train_dense_bytes": train_rows, "test_dense_bytes": test_rows},
        protocol.matrix_limit_bytes,
        f"{path}.final_preprocessing",
    )
    scores = _object(value.get("outer_scores"), f"{path}.outer_scores")
    for metric in ("balanced_accuracy", "roc_auc"):
        _number(scores.get(metric), f"{path}.outer_scores.{metric}", 0, 1)
    return scores["balanced_accuracy"]


def validate_benchmark_result(result, expected_protocol: BenchmarkProtocol | None = None) -> None:
    """Require complete canonical full (default) or canonical smoke evidence.

    Raises ValueError with a field path. Does not modify or repair the input.
    Custom/reduced protocols cannot redefine research admission.
    """
    protocol = expected_protocol or BenchmarkProtocol.full()
    _require(isinstance(protocol, BenchmarkProtocol), "expected_protocol", "required protocol")
    canonical = {"full": BenchmarkProtocol.full(), "smoke": BenchmarkProtocol.smoke()}
    _require(protocol.name in canonical, "expected_protocol", "unsupported protocol")
    _same(asdict(protocol), asdict(canonical[protocol.name]), "expected_protocol")
    result = _object(result, "result")
    _same(result.get("project"), "CSCI447P033", "project")
    dataset = _object(result.get("dataset"), "dataset")
    for key in ("name", "family"):
        _require(
            isinstance(dataset.get(key), str) and bool(dataset[key].strip()),
            f"dataset.{key}",
            "required nonempty string",
        )
    for key in ("openml_id", "version"):
        _integer(dataset.get(key), f"dataset.{key}", 1)
    _require(type(dataset.get("clinical")) is bool, "dataset.clinical", "required boolean")
    _same(result.get("protocol"), asdict(protocol), "protocol")
    _same(result.get("status"), "success", "status")
    _same(result.get("research_valid"), protocol.name == "full", "research_valid")
    _require(isinstance(result.get("status_note"), str), "status_note", "required string")
    splits = result.get("outer_splits")
    _require(
        isinstance(splits, list) and len(splits) == len(protocol.outer_seeds),
        "outer_splits",
        "required complete canonical outer splits",
    )
    scores = {"GBDT": [], "DNN": []}
    descriptors = []
    totals = []
    for index, (split, seed) in enumerate(zip(splits, protocol.outer_seeds, strict=True)):
        path = f"outer_splits[{index}]"
        split = _object(split, path)
        _same(split.get("outer_seed"), seed, f"{path}.outer_seed")
        train = _integer(split.get("train_rows"), f"{path}.train_rows", protocol.inner_folds * 2)
        test = _integer(split.get("test_rows"), f"{path}.test_rows", 2)
        totals.append(train + test)
        _require(
            test == ceil((train + test) * protocol.test_size),
            path,
            "outer holdout row counts mismatch",
        )
        _same(split.get("paired_success"), True, f"{path}.paired_success")
        descriptors.append(_meta(split.get("meta_features"), train, f"{path}.meta_features"))
        families = _object(split.get("families"), f"{path}.families")
        _require(families.keys() == scores.keys(), f"{path}.families", "required both families")
        for family in scores:
            scores[family].append(
                _family(
                    families[family], family, protocol, train, test, f"{path}.families.{family}"
                )
            )
        _arithmetic(
            split.get("performance_gap_mlp_minus_gbdt"),
            scores["DNN"][-1] - scores["GBDT"][-1],
            f"{path}.performance_gap_mlp_minus_gbdt",
            -1,
            1,
        )
    _require(len(set(totals)) == 1, "outer_splits", "inconsistent dataset row counts")
    _require(
        len({item["n_features"] for item in descriptors}) == 1,
        "outer_splits",
        "inconsistent raw feature counts",
    )
    aggregate = _object(result.get("aggregate"), "aggregate")
    means = {family: _mean(values) for family, values in scores.items()}
    for family, suffix in (("GBDT", "gbdt"), ("DNN", "mlp")):
        key = f"mean_balanced_accuracy_{suffix}"
        _arithmetic(aggregate.get(key), means[family], f"aggregate.{key}", 0, 1)
    gap = means["DNN"] - means["GBDT"]
    _arithmetic(
        aggregate.get("performance_gap_mlp_minus_gbdt"),
        gap,
        "aggregate.performance_gap_mlp_minus_gbdt",
        -1,
        1,
    )
    _same(
        aggregate.get("actual_best_pipeline"),
        "DNN" if gap > 0 else "GBDT",
        "aggregate.actual_best_pipeline",
    )
    _same(
        aggregate.get("near_tie_within_margin"),
        abs(gap) <= protocol.recommendation_margin,
        "aggregate.near_tie_within_margin",
    )
    meta = _object(
        aggregate.get("meta_features_mean_over_outer_training_partitions"),
        "aggregate.meta_features",
    )
    _require(
        all(item.keys() == meta.keys() for item in descriptors),
        "aggregate.meta_features",
        "descriptor keys mismatch across outer partitions/aggregate",
    )
    for key, value in meta.items():
        _arithmetic(
            value, _mean([item[key] for item in descriptors]), f"aggregate.meta_features.{key}"
        )
