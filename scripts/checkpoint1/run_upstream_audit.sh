#!/usr/bin/env bash
# Run this from the ROOT of a cloned atschalz/dc_tabeval repository.
set -u
LOG="checkpoint1_run.log"
{
  echo "=== CSCI447P033 CODE AUDIT ==="
  date -u
  echo "=== GIT ==="
  git remote -v
  git rev-parse HEAD
  git log -1 --date=iso --format='%H%n%ad%n%s'
  echo "=== OS ==="
  uname -a
  [ -f /etc/os-release ] && cat /etc/os-release
  echo "=== PYTHON ==="
  python --version
  echo "=== IMPORTANT INSTALLED PACKAGES ==="
  python - <<'PY2'
from importlib.metadata import version, PackageNotFoundError
for p in ["catboost", "xgboost", "lightgbm", "torch", "tensorflow", "autogluon", "pandas", "numpy"]:
    try:
        print(f"{p}=={version(p)}")
    except PackageNotFoundError:
        print(f"{p}: NOT INSTALLED")
PY2
  echo "=== ATTEMPT: python run_experiment.py ==="
  python run_experiment.py
} 2>&1 | tee "$LOG"
tail -n 10 "$LOG" | tee checkpoint1_last10.txt
