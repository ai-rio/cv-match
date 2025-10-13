"""
Tests for subscription webhook event handlers.
Tests all subscription-specific webhook events with comprehensive scenarios.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest

from app.services.webhook_service import WebhookService


@pytest.fixture
def mock_webhook_service():
    """Mock webhook service with database dependencies."""
    with (
        patch("app.services.webhook_service.create_client") as mock_create_client,
        patch("app.services.webhook_service.UsageLimitService") as mock_usage_service,
        patch("app.services.webhook_service.SupabaseSession") as mock_session,
    ):
        # Mock Supabase client
        mock_client = Mock()
        mock_create_client.return_value = mock_client

        # Mock usage service
        mock_usage_instance = Mock()
        mock_usage_service.return_value = mock_usage_instance

        webhook_service = WebhookService()
        webhook_service.supabase = mock_client
        webhook_service.usage_limit_service = mock_usage_instance

        yield webhook_service, mock_client, mock_usage_instance


@pytest.fixture
def sample_subscription_created_event():
    """Sample customer.subscription.created event."""
    return {
        "id": "evt_sub_created_123",
        "type": "customer.subscription.created",
        "data": {
            "object": {
                "id": "sub_123",
                "customer": "cus_123",
                "status": "active",
                "items": {
                    "data": [{"price": {"id": "price_123", "currency": "brl", "unit_amount": 2990}}]
                },
                "metadata": {"user_id": "user_123", "tier_id": "flow_pro"},
                "current_period_start": int(datetime.utcnow().timestamp()),
                "current_period_end": int((datetime.utcnow() + timedelta(days=30)).timestamp()),
            }
        },
    }


@pytest.fixture
def sample_subscription_updated_event():
    """Sample customer.subscription.updated event."""
    return {
        "id": "evt_sub_updated_123",
        "type": "customer.subscription.updated",
        "data": {
            "object": {
                "id": "sub_123",
                "customer": "cus_123",
                "status": "active",
                "items": {
                    "data": [
                        {
                            "price": {
                                "id": "price_456",  # Different price (upgrade/downgrade)
                                "currency": "brl",
                                "unit_amount": 9990,
                            }
                        }
                    ]
                },
                "metadata": {"user_id": "user_123", "tier_id": "flow_business"},
                "cancel_at_period_end": False,
            }
        },
    }


@pytest.fixture
def sample_subscription_deleted_event():
    """Sample customer.subscription.deleted event."""
    return {
        "id": "evt_sub_deleted_123",
        "type": "customer.subscription.deleted",
        "data": {
            "object": {
                "id": "sub_123",
                "customer": "cus_123",
                "status": "canceled",
                "canceled_at": int(datetime.utcnow().timestamp()),
                "metadata": {"user_id": "user_123", "tier_id": "flow_pro"},
            }
        },
    }


@pytest.fixture
def sample_invoice_payment_succeeded_event():
    """Sample invoice.payment_succeeded event."""
    return {
        "id": "evt_invoice_paid_123",
        "type": "invoice.payment_succeeded",
        "data": {
            "object": {
                "id": "in_123",
                "customer": "cus_123",
                "subscription": "sub_123",
                "status": "paid",
                "amount_paid": 2990,
                "currency": "brl",
                "payment_intent": "pi_123",
                "metadata": {"user_id": "user_123"},
                "period_start": int(datetime.utcnow().timestamp()),
                "period_end": int((datetime.utcnow() + timedelta(days=30)).timestamp()),
            }
        },
    }


@pytest.fixture
def sample_invoice_payment_failed_event():
    """Sample invoice.payment_failed event."""
    return {
        "id": "evt_invoice_failed_123",
        "type": "invoice.payment_failed",
        "data": {
            "object": {
                "id": "in_456",
                "customer": "cus_123",
                "subscription": "sub_123",
                "status": "open",
                "amount_due": 2990,
                "currency": "brl",
                "attempt_count": 1,
                "metadata": {"user_id": "user_123"},
            }
        },
    }


class TestSubscriptionCreatedWebhook:
    """Test customer.subscription.created webhook event."""

    @pytest.mark.asyncio
    async def test_subscription_created_success(
        self, mock_webhook_service, sample_subscription_created_event
    ):
        """Test successful subscription creation webhook."""
        webhook_service, mock_client, mock_usage = mock_webhook_service

        # Mock database responses
        mock_client.table().select().execute.return_value = Mock(
            data=[]
        )  # No existing subscription
        mock_client.table().insert().execute.return_value = Mock(data=[{"id": "sub_db_123"}])

        # Mock subscription service
        with patch("app.services.webhook_service.subscription_service") as mock_sub_service:
            mock_sub_service.create_subscription.return_value = Mock(
                id="sub_db_123", tier_id="flow_pro"
            )

            # Act
            result = await webhook_service.process_subscription_created(
                sample_subscription_created_event["data"]["object"]
            )

            # Assert
            assert result["success"] is True
            assert result["subscription_id"] == "sub_db_123"
            assert result["user_id"] == "user_123"
            assert result["tier_id"] == "flow_pro"
            mock_sub_service.create_subscription.assert_called_once()

    @pytest.mark.asyncio
    async def test_subscription_created_missing_user_id(
        self, mock_webhook_service, sample_subscription_created_event
    ):
        """Test subscription creation webhook with missing user_id."""
        webhook_service, mock_client, mock_usage = mock_webhook_service

        # Remove user_id from metadata
        event_data = sample_subscription_created_event["data"]["object"]
        event_data["metadata"] = {}

        # Act
        result = await webhook_service.process_subscription_created(event_data)

        # Assert
        assert result["success"] is False
        assert "User ID not found" in result["error"]

    @pytest.mark.asyncio
    async def test_subscription_created_missing_price(
        self, mock_webhook_service, sample_subscription_created_event
    ):
        """Test subscription creation webhook with missing price information."""
        webhook_service, mock_client, mock_usage = mock_webhook_service

        # Remove price information
        event_data = sample_subscription_created_event["data"]["object"]
        event_data["items"]["data"][0]["price"] = {}

        # Mock database responses
        mock_client.table().select().execute.return_value = Mock(data=[])
        mock_client.table().insert().execute.return_value = Mock(data=[{"id": "sub_db_123"}])

        # Mock subscription service
        with patch("app.services.webhook_service.subscription_service") as mock_sub_service:
            mock_sub_service.create_subscription.return_value = Mock(id="sub_db_123")

            # Act
            result = await webhook_service.process_subscription_created(event_data)

            # Assert
            assert result["success"] is True
            # Should handle missing price gracefully

    @pytest.mark.asyncio
    async def test_subscription_created_service_error(
        self, mock_webhook_service, sample_subscription_created_event
    ):
        """Test subscription creation webhook when service fails."""
        webhook_service, mock_client, mock_usage = mock_webhook_service

        # Mock database responses
        mock_client.table().select().execute.return_value = Mock(data=[])

        # Mock subscription service to raise exception
        with patch("app.services.webhook_service.subscription_service") as mock_sub_service:
            mock_sub_service.create_subscription.side_effect = Exception("Service error")

            # Act
            result = await webhook_service.process_subscription_created(
                sample_subscription_created_event["data"]["object"]
            )

            # Assert
            assert result["success"] is False
            assert "Service error" in result["error"]


class TestSubscriptionUpdatedWebhook:
    """Test customer.subscription.updated webhook event."""

    @pytest.mark.asyncio
    async def test_subscription_updated_success(
        self, mock_webhook_service, sample_subscription_updated_event
    ):
        """Test successful subscription update webhook."""
        webhook_service, mock_client, mock_usage = mock_webhook_service

        # Mock existing subscription lookup
        mock_client.table().select().eq().execute.return_value = Mock(
            data=[{"id": "sub_db_123", "stripe_subscription_id": "sub_123", "user_id": "user_123"}]
        )

        # Mock subscription service
        with patch("app.services.webhook_service.subscription_service") as mock_sub_service:
            mock_sub_service.update_subscription.return_value = Mock(
                id="sub_db_123", tier_id="flow_business"
            )

            # Act
            result = await webhook_service.process_subscription_updated(
                sample_subscription_updated_event["data"]["object"]
            )

            # Assert
            assert result["success"] is True
            assert result["subscription_id"] == "sub_db_123"
            assert result["tier_id"] == "flow_business"
            mock_sub_service.update_subscription.assert_called_once()

    @pytest.mark.asyncio
    async def test_subscription_updated_not_found(
        self, mock_webhook_service, sample_subscription_updated_event
    ):
        """Test subscription update webhook when subscription not found."""
        webhook_service, mock_client, mock_usage = mock_webhook_service

        # Mock subscription lookup returns empty
        mock_client.table().select().eq().execute.return_value = Mock(data=[])

        # Act
        result = await webhook_service.process_subscription_updated(
            sample_subscription_updated_event["data"]["object"]
        )

        # Assert
        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_subscription_updated_tier_change(
        self, mock_webhook_service, sample_subscription_updated_event
    ):
        """Test subscription update webhook with tier change."""
        webhook_service, mock_client, mock_usage = mock_webhook_service

        # Mock existing subscription lookup
        mock_client.table().select().eq().execute.return_value = Mock(
            data=[
                {
                    "id": "sub_db_123",
                    "stripe_subscription_id": "sub_123",
                    "user_id": "user_123",
                    "tier_id": "flow_pro",  # Old tier
                }
            ]
        )

        # Mock subscription service
        with patch("app.services.webhook_service.subscription_service") as mock_sub_service:
            mock_sub_service.update_subscription.return_value = Mock(
                id="sub_db_123",
                tier_id="flow_business",  # New tier
            )

            # Act
            result = await webhook_service.process_subscription_updated(
                sample_subscription_updated_event["data"]["object"]
            )

            # Assert
            assert result["success"] is True

            # Verify update_data includes tier change
            call_args = mock_sub_service.update_subscription.call_args
            update_data = call_args[0][1]  # Second argument is the update data
            assert update_data.tier_id == "flow_business"

    @pytest.mark.asyncio
    async def test_subscription_updated_cancellation_flag(self, mock_webhook_service):
        """Test subscription update webhook with cancellation flag."""
        webhook_service, mock_client, mock_usage = mock_webhook_service

        # Create event with cancellation flag
        event_data = {
            "id": "sub_123",
            "customer": "cus_123",
            "status": "active",
            "cancel_at_period_end": True,  # Set to cancel at period end
            "items": {"data": [{"price": {"id": "price_123"}}]},
        }

        # Mock existing subscription lookup
        mock_client.table().select().eq().execute.return_value = Mock(
            data=[{"id": "sub_db_123", "stripe_subscription_id": "sub_123"}]
        )

        # Mock subscription service
        with patch("app.services.webhook_service.subscription_service") as mock_sub_service:
            mock_sub_service.update_subscription.return_value = Mock(id="sub_db_123")

            # Act
            result = await webhook_service.process_subscription_updated(event_data)

            # Assert
            assert result["success"] is True

            # Verify update_data includes cancellation flag
            call_args = mock_sub_service.update_subscription.call_args
            update_data = call_args[0][1]
            assert update_data.cancel_at_period_end is True


class TestSubscriptionDeletedWebhook:
    """Test customer.subscription.deleted webhook event."""

    @pytest.mark.asyncio
    async def test_subscription_deleted_success(
        self, mock_webhook_service, sample_subscription_deleted_event
    ):
        """Test successful subscription deletion webhook."""
        webhook_service, mock_client, mock_usage = mock_webhook_service

        # Mock existing subscription lookup
        mock_client.table().select().eq().execute.return_value = Mock(
            data=[{"id": "sub_db_123", "stripe_subscription_id": "sub_123", "user_id": "user_123"}]
        )

        # Mock subscription service
        with patch("app.services.webhook_service.subscription_service") as mock_sub_service:
            mock_sub_service.cancel_subscription.return_value = Mock(
                id="sub_db_123", status="canceled"
            )

            # Act
            result = await webhook_service.process_subscription_deleted(
                sample_subscription_deleted_event["data"]["object"]
            )

            # Assert
            assert result["success"] is True
            assert result["subscription_id"] == "sub_db_123"
            assert result["status"] == "canceled"
            mock_sub_service.cancel_subscription.assert_called_once_with(
                "sub_db_123", immediate=True
            )

    @pytest.mark.asyncio
    async def test_subscription_deleted_not_found(
        self, mock_webhook_service, sample_subscription_deleted_event
    ):
        """Test subscription deletion webhook when subscription not found."""
        webhook_service, mock_client, mock_usage = mock_webhook_service

        # Mock subscription lookup returns empty
        mock_client.table().select().eq().execute.return_value = Mock(data=[])

        # Act
        result = await webhook_service.process_subscription_deleted(
            sample_subscription_deleted_event["data"]["object"]
        )

        # Assert
        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_subscription_deleted_service_error(
        self, mock_webhook_service, sample_subscription_deleted_event
    ):
        """Test subscription deletion webhook when service fails."""
        webhook_service, mock_client, mock_usage = mock_webhook_service

        # Mock existing subscription lookup
        mock_client.table().select().eq().execute.return_value = Mock(
            data=[{"id": "sub_db_123", "stripe_subscription_id": "sub_123"}]
        )

        # Mock subscription service to raise exception
        with patch("app.services.webhook_service.subscription_service") as mock_sub_service:
            mock_sub_service.cancel_subscription.side_effect = Exception("Cancel failed")

            # Act
            result = await webhook_service.process_subscription_deleted(
                sample_subscription_deleted_event["data"]["object"]
            )

            # Assert
            assert result["success"] is False
            assert "Cancel failed" in result["error"]


class TestInvoicePaymentSucceededWebhook:
    """Test invoice.payment_succeeded webhook event."""

    @pytest.mark.asyncio
    async def test_invoice_payment_succeeded_with_subscription(
        self, mock_webhook_service, sample_invoice_payment_succeeded_event
    ):
        """Test successful invoice payment with subscription renewal."""
        webhook_service, mock_client, mock_usage = mock_webhook_service

        # Mock subscription lookup
        mock_client.table().select().eq().execute.return_value = Mock(
            data=[{"id": "sub_db_123", "stripe_subscription_id": "sub_123", "user_id": "user_123"}]
        )

        # Mock payment history creation
        mock_client.table().insert().execute.return_value = Mock(data=[{"id": "payment_hist_123"}])

        # Mock subscription service for renewal
        with patch("app.services.webhook_service.subscription_service") as mock_sub_service:
            mock_sub_service.process_period_renewal.return_value = Mock(
                id="sub_db_123", analyses_rollover=25
            )

            # Act
            result = await webhook_service.process_invoice_payment_succeeded(
                sample_invoice_payment_succeeded_event["data"]["object"]
            )

            # Assert
            assert result["success"] is True
            assert result["user_id"] == "user_123"
            assert result["subscription_renewed"] is True
            mock_sub_service.process_period_renewal.assert_called_once_with("sub_db_123")

    @pytest.mark.asyncio
    async def test_invoice_payment_succeeded_one_time_payment(self, mock_webhook_service):
        """Test successful invoice payment for one-time payment (no subscription)."""
        webhook_service, mock_client, mock_usage = mock_webhook_service

        # Create event without subscription
        event_data = {
            "id": "in_789",
            "customer": "cus_123",
            "amount_paid": 9990,
            "currency": "brl",
            "payment_intent": "pi_789",
            "metadata": {"user_id": "user_123"},
        }

        # Mock payment history creation
        mock_client.table().insert().execute.return_value = Mock(data=[{"id": "payment_hist_789"}])

        # Act
        result = await webhook_service.process_invoice_payment_succeeded(event_data)

        # Assert
        assert result["success"] is True
        assert result["user_id"] == "user_123"
        assert result["subscription_renewed"] is False

    @pytest.mark.asyncio
    async def test_invoice_payment_succeeded_missing_user_id(
        self, mock_webhook_service, sample_invoice_payment_succeeded_event
    ):
        """Test invoice payment succeeded with missing user_id."""
        webhook_service, mock_client, mock_usage = mock_webhook_service

        # Remove user_id from metadata
        event_data = sample_invoice_payment_succeeded_event["data"]["object"]
        event_data["metadata"] = {}

        # Mock subscription lookup to provide user_id
        mock_client.table().select().eq().execute.return_value = Mock(
            data=[
                {
                    "id": "sub_db_123",
                    "stripe_subscription_id": "sub_123",
                    "user_id": "user_123",  # Found via subscription lookup
                }
            ]
        )

        # Mock payment history creation
        mock_client.table().insert().execute.return_value = Mock(data=[{"id": "payment_hist_123"}])

        # Act
        result = await webhook_service.process_invoice_payment_succeeded(event_data)

        # Assert
        assert result["success"] is True
        assert result["user_id"] == "user_123"

    @pytest.mark.asyncio
    async def test_invoice_payment_succeeded_renewal_failure(
        self, mock_webhook_service, sample_invoice_payment_succeeded_event
    ):
        """Test invoice payment succeeded when renewal fails (should still record payment)."""
        webhook_service, mock_client, mock_usage = mock_webhook_service

        # Mock subscription lookup
        mock_client.table().select().eq().execute.return_value = Mock(
            data=[{"id": "sub_db_123", "stripe_subscription_id": "sub_123", "user_id": "user_123"}]
        )

        # Mock payment history creation
        mock_client.table().insert().execute.return_value = Mock(data=[{"id": "payment_hist_123"}])

        # Mock subscription service to fail renewal
        with patch("app.services.webhook_service.subscription_service") as mock_sub_service:
            mock_sub_service.process_period_renewal.side_effect = Exception("Renewal failed")

            # Act
            result = await webhook_service.process_invoice_payment_succeeded(
                sample_invoice_payment_succeeded_event["data"]["object"]
            )

            # Assert
            assert result["success"] is True  # Payment still recorded
            assert result["user_id"] == "user_123"


class TestInvoicePaymentFailedWebhook:
    """Test invoice.payment_failed webhook event."""

    @pytest.mark.asyncio
    async def test_invoice_payment_failed_success(
        self, mock_webhook_service, sample_invoice_payment_failed_event
    ):
        """Test invoice payment failed webhook processing."""
        webhook_service, mock_client, mock_usage = mock_webhook_service

        # Mock subscription lookup
        mock_client.table().select().eq().execute.return_value = Mock(
            data=[{"id": "sub_db_123", "stripe_subscription_id": "sub_123", "user_id": "user_123"}]
        )

        # Mock subscription service
        with patch("app.services.webhook_service.subscription_service") as mock_sub_service:
            mock_sub_service.update_subscription.return_value = Mock(
                id="sub_db_123", status="past_due"
            )

            # Act
            result = await webhook_service.process_invoice_payment_failed(
                sample_invoice_payment_failed_event["data"]["object"]
            )

            # Assert
            assert result["success"] is True
            assert result["subscription_id"] == "sub_db_123"
            assert result["status"] == "past_due"
            mock_sub_service.update_subscription.assert_called_once()

    @pytest.mark.asyncio
    async def test_invoice_payment_failed_subscription_not_found(
        self, mock_webhook_service, sample_invoice_payment_failed_event
    ):
        """Test invoice payment failed when subscription not found."""
        webhook_service, mock_client, mock_usage = mock_webhook_service

        # Mock subscription lookup returns empty
        mock_client.table().select().eq().execute.return_value = Mock(data=[])

        # Act
        result = await webhook_service.process_invoice_payment_failed(
            sample_invoice_payment_failed_event["data"]["object"]
        )

        # Assert
        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_invoice_payment_failed_missing_subscription_id(self, mock_webhook_service):
        """Test invoice payment failed with missing subscription ID."""
        webhook_service, mock_client, mock_usage = mock_webhook_service

        # Create event without subscription
        event_data = {
            "id": "in_no_sub",
            "customer": "cus_123",
            "amount_due": 2990,
            "currency": "brl",
        }

        # Act
        result = await webhook_service.process_invoice_payment_failed(event_data)

        # Assert
        assert result["success"] is False
        assert "Subscription ID not found" in result["error"]


class TestCompleteWebhookFlow:
    """Test complete webhook event flow with idempotency."""

    @pytest.mark.asyncio
    async def test_complete_subscription_lifecycle(self, mock_webhook_service):
        """Test complete subscription lifecycle through webhooks."""
        webhook_service, mock_client, mock_usage = mock_webhook_service

        # Step 1: Create subscription
        create_event = {
            "id": "sub_123",
            "customer": "cus_123",
            "status": "active",
            "items": {"data": [{"price": {"id": "price_123"}}]},
            "metadata": {"user_id": "user_123", "tier_id": "flow_pro"},
        }

        mock_client.table().select().execute.return_value = Mock(data=[])
        mock_client.table().insert().execute.return_value = Mock(data=[{"id": "sub_db_123"}])

        with patch("app.services.webhook_service.subscription_service") as mock_sub_service:
            mock_sub_service.create_subscription.return_value = Mock(id="sub_db_123")

            result1 = await webhook_service.process_subscription_created(create_event)
            assert result1["success"] is True

        # Step 2: Process successful payment (renewal)
        payment_event = {
            "id": "in_123",
            "customer": "cus_123",
            "subscription": "sub_123",
            "amount_paid": 2990,
            "currency": "brl",
            "metadata": {"user_id": "user_123"},
        }

        mock_client.table().select().eq().execute.return_value = Mock(
            data=[{"id": "sub_db_123", "stripe_subscription_id": "sub_123"}]
        )
        mock_client.table().insert().execute.return_value = Mock(data=[{"id": "payment_hist_123"}])

        with patch("app.services.webhook_service.subscription_service") as mock_sub_service:
            mock_sub_service.process_period_renewal.return_value = Mock(id="sub_db_123")

            result2 = await webhook_service.process_invoice_payment_succeeded(payment_event)
            assert result2["success"] is True

        # Step 3: Cancel subscription
        delete_event = {
            "id": "sub_123",
            "customer": "cus_123",
            "status": "canceled",
            "metadata": {"user_id": "user_123"},
        }

        mock_client.table().select().eq().execute.return_value = Mock(
            data=[{"id": "sub_db_123", "stripe_subscription_id": "sub_123"}]
        )

        with patch("app.services.webhook_service.subscription_service") as mock_sub_service:
            mock_sub_service.cancel_subscription.return_value = Mock(
                id="sub_db_123", status="canceled"
            )

            result3 = await webhook_service.process_subscription_deleted(delete_event)
            assert result3["success"] is True

    @pytest.mark.asyncio
    async def test_webhook_idempotency(
        self, mock_webhook_service, sample_subscription_created_event
    ):
        """Test webhook event idempotency."""
        webhook_service, mock_client, mock_usage = mock_webhook_service

        # First event - should succeed
        mock_client.table().select().execute.return_value = Mock(data=[])
        mock_client.table().insert().execute.return_value = Mock(data=[{"id": "sub_db_123"}])

        with patch("app.services.webhook_service.subscription_service") as mock_sub_service:
            mock_sub_service.create_subscription.return_value = Mock(id="sub_db_123")

            result1 = await webhook_service.process_webhook_event(
                "customer.subscription.created",
                sample_subscription_created_event["data"]["object"],
                "evt_sub_created_123",
            )
            assert result1["success"] is True
            assert result1["processed"] is True

        # Second event with same ID - should be idempotent
        mock_client.table().select().execute.return_value = Mock(
            data=[{"id": "evt_sub_created_123", "processed": True}]  # Event already processed
        )

        result2 = await webhook_service.process_webhook_event(
            "customer.subscription.created",
            sample_subscription_created_event["data"]["object"],
            "evt_sub_created_123",
        )
        assert result2["success"] is True
        assert result2["idempotent"] is True
