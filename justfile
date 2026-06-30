set shell := ["bash", "-lc"]

example:
	UV_CACHE_DIR=/private/tmp/uv-cache uv run python -m examples.example

stubs:
	UV_CACHE_DIR=/private/tmp/uv-cache uv run python -m examples.example --generate-stub

test:
	UV_CACHE_DIR=/private/tmp/uv-cache uv run pytest -q

check:
	ty check .
	pyrefly check .
