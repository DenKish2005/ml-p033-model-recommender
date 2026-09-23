.PHONY: setup check test demo data
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
