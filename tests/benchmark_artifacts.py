"""Synthetic, complete runner-shaped artifacts; never scientific benchmark evidence."""

import json
from dataclasses import asdict

import numpy as np

from model_recommender.model_families import candidates_for_family
from model_recommender.runner import BenchmarkProtocol


def complete_result(name="test:admission", source=900001, *, smoke=False):
    protocol = BenchmarkProtocol.smoke() if smoke else BenchmarkProtocol.full()
    splits = []
    for seed in protocol.outer_seeds:
        families = {}
        for family, outer_score in (("GBDT", 0.7), ("DNN", 0.73)):
            trials = []
            for candidate in candidates_for_family(family, count=protocol.candidate_count):
                # Order 1 wins; order 0 has the best individual fold and AUC.
                scores = ([0.9, 0.3, 0.3] if candidate.order == 0 else [0.6] * 3)[
                    : protocol.inner_folds
                ]
                if candidate.order == 1:
                    scores = [0.7] * protocol.inner_folds
                trials.append(
                    {
                        "candidate_order": candidate.order,
                        "params": candidate.params,
                        "status": "success",
                        "folds": [
                            {"fold": fold, "balanced_accuracy": score, "roc_auc": 0.8}
                            for fold, score in enumerate(scores)
                        ],
                        "mean_balanced_accuracy": float(np.mean(scores)),
                        "mean_roc_auc": 0.8,
                        "fit_seconds": 0.1,
                        "convergence_warnings": [],
                        "error": None,
                    }
                )
            families[family] = {
                "family": family,
                "model": "mlp" if family == "DNN" else "hist_gradient_boosting",
                "all_trials_completed": True,
                "search_seconds": 0.5,
                "trials": trials,
                "preprocessing_folds": [
                    {
                        "fold": fold,
                        "n_encoded_features": 2,
                        "train_dense_bytes": (60 - 60 // protocol.inner_folds) * 16,
                        "validation_dense_bytes": (60 // protocol.inner_folds) * 16,
                    }
                    for fold in range(protocol.inner_folds)
                ],
                "selected_candidate_order": 1,
                "best_params": trials[1]["params"],
                "inner_balanced_accuracy": trials[1]["mean_balanced_accuracy"],
                "outer_scores": {"balanced_accuracy": outer_score, "roc_auc": 0.8},
                "refit_seconds": 0.1,
                "refit_convergence_warnings": ["synthetic finite convergence warning"],
                "final_preprocessing": {
                    "n_encoded_features": 2,
                    "train_dense_bytes": 960,
                    "test_dense_bytes": 320,
                },
                "error": None,
            }
        meta = {
            "n_samples": 60,
            "n_features": 2,
            "n_classes": 2,
            "samples_per_feature": 30.0,
            "categorical_fraction": 0.0,
            "missing_fraction": 0.1,
            "rows_with_missing_fraction": 0.2,
            "constant_feature_fraction": 0.0,
            "minority_class_fraction": 0.4,
            "imbalance_ratio": 1.5,
        }
        splits.append(
            {
                "outer_seed": seed,
                "train_rows": 60,
                "test_rows": 20,
                "meta_features": meta,
                "families": families,
                "paired_success": True,
                "performance_gap_mlp_minus_gbdt": 0.73 - 0.7,
            }
        )
    result = {
        "project": "CSCI447P033",
        "dataset": {
            "name": name,
            "openml_id": source,
            "version": 1,
            "family": "test:family",
            "clinical": False,
        },
        "protocol": asdict(protocol),
        "research_valid": not smoke,
        "status": "success",
        "status_note": "SYNTHETIC TEST ARTIFACT; not a research result",
        "outer_splits": splits,
        "aggregate": {
            "mean_balanced_accuracy_gbdt": 0.7,
            "mean_balanced_accuracy_mlp": 0.73,
            "performance_gap_mlp_minus_gbdt": 0.73 - 0.7,
            "actual_best_pipeline": "DNN",
            "near_tie_within_margin": False,
            "meta_features_mean_over_outer_training_partitions": {
                key: float(value) for key, value in meta.items()
            },
        },
    }
    # Exercise the actual serialized list representation of MLP tuples.
    return json.loads(json.dumps(result, allow_nan=False))
