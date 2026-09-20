import argparse
import json
from pathlib import Path

import pandas as pd

from model_recommender.benchmark import run_demo
from model_recommender.features import characterize


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
    args = parser.parse_args()
    try:
        if args.command == "demo":
            result = run_demo(args.seed)
        else:
            frame = pd.read_csv(args.csv)
            if args.target not in frame:
                raise ValueError(f"Target column {args.target!r} does not exist.")
            result = characterize(frame.drop(columns=[args.target]), frame[args.target])
        payload = json.dumps(result, indent=2, allow_nan=False) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(payload)
        else:
            print(payload, end="")
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
