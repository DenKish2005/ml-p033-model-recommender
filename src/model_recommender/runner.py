"""Leakage-safe benchmark orchestration and machine-readable run logging."""

from __future__ import annotations

import warnings
from dataclasses import asdict, dataclass
from time import perf_counter

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import balanced_accuracy_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, train_test_split

from model_recommender.datasets import LoadedDataset
from model_recommender.features import characterize
from model_recommender.model_families import (
    ModelCandidate,
    build_estimator,
    candidates_for_family,
    needs_numeric_scaling,
)
from model_recommender.preprocessing import (
    DEFAULT_MATRIX_LIMIT_BYTES,
    estimate_dense_bytes,
    fit_transform_checked,
    make_preprocessor,
    transform_checked,
)


@dataclass(frozen=True)
class BenchmarkProtocol:
    name: str
    outer_seeds: tuple[int, ...]
    test_size: float
    inner_folds: int
    candidate_count: int
    tuning_seed: int = 42
    matrix_limit_bytes: int = DEFAULT_MATRIX_LIMIT_BYTES
    recommendation_margin: float = 0.01

    @classmethod
    def full(cls) -> BenchmarkProtocol:
        return cls(
            name="full",
            outer_seeds=(42, 137, 2026),
            test_size=0.25,
            inner_folds=3,
            candidate_count=20,
        )

    @classmethod
    def smoke(cls) -> BenchmarkProtocol:
        return cls(
            name="smoke",
            outer_seeds=(42,),
            test_size=0.25,
            inner_folds=2,
            candidate_count=2,
        )


def protocol_by_name(name: str) -> BenchmarkProtocol:
    if name == "full":
        return BenchmarkProtocol.full()
    if name == "smoke":
        return BenchmarkProtocol.smoke()
    raise ValueError("mode must be 'smoke' or 'full'")


def _prediction_scores(estimator, X: np.ndarray, y: pd.Series) -> dict[str, float]:
    predictions = np.asarray(estimator.predict(X))
    probabilities = np.asarray(estimator.predict_proba(X))[:, 1]
    if not np.isfinite(predictions).all() or not np.isfinite(probabilities).all():
        raise ValueError("Estimator produced non-finite predictions.")
    balanced = float(balanced_accuracy_score(y, predictions))
    roc_auc = float(roc_auc_score(y, probabilities))
    if not np.isfinite([balanced, roc_auc]).all():
        raise ValueError("Estimator produced a non-finite score.")
    return {"balanced_accuracy": balanced, "roc_auc": roc_auc}


def _empty_trial(candidate: ModelCandidate) -> dict[str, object]:
    return {
        "candidate_order": candidate.order,
        "params": candidate.params,
        "status": "success",
        "folds": [],
        "mean_balanced_accuracy": None,
        "mean_roc_auc": None,
        "fit_seconds": 0.0,
        "convergence_warnings": [],
        "error": None,
    }


def _fail_trial(trial: dict[str, object], exc: Exception) -> None:
    trial["status"] = "failure"
    trial["error"] = f"{type(exc).__name__}: {exc}"


def _fit_candidate(
    candidate: ModelCandidate,
    trial: dict[str, object],
    X_train: np.ndarray,
    y_train: pd.Series,
    X_valid: np.ndarray,
    y_valid: pd.Series,
    *,
    random_state: int,
    fold: int,
) -> None:
    started = perf_counter()
    estimator = build_estimator(candidate, random_state=random_state)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        estimator.fit(X_train, y_train)
    elapsed = perf_counter() - started
    trial["fit_seconds"] = float(trial["fit_seconds"]) + elapsed
    messages = [
        str(item.message) for item in caught if issubclass(item.category, ConvergenceWarning)
    ]
    warning_list = trial["convergence_warnings"]
    assert isinstance(warning_list, list)
    warning_list.extend(message for message in messages if message not in warning_list)
    scores = _prediction_scores(estimator, X_valid, y_valid)
    folds = trial["folds"]
    assert isinstance(folds, list)
    folds.append({"fold": fold, **scores})


def _tune_family(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    *,
    family: str,
    outer_seed: int,
    protocol: BenchmarkProtocol,
) -> dict[str, object]:
    candidates = candidates_for_family(
        family,
        count=protocol.candidate_count,
        seed=protocol.tuning_seed,
    )
    trials = [_empty_trial(candidate) for candidate in candidates]
    preprocessing_folds: list[dict[str, object]] = []
    search_started = perf_counter()

    class_counts = y_train.value_counts()
    if class_counts.min() < protocol.inner_folds:
        error = ValueError(
            f"Smallest outer-training class has {class_counts.min()} samples; "
            f"need at least {protocol.inner_folds} for inner stratified CV."
        )
        for trial in trials:
            _fail_trial(trial, error)
    else:
        splitter = StratifiedKFold(
            n_splits=protocol.inner_folds,
            shuffle=True,
            random_state=outer_seed,
        )
        for fold, (fit_index, valid_index) in enumerate(splitter.split(X_train, y_train)):
            raw_fit = X_train.iloc[fit_index]
            raw_valid = X_train.iloc[valid_index]
            y_fit = y_train.iloc[fit_index]
            y_valid = y_train.iloc[valid_index]
            try:
                preprocessor = make_preprocessor(
                    raw_fit,
                    scale_numeric=needs_numeric_scaling(family),
                )
                transformed_fit = fit_transform_checked(
                    preprocessor,
                    raw_fit,
                    limit_bytes=protocol.matrix_limit_bytes,
                )
                transformed_valid = transform_checked(
                    preprocessor,
                    raw_valid,
                    limit_bytes=protocol.matrix_limit_bytes,
                )
                assert preprocessor.n_output_features_ is not None
                preprocessing_folds.append(
                    {
                        "fold": fold,
                        "n_encoded_features": preprocessor.n_output_features_,
                        "train_dense_bytes": estimate_dense_bytes(
                            len(raw_fit), preprocessor.n_output_features_
                        ),
                        "validation_dense_bytes": estimate_dense_bytes(
                            len(raw_valid), preprocessor.n_output_features_
                        ),
                    }
                )
            except Exception as exc:  # retained as diagnostic evidence in the result
                for trial in trials:
                    if trial["status"] == "success":
                        _fail_trial(trial, exc)
                break

            for candidate, trial in zip(candidates, trials, strict=True):
                if trial["status"] != "success":
                    continue
                try:
                    _fit_candidate(
                        candidate,
                        trial,
                        transformed_fit,
                        y_fit,
                        transformed_valid,
                        y_valid,
                        random_state=outer_seed,
                        fold=fold,
                    )
                except Exception as exc:  # do not replace failed trials per protocol
                    _fail_trial(trial, exc)

    for trial in trials:
        folds = trial["folds"]
        assert isinstance(folds, list)
        if trial["status"] == "success" and len(folds) == protocol.inner_folds:
            trial["mean_balanced_accuracy"] = float(
                np.mean([item["balanced_accuracy"] for item in folds])
            )
            trial["mean_roc_auc"] = float(np.mean([item["roc_auc"] for item in folds]))
        elif trial["status"] == "success":
            _fail_trial(trial, ValueError("Not every inner fold completed."))

    all_completed = all(trial["status"] == "success" for trial in trials)
    result: dict[str, object] = {
        "family": family,
        "model": candidates[0].model,
        "all_trials_completed": all_completed,
        "search_seconds": perf_counter() - search_started,
        "trials": trials,
        "preprocessing_folds": preprocessing_folds,
        "selected_candidate_order": None,
        "best_params": None,
        "inner_balanced_accuracy": None,
        "outer_scores": None,
        "refit_seconds": None,
        "refit_convergence_warnings": [],
        "final_preprocessing": None,
        "error": None,
    }
    if not all_completed:
        result["error"] = "Primary protocol requires every configured trial to finish every fold."
        return result

    selected_index = max(
        range(len(trials)),
        key=lambda index: (
            float(trials[index]["mean_balanced_accuracy"]),
            -int(trials[index]["candidate_order"]),
        ),
    )
    selected_trial = trials[selected_index]
    selected_candidate = candidates[selected_index]
    result["selected_candidate_order"] = selected_candidate.order
    result["best_params"] = selected_candidate.params
    result["inner_balanced_accuracy"] = selected_trial["mean_balanced_accuracy"]
    return result


def _refit_family(
    family_result: dict[str, object],
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    *,
    outer_seed: int,
    protocol: BenchmarkProtocol,
) -> None:
    if not family_result["all_trials_completed"]:
        return
    candidate = ModelCandidate(
        family=str(family_result["family"]),
        model=str(family_result["model"]),
        order=int(family_result["selected_candidate_order"]),
        params=dict(family_result["best_params"]),
    )
    try:
        preprocessor = make_preprocessor(
            X_train,
            scale_numeric=needs_numeric_scaling(candidate.family),
        )
        transformed_train = fit_transform_checked(
            preprocessor,
            X_train,
            limit_bytes=protocol.matrix_limit_bytes,
        )
        transformed_test = transform_checked(
            preprocessor,
            X_test,
            limit_bytes=protocol.matrix_limit_bytes,
        )
        assert preprocessor.n_output_features_ is not None
        family_result["final_preprocessing"] = {
            "n_encoded_features": preprocessor.n_output_features_,
            "train_dense_bytes": estimate_dense_bytes(
                len(X_train), preprocessor.n_output_features_
            ),
            "test_dense_bytes": estimate_dense_bytes(len(X_test), preprocessor.n_output_features_),
        }
        estimator = build_estimator(candidate, random_state=outer_seed)
        started = perf_counter()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            estimator.fit(transformed_train, y_train)
        family_result["refit_seconds"] = perf_counter() - started
        family_result["refit_convergence_warnings"] = list(
            dict.fromkeys(
                str(item.message)
                for item in caught
                if issubclass(item.category, ConvergenceWarning)
            )
        )
        family_result["outer_scores"] = _prediction_scores(estimator, transformed_test, y_test)
    except Exception as exc:  # keep partial search evidence
        family_result["all_trials_completed"] = False
        family_result["error"] = f"Final refit/scoring failed: {type(exc).__name__}: {exc}"


def _validate_outer_split(y: pd.Series, protocol: BenchmarkProtocol) -> None:
    counts = y.value_counts()
    if len(counts) != 2:
        raise ValueError("The initial benchmark protocol supports binary classification only.")
    if counts.min() < max(2, protocol.inner_folds):
        raise ValueError(
            "Each class needs enough observations for stratified outer and inner splits."
        )


def run_benchmark(
    loaded: LoadedDataset,
    *,
    protocol: BenchmarkProtocol | None = None,
) -> dict[str, object]:
    """Run the paired GBDT-vs-MLP benchmark on one validated dataset."""

    protocol = protocol or BenchmarkProtocol.full()
    _validate_outer_split(loaded.y, protocol)
    outer_results: list[dict[str, object]] = []

    for outer_seed in protocol.outer_seeds:
        X_train, X_test, y_train, y_test = train_test_split(
            loaded.X,
            loaded.y,
            test_size=protocol.test_size,
            random_state=outer_seed,
            stratify=loaded.y,
        )
        meta_features = characterize(X_train, y_train)
        families: dict[str, dict[str, object]] = {}
        for family in ("GBDT", "DNN"):
            family_result = _tune_family(
                X_train,
                y_train,
                family=family,
                outer_seed=outer_seed,
                protocol=protocol,
            )
            _refit_family(
                family_result,
                X_train,
                y_train,
                X_test,
                y_test,
                outer_seed=outer_seed,
                protocol=protocol,
            )
            families[family] = family_result

        paired_success = all(
            families[family]["all_trials_completed"]
            and families[family]["outer_scores"] is not None
            for family in ("GBDT", "DNN")
        )
        performance_gap = None
        if paired_success:
            performance_gap = float(
                families["DNN"]["outer_scores"]["balanced_accuracy"]
                - families["GBDT"]["outer_scores"]["balanced_accuracy"]
            )
        outer_results.append(
            {
                "outer_seed": outer_seed,
                "train_rows": len(X_train),
                "test_rows": len(X_test),
                "meta_features": meta_features,
                "families": families,
                "paired_success": paired_success,
                "performance_gap_mlp_minus_gbdt": performance_gap,
            }
        )

    primary_success = all(item["paired_success"] for item in outer_results)
    aggregate: dict[str, object] | None = None
    if primary_success:
        gbdt_scores = [
            item["families"]["GBDT"]["outer_scores"]["balanced_accuracy"] for item in outer_results
        ]
        mlp_scores = [
            item["families"]["DNN"]["outer_scores"]["balanced_accuracy"] for item in outer_results
        ]
        gap = float(np.mean(mlp_scores) - np.mean(gbdt_scores))
        meta_keys = outer_results[0]["meta_features"].keys()
        meta_features = {
            key: float(np.mean([item["meta_features"][key] for item in outer_results]))
            for key in meta_keys
        }
        aggregate = {
            "mean_balanced_accuracy_gbdt": float(np.mean(gbdt_scores)),
            "mean_balanced_accuracy_mlp": float(np.mean(mlp_scores)),
            "performance_gap_mlp_minus_gbdt": gap,
            "actual_best_pipeline": "DNN" if gap > 0 else "GBDT",
            "near_tie_within_margin": abs(gap) <= protocol.recommendation_margin,
            "meta_features_mean_over_outer_training_partitions": meta_features,
        }

    return {
        "project": "CSCI447P033",
        "dataset": {
            "name": loaded.spec.name,
            "openml_id": loaded.spec.openml_id,
            "version": loaded.spec.version,
            "family": loaded.spec.family,
            "clinical": loaded.spec.clinical,
        },
        "protocol": asdict(protocol),
        "research_valid": protocol.name == "full" and primary_success,
        "status": "success" if primary_success else "excluded",
        "status_note": (
            "Full protocol result eligible for meta-learning."
            if protocol.name == "full" and primary_success
            else "Smoke mode is development-only."
            if protocol.name == "smoke" and primary_success
            else "At least one required model trial/refit failed; retained for diagnostics only."
        ),
        "outer_splits": outer_results,
        "aggregate": aggregate,
    }
