#!/usr/bin/env python3
"""Evaluate a regression recommender with held-out dataset-family folds."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from model_recommender.evaluation import evaluate_recommender


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--meta", type=Path, default=Path("results/meta_dataset.csv"))
    parser.add_argument(
        "--model",
        choices=("dummy_mean", "ridge", "decision_tree", "random_forest"),
        default="ridge",
    )
    parser.add_argument(
        "--predictions",
        type=Path,
        default=Path("results/summaries/recommender_predictions.csv"),
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("results/summaries/recommender_summary.json"),
    )
    args = parser.parse_args()
    frame = pd.read_csv(args.meta)
    predictions, summary = evaluate_recommender(frame, model_name=args.model)
    args.predictions.parent.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(args.predictions, index=False)
    args.summary.write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n")
    print(json.dumps(summary, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
