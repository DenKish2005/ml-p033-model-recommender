# CSCI447P033 Repository Architecture

This scaffold complements the existing starter without replacing any existing files.

## Research flow

1. Reproduce/audit the upstream `atschalz/dc_tabeval` implementation.
2. Register general OpenML tabular datasets.
3. Benchmark comparable GBDT and DNN families under the same experimental regime.
4. Extract dataset-level meta-features.
5. Build a meta-dataset: one row = one dataset.
6. Train a simple model-family recommender.
7. Evaluate on entirely held-out datasets with leakage-safe splits.
8. Test transfer to clinical tabular datasets.
9. Run ablations, error analysis, and generate final figures/tables.

## Important

The current repository ignores `data/` and `artifacts/`. Those directories are local working storage and are not expected to be committed. Tracked schemas live in `schemas/`, while reproducible summaries/figures live in `results/`.

## Current implementation

The initial experiment follows [the protocol](docs/experiment-protocol.md). The pilot registry is `configs/datasets.toml`; `datasets.py` implements its validation, caching, and loading. Separate `registry.py` and `openml_loader.py` modules are reserved placeholders, not alternative implementations. Experiment configs and remaining pipeline modules are plans, not an implemented benchmark runner.
