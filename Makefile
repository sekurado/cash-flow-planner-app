.PHONY: lint format check

lint: format check mypy

format:
	ruff format --check src/ tests/

check:
	ruff check src/ tests/

mypy:
	mypy --strict src/
