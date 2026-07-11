set shell := ["bash", "-lc"]
export UV_CACHE_DIR := env_var_or_default("UV_CACHE_DIR", ".uv-cache")

test:
	uv run --extra test pytest -q

check:
	uv run --extra dev ruff check .
	uv run --extra dev ty check .
	uv run --extra dev pyrefly check .

bump kind:
	case "{{kind}}" in major|minor|patch) ;; *) echo "usage: just bump [major|minor|patch]"; exit 2 ;; esac
	uv version --bump "{{kind}}"
	just test
	just check
	jj describe -m "release: $(uv version --short)"
	jj bookmark move main --to @
	jj git push --bookmark main
	git tag "v$(uv version --short)" main
	git push origin "v$(uv version --short)"

benchmark:
	PYTHONPATH=src uv run python benchmarks/benchmark_projector.py

stubs:
	PYTHONPATH=src:. uv run --extra examples projector type-stubs examples/demo_example/models.py examples/fast_api_example/projects/models.py examples/fast_api_example/users/models.py

demo-example:
	PYTHONPATH=src uv run python -m examples.demo_example.main

fast-api-example:
	PYTHONPATH=src uv run --extra examples python -m examples.fast_api_example.http.main
