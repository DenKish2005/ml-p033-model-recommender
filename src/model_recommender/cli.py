import argparse
import json
from pathlib import Path

import pandas as pd

from model_recommender.audit import audit_dataset
from model_recommender.benchmark import run_demo
from model_recommender.datasets import DEFAULT_CACHE, DEFAULT_REGISTRY, load_dataset, read_registry
from model_recommender.features import characterize
from model_recommender.runner import protocol_by_name, run_benchmark


def _write_or_print(result: object, output: Path | None) -> None:
    payload = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload)
    else:
        print(payload, end="")


def main() -> None:
    parser = argparse.ArgumentParser(description="CSCI447P033 tabular model-selection experiments")
    commands = parser.add_subparsers(dest="command", required=True)

    demo = commands.add_parser("demo", help="Run an offline GBDT/MLP classification smoke test")
    demo.add_argument("--seed", type=int, default=42)
    demo.add_argument("--output", type=Path)

    describe = commands.add_parser("characterize", help="Extract classification CSV meta-features")
    describe.add_argument("csv", type=Path)
    describe.add_argument("--target", required=True)
    describe.add_argument("--output", type=Path)

    datasets = commands.add_parser("datasets", help="List the pinned dataset registry")
    datasets.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    datasets.add_argument("--output", type=Path)

    fetch = commands.add_parser("fetch", help="Download and validate a registered dataset")
    fetch.add_argument("name", help="Registered dataset name, or 'all' for development datasets")
    fetch.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    fetch.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE)
    fetch.add_argument("--output", type=Path)

    audit = commands.add_parser("audit", help="Audit duplicates/missingness before benchmarking")
    audit.add_argument("name", help="Registered dataset name")
    audit.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    audit.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE)
    audit.add_argument("--output", type=Path)

    benchmark = commands.add_parser("benchmark", help="Run paired GBDT-vs-MLP benchmark")
    benchmark.add_argument("name", help="Registered dataset name")
    benchmark.add_argument(
        "--mode",
        choices=("smoke", "full"),
        default="smoke",
        help="smoke validates the pipeline; full is the research protocol",
    )
    benchmark.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    benchmark.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE)
    benchmark.add_argument("--output", type=Path)

    args = parser.parse_args()
    try:
        if args.command == "demo":
            result = run_demo(args.seed)
        elif args.command in {"datasets", "fetch", "audit", "benchmark"}:
            registry = read_registry(args.registry)
            if args.command == "datasets":
                result = {
                    name: {
                        "openml_id": spec.openml_id,
                        "version": spec.version,
                        "family": spec.family,
                        "clinical": spec.clinical,
                        "expected_rows": spec.expected_rows,
                        "n_features": len(spec.numeric_features) + len(spec.categorical_features),
                    }
                    for name, spec in registry.items()
                }
            elif args.command == "fetch":
                if args.name == "all":
                    selected = [spec for spec in registry.values() if not spec.clinical]
                elif args.name in registry:
                    selected = [registry[args.name]]
                else:
                    raise ValueError(f"Unknown dataset {args.name!r}; run 'p033 datasets'.")
                result = [load_dataset(spec, args.cache_dir).summary() for spec in selected]
            else:
                if args.name not in registry:
                    raise ValueError(f"Unknown dataset {args.name!r}; run 'p033 datasets'.")
                loaded = load_dataset(registry[args.name], args.cache_dir)
                if args.command == "audit":
                    result = audit_dataset(loaded)
                else:
                    result = run_benchmark(loaded, protocol=protocol_by_name(args.mode))
        else:
            frame = pd.read_csv(args.csv)
            if args.target not in frame:
                raise ValueError(f"Target column {args.target!r} does not exist.")
            result = characterize(frame.drop(columns=[args.target]), frame[args.target])
        _write_or_print(result, args.output)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
