"""
Usage tracking service for freemium feature gating.

This service handles all operations related to tracking user usage of optimization features.
It manages monthly usage records, handles UPSERT operations, and provides usage statistics.
"""

import logging
from datetime import date, datetime
from uuid import UUID

from app.core.database import DatabaseOperations, SupabaseSession
from app.models.usage import (
    UsageTrackingCreate,
    UsageTrackingResponse,
)

logger = logging.getLogger(__name__)


class UsageTrackingError(Exception):
    """Base exception for usage tracking operations."""

    pass


class UsageTrackingNotFoundError(UsageTrackingError):
    """Raised when usage tracking record is not found."""

    pass


class UsageTrackingService:
    """
    Service for managing user usage tracking records.

    Handles monthly usage records with UPSERT operations to ensure
    proper tracking of free and paid optimization limits.
    """

    def __init__(self, db: SupabaseSession):
        self.db = db
        self.db_ops = DatabaseOperations(db)

    async def get_current_month_usage(self, user_id: UUID) -> UsageTrackingResponse | None:
        """
        Get usage tracking record for the current month.

        Args:
            user_id: The user ID to get usage for

        Returns:
            UsageTrackingResponse for current month or None if no record exists
        """
        try:
            current_month = date.today().replace(day=1)  # First day of current month

            # Query usage_tracking table for current month
            result = (
                self.db.client.table("usage_tracking")
                .select("*")
                .eq("user_id", str(user_id))
                .eq("month_date", current_month.isoformat())
                .execute()
            )

            if not result.data:
                return None

            record = result.data[0]
            return UsageTrackingResponse(
                id=UUID(record["id"]),
                user_id=UUID(record["user_id"]),
                month_date=datetime.fromisoformat(record["month_date"]).date(),
                free_optimizations_used=record["free_optimizations_used"],
                paid_optimizations_used=record["paid_optimizations_used"],
                created_at=datetime.fromisoformat(record["created_at"]),
                updated_at=datetime.fromisoformat(record["updated_at"]),
            )

        except Exception as e:
            logger.error(f"Failed to get current month usage for user {user_id}: {str(e)}")
            raise UsageTrackingError(f"Failed to retrieve usage tracking: {str(e)}")

    async def get_usage_for_month(self, user_id: UUID, month_date: date) -> UsageTrackingResponse | None:
        """
        Get usage tracking record for a specific month.

        Args:
            user_id: The user ID to get usage for
            month_date: The month date (first day of month)

        Returns:
            UsageTrackingResponse for specified month or None if no record exists
        """
        try:
            # Ensure month_date is first day of month
            month_first_day = month_date.replace(day=1)

            result = (
                self.db.client.table("usage_tracking")
                .select("*")
                .eq("user_id", str(user_id))
                .eq("month_date", month_first_day.isoformat())
                .execute()
            )

            if not result.data:
                return None

            record = result.data[0]
            return UsageTrackingResponse(
                id=UUID(record["id"]),
                user_id=UUID(record["user_id"]),
                month_date=datetime.fromisoformat(record["month_date"]).date(),
                free_optimizations_used=record["free_optimizations_used"],
                paid_optimizations_used=record["paid_optimizations_used"],
                created_at=datetime.fromisoformat(record["created_at"]),
                updated_at=datetime.fromisoformat(record["updated_at"]),
            )

        except Exception as e:
            logger.error(f"Failed to get usage for user {user_id}, month {month_date}: {str(e)}")
            raise UsageTrackingError(f"Failed to retrieve usage tracking: {str(e)}")

    async def create_or_update_usage(self, user_id: UUID, month_date: date | None = None) -> UsageTrackingResponse:
        """
        Create or update usage tracking record for a user (UPSERT operation).

        Args:
            user_id: The user ID to create/update usage for
            month_date: The month date (defaults to current month)

        Returns:
            UsageTrackingResponse with the created/updated record
        """
        try:
            if month_date is None:
                month_date = date.today().replace(day=1)  # First day of current month
            else:
                month_date = month_date.replace(day=1)  # Ensure first day of month

            # Check if record exists
            existing_usage = await self.get_usage_for_month(user_id, month_date)

            if existing_usage:
                # Record exists, return it
                logger.debug(f"Usage tracking record already exists for user {user_id}, month {month_date}")
                return existing_usage
            else:
                # Create new record
                usage_data = UsageTrackingCreate(
                    user_id=user_id, month_date=month_date, free_optimizations_used=0, paid_optimizations_used=0
                )

                result = (
                    self.db.client.table("usage_tracking")
                    .insert(
                        {
                            "user_id": str(usage_data.user_id),
                            "month_date": usage_data.month_date.isoformat(),
                            "free_optimizations_used": usage_data.free_optimizations_used,
                            "paid_optimizations_used": usage_data.paid_optimizations_used,
                        }
                    )
                    .execute()
                )

                if not result.data:
                    raise UsageTrackingError("Failed to create usage tracking record")

                record = result.data[0]
                logger.info(f"Created new usage tracking record for user {user_id}, month {month_date}")

                return UsageTrackingResponse(
                    id=UUID(record["id"]),
                    user_id=UUID(record["user_id"]),
                    month_date=datetime.fromisoformat(record["month_date"]).date(),
                    free_optimizations_used=record["free_optimizations_used"],
                    paid_optimizations_used=record["paid_optimizations_used"],
                    created_at=datetime.fromisoformat(record["created_at"]),
                    updated_at=datetime.fromisoformat(record["updated_at"]),
                )

        except Exception as e:
            logger.error(f"Failed to create/update usage tracking for user {user_id}: {str(e)}")
            raise UsageTrackingError(f"Failed to create/update usage tracking: {str(e)}")

    async def increment_usage(
        self, user_id: UUID, optimization_type: str = "free", month_date: date | None = None
    ) -> UsageTrackingResponse:
        """
        Increment usage count for a user.

        Args:
            user_id: The user ID to increment usage for
            optimization_type: Type of optimization ("free" or "paid")
            month_date: The month date (defaults to current month)

        Returns:
            UsageTrackingResponse with updated usage counts
        """
        try:
            if optimization_type not in ["free", "paid"]:
                raise ValueError("optimization_type must be 'free' or 'paid'")

            if month_date is None:
                month_date = date.today().replace(day=1)
            else:
                month_date = month_date.replace(day=1)

            # Ensure usage record exists
            usage_record = await self.create_or_update_usage(user_id, month_date)

            # Increment the appropriate counter
            if optimization_type == "free":
                new_free_count = usage_record.free_optimizations_used + 1
                update_data = {"free_optimizations_used": new_free_count}
            else:  # paid
                new_paid_count = usage_record.paid_optimizations_used + 1
                update_data = {"paid_optimizations_used": new_paid_count}

            # Update the record
            result = (
                self.db.client.table("usage_tracking")
                .update(update_data)
                .eq("user_id", str(user_id))
                .eq("month_date", month_date.isoformat())
                .execute()
            )

            if not result.data:
                raise UsageTrackingError("Failed to update usage tracking record")

            updated_record = result.data[0]
            logger.info(f"Incremented {optimization_type} usage for user {user_id}, month {month_date}")

            return UsageTrackingResponse(
                id=UUID(updated_record["id"]),
                user_id=UUID(updated_record["user_id"]),
                month_date=datetime.fromisoformat(updated_record["month_date"]).date(),
                free_optimizations_used=updated_record["free_optimizations_used"],
                paid_optimizations_used=updated_record["paid_optimizations_used"],
                created_at=datetime.fromisoformat(updated_record["created_at"]),
                updated_at=datetime.fromisoformat(updated_record["updated_at"]),
            )

        except Exception as e:
            logger.error(f"Failed to increment usage for user {user_id}: {str(e)}")
            raise UsageTrackingError(f"Failed to increment usage: {str(e)}")

    async def get_user_usage_history(self, user_id: UUID, months: int = 12) -> list[UsageTrackingResponse]:
        """
        Get usage history for a user for the past N months.

        Args:
            user_id: The user ID to get history for
            months: Number of months to retrieve (default: 12)

        Returns:
            List of UsageTrackingResponse objects ordered by month (newest first)
        """
        try:
            # Calculate date range
            end_date = date.today().replace(day=1)
            start_date = (
                end_date.replace(year=end_date.year - 1, month=end_date.month - months + 1)
                if end_date.month - months + 1 <= 0
                else end_date.replace(month=end_date.month - months + 1)
            )

            result = (
                self.db.client.table("usage_tracking")
                .select("*")
                .eq("user_id", str(user_id))
                .gte("month_date", start_date.isoformat())
                .lte("month_date", end_date.isoformat())
                .order("month_date", desc=True)
                .execute()
            )

            usage_history = []
            for record in result.data:
                usage_history.append(
                    UsageTrackingResponse(
                        id=UUID(record["id"]),
                        user_id=UUID(record["user_id"]),
                        month_date=datetime.fromisoformat(record["month_date"]).date(),
                        free_optimizations_used=record["free_optimizations_used"],
                        paid_optimizations_used=record["paid_optimizations_used"],
                        created_at=datetime.fromisoformat(record["created_at"]),
                        updated_at=datetime.fromisoformat(record["updated_at"]),
                    )
                )

            return usage_history

        except Exception as e:
            logger.error(f"Failed to get usage history for user {user_id}: {str(e)}")
            raise UsageTrackingError(f"Failed to retrieve usage history: {str(e)}")
