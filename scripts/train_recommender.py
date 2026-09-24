#!/usr/bin/env python3
"""Fit the current recommender on all supplied meta-dataset rows and print diagnostics.

Formal performance claims must come from scripts/evaluate_recommender.py, not this in-sample fit.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from model_recommender.recommender import train_recommender


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--meta", type=Path, default=Path("results/meta_dataset.csv"))
    parser.add_argument(
        "--model",
        choices=("dummy_mean", "ridge", "decision_tree", "random_forest"),
        default="ridge",
    )
    args = parser.parse_args()
    frame = pd.read_csv(args.meta)
    trained = train_recommender(frame, name=args.model)
    output = {
        "model": trained.name,
        "n_datasets": len(frame),
        "features": trained.features,
        "margin": trained.margin,
        "warning": "In-sample fit only; use held-out-family evaluation for performance claims.",
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
