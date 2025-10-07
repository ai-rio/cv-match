.PHONY: dev dev-frontend dev-backend prod prod-frontend prod-backend clean help
.PHONY: db-migration-new db-apply db-list db-push db-status

# Default target
.DEFAULT_GOAL := help

# Colors for terminal output
GREEN=\033[0;32m
YELLOW=\033[0;33m
RED=\033[0;31m
NC=\033[0m # No Color

# Development environment
dev: ## Start the full development environment
	@echo "${GREEN}Starting full development environment...${NC}"
	docker-compose up

dev-frontend: ## Start only the frontend development server
	@echo "${GREEN}Starting frontend development server...${NC}"
	docker-compose up frontend

dev-backend: ## Start only the backend development server
	@echo "${GREEN}Starting backend development server...${NC}"
	docker-compose up backend

# Production environment
prod: ## Start the full production environment
	@echo "${GREEN}Starting full production environment...${NC}"
	docker-compose -f docker-compose.prod.yml up -d

prod-frontend: ## Start only the frontend production server
	@echo "${GREEN}Starting frontend production server...${NC}"
	docker-compose -f docker-compose.prod.yml up -d frontend

prod-backend: ## Start only the backend production server
	@echo "${GREEN}Starting backend production server...${NC}"
	docker-compose -f docker-compose.prod.yml up -d backend

# Clean up
clean: ## Remove containers and volumes
	@echo "${YELLOW}Cleaning up containers and volumes...${NC}"
	docker-compose down -v
	docker-compose -f docker-compose.prod.yml down -v

# Frontend helpers
install-frontend: ## Install frontend dependencies locally
	@echo "${GREEN}Installing frontend dependencies...${NC}"
	cd frontend && bun install

build-frontend: ## Build frontend for production
	@echo "${GREEN}Building frontend for production...${NC}"
	cd frontend && bunx build

# Backend helpers
install-backend: ## Install backend dependencies locally
	@echo "${GREEN}Installing backend dependencies...${NC}"
	cd backend && pip install -r requirements.txt

install-backend-dev: ## Install backend dev dependencies locally
	@echo "${GREEN}Installing backend dev dependencies...${NC}"
	cd backend && pip install -e ".[dev]"

# Frontend helpers
install-frontend: ## Install frontend dependencies locally
	@echo "${GREEN}Installing frontend dependencies...${NC}"
	cd frontend && bun install

install-frontend-dev: ## Install frontend dev dependencies locally
	@echo "${GREEN}Installing frontend dev dependencies...${NC}"
	cd frontend && bun install

# Code quality
lint-frontend: ## Lint frontend code
	@echo "${GREEN}Linting frontend code...${NC}"
	cd frontend && bunx lint

lint-frontend-fix: ## Lint and fix frontend code
	@echo "${GREEN}Linting and fixing frontend code...${NC}"
	cd frontend && bunx lint:fix

lint-backend: ## Lint backend code
	@echo "${GREEN}Linting backend code...${NC}"
	cd backend && uv run --no-project ruff check .

lint-backend-fix: ## Lint and fix backend code
	@echo "${GREEN}Linting and fixing backend code...${NC}"
	cd backend && uv run --no-project ruff check --fix .

format-frontend: ## Format frontend code
	@echo "${GREEN}Formatting frontend code...${NC}"
	cd frontend && bunx format

format-backend: ## Format backend code
	@echo "${GREEN}Formatting backend code...${NC}"
	cd backend && uv run --no-project ruff format .

type-check-frontend: ## Type check frontend code
	@echo "${GREEN}Type checking frontend code...${NC}"
	cd frontend && bunx type-check

type-check-backend: ## Type check backend code
	@echo "${GREEN}Type checking backend code...${NC}"
	cd backend && uv run --no-project pyright

test-frontend: ## Run frontend tests
	@echo "${GREEN}Running frontend tests...${NC}"
	cd frontend && bunx test:coverage

test-backend: ## Run backend tests
	@echo "${GREEN}Running backend tests...${NC}"
	cd backend && python -m pytest tests/ -v --cov=app --cov-report=term-missing

test-backend-watch: ## Run backend tests in watch mode
	@echo "${GREEN}Running backend tests in watch mode...${NC}"
	cd backend && python -m pytest tests/ -v --cov=app --cov-report=term-missing -f

# Pre-commit setup
setup-precommit: ## Set up pre-commit hooks
	@echo "${GREEN}Setting up pre-commit hooks...${NC}"
	pip install pre-commit
	pre-commit install

run-precommit: ## Run pre-commit hooks on all files
	@echo "${GREEN}Running pre-commit hooks...${NC}"
	pre-commit run --all-files

# Supabase database migrations (all for remote database)
db-migration-new: ## Create a new migration file (Usage: make db-migration-new name=create_users_table)
	@echo "${GREEN}Creating new migration file: $(name)${NC}"
	supabase migration new $(name)

db-apply: ## Apply pending migrations to the remote database
	@echo "${GREEN}Applying pending migrations to remote database...${NC}"
	supabase db push

db-list: ## List all applied migrations on the remote database
	@echo "${GREEN}Listing applied migrations on remote database...${NC}"
	supabase migration list

db-push: ## Push migrations to remote Supabase project (same as db-apply)
	@echo "${GREEN}Pushing migrations to remote project...${NC}"
	supabase db push

db-status: ## Show pending migrations status
	@echo "${GREEN}Checking migration status...${NC}"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "${YELLOW}Migration status (via supabase migration list):${NC}"
	@supabase migration list || echo "  Failed to get migration status"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "${YELLOW}Migration files in project:${NC}"
	@ls -1 supabase/migrations/*.sql 2>/dev/null | sed 's/.*\//  /' || echo "  None"

# Help command
help: ## Show this help
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
