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
        ("dataset/openml_id", 10**400, "finite"),
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
        ("outer_splits/0/outer_seed", 42.0, "integer"),
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
        (TRIAL + "params/max_leaf_nodes", 31.0, "integer"),
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
        (FAMILY + "outer_scores/balanced_accuracy", float("nan"), "finite"),
        ("outer_splits/0/performance_gap_mlp_minus_gbdt", 0.1, "performance_gap"),
        ("aggregate/mean_balanced_accuracy_mlp", 0.8, "arithmetic"),
        ("aggregate/actual_best_pipeline", "GBDT", "actual_best_pipeline"),
        ("aggregate/near_tie_within_margin", True, "near_tie"),
        ("aggregate/near_tie_within_margin", 0, "near_tie"),
        ("aggregate/meta_features_mean_over_outer_training_partitions/n_samples", 80, "arithmetic"),
        ("outer_splits/0/meta_features/missing_fraction", -0.1, "finite"),
        ("outer_splits/0/meta_features/n_samples", 80, "n_samples"),
        ("outer_splits/0/meta_features/imbalance_ratio", 2, "imbalance_ratio"),
        ("outer_splits/0/meta_features/minority_class_fraction", 0.401, "minority_class_fraction"),
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


def test_correct_byte_arithmetic_above_matrix_limit_is_still_rejected():
    payload = complete_result()
    matrix = payload["outer_splits"][0]["families"]["GBDT"]["final_preprocessing"]
    width = 536870912 // (60 * 8) + 1
    matrix.update(
        n_encoded_features=width, train_dense_bytes=60 * width * 8, test_dense_bytes=20 * width * 8
    )
    with pytest.raises(ValueError, match="size/limit"):
        validate_benchmark_result(payload)


@pytest.mark.parametrize("expected", [False, 0, "full"])
def test_expected_protocol_cannot_be_an_untyped_default_alias(expected):
    with pytest.raises(ValueError, match="expected_protocol"):
        validate_benchmark_result(complete_result(), expected)


@pytest.mark.parametrize(
    "missing", ["params", "mean_balanced_accuracy", "error", "convergence_warnings"]
)
def test_missing_trial_fields_rejected(missing):
    payload = complete_result()
    del payload["outer_splits"][0]["families"]["GBDT"]["trials"][0][missing]
    with pytest.raises(ValueError, match=missing):
        validate_benchmark_result(payload)


def test_json_hidden_layers_and_unexpected_parameter_keys_are_exact():
    payload = complete_result()
    params = payload["outer_splits"][0]["families"]["DNN"]["trials"][0]["params"]
    assert params["hidden_layer_sizes"] == [32, 16]
    validate_benchmark_result(payload)
    params["hidden_layer_sizes"][1] = 17
    with pytest.raises(ValueError, match="hidden_layer_sizes"):
        validate_benchmark_result(payload)
    params["hidden_layer_sizes"][1] = 16
    params["unexpected"] = 1
    with pytest.raises(ValueError, match="keys mismatch"):
        validate_benchmark_result(payload)


def test_v1_extensions_are_numeric_without_becoming_an_allowlist():
    payload = complete_result()
    for split in payload["outer_splits"]:
        split["meta_features"]["test_extra_descriptor"] = -2.0
    meta = payload["aggregate"]["meta_features_mean_over_outer_training_partitions"]
    meta["test_extra_descriptor"] = -2.0
    validate_benchmark_result(payload)
    payload["outer_splits"][0]["meta_features"]["dataset"] = 123
    with pytest.raises(ValueError, match="collides"):
        validate_benchmark_result(payload)


def test_large_imbalanced_descriptor_uses_class_count_arithmetic():
    payload = complete_result()
    train, test = 36631, 12211
    for split in payload["outer_splits"]:
        split.update(train_rows=train, test_rows=test)
        split["meta_features"].update(
            n_samples=train,
            samples_per_feature=train / 2,
            minority_class_fraction=3 / train,
            imbalance_ratio=(train - 3) / 3,
        )
        for family in split["families"].values():
            family["final_preprocessing"].update(
                train_dense_bytes=train * 16, test_dense_bytes=test * 16
            )
            for index, fold in enumerate(family["preprocessing_folds"]):
                valid = train // 3 + (index < train % 3)
                fold.update(
                    train_dense_bytes=(train - valid) * 16, validation_dense_bytes=valid * 16
                )
    payload["aggregate"]["meta_features_mean_over_outer_training_partitions"].update(
        {k: float(v) for k, v in payload["outer_splits"][0]["meta_features"].items()}
    )
    validate_benchmark_result(payload)


@pytest.mark.parametrize("gap", [0.0, -0.03, 0.005, 0.01])
def test_paired_triples_means_descriptors_winner_and_near_tie(gap):
    import numpy as np

    payload = complete_result()
    for index, split in enumerate(payload["outer_splits"]):
        split["families"]["GBDT"]["outer_scores"]["balanced_accuracy"] = 0.5 + index * 0.1
        split["families"]["DNN"]["outer_scores"]["balanced_accuracy"] = 0.5 + index * 0.1 + gap
        split["performance_gap_mlp_minus_gbdt"] = (
            split["families"]["DNN"]["outer_scores"]["balanced_accuracy"]
            - split["families"]["GBDT"]["outer_scores"]["balanced_accuracy"]
        )
        split["meta_features"]["missing_fraction"] = index * 0.1
    agg = payload["aggregate"]
    for family, suffix in (("GBDT", "gbdt"), ("DNN", "mlp")):
        agg[f"mean_balanced_accuracy_{suffix}"] = float(
            np.mean(
                [
                    s["families"][family]["outer_scores"]["balanced_accuracy"]
                    for s in payload["outer_splits"]
                ]
            )
        )
    actual_gap = agg["mean_balanced_accuracy_mlp"] - agg["mean_balanced_accuracy_gbdt"]
    agg["performance_gap_mlp_minus_gbdt"] = actual_gap
    agg["actual_best_pipeline"] = "DNN" if actual_gap > 0 else "GBDT"
    agg["near_tie_within_margin"] = abs(actual_gap) <= 0.01
    agg["meta_features_mean_over_outer_training_partitions"]["missing_fraction"] = 0.1
    validate_benchmark_result(payload)
    row = benchmark_result_to_row(payload)
    assert row["performance_gap_mlp_minus_gbdt"] == pytest.approx(gap)
    assert row["missing_fraction"] == 0.1
    assert row["actual_best_pipeline"] == ("DNN" if gap > 0 else "GBDT")
    assert row["near_tie_within_margin"] is (abs(actual_gap) <= 0.01)
