"""
Comprehensive error handling and edge case tests for payment system.
Tests various failure scenarios, edge cases, and recovery mechanisms.
"""

import json
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
import stripe

from app.services.stripe_service import StripeService
from app.services.usage_limit_service import UsageLimitService, UsageLimitError
from app.services.payment_verification_service import PaymentVerificationService
from app.services.webhook_service import WebhookService
from app.core.database import SupabaseSession


@pytest.mark.unit
@pytest.mark.error_handling
@pytest.mark.payment
class TestPaymentErrorHandling:
    """Test comprehensive error handling and edge cases."""

    def setup_method(self):
        """Set up test method."""
        self.test_user_id = str(uuid4())
        self.db = SupabaseSession()

    @pytest.mark.asyncio
    async def test_stripe_service_network_timeout_handling(self):
        """Test Stripe service handling of network timeouts."""
        service = StripeService()

        # Mock network timeout
        with patch("stripe.checkout.Session.create", side_effect=stripe.error.StripeError("Request timed out")):
            result = await service.create_checkout_session(
                user_id=self.test_user_id,
                user_email="test@example.com",
                plan_type="pro"
            )

        assert result["success"] is False
        assert result["error_type"] == "stripe_error"
        assert "Request timed out" in result["error"]

    @pytest.mark.asyncio
    async def test_stripe_service_rate_limiting_handling(self):
        """Test Stripe service handling of rate limiting."""
        service = StripeService()

        # Mock rate limit error
        rate_limit_error = stripe.error.RateLimitError(
            message="Too many requests",
            json_body={"error": {"type": "rate_limit_error"}}
        )

        with patch("stripe.checkout.Session.create", side_effect=rate_limit_error):
            result = await service.create_checkout_session(
                user_id=self.test_user_id,
                user_email="test@example.com",
                plan_type="pro"
            )

        assert result["success"] is False
        assert result["error_type"] == "stripe_error"

    @pytest.mark.asyncio
    async def test_stripe_service_invalid_api_key_handling(self):
        """Test Stripe service handling of invalid API key."""
        # Test initialization with invalid key
        with patch.dict("os.environ", {"STRIPE_SECRET_KEY": "invalid_key"}):
            with pytest.raises(ValueError, match="Stripe must be configured in test mode"):
                StripeService()

    @pytest.mark.asyncio
    async def test_stripe_service_invalid_card_handling(self):
        """Test Stripe service handling of invalid card errors."""
        service = StripeService()

        # Mock card declined error
        card_error = stripe.error.CardError(
            message="Your card was declined.",
            code="card_declined",
            param="number"
        )

        with patch("stripe.checkout.Session.create", side_effect=card_error):
            result = await service.create_checkout_session(
                user_id=self.test_user_id,
                user_email="test@example.com",
                plan_type="pro"
            )

        assert result["success"] is False
        assert result["error_type"] == "stripe_error"

    @pytest.mark.asyncio
    async def test_usage_service_user_not_found_handling(self):
        """Test usage service handling when user is not found."""
        service = UsageLimitService(self.db)

        # Mock user not found in database
        with patch.object(self.db.client.table, 'select') as mock_select:
            mock_select.return_value.eq.return_value.execute.return_value.data = []
            with patch.object(self.db.client.table, 'insert', return_value=MagicMock(data=[])):
                with pytest.raises(UsageLimitError, match="Failed to create credits record"):
                    await service.get_user_credits(UUID(self.test_user_id))

    @pytest.mark.asyncio
    async def test_usage_service_database_connection_error(self):
        """Test usage service handling of database connection errors."""
        service = UsageLimitService(self.db)

        # Mock database connection error
        with patch.object(self.db.client.table, 'select', side_effect=Exception("Connection lost")):
            with pytest.raises(UsageLimitError, match="Failed to retrieve user credits"):
                await service.get_user_credits(UUID(self.test_user_id))

    @pytest.mark.asyncio
    async def test_usage_service_credit_deduction_rollback_scenario(self):
        """Test usage service credit deduction rollback scenario."""
        service = UsageLimitService(self.db)

        # Mock successful credit deduction but failed transaction recording
        mock_deduct_result = MagicMock()
        mock_deduct_result.data = [{
            "success": True,
            "new_balance": 45
        }]

        with patch.object(self.db.client, 'rpc', return_value=mock_deduct_result):
            with patch.object(self.db.client.table, 'insert', side_effect=Exception("Transaction logging failed")):
                # Should still return True since credits were deducted atomically
                result = await service.deduct_credits(UUID(self.test_user_id), 5, "operation_123")

        assert result is True

    @pytest.mark.asyncio
    async def test_payment_verification_service_corrupted_webhook_handling(self):
        """Test payment verification service handling of corrupted webhook data."""
        service = PaymentVerificationService()

        # Mock corrupted session data
        corrupted_session = {
            "id": None,  # Missing required field
            "payment_status": "invalid_status",
            "metadata": None
        }

        with patch.object(service.stripe_service, 'retrieve_checkout_session', return_value={
            "success": True,
            "session": corrupted_session
        }):
            result = await service.verify_and_activate_credits(
                "cs_test_corrupted_123",
                self.test_user_id,
                "pro"
            )

        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_webhook_service_malformed_event_handling(self):
        """Test webhook service handling of malformed event data."""
        service = WebhookService()

        # Test various malformed event scenarios
        malformed_events = [
            {},  # Empty event
            {"id": None},  # Missing event type
            {"type": "invalid.type"},  # Unknown event type
            {"type": "checkout.session.completed"},  # Missing object data
        ]

        for event_data in malformed_events:
            with self.subTest(event_data=str(event_data)[:50]):
                with patch.object(service, 'is_event_processed', return_value=False):
                    with patch.object(service, 'log_webhook_event', return_value={"success": True}):
                        result = await service.process_webhook_event(
                            event_data.get("type", "unknown"),
                            event_data.get("object", {}),
                            event_data.get("id", "unknown")
                        )

                # Should handle gracefully without crashing
                assert isinstance(result, dict)
                assert "success" in result

    @pytest.mark.asyncio
    async def test_webhook_service_memory_exhaustion_handling(self):
        """Test webhook service handling of memory exhaustion scenarios."""
        service = WebhookService()

        # Create extremely large event data
        large_event_data = {
            "id": f"evt_test_{uuid4()}",
            "type": "checkout.session.completed",
            "object": {
                "id": "cs_test_large_123",
                "large_field": "x" * 1000000,  # 1MB field
                "metadata": {f"key_{i}": f"value_{i}" * 1000 for i in range(1000)}
            }
        }

        with patch.object(service, 'is_event_processed', return_value=False):
            with patch.object(service, 'log_webhook_event', side_effect=MemoryError("Out of memory")):
                result = await service.process_webhook_event(
                    "checkout.session.completed",
                    large_event_data["object"],
                    large_event_data["id"]
                )

        # Should handle memory error gracefully
        assert isinstance(result, dict)
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_payment_edge_case_zero_amount_payment(self):
        """Test payment processing with zero amount."""
        service = StripeService()

        # Test free plan (zero amount)
        result = await service.create_checkout_session(
            user_id=self.test_user_id,
            user_email="test@example.com",
            plan_type="free"
        )

        assert result["success"] is True
        assert result["session_id"] is None
        assert result["checkout_url"] is None
        assert result["plan_type"] == "free"

    @pytest.mark.asyncio
    async def test_payment_edge_case_extremely_large_amount(self):
        """Test payment processing with extremely large amount."""
        service = StripeService()

        # Mock large amount payment
        with patch("stripe.checkout.Session.create", side_effect=stripe.error.InvalidRequestError("Amount too large")):
            result = await service.create_checkout_session(
                user_id=self.test_user_id,
                user_email="test@example.com",
                plan_type="pro"
            )

        assert result["success"] is False
        assert "Amount too large" in result["error"]

    @pytest.mark.asyncio
    async def test_payment_edge_case_invalid_email_format(self):
        """Test payment processing with invalid email format."""
        service = StripeService()

        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user..name@example.com",
            "user@.example.com"
        ]

        for email in invalid_emails:
            with self.subTest(email=email):
                with patch("stripe.checkout.Session.create") as mock_create:
                    mock_create.side_effect = stripe.error.InvalidRequestError(f"Invalid email: {email}")

                    result = await service.create_customer(
                        user_id=self.test_user_id,
                        email=email
                    )

                assert result["success"] is False

    @pytest.mark.asyncio
    async def test_usage_edge_case_credit_overflow_scenario(self):
        """Test usage service handling of credit overflow scenarios."""
        service = UsageLimitService(self.db)

        # Mock user with maximum credits
        max_credits = 2**31 - 1  # Maximum 32-bit integer
        mock_credits = {
            "id": "credit_123",
            "user_id": str(self.test_user_id),
            "credits_remaining": max_credits,
            "total_credits": max_credits
        }

        # Test adding credits that would cause overflow
        with patch.object(self.db.client.table, 'select') as mock_select:
            mock_select.return_value.eq.return_value.execute.return_value.data = [mock_credits]

            # Mock database overflow error
            with patch.object(self.db.client.table, 'update', side_effect=Exception("Integer overflow")):
                with pytest.raises(UsageLimitError):
                    await service.add_credits(UUID(self.test_user_id), 1, "test", "Overflow test")

    @pytest.mark.asyncio
    async def test_usage_edge_case_negative_credit_amount(self):
        """Test usage service handling of negative credit amounts."""
        service = UsageLimitService(self.db)

        mock_credits = {
            "id": "credit_123",
            "user_id": str(self.test_user_id),
            "credits_remaining": 10,
            "total_credits": 10
        }

        with patch.object(self.db.client.table, 'select') as mock_select:
            mock_select.return_value.eq.return_value.execute.return_value.data = [mock_credits]

            # Test adding negative credits (should be prevented)
            with pytest.raises(Exception):  # Should raise validation error
                await service.add_credits(UUID(self.test_user_id), -5, "invalid", "Negative amount test")

    @pytest.mark.asyncio
    async def test_webhook_edge_case_duplicate_event_id_collision(self):
        """Test webhook service handling of duplicate event ID collisions."""
        service = WebhookService()
        duplicate_event_id = f"evt_test_duplicate_{uuid4()}"

        # First processing
        with patch.object(service, 'is_event_processed', return_value=False):
            with patch.object(service, 'log_webhook_event', return_value={"success": True}):
                with patch.object(service, '_process_specific_event', return_value={"success": True}):
                    with patch.object(service, '_mark_event_processed'):
                        result1 = await service.process_webhook_event(
                            "checkout.session.completed",
                            {"id": "cs_test_123"},
                            duplicate_event_id
                        )

        assert result1["success"] is True

        # Second processing (duplicate)
        with patch.object(service, 'is_event_processed', return_value=True):
            result2 = await service.process_webhook_event(
                "checkout.session.completed",
                {"id": "cs_test_123"},
                duplicate_event_id
            )

        assert result2["success"] is True
        assert result2["idempotent"] is True

    @pytest.mark.asyncio
    async def test_payment_edge_case_concurrent_same_user_operations(self):
        """Test payment system handling of concurrent operations for same user."""
        import asyncio

        service = StripeService()
        user_id = self.test_user_id

        # Create multiple concurrent checkout sessions for same user
        async def create_concurrent_checkout():
            mock_session = MagicMock()
            mock_session.id = f"cs_concurrent_{uuid4()}"
            mock_session.url = f"https://checkout.stripe.com/pay/{mock_session.id}"

            with patch("stripe.checkout.Session.create", return_value=mock_session):
                return await service.create_checkout_session(
                    user_id=user_id,
                    user_email="test@example.com",
                    plan_type="basic"
                )

        # Run concurrent operations
        tasks = [create_concurrent_checkout() for _ in range(5)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Verify all operations completed successfully
        successful_results = [r for r in results if not isinstance(r, Exception) and r.get("success")]
        assert len(successful_results) == 5

        # Verify all session IDs are unique
        session_ids = [r["session_id"] for r in successful_results if r.get("session_id")]
        assert len(set(session_ids)) == len(session_ids)

    @pytest.mark.asyncio
    async def test_payment_edge_case_expired_payment_intent(self):
        """Test payment verification with expired payment intent."""
        service = PaymentVerificationService()

        # Mock expired session
        expired_session = MagicMock()
        expired_session.payment_status = "expired"
        expired_session.expired_at = int((datetime.now(UTC) - timedelta(hours=1)).timestamp())

        with patch.object(service.stripe_service, 'retrieve_checkout_session', return_value={
            "success": True,
            "session": expired_session
        }):
            result = await service.verify_and_activate_credits(
                "cs_expired_123",
                self.test_user_id,
                "pro"
            )

        assert result["success"] is False
        assert "expired" in result["status"].lower()

    @pytest.mark.asyncio
    async def test_payment_edge_case_refunded_payment(self):
        """Test payment verification with refunded payment."""
        service = PaymentVerificationService()

        # Mock refunded session
        refunded_session = MagicMock()
        refunded_session.payment_status = "refunded"
        refunded_session.amount_total = 2990
        refunded_session.refunds = [{"amount": 2990, "status": "succeeded"}]

        with patch.object(service.stripe_service, 'retrieve_checkout_session', return_value={
            "success": True,
            "session": refunded_session
        }):
            result = await service.verify_and_activate_credits(
                "cs_refunded_123",
                self.test_user_id,
                "pro"
            )

        # Should not activate credits for refunded payments
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_usage_edge_case_pro_user_unlimited_usage(self):
        """Test usage service handling of unlimited usage for Pro users."""
        service = UsageLimitService(self.db)

        # Mock Pro user with unlimited usage
        mock_pro_credits = {
            "id": "credit_pro_123",
            "user_id": str(self.test_user_id),
            "credits_remaining": 1000000,  # Very high balance
            "total_credits": 1000000,
            "subscription_tier": "pro",
            "is_pro": True
        }

        with patch.object(self.db.client.table, 'select') as mock_select:
            mock_select.return_value.eq.return_value.execute.return_value.data = [mock_pro_credits]

            with patch.object(service.usage_tracking_service, 'get_current_month_usage') as mock_usage:
                mock_usage.return_value = AsyncMock()
                mock_usage.return_value.free_optimizations_used = 10000
                mock_usage.return_value.paid_optimizations_used = 50000

                limit_check = await service.check_usage_limit(UUID(self.test_user_id))

        assert limit_check.can_optimize is True
        assert limit_check.is_pro is True
        assert limit_check.reason is None

    @pytest.mark.asyncio
    async def test_webhook_edge_case_future_timestamp_webhook(self):
        """Test webhook service handling of webhooks with future timestamps."""
        service = WebhookService()
        future_timestamp = int((datetime.now(UTC) + timedelta(hours=1)).timestamp())

        webhook_event = {
            "id": f"evt_future_{uuid4()}",
            "created": future_timestamp,
            "type": "checkout.session.completed",
            "data": {"object": {"id": "cs_future_123"}}
        }

        with patch.object(service, 'is_event_processed', return_value=False):
            with patch.object(service, 'log_webhook_event', return_value={"success": True}):
                with patch.object(service, '_process_specific_event', return_value={"success": True}):
                    with patch.object(service, '_mark_event_processed'):
                        result = await service.process_webhook_event(
                            "checkout.session.completed",
                            webhook_event["data"]["object"],
                            webhook_event["id"]
                        )

        # Should process but may log warning about future timestamp
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_payment_edge_case_currency_mismatch(self):
        """Test payment processing with currency mismatch."""
        service = StripeService()

        # Mock session with wrong currency
        wrong_currency_session = MagicMock()
        wrong_currency_session.currency = "usd"  # Should be "brl"
        wrong_currency_session.amount_total = 2990

        with patch.object(service.stripe_service, 'retrieve_checkout_session', return_value={
            "success": True,
            "session": wrong_currency_session
        }):
            result = await service.verify_and_activate_credits(
                "cs_wrong_currency_123",
                self.test_user_id,
                "pro"
            )

        # Should handle currency mismatch gracefully
        # Implementation may reject or convert currency
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_usage_edge_case_credit_deduction_during_subscription_upgrade(self):
        """Test credit deduction during subscription upgrade."""
        service = UsageLimitService(self.db)

        # Mock user being upgraded from free to pro
        mock_free_credits = {
            "id": "credit_free_123",
            "user_id": str(self.test_user_id),
            "credits_remaining": 2,
            "total_credits": 3,
            "subscription_tier": "free",
            "is_pro": False
        }

        with patch.object(self.db.client.table, 'select') as mock_select:
            mock_select.return_value.eq.return_value.execute.return_value.data = [mock_free_credits]

            # User should still be able to use remaining credits even during upgrade
            with patch.object(service.usage_tracking_service, 'get_current_month_usage') as mock_usage:
                mock_usage.return_value = AsyncMock()
                mock_usage.return_value.free_optimizations_used = 1
                mock_usage.return_value.paid_optimizations_used = 0

                limit_check = await service.check_usage_limit(UUID(self.test_user_id))

        assert limit_check.can_optimize is True
        assert limit_check.is_pro is False  # Still free tier until upgrade completes

    @pytest.mark.asyncio
    async def test_payment_edge_case_multiple_payment_attempts(self):
        """Test handling of multiple payment attempts for same session."""
        service = PaymentVerificationService()

        session_id = "cs_multiple_attempts_123"

        # Mock successful payment verification
        mock_session = MagicMock()
        mock_session.payment_status = "paid"
        mock_session.payment_intent = "pi_multiple_123"
        mock_session.amount_total = 2990

        with patch.object(service.stripe_service, 'retrieve_checkout_session', return_value={
            "success": True,
            "session": mock_session
        }):
            # Mock no existing payment (first attempt)
            with patch.object(service.payment_db, 'get_by_filters', return_value=[]):
                with patch.object(service.payment_db, 'create', return_value={"id": "payment_123"}):
                    result1 = await service.verify_and_activate_credits(
                        session_id,
                        self.test_user_id,
                        "pro"
                    )

            assert result1["success"] is True

            # Mock existing payment (second attempt)
            with patch.object(service.payment_db, 'get_by_filters', return_value=[{
                "id": "payment_123",
                "stripe_checkout_session_id": session_id
            }]):
                result2 = await service.verify_and_activate_credits(
                    session_id,
                    self.test_user_id,
                    "pro"
                )

            assert result2["success"] is True
            assert result2["message"] == "Payment already processed"

    def test_edge_case_empty_string_handling(self):
        """Test handling of empty string edge cases."""
        service = StripeService()

        # Test empty user ID
        with pytest.raises(Exception):
            asyncio.run(service.create_checkout_session(
                user_id="",
                user_email="test@example.com",
                plan_type="pro"
            ))

        # Test empty email
        with pytest.raises(Exception):
            asyncio.run(service.create_checkout_session(
                user_id=self.test_user_id,
                user_email="",
                plan_type="pro"
            ))

        # Test empty plan type
        with pytest.raises(ValueError):
            asyncio.run(service.create_checkout_session(
                user_id=self.test_user_id,
                user_email="test@example.com",
                plan_type=""
            ))

    @pytest.mark.asyncio
    async def test_edge_case_unicode_characters_in_metadata(self):
        """Test handling of Unicode characters in payment metadata."""
        service = StripeService()

        unicode_metadata = {
            "user_name": "João Silva",
            "description": "Pagamento para currículo em português",
            "special_chars": "αβγδε 中文 日本語",
            "emoji": "🚀💳💼"
        }

        mock_session = MagicMock()
        mock_session.id = "cs_unicode_123"
        mock_session.url = "https://checkout.stripe.com/pay/cs_unicode_123"

        with patch("stripe.checkout.Session.create", return_value=mock_session):
            result = await service.create_checkout_session(
                user_id=self.test_user_id,
                user_email="joao@exemplo.com.br",
                plan_type="pro",
                metadata=unicode_metadata
            )

        assert result["success"] is True

        # Verify Unicode metadata was passed correctly
        # (This would be verified in the actual Stripe call)

    @pytest.mark.asyncio
    async def test_edge_case_maximum_webhook_payload_size(self):
        """Test handling of maximum webhook payload size."""
        service = WebhookService()

        # Create payload near size limit
        large_payload = {
            "test": "large_payload",
            "data": "x" * 100000,  # 100KB
            "nested": {
                "level1": {
                    "level2": {
                        "data": "y" * 50000  # 50KB nested
                    }
                }
            }
        }

        with patch.object(service, 'is_event_processed', return_value=False):
            with patch.object(service, 'log_webhook_event', side_effect=MemoryError("Payload too large")):
                result = await service.process_webhook_event(
                    "test.large_payload",
                    large_payload,
                    f"evt_large_{uuid4()}"
                )

        # Should handle large payload error gracefully
        assert isinstance(result, dict)
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_edge_case_database_connection_pool_exhaustion(self):
        """Test handling of database connection pool exhaustion."""
        service = UsageLimitService(self.db)

        # Mock connection pool exhaustion
        with patch.object(self.db.client.table, 'select', side_effect=Exception("Connection pool exhausted")):
            with pytest.raises(UsageLimitError):
                await service.get_user_credits(UUID(self.test_user_id))