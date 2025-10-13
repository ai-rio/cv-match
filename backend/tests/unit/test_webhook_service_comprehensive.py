"""
Comprehensive unit tests for webhook service functionality.
Tests webhook processing, idempotency, and error handling for CV-Match.
"""

import json
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest

from app.services.webhook_service import WebhookService


@pytest.mark.unit
@pytest.mark.webhook
class TestWebhookServiceComprehensive:
    """Comprehensive tests for webhook service functionality."""

    def setup_method(self):
        """Set up test method."""
        self.service = WebhookService()
        self.test_user_id = str(uuid4())
        self.test_event_id = f"evt_test_{uuid4()}"

    @pytest.mark.asyncio
    async def test_process_webhook_event_success(self):
        """Test successful webhook event processing."""
        event_type = "checkout.session.completed"
        event_data = {
            "id": "cs_test_123",
            "metadata": {"user_id": self.test_user_id},
            "amount_total": 2990,
            "currency": "brl",
        }

        # Mock event not processed
        with patch.object(self.service, "is_event_processed", return_value=False):
            # Mock event logging
            with patch.object(self.service, "log_webhook_event", return_value={"success": True}):
                # Mock specific event processing
                with patch.object(
                    self.service, "_process_specific_event", return_value={"success": True}
                ):
                    # Mock marking as processed
                    with patch.object(self.service, "_mark_event_processed"):
                        result = await self.service.process_webhook_event(
                            event_type, event_data, self.test_event_id
                        )

        assert result["success"] is True
        assert result["event_id"] == self.test_event_id
        assert result["event_type"] == event_type
        assert result["processed"] is True
        assert "processing_time_ms" in result

    @pytest.mark.asyncio
    async def test_process_webhook_event_idempotency(self):
        """Test webhook event idempotency - already processed events are skipped."""
        event_type = "checkout.session.completed"
        event_data = {"id": "cs_test_123"}

        # Mock event already processed
        with patch.object(self.service, "is_event_processed", return_value=True):
            result = await self.service.process_webhook_event(
                event_type, event_data, self.test_event_id
            )

        assert result["success"] is True
        assert result["idempotent"] is True
        assert "already processed" in result["message"]

    @pytest.mark.asyncio
    async def test_process_webhook_event_processing_error(self):
        """Test webhook event processing with error."""
        event_type = "checkout.session.completed"
        event_data = {"id": "cs_test_123"}

        # Mock event not processed
        with patch.object(self.service, "is_event_processed", return_value=False):
            # Mock event logging
            with patch.object(self.service, "log_webhook_event", return_value={"success": True}):
                # Mock specific event processing failure
                with patch.object(
                    self.service,
                    "_process_specific_event",
                    return_value={"success": False, "error": "Processing failed"},
                ):
                    # Mock marking as processed with error
                    with patch.object(self.service, "_mark_event_processed"):
                        result = await self.service.process_webhook_event(
                            event_type, event_data, self.test_event_id
                        )

        assert result["success"] is False
        assert result["error"] == "Processing failed"
        assert result["processed"] is True

    @pytest.mark.asyncio
    async def test_process_webhook_event_system_error(self):
        """Test webhook event processing with system error."""
        event_type = "checkout.session.completed"
        event_data = {"id": "cs_test_123"}

        # Mock event not processed
        with patch.object(self.service, "is_event_processed", return_value=False):
            # Mock event logging
            with patch.object(self.service, "log_webhook_event", return_value={"success": True}):
                # Mock system error during processing
                with patch.object(
                    self.service, "_process_specific_event", side_effect=Exception("System error")
                ):
                    # Mock marking as processed with error
                    with patch.object(self.service, "_mark_event_processed"):
                        result = await self.service.process_webhook_event(
                            event_type, event_data, self.test_event_id
                        )

        assert result["success"] is False
        assert "Webhook processing failed" in result["error"]
        assert "System error" in result["error"]

    @pytest.mark.asyncio
    async def test_is_event_processed_true(self):
        """Test checking if event is processed returns True."""
        mock_event = {
            "id": "event_123",
            "processed": True,
            "processed_at": datetime.now(UTC).isoformat(),
        }

        with patch.object(self.service, "_get_by_field", return_value=mock_event):
            result = await self.service.is_event_processed(self.test_event_id)

        assert result is True

    @pytest.mark.asyncio
    async def test_is_event_processed_false(self):
        """Test checking if event is processed returns False."""
        with patch.object(self.service, "_get_by_field", return_value=None):
            result = await self.service.is_event_processed(self.test_event_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_is_event_processed_false_not_processed_flag(self):
        """Test checking if event exists but not processed returns False."""
        mock_event = {
            "id": "event_123",
            "processed": False,
            "created_at": datetime.now(UTC).isoformat(),
        }

        with patch.object(self.service, "_get_by_field", return_value=mock_event):
            result = await self.service.is_event_processed(self.test_event_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_is_event_processed_database_error(self):
        """Test checking event processing status with database error."""
        with patch.object(self.service, "_get_by_field", side_effect=Exception("Database error")):
            result = await self.service.is_event_processed(self.test_event_id)

        assert result is False  # Should default to False on error

    @pytest.mark.asyncio
    async def test_log_webhook_event_success(self):
        """Test successful webhook event logging."""
        event_data = {
            "id": "cs_test_123",
            "customer": "cus_test_123",
            "amount_total": 2990,
            "currency": "brl",
            "payment_status": "paid",
        }

        with patch.object(self.service, "_create", return_value={"id": "webhook_log_123"}):
            result = await self.service.log_webhook_event(
                self.test_event_id, "checkout.session.completed", event_data, False
            )

        assert result["success"] is True
        assert result["webhook_event_id"] == "webhook_log_123"
        assert result["stripe_event_id"] == self.test_event_id

    @pytest.mark.asyncio
    async def test_log_webhook_event_different_event_types(self):
        """Test logging webhook events for different event types."""
        test_cases = [
            {
                "event_type": "checkout.session.completed",
                "event_data": {
                    "id": "cs_test_123",
                    "customer": "cus_test_123",
                    "amount_total": 2990,
                    "currency": "brl",
                    "payment_status": "paid",
                    "metadata": {"user_id": self.test_user_id},
                },
                "expected_user_id": self.test_user_id,
                "expected_amount": 2990,
            },
            {
                "event_type": "invoice.payment_succeeded",
                "event_data": {
                    "id": "in_test_123",
                    "customer": "cus_test_123",
                    "subscription": "sub_test_123",
                    "amount_paid": 2990,
                    "currency": "brl",
                    "metadata": {"user_id": self.test_user_id},
                },
                "expected_user_id": self.test_user_id,
                "expected_amount": 2990,
            },
            {
                "event_type": "payment_intent.succeeded",
                "event_data": {
                    "id": "pi_test_123",
                    "customer": "cus_test_123",
                    "amount": 9990,
                    "currency": "brl",
                    "metadata": {"user_id": self.test_user_id},
                },
                "expected_user_id": self.test_user_id,
                "expected_amount": 9990,
            },
        ]

        for case in test_cases:
            with self.subTest(event_type=case["event_type"]):
                with patch.object(
                    self.service, "_create", return_value={"id": "webhook_log_123"}
                ) as mock_create:
                    result = await self.service.log_webhook_event(
                        f"evt_test_{case['event_type']}",
                        case["event_type"],
                        case["event_data"],
                        False,
                    )

                    assert result["success"] is True

                    # Verify the logged data
                    call_args = mock_create.call_args[0][1]
                    assert call_args["event_id"] == f"evt_test_{case['event_type']}"
                    assert call_args["event_type"] == case["event_type"]
                    assert call_args["user_id"] == case["expected_user_id"]
                    assert call_args["amount"] == case["expected_amount"]
                    assert call_args["currency"] == "brl"

    @pytest.mark.asyncio
    async def test_log_webhook_event_unsupported_type(self):
        """Test logging webhook event for unsupported event type."""
        event_data = {"id": "test_123", "object": {"test": "data"}}

        with patch.object(self.service, "_create", return_value={"id": "webhook_log_123"}):
            result = await self.service.log_webhook_event(
                self.test_event_id, "account.updated", event_data, False
            )

        assert result["success"] is True

        # Verify unsupported event types are still logged
        call_args = self.service._create.call_args[1]
        assert call_args["event_type"] == "account.updated"
        assert call_args["user_id"] is None  # No user extraction for unsupported types

    @pytest.mark.asyncio
    async def test_log_webhook_event_database_error(self):
        """Test webhook event logging with database error."""
        event_data = {"id": "cs_test_123"}

        with patch.object(self.service, "_create", side_effect=Exception("Database error")):
            result = await self.service.log_webhook_event(
                self.test_event_id, "checkout.session.completed", event_data, False
            )

        assert result["success"] is False
        assert "Database error" in result["error"]

    @pytest.mark.asyncio
    async def test_process_specific_event_checkout_session_completed(self):
        """Test processing checkout.session.completed event."""
        session_data = {
            "id": "cs_test_123",
            "customer": "cus_test_123",
            "amount_total": 2990,
            "currency": "brl",
            "metadata": {"user_id": self.test_user_id, "plan": "pro"},
        }

        # Mock user payment profile
        mock_user_profile = {
            "id": "profile_123",
            "user_id": self.test_user_id,
            "stripe_customer_id": None,
        }

        # Mock dependencies
        with patch.object(self.service, "_get_by_field", return_value=mock_user_profile):
            with patch.object(self.service, "_update", return_value={"id": "profile_123"}):
                with patch.object(self.service, "_create", return_value={"id": "payment_123"}):
                    with patch.object(self.service, "usage_limit_service") as mock_usage:
                        mock_usage.add_credits.return_value = None

                        result = await self.service._process_specific_event(
                            "checkout.session.completed", session_data
                        )

        assert result["success"] is True
        assert result["user_id"] == self.test_user_id
        assert result["amount"] == 2990
        assert result["currency"] == "brl"
        assert result["credits_added"] == 50  # Pro plan credits
        assert result["plan_type"] == "pro"

    @pytest.mark.asyncio
    async def test_process_specific_event_missing_user_id(self):
        """Test processing event with missing user_id."""
        session_data = {
            "id": "cs_test_123",
            "customer": "cus_test_123",
            "amount_total": 2990,
            "metadata": {},  # Missing user_id
        }

        result = await self.service._process_specific_event(
            "checkout.session.completed", session_data
        )

        assert result["success"] is False
        assert "User ID not found" in result["error"]

    @pytest.mark.asyncio
    async def test_process_specific_event_user_not_found(self):
        """Test processing event when user profile is not found."""
        session_data = {
            "id": "cs_test_123",
            "customer": "cus_test_123",
            "metadata": {"user_id": self.test_user_id},
        }

        with patch.object(self.service, "_get_by_field", return_value=None):
            result = await self.service._process_specific_event(
                "checkout.session.completed", session_data
            )

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_process_specific_event_credit_addition_failure(self):
        """Test processing event when credit addition fails."""
        session_data = {
            "id": "cs_test_123",
            "customer": "cus_test_123",
            "metadata": {"user_id": self.test_user_id, "plan": "pro"},
        }

        # Mock user profile
        mock_user_profile = {"id": "profile_123", "user_id": self.test_user_id}

        with patch.object(self.service, "_get_by_field", return_value=mock_user_profile):
            with patch.object(self.service, "usage_limit_service") as mock_usage:
                mock_usage.add_credits.side_effect = Exception("Credit addition failed")

                result = await self.service._process_specific_event(
                    "checkout.session.completed", session_data
                )

        assert result["success"] is False
        assert "Failed to add credits" in result["error"]

    @pytest.mark.asyncio
    async def test_process_subscription_created(self):
        """Test processing customer.subscription.created event."""
        subscription_data = {
            "id": "sub_test_123",
            "customer": "cus_test_123",
            "status": "active",
            "current_period_start": int(datetime.now(UTC).timestamp()),
            "current_period_end": int((datetime.now(UTC) + timedelta(days=30)).timestamp()),
            "metadata": {"user_id": self.test_user_id, "plan": "pro"},
        }

        with patch.object(
            self.service, "_create_subscription_record", return_value={"id": "subscription_123"}
        ):
            result = await self.service._process_specific_event(
                "customer.subscription.created", subscription_data
            )

        assert result["success"] is True
        assert result["subscription_id"] == "subscription_123"
        assert result["user_id"] == self.test_user_id
        assert result["status"] == "active"

    @pytest.mark.asyncio
    async def test_process_subscription_updated(self):
        """Test processing customer.subscription.updated event."""
        subscription_data = {
            "id": "sub_test_123",
            "status": "past_due",
            "current_period_start": int(datetime.now(UTC).timestamp()),
            "current_period_end": int((datetime.now(UTC) + timedelta(days=30)).timestamp()),
            "cancel_at_period_end": False,
        }

        # Mock existing subscription
        mock_existing = {
            "id": "subscription_123",
            "stripe_subscription_id": "sub_test_123",
            "user_id": self.test_user_id,
        }

        with patch.object(self.service, "_get_by_field", return_value=mock_existing):
            with patch.object(
                self.service, "_update", return_value={**mock_existing, "status": "past_due"}
            ):
                result = await self.service._process_specific_event(
                    "customer.subscription.updated", subscription_data
                )

        assert result["success"] is True
        assert result["subscription_id"] == "subscription_123"
        assert result["status"] == "past_due"

    @pytest.mark.asyncio
    async def test_process_subscription_updated_not_found(self):
        """Test processing subscription update when subscription not found."""
        subscription_data = {"id": "sub_test_123", "status": "past_due"}

        with patch.object(self.service, "_get_by_field", return_value=None):
            result = await self.service._process_specific_event(
                "customer.subscription.updated", subscription_data
            )

        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_process_subscription_deleted(self):
        """Test processing customer.subscription.deleted event."""
        subscription_data = {
            "id": "sub_test_123",
            "canceled_at": int(datetime.now(UTC).timestamp()),
        }

        # Mock existing subscription
        mock_existing = {
            "id": "subscription_123",
            "stripe_subscription_id": "sub_test_123",
            "user_id": self.test_user_id,
        }

        with patch.object(self.service, "_get_by_field", return_value=mock_existing):
            with patch.object(
                self.service, "_update", return_value={**mock_existing, "status": "canceled"}
            ):
                result = await self.service._process_specific_event(
                    "customer.subscription.deleted", subscription_data
                )

        assert result["success"] is True
        assert result["subscription_id"] == "subscription_123"
        assert result["status"] == "canceled"

    @pytest.mark.asyncio
    async def test_process_invoice_payment_succeeded(self):
        """Test processing invoice.payment_succeeded event."""
        invoice_data = {
            "id": "in_test_123",
            "customer": "cus_test_123",
            "subscription": "sub_test_123",
            "amount_paid": 2990,
            "currency": "brl",
            "metadata": {"user_id": self.test_user_id},
        }

        # Mock subscription lookup
        mock_subscription = {
            "id": "subscription_123",
            "stripe_subscription_id": "sub_test_123",
            "user_id": self.test_user_id,
        }

        with patch.object(self.service, "_get_by_field", return_value=mock_subscription):
            with patch.object(self.service, "_create", return_value={"id": "payment_123"}):
                with patch.object(self.service, "usage_limit_service") as mock_usage:
                    mock_usage.add_credits.return_value = None

                    result = await self.service._process_specific_event(
                        "invoice.payment_succeeded", invoice_data
                    )

        assert result["success"] is True
        assert result["payment_history_id"] == "payment_123"
        assert result["user_id"] == self.test_user_id
        assert result["amount"] == 2990

    @pytest.mark.asyncio
    async def test_process_invoice_payment_succeeded_subscription_lookup(self):
        """Test processing invoice payment succeeded with subscription lookup."""
        invoice_data = {
            "id": "in_test_123",
            "customer": "cus_test_123",
            "subscription": "sub_test_123",
            "amount_paid": 2990,
            "currency": "brl",
            # No user_id in metadata
        }

        # Mock subscription lookup for user_id
        mock_subscription = {
            "id": "subscription_123",
            "stripe_subscription_id": "sub_test_123",
            "user_id": self.test_user_id,
        }

        with patch.object(self.service, "_get_by_field", return_value=mock_subscription):
            with patch.object(self.service, "_create", return_value={"id": "payment_123"}):
                with patch.object(self.service, "usage_limit_service") as mock_usage:
                    mock_usage.add_credits.return_value = None

                    result = await self.service._process_specific_event(
                        "invoice.payment_succeeded", invoice_data
                    )

        assert result["success"] is True
        assert result["user_id"] == self.test_user_id

    @pytest.mark.asyncio
    async def test_process_payment_intent_succeeded(self):
        """Test processing payment_intent.succeeded event."""
        intent_data = {
            "id": "pi_test_123",
            "customer": "cus_test_123",
            "amount": 29900,  # R$ 297,00 - Lifetime plan
            "currency": "brl",
            "metadata": {"user_id": self.test_user_id},
        }

        with patch.object(self.service, "_create", return_value={"id": "payment_123"}):
            with patch.object(self.service, "usage_limit_service") as mock_usage:
                mock_usage.add_credits.return_value = None

                result = await self.service._process_specific_event(
                    "payment_intent.succeeded", intent_data
                )

        assert result["success"] is True
        assert result["payment_id"] == "payment_123"
        assert result["user_id"] == self.test_user_id
        assert result["amount"] == 29900
        assert result["credits_added"] == 1000  # Lifetime plan credits

    @pytest.mark.asyncio
    async def test_process_payment_intent_failed(self):
        """Test processing payment_intent.payment_failed event."""
        intent_data = {
            "id": "pi_test_failed_123",
            "customer": "cus_test_123",
            "amount": 2990,
            "currency": "brl",
            "metadata": {"user_id": self.test_user_id},
        }

        with patch.object(self.service, "_create", return_value={"id": "payment_failed_123"}):
            result = await self.service._process_specific_event(
                "payment_intent.payment_failed", intent_data
            )

        assert result["success"] is True
        assert result["payment_id"] == "payment_failed_123"
        assert result["user_id"] == self.test_user_id
        assert result["status"] == "failed"

    @pytest.mark.asyncio
    async def test_process_unsupported_event_type(self):
        """Test processing unsupported event type."""
        event_data = {"id": "test_123", "object": {"test": "data"}}

        result = await self.service._process_specific_event("account.updated", event_data)

        assert result["success"] is True
        assert "not handled" in result["message"]
        assert result["handled"] is False

    @pytest.mark.asyncio
    async def test_create_subscription_record(self):
        """Test creating subscription record."""
        subscription_data = {
            "id": "sub_test_123",
            "customer": "cus_test_123",
            "status": "active",
            "current_period_start": int(datetime.now(UTC).timestamp()),
            "current_period_end": int((datetime.now(UTC) + timedelta(days=30)).timestamp()),
            "items": {"data": [{"price": {"id": "price_test_123", "product": "prod_test_123"}}]},
        }

        with patch.object(self.service, "_create", return_value={"id": "subscription_123"}):
            result = await self.service._create_subscription_record(
                subscription_data, self.test_user_id
            )

        assert result["id"] == "subscription_123"

        # Verify the subscription data was properly formatted
        call_args = self.service._create.call_args[0][1]
        assert call_args["user_id"] == self.test_user_id
        assert call_args["stripe_subscription_id"] == "sub_test_123"
        assert call_args["stripe_customer_id"] == "cus_test_123"
        assert call_args["status"] == "active"
        assert call_args["price_id"] == "price_test_123"
        assert call_args["product_id"] == "prod_test_123"

    @pytest.mark.asyncio
    async def test_create_subscription_record_missing_timestamps(self):
        """Test creating subscription record with missing timestamps."""
        subscription_data = {
            "id": "sub_test_123",
            "customer": "cus_test_123",
            "status": "active",
            # Missing timestamps
        }

        with patch.object(self.service, "_create", return_value={"id": "subscription_123"}):
            result = await self.service._create_subscription_record(
                subscription_data, self.test_user_id
            )

        assert result["id"] == "subscription_123"

        # Verify default timestamps were created
        call_args = self.service._create.call_args[0][1]
        assert call_args["current_period_start"] is not None
        assert call_args["current_period_end"] is not None
        # Should be 30 days from now
        end_timestamp = datetime.fromisoformat(
            call_args["current_period_end"].replace("Z", "+00:00")
        )
        start_timestamp = datetime.fromisoformat(
            call_args["current_period_start"].replace("Z", "+00:00")
        )
        assert (end_timestamp - start_timestamp).days == 30

    @pytest.mark.asyncio
    async def test_mark_event_processed_success(self):
        """Test marking event as processed successfully."""
        mock_event = {"id": "event_123", "event_id": self.test_event_id}

        with patch.object(self.service, "_get_by_field", return_value=mock_event):
            with patch.object(
                self.service, "_update", return_value={**mock_event, "processed": True}
            ):
                await self.service._mark_event_processed(
                    self.test_event_id, processing_time_ms=150.5
                )

        # Verify update was called with correct data
        call_args = self.service._update.call_args[0][2]
        assert call_args["processed"] is True
        assert call_args["processing_time_ms"] == 150.5
        assert "processed_at" in call_args

    @pytest.mark.asyncio
    async def test_mark_event_processed_with_error(self):
        """Test marking event as processed with error."""
        mock_event = {"id": "event_123", "event_id": self.test_event_id}

        with patch.object(self.service, "_get_by_field", return_value=mock_event):
            with patch.object(
                self.service, "_update", return_value={**mock_event, "processed": True}
            ):
                await self.service._mark_event_processed(
                    self.test_event_id, processing_time_ms=100.0, error_message="Processing failed"
                )

        # Verify update was called with error
        call_args = self.service._update.call_args[0][2]
        assert call_args["processed"] is True
        assert call_args["error_message"] == "Processing failed"

    @pytest.mark.asyncio
    async def test_mark_event_processed_event_not_found(self):
        """Test marking event as processed when event not found."""
        with patch.object(self.service, "_get_by_field", return_value=None):
            # Should not raise exception
            await self.service._mark_event_processed(self.test_event_id, processing_time_ms=100.0)

        # Verify update was not called
        self.service._update.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_payment_description(self):
        """Test payment description generation."""
        test_cases = [
            {"plan": "pro", "amount": 2990, "expected": "Plano Profissional - R$ 29.90"},
            {"plan": "enterprise", "amount": 9990, "expected": "Plano Empresarial - R$ 99.90"},
            {"plan": "lifetime", "amount": 29700, "expected": "Acesso Vitalício - R$ 297.00"},
            {"plan": "free", "amount": 0, "expected": "Plano Grátis - R$ 0.00"},
            {"plan": "unknown", "amount": 5000, "expected": "Plano unknown - R$ 50.00"},
        ]

        for case in test_cases:
            with self.subTest(plan=case["plan"]):
                session_data = {
                    "metadata": {"plan": case["plan"]},
                    "amount_total": case["amount"],
                    "currency": "brl",
                }

                result = self.service._get_payment_description(session_data)

                assert result == case["expected"]

    @pytest.mark.asyncio
    async def test_safe_fromtimestamp(self):
        """Test safe timestamp conversion."""
        # Test with valid timestamp
        timestamp = 1704067200  # 2024-01-01 00:00:00 UTC
        result = self.service._safe_fromtimestamp(timestamp)
        assert result == "2024-01-01T00:00:00+00:00"

        # Test with None
        result = self.service._safe_fromtimestamp(None)
        assert result is None

        # Test with string timestamp
        timestamp_str = "1704067200"
        result = self.service._safe_fromtimestamp(timestamp_str)
        assert result == "2024-01-01T00:00:00+00:00"

    @pytest.mark.asyncio
    async def test_webhook_processing_time_measurement(self):
        """Test that webhook processing time is measured accurately."""
        event_type = "checkout.session.completed"
        event_data = {"id": "cs_test_123"}

        # Mock dependencies
        with patch.object(self.service, "is_event_processed", return_value=False):
            with patch.object(self.service, "log_webhook_event", return_value={"success": True}):
                with patch.object(
                    self.service, "_process_specific_event", return_value={"success": True}
                ):
                    with patch.object(self.service, "_mark_event_processed") as mock_mark:
                        await self.service.process_webhook_event(
                            event_type, event_data, self.test_event_id
                        )

                        # Verify _mark_event_processed was called
                        mock_mark.assert_called_once()

                        # Verify processing_time_ms was included
                        call_args = mock_mark.call_args[0]
                        assert "processing_time_ms" in call_args[1]
                        assert isinstance(call_args[1]["processing_time_ms"], float)
                        assert call_args[1]["processing_time_ms"] >= 0

    @pytest.mark.asyncio
    async def test_brazilian_credit_amounts(self):
        """Test Brazilian market credit amounts for different payment values."""
        test_cases = [
            {
                "amount": 29900,  # R$ 297,00 - Lifetime
                "expected_credits": 1000,
            },
            {
                "amount": 9990,  # R$ 99,90 - Enterprise
                "expected_credits": 1000,
            },
            {
                "amount": 2990,  # R$ 29,90 - Pro
                "expected_credits": 50,
            },
            {
                "amount": 990,  # R$ 9,90 - Basic
                "expected_credits": 10,
            },
            {
                "amount": 500,  # Below threshold
                "expected_credits": 0,
            },
        ]

        for case in test_cases:
            with self.subTest(amount=case["amount"]):
                intent_data = {
                    "id": f"pi_test_{case['amount']}",
                    "customer": "cus_test_123",
                    "amount": case["amount"],
                    "currency": "brl",
                    "metadata": {"user_id": self.test_user_id},
                }

                with patch.object(self.service, "_create", return_value={"id": "payment_123"}):
                    with patch.object(self.service, "usage_limit_service") as mock_usage:
                        mock_usage.add_credits.return_value = None

                        result = await self.service._process_specific_event(
                            "payment_intent.succeeded", intent_data
                        )

                        assert result["credits_added"] == case["expected_credits"]
                        if case["expected_credits"] > 0:
                            mock_usage.add_credits.assert_called_once_with(
                                user_id=UUID(self.test_user_id),
                                amount=case["expected_credits"],
                                source="payment",
                                description=f"Credits from one-time payment of R$ {case['amount'] / 100:.2f}",
                            )
