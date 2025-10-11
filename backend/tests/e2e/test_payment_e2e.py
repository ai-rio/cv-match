"""
End-to-end tests for complete payment workflow.
Tests the full user journey from browsing to payment to credit usage.
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


@pytest.mark.e2e
@pytest.mark.payment
@pytest.mark.usefixtures("cleanup_test_data")
class TestPaymentE2E:
    """End-to-end tests for payment workflow."""

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
    async def test_full_user_journey_free_to_paid(self, async_client: AsyncClient):
        """Complete user journey from free tier to paid subscription."""

        # Step 1: User starts with free tier (3 credits)
        print("Step 1: User starts with free tier")

        # Mock initial free user credits
        mock_free_credits = {
            "id": "credit_free_123",
            "user_id": self.test_user_id,
            "credits_remaining": 3,
            "total_credits": 3,
            "subscription_tier": "free",
            "is_pro": False
        }

        usage_service = UsageLimitService(self.db)

        with patch.object(self.db.client.table, 'select') as mock_select:
            mock_select.return_value.eq.return_value.execute.return_value.data = [mock_free_credits]
            initial_credits = await usage_service.get_user_credits(UUID(self.test_user_id))

        assert initial_credits["credits_remaining"] == 3
        assert initial_credits["subscription_tier"] == "free"
        assert initial_credits["is_pro"] is False

        # Step 2: User checks usage limits
        print("Step 2: User checks usage limits")

        with patch.object(self.db.client.table, 'select') as mock_select:
            mock_select.return_value.eq.return_value.execute.return_value.data = [mock_free_credits]
            with patch.object(usage_service.usage_tracking_service, 'get_current_month_usage') as mock_usage:
                mock_usage.return_value = AsyncMock()
                mock_usage.return_value.free_optimizations_used = 0
                mock_usage.return_value.paid_optimizations_used = 0

                limit_check = await usage_service.check_usage_limit(UUID(self.test_user_id))

        assert limit_check.can_optimize is True
        assert limit_check.free_optimizations_limit == 3
        assert limit_check.remaining_free_optimizations == 3

        # Step 3: User uses all free credits
        print("Step 3: User uses all free credits")

        for i in range(3):
            with patch.object(self.db.client.table, 'select') as mock_select:
                mock_select.return_value.eq.return_value.execute.return_value.data = [{
                    **mock_free_credits,
                    "credits_remaining": 3 - i - 1,
                    "total_credits": 3
                }]
                with patch.object(usage_service, 'deduct_credits', return_value=True):
                    with patch.object(usage_service.usage_tracking_service, 'increment_usage', return_value=None):
                        with patch.object(usage_service.usage_tracking_service, 'get_current_month_usage') as mock_usage:
                            mock_usage.return_value = AsyncMock()
                            mock_usage.return_value.free_optimizations_used = i + 1
                            mock_usage.return_value.paid_optimizations_used = 0

                            await usage_service.check_and_track_usage(
                                UUID(self.test_user_id),
                                "free",
                                cost_credits=1
                            )

        # Step 4: User has no credits left, decides to upgrade
        print("Step 4: User has no credits, decides to upgrade")

        # Check pricing options
        pricing_response = await async_client.get("/api/payments/pricing")
        assert pricing_response.status_code == status.HTTP_200_OK
        pricing_data = pricing_response.json()

        assert pricing_data["success"] is True
        assert "free" in pricing_data["pricing"]
        assert "pro" in pricing_data["pricing"]
        assert "enterprise" in pricing_data["pricing"]

        # Step 5: User creates checkout session for pro plan
        print("Step 5: User creates checkout session for pro plan")

        checkout_request = {
            "tier": "pro",
            "success_url": "https://cv-match.com/sucesso",
            "cancel_url": "https://cv-match.com/cancelar"
        }

        mock_checkout_response = {
            "success": True,
            "session_id": "cs_test_e2e_123",
            "checkout_url": "https://checkout.stripe.com/pay/cs_test_e2e_123",
            "plan_type": "pro",
            "currency": "brl",
            "amount": 2990
        }

        with patch("app.api.endpoints.payments.stripe_service.create_checkout_session", return_value=mock_checkout_response):
            with patch("app.api.endpoints.payments.get_current_user", return_value=self.test_user):
                checkout_response = await async_client.post("/api/payments/create-checkout", json=checkout_request)

        assert checkout_response.status_code == status.HTTP_200_OK
        checkout_data = checkout_response.json()

        assert checkout_data["success"] is True
        assert checkout_data["tier"] == "pro"
        assert checkout_data["credits"] == 50
        assert checkout_data["currency"] == "brl"
        assert checkout_data["amount"] == 2990

        # Step 6: User completes payment via Stripe
        print("Step 6: User completes payment via Stripe")

        webhook_payload = {
            "id": f"evt_test_{uuid4()}",
            "object": "event",
            "api_version": "2023-10-16",
            "created": int(datetime.now(UTC).timestamp()),
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_e2e_123",
                    "object": "checkout.session",
                    "amount_total": 2990,
                    "currency": "brl",
                    "payment_status": "paid",
                    "status": "complete",
                    "customer": "cus_test_e2e_123",
                    "payment_intent": "pi_test_e2e_123",
                    "success_url": "https://cv-match.com/sucesso",
                    "cancel_url": "https://cv-match.com/cancelar",
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

        # Mock webhook processing
        mock_user_profile = {"id": "profile_e2e_123", "user_id": self.test_user_id, "stripe_customer_id": None}

        with patch("app.api.endpoints.webhooks.stripe_service.verify_webhook_signature", return_value={
            "success": True,
            "event": MagicMock(),
            "event_type": "checkout.session.completed",
            "event_id": webhook_payload["id"]
        }):
            with patch("app.services.webhook_service.WebhookService._get_by_field", return_value=mock_user_profile):
                with patch("app.services.webhook_service.WebhookService._update", return_value={"id": "profile_e2e_123"}):
                    with patch("app.services.webhook_service.WebhookService._create", return_value={"id": "payment_e2e_123"}):
                        with patch("app.services.usage_limit_service.UsageLimitService.add_credits", return_value=None):
                            webhook_response = await async_client.post(
                                "/api/webhooks/stripe",
                                data=json.dumps(webhook_payload, separators=(",", ":")),
                                headers={"stripe-signature": "t=1234567890,v1=signature123", "content-type": "application/json"}
                            )

        assert webhook_response.status_code == status.HTTP_200_OK
        webhook_data = webhook_response.json()
        assert webhook_data["success"] is True

        # Step 7: User now has pro credits
        print("Step 7: User now has pro credits")

        mock_pro_credits = {
            "id": "credit_pro_123",
            "user_id": self.test_user_id,
            "credits_remaining": 50,  # Pro plan credits
            "total_credits": 53,  # 3 initial + 50 pro
            "subscription_tier": "pro",
            "is_pro": True
        }

        with patch.object(self.db.client.table, 'select') as mock_select:
            mock_select.return_value.eq.return_value.execute.return_value.data = [mock_pro_credits]
            updated_credits = await usage_service.get_user_credits(UUID(self.test_user_id))

        assert updated_credits["credits_remaining"] == 50
        assert updated_credits["total_credits"] == 53
        assert updated_credits["subscription_tier"] == "pro"
        assert updated_credits["is_pro"] is True

        # Step 8: User can now optimize with pro benefits
        print("Step 8: User can now optimize with pro benefits")

        with patch.object(self.db.client.table, 'select') as mock_select:
            mock_select.return_value.eq.return_value.execute.return_value.data = [mock_pro_credits]
            with patch.object(usage_service.usage_tracking_service, 'get_current_month_usage') as mock_usage:
                mock_usage.return_value = AsyncMock()
                mock_usage.return_value.free_optimizations_used = 3
                mock_usage.return_value.paid_optimizations_used = 0

                pro_limit_check = await usage_service.check_usage_limit(UUID(self.test_user_id))

        assert pro_limit_check.can_optimize is True
        assert pro_limit_check.is_pro is True
        assert pro_limit_check.reason is None
        assert pro_limit_check.upgrade_prompt is None

        # Step 9: User uses optimization services
        print("Step 9: User uses optimization services")

        # Pro users don't need credit deduction for basic usage
        with patch.object(self.db.client.table, 'select') as mock_select:
            mock_select.return_value.eq.return_value.execute.return_value.data = [mock_pro_credits]
            with patch.object(usage_service.usage_tracking_service, 'increment_usage', return_value=None):
                with patch.object(usage_service.usage_tracking_service, 'get_current_month_usage') as mock_usage:
                    mock_usage.return_value = AsyncMock()
                    mock_usage.return_value.free_optimizations_used = 4
                    mock_usage.return_value.paid_optimizations_used = 1

                    await usage_service.check_and_track_usage(
                        UUID(self.test_user_id),
                        "paid",
                        cost_credits=0  # Pro users don't pay
                    )

        # Step 10: Check payment history
        print("Step 10: Check payment history")

        with patch("app.services.payment_verification_service.payment_verification_service.payment_db.get_by_filters", return_value=[{
            "id": "payment_e2e_123",
            "user_id": self.test_user_id,
            "amount": 2990,
            "currency": "brl",
            "status": "succeeded",
            "payment_type": "subscription",
            "created_at": datetime.now(UTC).isoformat()
        }]):
            from app.services.payment_verification_service import payment_verification_service
            history = await payment_verification_service.get_user_payment_history(self.test_user_id)

        assert history["success"] is True
        assert history["total_count"] == 1
        assert history["payments"][0]["amount"] == 2990
        assert history["payments"][0]["status"] == "succeeded"

        print("✅ Full user journey completed successfully!")

    @pytest.mark.asyncio
    async def test_subscription_lifecycle_management(self, async_client: AsyncClient):
        """Test complete subscription lifecycle: creation, renewal, cancellation."""

        # Step 1: Create initial subscription
        print("Step 1: Create initial subscription")

        checkout_request = {"tier": "enterprise"}

        mock_checkout_response = {
            "success": True,
            "session_id": "cs_test_sub_123",
            "checkout_url": "https://checkout.stripe.com/pay/cs_test_sub_123",
            "plan_type": "enterprise",
            "currency": "brl",
            "amount": 9990
        }

        with patch("app.api.endpoints.payments.stripe_service.create_checkout_session", return_value=mock_checkout_response):
            with patch("app.api.endpoints.payments.get_current_user", return_value=self.test_user):
                checkout_response = await async_client.post("/api/payments/create-checkout", json=checkout_request)

        assert checkout_response.status_code == status.HTTP_200_OK

        # Step 2: Process subscription creation webhook
        print("Step 2: Process subscription creation webhook")

        subscription_webhook = {
            "id": f"evt_test_{uuid4()}",
            "object": "event",
            "type": "customer.subscription.created",
            "data": {
                "object": {
                    "id": "sub_test_lifecycle_123",
                    "customer": "cus_test_lifecycle_123",
                    "status": "active",
                    "current_period_start": int(datetime.now(UTC).timestamp()),
                    "current_period_end": int((datetime.now(UTC) + timedelta(days=30)).timestamp()),
                    "metadata": {
                        "user_id": self.test_user_id,
                        "plan": "enterprise"
                    }
                }
            }
        }

        mock_user_profile = {"id": "profile_lifecycle_123", "user_id": self.test_user_id}

        with patch("app.api.endpoints.webhooks.stripe_service.verify_webhook_signature", return_value={
            "success": True,
            "event": MagicMock(),
            "event_type": "customer.subscription.created",
            "event_id": subscription_webhook["id"]
        }):
            with patch("app.services.webhook_service.WebhookService._get_by_field", return_value=mock_user_profile):
                with patch("app.services.webhook_service.WebhookService._create_subscription_record", return_value={"id": "subscription_lifecycle_123"}):
                    webhook_response = await async_client.post(
                        "/api/webhooks/stripe",
                        data=json.dumps(subscription_webhook, separators=(",", ":")),
                        headers={"stripe-signature": "t=1234567890,v1=signature123", "content-type": "application/json"}
                    )

        assert webhook_response.status_code == status.HTTP_200_OK

        # Step 3: Process monthly renewal
        print("Step 3: Process monthly renewal")

        renewal_webhook = {
            "id": f"evt_test_{uuid4()}",
            "object": "event",
            "type": "invoice.payment_succeeded",
            "data": {
                "object": {
                    "id": "in_test_renewal_123",
                    "customer": "cus_test_lifecycle_123",
                    "subscription": "sub_test_lifecycle_123",
                    "amount_paid": 9990,
                    "currency": "brl",
                    "status": "paid",
                    "period_start": int(datetime.now(UTC).timestamp()),
                    "period_end": int((datetime.now(UTC) + timedelta(days=30)).timestamp()),
                    "metadata": {
                        "user_id": self.test_user_id
                    }
                }
            }
        }

        with patch("app.api.endpoints.webhooks.stripe_service.verify_webhook_signature", return_value={
            "success": True,
            "event": MagicMock(),
            "event_type": "invoice.payment_succeeded",
            "event_id": renewal_webhook["id"]
        }):
            with patch("app.services.webhook_service.WebhookService._get_by_field", return_value={
                "id": "subscription_lifecycle_123",
                "stripe_subscription_id": "sub_test_lifecycle_123",
                "user_id": self.test_user_id
            }):
                with patch("app.services.webhook_service.WebhookService._create", return_value={"id": "payment_renewal_123"}):
                    with patch("app.services.usage_limit_service.UsageLimitService.add_credits", return_value=None):
                        renewal_response = await async_client.post(
                            "/api/webhooks/stripe",
                            data=json.dumps(renewal_webhook, separators=(",", ":")),
                            headers={"stripe-signature": "t=1234567890,v1=signature123", "content-type": "application/json"}
                        )

        assert renewal_response.status_code == status.HTTP_200_OK

        # Step 4: Process subscription update (e.g., plan change)
        print("Step 4: Process subscription update")

        update_webhook = {
            "id": f"evt_test_{uuid4()}",
            "object": "event",
            "type": "customer.subscription.updated",
            "data": {
                "object": {
                    "id": "sub_test_lifecycle_123",
                    "status": "active",
                    "current_period_start": int(datetime.now(UTC).timestamp()),
                    "current_period_end": int((datetime.now(UTC) + timedelta(days=30)).timestamp()),
                    "cancel_at_period_end": False
                }
            }
        }

        with patch("app.api.endpoints.webhooks.stripe_service.verify_webhook_signature", return_value={
            "success": True,
            "event": MagicMock(),
            "event_type": "customer.subscription.updated",
            "event_id": update_webhook["id"]
        }):
            with patch("app.services.webhook_service.WebhookService._get_by_field", return_value={
                "id": "subscription_lifecycle_123",
                "stripe_subscription_id": "sub_test_lifecycle_123",
                "user_id": self.test_user_id
            }):
                with patch("app.services.webhook_service.WebhookService._update", return_value={"id": "subscription_lifecycle_123"}):
                    update_response = await async_client.post(
                        "/api/webhooks/stripe",
                        data=json.dumps(update_webhook, separators=(",", ":")),
                        headers={"stripe-signature": "t=1234567890,v1=signature123", "content-type": "application/json"}
                    )

        assert update_response.status_code == status.HTTP_200_OK

        # Step 5: Process payment failure during renewal
        print("Step 5: Process payment failure during renewal")

        failure_webhook = {
            "id": f"evt_test_{uuid4()}",
            "object": "event",
            "type": "invoice.payment_failed",
            "data": {
                "object": {
                    "id": "in_test_failed_123",
                    "customer": "cus_test_lifecycle_123",
                    "subscription": "sub_test_lifecycle_123",
                    "status": "open",
                    "amount_paid": 0,
                    "attempt_count": 1
                }
            }
        }

        with patch("app.api.endpoints.webhooks.stripe_service.verify_webhook_signature", return_value={
            "success": True,
            "event": MagicMock(),
            "event_type": "invoice.payment_failed",
            "event_id": failure_webhook["id"]
        }):
            with patch("app.services.webhook_service.WebhookService._get_by_field", return_value={
                "id": "subscription_lifecycle_123",
                "stripe_subscription_id": "sub_test_lifecycle_123",
                "user_id": self.test_user_id
            }):
                with patch("app.services.webhook_service.WebhookService._update", return_value={"id": "subscription_lifecycle_123"}):
                    failure_response = await async_client.post(
                        "/api/webhooks/stripe",
                        data=json.dumps(failure_webhook, separators=(",", ":")),
                        headers={"stripe-signature": "t=1234567890,v1=signature123", "content-type": "application/json"}
                    )

        assert failure_response.status_code == status.HTTP_200_OK

        # Step 6: Process subscription cancellation
        print("Step 6: Process subscription cancellation")

        cancellation_webhook = {
            "id": f"evt_test_{uuid4()}",
            "object": "event",
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "id": "sub_test_lifecycle_123",
                    "status": "canceled",
                    "canceled_at": int(datetime.now(UTC).timestamp())
                }
            }
        }

        with patch("app.api.endpoints.webhooks.stripe_service.verify_webhook_signature", return_value={
            "success": True,
            "event": MagicMock(),
            "event_type": "customer.subscription.deleted",
            "event_id": cancellation_webhook["id"]
        }):
            with patch("app.services.webhook_service.WebhookService._get_by_field", return_value={
                "id": "subscription_lifecycle_123",
                "stripe_subscription_id": "sub_test_lifecycle_123",
                "user_id": self.test_user_id
            }):
                with patch("app.services.webhook_service.WebhookService._update", return_value={"id": "subscription_lifecycle_123"}):
                    cancellation_response = await async_client.post(
                        "/api/webhooks/stripe",
                        data=json.dumps(cancellation_webhook, separators=(",", ":")),
                        headers={"stripe-signature": "t=1234567890,v1=signature123", "content-type": "application/json"}
                    )

        assert cancellation_response.status_code == status.HTTP_200_OK

        print("✅ Subscription lifecycle completed successfully!")

    @pytest.mark.asyncio
    async def test_brazilian_market_payment_experience(self, async_client: AsyncClient):
        """Test complete payment experience for Brazilian market."""

        # Brazilian user
        brazilian_user = {
            "id": self.test_user_id,
            "email": "joao.silva@exemplo.com.br",
            "name": "João Silva"
        }

        # Step 1: Check Brazilian pricing
        print("Step 1: Check Brazilian pricing")

        pricing_response = await async_client.get("/api/payments/pricing")
        assert pricing_response.status_code == status.HTTP_200_OK
        pricing_data = pricing_response.json()

        assert pricing_data["currency"] == "brl"
        assert pricing_data["country"] == "BR"
        assert pricing_data["locale"] == "pt-BR"

        # Verify Brazilian plans
        plans = pricing_data["pricing"]
        assert "Plano Grátis" in [plan["name"] for plan in plans.values()]
        assert "Plano Profissional" in [plan["name"] for plan in plans.values()]

        # Step 2: Create Brazilian checkout session
        print("Step 2: Create Brazilian checkout session")

        checkout_request = {
            "tier": "pro",
            "metadata": {
                "campaign": "verao_2024",
                "utm_source": "google",
                "market": "brazil"
            }
        }

        mock_checkout_response = {
            "success": True,
            "session_id": "cs_test_brazil_e2e_123",
            "checkout_url": "https://checkout.stripe.com/pay/cs_test_brazil_e2e_123",
            "plan_type": "pro",
            "currency": "brl",
            "amount": 2990
        }

        with patch("app.api.endpoints.payments.stripe_service.create_checkout_session", return_value=mock_checkout_response):
            with patch("app.api.endpoints.payments.get_current_user", return_value=brazilian_user):
                checkout_response = await async_client.post("/api/payments/create-checkout", json=checkout_request)

        assert checkout_response.status_code == status.HTTP_200_OK
        checkout_data = checkout_response.json()

        assert checkout_data["currency"] == "brl"
        assert checkout_data["amount"] == 2990  # R$ 29,90

        # Step 3: Get test payment methods for Brazilian market
        print("Step 3: Get test payment methods for Brazilian market")

        test_methods_response = await async_client.get("/api/webhooks/stripe/test-payment-methods")
        assert test_methods_response.status_code == status.HTTP_200_OK
        methods_data = test_methods_response.json()

        assert methods_data["currency"] == "brl"
        assert methods_data["country"] == "BR"
        assert methods_data["locale"] == "pt-BR"

        # Check for Brazilian card types
        card_method = next((pm for pm in methods_data["payment_methods"] if pm["type"] == "card"), None)
        assert card_method is not None
        assert "Cartão de Crédito" in card_method["name"]

        # Step 4: Process Brazilian payment webhook
        print("Step 4: Process Brazilian payment webhook")

        brazilian_webhook = {
            "id": f"evt_test_{uuid4()}",
            "object": "event",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_brazil_e2e_123",
                    "amount_total": 2990,
                    "currency": "brl",
                    "payment_status": "paid",
                    "customer_details": {
                        "email": "joao.silva@exemplo.com.br",
                        "name": "João Silva",
                        "address": {
                            "country": "BR",
                            "state": "SP",
                            "city": "São Paulo",
                            "line1": "Rua das Flores, 123",
                            "postal_code": "01234-567"
                        }
                    },
                    "metadata": {
                        "user_id": self.test_user_id,
                        "plan": "pro",
                        "market": "brazil",
                        "language": "pt-br"
                    }
                }
            }
        }

        mock_user_profile = {"id": "profile_brazil_123", "user_id": self.test_user_id}

        with patch("app.api.endpoints.webhooks.stripe_service.verify_webhook_signature", return_value={
            "success": True,
            "event": MagicMock(),
            "event_type": "checkout.session.completed",
            "event_id": brazilian_webhook["id"]
        }):
            with patch("app.services.webhook_service.WebhookService._get_by_field", return_value=mock_user_profile):
                with patch("app.services.webhook_service.WebhookService._update", return_value={"id": "profile_brazil_123"}):
                    with patch("app.services.webhook_service.WebhookService._create", return_value={"id": "payment_brazil_123"}):
                        with patch("app.services.usage_limit_service.UsageLimitService.add_credits", return_value=None):
                            webhook_response = await async_client.post(
                                "/api/webhooks/stripe",
                                data=json.dumps(brazilian_webhook, separators=(",", ":")),
                                headers={"stripe-signature": "t=1234567890,v1=signature123", "content-type": "application/json"}
                            )

        assert webhook_response.status_code == status.HTTP_200_OK

        # Step 5: Verify Brazilian user experience
        print("Step 5: Verify Brazilian user experience")

        usage_service = UsageLimitService(self.db)

        mock_brazilian_credits = {
            "id": "credit_brazil_123",
            "user_id": self.test_user_id,
            "credits_remaining": 50,
            "total_credits": 50,
            "subscription_tier": "pro",
            "is_pro": True
        }

        with patch.object(self.db.client.table, 'select') as mock_select:
            mock_select.return_value.eq.return_value.execute.return_value.data = [mock_brazilian_credits]
            credits = await usage_service.get_user_credits(UUID(self.test_user_id))

        assert credits["credits_remaining"] == 50

        # Step 6: Check health endpoints are configured for Brazil
        print("Step 6: Check health endpoints are configured for Brazil")

        payments_health = await async_client.get("/api/payments/health")
        assert payments_health.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]

        webhooks_health = await async_client.get("/api/webhooks/stripe/health")
        assert webhooks_health.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]

        print("✅ Brazilian market payment experience completed successfully!")

    @pytest.mark.asyncio
    async def test_credit_exhaustion_and_replenishment_cycle(self, async_client: AsyncClient):
        """Test complete cycle of credit usage, exhaustion, and replenishment."""

        # Step 1: User starts with basic credits
        print("Step 1: User starts with basic credits")

        usage_service = UsageLimitService(self.db)

        initial_credits = 10
        mock_initial_credits = {
            "id": "credit_cycle_123",
            "user_id": self.test_user_id,
            "credits_remaining": initial_credits,
            "total_credits": initial_credits,
            "subscription_tier": "basic",
            "is_pro": False
        }

        with patch.object(self.db.client.table, 'select') as mock_select:
            mock_select.return_value.eq.return_value.execute.return_value.data = [mock_initial_credits]
            credits = await usage_service.get_user_credits(UUID(self.test_user_id))

        assert credits["credits_remaining"] == initial_credits

        # Step 2: User consumes credits gradually
        print("Step 2: User consumes credits gradually")

        operations_performed = []

        for i in range(initial_credits):
            remaining = initial_credits - i

            with patch.object(self.db.client.table, 'select') as mock_select:
                mock_select.return_value.eq.return_value.execute.return_value.data = [{
                    **mock_initial_credits,
                    "credits_remaining": remaining
                }]
                with patch.object(usage_service, 'deduct_credits', return_value=True):
                    with patch.object(usage_service.usage_tracking_service, 'increment_usage', return_value=None):
                        with patch.object(usage_service.usage_tracking_service, 'get_current_month_usage') as mock_usage:
                            mock_usage.return_value = AsyncMock()
                            mock_usage.return_value.free_optimizations_used = i + 1
                            mock_usage.return_value.paid_optimizations_used = 0

                            operation_id = f"op_{i+1}"
                            result = await usage_service.check_and_track_usage(
                                UUID(self.test_user_id),
                                "free",
                                cost_credits=1
                            )

                            operations_performed.append({
                                "operation_id": operation_id,
                                "credits_before": remaining,
                                "credits_after": remaining - 1,
                                "can_optimize": result.can_optimize
                            })

        # Verify all operations succeeded
        for op in operations_performed:
            assert op["can_optimize"] is True

        # Step 3: User has no credits left
        print("Step 3: User has no credits left")

        mock_no_credits = {
            **mock_initial_credits,
            "credits_remaining": 0
        }

        with patch.object(self.db.client.table, 'select') as mock_select:
            mock_select.return_value.eq.return_value.execute.return_value.data = [mock_no_credits]
            with patch.object(usage_service.usage_tracking_service, 'get_current_month_usage') as mock_usage:
                mock_usage.return_value = AsyncMock()
                mock_usage.return_value.free_optimizations_used = initial_credits
                mock_usage.return_value.paid_optimizations_used = 0

                limit_check = await usage_service.check_usage_limit(UUID(self.test_user_id))

        assert limit_check.can_optimize is False
        assert "Insufficient credits" in limit_check.reason

        # Step 4: User attempts operation but fails
        print("Step 4: User attempts operation but fails")

        with patch.object(self.db.client.table, 'select') as mock_select:
            mock_select.return_value.eq.return_value.execute.return_value.data = [mock_no_credits]
            with patch.object(usage_service, 'deduct_credits', return_value=False):
                with patch.object(usage_service.usage_tracking_service, 'get_current_month_usage') as mock_usage:
                    mock_usage.return_value = AsyncMock()
                    mock_usage.return_value.free_optimizations_used = initial_credits
                    mock_usage.return_value.paid_optimizations_used = 0

                    from app.services.usage_limit_service import UsageLimitExceededError

                    with pytest.raises(UsageLimitExceededError):
                        await usage_service.check_and_track_usage(
                            UUID(self.test_user_id),
                            "free",
                            cost_credits=1
                        )

        # Step 5: User purchases more credits
        print("Step 5: User purchases more credits")

        # Create one-time payment for credits
        payment_intent_request = {
            "user_id": self.test_user_id,
            "user_email": self.test_user["email"],
            "amount": 2990,  # R$ 29,90 - Buy 50 credits
            "metadata": {"purchase_type": "credits"}
        }

        mock_payment_response = {
            "success": True,
            "client_secret": "pi_test_cycle_123_secret",
            "payment_intent_id": "pi_test_cycle_123",
            "amount": 2990,
            "currency": "brl"
        }

        with patch("app.api.endpoints.payments.stripe_service.create_payment_intent", return_value=mock_payment_response):
            payment_response = await async_client.post("/api/payments/create-payment-intent", json=payment_intent_request)

        assert payment_response.status_code == status.HTTP_200_OK
        payment_data = payment_response.json()
        assert payment_data["success"] is True

        # Step 6: Payment succeeds, credits are added
        print("Step 6: Payment succeeds, credits are added")

        payment_webhook = {
            "id": f"evt_test_{uuid4()}",
            "object": "event",
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_test_cycle_123",
                    "amount": 2990,
                    "currency": "brl",
                    "customer": "cus_test_cycle_123",
                    "metadata": {
                        "user_id": self.test_user_id,
                        "purchase_type": "credits"
                    }
                }
            }
        }

        with patch("app.api.endpoints.webhooks.stripe_service.verify_webhook_signature", return_value={
            "success": True,
            "event": MagicMock(),
            "event_type": "payment_intent.succeeded",
            "event_id": payment_webhook["id"]
        }):
            with patch("app.services.webhook_service.WebhookService._create", return_value={"id": "payment_cycle_123"}):
                with patch("app.services.usage_limit_service.UsageLimitService.add_credits", return_value=None):
                    webhook_response = await async_client.post(
                        "/api/webhooks/stripe",
                        data=json.dumps(payment_webhook, separators=(",", ":")),
                        headers={"stripe-signature": "t=1234567890,v1=signature123", "content-type": "application/json"}
                    )

        assert webhook_response.status_code == status.HTTP_200_OK

        # Step 7: User has credits again
        print("Step 7: User has credits again")

        mock_replenished_credits = {
            **mock_initial_credits,
            "credits_remaining": 50,  # New credits purchased
            "total_credits": 60    # 10 initial + 50 purchased
        }

        with patch.object(self.db.client.table, 'select') as mock_select:
            mock_select.return_value.eq.return_value.execute.return_value.data = [mock_replenished_credits]
            replenished_credits = await usage_service.get_user_credits(UUID(self.test_user_id))

        assert replenished_credits["credits_remaining"] == 50
        assert replenished_credits["total_credits"] == 60

        # Step 8: User can optimize again
        print("Step 8: User can optimize again")

        with patch.object(self.db.client.table, 'select') as mock_select:
            mock_select.return_value.eq.return_value.execute.return_value.data = [mock_replenished_credits]
            with patch.object(usage_service, 'deduct_credits', return_value=True):
                with patch.object(usage_service.usage_tracking_service, 'increment_usage', return_value=None):
                    with patch.object(usage_service.usage_tracking_service, 'get_current_month_usage') as mock_usage:
                        mock_usage.return_value = AsyncMock()
                        mock_usage.return_value.free_optimizations_used = initial_credits + 1
                        mock_usage.return_value.paid_optimizations_used = 0

                        final_check = await usage_service.check_and_track_usage(
                            UUID(self.test_user_id),
                            "free",
                            cost_credits=1
                        )

        assert final_check.can_optimize is True

        print("✅ Credit exhaustion and replenishment cycle completed successfully!")

    @pytest.mark.asyncio
    async def test_payment_error_recovery_scenarios(self, async_client: AsyncClient):
        """Test various payment error scenarios and recovery mechanisms."""

        # Scenario 1: Payment method declined
        print("Scenario 1: Payment method declined")

        checkout_request = {"tier": "pro"}

        # Mock checkout creation
        mock_checkout_response = {
            "success": True,
            "session_id": "cs_test_declined_123",
            "checkout_url": "https://checkout.stripe.com/pay/cs_test_declined_123",
            "plan_type": "pro",
            "currency": "brl",
            "amount": 2990
        }

        with patch("app.api.endpoints.payments.stripe_service.create_checkout_session", return_value=mock_checkout_response):
            with patch("app.api.endpoints.payments.get_current_user", return_value=self.test_user):
                checkout_response = await async_client.post("/api/payments/create-checkout", json=checkout_request)

        assert checkout_response.status_code == status.HTTP_200_OK

        # Mock payment failure webhook
        failure_webhook = {
            "id": f"evt_test_{uuid4()}",
            "object": "event",
            "type": "payment_intent.payment_failed",
            "data": {
                "object": {
                    "id": "pi_test_declined_123",
                    "amount": 2990,
                    "currency": "brl",
                    "status": "requires_payment_method",
                    "last_payment_error": {
                        "message": "Your card was declined.",
                        "type": "card_error"
                    },
                    "metadata": {
                        "user_id": self.test_user_id
                    }
                }
            }
        }

        with patch("app.api.endpoints.webhooks.stripe_service.verify_webhook_signature", return_value={
            "success": True,
            "event": MagicMock(),
            "event_type": "payment_intent.payment_failed",
            "event_id": failure_webhook["id"]
        }):
            with patch("app.services.webhook_service.WebhookService._create", return_value={"id": "payment_failed_123"}):
                failure_response = await async_client.post(
                    "/api/webhooks/stripe",
                    data=json.dumps(failure_webhook, separators=(",", ":")),
                    headers={"stripe-signature": "t=1234567890,v1=signature123", "content-type": "application/json"}
                )

        assert failure_response.status_code == status.HTTP_200_OK
        failure_data = failure_response.json()
        assert failure_data["success"] is True
        assert failure_data["status"] == "failed"

        # Scenario 2: Insufficient funds
        print("Scenario 2: Insufficient funds")

        insufficient_funds_webhook = {
            "id": f"evt_test_{uuid4()}",
            "object": "event",
            "type": "payment_intent.payment_failed",
            "data": {
                "object": {
                    "id": "pi_test_insufficient_123",
                    "amount": 9990,
                    "currency": "brl",
                    "status": "requires_payment_method",
                    "last_payment_error": {
                        "message": "Insufficient funds.",
                        "type": "card_error"
                    },
                    "metadata": {
                        "user_id": self.test_user_id
                    }
                }
            }
        }

        with patch("app.api.endpoints.webhooks.stripe_service.verify_webhook_signature", return_value={
            "success": True,
            "event": MagicMock(),
            "event_type": "payment_intent.payment_failed",
            "event_id": insufficient_funds_webhook["id"]
        }):
            with patch("app.services.webhook_service.WebhookService._create", return_value={"id": "payment_insufficient_123"}):
                insufficient_response = await async_client.post(
                    "/api/webhooks/stripe",
                    data=json.dumps(insufficient_funds_webhook, separators=(",", ":")),
                    headers={"stripe-signature": "t=1234567890,v1=signature123", "content-type": "application/json"}
                )

        assert insufficient_response.status_code == status.HTTP_200_OK

        # Scenario 3: User retries with different payment method
        print("Scenario 3: User retries with different payment method")

        # Create new checkout session
        retry_checkout_response = {
            "success": True,
            "session_id": "cs_test_retry_123",
            "checkout_url": "https://checkout.stripe.com/pay/cs_test_retry_123",
            "plan_type": "basic",
            "currency": "brl",
            "amount": 2990
        }

        with patch("app.api.endpoints.payments.stripe_service.create_checkout_session", return_value=retry_checkout_response):
            with patch("app.api.endpoints.payments.get_current_user", return_value=self.test_user):
                retry_response = await async_client.post("/api/payments/create-checkout", json={"tier": "basic"})

        assert retry_response.status_code == status.HTTP_200_OK

        # Payment succeeds on retry
        success_webhook = {
            "id": f"evt_test_{uuid4()}",
            "object": "event",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_retry_123",
                    "amount_total": 2990,
                    "currency": "brl",
                    "payment_status": "paid",
                    "metadata": {
                        "user_id": self.test_user_id,
                        "tier": "basic",
                        "retry_attempt": "2"
                    }
                }
            }
        }

        mock_user_profile = {"id": "profile_retry_123", "user_id": self.test_user_id}

        with patch("app.api.endpoints.webhooks.stripe_service.verify_webhook_signature", return_value={
            "success": True,
            "event": MagicMock(),
            "event_type": "checkout.session.completed",
            "event_id": success_webhook["id"]
        }):
            with patch("app.services.webhook_service.WebhookService._get_by_field", return_value=mock_user_profile):
                with patch("app.services.webhook_service.WebhookService._create", return_value={"id": "payment_retry_success_123"}):
                    with patch("app.services.usage_limit_service.UsageLimitService.add_credits", return_value=None):
                        success_response = await async_client.post(
                            "/api/webhooks/stripe",
                            data=json.dumps(success_webhook, separators=(",", ":")),
                            headers={"stripe-signature": "t=1234567890,v1=signature123", "content-type": "application/json"}
                        )

        assert success_response.status_code == status.HTTP_200_OK
        success_data = success_response.json()
        assert success_data["success"] is True

        # Scenario 4: System error during webhook processing
        print("Scenario 4: System error during webhook processing")

        system_error_webhook = {
            "id": f"evt_test_{uuid4()}",
            "object": "event",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_system_error_123",
                    "amount_total": 2990,
                    "payment_status": "paid",
                    "metadata": {
                        "user_id": self.test_user_id
                    }
                }
            }
        }

        # Mock webhook verification success but processing failure
        with patch("app.api.endpoints.webhooks.stripe_service.verify_webhook_signature", return_value={
            "success": True,
            "event": MagicMock(),
            "event_type": "checkout.session.completed",
            "event_id": system_error_webhook["id"]
        }):
            with patch("app.services.webhook_service.WebhookService.process_webhook_event", side_effect=Exception("Database connection lost")):
                error_response = await async_client.post(
                    "/api/webhooks/stripe",
                    data=json.dumps(system_error_webhook, separators=(",", ":")),
                    headers={"stripe-signature": "t=1234567890,v1=signature123", "content-type": "application/json"}
                )

        # Should still return 200 to prevent Stripe retries
        assert error_response.status_code == status.HTTP_200_OK
        error_data = error_response.json()
        assert error_data["success"] is False
        assert "Internal processing error" in error_data["error"]

        print("✅ Payment error recovery scenarios handled successfully!")