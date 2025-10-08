# CV-Match Test Suite Commands Guide

## Running Tests in Docker Container (Recommended)

### Start Development Environment
```bash
make dev
```

### Run Specific Test Files
```bash
# Input sanitizer tests
docker exec cv-match_backend_1 python -m pytest tests/unit/test_input_sanitizer.py -v

# Security middleware tests
docker exec cv-match_backend_1 python -m pytest tests/unit/test_security_middleware.py -v

# Webhook service tests
docker exec cv-match_backend_1 python -m pytest tests/unit/test_webhook_service.py -v

# Payment webhook integration tests
docker exec cv-match_backend_1 python -m pytest tests/integration/test_payment_webhooks.py -v
```

### Run All Tests
```bash
# Run complete test suite
docker exec cv-match_backend_1 python -m pytest tests/ -v

# Run with coverage report
docker exec cv-match_backend_1 python -m pytest tests/ --cov=app --cov-report=html --cov-report=term
```

## Test File Locations
- **Unit Tests**: `backend/tests/unit/`
  - `test_input_sanitizer.py`
  - `test_security_middleware.py`
  - `test_webhook_service.py`
- **Integration Tests**: `backend/tests/integration/`
  - `test_payment_webhooks.py`

## Test Categories
```bash
# Unit tests only
docker exec cv-match_backend_1 python -m pytest tests/unit/ -v

# Integration tests only
docker exec cv-match_backend_1 python -m pytest tests/integration/ -v

# Tests matching specific patterns
docker exec cv-match_backend_1 python -m pytest tests/ -k "sanitize" -v
docker exec cv-match_backend_1 python -m pytest tests/ -k "webhook" -v
docker exec cv-match_backend_1 python -m pytest tests/ -k "security" -v
```

## Configuration Files
- **pytest.ini**: Test configuration located at `backend/pytest.ini`
- **conftest.py**: Test fixtures at `backend/tests/conftest.py`
- **requirements-test.txt**: Test dependencies at `backend/requirements-test.txt`

## Environment Requirements
- Docker and Docker Compose installed
- `make dev` to start development services
- Tests run inside `cv-match_backend_1` container
- Python 3.12 with pytest pre-installed in container

## Alternative: Using Backend Make Commands
```bash
# From backend directory
make test              # Run all tests
make test-unit         # Run unit tests only
make test-integration  # Run integration tests only
make test-webhooks     # Run webhook tests only
make test-cov          # Run with coverage
```

## Troubleshooting

### Permission Issues with Local .venv
If you encounter permission errors with the virtual environment:
```bash
# Use Docker approach instead
make dev
docker exec cv-match_backend_1 python -m pytest tests/ -v
```

### Missing Dependencies in Container
```bash
docker exec cv-match_backend_1 pip install pytest pytest-asyncio pytest-cov
```

### Async Test Issues
```bash
# Run with asyncio auto mode
docker exec cv-match_backend_1 python -m pytest tests/ --asyncio-mode=auto -v
```

### Test Configuration Check
```bash
# Check pytest configuration
docker exec cv-match_backend_1 cat pytest.ini

# List available test markers
docker exec cv-match_backend_1 python -m pytest --markers
```