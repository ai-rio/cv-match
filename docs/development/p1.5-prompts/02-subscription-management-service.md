# 🎯 P1.5 Phase 1.2: Subscription Management Service

**Agent**: backend-specialist
**Phase**: 1 (Parallel execution with Prompt 01)
**Time Estimate**: 2 hours
**Dependencies**: None - can start immediately in parallel

**Why backend-specialist?** This task involves building backend service layer with business logic, FastAPI dependency injection, and repository patterns - core backend development.

---

## 📋 Mission

Create the subscription management service that handles subscription lifecycle operations. This is the core business logic layer that will be used by API endpoints (Phase 3) and integrates with Stripe subscriptions.

**What You're Building:**

- Subscription CRUD service
- Usage tracking and limit enforcement
- Rollover logic for unused analyses
- Subscription status management
- Integration with existing credit system

---

## 🔍 Context

### Current State

- ✅ Credit usage service exists in `/backend/app/services/usage_limit_service.py`
- ✅ Stripe service exists in `/backend/app/services/stripe_service.py`
- ❌ No subscription management service
- ❌ No usage tracking for subscriptions
- ❌ No rollover implementation

### Target State

- ✅ Complete subscription lifecycle management
- ✅ Usage limits enforced per subscription tier
- ✅ Unused analyses rollover monthly
- ✅ Integration with Stripe subscription webhooks
- ✅ Unified credit + subscription usage tracking

### Reference Architecture

You're adapting **QuoteKit's subscription management** to CV-Match:

- QuoteKit: `/home/carlos/projects/QuoteKit/src/features/account/controllers/subscription-helpers.ts`
- QuoteKit: `/home/carlos/projects/QuoteKit/src/features/account/controllers/upsert-user-subscription.ts`

---

## 🛠️ CRITICAL: Tools You MUST Use

### 1. Context7 - Library Documentation

**ALWAYS check documentation before implementing!**

```bash
# Get FastAPI dependency injection patterns
context7:resolve-library-id --library-name="fastapi"
context7:get-library-docs --library-id="/tiangolo/fastapi" --topic="dependency injection"

# Get Pydantic model patterns
context7:get-library-docs --library-id="/pydantic/pydantic" --topic="dataclass validation"

# Get async patterns
context7:get-library-docs --library-id="/tiangolo/fastapi" --topic="async dependencies"
```

### 2. Python REPL Testing

Test your service as you build:

```bash
docker compose exec backend python -c "
from app.services.subscription_service import subscription_service
import asyncio

async def test():
    result = await subscription_service.get_subscription_by_user('test-user-id')
    print(result)

asyncio.run(test())
"
```

---

## 📝 Implementation Tasks

### Task 1: Create Subscription Models (20 min)

**File**: `/backend/app/models/subscription.py`

```python
"""
Subscription models for CV-Match.
Represents user subscriptions and their usage.
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class SubscriptionBase(BaseModel):
    """Base subscription model."""
    user_id: str
    tier_id: str  # e.g., "flow_pro"
    status: Literal["active", "canceled", "past_due", "paused"] = "active"


class SubscriptionCreate(SubscriptionBase):
    """Model for creating a new subscription."""
    stripe_subscription_id: str
    stripe_customer_id: str
    stripe_price_id: str


class SubscriptionUpdate(BaseModel):
    """Model for updating a subscription."""
    tier_id: Optional[str] = None
    status: Optional[Literal["active", "canceled", "past_due", "paused"]] = None
    cancel_at_period_end: Optional[bool] = None


class SubscriptionUsage(BaseModel):
    """Model for subscription usage tracking."""
    subscription_id: str
    user_id: str
    analyses_used_this_period: int = 0
    analyses_rollover: int = 0
    period_start: datetime
    period_end: datetime


class SubscriptionDetails(SubscriptionBase):
    """Complete subscription details with usage."""
    id: str
    stripe_subscription_id: str
    stripe_customer_id: str
    stripe_price_id: str

    # Period info
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool = False
    canceled_at: Optional[datetime] = None

    # Usage tracking
    analyses_used_this_period: int = 0
    analyses_rollover: int = 0
    analyses_available: int  # Computed: tier limit + rollover - used

    # Tier info (from pricing config)
    tier_name: str
    analyses_per_month: int
    rollover_limit: int

    # Timestamps
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubscriptionStatus(BaseModel):
    """Quick subscription status check."""
    has_active_subscription: bool
    tier_id: Optional[str] = None
    analyses_remaining: int = 0
    can_use_service: bool  # True if has subscription OR has credits
```

---

### Task 2: Create Subscription Service (60 min)

**File**: `/backend/app/services/subscription_service.py`

```python
"""
Subscription management service for CV-Match.
Handles subscription lifecycle, usage tracking, and rollover.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

from app.core.database import get_supabase_client
from app.config.pricing import pricing_config
from app.models.subscription import (
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionDetails,
    SubscriptionUsage,
    SubscriptionStatus,
)

logger = logging.getLogger(__name__)


class SubscriptionService:
    """Service for managing user subscriptions."""

    def __init__(self):
        self.supabase = get_supabase_client()

    async def create_subscription(
        self,
        subscription_data: SubscriptionCreate
    ) -> SubscriptionDetails:
        """
        Create a new subscription for a user.

        Args:
            subscription_data: Subscription creation data

        Returns:
            Created subscription details

        Raises:
            ValueError: If user already has active subscription
            ValueError: If tier_id is invalid
        """
        # Validate tier
        tier = pricing_config.get_tier(subscription_data.tier_id)
        if not tier or not tier.is_subscription:
            raise ValueError(f"Invalid subscription tier: {subscription_data.tier_id}")

        # Check for existing active subscription
        existing = await self.get_active_subscription(subscription_data.user_id)
        if existing:
            raise ValueError(
                f"User already has active subscription: {existing['tier_id']}"
            )

        # Calculate period (current month)
        now = datetime.utcnow()
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Next month, same day
        if now.month == 12:
            period_end = period_start.replace(year=now.year + 1, month=1)
        else:
            period_end = period_start.replace(month=now.month + 1)

        # Create subscription record
        subscription_record = {
            "user_id": subscription_data.user_id,
            "tier_id": subscription_data.tier_id,
            "status": subscription_data.status,
            "stripe_subscription_id": subscription_data.stripe_subscription_id,
            "stripe_customer_id": subscription_data.stripe_customer_id,
            "stripe_price_id": subscription_data.stripe_price_id,
            "current_period_start": period_start.isoformat(),
            "current_period_end": period_end.isoformat(),
            "cancel_at_period_end": False,
            "analyses_used_this_period": 0,
            "analyses_rollover": 0,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        result = self.supabase.table("subscriptions").insert(subscription_record).execute()

        if not result.data:
            raise ValueError("Failed to create subscription")

        logger.info(
            f"Created subscription for user {subscription_data.user_id}: "
            f"{subscription_data.tier_id}"
        )

        return await self.get_subscription_details(result.data[0]["id"])

    async def get_subscription_details(
        self,
        subscription_id: str
    ) -> SubscriptionDetails:
        """
        Get complete subscription details with usage.

        Args:
            subscription_id: Subscription ID

        Returns:
            Subscription details
        """
        result = self.supabase.table("subscriptions").select("*").eq(
            "id", subscription_id
        ).single().execute()

        if not result.data:
            raise ValueError(f"Subscription not found: {subscription_id}")

        subscription = result.data

        # Get tier info
        tier = pricing_config.get_tier(subscription["tier_id"])
        if not tier:
            raise ValueError(f"Invalid tier: {subscription['tier_id']}")

        # Calculate available analyses
        analyses_available = (
            tier.analyses_per_month
            + subscription["analyses_rollover"]
            - subscription["analyses_used_this_period"]
        )

        return SubscriptionDetails(
            id=subscription["id"],
            user_id=subscription["user_id"],
            tier_id=subscription["tier_id"],
            status=subscription["status"],
            stripe_subscription_id=subscription["stripe_subscription_id"],
            stripe_customer_id=subscription["stripe_customer_id"],
            stripe_price_id=subscription["stripe_price_id"],
            current_period_start=subscription["current_period_start"],
            current_period_end=subscription["current_period_end"],
            cancel_at_period_end=subscription["cancel_at_period_end"],
            canceled_at=subscription.get("canceled_at"),
            analyses_used_this_period=subscription["analyses_used_this_period"],
            analyses_rollover=subscription["analyses_rollover"],
            analyses_available=max(0, analyses_available),
            tier_name=tier.name,
            analyses_per_month=tier.analyses_per_month,
            rollover_limit=tier.rollover_limit,
            created_at=subscription["created_at"],
            updated_at=subscription["updated_at"],
        )

    async def get_active_subscription(
        self,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get user's active subscription if exists.

        Args:
            user_id: User ID

        Returns:
            Subscription data or None
        """
        result = self.supabase.table("subscriptions").select("*").eq(
            "user_id", user_id
        ).eq("status", "active").order("created_at", desc=True).limit(1).execute()

        if result.data and len(result.data) > 0:
            return result.data[0]
        return None

    async def update_subscription(
        self,
        subscription_id: str,
        update_data: SubscriptionUpdate
    ) -> SubscriptionDetails:
        """
        Update subscription details.

        Args:
            subscription_id: Subscription ID
            update_data: Update data

        Returns:
            Updated subscription details
        """
        update_dict = update_data.model_dump(exclude_none=True)
        update_dict["updated_at"] = datetime.utcnow().isoformat()

        result = self.supabase.table("subscriptions").update(update_dict).eq(
            "id", subscription_id
        ).execute()

        if not result.data:
            raise ValueError(f"Failed to update subscription: {subscription_id}")

        logger.info(f"Updated subscription {subscription_id}: {update_dict}")

        return await self.get_subscription_details(subscription_id)

    async def cancel_subscription(
        self,
        subscription_id: str,
        immediate: bool = False
    ) -> SubscriptionDetails:
        """
        Cancel a subscription.

        Args:
            subscription_id: Subscription ID
            immediate: If True, cancel immediately. If False, at period end.

        Returns:
            Updated subscription details
        """
        update_data = {
            "cancel_at_period_end": not immediate,
            "canceled_at": datetime.utcnow().isoformat() if immediate else None,
            "status": "canceled" if immediate else "active",
            "updated_at": datetime.utcnow().isoformat(),
        }

        result = self.supabase.table("subscriptions").update(update_data).eq(
            "id", subscription_id
        ).execute()

        if not result.data:
            raise ValueError(f"Failed to cancel subscription: {subscription_id}")

        logger.info(
            f"Canceled subscription {subscription_id} "
            f"(immediate: {immediate})"
        )

        return await self.get_subscription_details(subscription_id)

    async def use_analysis(
        self,
        user_id: str,
        subscription_id: str
    ) -> SubscriptionUsage:
        """
        Record usage of one analysis from subscription.

        Args:
            user_id: User ID
            subscription_id: Subscription ID

        Returns:
            Updated usage data

        Raises:
            ValueError: If no analyses available
        """
        subscription = await self.get_subscription_details(subscription_id)

        if subscription.analyses_available <= 0:
            raise ValueError(
                "No analyses available. Limit reached for this period."
            )

        # Increment usage
        new_usage = subscription.analyses_used_this_period + 1

        result = self.supabase.table("subscriptions").update({
            "analyses_used_this_period": new_usage,
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("id", subscription_id).execute()

        if not result.data:
            raise ValueError("Failed to update usage")

        logger.info(
            f"User {user_id} used analysis. "
            f"Remaining: {subscription.analyses_available - 1}"
        )

        return SubscriptionUsage(
            subscription_id=subscription_id,
            user_id=user_id,
            analyses_used_this_period=new_usage,
            analyses_rollover=subscription.analyses_rollover,
            period_start=subscription.current_period_start,
            period_end=subscription.current_period_end,
        )

    async def process_period_renewal(
        self,
        subscription_id: str
    ) -> SubscriptionDetails:
        """
        Process monthly subscription renewal.
        Called by Stripe webhook on period renewal.

        Args:
            subscription_id: Subscription ID

        Returns:
            Updated subscription details
        """
        subscription = await self.get_subscription_details(subscription_id)
        tier = pricing_config.get_tier(subscription.tier_id)

        if not tier:
            raise ValueError(f"Invalid tier: {subscription.tier_id}")

        # Calculate rollover
        unused = (
            tier.analyses_per_month
            + subscription.analyses_rollover
            - subscription.analyses_used_this_period
        )

        # Cap rollover at tier limit
        new_rollover = min(unused, tier.rollover_limit)

        # Calculate new period
        period_start = subscription.current_period_end
        if period_start.month == 12:
            period_end = period_start.replace(year=period_start.year + 1, month=1)
        else:
            period_end = period_start.replace(month=period_start.month + 1)

        # Update subscription
        update_data = {
            "current_period_start": period_start.isoformat(),
            "current_period_end": period_end.isoformat(),
            "analyses_used_this_period": 0,
            "analyses_rollover": new_rollover,
            "updated_at": datetime.utcnow().isoformat(),
        }

        result = self.supabase.table("subscriptions").update(update_data).eq(
            "id", subscription_id
        ).execute()

        if not result.data:
            raise ValueError("Failed to renew subscription period")

        logger.info(
            f"Renewed subscription {subscription_id}. "
            f"Rollover: {new_rollover} analyses"
        )

        return await self.get_subscription_details(subscription_id)

    async def get_subscription_status(
        self,
        user_id: str
    ) -> SubscriptionStatus:
        """
        Get quick status check for user subscription + credits.

        Args:
            user_id: User ID

        Returns:
            Combined subscription and credit status
        """
        # Check for active subscription
        subscription = await self.get_active_subscription(user_id)

        if subscription:
            details = await self.get_subscription_details(subscription["id"])
            return SubscriptionStatus(
                has_active_subscription=True,
                tier_id=details.tier_id,
                analyses_remaining=details.analyses_available,
                can_use_service=details.analyses_available > 0,
            )

        # Check for credits (existing credit system)
        from app.services.usage_limit_service import usage_limit_service

        credit_balance = await usage_limit_service.get_user_balance(user_id)

        return SubscriptionStatus(
            has_active_subscription=False,
            tier_id=None,
            analyses_remaining=credit_balance,
            can_use_service=credit_balance > 0,
        )


# Global service instance
subscription_service = SubscriptionService()
```

---

### Task 3: Integration with Usage Middleware (30 min)

**Update File**: `/backend/app/middleware/credit_middleware.py`

Add subscription support to the existing credit middleware:

```python
"""
Enhanced usage middleware for credits AND subscriptions.
"""

from fastapi import Request, HTTPException
from app.services.subscription_service import subscription_service
from app.services.usage_limit_service import usage_limit_service


async def check_usage_limit(request: Request, user_id: str):
    """
    Check if user can use service (subscription OR credits).

    Priority:
    1. Check active subscription first
    2. Fall back to credit balance

    Raises:
        HTTPException: If no access available
    """
    # Check subscription status
    status = await subscription_service.get_subscription_status(user_id)

    if status.can_use_service:
        # User has access (subscription or credits)
        return

    # No access
    if status.has_active_subscription:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "subscription_limit_reached",
                "message": "Limite de análises atingido para este mês.",
                "tier": status.tier_id,
                "can_upgrade": True,
            }
        )
    else:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "no_credits",
                "message": "Sem créditos ou assinatura ativa. Compre créditos ou assine.",
                "can_purchase_credits": True,
                "can_subscribe": True,
            }
        )


async def consume_usage(user_id: str):
    """
    Consume one analysis (from subscription OR credits).

    Priority:
    1. Use subscription analysis if active
    2. Fall back to credit consumption
    """
    # Check for active subscription
    subscription = await subscription_service.get_active_subscription(user_id)

    if subscription:
        # Use subscription
        await subscription_service.use_analysis(user_id, subscription["id"])
        return {"source": "subscription", "type": "analysis"}
    else:
        # Use credit
        await usage_limit_service.consume_credit(user_id)
        return {"source": "credits", "type": "credit"}
```

---

### Task 4: Add Service Tests (10 min)

**Create**: `/backend/tests/unit/test_subscription_service.py`

```python
"""
Unit tests for subscription service.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from app.services.subscription_service import subscription_service
from app.models.subscription import SubscriptionCreate


@pytest.fixture
def mock_supabase():
    """Mock Supabase client."""
    with patch('app.services.subscription_service.get_supabase_client') as mock:
        client = Mock()
        mock.return_value = client
        yield client


@pytest.mark.asyncio
async def test_create_subscription_success(mock_supabase):
    """Test successful subscription creation."""
    # Arrange
    mock_supabase.table().insert().execute.return_value = Mock(
        data=[{
            "id": "sub_123",
            "user_id": "user_123",
            "tier_id": "flow_pro",
            "status": "active",
        }]
    )

    subscription_data = SubscriptionCreate(
        user_id="user_123",
        tier_id="flow_pro",
        stripe_subscription_id="sub_stripe_123",
        stripe_customer_id="cus_123",
        stripe_price_id="price_123",
    )

    # Act
    result = await subscription_service.create_subscription(subscription_data)

    # Assert
    assert result is not None
    assert result.tier_id == "flow_pro"
    mock_supabase.table().insert.assert_called_once()


@pytest.mark.asyncio
async def test_create_subscription_duplicate_fails(mock_supabase):
    """Test that creating duplicate subscription fails."""
    # Arrange - user already has subscription
    mock_supabase.table().select().eq().eq().order().limit().execute.return_value = Mock(
        data=[{"id": "existing_sub", "tier_id": "flow_starter"}]
    )

    subscription_data = SubscriptionCreate(
        user_id="user_123",
        tier_id="flow_pro",
        stripe_subscription_id="sub_stripe_123",
        stripe_customer_id="cus_123",
        stripe_price_id="price_123",
    )

    # Act & Assert
    with pytest.raises(ValueError, match="already has active subscription"):
        await subscription_service.create_subscription(subscription_data)


@pytest.mark.asyncio
async def test_use_analysis_success(mock_supabase):
    """Test using an analysis from subscription."""
    # Arrange
    mock_supabase.table().select().eq().single().execute.return_value = Mock(
        data={
            "id": "sub_123",
            "user_id": "user_123",
            "tier_id": "flow_pro",
            "analyses_used_this_period": 5,
            "analyses_rollover": 10,
            "current_period_start": datetime.utcnow().isoformat(),
            "current_period_end": datetime.utcnow().isoformat(),
        }
    )

    mock_supabase.table().update().eq().execute.return_value = Mock(
        data=[{"analyses_used_this_period": 6}]
    )

    # Act
    result = await subscription_service.use_analysis("user_123", "sub_123")

    # Assert
    assert result.analyses_used_this_period == 6
    mock_supabase.table().update.assert_called_once()


@pytest.mark.asyncio
async def test_use_analysis_limit_reached(mock_supabase):
    """Test that usage fails when limit reached."""
    # Arrange - all analyses used
    mock_supabase.table().select().eq().single().execute.return_value = Mock(
        data={
            "id": "sub_123",
            "user_id": "user_123",
            "tier_id": "flow_starter",
            "analyses_used_this_period": 15,  # Limit is 15
            "analyses_rollover": 0,
            "current_period_start": datetime.utcnow().isoformat(),
            "current_period_end": datetime.utcnow().isoformat(),
        }
    )

    # Act & Assert
    with pytest.raises(ValueError, match="No analyses available"):
        await subscription_service.use_analysis("user_123", "sub_123")
```

---

## ✅ Verification Checklist

After completing all tasks:

### 1. Service Loads Correctly

```bash
cd /home/carlos/projects/cv-match/backend

# Test service import
docker compose exec backend python -c "
from app.services.subscription_service import subscription_service
print('✅ Subscription service loaded')
print('Methods:', dir(subscription_service))
"
```

### 2. Models Validate

```bash
docker compose exec backend python -c "
from app.models.subscription import SubscriptionCreate
from pydantic import ValidationError

# Test valid subscription
sub = SubscriptionCreate(
    user_id='test',
    tier_id='flow_pro',
    stripe_subscription_id='sub_123',
    stripe_customer_id='cus_123',
    stripe_price_id='price_123'
)
print('✅ Valid subscription:', sub.tier_id)

# Test invalid status
try:
    sub = SubscriptionCreate(
        user_id='test',
        tier_id='flow_pro',
        status='invalid_status',
        stripe_subscription_id='sub_123',
        stripe_customer_id='cus_123',
        stripe_price_id='price_123'
    )
except ValidationError as e:
    print('✅ Validation working:', e.errors()[0]['msg'])
"
```

### 3. Integration with Middleware

```bash
docker compose exec backend python -c "
from app.middleware.credit_middleware import check_usage_limit, consume_usage
print('✅ Middleware functions available')
"
```

### 4. Tests Pass

```bash
docker compose exec backend pytest tests/unit/test_subscription_service.py -v
```

Expected: All tests pass.

### 5. Type Checking

```bash
docker compose exec backend mypy app/services/subscription_service.py
docker compose exec backend mypy app/models/subscription.py
```

No errors should appear.

---

## 🚨 Common Issues & Solutions

### Issue 1: Circular Import

**Error**: `ImportError: cannot import name 'subscription_service'`

**Solution**:

```python
# Don't import at module level
# Import inside function when needed:
from app.services.subscription_service import subscription_service
```

### Issue 2: Supabase Client Not Found

**Error**: `NameError: name 'get_supabase_client' is not defined`

**Solution**:

```python
# Add to top of subscription_service.py:
from app.core.database import get_supabase_client
```

### Issue 3: Pydantic Validation Errors

**Error**: `ValidationError: 1 validation error for SubscriptionCreate`

**Solution**:

```bash
# Check field types match model
# Use .model_dump() instead of .dict() in Pydantic v2
```

---

## 📊 Success Criteria

Phase 1.2 is complete when:

- ✅ All models created and validate correctly
- ✅ Subscription service implements all CRUD operations
- ✅ Usage tracking works with rollover logic
- ✅ Middleware integrates both credits + subscriptions
- ✅ All tests pass
- ✅ Type checking passes
- ✅ Code committed to git

---

## 🎯 Next Step

After completing Phase 1.2:
→ **WAIT for Phase 1.1 to complete** (if running in parallel)
→ **Once both Phase 1.1 AND 1.2 complete**:
→ **Proceed to Phase 2**: Database Subscription Updates
→ **Prompt**: `03-database-subscription-updates.md`

---

## 💡 Tips

1. **Follow Repository Pattern** - Keep business logic in service, not routes
2. **Use async/await properly** - All database calls should be async
3. **Test edge cases** - What happens when limit reached? Period ends?
4. **Log important events** - Subscription created, renewed, canceled
5. **Handle errors gracefully** - Provide clear error messages in Portuguese

---

**Time check**: This should take ~2 hours. If taking longer, ask for help!

**Parallel Execution**: This can run at the same time as Prompt 01 (Subscription Pricing Config). Both are independent!

Good luck! 🚀
