# Payment Webhook Testing Guide

This directory contains comprehensive integration tests for payment webhooks in the CV-Match application, specifically designed for the Brazilian market SaaS implementation.

## Overview

The test suite covers all critical Stripe webhook events required for a robust payment system:

- `checkout.session.completed` - One-time payments and subscription activation
- `invoice.payment_succeeded` - Successful recurring payments
- `invoice.payment_failed` - Failed recurring payments
- `customer.subscription.created` - New subscription creation
- `customer.subscription.updated` - Subscription changes
- `customer.subscription.deleted` - Subscription cancellation

## Test Structure

```
tests/
├── conftest.py                    # Global test configuration and fixtures
├── fixtures/
│   └── webhook_fixtures.py       # Webhook-specific fixtures and utilities
├── unit/
│   └── test_webhook_service.py   # Unit tests for webhook service
├── integration/
│   └── test_payment_webhooks.py  # Integration tests for webhook endpoints
└── README.md                     # This file
```

## Setup and Installation

### 1. Install Test Dependencies

```bash
# Navigate to backend directory
cd backend

# Install test dependencies
pip install -r requirements-test.txt
```

### 2. Environment Configuration

The tests use environment variables configured in `conftest.py`. Key variables:

- `STRIPE_SECRET_KEY` - Stripe secret key (test)
- `STRIPE_WEBHOOK_SECRET` - Webhook secret for signature verification
- `SUPABASE_URL` - Supabase instance URL
- `SUPABASE_SERVICE_KEY` - Supabase service key
- `ENVIRONMENT` - Set to "test"

### 3. Test Database Setup

For integration tests, ensure you have a test Supabase instance or mock the database responses:

```bash
# Using test Supabase instance
supabase db reset --db-url postgresql://postgres:postgres@localhost:54322/postgres
```

## Running Tests

### Run All Tests

```bash
# Run all tests with coverage
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=html
```

### Run Specific Test Categories

```bash
# Run only webhook tests
pytest -m webhook

# Run only integration tests
pytest -m integration

# Run only unit tests
pytest -m unit

# Run only Stripe-specific tests
pytest -m stripe
```

### Run Specific Test Files

```bash
# Run webhook integration tests
pytest tests/integration/test_payment_webhooks.py

# Run webhook service unit tests
pytest tests/unit/test_webhook_service.py
```

### Run Individual Tests

```bash
# Run specific test method
pytest tests/integration/test_payment_webhooks.py::TestPaymentWebhooks::test_checkout_session_completed_webhook_success

# Run with keyword filter
pytest -k "checkout_session_completed"
```

## Test Categories

### 1. Integration Tests (`tests/integration/`)

These tests verify the complete webhook processing flow, including:

- HTTP request handling
- Signature verification
- Database operations
- Error handling
- Idempotency protection

**Key test scenarios:**
- Successful webhook processing for all event types
- Brazilian market-specific webhook handling
- Signature verification failures
- Idempotency protection (duplicate events)
- Error handling for missing users/data
- Invalid payload handling

### 2. Unit Tests (`tests/unit/`)

These tests focus on individual service methods:

- Webhook signature verification
- Event processing logic
- Database service interactions
- Brazilian metadata processing
- Performance tracking

## Key Features Tested

### 1. Brazilian Market Integration

- BRL currency handling
- Portuguese language support
- Brazilian customer details
- Localized product metadata

### 2. Security and Reliability

- Webhook signature verification
- Idempotency protection
- Error handling and logging
- Processing time tracking

### 3. Payment Workflow

- One-time payment processing
- Subscription lifecycle management
- Failed payment handling
- User account updates

## Test Fixtures

### WebhookFixtureGenerator

Creates webhook event payloads for testing:

```python
fixture_generator = WebhookFixtureGenerator()
webhook_event = fixture_generator.create_checkout_session_completed_event(
    session_data=sample_session
)
```

### WebhookSignatureGenerator

Generates valid webhook signatures:

```python
signature_gen = WebhookSignatureGenerator()
headers = signature_gen.generate_headers(payload)
```

### BrazilianWebhookFixtures

Creates Brazilian-specific test data:

```python
brazilian_fixtures = BrazilianWebhookFixtures()
session = brazilian_fixtures.create_brazilian_checkout_session(
    user_id="user_123",
    plan_type="pro"
)
```

## Mocking Strategy

The tests use comprehensive mocking to isolate the webhook processing logic:

- **Stripe API**: Mocked to avoid external dependencies
- **Supabase Database**: Mocked for consistent test environments
- **HTTP Requests**: Using FastAPI test client

## Continuous Integration

### GitHub Actions Configuration

Add to your `.github/workflows/test.yml`:

```yaml
name: Payment Webhook Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test-webhooks:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install -r requirements-test.txt

    - name: Run webhook tests
      run: |
        cd backend
        pytest tests/ -m webhook --cov=app --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: backend/coverage.xml
```

## Test Data Examples

### Brazilian Checkout Session

```json
{
  "id": "cs_test_brazilian_123",
  "currency": "brl",
  "amount_total": 2990,
  "customer": "cus_brazilian_123",
  "payment_status": "paid",
  "status": "complete",
  "metadata": {
    "user_id": "user_123",
    "product": "cv_optimization",
    "plan": "pro",
    "market": "brazil",
    "language": "pt-br"
  },
  "customer_details": {
    "email": "usuario@exemplo.com.br",
    "name": "João Silva",
    "address": {
      "country": "BR",
      "state": "SP",
      "city": "São Paulo"
    }
  }
}
```

### Brazilian Subscription

```json
{
  "id": "sub_brazilian_123",
  "status": "active",
  "customer": "cus_brazilian_123",
  "items": {
    "data": [
      {
        "price": {
          "currency": "brl",
          "unit_amount": 2990,
          "recurring": {"interval": "month"},
          "nickname": "CV-Match Pro (BRL)"
        }
      }
    ]
  },
  "metadata": {
    "user_id": "user_123",
    "plan": "pro",
    "market": "brazil",
    "language": "pt-br"
  }
}
```

## Performance Testing

The test suite includes performance tracking for webhook processing:

```python
# Processing time is automatically tracked in webhook events
assert "processing_time_ms" in response_data
assert response_data["processing_time_ms"] < 1000  # Should be under 1 second
```

## Error Handling Tests

Comprehensive error scenarios are tested:

1. **Invalid Signatures**: Rejected with 400 status
2. **Missing Users**: Graceful handling with error logging
3. **Database Failures**: Proper error handling and retry logic
4. **Malformed Payloads**: Validation and rejection
5. **Unsupported Events**: Logged and acknowledged

## Best Practices

### 1. Test Isolation

Each test is isolated with proper setup/teardown:
- Unique event IDs
- Mocked database responses
- Fresh fixtures for each test

### 2. Brazilian Market Focus

Tests specifically validate:
- BRL currency processing
- Portuguese language support
- Brazilian customer data handling
- Local tax compliance (metadata)

### 3. Security Validation

Security features are thoroughly tested:
- Signature verification with tolerance
- Idempotency protection
- Request validation
- Error information leakage prevention

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
   ```bash
   pip install -r requirements-test.txt
   ```

2. **Database Connection**: Check Supabase configuration
   ```bash
   # Verify test database is running
   supabase status
   ```

3. **Mock Configuration**: Ensure proper mocking in conftest.py

4. **Signature Verification**: Check webhook secret configuration

### Debug Mode

Run tests with debug output:

```bash
pytest -v -s --tb=short tests/integration/test_payment_webhooks.py
```

### Coverage Analysis

Generate detailed coverage reports:

```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## Contributing

When adding new webhook tests:

1. Follow the existing naming conventions
2. Add appropriate test markers (`@pytest.mark.webhook`, `@pytest.mark.integration`)
3. Include Brazilian market scenarios
4. Add comprehensive error handling tests
5. Update this documentation

## Security Notes

- Never commit real Stripe keys or webhook secrets
- Use test mode for all webhook testing
- Rotate test secrets regularly
- Validate all test data for PII

## Support

For test-related issues:

1. Check the test logs for detailed error messages
2. Verify environment configuration
3. Ensure proper database setup
4. Review Stripe webhook documentation for format changes

## References

- [Stripe Webhooks Documentation](https://stripe.com/docs/webhooks)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [Pytest Documentation](https://docs.pytest.org/)
- [CV-Match Project Documentation](../../../docs/development/)