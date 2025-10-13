"""
Pricing API endpoints for CV-Match.
Returns both credit packages (Flex) and subscriptions (Flow).
"""

from typing import Any

from fastapi import APIRouter, HTTPException

from app.config.pricing import pricing_config

router = APIRouter(tags=["pricing"])


@router.get("/")
async def get_all_pricing() -> dict[str, Any]:
    """
    Get all pricing tiers (credits + subscriptions).
    Returns organized structure for frontend.
    """
    all_tiers = pricing_config.get_all_tiers()

    # Separate into categories
    credit_tiers = {
        tier_id: tier
        for tier_id, tier in all_tiers.items()
        if not tier.get("is_subscription", False)
    }

    subscription_tiers = {
        tier_id: tier for tier_id, tier in all_tiers.items() if tier.get("is_subscription", False)
    }

    return {
        "success": True,
        "data": {
            "credits": credit_tiers,
            "subscriptions": subscription_tiers,
            "currency": "brl",
            "market": "brazil",
        },
    }


@router.get("/subscriptions")
async def get_subscription_pricing() -> dict[str, Any]:
    """Get only subscription pricing (Flow tiers)."""
    subscription_tiers = pricing_config.get_subscription_tiers()

    return {
        "success": True,
        "data": {
            tier_id: {
                "id": tier.id,
                "name": tier.name,
                "description": tier.description,
                "price": tier.price,
                "analyses_per_month": tier.analyses_per_month,
                "rollover_limit": tier.rollover_limit,
                "currency": tier.currency,
                "stripe_price_id": tier.stripe_price_id,
                "features": tier.features or [],
                "popular": tier.popular,
            }
            for tier_id, tier in subscription_tiers.items()
        },
    }


@router.get("/credits")
async def get_credit_pricing() -> dict[str, Any]:
    """Get only credit pricing (Flex packages)."""
    credit_tiers = pricing_config.get_credit_tiers()

    return {
        "success": True,
        "data": {
            tier_id: {
                "id": tier.id,
                "name": tier.name,
                "description": tier.description,
                "price": tier.price,
                "credits": tier.credits,
                "currency": tier.currency,
                "stripe_price_id": tier.stripe_price_id,
                "features": tier.features or [],
                "popular": tier.popular,
            }
            for tier_id, tier in credit_tiers.items()
        },
    }


@router.get("/tier/{tier_id}")
async def get_tier_details(tier_id: str) -> dict[str, Any]:
    """Get details for a specific tier."""
    tier = pricing_config.get_tier(tier_id)

    if not tier:
        raise HTTPException(status_code=404, detail=f"Tier not found: {tier_id}")

    return {
        "success": True,
        "data": {
            "id": tier.id,
            "name": tier.name,
            "description": tier.description,
            "price": tier.price,
            "currency": tier.currency,
            "is_subscription": tier.is_subscription,
            "credits": tier.credits if not tier.is_subscription else None,
            "analyses_per_month": tier.analyses_per_month if tier.is_subscription else None,
            "rollover_limit": tier.rollover_limit if tier.is_subscription else None,
            "stripe_price_id": tier.stripe_price_id,
            "features": tier.features or [],
            "popular": tier.popular,
        },
    }
