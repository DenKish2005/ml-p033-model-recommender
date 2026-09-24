# CSCI447P033 Repository Architecture

## End-to-end flow

```text
OpenML registry
    ↓
validated raw dataset
    ├── dataset audit
    └── raw outer-train meta-features
             ↓
paired nested benchmark
    ├── HistGradientBoosting
    └── MLP
             ↓
full benchmark JSON per dataset
             ↓
meta_dataset.csv
(one row = one dataset)
             ↓
performance-gap regression recommender
             ↓
held-out dataset-family evaluation
             ↓
clinical transfer (later)
```

## Implemented core modules

- `datasets.py` — pinned OpenML loading and validation.
- `audit.py` — duplicates, missingness, constant columns, conflicting target signatures.
- `features.py` — raw dataset meta-features.
- `preprocessing.py` — fold-local imputing/encoding/scaling + dense memory guard.
- `model_families.py` — deterministic GBDT/MLP candidates and estimator construction.
- `runner.py` — nested paired benchmark, full/smoke modes, diagnostics, aggregation.
- `meta_dataset.py` — benchmark JSON → one-row-per-dataset table.
- `recommender.py` — regression meta-model baselines.
- `evaluation.py` — held-out dataset-family evaluation and selection regret.

## Scripts

- `scripts/audit_datasets.py` — audit registered pilots.
- `scripts/collect_openml_results.py` — batch smoke/full benchmark runner.
- `scripts/build_meta_dataset.py` — create `results/meta_dataset.csv`.
- `scripts/evaluate_recommender.py` — leakage-safe meta-level evaluation.
- `scripts/train_recommender.py` — diagnostic all-data fit only.
- `scripts/run_reproduction.py` — capture upstream Git/Python/run evidence.

## Still intentionally later

- clinical registry/transfer implementation;
- broader model-family coverage (XGBoost/CatBoost/LightGBM, FT-Transformer/ResNet/etc.);
- richer meta-feature ablations;
- final publication figures/report automation.

## Storage

`data/` and `artifacts/` are ignored local storage. `results/` holds generated research outputs; decide what summaries/figures to commit after the experiment protocol is frozen.
