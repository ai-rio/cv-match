"""
Unit tests for usage limit service functionality.
Tests credit management and usage tracking for the CV-Match SaaS.
"""

import asyncio
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest

from app.services.usage_limit_service import (
    CREDIT_TIERS,
    UsageLimitError,
    UsageLimitExceededError,
    UsageLimitService,
    UserNotFoundError,
)


@pytest.mark.unit
@pytest.mark.usage
class TestUsageLimitService:
    """Test usage limit service functionality."""

    def setup_method(self):
        """Set up test method."""
        self.test_user_id = uuid4()
        self.mock_db = MagicMock()

    def create_mock_service(self):
        """Create a mock usage limit service."""
        service = UsageLimitService(self.mock_db)
        service.usage_tracking_service = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_get_user_credits_existing_user(self):
        """Test getting credits for existing user."""
        service = self.create_mock_service()

        # Mock existing user credits
        mock_credits = {
            "id": "credit_123",
            "user_id": str(self.test_user_id),
            "credits_remaining": 25,
            "total_credits": 50,
            "subscription_tier": "pro",
            "is_pro": True
        }

        self.mock_db.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_credits]

        result = await service.get_user_credits(self.test_user_id)

        assert result == mock_credits
        self.mock_db.client.table.return_value.select.return_value.eq.assert_called_once_with(str(self.test_user_id))

    @pytest.mark.asyncio
    async def test_get_user_credits_new_user_creates_record(self):
        """Test getting credits for new user creates initial record."""
        service = self.create_mock_service()

        # Mock empty response (no existing credits)
        self.mock_db.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

        # Mock successful creation
        mock_created_credits = {
            "id": "credit_new_123",
            "user_id": str(self.test_user_id),
            "credits_remaining": CREDIT_TIERS["free"],
            "total_credits": CREDIT_TIERS["free"],
            "subscription_tier": "free",
            "is_pro": False
        }

        self.mock_db.client.table.return_value.insert.return_value.execute.return_value.data = [mock_created_credits]

        result = await service.get_user_credits(self.test_user_id)

        assert result == mock_created_credits
        self.mock_db.client.table.return_value.insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_credits_creation_failure(self):
        """Test getting credits when record creation fails."""
        service = self.create_mock_service()

        # Mock empty response and failed creation
        self.mock_db.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        self.mock_db.client.table.return_value.insert.return_value.execute.return_value.data = []

        with pytest.raises(UserNotFoundError, match="Failed to create credits record"):
            await service.get_user_credits(self.test_user_id)

    @pytest.mark.asyncio
    async def test_get_user_credits_database_error(self):
        """Test getting credits with database error."""
        service = self.create_mock_service()

        # Mock database error
        self.mock_db.client.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception("Database error")

        with pytest.raises(UsageLimitError, match="Failed to retrieve user credits"):
            await service.get_user_credits(self.test_user_id)

    @pytest.mark.asyncio
    async def test_check_usage_limit_pro_user_unlimited(self):
        """Test usage limit check for Pro user (unlimited)."""
        service = self.create_mock_service()

        # Mock Pro user credits
        mock_credits = {
            "id": "credit_pro_123",
            "user_id": str(self.test_user_id),
            "credits_remaining": 100,
            "total_credits": 100,
            "subscription_tier": "pro",
            "is_pro": True
        }

        self.mock_db.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_credits]

        # Mock usage tracking
        mock_usage = AsyncMock()
        mock_usage.free_optimizations_used = 5
        mock_usage.paid_optimizations_used = 20
        service.usage_tracking_service.get_current_month_usage.return_value = mock_usage

        result = await service.check_usage_limit(self.test_user_id)

        assert result.can_optimize is True
        assert result.is_pro is True
        assert result.free_optimizations_used == 25  # 5 + 20
        assert result.reason is None
        assert result.upgrade_prompt is None

    @pytest.mark.asyncio
    async def test_check_usage_limit_free_user_sufficient_credits(self):
        """Test usage limit check for free user with sufficient credits."""
        service = self.create_mock_service()

        # Mock free user credits
        mock_credits = {
            "id": "credit_free_123",
            "user_id": str(self.test_user_id),
            "credits_remaining": 5,
            "total_credits": 10,
            "subscription_tier": "free",
            "is_pro": False
        }

        self.mock_db.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_credits]

        # Mock usage tracking
        mock_usage = AsyncMock()
        mock_usage.free_optimizations_used = 2
        mock_usage.paid_optimizations_used = 0
        service.usage_tracking_service.get_current_month_usage.return_value = mock_usage

        result = await service.check_usage_limit(self.test_user_id)

        assert result.can_optimize is True
        assert result.is_pro is False
        assert result.free_optimizations_used == 2
        assert result.remaining_free_optimizations == 5
        assert result.reason is None
        assert result.upgrade_prompt is None

    @pytest.mark.asyncio
    async def test_check_usage_limit_free_user_insufficient_credits(self):
        """Test usage limit check for free user with insufficient credits."""
        service = self.create_mock_service()

        # Mock free user with no credits
        mock_credits = {
            "id": "credit_no_credits_123",
            "user_id": str(self.test_user_id),
            "credits_remaining": 0,
            "total_credits": 3,
            "subscription_tier": "free",
            "is_pro": False
        }

        self.mock_db.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_credits]

        # Mock usage tracking
        mock_usage = AsyncMock()
        mock_usage.free_optimizations_used = 3
        mock_usage.paid_optimizations_used = 0
        service.usage_tracking_service.get_current_month_usage.return_value = mock_usage

        result = await service.check_usage_limit(self.test_user_id)

        assert result.can_optimize is False
        assert result.is_pro is False
        assert result.free_optimizations_used == 3
        assert result.remaining_free_optimizations == 0
        assert "Insufficient credits" in result.reason
        assert "Upgrade to Pro" in result.upgrade_prompt

    @pytest.mark.asyncio
    async def test_check_usage_limit_no_usage_record_creates_one(self):
        """Test usage limit check creates usage record if none exists."""
        service = self.create_mock_service()

        # Mock user credits
        mock_credits = {
            "id": "credit_123",
            "user_id": str(self.test_user_id),
            "credits_remaining": 5,
            "total_credits": 5,
            "subscription_tier": "free",
            "is_pro": False
        }

        self.mock_db.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_credits]

        # Mock no usage record initially, then create one
        service.usage_tracking_service.get_current_month_usage.return_value = None
        mock_new_usage = AsyncMock()
        mock_new_usage.free_optimizations_used = 0
        mock_new_usage.paid_optimizations_used = 0
        service.usage_tracking_service.create_or_update_usage.return_value = mock_new_usage

        result = await service.check_usage_limit(self.test_user_id)

        assert result.can_optimize is True
        assert result.free_optimizations_used == 0
        service.usage_tracking_service.create_or_update_usage.assert_called_once_with(self.test_user_id)

    @pytest.mark.asyncio
    async def test_check_usage_limit_user_not_found(self):
        """Test usage limit check when user credits record doesn't exist."""
        service = self.create_mock_service()

        # Mock user not found
        self.mock_db.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        self.mock_db.client.table.return_value.insert.return_value.execute.return_value.data = []

        with pytest.raises(UserNotFoundError):
            await service.check_usage_limit(self.test_user_id)

    @pytest.mark.asyncio
    async def test_check_usage_limit_tracking_error(self):
        """Test usage limit check with usage tracking error."""
        service = self.create_mock_service()

        # Mock user credits
        mock_credits = {
            "id": "credit_123",
            "user_id": str(self.test_user_id),
            "credits_remaining": 5,
            "total_credits": 5,
            "subscription_tier": "free",
            "is_pro": False
        }

        self.mock_db.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_credits]

        # Mock usage tracking error
        from app.services.usage_tracking_service import UsageTrackingError
        service.usage_tracking_service.get_current_month_usage.side_effect = UsageTrackingError("Tracking error")

        with pytest.raises(UsageLimitError, match="Failed to check usage limits"):
            await service.check_usage_limit(self.test_user_id)

    @pytest.mark.asyncio
    async def test_get_usage_stats_success(self):
        """Test getting comprehensive usage statistics."""
        service = self.create_mock_service()

        # Mock user credits
        mock_credits = {
            "id": "credit_123",
            "user_id": str(self.test_user_id),
            "credits_remaining": 3,
            "total_credits": 5,
            "subscription_tier": "free",
            "is_pro": False
        }

        self.mock_db.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_credits]

        # Mock current usage
        mock_usage = AsyncMock()
        mock_usage.free_optimizations_used = 2
        mock_usage.paid_optimizations_used = 0
        mock_usage.month_date = datetime.now(UTC).date()
        service.usage_tracking_service.get_current_month_usage.return_value = mock_usage

        result = await service.get_usage_stats(self.test_user_id)

        assert result.user_id == self.test_user_id
        assert result.free_optimizations_used == 2
        assert result.paid_optimizations_used == 0
        assert result.free_optimizations_limit == 1  # Free users get 1 optimization per month
        assert result.is_pro is False
        assert result.can_optimize is True  # 2 < 1 is False, but this should be based on credits
        assert result.remaining_free_optimizations == 0  # max(0, 1-2)
        assert result.total_optimizations_this_month == 2

    @pytest.mark.asyncio
    async def test_get_usage_stats_no_usage_record(self):
        """Test getting usage stats when no usage record exists."""
        service = self.create_mock_service()

        # Mock user credits
        mock_credits = {
            "id": "credit_123",
            "user_id": str(self.test_user_id),
            "credits_remaining": 5,
            "total_credits": 5,
            "subscription_tier": "free",
            "is_pro": False
        }

        self.mock_db.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_credits]

        # Mock no usage record, create new one
        service.usage_tracking_service.get_current_month_usage.return_value = None
        mock_new_usage = AsyncMock()
        mock_new_usage.free_optimizations_used = 0
        mock_new_usage.paid_optimizations_used = 0
        mock_new_usage.month_date = datetime.now(UTC).date()
        service.usage_tracking_service.create_or_update_usage.return_value = mock_new_usage

        result = await service.get_usage_stats(self.test_user_id)

        assert result.free_optimizations_used == 0
        assert result.paid_optimizations_used == 0
        assert result.can_optimize is True
        service.usage_tracking_service.create_or_update_usage.assert_called_once_with(self.test_user_id)

    @pytest.mark.asyncio
    async def test_get_usage_stats_pro_user(self):
        """Test getting usage stats for Pro user."""
        service = self.create_mock_service()

        # Mock Pro user credits
        mock_credits = {
            "id": "credit_pro_123",
            "user_id": str(self.test_user_id),
            "credits_remaining": 100,
            "total_credits": 100,
            "subscription_tier": "pro",
            "is_pro": True
        }

        self.mock_db.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_credits]

        # Mock current usage
        mock_usage = AsyncMock()
        mock_usage.free_optimizations_used = 50
        mock_usage.paid_optimizations_used = 100
        mock_usage.month_date = datetime.now(UTC).date()
        service.usage_tracking_service.get_current_month_usage.return_value = mock_usage

        result = await service.get_usage_stats(self.test_user_id)

        assert result.is_pro is True
        assert result.can_optimize is True  # Pro users can always optimize
        assert result.total_optimizations_this_month == 150

    @pytest.mark.asyncio
    async def test_deduct_credits_atomic_success(self):
        """Test successful atomic credit deduction."""
        service = self.create_mock_service()

        # Mock successful atomic deduction
        mock_result = MagicMock()
        mock_result.data = [{"success": True, "new_balance": 45}]
        self.mock_db.client.rpc.return_value.execute.return_value = mock_result

        # Mock transaction creation
        self.mock_db.client.table.return_value.insert.return_value.execute.return_value.data = [{"id": "transaction_123"}]

        result = await service.deduct_credits(self.test_user_id, 5, "operation_123")

        assert result is True
        self.mock_db.client.rpc.assert_called_once_with("deduct_credits_atomically", {
            "p_user_id": str(self.test_user_id),
            "p_amount": 5
        })

    @pytest.mark.asyncio
    async def test_deduct_credits_atomic_insufficient_credits(self):
        """Test atomic credit deduction with insufficient credits."""
        service = self.create_mock_service()

        # Mock insufficient credits response
        mock_result = MagicMock()
        mock_result.data = [{"success": False, "reason": "insufficient_credits"}]
        self.mock_db.client.rpc.return_value.execute.return_value = mock_result

        result = await service.deduct_credits(self.test_user_id, 10, "operation_123")

        assert result is False

    @pytest.mark.asyncio
    async def test_deduct_credits_atomic_fallback_success(self):
        """Test credit deduction fallback to standard method."""
        service = self.create_mock_service()

        # Mock RPC function not available
        self.mock_db.client.rpc.return_value.execute.side_effect = Exception("RPC not available")

        # Mock fallback operations
        mock_credits = {
            "id": "credit_123",
            "user_id": str(self.test_user_id),
            "credits_remaining": 10,
            "total_credits": 10,
            "subscription_tier": "free",
            "is_pro": False
        }

        self.mock_db.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_credits]
        self.mock_db.client.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value.data = [mock_credits]
        self.mock_db.client.table.return_value.insert.return_value.execute.return_value.data = [{"id": "transaction_123"}]

        result = await service.deduct_credits(self.test_user_id, 5, "operation_123")

        assert result is True

    @pytest.mark.asyncio
    async def test_deduct_credits_race_condition_retry(self):
        """Test credit deduction handles race conditions with retry."""
        service = self.create_mock_service()

        # Mock initial credits
        mock_credits = {
            "id": "credit_123",
            "user_id": str(self.test_user_id),
            "credits_remaining": 10,
            "total_credits": 10,
            "subscription_tier": "free",
            "is_pro": False
        }

        self.mock_db.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_credits]

        # Mock race condition - first update fails (no rows), second succeeds via retry
        update_response = MagicMock()
        update_response.data = []  # No rows updated on first attempt
        self.mock_db.client.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.side_effect = [
            update_response,  # First call fails
            update_response   # Second call will be mocked in retry
        ]

        # Mock successful retry
        with patch.object(service, 'deduct_credits', return_value=True) as mock_retry:
            result = await service.deduct_credits_fallback(self.test_user_id, 5, "operation_123")

        assert result is True

    @pytest.mark.asyncio
    async def test_deduct_credits_fallback_insufficient_credits(self):
        """Test credit deduction fallback with insufficient credits."""
        service = self.create_mock_service()

        # Mock insufficient credits
        mock_credits = {
            "id": "credit_123",
            "user_id": str(self.test_user_id),
            "credits_remaining": 2,
            "total_credits": 5,
            "subscription_tier": "free",
            "is_pro": False
        }

        self.mock_db.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_credits]

        result = await service.deduct_credits_fallback(self.test_user_id, 5, "operation_123")

        assert result is False

    @pytest.mark.asyncio
    async def test_add_credits_success(self):
        """Test successful credit addition."""
        service = self.create_mock_service()

        # Mock existing credits
        mock_credits = {
            "id": "credit_123",
            "user_id": str(self.test_user_id),
            "credits_remaining": 10,
            "total_credits": 10,
            "subscription_tier": "free",
            "is_pro": False
        }

        self.mock_db.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_credits]

        # Mock successful update
        updated_credits = mock_credits.copy()
        updated_credits["credits_remaining"] = 20
        updated_credits["total_credits"] = 20
        self.mock_db.client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [updated_credits]

        # Mock transaction creation
        self.mock_db.client.table.return_value.insert.return_value.execute.return_value.data = [{"id": "transaction_123"}]

        result = await service.add_credits(self.test_user_id, 10, "payment", "Test payment")

        assert result is True
        self.mock_db.client.table.return_value.update.assert_called_once()
        self.mock_db.client.table.return_value.insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_credits_failure(self):
        """Test credit addition failure."""
        service = self.create_mock_service()

        # Mock existing credits
        mock_credits = {
            "id": "credit_123",
            "user_id": str(self.test_user_id),
            "credits_remaining": 10,
            "total_credits": 10,
            "subscription_tier": "free",
            "is_pro": False
        }

        self.mock_db.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_credits]

        # Mock failed update
        self.mock_db.client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = []

        with pytest.raises(UsageLimitError, match="Failed to update user credits"):
            await service.add_credits(self.test_user_id, 10, "payment")

    @pytest.mark.asyncio
    async def test_check_and_track_usage_pro_user(self):
        """Test check and track usage for Pro user (no credit deduction)."""
        service = self.create_mock_service()

        # Mock Pro user
        mock_credits = {
            "id": "credit_pro_123",
            "user_id": str(self.test_user_id),
            "credits_remaining": 100,
            "total_credits": 100,
            "subscription_tier": "pro",
            "is_pro": True
        }

        self.mock_db.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_credits]

        # Mock usage tracking
        mock_usage = AsyncMock()
        mock_usage.free_optimizations_used = 5
        mock_usage.paid_optimizations_used = 20
        mock_usage.remaining_free_optimizations = 50
        service.usage_tracking_service.get_current_month_usage.return_value = mock_usage

        result = await service.check_and_track_usage(self.test_user_id, "paid", 0)

        assert result.can_optimize is True
        assert result.is_pro is True
        service.usage_tracking_service.increment_usage.assert_called_once_with(
            user_id=self.test_user_id,
            optimization_type="paid"
        )

    @pytest.mark.asyncio
    async def test_check_and_track_usage_free_user_with_credits(self):
        """Test check and track usage for free user with sufficient credits."""
        service = self.create_mock_service()

        # Mock free user with credits
        mock_credits = {
            "id": "credit_free_123",
            "user_id": str(self.test_user_id),
            "credits_remaining": 5,
            "total_credits": 10,
            "subscription_tier": "free",
            "is_pro": False
        }

        self.mock_db.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_credits]

        # Mock usage tracking
        mock_usage = AsyncMock()
        mock_usage.free_optimizations_used = 2
        mock_usage.paid_optimizations_used = 0
        mock_usage.remaining_free_optimizations = 3
        service.usage_tracking_service.get_current_month_usage.return_value = mock_usage

        # Mock successful credit deduction
        with patch.object(service, 'deduct_credits', return_value=True):
            result = await service.check_and_track_usage(self.test_user_id, "free", 1)

        assert result.can_optimize is True
        assert result.is_pro is False
        service.usage_tracking_service.increment_usage.assert_called_once_with(
            user_id=self.test_user_id,
            optimization_type="free"
        )

    @pytest.mark.asyncio
    async def test_check_and_track_usage_insufficient_credits(self):
        """Test check and track usage with insufficient credits."""
        service = self.create_mock_service()

        # Mock free user with no credits
        mock_credits = {
            "id": "credit_no_credits_123",
            "user_id": str(self.test_user_id),
            "credits_remaining": 0,
            "total_credits": 3,
            "subscription_tier": "free",
            "is_pro": False
        }

        self.mock_db.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_credits]

        # Mock usage tracking
        mock_usage = AsyncMock()
        mock_usage.free_optimizations_used = 3
        mock_usage.paid_optimizations_used = 0
        mock_usage.remaining_free_optimizations = 0
        service.usage_tracking_service.get_current_month_usage.return_value = mock_usage

        with pytest.raises(UsageLimitExceededError, match="Insufficient credits"):
            await service.check_and_track_usage(self.test_user_id, "free", 1)

    @pytest.mark.asyncio
    async def test_check_and_track_usage_credit_deduction_failure(self):
        """Test check and track usage when credit deduction fails."""
        service = self.create_mock_service()

        # Mock free user with some credits
        mock_credits = {
            "id": "credit_some_123",
            "user_id": str(self.test_user_id),
            "credits_remaining": 2,
            "total_credits": 5,
            "subscription_tier": "free",
            "is_pro": False
        }

        self.mock_db.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_credits]

        # Mock usage tracking
        mock_usage = AsyncMock()
        mock_usage.free_optimizations_used = 1
        mock_usage.paid_optimizations_used = 0
        mock_usage.remaining_free_optimizations = 2
        service.usage_tracking_service.get_current_month_usage.return_value = mock_usage

        # Mock failed credit deduction
        with patch.object(service, 'deduct_credits', return_value=False):
            with pytest.raises(UsageLimitExceededError, match="Failed to deduct credits"):
                await service.check_and_track_usage(self.test_user_id, "free", 1)

    @pytest.mark.asyncio
    async def test_reset_monthly_usage_if_needed_existing_record(self):
        """Test monthly usage reset when record already exists."""
        service = self.create_mock_service()

        # Mock existing usage record
        mock_usage = AsyncMock()
        service.usage_tracking_service.get_current_month_usage.return_value = mock_usage

        result = await service.reset_monthly_usage_if_needed(self.test_user_id)

        assert result is False
        service.usage_tracking_service.create_or_update_usage.assert_not_called()

    @pytest.mark.asyncio
    async def test_reset_monthly_usage_if_needed_no_record(self):
        """Test monthly usage reset when no record exists."""
        service = self.create_mock_service()

        # Mock no existing record
        service.usage_tracking_service.get_current_month_usage.return_value = None
        service.usage_tracking_service.create_or_update_usage.return_value = AsyncMock()

        result = await service.reset_monthly_usage_if_needed(self.test_user_id)

        assert result is True
        service.usage_tracking_service.create_or_update_usage.assert_called_once_with(self.test_user_id)

    @pytest.mark.asyncio
    async def test_reset_monthly_usage_tracking_error(self):
        """Test monthly usage reset with tracking error."""
        service = self.create_mock_service()

        # Mock tracking error
        from app.services.usage_tracking_service import UsageTrackingError
        service.usage_tracking_service.get_current_month_usage.side_effect = UsageTrackingError("Tracking error")

        with pytest.raises(UsageLimitError, match="Failed to reset monthly usage"):
            await service.reset_monthly_usage_if_needed(self.test_user_id)

    def test_credit_tiers_constants(self):
        """Test credit tiers are properly defined."""
        assert "free" in CREDIT_TIERS
        assert "basic" in CREDIT_TIERS
        assert "pro" in CREDIT_TIERS
        assert "enterprise" in CREDIT_TIERS

        assert CREDIT_TIERS["free"] == 3
        assert CREDIT_TIERS["basic"] == 10
        assert CREDIT_TIERS["pro"] == 50
        assert CREDIT_TIERS["enterprise"] == 1000

        # Verify progression
        assert CREDIT_TIERS["free"] < CREDIT_TIERS["basic"] < CREDIT_TIERS["pro"] < CREDIT_TIERS["enterprise"]