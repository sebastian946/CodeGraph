.DEFAULT_GOAL := help

.PHONY: dev index test lint help

dev: ## Start the development environment via Docker Compose
	cd LLM && docker compose up --build

index: ## Run the document indexer
	cd LLM && uv run python -m indexer

test: ## Run the test suite
	cd LLM && uv run pytest tests/ -v

lint: ## Lint and check code formatting with ruff
	cd LLM && uv run ruff check . && uv run ruff format --check .

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
