"""
Enhanced usage middleware for credits AND subscriptions.
"""

from fastapi import Request, HTTPException
from app.services.subscription_service import subscription_service
from app.services.usage_limit_service import UsageLimitService
from app.core.database import SupabaseSession


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
        usage_service = UsageLimitService(SupabaseSession())
        await usage_service.check_and_track_usage(user_id, "free", 1)
        return {"source": "credits", "type": "credit"}