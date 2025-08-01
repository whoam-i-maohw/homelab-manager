.PHONY: help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

setup-external_systems: ## Setup the external_systems layer (component) of the project
	@cd external_systems && poetry install

setup-services: ## Setup the services layer (component) of the project
	@cd services && poetry install

setup-adapters: ## Setup the adapters layer (component) of the project
	@cd adapters && poetry install

setup-ports: ## Setup the ports layer (component) of the project
	@cd ports && poetry install

setup-domain: ## Setup the domain layer (component) of the project
	@cd domain && poetry install

setup-all: setup-domain setup-ports setup-adapters setup-services setup-external_systems ## Setup all project components
	@echo "Setup the project components ..."

update-external_systems: ## Update the external_systems layer (component) of the project
	@cd external_systems && poetry update

update-services: ## Update the services layer (component) of the project
	@cd services && poetry update

update-adapters: ## Update the adapters layer (component) of the project
	@cd adapters && poetry update

update-ports: ## Update the ports layer (component) of the project
	@cd ports && poetry update

update-domain: ## Update the domain layer (component) of the project
	@cd domain && poetry update

update-all: update-domain update-ports update-adapters update-services update-external_systems ## Updating all project components
	@echo "Update the project components ..."

lint-external_systems: ## Lint the external_systems layer (component) of the project
	@cd external_systems && poetry run ruff check src --config ruff.toml

lint-services: ## Lint the services layer (component) of the project
	@cd services && poetry run ruff check src --config ruff.toml

lint-adapters: ## Lint the adapters layer (component) of the project
	@cd adapters && poetry run ruff check src --config ruff.toml

lint-ports: ## Lint the ports layer (component) of the project
	@cd ports && poetry run ruff check src --config ruff.toml

lint-domain: ## Lint the domain layer (component) of the project
	@cd domain && poetry run ruff check src --config ruff.toml

lint-all: lint-domain lint-ports lint-adapters lint-services lint-external_systems ## Linting all project components
	@echo "Linting the project components ..."

test-coverage-external_systems: ## Test-Coverage the external_systems layer (component) of the project
	@cd external_systems && poetry run coverage run -m pytest tests/ -vv && poetry run coverage report -m && poetry run coverage html

test-coverage-services: ## Test-Coverage the services layer (component) of the project
	@cd services && poetry run coverage run -m pytest tests/ -vv && poetry run coverage report -m && poetry run coverage html

test-coverage-adapters: ## Test-Coverage the adapters layer (component) of the project
	@cd adapters && poetry run coverage run -m pytest tests/ -vv && poetry run coverage report -m && poetry run coverage html

test-coverage-ports: ## Test-Coverage the ports layer (component) of the project
	@cd ports && poetry run coverage run -m pytest tests/ -vv && poetry run coverage report -m && poetry run coverage html

test-coverage-domain: ## Test-Coverage the domain layer (component) of the project
	@cd domain && poetry run coverage run -m pytest tests/ -vv && poetry run coverage report -m && poetry run coverage html

test-coverage-all: test-coverage-domain test-coverage-ports test-coverage-adapters test-coverage-services test-coverage-external_systems ## Test-Coverage all project components
	@echo "Testing-Coverage the project components ..."

health-check: setup-all update-all lint-all test-coverage-all ## Building the project
	@echo "HealthCheck for all components ..."