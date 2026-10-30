# Reproducibility

## Two separate environments

Do not force the original `atschalz/dc_tabeval` repository into this project's modern environment.

### Project environment

- repository: `ml-p033-model-recommender`
- Python: pinned by `.python-version` / `pyproject.toml`
- dependencies: locked by `uv.lock`
- install: `make setup`

## Portable locked setup (P033-002)

Run from the repository root. Python **3.14.7** comes from
[.python-version](../.python-version); [pyproject.toml](../pyproject.toml) requires
`>=3.14.7,<3.15`, and [uv.lock](../uv.lock) fixes runtime/dev versions and distribution
hashes. Use **uv 0.12.18**, matching [CI](../.github/workflows/ci.yml). Do not run
`uv lock --upgrade` or substitute the system Python during an experiment.
The build backend is separately pinned to `hatchling==1.32.3` in pyproject;
isolated build dependencies are not a complete hermetic build lock.
See the official [uv command reference](https://docs.astral.sh/uv/reference/cli/)
and [GitHub Actions guide](https://docs.astral.sh/uv/guides/integration/github/).

The examples below install into a **new** ignored environment, preserving `.venv`.
Choose an unused `artifacts/repro-env` path for each clean-install attempt. Use a
fresh shell and close it afterwards to discard environment overrides. Stop on any
nonzero command exit. No activation or `make` is required.

### PowerShell

```powershell
$root = (Get-Location).Path
$env:UV_CACHE_DIR = Join-Path $root 'artifacts/repro-cache'
$env:UV_PROJECT_ENVIRONMENT = Join-Path $root 'artifacts/repro-env'
$env:TEMP = Join-Path $root 'artifacts/repro-temp'
$env:TMP = $env:TEMP
if (Test-Path -LiteralPath $env:UV_PROJECT_ENVIRONMENT) { throw 'Choose a new environment path' }
New-Item -ItemType Directory -Force -Path $env:TEMP | Out-Null
uv --version
uv python install 3.14.7
uv sync --locked
```

### CMD (save as a `.cmd` file in the repository root)

```batch
@echo off
setlocal
set "UV_CACHE_DIR=%CD%\artifacts\repro-cache"
set "UV_PROJECT_ENVIRONMENT=%CD%\artifacts\repro-env"
set "TEMP=%CD%\artifacts\repro-temp"
set "TMP=%TEMP%"
if exist "%UV_PROJECT_ENVIRONMENT%" exit /b 1
if not exist "%TEMP%" mkdir "%TEMP%"
uv --version || exit /b 1
uv python install 3.14.7 || exit /b 1
uv sync --locked || exit /b 1
rem Append the common checks below before endlocal.
endlocal
```

### bash (Ubuntu; also the shell used in both CI jobs)

```bash
set -eu
export UV_CACHE_DIR="$PWD/artifacts/repro-cache"
export UV_PROJECT_ENVIRONMENT="$PWD/artifacts/repro-env"
export TMPDIR="$PWD/artifacts/repro-temp"
test ! -e "$UV_PROJECT_ENVIRONMENT"
mkdir -p "$TMPDIR"
uv --version
uv python install 3.14.7
uv sync --locked
```

### Common checks after successful installation

These commands work in PowerShell, CMD and bash. In a CMD script, append
`|| exit /b 1` to each check and place them before `endlocal`.

```text
uv run --locked --offline python -c "import sys, platform; print(sys.version); print(sys.prefix); print(platform.platform())"
uv lock --check --offline
uv run --locked --offline ruff check .
uv run --locked --offline ruff format --check .
uv run --locked --offline python -c "from pathlib import Path; Path('artifacts/repro-tests').mkdir(parents=True, exist_ok=True)"
uv run --locked --offline pytest -q --basetemp=artifacts/repro-tests/first
uv run --locked --offline pytest -q --basetemp=artifacts/repro-tests/repeat
uv run --locked --offline p033 --help
uv run --locked --offline p033 datasets --output artifacts/repro-registry.json
```

The workspace Temp/cache workaround avoids writes to restricted system Temp and
the default uv cache. **Create the basetemp parent first**: pytest creates the last
component, not missing parents. `--basetemp` is managed/cleared by pytest; use only
a dedicated disposable test directory, never a dataset or environment directory.
The cached installation/build may still require network the first time. A later
`uv sync --locked --offline` works only if the interpreter, distributions and
build requirements are already available. `--dry-run` is not installation evidence.

For an independent checkout, clone into a new permitted folder (for example
`git clone https://github.com/DenKish2005/ml-p033-model-recommender.git artifacts/repro-checkout`),
enter it, record `git rev-parse HEAD`, then follow the same instructions. The local
P033-002 check used a new environment in the existing checkout; clean checkouts
are additionally exercised by hosted CI. This is not independent human acceptance
of the complete T14 research/submission workflow.

### Offline boundary and opt-in source checks

[tests/conftest.py](../tests/conftest.py) blocks Python socket creation, connections
and DNS during each default test. Existing OpenML loader tests use mocked responses;
the small runner test uses synthetic data. [test_offline.py](../tests/test_offline.py)
checks that accidental socket/DNS use fails. `uv --offline` controls uv's own
networking; the pytest fixture controls test-body Python networking. Neither is an
OS firewall: collection-time imports, pre-existing socket aliases, subprocesses and
native networking are outside this fixture's guarantee. Current test/source review
found no such network path in the default suite.

Future real OpenML/dataset tests must use `@pytest.mark.network`; they are skipped
unless `--run-network` is explicitly passed. Even with that flag, unmarked tests
remain socket-blocked. The current suite has **no live network tests**; the following
is the opt-in selection contract, not evidence that a real dataset was checked:

```text
uv run --locked pytest -m network --run-network
```

Real `p033 fetch`, `audit`, `benchmark`, data/smoke/full Make targets and upstream
scripts are separate explicit operator actions. They are absent from default CI.
Dataset downloads, real benchmarks and upstream reproduction were not run for
P033-002; their source/protocol gates remain in later backlog tasks.

### Validation evidence, 2026-10-30

This is **new P033-002 evidence**, separate from the historical 35-test audit in
[PROJECT_AUDIT.md](PROJECT_AUDIT.md). Applicable scope: T08 environment/offline CI,
FR-039, NFR-003/007/012/013/018/019/020; not all future T08/T14 scenarios.

| Check | Actual result / limitation |
|---|---|
| Local host/tools | Windows 11 build 26200, PowerShell; system Python 3.12.10; project CPython 3.14.7; uv 0.12.18; gh 2.96.0 |
| Project packages | numpy 2.5.3, pandas 3.0.6, scikit-learn 1.9.1, pytest 9.1.1, Ruff 0.16.8; pins/lock unchanged |
| Before edits | `uv lock --check --offline` exit 0; `uv run --locked --offline pytest -q --basetemp=artifacts/p033002/baseline-tmp --tb=short`: **35 passed in 11.66 s** |
| Actual clean install | First `artifacts/p033002/clean-env` attempt failed with sandbox DNS error fetching wheels; partial environment retained, not counted as success. Second new `artifacts/p033002/clean-env-2`, workspace UV_CACHE_DIR/TEMP/TMP, `uv sync --locked --python .venv/Scripts/python.exe` with permitted network: **19 packages installed**, exit 0 (28.11 s preparation, 1.61 s installation). Existing `.venv` retained |
| Clean environment compatibility | `uv pip check --python artifacts/p033002/clean-env-2/Scripts/python.exe`: 19 packages compatible; interpreter 3.14.7 and package versions match above |
| Offline repetition | Existing `.venv`: **38 passed**, 9.66 s / 10.04 s; new environment: **38 passed**, 24.34 s / 10.59 s. Separate pytest processes/basetemps, including socket guard regressions; timing includes cold imports, not a benchmark |
| Quality/lock/CLI | Ruff check and format check exit 0 (63 format units); `uv lock --check --offline` resolves 19 packages, exit 0; real offline `p033 --help` / `p033 datasets --output artifacts/p033002/registry.json` exit 0 |
| Initial remote CI | [run 41019463627](https://github.com/DenKish2005/ml-p033-model-recommender/actions/runs/41019463627), commit `12670b1`: **failure on both OS**, 34 passed / 4 setup errors, missing `artifacts/ci` parent. Locked install/lint/format passed. Fix: explicit parent creation and setup-uv `cache-local-path`; no blind rerun |
| Fresh-parent regression after fix | Two local offline runs with newly created `artifacts/p033002/fresh-parent-check`: **38 passed**, 7.65 s / 9.75 s; lock/Ruff/format exit 0 |
| Opt-in isolation | Temporary synthetic probe under ignored `artifacts/p033002`, loading the actual conftest: default **1 passed / 1 skipped**; `--run-network` **2 passed**. Marked probe only created/closed a socket; unmarked probe remained blocked. No connection or DNS performed |
| Shell checks | PowerShell above; CMD and Git Bash executed equivalent setup/check sequences in separate new `artifacts/p033002/cmd-env` / `bash-env`, reusing the warmed cache with `uv sync --locked --offline`: 19 packages installed each, lock/Ruff/format and two 38-test runs each passed. CMD tests 19.18 s / 8.57 s; Git Bash 19.18 s / 8.53 s. CLI help/registry also passed. Sandbox initially denied uv managed-Python lock / MSYS startup; permitted execution resolved these host restrictions. Git Bash on Windows is not a local Ubuntu installation |
| Clean hosted matrix, attempt 1 | [run 41019812975, attempt 1](https://github.com/DenKish2005/ml-p033-model-recommender/actions/runs/41019812975/attempts/1), fix `567320d`: **success on both OS**, Ubuntu 24.04.5 (17 applicable packages), Windows Server 2025 build 26100 (19). Python 3.14.7 / uv 0.12.18; lock/lint/format green. Ubuntu **38 passed**, 4.49 s / 1.73 s; Windows **38 passed**, 5.60 s / 1.71 s |
| Consecutive clean matrix, attempt 2 | [same SHA, full new hosted jobs, attempt 2](https://github.com/DenKish2005/ml-p033-model-recommender/actions/runs/41019812975/attempts/2): **success on both OS**, fresh checkout/interpreter/env/install, no cache restore. Ubuntu **38 passed**, 4.52 s / 1.88 s; Windows **38 passed**, 5.28 s / 1.57 s. Both install/lock/lint/format steps passed. This full successful-run repetition verifies NFR-019; it was not a retry of an unexplained failure |

CI installs Python from `.python-version` and locked dependencies online, then runs
lock/lint/format/tests offline. Job timeout is 15 minutes; install and each pytest
step have 5-minute limits. Both OS execute the suite twice. Matrix fail-fast is off;
workflow/ref concurrency cancels superseded runs, not retries failures. Cache restore
is disabled so each hosted run starts with a fresh environment and downloads wheels.
Two consecutive successful clean matrix attempts after the infrastructure fix are
linked above. P033-002 is DONE within that environment/CI scope; no required platform
or clean-install check remains pending. Real OpenML/upstream, future T08 CLI/E2E
cases and full T14 independent research reproduction remain unverified and belong
to later tasks. Scores across OS, bitwise reproducibility and the complete G1 gate
are not certified by passing the present suite.

## Upstream reproduction environment

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
