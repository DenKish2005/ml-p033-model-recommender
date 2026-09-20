.PHONY: setup check test demo
setup:
	uv sync --locked
check:
	uv run ruff check .
	uv run ruff format --check .
test:
	uv run pytest
demo:
	uv run p033 demo --output artifacts/demo.json
