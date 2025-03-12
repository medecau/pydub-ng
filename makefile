.PHONY: all fmt test coverage

all: fmt test

fmt:
	ruff check --fix .
	ruff format .

test:
	tox -p
	
coverage:
	uv run pytest tests/ -v --cov=pydub --cov-report=term --cov-report=html
