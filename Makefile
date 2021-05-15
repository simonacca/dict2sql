.PHONY: unit_test clean


test:
	poetry run python3 -m unittest discover -t dict2sql -s dict2sql -p "*_test.py"

build:
	poetry build

clean:
	rm -rf dist

lint:
	black --check dict2sql

format:
	black dict2sql

typecheck:
	mypy dict2sql
