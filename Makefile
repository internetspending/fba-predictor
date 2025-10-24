.PHONY: fmt lint type test cov hooks

fmt:	## Format with ruff
	ruff format apps/api

lint:	## Lint with ruff
	ruff check apps/api

type:	## Type-check with mypy
	mypy apps/api/app

test:	## Run tests
	pytest -q

cov:	## Coverage report
	pytest --cov=apps/api/app --cov-report=term-missing

hooks:	## Install and run pre-commit
	pre-commit install
	pre-commit run --all-files
