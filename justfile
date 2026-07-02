set shell := ["bash", "-lc"]

example:
	PYTHONPATH=src .venv/bin/python -m examples.demo_example.main

stubs:
	PYTHONPATH=src:. .venv/bin/python -c "from app.cli import main; main(['stubs', 'examples.demo_example.models'])"
	PYTHONPATH=src:. .venv/bin/python -c "from app.cli import main; main(['stubs', 'examples.fast_api_example.domain_models'])"

fast-api-example:
	PYTHONPATH=src .venv/bin/python -m examples.fast_api_example.main

test:
	.venv/bin/pytest -q

check:
	ruff check .
	ty check .
	pyrefly check .
