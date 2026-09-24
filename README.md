# CSCI447P033: Tabular Model Recommender

Course project by Daniyar Kshibekov and Yerassyl Auyeskhan.

The project asks whether **dataset-level meta-features** can predict which of two tabular ML pipelines will perform better on an unseen dataset. The first implemented benchmark compares `HistGradientBoostingClassifier` (GBDT) with `MLPClassifier` (DNN-like baseline), then predicts the continuous performance gap from dataset characteristics. A later stage evaluates transfer to clinical tabular data.

The work builds on **A Data-Centric Perspective on Evaluating Machine Learning Models for Tabular Data** and its `atschalz/dc_tabeval` reference implementation. The upstream reproduction remains separate from this modern project environment.

## What is implemented now

- pinned five-dataset OpenML registry with metadata/checksum validation;
- raw-dataset meta-feature extraction;
- duplicate/missingness/conflicting-signature audit;
- leakage-safe numeric/categorical preprocessing;
- median imputation + missing indicators;
- categorical constant imputation + dense one-hot encoding;
- MLP numeric scaling;
- pre-allocation 512 MiB dense-matrix guard;
- deterministic HistGradientBoosting and MLP candidate sets;
- nested benchmark runner with paired outer/inner splits;
- `smoke` and `full` benchmark modes;
- machine-readable trial/failure/warning/result logging;
- meta-dataset builder (one row = one dataset);
- performance-gap regression recommenders;
- held-out dataset-family evaluation and recommendation regret;
- upstream reproduction evidence helper;
- unit tests.

No real full OpenML benchmark results are bundled in this archive. Those must be produced on the user's machine from the pinned public sources.

## Setup

Install `uv`, then run from the repository root:

```bash
uv python install 3.14.7
make setup
make check
make test
```

## Quick workflow

### 1. Download pilot data

```bash
make data
```

### 2. Audit one dataset

```bash
make audit DATASET=credit-g
```

### 3. Run one fast end-to-end smoke benchmark

```bash
make smoke DATASET=credit-g
```

Output:

`results/raw_model_runs/credit-g.smoke.json`

Smoke mode is for engineering validation only and sets `research_valid: false`.

### 4. Run the full research protocol for one dataset

```bash
make full DATASET=credit-g
```

Output:

`results/raw_model_runs/credit-g.full.json`

A successful full run has `research_valid: true` and can enter the meta-dataset.

### 5. Run all registered nonclinical datasets

Development first:

```bash
uv run python scripts/collect_openml_results.py --mode smoke
```

Then, after smoke failures are resolved:

```bash
uv run python scripts/collect_openml_results.py --mode full
```

### 6. Build the meta-dataset

```bash
make meta
```

This consumes successful full benchmark JSON files and creates:

`results/meta_dataset.csv`

### 7. Evaluate the recommender

```bash
make evaluate
```

The initial meta-target is:

`MLP mean balanced accuracy - GBDT mean balanced accuracy`.

DNN is recommended only when predicted advantage is greater than `0.01`; otherwise GBDT is selected. This margin is an operational near-tie rule, not a statistical-equivalence claim.

## CLI

```bash
uv run p033 datasets
uv run p033 fetch credit-g
uv run p033 audit credit-g
uv run p033 benchmark credit-g --mode smoke
uv run p033 benchmark credit-g --mode full
uv run p033 characterize path/to/data.csv --target outcome
```

## Pilot registry

The current engineering pilots are:

- `credit-g`
- `ionosphere`
- `spambase`
- `adult`
- `tic-tac-toe`

Five datasets are **not enough** for final meta-learning claims. After validating the runner, expand toward at least 20–30 nonclinical datasets; 30–60 is the stronger target if compute allows.

## Experiment design

The authoritative protocol is in [`docs/experiment-protocol.md`](docs/experiment-protocol.md).

Full mode uses:

- outer seeds `42`, `137`, `2026`;
- stratified 75/25 outer splits;
- shuffled 3-fold inner CV;
- 20 deterministic candidate configurations/model;
- balanced accuracy as the primary metric;
- ROC-AUC and timing as secondary diagnostics;
- all-or-nothing eligibility: every candidate/fold and final refit must succeed;
- one aggregated meta-learning row per dataset.

The recommender is evaluated with complete dataset-family holdouts rather than random row splitting of the meta-table.

## Upstream reproduction

Keep `atschalz/dc_tabeval` in a separate Linux/WSL + Python 3.11.7 environment. Do **not** install its old pinned stack into this project's environment.

Record a real run/failure with:

```bash
uv run python scripts/run_reproduction.py \
  --repo /path/to/dc_tabeval \
  --python /path/to/python3.11
```

## Documentation

- [`NEXT_STEPS.md`](NEXT_STEPS.md) — exact order of work from here;
- [`docs/experiment-protocol.md`](docs/experiment-protocol.md) — scientific protocol;
- [`docs/decisions.md`](docs/decisions.md) — design decisions and rationale;
- [`docs/reproducibility.md`](docs/reproducibility.md) — environment/evidence rules;
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — repository flow.

## Important interpretation limit

The implemented first-stage result is a recommendation between **HistGradientBoosting and MLP pipelines**. It is not yet evidence that one entire model family (“all GBDTs” or “all DNNs”) is preferable. Family-level claims require adding and validating multiple models per family later.

Local OpenML caches and generated artifacts are intentionally not committed.
