POETRY_VERSION=2.0.0

.PHONY: all
.DEFAULT_GOAL=help

.PHONY: install
install: ## Install project dependencies
	poetry install

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
build: ## Build python package artifacts
	poetry build

.PHONY: update
update:
	poetry update

.PHONY: precommit
precommit:
	pre-commit install
	pre-commit run --all-files


.PHONY: test
test:
	@poetry run pytest; \
	EXIT_CODE=$$?; \
	if [ $$EXIT_CODE -ne 0 ] && [ $$EXIT_CODE -ne 5 ]; then \
		exit $$EXIT_CODE; \
	fi

.PHONY: cover
cover:
	@poetry run pytest --cov src/ --junitxml reports/xunit.xml \
	--cov-report xml:reports/coverage.xml --cov-report term-missing; \
	EXIT_CODE=$$?; \
	if [ $$EXIT_CODE -ne 0 ] && [ $$EXIT_CODE -ne 5 ]; then \
		exit $$EXIT_CODE; \
	fi

.PHONY: package
package: ## Create deployable whl package for python3 project
	@if rg -q "package-mode = false" pyproject.toml; then \
		echo "Skipping package build (package-mode=false)."; \
	else \
		poetry build --format=wheel; \
	fi

.PHONY: ci
ci: clean install test cover package ## Runs clean, install, test, cover and package

.PHONY: format
format: ## Formats the python3 files
	ruff format

.PHONY: lint
lint: ## Lints the python3 files
	ruff check .

.PHONY: run
run: ## Run the frontend Flask app locally
	poetry run python src/frontend_app.py

.PHONY: help
help: ## Show this help
	@awk -F ':|##' '/^[^\t].+?:.*?##/ {\
	printf "\033[36m%-30s\033[0m %s\n", $$1, $$NF\
	}' $(MAKEFILE_LIST)
