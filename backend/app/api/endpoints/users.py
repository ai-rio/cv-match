"""
User endpoints for CV-Match API.

Provides endpoints for retrieving user information and credits.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth_dependencies import get_current_user
from app.core.database import SupabaseSession
from app.models.usage import UserCreditsResponse
from app.services.usage_limit_service import UsageLimitService

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_db() -> SupabaseSession:
    """Get database session."""
    return SupabaseSession()


@router.get("/credits", response_model=UserCreditsResponse)
async def get_user_credits(
    current_user: dict = Depends(get_current_user), db: SupabaseSession = Depends(get_db)
) -> UserCreditsResponse:
    """
    Get current user's credit balance and subscription information.

    This endpoint returns detailed information about the user's credit balance,
    subscription tier, and whether they can perform optimizations.

    Args:
        current_user: Currently authenticated user
        db: Database session

    Returns:
        UserCreditsResponse with credit information

    Raises:
        HTTPException: If there's an error retrieving credit information
    """
    try:
        usage_limit_service = UsageLimitService(db)
        user_id = UUID(current_user["id"])

        # Get user credits information
        credits_data = await usage_limit_service.get_user_credits(user_id)
        credits_remaining = credits_data.get("credits_remaining", 0)
        total_credits = credits_data.get("total_credits", 0)
        is_pro = credits_data.get("is_pro", False)
        subscription_tier = credits_data.get("subscription_tier", "free")

        # Check if user can optimize
        # Pro users have unlimited access, others need credits
        can_optimize = is_pro or credits_remaining > 0

        # Generate upgrade prompt if needed
        upgrade_prompt = None
        if not can_optimize:
            if is_pro:
                upgrade_prompt = "Your Pro subscription is active. Contact support if you're seeing this message."
            else:
                upgrade_prompt = "Purchase more credits to continue optimizing your resume."

        logger.info(
            f"Retrieved credits for user {current_user['id']}: {credits_remaining} credits, tier: {subscription_tier}"
        )

        return UserCreditsResponse(
            credits_remaining=credits_remaining,
            tier=subscription_tier,
            can_optimize=can_optimize,
            upgrade_prompt=upgrade_prompt,
            is_pro=is_pro,
            total_credits=total_credits,
        )

    except Exception as e:
        logger.error(f"Error retrieving credits for user {current_user['id']}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve credit information",
        )
