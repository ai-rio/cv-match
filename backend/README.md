# CV-Match Backend

FastAPI backend for CV-Match - AI-powered resume optimization for the Brazilian market.

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (fast Python package manager)
- Supabase account (for database and auth)

### Installation

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
make venv
# or: uv venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
make install-dev
# or: uv pip install -e ".[dev]"
```

### Running the Server

```bash
# With virtual environment activated
make dev
# or: uvicorn app.main:app --reload

# Without activation (using uv run)
make dev-uv
# or: uv run uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📦 Package Management with UV

This project uses [uv](https://github.com/astral-sh/uv) for Python package management, which is 10-100x faster than pip.

### Why UV?

- ⚡ **Blazing fast**: 10-100x faster than pip
- 🔒 **Deterministic**: Consistent installs across environments
- 🎯 **Better resolution**: Smarter dependency resolution
- 📦 **Modern**: Built in Rust, works with pyproject.toml

### Common Commands

```bash
# Create virtual environment
uv venv

# Install from pyproject.toml
uv pip install -e .

# Install with dev dependencies
uv pip install -e ".[dev]"

# Add a new dependency
# 1. Add to pyproject.toml [project.dependencies]
# 2. Run: uv pip install -e .

# Run without activation
uv run uvicorn app.main:app --reload
uv run pytest
uv run black app
```

## 🛠️ Development

### Available Make Commands

```bash
make help           # Show all available commands
make venv           # Create virtual environment
make install        # Install production dependencies
make install-dev    # Install with dev dependencies
make sync           # Sync dependencies from pyproject.toml
make dev            # Start development server
make dev-uv         # Start dev server with uv run
make format         # Format code with black
make lint           # Lint code with ruff
make lint-fix       # Lint and auto-fix issues
make type-check     # Type check with mypy
make test           # Run tests
make test-cov       # Run tests with coverage
make clean          # Clean cache files and .venv
```

### Code Quality

```bash
# Format code
make format
# or: black app

# Lint code
make lint
# or: ruff check app

# Type check
make type-check
# or: mypy app

# Run all quality checks
make format && make lint && make type-check
```

### Testing

```bash
# Run tests
make test
# or: pytest

# Run with coverage
make test-cov
# or: pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── core/
│   │   └── config.py        # Configuration and settings
│   ├── models/              # Pydantic models
│   │   ├── auth.py
│   │   ├── llm.py
│   │   └── vectordb.py
│   ├── services/            # Business logic services
│   │   ├── supabase/        # Supabase integration
│   │   ├── llm/             # LLM services
│   │   └── vectordb/        # Vector database
│   └── api/
│       ├── router.py        # API router registration
│       └── endpoints/       # API endpoints
├── tests/                   # Test files
├── pyproject.toml          # Project dependencies and config
├── Dockerfile              # Production Docker image
├── Dockerfile.dev          # Development Docker image
├── Makefile                # Development commands
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_key
SUPABASE_ANON_KEY=your_anon_key

# OpenRouter (for Claude)
OPENROUTER_API_KEY=sk-or-xxx

# OpenAI (optional)
OPENAI_API_KEY=sk-xxx

# Anthropic (optional)
ANTHROPIC_API_KEY=sk-ant-xxx

# Qdrant Vector Database
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_key

# Application
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000
```

### Settings

All configuration is managed through `app/core/config.py` using Pydantic settings:

```python
from app.core.config import settings

# Access configuration
supabase_url = settings.SUPABASE_URL
openai_key = settings.OPENAI_API_KEY
```

## 🐳 Docker

### Development

```bash
# Build development image
docker build -f Dockerfile.dev -t cv-match-backend:dev .

# Run container
docker run -p 8000:8000 --env-file .env cv-match-backend:dev
```

### Production

```bash
# Build production image
docker build -f Dockerfile -t cv-match-backend:prod .

# Run container
docker run -p 8000:8000 --env-file .env cv-match-backend:prod
```

## 🧪 Testing

Tests are written using pytest with async support:

```python
import pytest
from fastapi.testclient import TestClient

@pytest.mark.asyncio
async def test_example():
    # Your async test here
    pass
```

Run tests:
```bash
pytest                    # Run all tests
pytest tests/api/        # Run specific directory
pytest -v                # Verbose output
pytest --cov=app         # With coverage
```

## 📝 API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🔐 Authentication

The API uses Supabase Auth with JWT tokens:

```bash
# Example authenticated request
curl -H "Authorization: Bearer <your-jwt-token>" \
     http://localhost:8000/api/protected-endpoint
```

All protected endpoints require the `Authorization` header with a valid Supabase JWT token.

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [UV Documentation](https://github.com/astral-sh/uv)
- [Supabase Documentation](https://supabase.com/docs)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Run quality checks: `make format && make lint && make test`
4. Submit a pull request

## 📄 License

MIT
