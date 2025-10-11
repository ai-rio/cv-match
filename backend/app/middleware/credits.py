"""
Credit Check Middleware

This module provides middleware to automatically check user credits before
allowing access to paid operations like resume optimization.

Usage:
    @router.post("/optimize")
    @require_credits(1)
    async def optimize_resume(...):
        # Credits already checked, user has sufficient credits
        ...
"""

from functools import wraps
from typing import Callable, Dict, Any, Optional
from uuid import UUID
from fastapi import HTTPException, Depends, status
from app.core.auth import get_current_user
from app.services.usage_limit_service import UsageLimitService
from app.core.supabase import get_supabase_client
import logging

logger = logging.getLogger(__name__)

def require_credits(credits_needed: int = 1):
    """
    Decorator to check user has sufficient credits before allowing access.

    Args:
        credits_needed (int): Number of credits required for the operation

    Returns:
        Dependency that throws HTTPException if insufficient credits

    Usage:
        @router.post("/optimize")
        @require_credits(1)
        async def optimize_resume(
            request: OptimizationRequest,
            current_user: dict = Depends(get_current_user_with_credits)
        ):
            # Credits already verified, proceed with optimization
            ...
    """
    async def credit_dependency(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        """
        Check if user has sufficient credits and return user info.

        Raises:
            HTTPException: If user has insufficient credits

        Returns:
            Dict containing user information
        """
        try:
            user_id = current_user.get("id")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not authenticated"
                )

            # Initialize usage limit service
            supabase = get_supabase_client()
            usage_service = UsageLimitService(supabase)

            # Check usage limits
            limit_check = await usage_service.check_usage_limit(UUID(user_id))

            if not limit_check.can_optimize:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail={
                        "error": "Insufficient credits",
                        "message": "You don't have enough credits to perform this operation",
                        "credits_remaining": limit_check.remaining_free_optimizations,
                        "credits_needed": credits_needed,
                        "tier": limit_check.tier,
                        "upgrade_prompt": limit_check.upgrade_prompt,
                        "pricing_url": "/pricing"
                    }
                )

            # Log successful credit check
            logger.info(
                f"Credit check passed for user {user_id}: "
                f"{limit_check.remaining_free_optimizations} credits remaining"
            )

            # Add credit info to user dict for downstream use
            current_user["credits_info"] = {
                "remaining": limit_check.remaining_free_optimizations,
                "tier": limit_check.tier,
                "can_optimize": limit_check.can_optimize
            }

            return current_user

        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Error checking credits for user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify credits"
            )

    return Depends(credit_dependency)


def get_current_user_with_credits(credits_needed: int = 1):
    """
    Combined dependency that gets current user and checks credits in one call.

    This is more efficient than separate get_current_user and require_credits calls.

    Args:
        credits_needed (int): Number of credits required

    Returns:
        User with credit information included
    """
    return require_credits(credits_needed)


class CreditChecker:
    """
    Utility class for checking credits outside of dependency injection.

    Useful for service classes that need to check credits programmatically.
    """

    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.usage_service = UsageLimitService(supabase_client)

    async def check_user_credits(self, user_id: str, credits_needed: int = 1) -> Dict[str, Any]:
        """
        Check if a user has sufficient credits.

        Args:
            user_id (str): The user ID to check
            credits_needed (int): Number of credits needed

        Returns:
            Dict with credit check result

        Raises:
            ValueError: If insufficient credits
        """
        limit_check = await self.usage_service.check_usage_limit(UUID(user_id))

        if not limit_check.can_optimize:
            raise ValueError(f"Insufficient credits: {limit_check.remaining_free_optimizations} remaining, {credits_needed} needed")

        return {
            "can_optimize": True,
            "remaining": limit_check.remaining_free_optimizations,
            "tier": limit_check.tier,
            "user_id": user_id
        }

    async def get_credit_balance(self, user_id: str) -> Dict[str, Any]:
        """
        Get the current credit balance for a user.

        Args:
            user_id (str): The user ID to check

        Returns:
            Dict with current credit information
        """
        limit_check = await self.usage_service.check_usage_limit(UUID(user_id))

        return {
            "credits_remaining": limit_check.remaining_free_optimizations,
            "tier": limit_check.tier,
            "can_optimize": limit_check.can_optimize,
            "upgrade_prompt": limit_check.upgrade_prompt,
            "user_id": user_id
        }


# Utility function for manual credit checking in services
async def verify_credits_manual(user_id: str, credits_needed: int = 1, supabase_client=None) -> bool:
    """
    Manual credit verification utility for use in service classes.

    Args:
        user_id (str): User ID to verify
        credits_needed (int): Credits needed
        supabase_client: Supabase client instance

    Returns:
        bool: True if user has sufficient credits
    """
    if not supabase_client:
        from app.core.supabase import get_supabase_client
        supabase_client = get_supabase_client()

    checker = CreditChecker(supabase_client)
    try:
        await checker.check_user_credits(user_id, credits_needed)
        return True
    except ValueError:
        return False