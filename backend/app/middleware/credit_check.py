"""
Credit check middleware for protecting API endpoints.
"""

import logging
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.core.auth import get_current_user
from app.core.database import SupabaseSession
from app.services.usage_limit_service import UsageLimitService

logger = logging.getLogger(__name__)

# Database dependency
async def get_db() -> SupabaseSession:
    """Get database session."""
    return SupabaseSession()

async def check_credits(
    current_user: dict = Depends(get_current_user),
    db: SupabaseSession = Depends(get_db)
) -> dict:
    """
    Check if user has sufficient credits for optimization operations.

    This dependency function checks if the user has enough credits before
    allowing access to protected endpoints. It raises an HTTPException
    if credits are insufficient.

    Args:
        current_user: Currently authenticated user
        db: Database session

    Returns:
        User data with credit information

    Raises:
        HTTPException: If user has insufficient credits (402 Payment Required)
    """
    try:
        usage_limit_service = UsageLimitService(db)
        user_id = UUID(current_user["id"])

        # Check user credits
        credits_data = await usage_limit_service.get_user_credits(user_id)
        credits_remaining = credits_data.get("credits_remaining", 0)
        is_pro = credits_data.get("is_pro", False)

        # Pro users have unlimited access, check credits for others
        if not is_pro and credits_remaining <= 0:
            logger.warning(f"User {current_user['id']} has insufficient credits: {credits_remaining}")
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "Insufficient credits",
                    "message": f"You have {credits_remaining} credits remaining. Purchase more credits to continue.",
                    "credits_remaining": credits_remaining,
                    "upgrade_prompt": "Purchase more credits to continue optimizing your resume."
                }
            )

        logger.info(f"Credit check passed for user {current_user['id']}: {credits_remaining} credits remaining")
        return {
            **current_user,
            "credits_remaining": credits_remaining,
            "is_pro": is_pro
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking credits for user {current_user['id']}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify credits"
        )

async def require_pro_or_credits(
    current_user: dict = Depends(get_current_user),
    db: SupabaseSession = Depends(get_db)
) -> dict:
    """
    Check if user has Pro status or sufficient credits.

    This is a more permissive check that allows either Pro users or users
    with sufficient credits to access endpoints.

    Args:
        current_user: Currently authenticated user
        db: Database session

    Returns:
        User data with credit information

    Raises:
        HTTPException: If user is neither Pro nor has sufficient credits
    """
    try:
        usage_limit_service = UsageLimitService(db)
        user_id = UUID(current_user["id"])

        # Check user credits and status
        credits_data = await usage_limit_service.get_user_credits(user_id)
        credits_remaining = credits_data.get("credits_remaining", 0)
        is_pro = credits_data.get("is_pro", False)

        # Allow access if Pro user OR has credits
        if not is_pro and credits_remaining <= 0:
            logger.warning(f"User {current_user['id']} lacks Pro status and has insufficient credits: {credits_remaining}")
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "Premium access required",
                    "message": "Upgrade to Pro for unlimited access or purchase credits to continue.",
                    "credits_remaining": credits_remaining,
                    "is_pro": is_pro,
                    "upgrade_prompt": "Upgrade to Pro for unlimited optimizations or purchase credit packs."
                }
            )

        return {
            **current_user,
            "credits_remaining": credits_remaining,
            "is_pro": is_pro
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking Pro/credits for user {current_user['id']}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify access"
        )