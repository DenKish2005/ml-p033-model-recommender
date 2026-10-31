#!/usr/bin/env python3
"""Build meta_dataset.csv from successful full benchmark JSON files."""

from __future__ import annotations

import argparse
from pathlib import Path

from model_recommender.meta_dataset import build_development_meta_dataset, build_meta_dataset


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path("results/raw_model_runs"),
        help="Benchmark JSON folder",
    )
    parser.add_argument(
        "--output", type=Path, help="CSV output; development requires .development.csv"
    )
    parser.add_argument(
        "--report", type=Path, help="Admission JSON; default: <output stem>.admission.json"
    )
    parser.add_argument(
        "--allow-smoke",
        action="store_true",
        help=("Development only: select validated canonical smoke inputs only, with marked rows."),
    )
    args = parser.parse_args()
    output = args.output or Path(
        "results/development/meta_dataset.development.csv"
        if args.allow_smoke
        else "results/meta_dataset.csv"
    )
    report = args.report or output.with_suffix(".admission.json")
    if args.allow_smoke and not output.name.endswith(".development.csv"):
        parser.error(
            "Development output must end with .development.csv; research CSV is forbidden."
        )
    paths = sorted(args.results_dir.glob("*.json"))
    if not args.results_dir.is_dir():
        parser.error(f"Results directory does not exist: {args.results_dir}")
    if report.resolve() == output.resolve():
        parser.error("Report and CSV output must be different paths.")
    if report.resolve().parent == args.results_dir.resolve():
        parser.error("Keep the admission report outside the benchmark JSON input directory.")
    if output.resolve() in {path.resolve() for path in paths}:
        parser.error("CSV output must not overwrite an input artifact.")
    builder = build_development_meta_dataset if args.allow_smoke else build_meta_dataset
    try:
        frame = builder(paths, report_path=report)
        output.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(output, index=False)
    except (OSError, ValueError) as exc:
        parser.error(f"{exc} Admission report: {report}")
    summary = frame.attrs["admission_report"]
    mode = "DEVELOPMENT ONLY" if args.allow_smoke else "canonical full"
    print(
        f"Wrote {len(frame)} {mode} dataset rows to {output}; "
        f"rejected {summary['rejected_count']}/{summary['input_count']}; report: {report}"
    )


if __name__ == "__main__":
    main()
