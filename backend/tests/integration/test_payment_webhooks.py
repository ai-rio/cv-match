"""
Comprehensive integration tests for payment webhooks.
Tests Stripe webhook handling for the CV-Match Brazilian market SaaS.
"""

import json
from datetime import UTC, datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient

from tests.fixtures.webhook_fixtures import (
    BrazilianWebhookFixtures,
    MockDataGenerator,
    WebhookFixtureGenerator,
    WebhookSignatureGenerator,
)


@pytest.mark.integration
@pytest.mark.webhook
@pytest.mark.stripe
class TestPaymentWebhooks:
    """Test payment webhook processing."""

    def setup_method(self):
        """Set up test method."""
        self.fixture_generator = WebhookFixtureGenerator()
        self.signature_generator = WebhookSignatureGenerator()
        self.brazilian_fixtures = BrazilianWebhookFixtures()
        self.mock_generator = MockDataGenerator()

    @pytest.mark.asyncio
    async def test_checkout_session_completed_webhook_success(
        self,
        async_client: AsyncClient,
        sample_checkout_session: dict,
        webhook_headers: dict,
        mock_supabase: AsyncMock
    ):
        """Test successful checkout.session.completed webhook processing."""
        # Create webhook event
        webhook_event = self.fixture_generator.create_checkout_session_completed_event(
            session_data=sample_checkout_session
        )

        # Generate payload and signature
        payload = json.dumps(webhook_event, separators=(',', ':'))
        headers = self.signature_generator.generate_headers(payload)

        # Mock database responses
        mock_user = self.mock_generator.create_mock_user(
            id=sample_checkout_session["metadata"]["user_id"],
            email="test@example.com",
            stripe_customer_id=sample_checkout_session["customer"]
        )
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_user]
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "payment_123"}
        ]

        # Mock existing webhook event check
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

        with patch('app.api.endpoints.webhooks.supabase', mock_supabase):
            with patch('app.services.stripe_service.stripe.Webhook.construct_event') as mock_verify:
                mock_verify.return_value = webhook_event

                response = await async_client.post(
                    "/api/webhooks/stripe",
                    data=payload,
                    headers=headers
                )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["success"] is True
        assert "processed" in response_data

        # Verify database calls
        mock_supabase.table.assert_any_call("stripe_webhook_events")
        mock_supabase.table.assert_any_call("payment_history")
        mock_supabase.table.assert_any_call("users")

    @pytest.mark.asyncio
    async def test_checkout_session_completed_brazilian_market(
        self,
        async_client: AsyncClient,
        webhook_headers: dict,
        mock_supabase: AsyncMock
    ):
        """Test checkout.session.completed for Brazilian market."""
        # Create Brazilian checkout session
        brazilian_session = self.brazilian_fixtures.create_brazilian_checkout_session(
            user_id="user_brazilian_123",
            plan_type="pro"
        )

        # Create webhook event
        webhook_event = self.fixture_generator.create_checkout_session_completed_event(
            session_data=brazilian_session
        )

        # Generate payload and signature
        payload = json.dumps(webhook_event, separators=(',', ':'))
        headers = self.signature_generator.generate_headers(payload)

        # Mock Brazilian user
        mock_user = self.mock_generator.create_mock_user(
            id="user_brazilian_123",
            email="usuario@exemplo.com.br",
            name="João Silva",
            stripe_customer_id=brazilian_session["customer"]
        )
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_user]
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "payment_brazilian_123"}
        ]

        # Mock existing webhook event check
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

        with patch('app.api.endpoints.webhooks.supabase', mock_supabase):
            with patch('app.services.stripe_service.stripe.Webhook.construct_event') as mock_verify:
                mock_verify.return_value = webhook_event

                response = await async_client.post(
                    "/api/webhooks/stripe",
                    data=payload,
                    headers=headers
                )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["success"] is True

        # Verify Brazilian metadata processing
        mock_supabase.table.assert_any_call("payment_history")

    @pytest.mark.asyncio
    async def test_invoice_payment_succeeded_webhook(
        self,
        async_client: AsyncClient,
        sample_invoice: dict,
        webhook_headers: dict,
        mock_supabase: AsyncMock
    ):
        """Test invoice.payment_succeeded webhook processing."""
        # Create webhook event
        webhook_event = self.fixture_generator.create_invoice_payment_succeeded_event(
            invoice_data=sample_invoice
        )

        # Generate payload and signature
        payload = json.dumps(webhook_event, separators=(',', ':'))
        headers = self.signature_generator.generate_headers(payload)

        # Mock subscription lookup
        mock_subscription = self.mock_generator.create_mock_subscription(
            stripe_subscription_id=sample_invoice["subscription"],
            user_id=sample_invoice["metadata"]["user_id"]
        )
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_subscription]
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "payment_history_123"}
        ]

        # Mock existing webhook event check
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

        with patch('app.api.endpoints.webhooks.supabase', mock_supabase):
            with patch('app.services.stripe_service.stripe.Webhook.construct_event') as mock_verify:
                mock_verify.return_value = webhook_event

                response = await async_client.post(
                    "/api/webhooks/stripe",
                    data=payload,
                    headers=headers
                )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["success"] is True

    @pytest.mark.asyncio
    async def test_invoice_payment_failed_webhook(
        self,
        async_client: AsyncClient,
        sample_invoice: dict,
        webhook_headers: dict,
        mock_supabase: AsyncMock
    ):
        """Test invoice.payment_failed webhook processing."""
        # Create failed invoice
        failed_invoice = sample_invoice.copy()
        failed_invoice["status"] = "open"
        failed_invoice["payment_intent"] = None
        failed_invoice["amount_paid"] = 0

        # Create webhook event
        webhook_event = self.fixture_generator.create_invoice_payment_failed_event(
            invoice_data=failed_invoice
        )

        # Generate payload and signature
        payload = json.dumps(webhook_event, separators=(',', ':'))
        headers = self.signature_generator.generate_headers(payload)

        # Mock subscription lookup
        mock_subscription = self.mock_generator.create_mock_subscription(
            stripe_subscription_id=failed_invoice["subscription"],
            user_id=failed_invoice["metadata"]["user_id"]
        )
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_subscription]

        # Mock existing webhook event check
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

        with patch('app.api.endpoints.webhooks.supabase', mock_supabase):
            with patch('app.services.stripe_service.stripe.Webhook.construct_event') as mock_verify:
                mock_verify.return_value = webhook_event

                response = await async_client.post(
                    "/api/webhooks/stripe",
                    data=payload,
                    headers=headers
                )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["success"] is True

    @pytest.mark.asyncio
    async def test_customer_subscription_created_webhook(
        self,
        async_client: AsyncClient,
        sample_subscription: dict,
        webhook_headers: dict,
        mock_supabase: AsyncMock
    ):
        """Test customer.subscription.created webhook processing."""
        # Create webhook event
        webhook_event = self.fixture_generator.create_customer_subscription_created_event(
            subscription_data=sample_subscription
        )

        # Generate payload and signature
        payload = json.dumps(webhook_event, separators=(',', ':'))
        headers = self.signature_generator.generate_headers(payload)

        # Mock user lookup
        mock_user = self.mock_generator.create_mock_user(
            id=sample_subscription["metadata"]["user_id"],
            stripe_customer_id=sample_subscription["customer"]
        )
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_user]
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "subscription_123"}
        ]

        # Mock existing webhook event check
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

        with patch('app.api.endpoints.webhooks.supabase', mock_supabase):
            with patch('app.services.stripe_service.stripe.Webhook.construct_event') as mock_verify:
                mock_verify.return_value = webhook_event

                response = await async_client.post(
                    "/api/webhooks/stripe",
                    data=payload,
                    headers=headers
                )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["success"] is True

    @pytest.mark.asyncio
    async def test_customer_subscription_updated_webhook(
        self,
        async_client: AsyncClient,
        sample_subscription: dict,
        webhook_headers: dict,
        mock_supabase: AsyncMock
    ):
        """Test customer.subscription.updated webhook processing."""
        # Create updated subscription
        updated_subscription = sample_subscription.copy()
        updated_subscription["status"] = "past_due"

        # Create webhook event
        webhook_event = self.fixture_generator.create_customer_subscription_updated_event(
            subscription_data=updated_subscription
        )

        # Generate payload and signature
        payload = json.dumps(webhook_event, separators=(',', ':'))
        headers = self.signature_generator.generate_headers(payload)

        # Mock existing subscription lookup
        mock_subscription = self.mock_generator.create_mock_subscription(
            stripe_subscription_id=updated_subscription["id"],
            user_id=updated_subscription["metadata"]["user_id"]
        )
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_subscription]
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [mock_subscription]

        # Mock existing webhook event check
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

        with patch('app.api.endpoints.webhooks.supabase', mock_supabase):
            with patch('app.services.stripe_service.stripe.Webhook.construct_event') as mock_verify:
                mock_verify.return_value = webhook_event

                response = await async_client.post(
                    "/api/webhooks/stripe",
                    data=payload,
                    headers=headers
                )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["success"] is True

    @pytest.mark.asyncio
    async def test_customer_subscription_deleted_webhook(
        self,
        async_client: AsyncClient,
        sample_subscription: dict,
        webhook_headers: dict,
        mock_supabase: AsyncMock
    ):
        """Test customer.subscription.deleted webhook processing."""
        # Create deleted subscription
        deleted_subscription = sample_subscription.copy()
        deleted_subscription["status"] = "canceled"
        deleted_subscription["canceled_at"] = int(datetime.now(UTC).timestamp())

        # Create webhook event
        webhook_event = self.fixture_generator.create_customer_subscription_deleted_event(
            subscription_data=deleted_subscription
        )

        # Generate payload and signature
        payload = json.dumps(webhook_event, separators=(',', ':'))
        headers = self.signature_generator.generate_headers(payload)

        # Mock existing subscription lookup
        mock_subscription = self.mock_generator.create_mock_subscription(
            stripe_subscription_id=deleted_subscription["id"],
            user_id=deleted_subscription["metadata"]["user_id"]
        )
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_subscription]
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [mock_subscription]

        # Mock existing webhook event check
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

        with patch('app.api.endpoints.webhooks.supabase', mock_supabase):
            with patch('app.services.stripe_service.stripe.Webhook.construct_event') as mock_verify:
                mock_verify.return_value = webhook_event

                response = await async_client.post(
                    "/api/webhooks/stripe",
                    data=payload,
                    headers=headers
                )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["success"] is True

    @pytest.mark.asyncio
    async def test_webhook_signature_verification_failure(
        self,
        async_client: AsyncClient,
        sample_checkout_session: dict,
        webhook_headers: dict
    ):
        """Test webhook signature verification failure."""
        # Create webhook event
        webhook_event = self.fixture_generator.create_checkout_session_completed_event(
            session_data=sample_checkout_session
        )

        # Generate payload with invalid signature
        payload = json.dumps(webhook_event, separators=(',', ':'))
        headers = {
            "stripe-signature": "invalid_signature",
            "content-type": "application/json",
        }

        with patch('app.services.stripe_service.stripe.Webhook.construct_event') as mock_verify:
            mock_verify.side_effect = Exception("Invalid signature")

            response = await async_client.post(
                "/api/webhooks/stripe",
                data=payload,
                headers=headers
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_webhook_idempotency_protection(
        self,
        async_client: AsyncClient,
        sample_checkout_session: dict,
        webhook_headers: dict,
        mock_supabase: AsyncMock
    ):
        """Test webhook idempotency protection."""
        # Create webhook event
        webhook_event = self.fixture_generator.create_checkout_session_completed_event(
            session_data=sample_checkout_session
        )

        # Generate payload and signature
        payload = json.dumps(webhook_event, separators=(',', ':'))
        headers = self.signature_generator.generate_headers(payload)

        # Mock existing processed webhook event
        mock_webhook_event = self.mock_generator.create_mock_webhook_event(
            stripe_event_id=webhook_event["id"],
            processed=True
        )
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [mock_webhook_event]

        with patch('app.api.endpoints.webhooks.supabase', mock_supabase):
            with patch('app.services.stripe_service.stripe.Webhook.construct_event') as mock_verify:
                mock_verify.return_value = webhook_event

                response = await async_client.post(
                    "/api/webhooks/stripe",
                    data=payload,
                    headers=headers
                )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["success"] is True
        assert "already processed" in response_data.get("message", "").lower()

    @pytest.mark.asyncio
    async def test_webhook_processing_error_handling(
        self,
        async_client: AsyncClient,
        sample_checkout_session: dict,
        webhook_headers: dict,
        mock_supabase: AsyncMock
    ):
        """Test webhook processing error handling."""
        # Create webhook event
        webhook_event = self.fixture_generator.create_checkout_session_completed_event(
            session_data=sample_checkout_session
        )

        # Generate payload and signature
        payload = json.dumps(webhook_event, separators=(',', ':'))
        headers = self.signature_generator.generate_headers(payload)

        # Mock user lookup to raise an exception
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception("Database error")

        with patch('app.api.endpoints.webhooks.supabase', mock_supabase):
            with patch('app.services.stripe_service.stripe.Webhook.construct_event') as mock_verify:
                mock_verify.return_value = webhook_event

                response = await async_client.post(
                    "/api/webhooks/stripe",
                    data=payload,
                    headers=headers
                )

        # Should still return 200 to acknowledge receipt, but with error logged
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_webhook_missing_user_handling(
        self,
        async_client: AsyncClient,
        sample_checkout_session: dict,
        webhook_headers: dict,
        mock_supabase: AsyncMock
    ):
        """Test webhook handling when user is not found."""
        # Create webhook event
        webhook_event = self.fixture_generator.create_checkout_session_completed_event(
            session_data=sample_checkout_session
        )

        # Generate payload and signature
        payload = json.dumps(webhook_event, separators=(',', ':'))
        headers = self.signature_generator.generate_headers(payload)

        # Mock user lookup to return empty
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

        # Mock existing webhook event check
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

        with patch('app.api.endpoints.webhooks.supabase', mock_supabase):
            with patch('app.services.stripe_service.stripe.Webhook.construct_event') as mock_verify:
                mock_verify.return_value = webhook_event

                response = await async_client.post(
                    "/api/webhooks/stripe",
                    data=payload,
                    headers=headers
                )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["success"] is True

    @pytest.mark.asyncio
    async def test_webhook_unsupported_event_type(
        self,
        async_client: AsyncClient,
        sample_checkout_session: dict,
        webhook_headers: dict,
        mock_supabase: AsyncMock
    ):
        """Test webhook handling of unsupported event types."""
        # Create webhook event with unsupported type
        webhook_event = self.fixture_generator.create_checkout_session_completed_event(
            session_data=sample_checkout_session
        )
        webhook_event["type"] = "account.updated"  # Unsupported event type

        # Generate payload and signature
        payload = json.dumps(webhook_event, separators=(',', ':'))
        headers = self.signature_generator.generate_headers(payload)

        # Mock existing webhook event check
        mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

        with patch('app.api.endpoints.webhooks.supabase', mock_supabase):
            with patch('app.services.stripe_service.stripe.Webhook.construct_event') as mock_verify:
                mock_verify.return_value = webhook_event

                response = await async_client.post(
                    "/api/webhooks/stripe",
                    data=payload,
                    headers=headers
                )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["success"] is True
        assert "not handled" in response_data.get("message", "").lower()

    @pytest.mark.asyncio
    async def test_webhook_invalid_json_payload(
        self,
        async_client: AsyncClient,
        webhook_headers: dict
    ):
        """Test webhook handling of invalid JSON payload."""
        invalid_payload = "{ invalid json }"
        headers = self.signature_generator.generate_headers(invalid_payload)

        response = await async_client.post(
            "/api/webhooks/stripe",
            data=invalid_payload,
            headers=headers
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_webhook_missing_signature_header(
        self,
        async_client: AsyncClient,
        sample_checkout_session: dict
    ):
        """Test webhook handling of missing signature header."""
        webhook_event = self.fixture_generator.create_checkout_session_completed_event(
            session_data=sample_checkout_session
        )
        payload = json.dumps(webhook_event, separators=(',', ':'))

        headers = {
            "content-type": "application/json",
        }

        response = await async_client.post(
            "/api/webhooks/stripe",
            data=payload,
            headers=headers
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
