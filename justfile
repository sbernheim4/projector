set shell := ["bash", "-lc"]

example:
	.venv/bin/python -m examples.example

stubs:
	.venv/bin/python -m examples.example --generate-stub

test:
	.venv/bin/pytest -q

check:
	ty check .
	pyrefly check .
