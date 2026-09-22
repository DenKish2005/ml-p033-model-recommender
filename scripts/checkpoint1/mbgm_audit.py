#!/usr/bin/env python3
"""CSCI447P033 Checkpoint 1: audit Mercedes-Benz Greener Manufacturing files."""

import argparse
from pathlib import Path
import pandas as pd

TARGET = "y"
ID_COL = "ID"

def _missing(df: pd.DataFrame, name: str) -> None:
    missing = df.isna().sum()
    nonzero = missing[missing > 0]
    print(f"\n[{name}] missing cells total: {int(missing.sum())}")
    if nonzero.empty:
        print(f"[{name}] columns with missing values: NONE")
    else:
        for col, count in nonzero.items():
            print(f"  {col}: {int(count)}")

def _overlap(left: pd.DataFrame, right: pd.DataFrame, cols: list[str]) -> int:
    if not cols:
        return 0
    return len(left[cols].drop_duplicates().merge(right[cols].drop_duplicates(), on=cols, how="inner"))

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", required=True)
    parser.add_argument("--test", required=True)
    args = parser.parse_args()
    train_path, test_path = Path(args.train), Path(args.test)
    train, test = pd.read_csv(train_path), pd.read_csv(test_path)

    print("=== CSCI447P033 / MBGM DATA AUDIT ===")
    print(f"train file: {train_path.resolve()}")
    print(f"test file : {test_path.resolve()}")
    print("\n1) SHAPES AFTER LOADING")
    print(f"train.shape = {train.shape}")
    print(f"test.shape  = {test.shape}")
    print(f"number of predictors in train = {train.shape[1] - (1 if TARGET in train.columns else 0)}")

    print("\n2) FIRST FIVE TRAIN ROWS — PLAIN TEXT")
    with pd.option_context("display.max_columns", None, "display.width", None):
        print(train.head(5).to_string(index=False))

    print("\n3) TARGET / CLASS DISTRIBUTION")
    if TARGET in train:
        y = train[TARGET]
        print("Task type: regression; class distribution = NOT APPLICABLE.")
        print(f"target column = {TARGET}")
        print(f"target count  = {int(y.count())}")
        print(f"target min    = {y.min()}")
        print(f"target max    = {y.max()}")
        print(f"target mean   = {y.mean()}")
        print(f"target std    = {y.std()}")

    predictor_cols = [c for c in train.columns if c != TARGET]
    categorical_cols = [c for c in predictor_cols if train[c].dtype == "object" or str(train[c].dtype).startswith("category")]
    print("\nFEATURE TYPES IN LOADED TRAIN FILE")
    print(f"predictor count       = {len(predictor_cols)}")
    print(f"categorical count     = {len(categorical_cols)}")
    print(f"non-categorical count = {len(predictor_cols) - len(categorical_cols)}")
    print(f"categorical columns   = {categorical_cols}")
    _missing(train, "TRAIN")
    _missing(test, "TEST")

    print("\n5) TRAIN/TEST OVERLAP CHECK")
    common = [c for c in predictor_cols if c in test.columns]
    print(f"exact unique predictor rows shared between train and test (including ID): {_overlap(train, test, common)}")
    signature = [c for c in common if c != ID_COL]
    print(f"unique predictor signatures shared between train and test (excluding ID): {_overlap(train, test, signature)}")
    if signature:
        print(f"train rows belonging to a duplicated predictor signature (excluding ID): {int(train.duplicated(subset=signature, keep=False).sum())}")
        print(f"test rows belonging to a duplicated predictor signature (excluding ID): {int(test.duplicated(subset=signature, keep=False).sum())}")
    print("\nCV NOTE")
    print("For MBGM, the upstream repository uses shuffled 10-fold KFold; there is no permanent validation CSV.")
    print("\n=== END AUDIT ===")

if __name__ == "__main__":
    main()
