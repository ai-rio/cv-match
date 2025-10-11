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

        # Parse datetime strings
        current_period_start = datetime.fromisoformat(subscription["current_period_start"])
        current_period_end = datetime.fromisoformat(subscription["current_period_end"])
        created_at = datetime.fromisoformat(subscription["created_at"])
        updated_at = datetime.fromisoformat(subscription["updated_at"])
        canceled_at = None
        if subscription.get("canceled_at"):
            canceled_at = datetime.fromisoformat(subscription["canceled_at"])

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
            current_period_start=current_period_start,
            current_period_end=current_period_end,
            cancel_at_period_end=subscription["cancel_at_period_end"],
            canceled_at=canceled_at,
            analyses_used_this_period=subscription["analyses_used_this_period"],
            analyses_rollover=subscription["analyses_rollover"],
            analyses_available=max(0, analyses_available),
            tier_name=tier.name,
            analyses_per_month=tier.analyses_per_month,
            rollover_limit=tier.rollover_limit,
            created_at=created_at,
            updated_at=updated_at,
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
        # Import here to avoid circular imports
        from app.services.usage_limit_service import UsageLimitService
        from app.core.database import SupabaseSession
        from uuid import UUID

        usage_service = UsageLimitService(SupabaseSession())
        credits = await usage_service.get_user_credits(UUID(user_id))
        credit_balance = credits.get("credits_remaining", 0)

        return SubscriptionStatus(
            has_active_subscription=False,
            tier_id=None,
            analyses_remaining=credit_balance,
            can_use_service=credit_balance > 0,
        )


# Global service instance
subscription_service = SubscriptionService()