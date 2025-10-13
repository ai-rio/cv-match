"""
Subscription API endpoints for CV-Match.
"""

import logging
import os
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.config.pricing import pricing_config
from app.core.auth import get_current_user
from app.models.subscription import (
    SubscriptionCreate,
    SubscriptionDetails,
    SubscriptionStatus,
    SubscriptionUpdate,
)
from app.services.subscription_service import subscription_service

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])
logger = logging.getLogger(__name__)


class CheckoutRequest(BaseModel):
    tier_id: str
    success_url: str | None = None
    cancel_url: str | None = None


@router.get("/status", response_model=SubscriptionStatus)
async def get_subscription_status(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> SubscriptionStatus:
    """Get user's subscription + credit status."""
    try:
        return await subscription_service.get_subscription_status(current_user["id"])
    except Exception as e:
        logger.error(f"Failed to get status for user {current_user['id']}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/current")
async def get_current_subscription(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> SubscriptionDetails | None:
    """Get user's current active subscription."""
    try:
        subscription = await subscription_service.get_active_subscription(current_user["id"])
        if not subscription:
            return None
        return await subscription_service.get_subscription_details(subscription["id"])
    except Exception as e:
        logger.error(f"Failed to get subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=SubscriptionDetails, status_code=201)
async def create_subscription(
    subscription_data: SubscriptionCreate, current_user: dict[str, Any] = Depends(get_current_user)
) -> SubscriptionDetails:
    """Create new subscription after Stripe checkout."""
    if subscription_data.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Não pode criar assinatura para outro usuário")

    try:
        return await subscription_service.create_subscription(subscription_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create subscription: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao criar assinatura")


@router.patch("/{subscription_id}", response_model=SubscriptionDetails)
async def update_subscription(
    subscription_id: str,
    update_data: SubscriptionUpdate,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> SubscriptionDetails:
    """Update subscription (tier, status)."""
    try:
        # Verify ownership
        subscription = await subscription_service.get_subscription_details(subscription_id)
        if subscription.user_id != current_user["id"]:
            raise HTTPException(status_code=403, detail="Esta não é a sua assinatura")

        return await subscription_service.update_subscription(subscription_id, update_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update subscription: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao atualizar assinatura")


@router.post("/{subscription_id}/cancel", response_model=SubscriptionDetails)
async def cancel_subscription(
    subscription_id: str,
    immediate: bool = False,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> SubscriptionDetails:
    """Cancel subscription (immediate or at period end)."""
    try:
        # Verify ownership
        subscription = await subscription_service.get_subscription_details(subscription_id)
        if subscription.user_id != current_user["id"]:
            raise HTTPException(status_code=403, detail="Esta não é a sua assinatura")

        # Cancel in Stripe first
        if subscription.stripe_subscription_id:
            import stripe

            stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

            if immediate:
                stripe.Subscription.delete(subscription.stripe_subscription_id)
            else:
                stripe.Subscription.modify(
                    subscription.stripe_subscription_id, cancel_at_period_end=True
                )

        # Update local record
        return await subscription_service.cancel_subscription(subscription_id, immediate)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to cancel subscription: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao cancelar assinatura")


@router.get("/history")
async def get_usage_history(
    current_user: dict[str, Any] = Depends(get_current_user), limit: int = 50
):
    """Get subscription usage history."""
    try:
        from app.core.database import get_supabase_client

        supabase = get_supabase_client()

        result = (
            supabase.table("subscription_usage_history")
            .select("*")
            .eq("user_id", current_user["id"])
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        return {"success": True, "data": result.data}
    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar histórico")


@router.post("/checkout", response_model=dict[str, Any])
async def create_checkout_session(
    request: CheckoutRequest, current_user: dict[str, Any] = Depends(get_current_user)
) -> dict[str, Any]:
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
    # Validate tier
    tier = pricing_config.get_tier(request.tier_id)
    if not tier or not tier.is_subscription:
        raise HTTPException(
            status_code=400, detail=f"Plano de assinatura inválido: {request.tier_id}"
        )

    if not tier.stripe_price_id:
        raise HTTPException(
            status_code=400, detail=f"Preço Stripe não configurado para o plano: {request.tier_id}"
        )

    # Create or get Stripe customer
    from app.core.database import get_supabase_client

    supabase = get_supabase_client()

    user_result = (
        supabase.table("users")
        .select("stripe_customer_id")
        .eq("id", current_user["id"])
        .single()
        .execute()
    )

    stripe_customer_id = user_result.data.get("stripe_customer_id") if user_result.data else None

    if not stripe_customer_id:
        # Create Stripe customer
        import stripe

        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

        customer = stripe.Customer.create(
            email=current_user["email"], metadata={"user_id": current_user["id"]}
        )
        stripe_customer_id = customer.id

        # Update user record
        supabase.table("users").update({"stripe_customer_id": stripe_customer_id}).eq(
            "id", current_user["id"]
        ).execute()

    # Create checkout session
    import stripe

    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    success_url = (
        request.success_url or f"{frontend_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
    )
    cancel_url = request.cancel_url or f"{frontend_url}/pricing"

    session = stripe.checkout.Session.create(
        customer=stripe_customer_id,
        payment_method_types=["card"],
        mode="subscription",
        line_items=[
            {
                "price": tier.stripe_price_id,
                "quantity": 1,
            }
        ],
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
        },
    )

    logger.info(f"Created checkout session for user {current_user['id']}: {session.id}")

    return {
        "success": True,
        "checkout_url": session.url,
        "session_id": session.id,
    }
