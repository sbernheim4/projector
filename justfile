set shell := ["bash", "-lc"]

example:
	PYTHONPATH=src uv run python -m examples.example

stubs:
	PYTHONPATH=src uv run python -m examples.example --generate-stub

test:
	UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest -q
