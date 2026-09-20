import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd
from sklearn.datasets import fetch_openml

from model_recommender.features import characterize

DEFAULT_REGISTRY = Path("configs/datasets.toml")
DEFAULT_CACHE = Path("data/openml")


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    openml_id: int
    version: int
    md5_checksum: str
    source_url: str
    original_source_url: str
    license: str
    family: str
    clinical: bool
    target: str
    positive_class: str
    class_labels: list[str]
    expected_rows: int
    numeric_features: list[str]
    categorical_features: list[str]
    excluded_features: list[str]
    split_strategy: str
    split_notes: str
    selection_reason: str

    def __post_init__(self) -> None:
        if not (
            len(self.class_labels) == len(set(self.class_labels)) == 2
            and self.positive_class in self.class_labels
        ):
            raise ValueError(f"{self.name}: register two classes and a matching positive class.")
        features = self.numeric_features + self.categorical_features + self.excluded_features
        if not self.numeric_features and not self.categorical_features:
            raise ValueError(f"{self.name}: no predictors registered.")
        if len(features) != len(set(features)) or self.target in features:
            raise ValueError(f"{self.name}: feature roles overlap or include the target.")
        if type(self.clinical) is not bool:
            raise ValueError(f"{self.name}: clinical must be a boolean.")


def read_registry(path: Path = DEFAULT_REGISTRY) -> dict[str, DatasetSpec]:
    with path.open("rb") as stream:
        payload = tomllib.load(stream)
    if payload.get("schema_version") != 1:
        raise ValueError("Unsupported dataset registry schema version.")
    if not isinstance(payload.get("datasets"), list) or not payload["datasets"]:
        raise ValueError("Dataset registry is empty or missing its datasets list.")
    registry = {}
    ids = set()
    for entry in payload["datasets"]:
        try:
            spec = DatasetSpec(**entry)
        except TypeError as exc:
            raise ValueError(f"Invalid dataset registry entry: {exc}") from exc
        if spec.name in registry or spec.openml_id in ids:
            raise ValueError(f"Duplicate dataset name or OpenML ID: {spec.name}.")
        registry[spec.name] = spec
        ids.add(spec.openml_id)
    return registry


@dataclass
class LoadedDataset:
    spec: DatasetSpec
    X: pd.DataFrame
    y: pd.Series

    def summary(self) -> dict:
        return {
            "dataset": asdict(self.spec),
            "n_rows": len(self.X),
            "n_features": self.X.shape[1],
            "missing_cells": int(self.X.isna().sum().sum()),
            "class_counts": {
                label: int((self.y == int(label == self.spec.positive_class)).sum())
                for label in self.spec.class_labels
            },
            "target_encoding": {
                label: int(label == self.spec.positive_class) for label in self.spec.class_labels
            },
        }


def load_dataset(spec: DatasetSpec, cache_dir: Path = DEFAULT_CACHE) -> LoadedDataset:
    dataset = fetch_openml(
        data_id=spec.openml_id,
        target_column=spec.target,
        as_frame=True,
        parser="pandas",
        cache=True,
        data_home=str(cache_dir),
    )
    expected = {
        "id": str(spec.openml_id),
        "name": spec.name,
        "version": str(spec.version),
        "md5_checksum": spec.md5_checksum,
    }
    for key, value in expected.items():
        if str(dataset.details.get(key)) != value:
            raise ValueError(f"{spec.name}: OpenML {key} does not match the registry.")
    X, target = dataset.data, dataset.target
    if not isinstance(X, pd.DataFrame) or not isinstance(target, pd.Series):
        raise ValueError(f"{spec.name}: expected a feature frame and one target column.")
    if target.name != spec.target or len(X) != spec.expected_rows:
        raise ValueError(f"{spec.name}: target name or row count does not match the registry.")
    columns = spec.numeric_features + spec.categorical_features + spec.excluded_features
    if not X.columns.is_unique or set(X.columns) != set(columns):
        raise ValueError(f"{spec.name}: feature columns do not match the registry.")
    X = X.drop(columns=spec.excluded_features).copy()
    numeric = set(X.select_dtypes(include="number").columns)
    if numeric != set(spec.numeric_features):
        raise ValueError(f"{spec.name}: numeric feature types do not match the registry.")
    if target.isna().any():
        raise ValueError(f"{spec.name}: target contains missing values.")
    labels = target.astype(str)
    if set(labels.unique()) != set(spec.class_labels):
        raise ValueError(f"{spec.name}: observed classes do not match the registry.")
    for column in spec.categorical_features:
        X[column] = X[column].astype("category")
    y = labels.eq(spec.positive_class).astype("int64").rename(spec.target)
    characterize(X, y)
    return LoadedDataset(spec, X, y)
