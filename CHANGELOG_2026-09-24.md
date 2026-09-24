# P033 implementation update — 2026-09-24

This archive is a full replacement for the previous project folder.

## Newly implemented

- `src/model_recommender/preprocessing.py`
  - fold-local imputation/encoding/scaling;
  - dense float64 output;
  - encoded-width detection before one-hot matrix allocation;
  - 512 MiB matrix guard.
- `src/model_recommender/model_families.py`
  - deterministic 20-candidate GBDT and MLP search sets;
  - documented baselines;
  - estimator factory.
- `src/model_recommender/runner.py`
  - stratified outer holdouts;
  - inner CV tuning;
  - identical partitions for both models;
  - trial/fold timing, scores, warning/failure logging;
  - final refit/test scoring;
  - full/smoke modes;
  - aggregate MLP-minus-GBDT gap.
- `src/model_recommender/audit.py`
  - duplicates;
  - conflicting target signatures;
  - missingness;
  - constants;
  - class counts.
- `src/model_recommender/meta_dataset.py`
  - benchmark JSON → one dataset row.
- `src/model_recommender/recommender.py`
  - dummy, ridge, decision-tree, random-forest gap regressors.
- `src/model_recommender/evaluation.py`
  - leave-one-dataset-family-out evaluation;
  - fixed-choice baselines;
  - recommendation regret;
  - gap RMSE.
- CLI commands:
  - `p033 audit ...`
  - `p033 benchmark ... --mode smoke|full`
- scripts:
  - `audit_datasets.py`
  - completed `collect_openml_results.py`
  - completed `build_meta_dataset.py`
  - completed `train_recommender.py`
  - completed `evaluate_recommender.py`
  - completed `run_reproduction.py`
- research documentation, config search spaces, schemas, and exact next-step checklist.

## Validation performed before packaging

- `pytest`: **35 passed** in the packaging environment;
- Python compile check: passed;
- JSON serialization of an end-to-end synthetic smoke benchmark: passed.

The packaging environment has no network access, so real OpenML downloads/full experiments were intentionally **not fabricated**. Run those locally from the pinned registry.
