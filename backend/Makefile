.PHONY: install dev test lint format clean venv sync test-webhooks test-unit test-integration test-brazilian install-test-deps

# Default target
.DEFAULT_GOAL := help

# Colors for terminal output
GREEN=\033[0;32m
YELLOW=\033[0;33m
BLUE=\033[0;34m
NC=\033[0m # No Color

venv: ## Create virtual environment with uv
	@echo "${GREEN}Creating virtual environment with uv...${NC}"
	uv venv

install: ## Install dependencies with uv
	@echo "${GREEN}Installing dependencies with uv...${NC}"
	uv pip install -e .

install-dev: ## Install dependencies with dev tools
	@echo "${GREEN}Installing dependencies with dev tools...${NC}"
	uv pip install -e ".[dev]"

install-test-deps: ## Install test dependencies for webhook testing
	@echo "${GREEN}Installing test dependencies...${NC}"
	pip install -r requirements-test.txt

sync: ## Sync dependencies (install/update from pyproject.toml)
	@echo "${BLUE}Syncing dependencies...${NC}"
	uv pip install -e ".[dev]"

dev: ## Run development server
	@echo "${GREEN}Starting development server...${NC}"
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-uv: ## Run development server with uv run (no activation needed)
	@echo "${GREEN}Starting development server with uv run...${NC}"
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

format: ## Format code with black
	@echo "${GREEN}Formatting code...${NC}"
	black app

lint: ## Run linting with ruff
	@echo "${GREEN}Running linters...${NC}"
	ruff check app

lint-fix: ## Run linting with automatic fixes
	@echo "${GREEN}Running linters with fixes...${NC}"
	ruff check --fix app

type-check: ## Run type checking with mypy
	@echo "${GREEN}Running type checking...${NC}"
	mypy app

test: ## Run tests
	@echo "${GREEN}Running tests...${NC}"
	pytest

test-cov: ## Run tests with coverage
	@echo "${GREEN}Running tests with coverage...${NC}"
	pytest --cov=app --cov-report=html --cov-report=term

# Payment Webhook Testing Targets
test-webhooks: ## Run only webhook tests
	@echo "${GREEN}Running webhook tests...${NC}"
	python -m pytest tests/ -m webhook -v

test-unit: ## Run only unit tests
	@echo "${GREEN}Running unit tests...${NC}"
	python -m pytest tests/unit/ -v

test-integration: ## Run only integration tests
	@echo "${GREEN}Running integration tests...${NC}"
	python -m pytest tests/integration/ -v

test-brazilian: ## Run Brazilian market specific tests
	@echo "${GREEN}Running Brazilian market tests...${NC}"
	python -m pytest tests/ -k "brazilian" -v

test-webhook-all: clean-coverage install-test-deps test-webhooks ## Full webhook test suite with setup and cleanup

# Combined webhook test commands
test-webhook-security: ## Run security-focused webhook tests
	@echo "${GREEN}Running webhook security tests...${NC}"
	python -m pytest tests/ -k "security or signature" -v

test-webhook-performance: ## Run performance-focused webhook tests
	@echo "${GREEN}Running webhook performance tests...${NC}"
	python -m pytest tests/ -k "performance or timing" -v --durations=10

test-webhook-integration: test-integration ## Alias for integration tests
test-webhook-unit: test-unit ## Alias for unit tests

# CI/CD webhook testing
test-webhook-ci: ## Run webhook tests in CI mode
	@echo "${GREEN}Running webhook tests for CI...${NC}"
	python -m pytest tests/ -m webhook --cov=app --cov-report=xml --junitxml=pytest-webhook.xml -v

clean: ## Clean up cache files and virtual environment
	@echo "${YELLOW}Cleaning up cache files...${NC}"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	rm -rf .venv 2>/dev/null || true

clean-coverage: ## Clean only coverage files
	@echo "${YELLOW}Cleaning coverage files...${NC}"
	rm -rf .coverage htmlcov/ pytest.xml pytest-webhook.xml

help: ## Show this help
	@echo "${BLUE}CV-Match Backend - UV Package Manager${NC}"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "${YELLOW}Quick Start:${NC}"
	@echo "  1. make venv         # Create virtual environment"
	@echo "  2. source .venv/bin/activate"
	@echo "  3. make install-dev  # Install with dev tools"
	@echo "  4. make dev          # Start development server"
	@echo ""
	@echo "${YELLOW}Webhook Testing:${NC}"
	@echo "  1. make install-test-deps  # Install test dependencies"
	@echo "  2. make test-webhooks     # Run webhook tests"
	@echo "  3. make test-webhook-all  # Full webhook test suite"