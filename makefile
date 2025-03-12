.PHONY: all fmt test

all: fmt test

fmt:
	ruff check --fix .
	ruff format .

test:
	tox -p
