set shell := ["bash", "-lc"]

test:
	.venv/bin/pytest -q

stubs:
	PYTHONPATH=src:. .venv/bin/python -c "from app.cli import main; main(['stubs', 'examples.demo_example.models'])"
	PYTHONPATH=src:. .venv/bin/python -c "from app.cli import main; main(['stubs', 'examples.fast_api_example.users.models'])"
	PYTHONPATH=src:. .venv/bin/python -c "from app.cli import main; main(['stubs', 'examples.fast_api_example.projects.models'])"
	PYTHONPATH=src:. .venv/bin/python -c "from app.cli import main; main(['module-stubs', 'examples.fast_api_example.http.users'])"
	PYTHONPATH=src:. .venv/bin/python -c "from app.cli import main; main(['module-stubs', 'examples.fast_api_example.http.projects'])"

demo-example:
	PYTHONPATH=src .venv/bin/python -m examples.demo_example.main

fast-api-example:
	PYTHONPATH=src .venv/bin/python -m examples.fast_api_example.http.main

check:
	ruff check .
	ty check .
	pyrefly check .
