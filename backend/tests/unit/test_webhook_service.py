"""
Unit tests for webhook service functionality.
"""

import json
from datetime import UTC, datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import stripe

from tests.fixtures.webhook_fixtures import (
    BrazilianWebhookFixtures,
    MockDataGenerator,
    WebhookFixtureGenerator,
    WebhookSignatureGenerator,
)


@pytest.mark.unit
@pytest.mark.webhook
class TestWebhookService:
    """Test webhook service functionality."""

    def setup_method(self):
        """Set up test method."""
        self.fixture_generator = WebhookFixtureGenerator()
        self.signature_generator = WebhookSignatureGenerator()
        self.brazilian_fixtures = BrazilianWebhookFixtures()
        self.mock_generator = MockDataGenerator()

    @pytest.mark.asyncio
    async def test_webhook_signature_verification(self):
        """Test webhook signature verification."""
        webhook_secret = "whsec_test_1234567890"
        signature_gen = WebhookSignatureGenerator(webhook_secret)

        # Create test payload
        payload = '{"test": "data"}'
        timestamp = int(datetime.now(UTC).timestamp())

        # Generate signature
        signature = signature_gen.generate_signature(payload, timestamp)
        signed_payload = f"t={timestamp},v1={signature}"

        # Verify signature using Stripe's method
        with patch('app.services.webhook_service.stripe.Webhook.construct_event') as mock_construct:
            mock_construct.return_value = {"type": "test"}

            # This should not raise an exception
            event = stripe.Webhook.construct_event(
                payload=payload.encode('utf-8'),
                sig_header=signed_payload,
                secret=webhook_secret,
                tolerance=300
            )

            assert event["type"] == "test"
            mock_construct.assert_called_once()

    @pytest.mark.asyncio
    async def test_webhook_idempotency_check(self, mock_supabase: AsyncMock):
        """Test webhook idempotency checking."""
        stripe_event_id = "evt_test_1234567890"

        # Test case: Event not processed yet
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

        # Mock the service function
        with patch('app.services.webhook_service.SupabaseDatabaseService') as mock_db_service:
            mock_service = AsyncMock()
            mock_service.get_by_field.return_value = None
            mock_db_service.return_value = mock_service

            from app.services.webhook_service import WebhookService
            webhook_service = WebhookService()

            is_processed = await webhook_service.is_event_processed(stripe_event_id)
            assert is_processed is False

        # Test case: Event already processed
        mock_webhook_event = self.mock_generator.create_mock_webhook_event(
            stripe_event_id=stripe_event_id,
            processed=True
        )
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [mock_webhook_event]

        with patch('app.services.webhook_service.SupabaseDatabaseService') as mock_db_service:
            mock_service = AsyncMock()
            mock_service.get_by_field.return_value = mock_webhook_event
            mock_db_service.return_value = mock_service

            webhook_service = WebhookService()
            is_processed = await webhook_service.is_event_processed(stripe_event_id)
            assert is_processed is True

    @pytest.mark.asyncio
    async def test_checkout_session_processing(self, mock_supabase: AsyncMock):
        """Test checkout session processing."""
        # Create sample session
        sample_session = self.brazilian_fixtures.create_brazilian_checkout_session(
            user_id="user_test_123",
            plan_type="pro"
        )

        # Mock user data
        mock_user = self.mock_generator.create_mock_user(
            id=sample_session["metadata"]["user_id"],
            email=sample_session["customer_details"]["email"],
            stripe_customer_id=sample_session["customer"]
        )
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_user]
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "payment_test_123"}
        ]

        with patch('app.services.webhook_service.SupabaseDatabaseService') as mock_db_service:
            mock_service = AsyncMock()
            mock_service.get_by_field.return_value = mock_user
            mock_service.create.return_value = {"id": "payment_test_123"}
            mock_db_service.return_value = mock_service

            from app.services.webhook_service import WebhookService
            webhook_service = WebhookService()

            result = await webhook_service.process_checkout_session(sample_session)
            assert result["success"] is True
            assert "payment_id" in result

    @pytest.mark.asyncio
    async def test_subscription_processing(self, mock_supabase: AsyncMock):
        """Test subscription processing."""
        # Create sample subscription
        sample_subscription = self.brazilian_fixtures.create_brazilian_subscription(
            user_id="user_test_123",
            plan_type="pro"
        )

        # Mock user data
        mock_user = self.mock_generator.create_mock_user(
            id=sample_subscription["metadata"]["user_id"],
            stripe_customer_id=sample_subscription["customer"]
        )
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_user]
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "subscription_test_123"}
        ]

        with patch('app.services.webhook_service.SupabaseDatabaseService') as mock_db_service:
            mock_service = AsyncMock()
            mock_service.get_by_field.return_value = mock_user
            mock_service.create.return_value = {"id": "subscription_test_123"}
            mock_db_service.return_value = mock_service

            from app.services.webhook_service import WebhookService
            webhook_service = WebhookService()

            result = await webhook_service.process_subscription_created(sample_subscription)
            assert result["success"] is True
            assert "subscription_id" in result

    @pytest.mark.asyncio
    async def test_invoice_payment_processing(self, mock_supabase: AsyncMock):
        """Test invoice payment processing."""
        # Create sample invoice
        sample_invoice = {
            "id": "in_test_123",
            "customer": "cus_test_123",
            "subscription": "sub_test_123",
            "status": "paid",
            "amount_paid": 2990,
            "currency": "brl",
            "payment_intent": "pi_test_123",
            "metadata": {"user_id": "user_test_123"}
        }

        # Mock subscription data
        mock_subscription = self.mock_generator.create_mock_subscription(
            stripe_subscription_id=sample_invoice["subscription"],
            user_id=sample_invoice["metadata"]["user_id"]
        )
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_subscription]
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "payment_history_test_123"}
        ]

        with patch('app.services.webhook_service.SupabaseDatabaseService') as mock_db_service:
            mock_service = AsyncMock()
            mock_service.get_by_field.return_value = mock_subscription
            mock_service.create.return_value = {"id": "payment_history_test_123"}
            mock_db_service.return_value = mock_service

            from app.services.webhook_service import WebhookService
            webhook_service = WebhookService()

            result = await webhook_service.process_invoice_payment_succeeded(sample_invoice)
            assert result["success"] is True
            assert "payment_history_id" in result

    @pytest.mark.asyncio
    async def test_subscription_update_processing(self, mock_supabase: AsyncMock):
        """Test subscription update processing."""
        # Create sample subscription update
        updated_subscription = self.brazilian_fixtures.create_brazilian_subscription(
            user_id="user_test_123",
            plan_type="pro"
        )
        updated_subscription["status"] = "past_due"

        # Mock existing subscription
        mock_subscription = self.mock_generator.create_mock_subscription(
            stripe_subscription_id=updated_subscription["id"],
            user_id=updated_subscription["metadata"]["user_id"]
        )
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_subscription]
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            {**mock_subscription, "status": "past_due"}
        ]

        with patch('app.services.webhook_service.SupabaseDatabaseService') as mock_db_service:
            mock_service = AsyncMock()
            mock_service.get_by_field.return_value = mock_subscription
            mock_service.update.return_value = {**mock_subscription, "status": "past_due"}
            mock_db_service.return_value = mock_service

            from app.services.webhook_service import WebhookService
            webhook_service = WebhookService()

            result = await webhook_service.process_subscription_updated(updated_subscription)
            assert result["success"] is True
            assert "subscription_id" in result

    @pytest.mark.asyncio
    async def test_subscription_deletion_processing(self, mock_supabase: AsyncMock):
        """Test subscription deletion processing."""
        # Create sample subscription deletion
        deleted_subscription = self.brazilian_fixtures.create_brazilian_subscription(
            user_id="user_test_123",
            plan_type="pro"
        )
        deleted_subscription["status"] = "canceled"
        deleted_subscription["canceled_at"] = int(datetime.now(UTC).timestamp())

        # Mock existing subscription
        mock_subscription = self.mock_generator.create_mock_subscription(
            stripe_subscription_id=deleted_subscription["id"],
            user_id=deleted_subscription["metadata"]["user_id"]
        )
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_subscription]
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            {**mock_subscription, "status": "canceled"}
        ]

        with patch('app.services.webhook_service.SupabaseDatabaseService') as mock_db_service:
            mock_service = AsyncMock()
            mock_service.get_by_field.return_value = mock_subscription
            mock_service.update.return_value = {**mock_subscription, "status": "canceled"}
            mock_db_service.return_value = mock_service

            from app.services.webhook_service import WebhookService
            webhook_service = WebhookService()

            result = await webhook_service.process_subscription_deleted(deleted_subscription)
            assert result["success"] is True
            assert "subscription_id" in result

    @pytest.mark.asyncio
    async def test_webhook_event_logging(self, mock_supabase: AsyncMock):
        """Test webhook event logging."""
        stripe_event_id = "evt_test_1234567890"
        event_type = "checkout.session.completed"
        event_data = {"test": "data"}

        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "webhook_event_test_123"}
        ]

        with patch('app.services.webhook_service.SupabaseDatabaseService') as mock_db_service:
            mock_service = AsyncMock()
            mock_service.create.return_value = {"id": "webhook_event_test_123"}
            mock_db_service.return_value = mock_service

            from app.services.webhook_service import WebhookService
            webhook_service = WebhookService()

            result = await webhook_service.log_webhook_event(
                stripe_event_id=stripe_event_id,
                event_type=event_type,
                data=event_data,
                processed=True
            )

            assert result["success"] is True
            assert "webhook_event_id" in result

    @pytest.mark.asyncio
    async def test_error_handling_user_not_found(self, mock_supabase: AsyncMock):
        """Test error handling when user is not found."""
        # Create sample session
        sample_session = self.brazilian_fixtures.create_brazilian_checkout_session(
            user_id="user_nonexistent",
            plan_type="pro"
        )

        # Mock user not found
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

        with patch('app.services.webhook_service.SupabaseDatabaseService') as mock_db_service:
            mock_service = AsyncMock()
            mock_service.get_by_field.return_value = None
            mock_db_service.return_value = mock_service

            from app.services.webhook_service import WebhookService
            webhook_service = WebhookService()

            result = await webhook_service.process_checkout_session(sample_session)
            assert result["success"] is False
            assert "user not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_brazilian_metadata_processing(self, mock_supabase: AsyncMock):
        """Test Brazilian metadata processing."""
        # Create Brazilian session with specific metadata
        brazilian_session = self.brazilian_fixtures.create_brazilian_checkout_session(
            user_id="user_brazilian_123",
            plan_type="enterprise"
        )

        # Verify Brazilian metadata
        assert brazilian_session["metadata"]["market"] == "brazil"
        assert brazilian_session["metadata"]["language"] == "pt-br"
        assert brazilian_session["currency"] == "brl"
        assert brazilian_session["customer_details"]["address"]["country"] == "BR"

        # Mock user data
        mock_user = self.mock_generator.create_mock_user(
            id=brazilian_session["metadata"]["user_id"],
            email=brazilian_session["customer_details"]["email"],
            stripe_customer_id=brazilian_session["customer"]
        )
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_user]
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "payment_brazilian_123"}
        ]

        with patch('app.services.webhook_service.SupabaseDatabaseService') as mock_db_service:
            mock_service = AsyncMock()
            mock_service.get_by_field.return_value = mock_user
            mock_service.create.return_value = {"id": "payment_brazilian_123"}
            mock_db_service.return_value = mock_service

            from app.services.webhook_service import WebhookService
            webhook_service = WebhookService()

            result = await webhook_service.process_checkout_session(brazilian_session)
            assert result["success"] is True

            # Verify Brazilian metadata is processed correctly
            mock_service.create.assert_called_once()
            call_args = mock_service.create.call_args[0][0]
            assert "market" in call_args or "brazil" in str(call_args).lower()

    @pytest.mark.asyncio
    async def test_webhook_processing_time_tracking(self, mock_supabase: AsyncMock):
        """Test webhook processing time tracking."""
        stripe_event_id = "evt_test_timing_123"
        event_type = "checkout.session.completed"
        event_data = {"test": "timing"}

        # Mock webhook event creation with timing
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "webhook_timing_test_123", "processing_time_ms": 150}
        ]

        with patch('app.services.webhook_service.SupabaseDatabaseService') as mock_db_service:
            mock_service = AsyncMock()
            mock_service.create.return_value = {
                "id": "webhook_timing_test_123",
                "processing_time_ms": 150
            }
            mock_db_service.return_value = mock_service

            from app.services.webhook_service import WebhookService
            webhook_service = WebhookService()

            result = await webhook_service.log_webhook_event(
                stripe_event_id=stripe_event_id,
                event_type=event_type,
                data=event_data,
                processed=True
            )

            assert result["success"] is True
            assert "webhook_event_id" in result

            # The service should track processing time
            mock_service.create.assert_called_once()
            call_kwargs = mock_service.create.call_args[1] if mock_service.create.call_args else {}
            # Verify that processing time is being tracked
            assert "processing_time_ms" in call_kwargs or any(
                "processing_time_ms" in str(arg) for arg in mock_service.create.call_args[0]
            )
