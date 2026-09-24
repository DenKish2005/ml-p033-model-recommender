"""Leakage-safe preprocessing shared by the benchmark runner.

A custom lightweight preprocessor is used instead of ``ColumnTransformer.fit`` so
the encoded feature width can be learned *before* the dense float64 design matrix
is allocated. This makes the 512 MiB per-matrix protocol guard meaningful even
for high-cardinality categorical datasets.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

DEFAULT_MATRIX_LIMIT_BYTES = 512 * 1024 * 1024
FLOAT_BYTES = np.dtype(np.float64).itemsize


class MatrixTooLargeError(ValueError):
    """Raised before a transformed dense matrix would exceed the protocol limit."""


@dataclass(frozen=True)
class FeatureRoles:
    numeric: tuple[str, ...]
    categorical: tuple[str, ...]

    @property
    def all(self) -> tuple[str, ...]:
        return self.numeric + self.categorical


def infer_feature_roles(X: pd.DataFrame) -> FeatureRoles:
    if not isinstance(X, pd.DataFrame) or X.shape[1] == 0:
        raise ValueError("Expected a non-empty pandas DataFrame.")
    if not X.columns.is_unique:
        raise ValueError("Feature columns must be unique.")
    numeric = tuple(str(column) for column in X.select_dtypes(include="number").columns)
    categorical = tuple(str(column) for column in X.columns if str(column) not in numeric)
    return FeatureRoles(numeric=numeric, categorical=categorical)


@dataclass
class DensePreprocessor:
    roles: FeatureRoles
    scale_numeric: bool
    numeric_imputer: SimpleImputer | None = field(init=False, default=None)
    numeric_scaler: StandardScaler | None = field(init=False, default=None)
    categorical_imputer: SimpleImputer | None = field(init=False, default=None)
    onehot: OneHotEncoder | None = field(init=False, default=None)
    n_output_features_: int | None = field(init=False, default=None)
    _feature_names: np.ndarray | None = field(init=False, default=None)
    _ready: bool = field(init=False, default=False)

    def _validate_columns(self, X: pd.DataFrame) -> None:
        missing = set(self.roles.all) - set(X.columns)
        if missing:
            raise ValueError(f"Missing preprocessing columns: {sorted(missing)}")

    def fit_structure(self, X: pd.DataFrame) -> "DensePreprocessor":
        """Fit imputers/encoder and determine final width without materialising one-hot output."""

        self._validate_columns(X)
        names: list[str] = []
        total = 0

        if self.roles.numeric:
            self.numeric_imputer = SimpleImputer(
                strategy="median",
                add_indicator=True,
                keep_empty_features=True,
            )
            self.numeric_imputer.fit(X.loc[:, self.roles.numeric])
            numeric_names = self.numeric_imputer.get_feature_names_out(self.roles.numeric)
            names.extend(str(name) for name in numeric_names)
            total += len(numeric_names)

        if self.roles.categorical:
            self.categorical_imputer = SimpleImputer(
                strategy="constant",
                fill_value="__missing__",
                keep_empty_features=True,
            )
            categorical = X.loc[:, self.roles.categorical]
            self.categorical_imputer.fit(categorical)
            # This intermediate object array has only the original categorical width;
            # the potentially huge one-hot float64 matrix is not produced here.
            categorical_imputed = self.categorical_imputer.transform(categorical)
            self.onehot = OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False,
                dtype=np.float64,
            )
            self.onehot.fit(categorical_imputed)
            categorical_names = self.onehot.get_feature_names_out(self.roles.categorical)
            names.extend(str(name) for name in categorical_names)
            total += len(categorical_names)

        self.n_output_features_ = total
        self._feature_names = np.asarray(names, dtype=object)
        return self

    def fit_scaler(self, X: pd.DataFrame) -> None:
        if self.scale_numeric and self.roles.numeric:
            assert self.numeric_imputer is not None
            numeric = self.numeric_imputer.transform(X.loc[:, self.roles.numeric])
            self.numeric_scaler = StandardScaler()
            self.numeric_scaler.fit(numeric)
        self._ready = True

    def get_feature_names_out(self) -> np.ndarray:
        if self._feature_names is None:
            raise ValueError("Preprocessor structure has not been fitted.")
        return self._feature_names.copy()

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        if not self._ready:
            raise ValueError("Preprocessor is not ready; use fit_transform_checked first.")
        self._validate_columns(X)
        blocks: list[np.ndarray] = []
        if self.roles.numeric:
            assert self.numeric_imputer is not None
            numeric = np.asarray(
                self.numeric_imputer.transform(X.loc[:, self.roles.numeric]),
                dtype=np.float64,
            )
            if self.numeric_scaler is not None:
                numeric = np.asarray(self.numeric_scaler.transform(numeric), dtype=np.float64)
            blocks.append(numeric)
        if self.roles.categorical:
            assert self.categorical_imputer is not None and self.onehot is not None
            categorical = self.categorical_imputer.transform(X.loc[:, self.roles.categorical])
            blocks.append(np.asarray(self.onehot.transform(categorical), dtype=np.float64))
        return blocks[0] if len(blocks) == 1 else np.hstack(blocks)


def make_preprocessor(X: pd.DataFrame, *, scale_numeric: bool) -> DensePreprocessor:
    return DensePreprocessor(infer_feature_roles(X), scale_numeric=scale_numeric)


def estimate_dense_bytes(n_rows: int, n_features: int) -> int:
    return int(n_rows) * int(n_features) * FLOAT_BYTES


def ensure_dense_matrix_fits(
    preprocessor: DensePreprocessor,
    n_rows: int,
    *,
    limit_bytes: int = DEFAULT_MATRIX_LIMIT_BYTES,
) -> int:
    if preprocessor.n_output_features_ is None:
        raise ValueError("Preprocessor structure must be fitted before size is checked.")
    required = estimate_dense_bytes(n_rows, preprocessor.n_output_features_)
    if required > limit_bytes:
        mib = required / (1024 * 1024)
        limit_mib = limit_bytes / (1024 * 1024)
        raise MatrixTooLargeError(
            f"Dense transformed matrix would require {mib:.1f} MiB, "
            f"above the {limit_mib:.1f} MiB protocol limit."
        )
    return required


def fit_transform_checked(
    preprocessor: DensePreprocessor,
    X_train: pd.DataFrame,
    *,
    limit_bytes: int = DEFAULT_MATRIX_LIMIT_BYTES,
) -> np.ndarray:
    preprocessor.fit_structure(X_train)
    ensure_dense_matrix_fits(preprocessor, len(X_train), limit_bytes=limit_bytes)
    preprocessor.fit_scaler(X_train)
    return preprocessor.transform(X_train)


def transform_checked(
    preprocessor: DensePreprocessor,
    X: pd.DataFrame,
    *,
    limit_bytes: int = DEFAULT_MATRIX_LIMIT_BYTES,
) -> np.ndarray:
    ensure_dense_matrix_fits(preprocessor, len(X), limit_bytes=limit_bytes)
    return preprocessor.transform(X)
