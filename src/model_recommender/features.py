import numpy as np
import pandas as pd


def characterize(X: pd.DataFrame, y: pd.Series) -> dict[str, int | float]:
    if X.empty:
        raise ValueError("Dataset must have at least one row and one feature.")
    if len(X) != len(y) or not X.index.equals(y.index):
        raise ValueError("Features and target must have matching rows and indices.")
    if y.isna().any():
        raise ValueError("Target contains missing values.")
    counts = y.value_counts()
    if len(counts) < 2:
        raise ValueError("Classification requires at least two target classes.")
    numeric = X.select_dtypes(include="number")
    if np.isinf(numeric.to_numpy(dtype=float)).any():
        raise ValueError("Numeric features contain infinite values.")
    return {
        "n_samples": len(X),
        "n_features": X.shape[1],
        "n_classes": len(counts),
        "samples_per_feature": len(X) / X.shape[1],
        "categorical_fraction": 1 - numeric.shape[1] / X.shape[1],
        "missing_fraction": float(X.isna().to_numpy().mean()),
        "rows_with_missing_fraction": float(X.isna().any(axis=1).mean()),
        "constant_feature_fraction": float((X.nunique(dropna=False) <= 1).mean()),
        "minority_class_fraction": float(counts.min() / len(y)),
        "imbalance_ratio": float(counts.max() / counts.min()),
    }
