install:
	uv pip install -e .

install-dev:
	uv pip install -e ".[dev]"

test:
	pytest -v
