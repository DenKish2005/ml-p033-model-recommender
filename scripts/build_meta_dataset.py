#!/usr/bin/env python3
"""Build meta_dataset.csv from successful full benchmark JSON files."""

from __future__ import annotations

import argparse
from pathlib import Path

from model_recommender.meta_dataset import build_meta_dataset


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path("results/raw_model_runs"),
        help="Benchmark JSON folder",
    )
    parser.add_argument("--output", type=Path, default=Path("results/meta_dataset.csv"))
    parser.add_argument(
        "--allow-smoke",
        action="store_true",
        help=(
            "Development only: permit successful smoke JSONs; do not use for research conclusions."
        ),
    )
    args = parser.parse_args()
    paths = sorted(args.results_dir.glob("*.json"))
    frame = build_meta_dataset(paths, require_research_valid=not args.allow_smoke)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output, index=False)
    print(f"Wrote {len(frame)} dataset rows to {args.output}")


if __name__ == "__main__":
    main()
