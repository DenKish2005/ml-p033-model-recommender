# CSCI447P033: Tabular Model Recommender

Course project by Daniyar Kshibekov and Yerassyl Auyeskhan.

The goal is to recommend gradient-boosted decision trees (GBDTs) or deep networks from dataset properties such as sample size, missingness, and class imbalance, and evaluate the recommender on clinical tabular data.

The project builds on [A Data-Centric Perspective on Evaluating Machine Learning Models for Tabular Data](https://arxiv.org/abs/2407.02112) and its [reference code](https://github.com/atschalz/dc_tabeval). [OpenML](https://www.openml.org/search?type=data) is the planned dataset source.

## Setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and run from the repository root:

```bash
uv python install 3.14.7
make setup
```

This creates a local Python environment using the locked dependencies.

## Usage

Run the offline GBDT-versus-MLP demo on scikit-learn's breast cancer dataset:

```bash
make demo
```

Results are saved to `artifacts/demo.json`. This demo checks the experiment pipeline; it does not provide a validated model recommendation.

Extract meta-features from a classification CSV, replacing the path and target column below:

```bash
uv run p033 characterize data/dataset.csv --target outcome
```

Use a training partition when preparing meta-features for an experiment. The target must have at least two classes and no missing values.

Run the development checks:

```bash
make check
make test
```

## Status

The starter includes meta-feature extraction, a GBDT/MLP demo, and tests. OpenML loading, benchmarking across datasets, recommender training, and evaluation on held-out datasets are still to be implemented.

Local data and generated artifacts are ignored by Git.
