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
	@poetry run ruff check src --config ruff.toml

test-in-parallel: lint ## Running tests for the project in parallel for the project
	@echo "Running tests in parallel for the project ..."
	@poetry run pytest -n auto tests -vv

test-coverage: lint ## Test-Coverage the project
	@echo "Running test-coverage for the project ..."
	@poetry run coverage run -m pytest tests -vv
	@poetry run coverage report -m
	@poetry run coverage html


all-commands-persisting-handler: ## Running the all-commands-persisting-handler
	@poetry run python src/external_systems/commands_handler/generic/all_commands_persisting_handler.py

download-youtube-video-for-url-command-handler: ## Running the download_youtube_video_for_url_command_handler
	@poetry run python src/external_systems/commands_handler/video/download/youtube/download_youtube_video_for_url_command_handler.py

download-youtube-video-from-txt-file-command-handler: ## Running the download_youtube_video_from_txt_file_command_handler
	@poetry run python src/external_systems/commands_handler/video/download/youtube/download_youtube_video_from_txt_file_command_handler.py

download-youtube-video-from-txt-file-to-channel-name-dir-command-handler: ## Running the download_youtube_video_from_txt_file_to_channel_name_dir_command_handler
	@poetry run python src/external_systems/commands_handler/video/download/youtube/download_youtube_video_from_txt_file_to_channel_name_dir_command_handler.py

download-youtube-video-from-url-to-channel-name-command-handler-dir: ## Running the download_youtube_video_from_url_to_channel_name_command_handler_dir
	@poetry run python src/external_systems/commands_handler/video/download/youtube/download_youtube_video_from_url_to_channel_name_command_handler_dir.py

downloaded-youtube-video-event-handler: ## Running the downloaded_youtube_video_event_handler
	@poetry run python src/external_systems/events_handler/video/persist/youtube/downloaded_youtube_video_event_handler.py

all-events-persisting-handler: ## Running the all-events-persisting-handler
	@poetry run python src/external_systems/events_handler/generic/all_events_persisting_handler.py

run-gateway-server: ## Running the run_gateway_server
	@sh src/external_systems/scripts/run_gateway_server.sh