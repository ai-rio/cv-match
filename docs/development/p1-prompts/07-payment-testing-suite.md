# Agent Prompt: Payment Testing Suite

**Agent**: test-writer-agent
**Phase**: 4 - Testing (Parallel with frontend)
**Priority**: P0
**Time**: 1.5 hours

## Mission

Write comprehensive tests for payment flow, webhooks, and credit management.

## Tasks

### Task 1: Webhook Tests (45min)

```python
# tests/integration/test_payment_webhooks.py

def test_webhook_signature_verification():
    """Test webhook rejects invalid signatures"""
    response = client.post(
        "/api/webhooks/stripe",
        json={"test": "data"},
        headers={"stripe-signature": "invalid"}
    )
    assert response.status_code == 401

def test_webhook_idempotency():
    """Test same event only processed once"""
    # Send same event twice
    # Verify credits only added once

def test_checkout_completed():
    """Test credits added on successful payment"""
    # Mock webhook event
    # Verify credits increased
```

### Task 2: Credit Management Tests (45min)

```python
# tests/unit/test_usage_limit_service.py

async def test_deduct_credits_atomic():
    """Test atomic credit deduction"""
    # Test with sufficient credits
    # Test with insufficient credits
    # Test idempotency

async def test_concurrent_deduction():
    """Test no race conditions"""
    # Run multiple deductions concurrently
    # Verify final balance is correct
```

### Task 3: E2E Payment Flow (30min)

```python
# tests/e2e/test_payment_flow.py

async def test_complete_payment_flow():
    """Test full payment journey"""
    # 1. Check credits (0 or low)
    # 2. Create checkout session
    # 3. Simulate successful payment webhook
    # 4. Verify credits increased
    # 5. Use optimization
    # 6. Verify credit deducted
```

## Coverage Requirements

- Webhook handling: 90%+
- Credit management: 95%+
- Payment endpoints: 85%+
- Overall P1 code: 80%+

## Success Criteria

- All payment tests pass
- Webhook idempotency verified
- Atomic operations tested
- Race conditions prevented
- 80%+ coverage achieved

Total: 1.5 hours
