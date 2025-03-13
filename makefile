.PHONY: all fmt lint test coverage

all: lint test

fmt:
	ruff format .
	ruff check --fix .

lint:
	ruff check .
	ruff format --check .

test:
	tox -p

coverage:
	pytest tests/ -v --cov=pydub --cov-report=term --cov-report=html
