.PHONY: test coverage_report build clean lint format typecheck


test:
	# Run unit tests and gather coverage info
	poetry run coverage  run --source dict2sql -m unittest discover -t dict2sql -s dict2sql -p "*_test.py"

coverage_report:
	# Show coverage and fail when it's <90%
	poetry run coverage report --fail-under 90

build:
	poetry build

clean:
	rm -rf dist

lint:
	poetry run black --check dict2sql
	poetry run isort --check dict2sql


format:
	poetry run isort dict2sql
	poetry run black dict2sql

typecheck:
	poetry run pyright typecheck dict2sql
