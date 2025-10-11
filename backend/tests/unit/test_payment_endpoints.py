"""
Unit tests for payment API endpoints.
Tests payment creation, webhook processing, and related functionality.
"""

import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient

from app.api.endpoints.payments import CREDIT_TIERS, get_credits_for_tier, get_price_id_for_tier


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.payment
class TestPaymentEndpoints:
    """Test payment API endpoints."""

    def setup_method(self):
        """Set up test method."""
        self.test_user = {
            "id": "user_1234567890",
            "email": "test@example.com",
            "name": "Test User"
        }

    @pytest.mark.asyncio
    async def test_create_checkout_session_success(self, async_client: AsyncClient):
        """Test successful checkout session creation."""
        request_data = {
            "tier": "pro",
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel",
            "metadata": {"custom_field": "custom_value"}
        }

        # Mock Stripe service response
        mock_stripe_response = {
            "success": True,
            "session_id": "cs_test_1234567890",
            "checkout_url": "https://checkout.stripe.com/pay/cs_test_1234567890",
            "plan_type": "pro",
            "currency": "brl",
            "amount": 2990
        }

        with patch("app.api.endpoints.payments.stripe_service.create_checkout_session", return_value=mock_stripe_response):
            with patch("app.api.endpoints.payments.get_current_user", return_value=self.test_user):
                response = await async_client.post("/api/payments/create-checkout", json=request_data)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["success"] is True
        assert response_data["session_id"] == "cs_test_1234567890"
        assert response_data["checkout_url"] == "https://checkout.stripe.com/pay/cs_test_1234567890"
        assert response_data["tier"] == "pro"
        assert response_data["credits"] == 50  # Pro tier credits
        assert response_data["currency"] == "brl"
        assert response_data["amount"] == 2990

    @pytest.mark.asyncio
    async def test_create_checkout_session_basic_tier(self, async_client: AsyncClient):
        """Test checkout session creation for basic tier."""
        request_data = {"tier": "basic"}

        mock_stripe_response = {
            "success": True,
            "session_id": "cs_test_basic_123",
            "checkout_url": "https://checkout.stripe.com/pay/cs_test_basic_123",
            "plan_type": "pro",  # Maps to pro in StripeService
            "currency": "brl",
            "amount": 2990
        }

        with patch("app.api.endpoints.payments.stripe_service.create_checkout_session", return_value=mock_stripe_response):
            with patch("app.api.endpoints.payments.get_current_user", return_value=self.test_user):
                response = await async_client.post("/api/payments/create-checkout", json=request_data)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["tier"] == "basic"
        assert response_data["credits"] == 10  # Basic tier credits

    @pytest.mark.asyncio
    async def test_create_checkout_session_enterprise_tier(self, async_client: AsyncClient):
        """Test checkout session creation for enterprise tier."""
        request_data = {"tier": "enterprise"}

        mock_stripe_response = {
            "success": True,
            "session_id": "cs_test_enterprise_123",
            "checkout_url": "https://checkout.stripe.com/pay/cs_test_enterprise_123",
            "plan_type": "enterprise",
            "currency": "brl",
            "amount": 9990
        }

        with patch("app.api.endpoints.payments.stripe_service.create_checkout_session", return_value=mock_stripe_response):
            with patch("app.api.endpoints.payments.get_current_user", return_value=self.test_user):
                response = await async_client.post("/api/payments/create-checkout", json=request_data)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["tier"] == "enterprise"
        assert response_data["credits"] == 1000  # Enterprise tier credits
        assert response_data["amount"] == 9990

    @pytest.mark.asyncio
    async def test_create_checkout_session_invalid_tier(self, async_client: AsyncClient):
        """Test checkout session creation with invalid tier."""
        request_data = {"tier": "invalid_tier"}

        with patch("app.api.endpoints.payments.get_current_user", return_value=self.test_user):
            response = await async_client.post("/api/payments/create-checkout", json=request_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert "Invalid tier" in response_data["detail"]
        assert "basic" in response_data["detail"]
        assert "pro" in response_data["detail"]
        assert "enterprise" in response_data["detail"]

    @pytest.mark.asyncio
    async def test_create_checkout_session_stripe_error(self, async_client: AsyncClient):
        """Test checkout session creation with Stripe error."""
        request_data = {"tier": "pro"}

        with patch("app.api.endpoints.payments.stripe_service.create_checkout_session", return_value={
            "success": False,
            "error": "Card declined",
            "error_type": "stripe_error"
        }):
            with patch("app.api.endpoints.payments.get_current_user", return_value=self.test_user):
                response = await async_client.post("/api/payments/create-checkout", json=request_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert response_data["detail"] == "Card declined"

    @pytest.mark.asyncio
    async def test_create_checkout_session_missing_auth(self, async_client: AsyncClient):
        """Test checkout session creation without authentication."""
        request_data = {"tier": "pro"}

        with patch("app.api.endpoints.payments.get_current_user", side_effect=Exception("Not authenticated")):
            response = await async_client.post("/api/payments/create-checkout", json=request_data)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    @pytest.mark.asyncio
    async def test_create_payment_intent_success(self, async_client: AsyncClient):
        """Test successful payment intent creation."""
        request_data = {
            "user_id": "user_123",
            "user_email": "test@example.com",
            "amount": 2990,  # R$ 29,90
            "metadata": {"plan_type": "pro"}
        }

        mock_stripe_response = {
            "success": True,
            "client_secret": "pi_test_1234567890_secret_test",
            "payment_intent_id": "pi_test_1234567890",
            "amount": 2990,
            "currency": "brl"
        }

        with patch("app.api.endpoints.payments.stripe_service.create_payment_intent", return_value=mock_stripe_response):
            response = await async_client.post("/api/payments/create-payment-intent", json=request_data)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["success"] is True
        assert response_data["client_secret"] == "pi_test_1234567890_secret_test"
        assert response_data["payment_intent_id"] == "pi_test_1234567890"
        assert response_data["amount"] == 2990
        assert response_data["currency"] == "brl"

    @pytest.mark.asyncio
    async def test_create_payment_intent_stripe_error(self, async_client: AsyncClient):
        """Test payment intent creation with Stripe error."""
        request_data = {
            "user_id": "user_123",
            "user_email": "test@example.com",
            "amount": 2990
        }

        with patch("app.api.endpoints.payments.stripe_service.create_payment_intent", return_value={
            "success": False,
            "error": "Insufficient funds",
            "error_type": "stripe_error"
        }):
            response = await async_client.post("/api/payments/create-payment-intent", json=request_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert response_data["detail"] == "Insufficient funds"

    @pytest.mark.asyncio
    async def test_create_customer_success(self, async_client: AsyncClient):
        """Test successful customer creation."""
        request_data = {
            "user_id": "user_123",
            "email": "test@example.com",
            "name": "Test User",
            "address": {
                "country": "BR",
                "state": "SP",
                "city": "São Paulo",
                "line1": "Rua Teste, 123",
                "postal_code": "01234-567"
            }
        }

        mock_stripe_response = {
            "success": True,
            "customer_id": "cus_test_1234567890",
            "customer": {"id": "cus_test_1234567890", "email": "test@example.com"}
        }

        with patch("app.api.endpoints.payments.stripe_service.create_customer", return_value=mock_stripe_response):
            response = await async_client.post("/api/payments/create-customer", json=request_data)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["success"] is True
        assert response_data["customer_id"] == "cus_test_1234567890"
        assert "customer" in response_data

    @pytest.mark.asyncio
    async def test_create_customer_minimal_data(self, async_client: AsyncClient):
        """Test customer creation with minimal data."""
        request_data = {
            "user_id": "user_123",
            "email": "test@example.com"
        }

        mock_stripe_response = {
            "success": True,
            "customer_id": "cus_test_minimal_123",
            "customer": {"id": "cus_test_minimal_123", "email": "test@example.com"}
        }

        with patch("app.api.endpoints.payments.stripe_service.create_customer", return_value=mock_stripe_response):
            response = await async_client.post("/api/payments/create-customer", json=request_data)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["success"] is True
        assert response_data["customer_id"] == "cus_test_minimal_123"

    @pytest.mark.asyncio
    async def test_create_customer_stripe_error(self, async_client: AsyncClient):
        """Test customer creation with Stripe error."""
        request_data = {
            "user_id": "user_123",
            "email": "invalid-email"
        }

        with patch("app.api.endpoints.payments.stripe_service.create_customer", return_value={
            "success": False,
            "error": "Invalid email",
            "error_type": "stripe_error"
        }):
            response = await async_client.post("/api/payments/create-customer", json=request_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert response_data["detail"] == "Invalid email"

    @pytest.mark.asyncio
    async def test_retrieve_checkout_session_success(self, async_client: AsyncClient):
        """Test successful checkout session retrieval."""
        session_id = "cs_test_1234567890"

        mock_stripe_response = {
            "success": True,
            "session": {
                "id": session_id,
                "payment_status": "paid",
                "amount_total": 2990,
                "currency": "brl"
            }
        }

        with patch("app.api.endpoints.payments.stripe_service.retrieve_checkout_session", return_value=mock_stripe_response):
            response = await async_client.get(f"/api/payments/retrieve-session/{session_id}")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["success"] is True
        assert response_data["session"]["id"] == session_id
        assert response_data["session"]["payment_status"] == "paid"

    @pytest.mark.asyncio
    async def test_retrieve_checkout_session_not_found(self, async_client: AsyncClient):
        """Test checkout session retrieval with non-existent session."""
        session_id = "cs_nonexistent"

        with patch("app.api.endpoints.payments.stripe_service.retrieve_checkout_session", return_value={
            "success": False,
            "error": "Session not found",
            "error_type": "stripe_error"
        }):
            response = await async_client.get(f"/api/payments/retrieve-session/{session_id}")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert response_data["detail"] == "Session not found"

    @pytest.mark.asyncio
    async def test_get_brazilian_pricing_success(self, async_client: AsyncClient):
        """Test getting Brazilian pricing configuration."""
        mock_pricing = {
            "free": {
                "name": "Plano Grátis",
                "price": 0,
                "currency": "brl",
                "credits": 5
            },
            "pro": {
                "name": "Plano Profissional",
                "price": 2990,
                "currency": "brl",
                "credits": 50
            },
            "enterprise": {
                "name": "Plano Empresarial",
                "price": 9990,
                "currency": "brl",
                "credits": 200
            },
            "lifetime": {
                "name": "Acesso Vitalício",
                "price": 29700,
                "currency": "brl",
                "credits": 1000
            }
        }

        with patch("app.api.endpoints.payments.stripe_service._get_brazilian_pricing", return_value=mock_pricing):
            response = await async_client.get("/api/payments/pricing")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["success"] is True
        assert response_data["pricing"] == mock_pricing
        assert response_data["currency"] == "brl"
        assert response_data["country"] == "BR"
        assert response_data["locale"] == "pt-BR"

    @pytest.mark.asyncio
    async def test_payments_health_check_healthy(self, async_client: AsyncClient):
        """Test payments health check when healthy."""
        with patch("app.api.endpoints.payments.stripe_service") as mock_stripe:
            mock_stripe.api_key = "sk_test_1234567890"
            mock_stripe.webhook_secret = "whsec_test_1234567890"
            mock_stripe.default_currency = "brl"
            mock_stripe.default_country = "BR"
            mock_stripe.default_locale = "pt-BR"

            response = await async_client.get("/api/payments/health")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["status"] == "healthy"
        assert response_data["stripe_configured"] is True
        assert response_data["test_mode"] is True
        assert response_data["currency"] == "brl"
        assert response_data["country"] == "BR"
        assert response_data["locale"] == "pt-BR"

    @pytest.mark.asyncio
    async def test_payments_health_check_unhealthy(self, async_client: AsyncClient):
        """Test payments health check when unhealthy."""
        with patch("app.api.endpoints.payments.stripe_service") as mock_stripe:
            mock_stripe.api_key = None  # Not configured
            mock_stripe.webhook_secret = None
            mock_stripe.default_currency = "brl"

            response = await async_client.get("/api/payments/health")

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        response_data = response.json()
        assert response_data["status"] == "unhealthy"

    @pytest.mark.asyncio
    async def test_payments_health_check_system_error(self, async_client: AsyncClient):
        """Test payments health check with system error."""
        with patch("app.api.endpoints.payments.stripe_service", side_effect=Exception("System error")):
            response = await async_client.get("/api/payments/health")

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        response_data = response.json()
        assert response_data["status"] == "unhealthy"
        assert "System error" in response_data["error"]

    def test_get_credits_for_tier_all_tiers(self):
        """Test getting credits for all tiers."""
        test_cases = [
            ("basic", 10),
            ("pro", 50),
            ("enterprise", 1000),
            ("invalid_tier", 10),  # Defaults to 10
        ]

        for tier, expected_credits in test_cases:
            with self.subTest(tier=tier):
                credits = get_credits_for_tier(tier)
                assert credits == expected_credits

    def test_get_price_id_for_tier_all_tiers(self):
        """Test getting price ID for all tiers."""
        test_cases = [
            ("basic", "pro"),
            ("pro", "pro"),
            ("enterprise", "enterprise"),
            ("invalid_tier", "pro"),  # Defaults to pro
        ]

        for tier, expected_price_id in test_cases:
            with self.subTest(tier=tier):
                price_id = get_price_id_for_tier(tier)
                assert price_id == expected_price_id

    def test_credit_tiers_constant(self):
        """Test credit tiers constant is properly defined."""
        assert "basic" in CREDIT_TIERS
        assert "pro" in CREDIT_TIERS
        assert "enterprise" in CREDIT_TIERS

        assert CREDIT_TIERS["basic"] == 10
        assert CREDIT_TIERS["pro"] == 50
        assert CREDIT_TIERS["enterprise"] == 1000

        # Verify progression
        assert CREDIT_TIERS["basic"] < CREDIT_TIERS["pro"] < CREDIT_TIERS["enterprise"]

    @pytest.mark.asyncio
    async def test_create_checkout_session_with_custom_metadata(self, async_client: AsyncClient):
        """Test checkout session creation with custom metadata."""
        request_data = {
            "tier": "pro",
            "metadata": {
                "campaign": "summer_sale",
                "referrer": "user_456",
                "utm_source": "google"
            }
        }

        mock_stripe_response = {
            "success": True,
            "session_id": "cs_test_metadata_123",
            "checkout_url": "https://checkout.stripe.com/pay/cs_test_metadata_123",
            "plan_type": "pro",
            "currency": "brl",
            "amount": 2990
        }

        with patch("app.api.endpoints.payments.stripe_service.create_checkout_session", return_value=mock_stripe_response) as mock_create:
            with patch("app.api.endpoints.payments.get_current_user", return_value=self.test_user):
                response = await async_client.post("/api/payments/create-checkout", json=request_data)

        assert response.status_code == status.HTTP_200_OK

        # Verify metadata was passed correctly
        call_args = mock_create.call_args[1]
        metadata = call_args["metadata"]
        assert metadata["user_id"] == self.test_user["id"]
        assert metadata["credits"] == "50"
        assert metadata["tier"] == "pro"
        assert metadata["campaign"] == "summer_sale"
        assert metadata["referrer"] == "user_456"
        assert metadata["utm_source"] == "google"

    @pytest.mark.asyncio
    async def test_create_checkout_session_without_optional_fields(self, async_client: AsyncClient):
        """Test checkout session creation without optional fields."""
        request_data = {"tier": "pro"}  # Only required field

        mock_stripe_response = {
            "success": True,
            "session_id": "cs_test_minimal_123",
            "checkout_url": "https://checkout.stripe.com/pay/cs_test_minimal_123",
            "plan_type": "pro",
            "currency": "brl",
            "amount": 2990
        }

        with patch("app.api.endpoints.payments.stripe_service.create_checkout_session", return_value=mock_stripe_response) as mock_create:
            with patch("app.api.endpoints.payments.get_current_user", return_value=self.test_user):
                response = await async_client.post("/api/payments/create-checkout", json=request_data)

        assert response.status_code == status.HTTP_200_OK

        # Verify default values were used
        call_args = mock_create.call_args[1]
        assert call_args["success_url"] is not None  # Default URL
        assert call_args["cancel_url"] is not None   # Default URL

    @pytest.mark.asyncio
    async def test_create_payment_intent_validation_error(self, async_client: AsyncClient):
        """Test payment intent creation with validation error."""
        # Missing required fields
        request_data = {
            "user_id": "user_123"
            # Missing user_email and amount
        }

        response = await async_client.post("/api/payments/create-payment-intent", json=request_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_create_customer_validation_error(self, async_client: AsyncClient):
        """Test customer creation with validation error."""
        # Invalid email format
        request_data = {
            "user_id": "user_123",
            "user_email": "invalid-email-format"
        }

        response = await async_client.post("/api/payments/create-customer", json=request_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_brazilian_pricing_structure(self, async_client: AsyncClient):
        """Test Brazilian pricing structure includes all expected fields."""
        mock_pricing = {
            "free": {
                "name": "Plano Grátis",
                "description": "Análise básica de currículo",
                "price": 0,
                "currency": "brl",
                "features": ["5 análises por mês", "Matching básico"]
            },
            "pro": {
                "name": "Plano Profissional",
                "description": "Análise avançada com IA",
                "price": 2990,
                "currency": "brl",
                "features": ["Análises ilimitadas", "Suporte prioritário"]
            }
        }

        with patch("app.api.endpoints.payments.stripe_service._get_brazilian_pricing", return_value=mock_pricing):
            response = await async_client.get("/api/payments/pricing")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        # Verify pricing structure
        pricing = response_data["pricing"]
        for plan_name, plan_data in pricing.items():
            assert "name" in plan_data
            assert "price" in plan_data
            assert "currency" in plan_data
            assert plan_data["currency"] == "brl"

            # All plans should have a price in cents
            assert isinstance(plan_data["price"], int)
            assert plan_data["price"] >= 0

    @pytest.mark.asyncio
    async def test_error_handling_unexpected_exception(self, async_client: AsyncClient):
        """Test error handling for unexpected exceptions."""
        request_data = {"tier": "pro"}

        with patch("app.api.endpoints.payments.get_current_user", return_value=self.test_user):
            with patch("app.api.endpoints.payments.stripe_service.create_checkout_session", side_effect=Exception("Unexpected error")):
                response = await async_client.post("/api/payments/create-checkout", json=request_data)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        response_data = response.json()
        assert "Internal server error" in response_data["detail"]