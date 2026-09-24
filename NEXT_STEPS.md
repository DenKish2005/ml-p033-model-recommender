# CSCI447P033 — What to do next

The repository now contains the engineering pipeline needed for the next phase. Do the steps below in order; do not jump to clinical transfer yet.

## 0. Install and verify

```bash
make setup
make check
make test
```

Expected unit-test baseline for this packaged version: **35 tests passing**.

## 1. Keep upstream reproduction separate

Clone `https://github.com/atschalz/dc_tabeval` into a separate folder/WSL environment using Python 3.11.7. Do not copy its old dependencies into this project.

Record the real attempt:

```bash
uv run python scripts/run_reproduction.py \
  --repo /path/to/dc_tabeval \
  --python /path/to/python3.11
```

A documented upstream failure is still evidence. Do not invent output.

## 2. Download the five pilot OpenML datasets

```bash
make data
```

The registry pins:

- `credit-g`
- `ionosphere`
- `spambase`
- `adult`
- `tic-tac-toe`

## 3. Audit before fitting models

Start with:

```bash
make audit DATASET=credit-g
```

Then audit all pilots:

```bash
uv run python scripts/audit_datasets.py
```

Review duplicate predictor signatures, conflicting-target signatures, missingness, and constant columns. The audit records issues; it does **not** silently delete data.

## 4. First end-to-end smoke benchmark

```bash
make smoke DATASET=credit-g
```

This runs a reduced development protocol:

- one outer seed;
- two candidates per model;
- two inner folds.

The output should appear at:

`results/raw_model_runs/credit-g.smoke.json`

A successful smoke run proves that loading → splitting → preprocessing → tuning → refit → scoring → JSON logging works. **Smoke results are not research-valid.**

## 5. Smoke all five pilots

```bash
uv run python scripts/collect_openml_results.py --mode smoke
```

Inspect:

- `results/summaries/benchmark_index.json`
- `results/summaries/dataset_audits/`
- `results/raw_model_runs/*.smoke.json`

Resolve failures before expensive runs.

## 6. First full research run

Run one dataset first:

```bash
make full DATASET=credit-g
```

The full protocol is deliberately expensive:

- 3 outer splits;
- 20 GBDT candidates + 20 MLP candidates;
- 3 inner folds;
- 360 inner fits + 6 final refits per dataset.

Only successful full runs have `research_valid: true` and are eligible for the meta-dataset.

## 7. Full five-pilot benchmark

After the first full dataset is clean:

```bash
uv run python scripts/collect_openml_results.py --mode full
```

Do not treat five datasets as enough for the final recommender. They are an engineering pilot.

## 8. Expand the nonclinical registry

Target progression:

1. 5 pilots — engineering validation;
2. 10 datasets — early sanity check;
3. 20–30 datasets — minimum useful meta-learning study;
4. 30–60 datasets — stronger target if compute allows.

Every added dataset needs a pinned OpenML ID/version/checksum, family/group identifier, feature roles, target/positive class, provenance, and split notes.

## 9. Build the meta-dataset

Once enough successful `.full.json` files exist:

```bash
make meta
```

The output is:

`results/meta_dataset.csv`

One row = one dataset. The regression target is:

`MLP mean balanced accuracy - GBDT mean balanced accuracy`.

## 10. Evaluate the recommender

```bash
make evaluate
```

This uses held-out dataset-family folds and reports selection regret. Compare at least:

- dummy mean gap;
- ridge;
- shallow decision tree;
- random forest;
- always GBDT;
- always DNN;
- training-selected best fixed pipeline;
- oracle.

Do not report in-sample recommender fit as performance.

## 11. Only then move to clinical transfer

Clinical work remains intentionally later. First freeze the nonclinical protocol and recommender. Then register public clinical tabular holdouts with patient-level/temporal splitting where required.

---

## Windows CMD / PowerShell equivalents (no `make` required)

If `make` is not installed on Windows, use these commands from the repository root:

```text
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run pytest

uv run p033 fetch all --output artifacts/datasets.json
uv run p033 audit credit-g --output results/summaries/dataset_audits/credit-g.json
uv run p033 benchmark credit-g --mode smoke --output results/raw_model_runs/credit-g.smoke.json
uv run p033 benchmark credit-g --mode full --output results/raw_model_runs/credit-g.full.json

uv run python scripts/collect_openml_results.py --mode smoke
uv run python scripts/collect_openml_results.py --mode full
uv run python scripts/build_meta_dataset.py
uv run python scripts/evaluate_recommender.py --model ridge
```

Use `smoke` first. A full run is intentionally much heavier.
