.PHONY: install test lint format clean

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest -v

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf build/ dist/ *.egg-info/
