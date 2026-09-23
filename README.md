# CSCI447P033: Tabular Model Recommender

Course project by Daniyar Kshibekov and Yerassyl Auyeskhan.

The goal is to recommend gradient-boosted decision trees (GBDTs) or deep networks from dataset properties such as sample size, missingness, and class imbalance, and evaluate the recommender on clinical tabular data.

The project builds on [A Data-Centric Perspective on Evaluating Machine Learning Models for Tabular Data](https://arxiv.org/abs/2407.02112) and its [reference code](https://github.com/atschalz/dc_tabeval). [OpenML](https://www.openml.org/search?type=data) is the planned dataset source.

The reference study uses ten Kaggle competition datasets to examine the effects of preprocessing, feature engineering, and hyperparameter tuning on model rankings. Our extension asks whether dataset meta-features can predict a useful model choice on unseen datasets, including clinical data.

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

List the pinned pilot datasets and download them into the local OpenML cache:

```bash
uv run p033 datasets
make data
```

Fetch one dataset with `uv run p033 fetch credit-g`. Use `--registry` or `--cache-dir`
to override the default paths. Run commands from the repository root. `make data` writes a
validation summary to `artifacts/datasets.json`; downloads are cached under `data/openml`.

The [registry](configs/datasets.toml) pins five nonclinical pilots: credit-g, ionosphere,
spambase, adult, and tic-tac-toe. It records provenance, feature roles, families, and split
assumptions. `fetch all` excludes clinical datasets, which are reserved for transfer evaluation.

The loader validates dataset identity, checksum, schema, and classes, preserves missing values,
and encodes the registered positive class as `1`. Splitting and preprocessing belong to the
benchmark runner. Five pilots exercise the pipeline; recommender evaluation needs more datasets.

Run the development checks:

```bash
make check
make test
```

## Status

The project includes meta-feature extraction, a GBDT/MLP demo, a pinned five-dataset registry,
cached OpenML loading with validation, and tests. Benchmarking across datasets, recommender
training, and evaluation on held-out datasets are still to be implemented.

Local data and generated artifacts are ignored by Git.

## Planned experiment

Compare tuned HistGradientBoosting and MLP pipelines on binary classification datasets, then learn to select between them from dataset meta-features. See the [experiment protocol](docs/experiment-protocol.md) for the planned evaluation; it is not yet implemented by the CLI or demo.

Next: audit pilot duplicates and implement the benchmark runner using the registered split
constraints and experiment protocol, then expand the registry beyond the pilot datasets.
