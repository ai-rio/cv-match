# 🎯 P1.5 Phase 3: Subscription API Endpoints

**Agent**: backend-specialist
**Phase**: 3 (Sequential - MUST wait for Phase 2 to complete)
**Time Estimate**: 4 hours
**Dependencies**: Phase 2 must be complete

**Why backend-specialist?** This task involves FastAPI route handlers, request/response models, dependency injection, and API design - core backend development.

**⚠️ CRITICAL**: DO NOT start this phase until Phase 2 (Database Updates) is complete!

---

## 📋 Mission

Create the FastAPI API endpoints for subscription management. These endpoints will be used by the frontend (Phase 4) and handle all subscription operations through the subscription service (Phase 1.2).

**What You're Building:**

- Subscription CRUD endpoints (create, read, update, cancel)
- Subscription status check endpoint
- Usage tracking endpoints
- Stripe webhook handler for subscriptions
- Integration with existing authentication

---

## 🔍 Context

### Current State

- ✅ Subscription service exists (`subscription_service.py`)
- ✅ Database tables exist (`subscriptions`, `subscription_usage_history`)
- ✅ Auth middleware exists
- ❌ No subscription API endpoints
- ❌ No webhook handler for subscriptions

### Target State

- ✅ Complete REST API for subscriptions
- ✅ Stripe webhook handler processes subscription events
- ✅ Endpoints documented in Swagger
- ✅ Proper error handling and validation
- ✅ Integration with existing credit system

---

## 🛠️ CRITICAL: Tools You MUST Use

### 1. Context7 - Library Documentation

```bash
# FastAPI router patterns
context7:get-library-docs --library-id="/tiangolo/fastapi" --topic="APIRouter dependencies"

# Stripe webhook handling
context7:get-library-docs --library-id="/stripe/stripe-python" --topic="webhooks subscription events"
```

---

## 📝 Implementation Tasks

### Task 1: Create Subscription API Router (60 min)

**Create**: `/backend/app/api/subscriptions.py`

```python
"""
Subscription API endpoints for CV-Match.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from typing import Dict, Any, Optional
import logging

from app.models.subscription import (
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionDetails,
    SubscriptionStatus,
)
from app.services.subscription_service import subscription_service
from app.services.stripe_service import stripe_service
from app.core.auth import get_current_user

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])
logger = logging.getLogger(__name__)


@router.get("/status", response_model=SubscriptionStatus)
async def get_subscription_status(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> SubscriptionStatus:
    """Get user's subscription + credit status."""
    try:
        return await subscription_service.get_subscription_status(current_user["id"])
    except Exception as e:
        logger.error(f"Failed to get status for user {current_user['id']}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/current")
async def get_current_subscription(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Optional[SubscriptionDetails]:
    """Get user's current active subscription."""
    try:
        subscription = await subscription_service.get_active_subscription(
            current_user["id"]
        )
        if not subscription:
            return None
        return await subscription_service.get_subscription_details(subscription["id"])
    except Exception as e:
        logger.error(f"Failed to get subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=SubscriptionDetails, status_code=201)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> SubscriptionDetails:
    """Create new subscription after Stripe checkout."""
    if subscription_data.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Cannot create for another user")

    try:
        return await subscription_service.create_subscription(subscription_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{subscription_id}", response_model=SubscriptionDetails)
async def update_subscription(
    subscription_id: str,
    update_data: SubscriptionUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> SubscriptionDetails:
    """Update subscription (tier, status)."""
    try:
        # Verify ownership
        subscription = await subscription_service.get_subscription_details(subscription_id)
        if subscription.user_id != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not your subscription")

        return await subscription_service.update_subscription(
            subscription_id, update_data
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{subscription_id}/cancel", response_model=SubscriptionDetails)
async def cancel_subscription(
    subscription_id: str,
    immediate: bool = False,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> SubscriptionDetails:
    """Cancel subscription (immediate or at period end)."""
    try:
        # Verify ownership
        subscription = await subscription_service.get_subscription_details(subscription_id)
        if subscription.user_id != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not your subscription")

        # Cancel in Stripe first
        if subscription.stripe_subscription_id:
            # TODO: Call Stripe API to cancel
            pass

        # Update local record
        return await subscription_service.cancel_subscription(
            subscription_id, immediate
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to cancel subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_usage_history(
    current_user: Dict[str, Any] = Depends(get_current_user),
    limit: int = 50
):
    """Get subscription usage history."""
    try:
        from app.core.database import get_supabase_client
        supabase = get_supabase_client()

        result = supabase.table("subscription_usage_history").select("*").eq(
            "user_id", current_user["id"]
        ).order("created_at", desc=True).limit(limit).execute()

        return {"success": True, "data": result.data}
    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

### Task 2: Update Webhook Handler (90 min)

**Update**: `/backend/app/services/webhook_service.py`

Add subscription event handlers:

```python
"""
Enhanced webhook service with subscription support.
"""

import logging
from typing import Dict, Any

from app.services.subscription_service import subscription_service
from app.core.database import get_supabase_client

logger = logging.getLogger(__name__)


async def handle_webhook_event(event: Dict[str, Any]) -> Dict[str, str]:
    """
    Handle Stripe webhook events.

    Args:
        event: Stripe event object

    Returns:
        Result with status
    """
    event_type = event.get("type")
    event_id = event.get("id")

    logger.info(f"Processing webhook event: {event_type} ({event_id})")

    # Check for duplicate event (idempotency)
    supabase = get_supabase_client()
    existing = supabase.table("stripe_webhook_events").select("id").eq(
        "stripe_event_id", event_id
    ).execute()

    if existing.data:
        logger.info(f"Event {event_id} already processed")
        return {"status": "already_processed", "event_id": event_id}

    # Store event
    supabase.table("stripe_webhook_events").insert({
        "stripe_event_id": event_id,
        "event_type": event_type,
        "event_data": event,
        "processed": False,
    }).execute()

    try:
        # Route to appropriate handler
        if event_type.startswith("customer.subscription."):
            await handle_subscription_event(event)
        elif event_type.startswith("invoice."):
            await handle_invoice_event(event)
        elif event_type.startswith("payment_intent."):
            await handle_payment_event(event)
        else:
            logger.warning(f"Unhandled event type: {event_type}")

        # Mark as processed
        supabase.table("stripe_webhook_events").update({
            "processed": True,
            "processed_at": "NOW()"
        }).eq("stripe_event_id", event_id).execute()

        return {"status": "success", "event_id": event_id}

    except Exception as e:
        logger.error(f"Failed to process event {event_id}: {e}")

        # Mark as failed
        supabase.table("stripe_webhook_events").update({
            "processing_error": str(e),
            "retry_count": supabase.rpc("increment", {"x": 1, "row_id": event_id})
        }).eq("stripe_event_id", event_id).execute()

        raise


async def handle_subscription_event(event: Dict[str, Any]):
    """Handle subscription-related events."""
    event_type = event["type"]
    subscription_data = event["data"]["object"]
    stripe_subscription_id = subscription_data["id"]

    logger.info(f"Handling subscription event: {event_type}")

    # Get local subscription
    supabase = get_supabase_client()
    result = supabase.table("subscriptions").select("*").eq(
        "stripe_subscription_id", stripe_subscription_id
    ).single().execute()

    if not result.data:
        logger.warning(f"Subscription not found: {stripe_subscription_id}")
        return

    local_subscription_id = result.data["id"]

    # Handle specific events
    if event_type == "customer.subscription.created":
        logger.info(f"Subscription created in Stripe: {stripe_subscription_id}")
        # Already created by API, nothing to do

    elif event_type == "customer.subscription.updated":
        logger.info(f"Subscription updated: {stripe_subscription_id}")

        # Check for tier changes
        new_price_id = subscription_data["items"]["data"][0]["price"]["id"]
        if new_price_id != result.data["stripe_price_id"]:
            logger.info(f"Tier changed to {new_price_id}")
            from app.models.subscription import SubscriptionUpdate
            await subscription_service.update_subscription(
                local_subscription_id,
                SubscriptionUpdate(stripe_price_id=new_price_id)
            )

    elif event_type == "customer.subscription.deleted":
        logger.info(f"Subscription canceled: {stripe_subscription_id}")
        await subscription_service.cancel_subscription(
            local_subscription_id, immediate=True
        )

    elif event_type == "customer.subscription.trial_will_end":
        logger.info(f"Trial ending soon: {stripe_subscription_id}")
        # TODO: Send email notification

    else:
        logger.warning(f"Unhandled subscription event: {event_type}")


async def handle_invoice_event(event: Dict[str, Any]):
    """Handle invoice-related events."""
    event_type = event["type"]
    invoice_data = event["data"]["object"]

    logger.info(f"Handling invoice event: {event_type}")

    if event_type == "invoice.paid":
        # Subscription renewed successfully
        subscription_id = invoice_data.get("subscription")
        if subscription_id:
            supabase = get_supabase_client()
            result = supabase.table("subscriptions").select("id").eq(
                "stripe_subscription_id", subscription_id
            ).single().execute()

            if result.data:
                await subscription_service.process_period_renewal(result.data["id"])

    elif event_type == "invoice.payment_failed":
        # Payment failed - mark subscription as past_due
        subscription_id = invoice_data.get("subscription")
        if subscription_id:
            supabase = get_supabase_client()
            result = supabase.table("subscriptions").select("id").eq(
                "stripe_subscription_id", subscription_id
            ).single().execute()

            if result.data:
                from app.models.subscription import SubscriptionUpdate
                await subscription_service.update_subscription(
                    result.data["id"],
                    SubscriptionUpdate(status="past_due")
                )


async def handle_payment_event(event: Dict[str, Any]):
    """Handle payment intent events (for one-time credits)."""
    event_type = event["type"]

    logger.info(f"Handling payment event: {event_type}")

    # Existing credit payment handling
    # (Keep existing implementation)
    pass
```

---

### Task 3: Register Routes in Main App (10 min)

**Update**: `/backend/app/main.py`

```python
# Add to imports
from app.api.subscriptions import router as subscriptions_router

# Add to app
app.include_router(subscriptions_router)
```

---

### Task 4: Create Stripe Checkout Session Endpoint (40 min)

**Add to** `/backend/app/api/subscriptions.py`:

```python
from pydantic import BaseModel

class CheckoutRequest(BaseModel):
    tier_id: str
    success_url: str | None = None
    cancel_url: str | None = None


@router.post("/checkout", response_model=Dict[str, Any])
async def create_checkout_session(
    request: CheckoutRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Create Stripe checkout session for subscription.

    Request Body:
    - tier_id: Subscription tier (flow_starter, flow_pro, flow_business)
    - success_url: Optional success redirect URL
    - cancel_url: Optional cancel redirect URL

    Returns:
    - checkout_url: Stripe checkout URL to redirect user
    - session_id: Stripe session ID

    Responses:
    - 200: Checkout session created
    - 400: Invalid tier
    - 401: Unauthorized
    """
    from app.config.pricing import pricing_config
    import os

    # Validate tier
    tier = pricing_config.get_tier(request.tier_id)
    if not tier or not tier.is_subscription:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid subscription tier: {request.tier_id}"
        )

    if not tier.stripe_price_id:
        raise HTTPException(
            status_code=400,
            detail=f"Stripe price not configured for tier: {request.tier_id}"
        )

    # Create or get Stripe customer
    from app.core.database import get_supabase_client
    supabase = get_supabase_client()

    user_result = supabase.table("users").select("stripe_customer_id").eq(
        "id", current_user["id"]
    ).single().execute()

    stripe_customer_id = user_result.data.get("stripe_customer_id") if user_result.data else None

    if not stripe_customer_id:
        # Create Stripe customer
        import stripe
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

        customer = stripe.Customer.create(
            email=current_user["email"],
            metadata={"user_id": current_user["id"]}
        )
        stripe_customer_id = customer.id

        # Update user record
        supabase.table("users").update({
            "stripe_customer_id": stripe_customer_id
        }).eq("id", current_user["id"]).execute()

    # Create checkout session
    import stripe
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    success_url = request.success_url or f"{frontend_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = request.cancel_url or f"{frontend_url}/pricing"

    session = stripe.checkout.Session.create(
        customer=stripe_customer_id,
        payment_method_types=["card"],
        mode="subscription",
        line_items=[{
            "price": tier.stripe_price_id,
            "quantity": 1,
        }],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "user_id": current_user["id"],
            "tier_id": request.tier_id,
        },
        subscription_data={
            "metadata": {
                "user_id": current_user["id"],
                "tier_id": request.tier_id,
            }
        }
    )

    logger.info(f"Created checkout session for user {current_user['id']}: {session.id}")

    return {
        "success": True,
        "checkout_url": session.url,
        "session_id": session.id,
    }
```

---

### Task 5: Add Webhook Endpoint (20 min)

**Create**: `/backend/app/api/webhooks.py` (or update existing)

```python
"""
Stripe webhook endpoint.
"""

from fastapi import APIRouter, Request, HTTPException, Header
import logging

from app.services.webhook_service import handle_webhook_event
from app.services.stripe_service import stripe_service

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature")
):
    """
    Handle Stripe webhook events.

    This endpoint receives events from Stripe and processes them.
    """
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")

    payload = await request.body()

    # Verify webhook signature
    verification = await stripe_service.verify_webhook_signature(
        payload, stripe_signature
    )

    if not verification["success"]:
        logger.error(f"Webhook verification failed: {verification['error']}")
        raise HTTPException(status_code=400, detail=verification["error"])

    event = verification["event"]

    # Process event
    try:
        result = await handle_webhook_event(event)
        return result
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

Register in `main.py`:

```python
from app.api.webhooks import router as webhooks_router
app.include_router(webhooks_router)
```

---

## ✅ Verification Checklist

### 1. Routes Registered

```bash
docker compose exec backend python -c "
from app.main import app
routes = [route.path for route in app.routes]
subscription_routes = [r for r in routes if 'subscription' in r]
print('Subscription routes:', subscription_routes)
"
```

Expected: At least 6 routes.

### 2. Swagger Documentation

```bash
# Open Swagger UI
open http://localhost:8000/docs

# Check for /api/subscriptions endpoints
```

### 3. Test Status Endpoint

```bash
# Get auth token first
TOKEN="your_test_token"

curl -X GET http://localhost:8000/api/subscriptions/status \
  -H "Authorization: Bearer $TOKEN"
```

Expected: JSON with subscription status.

### 4. Test Checkout Endpoint

```bash
curl -X POST http://localhost:8000/api/subscriptions/checkout \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tier_id": "flow_pro"}'
```

Expected: JSON with `checkout_url`.

### 5. Test Webhook Endpoint

```bash
# Use Stripe CLI to test
stripe listen --forward-to localhost:8000/api/webhooks/stripe

# In another terminal
stripe trigger customer.subscription.created
```

Expected: Event processed successfully.

---

## 🚨 Common Issues & Solutions

### Issue 1: Routes Not Found

**Error**: `404 Not Found` on subscription endpoints

**Solution**:

```python
# Verify router is included in main.py
from app.api.subscriptions import router as subscriptions_router
app.include_router(subscriptions_router)
```

### Issue 2: Auth Dependency Fails

**Error**: `HTTPException: Unauthorized`

**Solution**:

```bash
# Check auth middleware is working
# Get valid token from Supabase auth
```

### Issue 3: Stripe API Key Not Set

**Error**: `ValueError: STRIPE_SECRET_KEY not set`

**Solution**:

```bash
# Check .env file
echo $STRIPE_SECRET_KEY
```

---

## 📊 Success Criteria

Phase 3 is complete when:

- ✅ All subscription endpoints created
- ✅ Checkout session creation works
- ✅ Webhook handler processes events
- ✅ Swagger docs show all endpoints
- ✅ All tests pass
- ✅ Code committed to git

---

## 🎯 Next Step

After completing Phase 3:
→ **Proceed to Phase 4**: Frontend Subscription UI & Testing (PARALLEL)
→ **Prompts**: `05-subscription-frontend-ui.md` AND `06-subscription-testing-suite.md`

---

**Time check**: This should take ~4 hours. If taking longer, ask for help!

Good luck! 🚀
