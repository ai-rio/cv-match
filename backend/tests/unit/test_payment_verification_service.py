"""
Unit tests for payment verification service functionality.
Tests payment verification and credit activation for the CV-Match SaaS.
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.payment_verification import (
    PaymentVerificationService,
    payment_verification_service,
)


@pytest.mark.unit
@pytest.mark.payment
class TestPaymentVerificationService:
    """Test payment verification service functionality."""

    def setup_method(self):
        """Set up test method."""
        self.test_user_id = "user_1234567890"
        self.test_session_id = "cs_test_1234567890"
        self.service = PaymentVerificationService()

    @pytest.mark.asyncio
    async def test_verify_and_activate_credits_success(self):
        """Test successful payment verification and credit activation."""
        # Mock successful Stripe session retrieval
        mock_session = MagicMock()
        mock_session.payment_status = "paid"
        mock_session.payment_intent = "pi_test_1234567890"
        mock_session.amount_total = 2990  # R$ 29,90
        mock_session.currency = "brl"

        with patch.object(self.service.stripe_service, 'retrieve_checkout_session', return_value={
            "success": True,
            "session": mock_session
        }):
            # Mock no existing payment (idempotency check)
            with patch.object(self.service.payment_db, 'get_by_filters', return_value=[]):
                # Mock successful payment creation
                mock_payment = {
                    "id": "payment_123",
                    "user_id": self.test_user_id,
                    "amount": 2990,
                    "status": "succeeded"
                }
                with patch.object(self.service.payment_db, 'create', return_value=mock_payment):
                    result = await self.service.verify_and_activate_credits(
                        self.test_session_id,
                        self.test_user_id,
                        "pro"
                    )

        assert result["success"] is True
        assert result["user_id"] == self.test_user_id
        assert result["plan_type"] == "pro"
        assert result["payment_id"] == "payment_123"
        assert result["amount_paid"] == 2990
        assert result["currency"] == "brl"
        assert result["credits_activated"] == 100  # Pro plan credits

    @pytest.mark.asyncio
    async def test_verify_and_activate_credits_session_not_paid(self):
        """Test payment verification when session is not paid."""
        # Mock unpaid session
        mock_session = MagicMock()
        mock_session.payment_status = "unpaid"
        mock_session.amount_total = 2990
        mock_session.currency = "brl"

        with patch.object(self.service.stripe_service, 'retrieve_checkout_session', return_value={
            "success": True,
            "session": mock_session
        }):
            result = await self.service.verify_and_activate_credits(
                self.test_session_id,
                self.test_user_id,
                "pro"
            )

        assert result["success"] is False
        assert result["error"] == "Payment not completed"
        assert result["status"] == "unpaid"

    @pytest.mark.asyncio
    async def test_verify_and_activate_credits_invalid_session(self):
        """Test payment verification with invalid session."""
        with patch.object(self.service.stripe_service, 'retrieve_checkout_session', return_value={
            "success": False,
            "error": "Invalid session"
        }):
            result = await self.service.verify_and_activate_credits(
                self.test_session_id,
                self.test_user_id,
                "pro"
            )

        assert result["success"] is False
        assert result["error"] == "Invalid session"

    @pytest.mark.asyncio
    async def test_verify_and_activate_credits_already_processed(self):
        """Test payment verification for already processed payment (idempotency)."""
        # Mock successful session retrieval
        mock_session = MagicMock()
        mock_session.payment_status = "paid"
        mock_session.payment_intent = "pi_test_1234567890"
        mock_session.amount_total = 2990
        mock_session.currency = "brl"

        with patch.object(self.service.stripe_service, 'retrieve_checkout_session', return_value={
            "success": True,
            "session": mock_session
        }):
            # Mock existing payment (already processed)
            existing_payment = {
                "id": "payment_existing_123",
                "user_id": self.test_user_id,
                "stripe_checkout_session_id": self.test_session_id
            }
            with patch.object(self.service.payment_db, 'get_by_filters', return_value=[existing_payment]):
                result = await self.service.verify_and_activate_credits(
                    self.test_session_id,
                    self.test_user_id,
                    "pro"
                )

        assert result["success"] is True
        assert result["message"] == "Payment already processed"
        assert result["payment_id"] == "payment_existing_123"

    @pytest.mark.asyncio
    async def test_verify_and_activate_credits_different_plans(self):
        """Test payment verification for different plan types."""
        test_cases = [
            ("free", 5),
            ("pro", 100),
            ("enterprise", 500),
            ("lifetime", 1000),
        ]

        for plan_type, expected_credits in test_cases:
            with self.subTest(plan_type=plan_type):
                # Mock successful session
                mock_session = MagicMock()
                mock_session.payment_status = "paid"
                mock_session.payment_intent = f"pi_test_{plan_type}_123"
                mock_session.amount_total = 2990
                mock_session.currency = "brl"

                with patch.object(self.service.stripe_service, 'retrieve_checkout_session', return_value={
                    "success": True,
                    "session": mock_session
                }):
                    # Mock no existing payment
                    with patch.object(self.service.payment_db, 'get_by_filters', return_value=[]):
                        # Mock successful payment creation
                        mock_payment = {
                            "id": f"payment_{plan_type}_123",
                            "user_id": self.test_user_id,
                            "amount": 2990,
                            "status": "succeeded"
                        }
                        with patch.object(self.service.payment_db, 'create', return_value=mock_payment):
                            result = await self.service.verify_and_activate_credits(
                                f"cs_test_{plan_type}_123",
                                self.test_user_id,
                                plan_type
                            )

                assert result["success"] is True
                assert result["plan_type"] == plan_type
                assert result["credits_activated"] == expected_credits

    @pytest.mark.asyncio
    async def test_verify_and_activate_credits_payment_creation_failure(self):
        """Test payment verification when payment record creation fails."""
        # Mock successful session retrieval
        mock_session = MagicMock()
        mock_session.payment_status = "paid"
        mock_session.payment_intent = "pi_test_1234567890"
        mock_session.amount_total = 2990
        mock_session.currency = "brl"

        with patch.object(self.service.stripe_service, 'retrieve_checkout_session', return_value={
            "success": True,
            "session": mock_session
        }):
            # Mock no existing payment
            with patch.object(self.service.payment_db, 'get_by_filters', return_value=[]):
                # Mock failed payment creation
                with patch.object(self.service.payment_db, 'create', return_value=None):
                    result = await self.service.verify_and_activate_credits(
                        self.test_session_id,
                        self.test_user_id,
                        "pro"
                    )

        assert result["success"] is False
        assert result["error"] == "Failed to record payment"

    @pytest.mark.asyncio
    async def test_verify_and_activate_credits_system_error(self):
        """Test payment verification with system error."""
        with patch.object(self.service.stripe_service, 'retrieve_checkout_session', side_effect=Exception("System error")):
            with pytest.raises(Exception, match="System error"):
                await self.service.verify_and_activate_credits(
                    self.test_session_id,
                    self.test_user_id,
                    "pro"
                )

    @pytest.mark.asyncio
    async def test_handle_checkout_completed_success(self):
        """Test handling checkout.session.completed webhook event."""
        # Mock event data
        event_data = {
            "object": {
                "id": self.test_session_id,
                "metadata": {
                    "user_id": self.test_user_id,
                    "plan": "pro"
                }
            }
        }

        # Mock successful verification
        with patch.object(self.service, 'verify_and_activate_credits', return_value={
            "success": True,
            "user_id": self.test_user_id,
            "plan_type": "pro",
            "payment_id": "payment_123",
            "credits_activated": 100
        }):
            result = await self.service.handle_checkout_completed(event_data)

        assert result["success"] is True
        assert result["user_id"] == self.test_user_id
        assert result["plan_type"] == "pro"
        assert result["payment_id"] == "payment_123"
        assert result["credits_activated"] == 100

    @pytest.mark.asyncio
    async def test_handle_checkout_completed_missing_user_id(self):
        """Test handling checkout completed event with missing user_id."""
        event_data = {
            "object": {
                "id": self.test_session_id,
                "metadata": {
                    "plan": "pro"
                    # Missing user_id
                }
            }
        }

        result = await self.service.handle_checkout_completed(event_data)

        assert result["success"] is False
        assert "Missing user_id" in result["error"]

    @pytest.mark.asyncio
    async def test_handle_checkout_completed_verification_failure(self):
        """Test handling checkout completed event when verification fails."""
        event_data = {
            "object": {
                "id": self.test_session_id,
                "metadata": {
                    "user_id": self.test_user_id,
                    "plan": "pro"
                }
            }
        }

        # Mock failed verification
        with patch.object(self.service, 'verify_and_activate_credits', return_value={
            "success": False,
            "error": "Payment not completed"
        }):
            result = await self.service.handle_checkout_completed(event_data)

        assert result["success"] is False
        assert result["error"] == "Payment not completed"

    @pytest.mark.asyncio
    async def test_handle_checkout_completed_system_error(self):
        """Test handling checkout completed event with system error."""
        event_data = {
            "object": {
                "id": self.test_session_id,
                "metadata": {
                    "user_id": self.test_user_id,
                    "plan": "pro"
                }
            }
        }

        # Mock system error
        with patch.object(self.service, 'verify_and_activate_credits', side_effect=Exception("System error")):
            result = await self.service.handle_checkout_completed(event_data)

        assert result["success"] is False
        assert result["error"] == "System error"

    @pytest.mark.asyncio
    async def test_handle_payment_intent_succeeded_success(self):
        """Test handling payment_intent.succeeded webhook event."""
        event_data = {
            "object": {
                "id": "pi_test_1234567890",
                "metadata": {
                    "user_id": self.test_user_id
                }
            }
        }

        result = await self.service.handle_payment_intent_succeeded(event_data)

        assert result["success"] is True
        assert result["user_id"] == self.test_user_id
        assert result["payment_intent_id"] == "pi_test_1234567890"

    @pytest.mark.asyncio
    async def test_handle_payment_intent_succeeded_missing_user_id(self):
        """Test handling payment intent succeeded with missing user_id."""
        event_data = {
            "object": {
                "id": "pi_test_1234567890",
                "metadata": {
                    # Missing user_id
                }
            }
        }

        result = await self.service.handle_payment_intent_succeeded(event_data)

        assert result["success"] is False
        assert "Missing user_id" in result["error"]

    @pytest.mark.asyncio
    async def test_handle_payment_intent_succeeded_system_error(self):
        """Test handling payment intent succeeded with system error."""
        event_data = {
            "object": {
                "id": "pi_test_1234567890",
                "metadata": {
                    "user_id": self.test_user_id
                }
            }
        }

        # Mock system error
        with patch.object(self.service, 'handle_payment_intent_succeeded', side_effect=Exception("System error")):
            result = await self.service.handle_payment_intent_succeeded(event_data)

        assert result["success"] is False
        assert result["error"] == "System error"

    @pytest.mark.asyncio
    async def test_handle_payment_failure(self):
        """Test handling payment failure."""
        error_message = "Card declined"

        # Mock failed payment creation
        mock_payment = {
            "id": "payment_failed_123",
            "user_id": self.test_user_id,
            "status": "failed"
        }
        with patch.object(self.service.payment_db, 'create', return_value=mock_payment):
            await self.service.handle_payment_failure(self.test_user_id, error_message)

        self.service.payment_db.create.assert_called_once()
        call_args = self.service.payment_db.create.call_args[0][0]
        assert call_args["user_id"] == self.test_user_id
        assert call_args["status"] == "failed"
        assert call_args["error_message"] == error_message
        assert "market" in call_args["metadata"]

    @pytest.mark.asyncio
    async def test_handle_payment_failure_database_error(self):
        """Test handling payment failure with database error."""
        error_message = "Card declined"

        # Mock database error
        with patch.object(self.service.payment_db, 'create', side_effect=Exception("Database error")):
            # Should not raise exception, just log error
            await self.service.handle_payment_failure(self.test_user_id, error_message)

    @pytest.mark.asyncio
    async def test_verify_payment_status_success(self):
        """Test payment status verification for successful payment."""
        # Mock successful session
        mock_session = MagicMock()
        mock_session.payment_status = "paid"
        mock_session.amount_total = 2990
        mock_session.currency = "brl"
        mock_session.status = "complete"
        mock_session.created = 1704067200

        with patch.object(self.service.stripe_service, 'retrieve_checkout_session', return_value={
            "success": True,
            "session": mock_session
        }):
            # Mock no existing payment
            with patch.object(self.service.payment_db, 'get_by_filters', return_value=[]):
                result = await self.service.verify_payment_status(self.test_session_id)

        assert result["success"] is True
        assert result["payment_status"] == "paid"
        assert result["amount_total"] == 2990
        assert result["currency"] == "brl"
        assert result["already_processed"] is False
        assert result["session"]["id"] == self.test_session_id
        assert result["session"]["status"] == "complete"

    @pytest.mark.asyncio
    async def test_verify_payment_status_already_processed(self):
        """Test payment status verification for already processed payment."""
        # Mock successful session
        mock_session = MagicMock()
        mock_session.payment_status = "paid"
        mock_session.amount_total = 2990
        mock_session.currency = "brl"

        with patch.object(self.service.stripe_service, 'retrieve_checkout_session', return_value={
            "success": True,
            "session": mock_session
        }):
            # Mock existing payment
            existing_payment = {
                "id": "payment_existing_123",
                "user_id": self.test_user_id,
                "stripe_checkout_session_id": self.test_session_id
            }
            with patch.object(self.service.payment_db, 'get_by_filters', return_value=[existing_payment]):
                result = await self.service.verify_payment_status(self.test_session_id)

        assert result["success"] is True
        assert result["already_processed"] is True

    @pytest.mark.asyncio
    async def test_verify_payment_status_invalid_session(self):
        """Test payment status verification with invalid session."""
        with patch.object(self.service.stripe_service, 'retrieve_checkout_session', return_value={
            "success": False,
            "error": "Invalid session"
        }):
            result = await self.service.verify_payment_status(self.test_session_id)

        assert result["success"] is False
        assert result["error"] == "Invalid session"

    @pytest.mark.asyncio
    async def test_verify_payment_status_system_error(self):
        """Test payment status verification with system error."""
        with patch.object(self.service.stripe_service, 'retrieve_checkout_session', side_effect=Exception("System error")):
            result = await self.service.verify_payment_status(self.test_session_id)

        assert result["success"] is False
        assert result["error"] == "System error"

    @pytest.mark.asyncio
    async def test_get_user_payment_history_success(self):
        """Test getting user payment history."""
        # Mock payment history
        mock_payments = [
            {
                "id": "payment_1",
                "user_id": self.test_user_id,
                "amount": 2990,
                "currency": "brl",
                "status": "succeeded",
                "created_at": datetime.now(UTC).isoformat()
            },
            {
                "id": "payment_2",
                "user_id": self.test_user_id,
                "amount": 9990,
                "currency": "brl",
                "status": "succeeded",
                "created_at": datetime.now(UTC).isoformat()
            }
        ]

        with patch.object(self.service.payment_db, 'get_by_filters', return_value=mock_payments):
            result = await self.service.get_user_payment_history(self.test_user_id)

        assert result["success"] is True
        assert result["payments"] == mock_payments
        assert result["total_count"] == 2

    @pytest.mark.asyncio
    async def test_get_user_payment_history_with_limit(self):
        """Test getting user payment history with limit."""
        # Mock payment history
        mock_payments = [
            {"id": f"payment_{i}", "user_id": self.test_user_id}
            for i in range(10)
        ]

        with patch.object(self.service.payment_db, 'get_by_filters', return_value=mock_payments[:5]):
            result = await self.service.get_user_payment_history(self.test_user_id, limit=5)

        assert result["success"] is True
        assert len(result["payments"]) == 5
        assert result["total_count"] == 5

    @pytest.mark.asyncio
    async def test_get_user_payment_history_no_payments(self):
        """Test getting payment history for user with no payments."""
        with patch.object(self.service.payment_db, 'get_by_filters', return_value=[]):
            result = await self.service.get_user_payment_history(self.test_user_id)

        assert result["success"] is True
        assert result["payments"] == []
        assert result["total_count"] == 0

    @pytest.mark.asyncio
    async def test_get_user_payment_history_database_error(self):
        """Test getting payment history with database error."""
        with patch.object(self.service.payment_db, 'get_by_filters', side_effect=Exception("Database error")):
            result = await self.service.get_user_payment_history(self.test_user_id)

        assert result["success"] is False
        assert result["error"] == "Database error"

    def test_get_credits_for_plan_all_plans(self):
        """Test getting credits for all plan types."""
        test_cases = [
            ("free", 5),
            ("pro", 100),
            ("enterprise", 500),
            ("lifetime", 1000),
            ("unknown", 0),  # Unknown plan returns 0
        ]

        for plan_type, expected_credits in test_cases:
            with self.subTest(plan_type=plan_type):
                credits = self.service._get_credits_for_plan(plan_type)
                assert credits == expected_credits

    def test_global_service_instance(self):
        """Test global payment verification service instance."""
        assert payment_verification_service is not None
        assert isinstance(payment_verification_service, PaymentVerificationService)

    @pytest.mark.asyncio
    async def test_brazilian_market_metadata(self):
        """Test Brazilian market metadata is properly included."""
        # Mock successful session
        mock_session = MagicMock()
        mock_session.payment_status = "paid"
        mock_session.payment_intent = "pi_test_brazil_123"
        mock_session.amount_total = 2990
        mock_session.currency = "brl"

        with patch.object(self.service.stripe_service, 'retrieve_checkout_session', return_value={
            "success": True,
            "session": mock_session
        }):
            # Mock no existing payment
            with patch.object(self.service.payment_db, 'get_by_filters', return_value=[]):
                # Mock successful payment creation
                mock_payment = {
                    "id": "payment_brazil_123",
                    "user_id": self.test_user_id,
                    "amount": 2990,
                    "status": "succeeded"
                }
                with patch.object(self.service.payment_db, 'create', return_value=mock_payment) as mock_create:
                    await self.service.verify_and_activate_credits(
                        "cs_test_brazil_123",
                        self.test_user_id,
                        "pro"
                    )

        # Verify Brazilian market metadata was included
        call_args = mock_create.call_args[0][0]
        assert call_args["payment_type"] == "subscription"
        assert call_args["description"] == "CV-Match Pro Plan"
        metadata = call_args["metadata"]
        assert metadata["plan_type"] == "pro"
        assert metadata["market"] == "brazil"
        assert metadata["language"] == "pt-br"

    @pytest.mark.asyncio
    async def test_subscription_vs_one_time_payment(self):
        """Test differentiation between subscription and one-time payments."""
        # Mock subscription session
        mock_subscription_session = MagicMock()
        mock_subscription_session.payment_status = "paid"
        mock_subscription_session.payment_intent = "pi_test_sub_123"
        mock_subscription_session.amount_total = 2990
        mock_subscription_session.currency = "brl"

        with patch.object(self.service.stripe_service, 'retrieve_checkout_session', return_value={
            "success": True,
            "session": mock_subscription_session
        }):
            with patch.object(self.service.payment_db, 'get_by_filters', return_value=[]):
                mock_payment = {
                    "id": "payment_sub_123",
                    "user_id": self.test_user_id,
                    "amount": 2990,
                    "status": "succeeded"
                }
                with patch.object(self.service.payment_db, 'create', return_value=mock_payment) as mock_create:
                    result = await self.service.verify_and_activate_credits(
                        "cs_test_sub_123",
                        self.test_user_id,
                        "pro"  # This creates a subscription
                    )

        assert result["success"] is True
        call_args = mock_create.call_args[0][0]
        assert call_args["payment_type"] == "subscription"

        # Mock one-time payment session (lifetime plan)
        mock_lifetime_session = MagicMock()
        mock_lifetime_session.payment_status = "paid"
        mock_lifetime_session.payment_intent = "pi_test_lifetime_123"
        mock_lifetime_session.amount_total = 29700  # R$ 297,00
        mock_lifetime_session.currency = "brl"

        with patch.object(self.service.stripe_service, 'retrieve_checkout_session', return_value={
            "success": True,
            "session": mock_lifetime_session
        }):
            with patch.object(self.service.payment_db, 'get_by_filters', return_value=[]):
                mock_payment = {
                    "id": "payment_lifetime_123",
                    "user_id": self.test_user_id,
                    "amount": 29700,
                    "status": "succeeded"
                }
                with patch.object(self.service.payment_db, 'create', return_value=mock_payment) as mock_create:
                    result = await self.service.verify_and_activate_credits(
                        "cs_test_lifetime_123",
                        self.test_user_id,
                        "lifetime"  # This creates a one-time payment
                    )

        assert result["success"] is True
        call_args = mock_create.call_args[0][0]
        assert call_args["payment_type"] == "one_time"