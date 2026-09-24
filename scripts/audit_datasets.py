#!/usr/bin/env python3
"""Audit registered datasets without fitting a model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from model_recommender.audit import audit_dataset
from model_recommender.datasets import DEFAULT_CACHE, DEFAULT_REGISTRY, load_dataset, read_registry


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("names", nargs="*", help="Dataset names; omit for nonclinical datasets")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--output-dir", type=Path, default=Path("results/summaries/dataset_audits"))
    args = parser.parse_args()
    registry = read_registry(args.registry)
    names = args.names or [name for name, spec in registry.items() if not spec.clinical]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summaries = []
    for name in names:
        if name not in registry:
            parser.error(f"Unknown dataset {name!r}")
        loaded = load_dataset(registry[name], args.cache_dir)
        result = audit_dataset(loaded)
        (args.output_dir / f"{name}.json").write_text(
            json.dumps(result, indent=2, allow_nan=False) + "\n"
        )
        summaries.append(result)
    print(json.dumps(summaries, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
