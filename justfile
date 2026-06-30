set shell := ["bash", "-lc"]

example:
	PYTHONPATH=src .venv/bin/python -m examples.example

stubs:
	PYTHONPATH=src .venv/bin/python -m examples.example --generate-stub

test:
	.venv/bin/pytest -q

check:
	ty check .
	pyrefly check .
