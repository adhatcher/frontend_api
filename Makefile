POETRY_VERSION=2.0.0

.PHONY: all
.DEFAULT_GOAL=help

.PHONY: clean
clean:
	rm -rf __pycache__ 
	rm -rf .pytest_cache 
	rm -rf .coverage 
	rm -rf dist 
	rm -rf requirements.txt
	rm -rf build 

.PHONY: distclean
distclean: clean
	- rm -rf .venv

.PHONY: build
build: build
	python3 -m poetry install
	python3 -m poetry build

.PHONY: update
update:
	python3 -m poetry update

.PHONY: precommit
precommit:
	pre-commit install
	pre-commit run --all-files


.PHONY: test
test:
	python3 -m poetry run pytest

.PHONY: cover
cover:
	poetry run pytest --cov src/ --junitxml reports/xunit.xml \
	--cov-report xml:reports/coverage.xml --cov-report term-missing

.PHONY: package
package: ## Create deployable whl package for python3 project
	python3 -m poetry build --format=wheel

.PHONY: ci
ci: clean build test cover package ## Runs clan, build and package

.PHONY: format
format: ## Formats the python3 files
	ruff format

.PHONY: lint
lint: ## Lints the python3 files
	ruff check .

.PHONY: help
help: ## Show this help
	@awk -F ':|##' '/^[^\t].+?:.*?##/ {\
	printf "\033[36m%-30s\033[0m %s\n", $$1, $$NF\
	}' $(MAKEFILE_LIST)
