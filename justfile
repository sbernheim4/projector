set shell := ["bash", "-lc"]

test:
	.venv/bin/pytest -q

stubs:
	PYTHONPATH=src:. .venv/bin/projector stubs examples/demo_example/models.py examples/fast_api_example/projects/models.py examples/fast_api_example/users/models.py

demo-example:
	PYTHONPATH=src .venv/bin/python -m examples.demo_example.main

fast-api-example:
	PYTHONPATH=src .venv/bin/python -m examples.fast_api_example.http.main

check:
	ruff check .
	ty check .
	pyrefly check .
