.PHONY: help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	
setup: ## Setup of the project
	@poetry install

lint: ## Running the linting of the project
	@poetry run ruff check src --config ruff.toml
		
test-coverage: ## Running test coverage for the project
	@poetry run coverage run -m pytest tests/ -vv
	@poetry run coverage report -m
	@poetry run coverage html

update: ## Updating the project packages
	@poetry update

build: setup update lint ## Building the project
	@poetry build
	@poetry version patch