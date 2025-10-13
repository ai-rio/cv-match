"""
Unit tests for subscription service.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest

from app.models.subscription import SubscriptionCreate, SubscriptionUpdate
from app.services.subscription_service import subscription_service


@pytest.fixture
def mock_supabase():
    """Mock Supabase client."""
    with patch("app.services.subscription_service.get_supabase_client") as mock:
        client = Mock()
        # Mock the table chain to prevent actual HTTP calls
        table_mock = Mock()
        client.table.return_value = table_mock
        mock.return_value = client
        yield client


@pytest.fixture
def mock_pricing_config():
    """Mock pricing configuration."""
    with patch("app.services.subscription_service.pricing_config") as mock:
        tier = Mock()
        tier.name = "Flow Pro"
        tier.analyses_per_month = 60
        tier.rollover_limit = 30
        tier.is_subscription = True
        mock.get_tier.return_value = tier
        yield mock


@pytest.mark.asyncio
async def test_create_subscription_success(mock_supabase):
    """Test successful subscription creation."""
    # Arrange
    mock_supabase.table().insert().execute.return_value = Mock(
        data=[
            {
                "id": "sub_123",
                "user_id": "user_123",
                "tier_id": "flow_pro",
                "status": "active",
            }
        ]
    )

    # Mock get_subscription_details to avoid the actual call
    with patch.object(subscription_service, "get_subscription_details") as mock_get_details:
        mock_get_details.return_value = Mock(tier_id="flow_pro", analyses_available=60)

        subscription_data = SubscriptionCreate(
            user_id="user_123",
            tier_id="flow_pro",
            stripe_subscription_id="sub_stripe_123",
            stripe_customer_id="cus_123",
            stripe_price_id="price_123",
        )

        # Act
        result = await subscription_service.create_subscription(subscription_data)

        # Assert
        assert result is not None
        assert result.tier_id == "flow_pro"
        mock_supabase.table().insert.assert_called_once()


@pytest.mark.asyncio
async def test_create_subscription_duplicate_fails(mock_supabase):
    """Test that creating duplicate subscription fails."""
    # Arrange - user already has subscription
    mock_supabase.table().select().eq().eq().order().limit().execute.return_value = Mock(
        data=[{"id": "existing_sub", "tier_id": "flow_starter"}]
    )

    subscription_data = SubscriptionCreate(
        user_id="user_123",
        tier_id="flow_pro",
        stripe_subscription_id="sub_stripe_123",
        stripe_customer_id="cus_123",
        stripe_price_id="price_123",
    )

    # Act & Assert
    with pytest.raises(ValueError, match="already has active subscription"):
        await subscription_service.create_subscription(subscription_data)


@pytest.mark.asyncio
async def test_create_subscription_invalid_tier_fails(mock_supabase):
    """Test that creating subscription with invalid tier fails."""
    subscription_data = SubscriptionCreate(
        user_id="user_123",
        tier_id="invalid_tier",
        stripe_subscription_id="sub_stripe_123",
        stripe_customer_id="cus_123",
        stripe_price_id="price_123",
    )

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid subscription tier"):
        await subscription_service.create_subscription(subscription_data)


@pytest.mark.asyncio
async def test_get_subscription_details_success(mock_supabase, mock_pricing_config):
    """Test getting subscription details successfully."""
    # Arrange
    now = datetime.utcnow()
    subscription_data = {
        "id": "sub_123",
        "user_id": "user_123",
        "tier_id": "flow_pro",
        "status": "active",
        "stripe_subscription_id": "sub_stripe_123",
        "stripe_customer_id": "cus_123",
        "stripe_price_id": "price_123",
        "current_period_start": now.isoformat(),
        "current_period_end": (now + timedelta(days=30)).isoformat(),
        "cancel_at_period_end": False,
        "analyses_used_this_period": 10,
        "analyses_rollover": 5,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }

    mock_supabase.table().select().eq().single().execute.return_value = Mock(data=subscription_data)

    # Act
    result = await subscription_service.get_subscription_details("sub_123")

    # Assert
    assert result is not None
    assert result.id == "sub_123"
    assert result.tier_id == "flow_pro"
    assert result.analyses_available == 55  # 60 + 5 - 10
    assert result.tier_name == "Flow Pro"
    assert result.analyses_per_month == 60
    assert result.rollover_limit == 30


@pytest.mark.asyncio
async def test_get_subscription_details_not_found(mock_supabase):
    """Test getting subscription details when not found."""
    # Arrange
    mock_supabase.table().select().eq().single().execute.return_value = Mock(data=None)

    # Act & Assert
    with pytest.raises(ValueError, match="Subscription not found"):
        await subscription_service.get_subscription_details("nonexistent")


@pytest.mark.asyncio
async def test_use_analysis_success(mock_supabase, mock_pricing_config):
    """Test using an analysis from subscription."""
    # Arrange
    now = datetime.utcnow()
    mock_supabase.table().select().eq().single().execute.return_value = Mock(
        data={
            "id": "sub_123",
            "user_id": "user_123",
            "tier_id": "flow_pro",
            "analyses_used_this_period": 5,
            "analyses_rollover": 10,
            "current_period_start": now.isoformat(),
            "current_period_end": (now + timedelta(days=30)).isoformat(),
        }
    )

    mock_supabase.table().update().eq().execute.return_value = Mock(
        data=[{"analyses_used_this_period": 6}]
    )

    # Act
    result = await subscription_service.use_analysis("user_123", "sub_123")

    # Assert
    assert result.analyses_used_this_period == 6
    mock_supabase.table().update.assert_called_once()


@pytest.mark.asyncio
async def test_use_analysis_limit_reached(mock_supabase):
    """Test that usage fails when limit reached."""
    # Arrange - all analyses used
    now = datetime.utcnow()
    mock_supabase.table().select().eq().single().execute.return_value = Mock(
        data={
            "id": "sub_123",
            "user_id": "user_123",
            "tier_id": "flow_starter",
            "analyses_used_this_period": 15,  # Limit is 15
            "analyses_rollover": 0,
            "current_period_start": now.isoformat(),
            "current_period_end": (now + timedelta(days=30)).isoformat(),
        }
    )

    # Mock pricing config
    with patch("app.services.subscription_service.pricing_config") as mock_pricing:
        mock_tier = Mock()
        mock_tier.name = "Flow Starter"
        mock_tier.analyses_per_month = 15
        mock_tier.rollover_limit = 5
        mock_pricing.get_tier.return_value = mock_tier

        # Act & Assert
        with pytest.raises(ValueError, match="No analyses available"):
            await subscription_service.use_analysis("user_123", "sub_123")


@pytest.mark.asyncio
async def test_get_active_subscription(mock_supabase):
    """Test getting active subscription for user."""
    # Arrange
    mock_supabase.table().select().eq().eq().order().limit().execute.return_value = Mock(
        data=[{"id": "sub_123", "user_id": "user_123", "tier_id": "flow_pro", "status": "active"}]
    )

    # Act
    result = await subscription_service.get_active_subscription("user_123")

    # Assert
    assert result is not None
    assert result["tier_id"] == "flow_pro"
    assert result["status"] == "active"


@pytest.mark.asyncio
async def test_get_active_subscription_none(mock_supabase):
    """Test getting active subscription when none exists."""
    # Arrange
    mock_supabase.table().select().eq().eq().order().limit().execute.return_value = Mock(data=[])

    # Act
    result = await subscription_service.get_active_subscription("user_123")

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_update_subscription(mock_supabase):
    """Test updating subscription."""
    # Arrange
    mock_supabase.table().update().eq().execute.return_value = Mock(
        data=[{"id": "sub_123", "tier_id": "flow_business"}]
    )

    with patch.object(subscription_service, "get_subscription_details") as mock_get_details:
        mock_get_details.return_value = Mock(tier_id="flow_business")

        update_data = SubscriptionUpdate(tier_id="flow_business")

        # Act
        result = await subscription_service.update_subscription("sub_123", update_data)

        # Assert
        assert result is not None
        assert result.tier_id == "flow_business"
        mock_supabase.table().update.assert_called_once()


@pytest.mark.asyncio
async def test_cancel_subscription_immediate(mock_supabase):
    """Test canceling subscription immediately."""
    # Arrange
    mock_supabase.table().update().eq().execute.return_value = Mock(
        data=[{"id": "sub_123", "status": "canceled"}]
    )

    with patch.object(subscription_service, "get_subscription_details") as mock_get_details:
        mock_get_details.return_value = Mock(status="canceled")

        # Act
        result = await subscription_service.cancel_subscription("sub_123", immediate=True)

        # Assert
        assert result is not None
        assert result.status == "canceled"
        mock_supabase.table().update.assert_called_once()

        # Verify update_data contains correct cancellation fields
        call_args = mock_supabase.table().update.call_args[0][0]
        assert call_args["status"] == "canceled"
        assert call_args["cancel_at_period_end"] is False
        assert call_args["canceled_at"] is not None


@pytest.mark.asyncio
async def test_cancel_subscription_at_period_end(mock_supabase):
    """Test canceling subscription at period end."""
    # Arrange
    mock_supabase.table().update().eq().execute.return_value = Mock(
        data=[{"id": "sub_123", "status": "active"}]
    )

    with patch.object(subscription_service, "get_subscription_details") as mock_get_details:
        mock_get_details.return_value = Mock(status="active")

        # Act
        result = await subscription_service.cancel_subscription("sub_123", immediate=False)

        # Assert
        assert result is not None
        assert result.status == "active"
        mock_supabase.table().update.assert_called_once()

        # Verify update_data contains correct cancellation fields
        call_args = mock_supabase.table().update.call_args[0][0]
        assert call_args["status"] == "active"
        assert call_args["cancel_at_period_end"] is True
        assert call_args["canceled_at"] is None


@pytest.mark.asyncio
async def test_process_period_renewal_with_rollover(mock_supabase, mock_pricing_config):
    """Test processing subscription period renewal with rollover."""
    # Arrange
    now = datetime.utcnow()
    period_start = now
    period_end = now + timedelta(days=30)

    subscription_details = Mock(
        id="sub_123",
        tier_id="flow_pro",
        analyses_used_this_period=40,  # Used 40 out of 60
        analyses_rollover=10,  # Has 10 rollover
        current_period_start=period_start,
        current_period_end=period_end,
    )

    mock_supabase.table().update().eq().execute.return_value = Mock(data=[{"id": "sub_123"}])

    with patch.object(subscription_service, "get_subscription_details") as mock_get_details:
        mock_get_details.return_value = subscription_details

        # Act
        result = await subscription_service.process_period_renewal("sub_123")

        # Assert
        assert result is not None
        mock_supabase.table().update.assert_called_once()

        # Verify rollover calculation: (60 + 10 - 40) = 30, capped at 30 limit
        call_args = mock_supabase.table().update.call_args[0][0]
        assert call_args["analyses_rollover"] == 30
        assert call_args["analyses_used_this_period"] == 0


@pytest.mark.asyncio
async def test_process_period_renewal_exceeds_limit(mock_supabase, mock_pricing_config):
    """Test period renewal when unused analyses exceed rollover limit."""
    # Arrange
    now = datetime.utcnow()
    period_start = now
    period_end = now + timedelta(days=30)

    subscription_details = Mock(
        id="sub_123",
        tier_id="flow_pro",
        analyses_used_this_period=10,  # Used only 10 out of 60
        analyses_rollover=20,  # Has 20 rollover
        current_period_start=period_start,
        current_period_end=period_end,
    )

    mock_supabase.table().update().eq().execute.return_value = Mock(data=[{"id": "sub_123"}])

    with patch.object(subscription_service, "get_subscription_details") as mock_get_details:
        mock_get_details.return_value = subscription_details

        # Act
        result = await subscription_service.process_period_renewal("sub_123")

        # Assert
        assert result is not None

        # Verify rollover calculation: (60 + 20 - 10) = 70, capped at 30 limit
        call_args = mock_supabase.table().update.call_args[0][0]
        assert call_args["analyses_rollover"] == 30  # Capped at limit


@pytest.mark.asyncio
async def test_get_subscription_status_with_active_subscription(mock_supabase, mock_pricing_config):
    """Test getting subscription status when user has active subscription."""
    # Arrange
    now = datetime.utcnow()
    mock_supabase.table().select().eq().eq().order().limit().execute.return_value = Mock(
        data=[{"id": "sub_123", "user_id": "user_123", "tier_id": "flow_pro", "status": "active"}]
    )

    with patch.object(subscription_service, "get_subscription_details") as mock_get_details:
        mock_get_details.return_value = Mock(tier_id="flow_pro", analyses_available=25)

        # Act
        result = await subscription_service.get_subscription_status("user_123")

        # Assert
        assert result is not None
        assert result.has_active_subscription is True
        assert result.tier_id == "flow_pro"
        assert result.analyses_remaining == 25
        assert result.can_use_service is True


@pytest.mark.asyncio
async def test_get_subscription_status_with_credits_only(mock_supabase):
    """Test getting subscription status when user only has credits."""
    # Arrange
    mock_supabase.table().select().eq().eq().order().limit().execute.return_value = Mock(
        data=[]  # No active subscription
    )

    # Mock usage limit service for credits
    with patch("app.services.usage_limit_service.UsageLimitService") as mock_usage_service:
        mock_service_instance = Mock()
        mock_service_instance.get_user_credits.return_value = {"credits_remaining": 15}
        mock_usage_service.return_value = mock_service_instance

        # Act
        result = await subscription_service.get_subscription_status("user_123")

        # Assert
        assert result is not None
        assert result.has_active_subscription is False
        assert result.tier_id is None
        assert result.analyses_remaining == 15
        assert result.can_use_service is True


@pytest.mark.asyncio
async def test_get_subscription_status_no_subscription_no_credits(mock_supabase):
    """Test getting subscription status when user has neither subscription nor credits."""
    # Arrange
    mock_supabase.table().select().eq().eq().order().limit().execute.return_value = Mock(
        data=[]  # No active subscription
    )

    # Mock usage limit service for credits
    with patch("app.services.usage_limit_service.UsageLimitService") as mock_usage_service:
        mock_service_instance = Mock()
        mock_service_instance.get_user_credits.return_value = {"credits_remaining": 0}
        mock_usage_service.return_value = mock_service_instance

        # Act
        result = await subscription_service.get_subscription_status("user_123")

        # Assert
        assert result is not None
        assert result.has_active_subscription is False
        assert result.tier_id is None
        assert result.analyses_remaining == 0
        assert result.can_use_service is False


@pytest.mark.asyncio
async def test_use_analysis_with_rollover_priority(mock_supabase, mock_pricing_config):
    """Test that analysis usage correctly calculates availability with rollover."""
    # Arrange
    now = datetime.utcnow()
    mock_supabase.table().select().eq().single().execute.return_value = Mock(
        data={
            "id": "sub_123",
            "user_id": "user_123",
            "tier_id": "flow_pro",
            "analyses_used_this_period": 58,  # Used 58 out of 60 this month
            "analyses_rollover": 5,  # Has 5 rollover
            "current_period_start": now.isoformat(),
            "current_period_end": (now + timedelta(days=30)).isoformat(),
        }
    )

    mock_supabase.table().update().eq().execute.return_value = Mock(
        data=[{"analyses_used_this_period": 59}]
    )

    # Act - Should still have 7 analyses available (60 + 5 - 58)
    result = await subscription_service.use_analysis("user_123", "sub_123")

    # Assert
    assert result.analyses_used_this_period == 59
    mock_supabase.table().update.assert_called_once()


@pytest.mark.asyncio
async def test_use_analysis_exactly_at_limit(mock_supabase):
    """Test using analysis when exactly at limit (no availability)."""
    # Arrange
    now = datetime.utcnow()
    mock_supabase.table().select().eq().single().execute.return_value = Mock(
        data={
            "id": "sub_123",
            "user_id": "user_123",
            "tier_id": "flow_pro",
            "analyses_used_this_period": 60,  # Used all 60
            "analyses_rollover": 0,  # No rollover
            "current_period_start": now.isoformat(),
            "current_period_end": (now + timedelta(days=30)).isoformat(),
        }
    )

    # Mock pricing config
    with patch("app.services.subscription_service.pricing_config") as mock_pricing:
        mock_tier = Mock()
        mock_tier.name = "Flow Pro"
        mock_tier.analyses_per_month = 60
        mock_tier.rollover_limit = 30
        mock_pricing.get_tier.return_value = mock_tier

        # Act & Assert
        with pytest.raises(ValueError, match="No analyses available"):
            await subscription_service.use_analysis("user_123", "sub_123")


@pytest.mark.asyncio
async def test_create_subscription_db_failure(mock_supabase):
    """Test subscription creation when database insert fails."""
    # Arrange
    mock_supabase.table().insert().execute.return_value = Mock(
        data=[]  # Empty data indicates failure
    )

    subscription_data = SubscriptionCreate(
        user_id="user_123",
        tier_id="flow_pro",
        stripe_subscription_id="sub_stripe_123",
        stripe_customer_id="cus_123",
        stripe_price_id="price_123",
    )

    # Act & Assert
    with pytest.raises(ValueError, match="Failed to create subscription"):
        await subscription_service.create_subscription(subscription_data)


@pytest.mark.asyncio
async def test_update_subscription_not_found(mock_supabase):
    """Test updating subscription when subscription not found."""
    # Arrange
    mock_supabase.table().update().eq().execute.return_value = Mock(
        data=[]  # Empty data indicates not found
    )

    update_data = SubscriptionUpdate(tier_id="flow_business")

    # Act & Assert
    with pytest.raises(ValueError, match="Failed to update subscription"):
        await subscription_service.update_subscription("nonexistent", update_data)


@pytest.mark.asyncio
async def test_cancel_subscription_not_found(mock_supabase):
    """Test canceling subscription when subscription not found."""
    # Arrange
    mock_supabase.table().update().eq().execute.return_value = Mock(
        data=[]  # Empty data indicates not found
    )

    # Act & Assert
    with pytest.raises(ValueError, match="Failed to cancel subscription"):
        await subscription_service.cancel_subscription("nonexistent", immediate=True)


@pytest.mark.asyncio
async def test_process_period_renewal_not_found(mock_supabase):
    """Test period renewal when subscription not found."""
    # Arrange
    with patch.object(subscription_service, "get_subscription_details") as mock_get_details:
        mock_get_details.side_effect = ValueError("Subscription not found")

        # Act & Assert
        with pytest.raises(ValueError, match="Subscription not found"):
            await subscription_service.process_period_renewal("nonexistent")
