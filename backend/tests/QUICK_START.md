# Webhook Testing Quick Start Guide

This guide provides quick instructions for running the payment webhook tests for the CV-Match application.

## Prerequisites

- Python 3.11+
- pip or uv package manager
- Access to the CV-Match codebase

## Quick Setup (5 minutes)

### 1. Install Test Dependencies

```bash
# Navigate to backend directory
cd backend

# Install test dependencies
make install-test-deps
```

### 2. Run All Webhook Tests

```bash
# Run all webhook tests
make test-webhooks

# Or using the test runner script
python run_webhook_tests.py webhook
```

### 3. Check Results

If all tests pass, you'll see:
```
✅ All webhook tests passed!
```

## Test Categories

### Basic Test Commands

```bash
# Run only unit tests
make test-unit

# Run only integration tests
make test-integration

# Run Brazilian market specific tests
make test-brazilian

# Run security-focused tests
make test-webhook-security

# Run performance tests
make test-webhook-performance
```

### Advanced Testing

```bash
# Full webhook test suite with coverage
make test-webhook-all

# Run with coverage report
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/integration/test_payment_webhooks.py

# Run with verbose output
pytest tests/ -v -s
```

## Test Runner Script

Use the convenient test runner script:

```bash
# Run all webhook tests
python run_webhook_tests.py webhook

# Run integration tests only
python run_webhook_tests.py integration

# Run with coverage
python run_webhook_tests.py coverage

# Run Brazilian market tests
python run_webhook_tests.py brazilian

# Run with keyword filter
python run_webhook_tests.py --keyword checkout
```

## Environment Setup

The tests use mock environment variables, but you can override them:

```bash
# Create .env.test file
cat > .env.test << EOF
STRIPE_SECRET_KEY=sk_test_1234567890
STRIPE_WEBHOOK_SECRET=whsec_test_1234567890
SUPABASE_URL=http://localhost:54321
SUPABASE_SERVICE_KEY=test_service_key
ENVIRONMENT=test
EOF

# Load environment variables
export $(cat .env.test | xargs)
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install -r requirements-test.txt
   ```

2. **Module Not Found**
   ```bash
   # Ensure you're in the backend directory
   cd backend
   python -m pytest tests/
   ```

3. **Test Database Issues**
   ```bash
   # Tests use mocks by default, no database needed
   # For integration with real database, configure SUPABASE_URL
   ```

4. **Permission Issues**
   ```bash
   chmod +x run_webhook_tests.py
   ```

### Debug Mode

Run tests with debug output:

```bash
pytest tests/ -v -s --tb=long
```

### Run Specific Tests

```bash
# Run specific test class
pytest tests/integration/test_payment_webhooks.py::TestPaymentWebhooks

# Run specific test method
pytest tests/integration/test_payment_webhooks.py::TestPaymentWebhooks::test_checkout_session_completed_webhook_success

# Run tests matching pattern
pytest tests/ -k "checkout_session"
```

## What the Tests Cover

### Webhook Events Tested
- ✅ `checkout.session.completed`
- ✅ `invoice.payment_succeeded`
- ✅ `invoice.payment_failed`
- ✅ `customer.subscription.created`
- ✅ `customer.subscription.updated`
- ✅ `customer.subscription.deleted`

### Security Features Tested
- ✅ Webhook signature verification
- ✅ Idempotency protection
- ✅ Error handling and logging
- ✅ Invalid payload rejection

### Brazilian Market Features
- ✅ BRL currency handling
- ✅ Portuguese language support
- ✅ Brazilian customer data
- ✅ Localized metadata processing

## Next Steps

1. **Review Test Results**: Check coverage reports with `make test-cov`
2. **Add New Tests**: Follow existing patterns in `tests/fixtures/`
3. **Update Documentation**: Keep this guide current
4. **CI/CD Integration**: Add to your pipeline with `make test-webhook-ci`

## Support

For issues:

1. Check the test output for detailed error messages
2. Verify all dependencies are installed
3. Review the test files for proper mocking
4. Consult the full documentation: `tests/README.md`

## Performance Benchmarks

Expected performance:
- Webhook processing: < 500ms
- Test suite completion: < 30 seconds
- Coverage: > 80% of webhook code

Run performance tests:
```bash
make test-webhook-performance
```

---

*This guide covers the essentials. For comprehensive documentation, see `tests/README.md`.*