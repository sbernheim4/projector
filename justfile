set shell := ["bash", "-lc"]

test:
	.venv/bin/pytest -q

stubs:
	PYTHONPATH=src:. .venv/bin/python -c "from app.cli import main; main(['stubs', 'examples.demo_example.models'])"
	PYTHONPATH=src:. .venv/bin/python -c "from app.cli import main; main(['stubs', 'examples.fast_api_example.domain_models'])"
	PYTHONPATH=src:. .venv/bin/python -c "from app.cli import main; main(['stubs', 'examples.fast_api_example.projects_models'])"

demo-example:
	PYTHONPATH=src .venv/bin/python -m examples.demo_example.main

fast-api-example:
	PYTHONPATH=src .venv/bin/python -m examples.fast_api_example.main

check:
	ruff check .
	ty check .
	pyrefly check .
