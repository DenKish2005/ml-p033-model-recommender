#!/usr/bin/env python3
"""Record a no-source-edit upstream dc_tabeval reproduction attempt.

Run this helper from the P033 repository, but point it at a separately cloned
upstream repository and its Python 3.11.7 interpreter/environment.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from time import time


def run(command: list[str], *, cwd: Path) -> dict[str, object]:
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo", type=Path, required=True, help="Separate atschalz/dc_tabeval clone"
    )
    parser.add_argument(
        "--python",
        default="python",
        help="Python executable from the upstream 3.11.7 environment",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/checkpoint1/upstream_reproduction.json"),
    )
    args = parser.parse_args()
    repo = args.repo.resolve()
    if not (repo / "run_experiment.py").exists():
        parser.error(f"{repo} does not look like the upstream dc_tabeval repository")

    evidence = {
        "utc_epoch_started": time(),
        "repo": str(repo),
        "git_remote": run(["git", "remote", "-v"], cwd=repo),
        "git_head": run(["git", "rev-parse", "HEAD"], cwd=repo),
        "git_latest": run(
            ["git", "log", "-1", "--date=iso", "--format=%H%n%ad%n%s"], cwd=repo
        ),
        "python_version": run([args.python, "--version"], cwd=repo),
        "experiment": run([args.python, "run_experiment.py"], cwd=repo),
    }
    evidence["success"] = evidence["experiment"]["returncode"] == 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"success": evidence["success"], "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
