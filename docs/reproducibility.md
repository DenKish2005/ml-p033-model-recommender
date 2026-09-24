# Reproducibility

## Two separate environments

Do not force the original `atschalz/dc_tabeval` repository into this project's modern environment.

### Project environment

- repository: `ml-p033-model-recommender`
- Python: pinned by `.python-version` / `pyproject.toml`
- dependencies: locked by `uv.lock`
- install: `make setup`

### Upstream reproduction environment

- repository: `https://github.com/atschalz/dc_tabeval`
- reference commit currently recorded in `configs/project.toml`
- Python: 3.11.7 as specified by the upstream project
- recommended OS: Linux / WSL2
- run evidence: `scripts/checkpoint1/run_upstream_audit.sh`

Record the **actual** upstream commit returned by `git rev-parse HEAD`, OS, Python version, package versions, command, output, and errors. Do not replace a failed reproduction with invented output.

## P033 benchmark reproducibility

The full initial benchmark is fixed by `docs/experiment-protocol.md`:

- outer seeds: 42, 137, 2026;
- 75/25 stratified outer holdout;
- shuffled 3-fold inner CV;
- tuning seed: 42;
- 20 candidates per model;
- balanced accuracy primary metric;
- deterministic dataset registry IDs/versions/checksums;
- dense transformed matrix limit: 512 MiB;
- all candidate/fold failures retained in JSON.

Use `smoke` runs only for engineering validation. Build the scientific meta-dataset only from successful `full` JSON results.
