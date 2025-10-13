# 🎯 P1.5 Phase 4.2: Subscription Testing Suite

**Agent**: test-writer-agent
**Phase**: 4 (Parallel execution with Prompt 05)
**Time Estimate**: 2 hours
**Dependencies**: Phase 3 must be complete

**Why test-writer-agent?** Writing comprehensive tests with proper mocking and coverage.

**⚠️ CRITICAL**:

- DO NOT start until Phase 3 complete!
- ✅ CAN RUN IN PARALLEL with Prompt 05

---

## 📋 Mission

Create comprehensive test suite for subscription system.

---

## 📝 Implementation Tasks

### Task 1: Service Unit Tests (60 min)

**Create**: `/backend/tests/unit/test_subscription_service.py`

```python
"""Unit tests for subscription service."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from app.services.subscription_service import subscription_service
from app.models.subscription import SubscriptionCreate

@pytest.fixture
def mock_supabase():
    with patch('app.services.subscription_service.get_supabase_client') as mock:
        yield mock.return_value

@pytest.mark.asyncio
async def test_create_subscription_success(mock_supabase):
    """Test successful subscription creation."""
    mock_supabase.table().select().execute.return_value = Mock(data=[])
    mock_supabase.table().insert().execute.return_value = Mock(
        data=[{"id": "sub_123", "tier_id": "flow_pro"}]
    )

    with patch.object(subscription_service, 'get_subscription_details'):
        data = SubscriptionCreate(
            user_id="user_123",
            tier_id="flow_pro",
            stripe_subscription_id="sub_123",
            stripe_customer_id="cus_123",
            stripe_price_id="price_123"
        )
        result = await subscription_service.create_subscription(data)
        assert result is not None

@pytest.mark.asyncio
async def test_use_analysis_success(mock_supabase):
    """Test using an analysis."""
    mock_supabase.table().select().single().execute.return_value = Mock(
        data={
            "id": "sub_123",
            "analyses_used_this_period": 5,
            "analyses_rollover": 10,
            "current_period_start": datetime.utcnow().isoformat(),
            "current_period_end": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        }
    )
    mock_supabase.table().update().execute.return_value = Mock(
        data=[{"analyses_used_this_period": 6}]
    )

    with patch('app.config.pricing.pricing_config.get_tier') as mock_tier:
        mock_tier.return_value = Mock(analyses_per_month=60, rollover_limit=30)
        result = await subscription_service.use_analysis("user_123", "sub_123")
        assert result.analyses_used_this_period == 6

@pytest.mark.asyncio
async def test_use_analysis_limit_reached(mock_supabase):
    """Test limit reached."""
    mock_supabase.table().select().single().execute.return_value = Mock(
        data={
            "id": "sub_123",
            "analyses_used_this_period": 15,
            "analyses_rollover": 0,
            "current_period_start": datetime.utcnow().isoformat(),
            "current_period_end": datetime.utcnow().isoformat(),
        }
    )

    with patch('app.config.pricing.pricing_config.get_tier') as mock_tier:
        mock_tier.return_value = Mock(analyses_per_month=15, rollover_limit=5)
        with pytest.raises(ValueError, match="No analyses available"):
            await subscription_service.use_analysis("user_123", "sub_123")
```

---

### Task 2: API Integration Tests (40 min)

**Create**: `/backend/tests/integration/test_subscription_api.py`

```python
"""Integration tests for subscription API."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_auth():
    with patch('app.core.auth.get_current_user') as mock:
        mock.return_value = {"id": "user_123", "email": "test@example.com"}
        yield mock

def test_get_subscription_status(mock_auth):
    """Test GET /api/subscriptions/status."""
    with patch('app.services.subscription_service.subscription_service.get_subscription_status') as mock:
        mock.return_value = Mock(
            has_active_subscription=True,
            tier_id="flow_pro",
            analyses_remaining=45
        )

        response = client.get(
            "/api/subscriptions/status",
            headers={"Authorization": "Bearer test"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["has_active_subscription"] is True

def test_create_subscription(mock_auth):
    """Test POST /api/subscriptions."""
    with patch('app.services.subscription_service.subscription_service.create_subscription') as mock:
        mock.return_value = Mock(id="sub_123", tier_id="flow_pro")

        response = client.post(
            "/api/subscriptions/",
            headers={"Authorization": "Bearer test"},
            json={
                "user_id": "user_123",
                "tier_id": "flow_pro",
                "stripe_subscription_id": "sub_123",
                "stripe_customer_id": "cus_123",
                "stripe_price_id": "price_123"
            }
        )

        assert response.status_code == 201

def test_create_checkout_session(mock_auth):
    """Test POST /api/subscriptions/checkout."""
    with patch('app.config.pricing.pricing_config.get_tier') as mock_tier:
        with patch('stripe.checkout.Session.create') as mock_stripe:
            mock_tier.return_value = Mock(
                is_subscription=True,
                stripe_price_id="price_123"
            )
            mock_stripe.return_value = Mock(
                id="cs_123",
                url="https://checkout.stripe.com/123"
            )

            response = client.post(
                "/api/subscriptions/checkout",
                headers={"Authorization": "Bearer test"},
                json={"tier_id": "flow_pro"}
            )

            assert response.status_code == 200
            data = response.json()
            assert "checkout_url" in data
```

---

### Task 3: Webhook Tests (20 min)

**Create**: `/backend/tests/unit/test_webhook_service.py`

```python
"""Tests for webhook event handlers."""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.webhook_service import (
    handle_webhook_event,
    handle_subscription_event
)

@pytest.mark.asyncio
async def test_handle_subscription_created():
    """Test subscription.created event."""
    event = {
        "id": "evt_123",
        "type": "customer.subscription.created",
        "data": {
            "object": {
                "id": "sub_123",
                "customer": "cus_123",
                "status": "active"
            }
        }
    }

    with patch('app.core.database.get_supabase_client') as mock_db:
        mock_db.return_value.table().select().execute.return_value = Mock(data=[])
        mock_db.return_value.table().insert().execute.return_value = Mock(data=[])

        result = await handle_webhook_event(event)
        assert result["status"] == "success"

@pytest.mark.asyncio
async def test_handle_subscription_updated():
    """Test subscription.updated event."""
    event = {
        "id": "evt_124",
        "type": "customer.subscription.updated",
        "data": {
            "object": {
                "id": "sub_123",
                "items": {
                    "data": [{"price": {"id": "price_new"}}]
                }
            }
        }
    }

    with patch('app.core.database.get_supabase_client') as mock_db:
        mock_db.return_value.table().select().execute.return_value = Mock(data=[])
        mock_db.return_value.table().insert().execute.return_value = Mock(data=[])
        mock_db.return_value.table().select().eq().single().execute.return_value = Mock(
            data={"id": "sub_123", "stripe_price_id": "price_old"}
        )

        with patch('app.services.subscription_service.subscription_service.update_subscription'):
            result = await handle_webhook_event(event)
            assert result["status"] in ["success", "already_processed"]

@pytest.mark.asyncio
async def test_duplicate_event_handling():
    """Test idempotency - duplicate events ignored."""
    event = {"id": "evt_123", "type": "customer.subscription.created"}

    with patch('app.core.database.get_supabase_client') as mock_db:
        # Event already exists
        mock_db.return_value.table().select().execute.return_value = Mock(
            data=[{"id": "existing"}]
        )

        result = await handle_webhook_event(event)
        assert result["status"] == "already_processed"
```

---

## ✅ Verification Checklist

### 1. Run All Tests

```bash
cd /home/carlos/projects/cv-match/backend

# Run unit tests
docker compose exec backend pytest tests/unit/test_subscription_service.py -v

# Run integration tests
docker compose exec backend pytest tests/integration/test_subscription_api.py -v

# Run webhook tests
docker compose exec backend pytest tests/unit/test_webhook_service.py -v

# Run all subscription tests
docker compose exec backend pytest tests/ -k subscription -v
```

**Expected**: All tests pass ✅

### 2. Check Coverage

```bash
docker compose exec backend pytest --cov=app/services/subscription_service --cov=app/api/subscriptions tests/
```

**Expected**: Coverage > 80%

### 3. Test Specific Scenarios

```bash
# Test limit enforcement
docker compose exec backend pytest tests/unit/test_subscription_service.py::test_use_analysis_limit_reached -v

# Test rollover logic
docker compose exec backend pytest tests/unit/test_subscription_service.py::test_process_period_renewal_with_rollover -v
```

---

## 🚨 Common Issues

### Issue 1: Import Errors

**Error**: `ModuleNotFoundError`

**Solution**:

```bash
# Ensure backend container running
docker compose up backend

# Check Python path
docker compose exec backend python -c "import sys; print(sys.path)"
```

### Issue 2: Mock Not Working

**Error**: `AttributeError: Mock object has no attribute`

**Solution**:

```python
# Use return_value for methods
mock.method.return_value = Mock(data=[])

# Use side_effect for exceptions
mock.method.side_effect = ValueError("error")
```

### Issue 3: Async Tests Fail

**Error**: `RuntimeWarning: coroutine was never awaited`

**Solution**:

```python
# Always mark with @pytest.mark.asyncio
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
```

---

## 📊 Success Criteria

Phase 4.2 is complete when:

- ✅ All service methods tested
- ✅ All API endpoints tested
- ✅ Webhook handlers tested
- ✅ Edge cases covered
- ✅ >80% test coverage
- ✅ All tests passing
- ✅ Code committed

---

## 🎯 Final Step

**After BOTH Phase 4.1 AND 4.2 complete:**

### P1.5 Complete! 🎉

1. **Full Integration Test**:

```bash
# End-to-end test
./scripts/test-subscription-flow.sh
```

2. **Manual Testing**:

- Create subscription via UI
- Use analyses
- Check rollover
- Cancel subscription

3. **Deployment Checklist**:

- [ ] All tests pass
- [ ] Migrations applied
- [ ] Stripe webhooks configured
- [ ] Environment variables set
- [ ] Documentation updated

4. **Celebrate!** 🚀

---

**Time check**: ~2 hours. If longer, ask for help!

Good luck! 🚀
