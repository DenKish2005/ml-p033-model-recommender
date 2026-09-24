"""Build the one-row-per-dataset table used by the meta-learning recommender."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

META_TARGET = "performance_gap_mlp_minus_gbdt"
IDENTIFIER_COLUMNS = {"dataset", "openml_id", "version", "family", "clinical"}
OUTCOME_COLUMNS = {
    META_TARGET,
    "mean_balanced_accuracy_gbdt",
    "mean_balanced_accuracy_mlp",
    "actual_best_pipeline",
    "near_tie_within_margin",
}


def benchmark_result_to_row(
    result: dict[str, object],
    *,
    require_research_valid: bool = True,
) -> dict[str, object]:
    if require_research_valid and not result.get("research_valid"):
        raise ValueError("Benchmark result is not a successful full-protocol research run.")
    aggregate = result.get("aggregate")
    if not isinstance(aggregate, dict):
        raise ValueError("Benchmark result has no aggregate scores.")
    dataset = result.get("dataset")
    if not isinstance(dataset, dict):
        raise ValueError("Benchmark result has no dataset metadata.")
    meta = aggregate.get("meta_features_mean_over_outer_training_partitions")
    if not isinstance(meta, dict):
        raise ValueError("Benchmark aggregate has no meta-features.")
    return {
        "dataset": dataset["name"],
        "openml_id": dataset["openml_id"],
        "version": dataset["version"],
        "family": dataset["family"],
        "clinical": dataset["clinical"],
        **meta,
        "mean_balanced_accuracy_gbdt": aggregate["mean_balanced_accuracy_gbdt"],
        "mean_balanced_accuracy_mlp": aggregate["mean_balanced_accuracy_mlp"],
        META_TARGET: aggregate[META_TARGET],
        "actual_best_pipeline": aggregate["actual_best_pipeline"],
        "near_tie_within_margin": aggregate["near_tie_within_margin"],
    }


def build_meta_dataset(
    result_files: list[Path],
    *,
    require_research_valid: bool = True,
) -> pd.DataFrame:
    rows = []
    for path in result_files:
        result = json.loads(path.read_text())
        rows.append(
            benchmark_result_to_row(result, require_research_valid=require_research_valid)
        )
    if not rows:
        raise ValueError("No benchmark result files were provided.")
    frame = pd.DataFrame(rows).sort_values("dataset").reset_index(drop=True)
    if frame["dataset"].duplicated().any():
        duplicates = frame.loc[frame["dataset"].duplicated(), "dataset"].tolist()
        raise ValueError(f"Meta-dataset contains duplicate dataset rows: {duplicates}")
    return frame


def meta_feature_columns(frame: pd.DataFrame) -> list[str]:
    blocked = IDENTIFIER_COLUMNS | OUTCOME_COLUMNS
    columns = [column for column in frame.columns if column not in blocked]
    if not columns:
        raise ValueError("No meta-feature columns found.")
    non_numeric = [column for column in columns if not pd.api.types.is_numeric_dtype(frame[column])]
    if non_numeric:
        raise ValueError(f"Meta-features must be numeric: {non_numeric}")
    return columns
