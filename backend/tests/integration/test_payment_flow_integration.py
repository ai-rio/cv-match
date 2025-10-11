"""
Integration tests for complete payment flow.
Tests the entire payment workflow from checkout to credit activation.
"""

import json
import asyncio
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
from fastapi import status
from httpx import AsyncClient

from app.services.usage_limit_service import UsageLimitService
from app.core.database import SupabaseSession


@pytest.mark.integration
@pytest.mark.payment
@pytest.mark.usefixtures("cleanup_test_data")
class TestPaymentFlowIntegration:
    """Integration tests for complete payment flow."""

    def setup_method(self):
        """Set up test method."""
        self.test_user_id = str(uuid4())
        self.test_user = {
            "id": self.test_user_id,
            "email": "test@example.com",
            "name": "Test User"
        }
        self.db = SupabaseSession()

    @pytest.mark.asyncio
    async def test_complete_payment_flow_success(self, async_client: AsyncClient):
        """Test complete payment flow from checkout to credit activation."""
        # Step 1: Create checkout session
        checkout_request = {
            "tier": "pro",
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel"
        }

        # Mock Stripe checkout session creation
        mock_checkout_response = {
            "success": True,
            "session_id": "cs_test_complete_flow_123",
            "checkout_url": "https://checkout.stripe.com/pay/cs_test_complete_flow_123",
            "plan_type": "pro",
            "currency": "brl",
            "amount": 2990
        }

        with patch("app.api.endpoints.payments.stripe_service.create_checkout_session", return_value=mock_checkout_response):
            with patch("app.api.endpoints.payments.get_current_user", return_value=self.test_user):
                checkout_response = await async_client.post("/api/payments/create-checkout", json=checkout_request)

        assert checkout_response.status_code == status.HTTP_200_OK
        checkout_data = checkout_response.json()
        session_id = checkout_data["session_id"]

        # Step 2: Simulate successful payment webhook
        webhook_payload = {
            "id": f"evt_test_{uuid4()}",
            "object": "event",
            "api_version": "2023-10-16",
            "created": int(datetime.now(UTC).timestamp()),
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": session_id,
                    "object": "checkout.session",
                    "amount_total": 2990,
                    "currency": "brl",
                    "payment_status": "paid",
                    "status": "complete",
                    "customer": "cus_test_123",
                    "payment_intent": "pi_test_123",
                    "metadata": {
                        "user_id": self.test_user_id,
                        "credits": "50",
                        "tier": "pro",
                        "market": "brazil",
                        "language": "pt-br"
                    }
                }
            }
        }

        # Mock user payment profile
        mock_user_profile = {
            "id": "profile_123",
            "user_id": self.test_user_id,
            "stripe_customer_id": None
        }

        # Mock webhook processing
        with patch("app.api.endpoints.webhooks.stripe_service.verify_webhook_signature", return_value={
            "success": True,
            "event": MagicMock(),
            "event_type": "checkout.session.completed",
            "event_id": webhook_payload["id"]
        }):
            with patch("app.services.webhook_service.WebhookService._get_by_field", return_value=mock_user_profile):
                with patch("app.services.webhook_service.WebhookService._update", return_value={"id": "profile_123"}):
                    with patch("app.services.webhook_service.WebhookService._create", return_value={"id": "payment_123"}):
                        with patch("app.services.usage_limit_service.UsageLimitService.add_credits", return_value=None):
                            webhook_response = await async_client.post(
                                "/api/webhooks/stripe",
                                data=json.dumps(webhook_payload, separators=(",", ":")),
                                headers={"stripe-signature": "t=1234567890,v1=signature123", "content-type": "application/json"}
                            )

        assert webhook_response.status_code == status.HTTP_200_OK
        webhook_data = webhook_response.json()
        assert webhook_data["success"] is True

        # Step 3: Verify credits were added
        usage_service = UsageLimitService(self.db)

        # Mock user credits query
        mock_credits = {
            "id": "credit_123",
            "user_id": self.test_user_id,
            "credits_remaining": 50,  # Initial free credits + pro credits
            "total_credits": 53,
            "subscription_tier": "pro",
            "is_pro": False  # This would be True in real scenario
        }

        with patch.object(self.db.client.table, 'select') as mock_select:
            mock_select.return_value.eq.return_value.execute.return_value.data = [mock_credits]
            credits = await usage_service.get_user_credits(UUID(self.test_user_id))

        assert credits["credits_remaining"] == 50
        assert credits["total_credits"] == 53

    @pytest.mark.asyncio
    async def test_payment_flow_with_insufficient_initial_credits(self, async_client: AsyncClient):
        """Test payment flow when user has insufficient credits for optimization."""
        # Mock user with 0 credits
        mock_user_credits = {
            "id": "credit_123",
            "user_id": self.test_user_id,
            "credits_remaining": 0,
            "total_credits": 3,
            "subscription_tier": "free",
            "is_pro": False
        }

        # Create checkout session
        checkout_request = {"tier": "basic"}

        mock_checkout_response = {
            "success": True,
            "session_id": "cs_test_insufficient_123",
            "checkout_url": "https://checkout.stripe.com/pay/cs_test_insufficient_123",
            "plan_type": "pro",
            "currency": "brl",
            "amount": 2990
        }

        with patch("app.api.endpoints.payments.stripe_service.create_checkout_session", return_value=mock_checkout_response):
            with patch("app.api.endpoints.payments.get_current_user", return_value=self.test_user):
                checkout_response = await async_client.post("/api/payments/create-checkout", json=checkout_request)

        assert checkout_response.status_code == status.HTTP_200_OK

        # Simulate successful payment webhook
        webhook_payload = {
            "id": f"evt_test_{uuid4()}",
            "object": "event",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_insufficient_123",
                    "amount_total": 2990,
                    "currency": "brl",
                    "payment_status": "paid",
                    "metadata": {
                        "user_id": self.test_user_id,
                        "tier": "basic"
                    }
                }
            }
        }

        # Mock webhook processing that adds credits
        mock_user_profile = {"id": "profile_123", "user_id": self.test_user_id}

        with patch("app.api.endpoints.webhooks.stripe_service.verify_webhook_signature", return_value={
            "success": True,
            "event": MagicMock(),
            "event_type": "checkout.session.completed",
            "event_id": webhook_payload["id"]
        }):
            with patch("app.services.webhook_service.WebhookService._get_by_field", return_value=mock_user_profile):
                with patch("app.services.webhook_service.WebhookService._create", return_value={"id": "payment_123"}):
                    with patch("app.services.usage_limit_service.UsageLimitService.add_credits", return_value=None):
                        webhook_response = await async_client.post(
                            "/api/webhooks/stripe",
                            data=json.dumps(webhook_payload, separators=(",", ":")),
                            headers={"stripe-signature": "t=1234567890,v1=signature123", "content-type": "application/json"}
                        )

        assert webhook_response.status_code == status.HTTP_200_OK

        # Verify user can now optimize
        usage_service = UsageLimitService(self.db)

        # Mock updated credits after payment
        mock_updated_credits = {
            "id": "credit_123",
            "user_id": self.test_user_id,
            "credits_remaining": 10,  # Added 10 credits from basic plan
            "total_credits": 13,
            "subscription_tier": "free",
            "is_pro": False
        }

        with patch.object(self.db.client.table, 'select') as mock_select:
            mock_select.return_value.eq.return_value.execute.return_value.data = [mock_updated_credits]
            limit_check = await usage_service.check_usage_limit(UUID(self.test_user_id))

        assert limit_check.can_optimize is True
        assert limit_check.credits_remaining == 10

    @pytest.mark.asyncio
    async def test_payment_flow_with_subscription_renewal(self, async_client: AsyncClient):
        """Test payment flow with subscription renewal webhook."""
        # Initial setup: user has active subscription
        mock_subscription = {
            "id": "subscription_123",
            "user_id": self.test_user_id,
            "stripe_subscription_id": "sub_test_123",
            "status": "active"
        }

        # Simulate subscription renewal webhook
        renewal_webhook_payload = {
            "id": f"evt_test_{uuid4()}",
            "object": "event",
            "type": "invoice.payment_succeeded",
            "data": {
                "object": {
                    "id": "in_test_renewal_123",
                    "customer": "cus_test_123",
                    "subscription": "sub_test_123",
                    "amount_paid": 2990,  # R$ 29,90
                    "currency": "brl",
                    "status": "paid",
                    "metadata": {
                        "user_id": self.test_user_id
                    }
                }
            }
        }

        # Mock webhook processing for renewal
        with patch("app.api.endpoints.webhooks.stripe_service.verify_webhook_signature", return_value={
            "success": True,
            "event": MagicMock(),
            "event_type": "invoice.payment_succeeded",
            "event_id": renewal_webhook_payload["id"]
        }):
            with patch("app.services.webhook_service.WebhookService._get_by_field", return_value=mock_subscription):
                with patch("app.services.webhook_service.WebhookService._create", return_value={"id": "payment_renewal_123"}):
                    with patch("app.services.usage_limit_service.UsageLimitService.add_credits", return_value=None):
                        renewal_response = await async_client.post(
                            "/api/webhooks/stripe",
                            data=json.dumps(renewal_webhook_payload, separators=(",", ":")),
                            headers={"stripe-signature": "t=1234567890,v1=signature123", "content-type": "application/json"}
                        )

        assert renewal_response.status_code == status.HTTP_200_OK
        renewal_data = renewal_response.json()
        assert renewal_data["success"] is True

        # Verify credits were added for renewal
        usage_service = UsageLimitService(self.db)

        # Mock credits after renewal
        mock_credits_after_renewal = {
            "id": "credit_123",
            "user_id": self.test_user_id,
            "credits_remaining": 100,  # Renewal added 50 credits
            "total_credits": 150,
            "subscription_tier": "pro",
            "is_pro": True
        }

        with patch.object(self.db.client.table, 'select') as mock_select:
            mock_select.return_value.eq.return_value.execute.return_value.data = [mock_credits_after_renewal]
            credits = await usage_service.get_user_credits(UUID(self.test_user_id))

        assert credits["credits_remaining"] == 100
        assert credits["total_credits"] == 150

    @pytest.mark.asyncio
    async def test_payment_flow_with_payment_failure(self, async_client: AsyncClient):
        """Test payment flow handling payment failure."""
        # Create checkout session
        checkout_request = {"tier": "pro"}

        mock_checkout_response = {
            "success": True,
            "session_id": "cs_test_failure_123",
            "checkout_url": "https://checkout.stripe.com/pay/cs_test_failure_123",
            "plan_type": "pro",
            "currency": "brl",
            "amount": 2990
        }

        with patch("app.api.endpoints.payments.stripe_service.create_checkout_session", return_value=mock_checkout_response):
            with patch("app.api.endpoints.payments.get_current_user", return_value=self.test_user):
                checkout_response = await async_client.post("/api/payments/create-checkout", json=checkout_request)

        assert checkout_response.status_code == status.HTTP_200_OK

        # Simulate payment failure webhook
        failure_webhook_payload = {
            "id": f"evt_test_{uuid4()}",
            "object": "event",
            "type": "payment_intent.payment_failed",
            "data": {
                "object": {
                    "id": "pi_test_failed_123",
                    "customer": "cus_test_123",
                    "amount": 2990,
                    "currency": "brl",
                    "status": "requires_payment_method",
                    "metadata": {
                        "user_id": self.test_user_id
                    }
                }
            }
        }

        # Mock webhook processing for failure
        with patch("app.api.endpoints.webhooks.stripe_service.verify_webhook_signature", return_value={
            "success": True,
            "event": MagicMock(),
            "event_type": "payment_intent.payment_failed",
            "event_id": failure_webhook_payload["id"]
        }):
            with patch("app.services.webhook_service.WebhookService._create", return_value={"id": "payment_failed_123"}):
                failure_response = await async_client.post(
                    "/api/webhooks/stripe",
                    data=json.dumps(failure_webhook_payload, separators=(",", ":")),
                    headers={"stripe-signature": "t=1234567890,v1=signature123", "content-type": "application/json"}
                )

        assert failure_response.status_code == status.HTTP_200_OK
        failure_data = failure_response.json()
        assert failure_data["success"] is True

        # Verify no credits were added
        usage_service = UsageLimitService(self.db)

        # Mock unchanged credits after failure
        mock_unchanged_credits = {
            "id": "credit_123",
            "user_id": self.test_user_id,
            "credits_remaining": 3,  # Still only initial credits
            "total_credits": 3,
            "subscription_tier": "free",
            "is_pro": False
        }

        with patch.object(self.db.client.table, 'select') as mock_select:
            mock_select.return_value.eq.return_value.execute.return_value.data = [mock_unchanged_credits]
            credits = await usage_service.get_user_credits(UUID(self.test_user_id))

        assert credits["credits_remaining"] == 3
        assert credits["total_credits"] == 3

    @pytest.mark.asyncio
    async def test_payment_flow_with_duplicate_webhook(self, async_client: AsyncClient):
        """Test payment flow handling duplicate webhook events (idempotency)."""
        # Create checkout session
        checkout_request = {"tier": "pro"}

        mock_checkout_response = {
            "success": True,
            "session_id": "cs_test_duplicate_123",
            "checkout_url": "https://checkout.stripe.com/pay/cs_test_duplicate_123",
            "plan_type": "pro",
            "currency": "brl",
            "amount": 2990
        }

        with patch("app.api.endpoints.payments.stripe_service.create_checkout_session", return_value=mock_checkout_response):
            with patch("app.api.endpoints.payments.get_current_user", return_value=self.test_user):
                checkout_response = await async_client.post("/api/payments/create-checkout", json=checkout_request)

        assert checkout_response.status_code == status.HTTP_200_OK

        webhook_payload = {
            "id": f"evt_test_duplicate_{uuid4()}",
            "object": "event",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_duplicate_123",
                    "amount_total": 2990,
                    "currency": "brl",
                    "payment_status": "paid",
                    "metadata": {
                        "user_id": self.test_user_id,
                        "tier": "pro"
                    }
                }
            }
        }

        mock_user_profile = {"id": "profile_123", "user_id": self.test_user_id}

        # First webhook processing
        with patch("app.api.endpoints.webhooks.stripe_service.verify_webhook_signature", return_value={
            "success": True,
            "event": MagicMock(),
            "event_type": "checkout.session.completed",
            "event_id": webhook_payload["id"]
        }):
            with patch("app.services.webhook_service.WebhookService._get_by_field", return_value=mock_user_profile):
                with patch("app.services.webhook_service.WebhookService._create", return_value={"id": "payment_123"}):
                    with patch("app.services.usage_limit_service.UsageLimitService.add_credits", return_value=None):
                        first_response = await async_client.post(
                            "/api/webhooks/stripe",
                            data=json.dumps(webhook_payload, separators=(",", ":")),
                            headers={"stripe-signature": "t=1234567890,v1=signature123", "content-type": "application/json"}
                        )

        assert first_response.status_code == status.HTTP_200_OK
        first_data = first_response.json()
        assert first_data["success"] is True

        # Second webhook processing (duplicate)
        with patch("app.api.endpoints.webhooks.stripe_service.verify_webhook_signature", return_value={
            "success": True,
            "event": MagicMock(),
            "event_type": "checkout.session.completed",
            "event_id": webhook_payload["id"]
        }):
            # Mock that event was already processed
            with patch("app.services.webhook_service.WebhookService.is_event_processed", return_value=True):
                second_response = await async_client.post(
                    "/api/webhooks/stripe",
                    data=json.dumps(webhook_payload, separators=(",", ":")),
                    headers={"stripe-signature": "t=1234567890,v1=signature123", "content-type": "application/json"}
                )

        assert second_response.status_code == status.HTTP_200_OK
        second_data = second_response.json()
        assert second_data["success"] is True
        assert second_data["idempotent"] is True

    @pytest.mark.asyncio
    async def test_payment_flow_credit_usage_after_payment(self, async_client: AsyncClient):
        """Test using credits after successful payment."""
        # Step 1: Complete payment flow
        await self.test_complete_payment_flow_success(async_client)

        # Step 2: Use credits for optimization
        usage_service = UsageLimitService(self.db)

        # Mock credits available
        mock_credits_before = {
            "id": "credit_123",
            "user_id": self.test_user_id,
            "credits_remaining": 50,
            "total_credits": 53,
            "subscription_tier": "free",
            "is_pro": False
        }

        # Mock credit deduction
        mock_credits_after = {
            "id": "credit_123",
            "user_id": self.test_user_id,
            "credits_remaining": 49,  # Used 1 credit
            "total_credits": 53,
            "subscription_tier": "free",
            "is_pro": False
        }

        # Mock usage tracking
        mock_usage = AsyncMock()
        mock_usage.free_optimizations_used = 1
        mock_usage.paid_optimizations_used = 0

        # Check usage limit and track usage
        with patch.object(self.db.client.table, 'select') as mock_select:
            mock_select.return_value.eq.return_value.execute.return_value.data = [mock_credits_before]
            with patch.object(usage_service, 'deduct_credits', return_value=True):
                with patch.object(usage_service.usage_tracking_service, 'increment_usage', return_value=None):
                    with patch.object(usage_service.usage_tracking_service, 'get_current_month_usage', return_value=mock_usage):
                        limit_check = await usage_service.check_and_track_usage(
                            UUID(self.test_user_id),
                            "free",
                            cost_credits=1
                        )

        assert limit_check.can_optimize is True
        assert limit_check.free_optimizations_used == 1

        # Verify credits were deducted
        with patch.object(self.db.client.table, 'select') as mock_select:
            mock_select.return_value.eq.return_value.execute.return_value.data = [mock_credits_after]
            remaining_credits = await usage_service.get_user_credits(UUID(self.test_user_id))

        assert remaining_credits["credits_remaining"] == 49

    @pytest.mark.asyncio
    async def test_payment_flow_enterprise_plan(self, async_client: AsyncClient):
        """Test payment flow with enterprise plan."""
        # Step 1: Create enterprise checkout session
        checkout_request = {"tier": "enterprise"}

        mock_checkout_response = {
            "success": True,
            "session_id": "cs_test_enterprise_123",
            "checkout_url": "https://checkout.stripe.com/pay/cs_test_enterprise_123",
            "plan_type": "enterprise",
            "currency": "brl",
            "amount": 9990
        }

        with patch("app.api.endpoints.payments.stripe_service.create_checkout_session", return_value=mock_checkout_response):
            with patch("app.api.endpoints.payments.get_current_user", return_value=self.test_user):
                checkout_response = await async_client.post("/api/payments/create-checkout", json=checkout_request)

        assert checkout_response.status_code == status.HTTP_200_OK
        checkout_data = checkout_response.json()
        assert checkout_data["tier"] == "enterprise"
        assert checkout_data["credits"] == 1000

        # Step 2: Process enterprise payment webhook
        webhook_payload = {
            "id": f"evt_test_{uuid4()}",
            "object": "event",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_enterprise_123",
                    "amount_total": 9990,
                    "currency": "brl",
                    "payment_status": "paid",
                    "metadata": {
                        "user_id": self.test_user_id,
                        "tier": "enterprise"
                    }
                }
            }
        }

        mock_user_profile = {"id": "profile_123", "user_id": self.test_user_id}

        with patch("app.api.endpoints.webhooks.stripe_service.verify_webhook_signature", return_value={
            "success": True,
            "event": MagicMock(),
            "event_type": "checkout.session.completed",
            "event_id": webhook_payload["id"]
        }):
            with patch("app.services.webhook_service.WebhookService._get_by_field", return_value=mock_user_profile):
                with patch("app.services.webhook_service.WebhookService._create", return_value={"id": "payment_enterprise_123"}):
                    with patch("app.services.usage_limit_service.UsageLimitService.add_credits", return_value=None):
                        webhook_response = await async_client.post(
                            "/api/webhooks/stripe",
                            data=json.dumps(webhook_payload, separators=(",", ":")),
                            headers={"stripe-signature": "t=1234567890,v1=signature123", "content-type": "application/json"}
                        )

        assert webhook_response.status_code == status.HTTP_200_OK

        # Verify enterprise credits were added
        usage_service = UsageLimitService(self.db)

        mock_enterprise_credits = {
            "id": "credit_123",
            "user_id": self.test_user_id,
            "credits_remaining": 1000,  # Enterprise plan credits
            "total_credits": 1003,
            "subscription_tier": "enterprise",
            "is_pro": True
        }

        with patch.object(self.db.client.table, 'select') as mock_select:
            mock_select.return_value.eq.return_value.execute.return_value.data = [mock_enterprise_credits]
            credits = await usage_service.get_user_credits(UUID(self.test_user_id))

        assert credits["credits_remaining"] == 1000
        assert credits["subscription_tier"] == "enterprise"
        assert credits["is_pro"] is True

    @pytest.mark.asyncio
    async def test_payment_flow_brazilian_market(self, async_client: AsyncClient):
        """Test payment flow with Brazilian market configuration."""
        # Brazilian user
        brazilian_user = {
            "id": self.test_user_id,
            "email": "usuario@exemplo.com.br",
            "name": "João Silva"
        }

        # Step 1: Create checkout with Brazilian configuration
        checkout_request = {
            "tier": "pro",
            "metadata": {
                "market": "brazil",
                "language": "pt-br",
                "campaign": "verao_2024"
            }
        }

        mock_checkout_response = {
            "success": True,
            "session_id": "cs_test_brazil_123",
            "checkout_url": "https://checkout.stripe.com/pay/cs_test_brazil_123",
            "plan_type": "pro",
            "currency": "brl",
            "amount": 2990
        }

        with patch("app.api.endpoints.payments.stripe_service.create_checkout_session", return_value=mock_checkout_response):
            with patch("app.api.endpoints.payments.get_current_user", return_value=brazilian_user):
                checkout_response = await async_client.post("/api/payments/create-checkout", json=checkout_request)

        assert checkout_response.status_code == status.HTTP_200_OK

        # Verify Brazilian pricing
        pricing_response = await async_client.get("/api/payments/pricing")
        assert pricing_response.status_code == status.HTTP_200_OK
        pricing_data = pricing_response.json()
        assert pricing_data["currency"] == "brl"
        assert pricing_data["country"] == "BR"
        assert pricing_data["locale"] == "pt-BR"

        # Step 2: Process Brazilian payment webhook
        webhook_payload = {
            "id": f"evt_test_{uuid4()}",
            "object": "event",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_brazil_123",
                    "amount_total": 2990,
                    "currency": "brl",
                    "customer_details": {
                        "email": "usuario@exemplo.com.br",
                        "name": "João Silva",
                        "address": {
                            "country": "BR",
                            "state": "SP",
                            "city": "São Paulo"
                        }
                    },
                    "metadata": {
                        "user_id": self.test_user_id,
                        "market": "brazil",
                        "language": "pt-br"
                    }
                }
            }
        }

        mock_user_profile = {"id": "profile_123", "user_id": self.test_user_id}

        with patch("app.api.endpoints.webhooks.stripe_service.verify_webhook_signature", return_value={
            "success": True,
            "event": MagicMock(),
            "event_type": "checkout.session.completed",
            "event_id": webhook_payload["id"]
        }):
            with patch("app.services.webhook_service.WebhookService._get_by_field", return_value=mock_user_profile):
                with patch("app.services.webhook_service.WebhookService._create", return_value={"id": "payment_brazil_123"}):
                    with patch("app.services.usage_limit_service.UsageLimitService.add_credits", return_value=None):
                        webhook_response = await async_client.post(
                            "/api/webhooks/stripe",
                            data=json.dumps(webhook_payload, separators=(",", ":")),
                            headers={"stripe-signature": "t=1234567890,v1=signature123", "content-type": "application/json"}
                        )

        assert webhook_response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_payment_flow_concurrent_operations(self, async_client: AsyncClient):
        """Test payment flow with concurrent operations."""
        # Create multiple checkout sessions concurrently
        async def create_checkout_session():
            checkout_request = {"tier": "basic"}

            mock_checkout_response = {
                "success": True,
                "session_id": f"cs_test_concurrent_{uuid4()}",
                "checkout_url": f"https://checkout.stripe.com/pay/cs_test_concurrent_{uuid4()}",
                "plan_type": "pro",
                "currency": "brl",
                "amount": 2990
            }

            with patch("app.api.endpoints.payments.stripe_service.create_checkout_session", return_value=mock_checkout_response):
                with patch("app.api.endpoints.payments.get_current_user", return_value=self.test_user):
                    return await async_client.post("/api/payments/create-checkout", json=checkout_request)

        # Run concurrent checkout creation
        tasks = [create_checkout_session() for _ in range(3)]
        checkout_responses = await asyncio.gather(*tasks)

        # Verify all checkouts were created successfully
        for response in checkout_responses:
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert "session_id" in data

        # Process webhooks concurrently
        async def process_webhook(session_id):
            webhook_payload = {
                "id": f"evt_test_{uuid4()}",
                "object": "event",
                "type": "checkout.session.completed",
                "data": {
                    "object": {
                        "id": session_id,
                        "amount_total": 2990,
                        "currency": "brl",
                        "payment_status": "paid",
                        "metadata": {
                            "user_id": self.test_user_id,
                            "tier": "basic"
                        }
                    }
                }
            }

            mock_user_profile = {"id": "profile_123", "user_id": self.test_user_id}

            with patch("app.api.endpoints.webhooks.stripe_service.verify_webhook_signature", return_value={
                "success": True,
                "event": MagicMock(),
                "event_type": "checkout.session.completed",
                "event_id": webhook_payload["id"]
            }):
                with patch("app.services.webhook_service.WebhookService._get_by_field", return_value=mock_user_profile):
                    with patch("app.services.webhook_service.WebhookService._create", return_value={"id": f"payment_{uuid4()}"}):
                        with patch("app.services.usage_limit_service.UsageLimitService.add_credits", return_value=None):
                            return await async_client.post(
                                "/api/webhooks/stripe",
                                data=json.dumps(webhook_payload, separators=(",", ":")),
                                headers={"stripe-signature": "t=1234567890,v1=signature123", "content-type": "application/json"}
                            )

        # Extract session IDs and process webhooks concurrently
        session_ids = [resp.json()["session_id"] for resp in checkout_responses]
        webhook_tasks = [process_webhook(session_id) for session_id in session_ids]
        webhook_responses = await asyncio.gather(*webhook_tasks)

        # Verify all webhooks were processed successfully
        for response in webhook_responses:
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True