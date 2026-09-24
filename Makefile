.PHONY: setup check test demo data audit smoke full meta evaluate
DATASET ?= credit-g

setup:
	uv sync --locked
check:
	uv run ruff check .
	uv run ruff format --check .
test:
	uv run pytest
demo:
	uv run p033 demo --output artifacts/demo.json
data:
	uv run p033 fetch all --output artifacts/datasets.json
audit:
	uv run p033 audit $(DATASET) --output results/summaries/dataset_audits/$(DATASET).json
smoke:
	uv run p033 benchmark $(DATASET) --mode smoke --output results/raw_model_runs/$(DATASET).smoke.json
full:
	uv run p033 benchmark $(DATASET) --mode full --output results/raw_model_runs/$(DATASET).full.json
meta:
	uv run python scripts/build_meta_dataset.py
evaluate:
	uv run python scripts/evaluate_recommender.py --model ridge
