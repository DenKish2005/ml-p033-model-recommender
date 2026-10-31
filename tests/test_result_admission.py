"""Regression tests for strict admission, with small synthetic JSON only."""

from copy import deepcopy
from dataclasses import replace

import pytest
from benchmark_artifacts import complete_result

from model_recommender.meta_dataset import benchmark_result_to_row
from model_recommender.result_validation import validate_benchmark_result
from model_recommender.runner import BenchmarkProtocol


def test_spoofed_flag_cannot_admit_incomplete_full():
    payload = complete_result()
    del payload["outer_splits"]
    with pytest.raises(ValueError, match="outer_splits"):
        benchmark_result_to_row(payload)


def test_reduced_protocol_named_full_cannot_enter_research():
    payload = complete_result(smoke=True)
    payload["protocol"]["name"] = "full"
    payload["research_valid"] = True
    with pytest.raises(ValueError, match="protocol"):
        benchmark_result_to_row(payload)


def test_corrupt_aggregate_cannot_be_repaired_or_trusted():
    payload = complete_result()
    payload["aggregate"]["performance_gap_mlp_minus_gbdt"] = 0.4
    with pytest.raises(ValueError, match="performance_gap"):
        benchmark_result_to_row(payload)


def set_field(payload, path, value):
    parts = path.split("/")
    for part in parts[:-1]:
        payload = payload[int(part)] if isinstance(payload, list) else payload[part]
    key = int(parts[-1]) if isinstance(payload, list) else parts[-1]
    payload[key] = value


FAMILY = "outer_splits/0/families/GBDT/"
TRIAL = FAMILY + "trials/0/"


@pytest.mark.parametrize(
    "path,value,reason",
    [
        ("project", "other", "project"),
        ("dataset/openml_id", True, "openml_id"),
        ("dataset/version", 1.0, "version"),
        ("dataset/clinical", 0, "clinical"),
        ("dataset/name", "", "name"),
        ("protocol/outer_seeds", [42, 42, 2026], "outer_seeds"),
        ("protocol/test_size", 0.2, "test_size"),
        ("protocol/inner_folds", True, "inner_folds"),
        ("protocol/candidate_count", 2, "candidate_count"),
        ("protocol/tuning_seed", 137, "tuning_seed"),
        ("protocol/matrix_limit_bytes", 512, "matrix_limit_bytes"),
        ("protocol/recommendation_margin", 0.02, "recommendation_margin"),
        ("status", "excluded", "status"),
        ("status", "unknown", "status"),
        ("research_valid", 1, "research_valid"),
        ("outer_splits/1/outer_seed", 42, "outer_seed"),
        ("outer_splits/0/train_rows", True, "train_rows"),
        ("outer_splits/0/test_rows", 19, "row counts"),
        ("outer_splits/0/paired_success", False, "paired_success"),
        ("outer_splits/0/families", {}, "both families"),
        (FAMILY + "model", "mlp", "model"),
        (FAMILY + "all_trials_completed", False, "all_trials_completed"),
        (FAMILY + "error", "refit failed", "error"),
        (FAMILY + "refit_seconds", None, "refit_seconds"),
        (FAMILY + "search_seconds", -1, "search_seconds"),
        (FAMILY + "refit_convergence_warnings", None, "warning"),
        (FAMILY + "final_preprocessing", None, "final_preprocessing"),
        (FAMILY + "final_preprocessing/train_dense_bytes", 968, "matrix"),
        (FAMILY + "preprocessing_folds/1/fold", 0, "fold"),
        (TRIAL + "candidate_order", True, "candidate_order"),
        (TRIAL + "params/learning_rate", 0.03, "params"),
        (TRIAL + "params/l2_regularization", False, "params"),
        (TRIAL + "status", "failure", "status"),
        (TRIAL + "error", "failed", "error"),
        (TRIAL + "folds/1/fold", 0, "fold"),
        (TRIAL + "folds/0/balanced_accuracy", float("nan"), "finite"),
        (TRIAL + "folds/0/roc_auc", float("inf"), "finite"),
        (TRIAL + "folds/0/balanced_accuracy", 1.01, "finite"),
        (TRIAL + "fit_seconds", True, "numeric"),
        (TRIAL + "mean_roc_auc", 0.7, "arithmetic"),
        (TRIAL + "mean_balanced_accuracy", 0.9, "arithmetic"),
        (FAMILY + "selected_candidate_order", 0, "selected_candidate_order"),
        (FAMILY + "best_params", {}, "best_params"),
        (FAMILY + "inner_balanced_accuracy", 0.9, "inner_balanced_accuracy"),
        (FAMILY + "outer_scores/roc_auc", -0.1, "roc_auc"),
        (FAMILY + "outer_scores/balanced_accuracy", True, "numeric"),
        ("outer_splits/0/performance_gap_mlp_minus_gbdt", 0.1, "performance_gap"),
        ("aggregate/mean_balanced_accuracy_mlp", 0.8, "arithmetic"),
        ("aggregate/actual_best_pipeline", "GBDT", "actual_best_pipeline"),
        ("aggregate/near_tie_within_margin", True, "near_tie"),
        ("aggregate/near_tie_within_margin", 0, "near_tie"),
        ("aggregate/meta_features_mean_over_outer_training_partitions/n_samples", 80, "arithmetic"),
        ("outer_splits/0/meta_features/missing_fraction", -0.1, "finite"),
        ("outer_splits/0/meta_features/n_samples", 80, "n_samples"),
        ("outer_splits/0/meta_features/imbalance_ratio", 2, "imbalance_ratio"),
    ],
)
def test_reject_corrupt_required_evidence(path, value, reason):
    payload = complete_result()
    set_field(payload, path, value)
    with pytest.raises(ValueError, match=reason):
        validate_benchmark_result(payload)


@pytest.mark.parametrize(
    "path", ["outer_splits", FAMILY + "trials", TRIAL + "folds", FAMILY + "preprocessing_folds"]
)
@pytest.mark.parametrize("operation", ["missing", "duplicate"])
def test_missing_or_duplicate_entries(path, operation):
    payload = complete_result()
    target = payload
    for part in path.strip("/").split("/"):
        target = target[int(part)] if isinstance(target, list) else target[part]
    if operation == "missing":
        target.pop()
    else:
        target[1] = deepcopy(target[0])
    with pytest.raises(ValueError):
        validate_benchmark_result(payload)


def test_valid_complete_json_and_canonical_smoke_without_mutation():
    for smoke in (False, True):
        payload = complete_result(smoke=smoke)
        original = deepcopy(payload)
        validate_benchmark_result(payload, BenchmarkProtocol.smoke() if smoke else None)
        assert payload == original
    with pytest.raises(ValueError, match="protocol"):
        validate_benchmark_result(complete_result(smoke=True))
    with pytest.raises(ValueError, match="expected_protocol"):
        validate_benchmark_result(
            complete_result(), replace(BenchmarkProtocol.full(), inner_folds=2)
        )


def test_exact_inner_tie_selects_first_order_and_keeps_finite_warnings():
    payload = complete_result()
    for split in payload["outer_splits"]:
        for family in split["families"].values():
            trial = family["trials"][2]
            for fold in trial["folds"]:
                fold["balanced_accuracy"] = 0.7
            trial["mean_balanced_accuracy"] = 0.7
            trial["convergence_warnings"] = ["finite at iteration limit"]
    validate_benchmark_result(payload)
    payload["outer_splits"][0]["families"]["GBDT"]["selected_candidate_order"] = 2
    with pytest.raises(ValueError, match="selected_candidate_order"):
        validate_benchmark_result(payload)


def test_arithmetic_tolerance_does_not_relax_signature_or_params():
    payload = complete_result()
    payload["aggregate"]["mean_balanced_accuracy_mlp"] += 5e-13
    validate_benchmark_result(payload)
    payload["protocol"]["test_size"] += 5e-13
    with pytest.raises(ValueError, match="test_size"):
        validate_benchmark_result(payload)
