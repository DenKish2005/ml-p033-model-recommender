#!/usr/bin/env python3
"""Run registered nonclinical datasets and save one JSON result per dataset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from model_recommender.audit import audit_dataset
from model_recommender.datasets import DEFAULT_CACHE, DEFAULT_REGISTRY, load_dataset, read_registry
from model_recommender.runner import protocol_by_name, run_benchmark


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "names", nargs="*", help="Dataset names; omit for every nonclinical registry row"
    )
    parser.add_argument("--mode", choices=("smoke", "full"), default="smoke")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--output-dir", type=Path, default=Path("results/raw_model_runs"))
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("results/summaries/benchmark_index.json"),
    )
    args = parser.parse_args()

    registry = read_registry(args.registry)
    selected_names = args.names or [name for name, spec in registry.items() if not spec.clinical]
    unknown = sorted(set(selected_names) - set(registry))
    if unknown:
        parser.error(f"Unknown dataset(s): {', '.join(unknown)}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    audit_dir = Path("results/summaries/dataset_audits")
    audit_dir.mkdir(parents=True, exist_ok=True)
    protocol = protocol_by_name(args.mode)
    index: list[dict[str, object]] = []

    for name in selected_names:
        spec = registry[name]
        if spec.clinical:
            index.append({"dataset": name, "status": "skipped", "reason": "clinical holdout"})
            continue
        try:
            loaded = load_dataset(spec, args.cache_dir)
            audit = audit_dataset(loaded)
            (audit_dir / f"{name}.json").write_text(
                json.dumps(audit, indent=2, allow_nan=False) + "\n"
            )
            result = run_benchmark(loaded, protocol=protocol)
            output = args.output_dir / f"{name}.{args.mode}.json"
            output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
            index.append(
                {
                    "dataset": name,
                    "status": result["status"],
                    "research_valid": result["research_valid"],
                    "result": str(output),
                }
            )
        except Exception as exc:  # batch runner records failure and continues
            index.append(
                {
                    "dataset": name,
                    "status": "failure",
                    "research_valid": False,
                    "reason": f"{type(exc).__name__}: {exc}",
                }
            )

    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(index, indent=2, allow_nan=False) + "\n")
    print(json.dumps(index, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
