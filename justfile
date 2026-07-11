set shell := ["bash", "-lc"]

test:
	.venv/bin/pytest -q

check:
	ruff check .
	ty check .
	pyrefly check .

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
	PYTHONPATH=src .venv/bin/python benchmarks/benchmark_projector.py

stubs:
	PYTHONPATH=src:. .venv/bin/projector type-stubs examples/demo_example/models.py examples/fast_api_example/projects/models.py examples/fast_api_example/users/models.py

demo-example:
	PYTHONPATH=src .venv/bin/python -m examples.demo_example.main

fast-api-example:
	PYTHONPATH=src .venv/bin/python -m examples.fast_api_example.http.main
