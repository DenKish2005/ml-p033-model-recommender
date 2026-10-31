"""Build the one-row-per-dataset table used by the meta-learning recommender."""

from __future__ import annotations

import json
from dataclasses import dataclass
from math import isfinite
from pathlib import Path

import pandas as pd

from model_recommender.result_validation import validate_benchmark_result
from model_recommender.runner import BenchmarkProtocol

META_TARGET = "performance_gap_mlp_minus_gbdt"
IDENTIFIER_COLUMNS = {"dataset", "openml_id", "version", "family", "clinical"}
OUTCOME_COLUMNS = {
    META_TARGET,
    "mean_balanced_accuracy_gbdt",
    "mean_balanced_accuracy_mlp",
    "actual_best_pipeline",
    "near_tie_within_margin",
}


@dataclass
class ResultSelection:
    """Accepted payloads and a JSON-serializable ledger for every supplied input."""

    accepted: list[dict[str, object]]
    report: dict[str, object]


class NoAcceptedResults(ValueError):
    def __init__(self, report):
        self.report = report
        reasons = "; ".join(entry["reason"] for entry in report["inputs"])
        super().__init__(f"No accepted canonical {report['mode']} results. {reasons}")


def _json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _json_float(value):
    number = float(value)
    if not isfinite(number):
        raise ValueError("non-finite JSON number")
    return number


def _json_constant(value):
    raise ValueError(f"non-standard JSON constant: {value}")


def _select_results(paths, protocol):
    entries, payloads = [], []
    claims = {}
    for path in sorted(map(Path, paths), key=str):
        entry = {"path": str(path), "outcome": "rejected", "code": "invalid_result", "reason": ""}
        result = None
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            entry.update(code="unreadable_input", reason=f"Unreadable input: {exc}")
        else:
            try:
                result = json.loads(
                    content,
                    object_pairs_hook=_json_object,
                    parse_float=_json_float,
                    parse_constant=_json_constant,
                )
            except (ValueError, RecursionError) as exc:
                entry.update(code="malformed_json", reason=f"Malformed JSON: {exc}")
            else:
                # Group *all* parseable claims of this project/mode, even invalid
                # ones. A successful retry cannot win by hiding conflicting evidence.
                if (
                    isinstance(result, dict)
                    and result.get("project") == "CSCI447P033"
                    and isinstance(result.get("protocol"), dict)
                    and result["protocol"].get("name") == protocol.name
                ):
                    dataset = result.get("dataset")
                    if isinstance(dataset, dict):
                        identity = {}
                        name, source, version = (
                            dataset.get(k) for k in ("name", "openml_id", "version")
                        )
                        if isinstance(name, str) and name.strip():
                            identity["name"] = name
                            claims.setdefault(("name", name), []).append(len(entries))
                        if type(source) is int and source > 0:
                            identity["openml_id"] = source
                            claims.setdefault(("openml_id", source), []).append(len(entries))
                        if type(version) is int and version > 0:
                            identity["version"] = version
                        entry["identity"] = identity
                try:
                    validate_benchmark_result(result, protocol)
                except ValueError as exc:
                    entry["reason"] = str(exc)
                else:
                    entry.update(
                        outcome="accepted",
                        code="accepted",
                        reason=f"Complete canonical {protocol.name} evidence",
                    )
        entries.append(entry)
        payloads.append(result)
    conflicts = {}
    for indices in claims.values():
        if len(indices) > 1:
            for index in indices:
                conflicts.setdefault(index, set()).update(indices)
    for index, group in conflicts.items():
        entry = entries[index]
        if entry["code"] != "accepted":
            entry["validation_reason"] = entry["reason"]
        entry.update(
            outcome="rejected",
            code="duplicate_identity",
            reason="Duplicate/conflicting source identity; all claims rejected: "
            + ", ".join(entries[i]["path"] for i in sorted(group)),
        )
    accepted = [
        result
        for entry, result in zip(entries, payloads, strict=True)
        if entry["outcome"] == "accepted"
    ]
    report = {
        "report_version": 1,
        "mode": protocol.name,
        "development_only": protocol.name == "smoke",
        "duplicate_policy": (
            "reject all same-mode claims sharing dataset name or OpenML ID (any version)"
        ),
        "input_count": len(entries),
        "accepted_count": len(accepted),
        "rejected_count": len(entries) - len(accepted),
        "inputs": entries,
    }
    return ResultSelection(accepted, report)


def select_research_results(paths: list[Path]) -> ResultSelection:
    """Deterministic full-only admission; empty selections retain a complete report.

    Duplicate/alias/conflicting full claims are all rejected, including invalid
    full claims with readable source identifiers. Smoke does not compete with full.
    Source identity is limited to recorded names/IDs/versions, not cohort dedup.
    """
    return _select_results(paths, BenchmarkProtocol.full())


def benchmark_result_to_row(
    result: dict[str, object],
    *,
    require_research_valid: bool = True,
) -> dict[str, object]:
    """Convert full research evidence, or smoke-only marked development evidence.

    Compatibility: False now means validated canonical smoke only, never bypass.
    """
    if type(require_research_valid) is not bool:
        raise ValueError("require_research_valid must be a boolean.")
    validate_benchmark_result(
        result, BenchmarkProtocol.full() if require_research_valid else BenchmarkProtocol.smoke()
    )
    aggregate = result.get("aggregate")
    if not isinstance(aggregate, dict):
        raise ValueError("Benchmark result has no aggregate scores.")
    dataset = result.get("dataset")
    if not isinstance(dataset, dict):
        raise ValueError("Benchmark result has no dataset metadata.")
    meta = aggregate.get("meta_features_mean_over_outer_training_partitions")
    if not isinstance(meta, dict):
        raise ValueError("Benchmark aggregate has no meta-features.")
    row = {
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
    if not require_research_valid:
        row.update(development_only=True, result_mode="smoke")
    return row


def build_meta_dataset(
    result_files: list[Path],
    *,
    require_research_valid: bool = True,
    report_path: Path | None = None,
) -> pd.DataFrame:
    """Build research rows; False is a compatibility alias for smoke-only development."""
    if type(require_research_valid) is not bool:
        raise ValueError("require_research_valid must be a boolean.")
    selection = (
        select_research_results(result_files)
        if require_research_valid
        else _select_results(result_files, BenchmarkProtocol.smoke())
    )
    if report_path is not None:
        if report_path.resolve() in {Path(path).resolve() for path in result_files}:
            raise ValueError("Admission report must not overwrite an input artifact.")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(selection.report, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
    rows = [
        benchmark_result_to_row(result, require_research_valid=require_research_valid)
        for result in selection.accepted
    ]
    if not rows:
        raise NoAcceptedResults(selection.report)
    frame = pd.DataFrame(rows).sort_values("dataset").reset_index(drop=True)
    frame.attrs["admission_report"] = selection.report
    return frame


def build_development_meta_dataset(
    result_files: list[Path], *, report_path: Path | None = None
) -> pd.DataFrame:
    """Build marked canonical-smoke rows only; full inputs are rejected, not mixed."""
    return build_meta_dataset(result_files, require_research_valid=False, report_path=report_path)


def meta_feature_columns(frame: pd.DataFrame) -> list[str]:
    blocked = IDENTIFIER_COLUMNS | OUTCOME_COLUMNS
    columns = [column for column in frame.columns if column not in blocked]
    if not columns:
        raise ValueError("No meta-feature columns found.")
    non_numeric = [column for column in columns if not pd.api.types.is_numeric_dtype(frame[column])]
    if non_numeric:
        raise ValueError(f"Meta-features must be numeric: {non_numeric}")
    return columns
