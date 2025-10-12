"""
Usage limit service for freemium feature gating.

This service handles checking user limits before allowing optimization operations.
It integrates with user profiles to determine Pro status and checks monthly usage limits.
"""

import logging
from datetime import date
from typing import Any
from uuid import UUID

from app.core.database import SupabaseSession
from app.models.usage import (
    UsageLimitCheckResponse,
    UsageStatsResponse,
)
from app.services.usage_tracking_service import (
    UsageTrackingError,
    UsageTrackingService,
)

logger = logging.getLogger(__name__)

# Credit tiers for cv-match pricing model
CREDIT_TIERS = {
    "free": 3,
    "basic": 10,
    "pro": 50,
    "enterprise": 1000
}


class UsageLimitError(Exception):
    """Base exception for usage limit operations."""

    pass


class UserNotFoundError(UsageLimitError):
    """Raised when user profile is not found."""

    pass


class UsageLimitExceededError(UsageLimitError):
    """Raised when user has exceeded their usage limits."""

    pass


class UsageLimitService:
    """
    Service for checking and enforcing user usage limits.

    Handles freemium feature gating by checking user's Pro status
    and monthly usage limits before allowing optimization operations.
    """

    def __init__(self, db: SupabaseSession):
        self.db = db
        self.usage_tracking_service = UsageTrackingService(db)

    async def get_user_credits(self, user_id: UUID) -> dict[str, Any]:
        """
        Get user credit information.

        Args:
            user_id: The user ID to get credits for

        Returns:
            Dictionary containing user credit data

        Raises:
            UserNotFoundError: If user credits record is not found
        """
        try:
            # Get user credits from user_credits table
            result = self.db.client.table("user_credits").select("*").eq("user_id", str(user_id)).execute()

            if not result.data:
                # Create initial credits record for new user
                initial_data = {
                    "user_id": str(user_id),
                    "credits_remaining": CREDIT_TIERS["free"],
                    "total_credits": CREDIT_TIERS["free"],
                    "subscription_tier": "free",
                    "is_pro": False
                }
                create_result = self.db.client.table("user_credits").insert(initial_data).execute()
                if not create_result.data:
                    raise UserNotFoundError(f"Failed to create credits record for user {user_id}")
                return create_result.data[0]

            return result.data[0]

        except Exception as e:
            logger.error(f"Failed to get user credits for {user_id}: {str(e)}")
            raise UsageLimitError(f"Failed to retrieve user credits: {str(e)}")

    async def check_usage_limit(self, user_id: UUID) -> UsageLimitCheckResponse:
        """
        Check if user can perform optimization based on their credit balance.

        Args:
            user_id: The user ID to check limits for

        Returns:
            UsageLimitCheckResponse with limit information and whether optimization is allowed

        Raises:
            UserNotFoundError: If user credits record is not found
            UsageLimitError: If there's an error checking limits
        """
        try:
            # Get user credits
            credits = await self.get_user_credits(user_id)
            is_pro = credits.get("is_pro", False)
            credits_remaining = credits.get("credits_remaining", 0)
            subscription_tier = credits.get("subscription_tier", "free")

            # Get current month usage for tracking
            current_usage = await self.usage_tracking_service.get_current_month_usage(user_id)
            if current_usage is None:
                current_usage = await self.usage_tracking_service.create_or_update_usage(user_id)

            total_used = current_usage.free_optimizations_used + current_usage.paid_optimizations_used

            # Credit cost per optimization (1 credit for free users, 0 for pro users)
            credit_cost = 0 if is_pro else 1

            # Determine if user can optimize
            can_optimize = is_pro or credits_remaining >= credit_cost

            if not can_optimize:
                reason = f"Insufficient credits. You have {credits_remaining} credits remaining."
                upgrade_prompt = "Upgrade to Pro for unlimited optimizations or purchase more credits."
            else:
                reason = None
                upgrade_prompt = None

            # Calculate "free optimizations" equivalent for compatibility
            free_limit = CREDIT_TIERS.get(subscription_tier, CREDIT_TIERS["free"])
            remaining_free = max(0, credits_remaining)

            return UsageLimitCheckResponse(
                can_optimize=can_optimize,
                is_pro=is_pro,
                free_optimizations_used=total_used,
                free_optimizations_limit=free_limit,
                remaining_free_optimizations=remaining_free,
                tier=subscription_tier,
                reason=reason,
                upgrade_prompt=upgrade_prompt,
            )

        except UserNotFoundError:
            raise
        except UsageTrackingError as e:
            logger.error(f"Usage tracking error for user {user_id}: {str(e)}")
            raise UsageLimitError(f"Failed to check usage limits: {str(e)}")
        except Exception as e:
            logger.error(f"Error checking usage limits for user {user_id}: {str(e)}")
            raise UsageLimitError(f"Failed to check usage limits: {str(e)}")

    async def get_usage_stats(self, user_id: UUID) -> UsageStatsResponse:
        """
        Get comprehensive usage statistics for a user.

        Args:
            user_id: The user ID to get stats for

        Returns:
            UsageStatsResponse with detailed usage information

        Raises:
            UserNotFoundError: If user profile is not found
            UsageLimitError: If there's an error retrieving stats
        """
        try:
            # Get user credits (which includes is_pro status)
            credits = await self.get_user_credits(user_id)
            is_pro = credits.get("is_pro", False)

            # Get current month usage
            current_usage = await self.usage_tracking_service.get_current_month_usage(user_id)

            if current_usage is None:
                # No usage record yet, create one
                current_usage = await self.usage_tracking_service.create_or_update_usage(user_id)

            free_used = current_usage.free_optimizations_used
            paid_used = current_usage.paid_optimizations_used
            free_limit = 1  # Free users get 1 optimization per month

            # Calculate remaining and totals
            remaining_free = max(0, free_limit - free_used)
            total_this_month = free_used + paid_used

            # Determine if user can optimize
            can_optimize = is_pro or free_used < free_limit

            return UsageStatsResponse(
                user_id=user_id,
                current_month_date=current_usage.month_date,
                free_optimizations_used=free_used,
                paid_optimizations_used=paid_used,
                free_optimizations_limit=free_limit,
                is_pro=is_pro,
                can_optimize=can_optimize,
                remaining_free_optimizations=remaining_free,
                total_optimizations_this_month=total_this_month,
            )

        except UserNotFoundError:
            raise
        except UsageTrackingError as e:
            logger.error(f"Usage tracking error for user {user_id}: {str(e)}")
            raise UsageLimitError(f"Failed to get usage stats: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting usage stats for user {user_id}: {str(e)}")
            raise UsageLimitError(f"Failed to get usage stats: {str(e)}")

    async def deduct_credits(self, user_id: UUID, amount: int, operation_id: str) -> bool:
        """
        Deduct credits from user account atomically.

        This method uses a database-level atomic operation to prevent race conditions.
        It checks and updates credits in a single operation using PostgreSQL's
        atomic update with a condition to ensure sufficient credits.

        Args:
            user_id: The user ID to deduct credits from
            amount: Amount of credits to deduct
            operation_id: ID of the operation being performed

        Returns:
            True if credits were deducted successfully, False if insufficient credits

        Raises:
            UsageLimitError: If there's an error deducting credits
        """
        try:
            # Use atomic database operation to prevent race conditions
            # This updates credits only if sufficient credits are available
            rpc_params = {
                "p_user_id": str(user_id),
                "p_amount": amount
            }

            # Call a PostgreSQL function for atomic credit deduction
            # This prevents race conditions by doing the check and update in one transaction
            try:
                result = self.db.client.rpc("deduct_credits_atomically", rpc_params).execute()
            except Exception as rpc_error:
                # RPC function might not exist, use fallback
                logger.warning(f"Atomic credit deduction RPC not available, using fallback: {str(rpc_error)}")
                return await self.deduct_credits_fallback(user_id, amount, operation_id)

            if not result.data or not result.data[0].get("success", False):
                # Check if it's insufficient credits or another error
                if result.data and result.data[0].get("reason") == "insufficient_credits":
                    logger.warning(f"Insufficient credits for user {user_id}")
                    return False
                else:
                    error_msg = result.data[0].get("error", "Unknown error") if result.data else "No response"
                    logger.warning(f"Atomic deduction failed, using fallback: {error_msg}")
                    return await self.deduct_credits_fallback(user_id, amount, operation_id)

            new_credits = result.data[0].get("new_balance", 0)

            # Record credit transaction after successful deduction
            transaction_data = {
                "user_id": str(user_id),
                "amount": -amount,  # Negative for deduction
                "type": "debit",
                "source": "optimization",
                "description": f"Credit deduction for operation {operation_id}",
                "operation_id": operation_id,
                "balance_after": new_credits
            }

            # Insert transaction record - this is done after the atomic credit deduction
            transaction_result = self.db.client.table("credit_transactions").insert(transaction_data).execute()
            if not transaction_result.data:
                # Log warning but don't fail the operation - credits were already deducted
                logger.warning(f"Failed to record credit transaction for user {user_id}, operation {operation_id}")

            logger.info(f"Deducted {amount} credits from user {user_id}, remaining: {new_credits}")
            return True

        except UsageLimitError:
            raise
        except Exception as e:
            logger.error(f"Error deducting credits for user {user_id}: {str(e)}")
            raise UsageLimitError(f"Failed to deduct credits: {str(e)}")

    async def deduct_credits_fallback(self, user_id: UUID, amount: int, operation_id: str) -> bool:
        """
        Fallback method for credit deduction using standard operations.

        This is used if the atomic RPC function is not available.
        It's less optimal than the atomic method but provides better error handling
        than the basic implementation.

        Args:
            user_id: The user ID to deduct credits from
            amount: Amount of credits to deduct
            operation_id: ID of the operation being performed

        Returns:
            True if credits were deducted successfully, False if insufficient credits

        Raises:
            UsageLimitError: If there's an error deducting credits
        """
        try:
            # Ensure user record exists
            credits = await self.get_user_credits(user_id)
            current_credits = credits.get("credits_remaining", 0)

            if current_credits < amount:
                logger.warning(f"Insufficient credits for user {user_id}: {current_credits} < {amount}")
                return False

            # Use optimistic locking with a version check to prevent race conditions
            # Update with a condition that ensures credits haven't changed since we read them
            result = self.db.client.table("user_credits").update({
                "credits_remaining": current_credits - amount,
                "updated_at": "now()"
            }).eq("user_id", str(user_id)).eq("credits_remaining", current_credits).execute()

            if not result.data:
                # If no rows were updated, it means either:
                # 1. The user doesn't exist (shouldn't happen due to get_user_credits)
                # 2. The credits changed between our read and update (race condition)
                # 3. Another concurrent operation deducted credits
                logger.warning(f"Concurrent credit modification detected for user {user_id}, retrying...")

                # Retry once after a brief delay
                import asyncio
                await asyncio.sleep(0.05)  # 50ms delay

                # Try the atomic method as a fallback
                return await self.deduct_credits(user_id, amount, operation_id)

            new_credits = current_credits - amount

            # Record credit transaction
            transaction_data = {
                "user_id": str(user_id),
                "amount": -amount,
                "type": "debit",
                "source": "optimization",
                "description": f"Credit deduction for operation {operation_id}",
                "operation_id": operation_id,
                "balance_after": new_credits
            }

            self.db.client.table("credit_transactions").insert(transaction_data).execute()

            logger.info(f"Deducted {amount} credits from user {user_id}, remaining: {new_credits}")
            return True

        except Exception as e:
            logger.error(f"Error in fallback credit deduction for user {user_id}: {str(e)}")
            raise UsageLimitError(f"Failed to deduct credits: {str(e)}")

    async def add_credits(self, user_id: UUID, amount: int, source: str, description: str | None = None) -> bool:
        """
        Add credits to user account.

        Args:
            user_id: The user ID to add credits to
            amount: Amount of credits to add
            source: Source of credits (e.g., "payment", "bonus")
            description: Optional description

        Returns:
            True if credits were added successfully

        Raises:
            UsageLimitError: If there's an error adding credits
        """
        try:
            # Get current credits
            credits = await self.get_user_credits(user_id)
            current_credits = credits.get("credits_remaining", 0)
            total_credits = credits.get("total_credits", 0)

            # Add credits
            new_credits = current_credits + amount
            new_total = total_credits + amount
            result = self.db.client.table("user_credits").update({
                "credits_remaining": new_credits,
                "total_credits": new_total
            }).eq("user_id", str(user_id)).execute()

            if not result.data:
                raise UsageLimitError("Failed to update user credits")

            # Record credit transaction
            transaction_data = {
                "user_id": str(user_id),
                "amount": amount,  # Positive for addition
                "type": "credit",
                "source": source,
                "description": description or f"Credit addition from {source}"
            }
            self.db.client.table("credit_transactions").insert(transaction_data).execute()

            logger.info(f"Added {amount} credits to user {user_id}, new total: {new_credits}")
            return True

        except Exception as e:
            logger.error(f"Error adding credits for user {user_id}: {str(e)}")
            raise UsageLimitError(f"Failed to add credits: {str(e)}")

    async def check_and_track_usage(self, user_id: UUID, optimization_type: str = "free", cost_credits: int = 1) -> UsageLimitCheckResponse:
        """
        Check usage limits and track usage if allowed.

        This method combines limit checking with usage tracking for optimization.
        It first checks if the user can perform optimization, deducts credits if needed,
        and tracks the usage.

        Args:
            user_id: The user ID to check and track for
            optimization_type: Type of optimization ("free" or "paid")
            cost_credits: Number of credits this operation costs

        Returns:
            UsageLimitCheckResponse with limit information

        Raises:
            UsageLimitExceededError: If user has exceeded their limits
            UserNotFoundError: If user credits record is not found
            UsageLimitError: If there's an error
        """
        try:
            # First check if user can optimize
            limit_check = await self.check_usage_limit(user_id)

            if not limit_check.can_optimize:
                raise UsageLimitExceededError(limit_check.reason or "Usage limit exceeded")

            # Generate operation ID for tracking
            import uuid
            operation_id = str(uuid.uuid4())

            # Deduct credits if not a Pro user
            if not limit_check.is_pro and cost_credits > 0:
                success = await self.deduct_credits(user_id, cost_credits, operation_id)
                if not success:
                    raise UsageLimitExceededError("Failed to deduct credits")

            # Track the usage
            await self.usage_tracking_service.increment_usage(user_id=user_id, optimization_type=optimization_type)

            # Update the response to reflect new usage
            limit_check.free_optimizations_used += 1
            limit_check.remaining_free_optimizations = max(
                0, limit_check.remaining_free_optimizations - cost_credits
            )

            logger.info(f"Tracked {optimization_type} usage for user {user_id}, cost: {cost_credits} credits")
            return limit_check

        except (UserNotFoundError, UsageLimitExceededError, UsageTrackingError):
            raise
        except Exception as e:
            logger.error(f"Error checking and tracking usage for user {user_id}: {str(e)}")
            raise UsageLimitError(f"Failed to check and track usage: {str(e)}")

    async def reset_monthly_usage_if_needed(self, user_id: UUID) -> bool:
        """
        Reset monthly usage if we're in a new month.

        This is a utility method to handle month boundaries. It checks if the
        current month usage record exists and creates one if it doesn't.

        Args:
            user_id: The user ID to reset usage for

        Returns:
            True if usage was reset, False if existing record was found
        """
        try:
            current_usage = await self.usage_tracking_service.get_current_month_usage(user_id)

            if current_usage is None:
                # No record for current month, create one
                await self.usage_tracking_service.create_or_update_usage(user_id)
                logger.info(f"Created new monthly usage record for user {user_id}")
                return True

            return False

        except UsageTrackingError:
            raise
        except Exception as e:
            logger.error(f"Error resetting monthly usage for user {user_id}: {str(e)}")
            raise UsageLimitError(f"Failed to reset monthly usage: {str(e)}")
