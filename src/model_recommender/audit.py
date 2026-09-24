"""Dataset quality checks used before expensive benchmark runs."""

from __future__ import annotations

import pandas as pd

from model_recommender.datasets import LoadedDataset


def audit_dataset(loaded: LoadedDataset) -> dict[str, object]:
    X = loaded.X
    y = loaded.y
    feature_hash = pd.util.hash_pandas_object(X, index=False)
    full_hash = pd.util.hash_pandas_object(pd.concat([X, y], axis=1), index=False)

    feature_sizes = feature_hash.value_counts()
    duplicate_feature_rows = int(feature_sizes[feature_sizes > 1].sum())
    duplicate_feature_groups = int((feature_sizes > 1).sum())

    combined = pd.DataFrame({"signature": feature_hash, "target": y.to_numpy()})
    conflicting = combined.groupby("signature", sort=False)["target"].nunique()
    conflicting_signatures = set(conflicting[conflicting > 1].index)
    conflicting_rows = int(combined["signature"].isin(conflicting_signatures).sum())

    full_sizes = full_hash.value_counts()
    exact_duplicate_rows = int(full_sizes[full_sizes > 1].sum())
    exact_duplicate_groups = int((full_sizes > 1).sum())

    class_counts = {
        str(label): int(count) for label, count in y.value_counts().sort_index().items()
    }
    missing_by_column = {
        str(column): int(count)
        for column, count in X.isna().sum().items()
        if int(count) > 0
    }

    return {
        "dataset": loaded.spec.name,
        "openml_id": loaded.spec.openml_id,
        "n_rows": len(X),
        "n_features": X.shape[1],
        "class_counts_encoded": class_counts,
        "missing_cells": int(X.isna().sum().sum()),
        "missing_by_column": missing_by_column,
        "constant_columns": [
            str(column) for column in X.columns if X[column].nunique(dropna=False) <= 1
        ],
        "duplicate_feature_rows": duplicate_feature_rows,
        "duplicate_feature_groups": duplicate_feature_groups,
        "exact_duplicate_rows": exact_duplicate_rows,
        "exact_duplicate_groups": exact_duplicate_groups,
        "conflicting_target_signature_rows": conflicting_rows,
        "conflicting_target_signature_groups": len(conflicting_signatures),
        "notes": (
            "Duplicate counts are diagnostics. Conflicting-target signatures deserve "
            "manual review; "
            "the benchmark runner does not silently delete rows."
        ),
    }
