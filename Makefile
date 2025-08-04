.PHONY: help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

setup: ## Setup the project with dependencies
	@echo "Doing project setup ..."
	@poetry install

update: ## Update the project dependencies
	@echo "Updating project dependencies ..."
	@poetry update

lint: ## Lint the project
	@echo "Linting the project"
	@poetry run ruff check domain ports adapters services external_systems --config ruff.toml

test-coverage: ## Test-Coverage the project
	@echo "Running test-coverage for the project ..."
	@poetry run coverage run -m pytest domain/tests ports/tests adapters/tests services/tests external_systems/tests -vv
	@poetry run coverage report -m
	@poetry run coverage html