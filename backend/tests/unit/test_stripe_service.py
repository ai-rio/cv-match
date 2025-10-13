"""
Unit tests for Stripe service functionality.
Tests payment processing for the CV-Match Brazilian market SaaS.
"""

import os
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import stripe

from app.services.stripe_service import StripeService, stripe_service


@pytest.mark.unit
@pytest.mark.stripe
class TestStripeService:
    """Test Stripe service functionality."""

    def setup_method(self):
        """Set up test method."""
        # Mock environment variables
        self.test_env = {
            "STRIPE_SECRET_KEY": "sk_test_1234567890",
            "STRIPE_WEBHOOK_SECRET": "whsec_test_1234567890",
            "FRONTEND_URL": "http://localhost:3000",
        }

    @pytest.mark.asyncio
    async def test_stripe_service_initialization(self):
        """Test Stripe service initialization with test mode."""
        with patch.dict(os.environ, self.test_env):
            service = StripeService()

            assert service.api_key == "sk_test_1234567890"
            assert service.default_currency == "brl"
            assert service.default_country == "BR"
            assert service.default_locale == "pt-BR"
            assert service.webhook_secret == "whsec_test_1234567890"
            assert stripe.api_key == "sk_test_1234567890"

    @pytest.mark.asyncio
    async def test_stripe_service_missing_api_key(self):
        """Test Stripe service initialization with missing API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(
                ValueError, match="STRIPE_SECRET_KEY environment variable is required"
            ):
                StripeService()

    @pytest.mark.asyncio
    async def test_stripe_service_production_mode_error(self):
        """Test Stripe service initialization with production key."""
        with patch.dict(os.environ, {"STRIPE_SECRET_KEY": "sk_live_1234567890"}):
            with pytest.raises(ValueError, match="Stripe must be configured in test mode"):
                StripeService()

    @pytest.mark.asyncio
    async def test_create_checkout_session_pro_plan_success(self):
        """Test successful checkout session creation for Pro plan."""
        with patch.dict(os.environ, self.test_env):
            service = StripeService()

            # Mock Stripe checkout session creation
            mock_session = MagicMock()
            mock_session.id = "cs_test_1234567890"
            mock_session.url = "https://checkout.stripe.com/pay/cs_test_1234567890"

            with patch("stripe.checkout.Session.create", return_value=mock_session):
                result = await service.create_checkout_session(
                    user_id="user_123", user_email="test@example.com", plan_type="pro"
                )

                assert result["success"] is True
                assert result["session_id"] == "cs_test_1234567890"
                assert (
                    result["checkout_url"] == "https://checkout.stripe.com/pay/cs_test_1234567890"
                )
                assert result["plan_type"] == "pro"
                assert result["currency"] == "brl"
                assert result["amount"] == 2990  # R$ 29,90

    @pytest.mark.asyncio
    async def test_create_checkout_session_enterprise_plan(self):
        """Test checkout session creation for Enterprise plan."""
        with patch.dict(os.environ, self.test_env):
            service = StripeService()

            mock_session = MagicMock()
            mock_session.id = "cs_test_enterprise_123"
            mock_session.url = "https://checkout.stripe.com/pay/cs_test_enterprise_123"

            with patch("stripe.checkout.Session.create", return_value=mock_session):
                result = await service.create_checkout_session(
                    user_id="user_456", user_email="enterprise@example.com", plan_type="enterprise"
                )

                assert result["success"] is True
                assert result["plan_type"] == "enterprise"
                assert result["amount"] == 9990  # R$ 99,90

    @pytest.mark.asyncio
    async def test_create_checkout_session_free_plan(self):
        """Test checkout session creation for Free plan (no payment required)."""
        with patch.dict(os.environ, self.test_env):
            service = StripeService()

            result = await service.create_checkout_session(
                user_id="user_789", user_email="free@example.com", plan_type="free"
            )

            assert result["success"] is True
            assert result["session_id"] is None
            assert result["checkout_url"] is None
            assert result["plan_type"] == "free"
            assert result["message"] == "Free plan activated"

    @pytest.mark.asyncio
    async def test_create_checkout_session_invalid_plan(self):
        """Test checkout session creation with invalid plan type."""
        with patch.dict(os.environ, self.test_env):
            service = StripeService()

            result = await service.create_checkout_session(
                user_id="user_123", user_email="test@example.com", plan_type="invalid_plan"
            )

            assert result["success"] is False
            assert "Invalid plan type" in result["error"]
            assert result["error_type"] == "value_error"

    @pytest.mark.asyncio
    async def test_create_checkout_session_stripe_error(self):
        """Test checkout session creation with Stripe error."""
        with patch.dict(os.environ, self.test_env):
            service = StripeService()

            with patch(
                "stripe.checkout.Session.create", side_effect=stripe.StripeError("Card declined")
            ):
                result = await service.create_checkout_session(
                    user_id="user_123", user_email="test@example.com", plan_type="pro"
                )

                assert result["success"] is False
                assert "Card declined" in result["error"]
                assert result["error_type"] == "stripe_error"

    @pytest.mark.asyncio
    async def test_create_checkout_session_system_error(self):
        """Test checkout session creation with system error."""
        with patch.dict(os.environ, self.test_env):
            service = StripeService()

            with patch("stripe.checkout.Session.create", side_effect=Exception("System error")):
                result = await service.create_checkout_session(
                    user_id="user_123", user_email="test@example.com", plan_type="pro"
                )

                assert result["success"] is False
                assert "Unexpected error: System error" in result["error"]
                assert result["error_type"] == "system_error"

    @pytest.mark.asyncio
    async def test_create_checkout_session_custom_urls(self):
        """Test checkout session creation with custom success/cancel URLs."""
        with patch.dict(os.environ, self.test_env):
            service = StripeService()

            mock_session = MagicMock()
            mock_session.id = "cs_test_custom_123"
            mock_session.url = "https://checkout.stripe.com/pay/cs_test_custom_123"

            with patch("stripe.checkout.Session.create", return_value=mock_session) as mock_create:
                result = await service.create_checkout_session(
                    user_id="user_123",
                    user_email="test@example.com",
                    plan_type="pro",
                    success_url="https://myapp.com/success",
                    cancel_url="https://myapp.com/cancel",
                )

                assert result["success"] is True

                # Verify custom URLs were passed to Stripe
                call_args = mock_create.call_args[1]
                assert call_args["success_url"] == "https://myapp.com/success"
                assert call_args["cancel_url"] == "https://myapp.com/cancel"

    @pytest.mark.asyncio
    async def test_create_checkout_session_brazilian_metadata(self):
        """Test checkout session creation includes Brazilian market metadata."""
        with patch.dict(os.environ, self.test_env):
            service = StripeService()

            mock_session = MagicMock()
            mock_session.id = "cs_test_brazil_123"
            mock_session.url = "https://checkout.stripe.com/pay/cs_test_brazil_123"

            with patch("stripe.checkout.Session.create", return_value=mock_session) as mock_create:
                result = await service.create_checkout_session(
                    user_id="user_brazil_123",
                    user_email="usuario@exemplo.com.br",
                    plan_type="pro",
                    metadata={"custom_field": "custom_value"},
                )

                assert result["success"] is True

                # Verify Brazilian metadata
                call_args = mock_create.call_args[1]
                metadata = call_args["metadata"]
                assert metadata["user_id"] == "user_brazil_123"
                assert metadata["product"] == "cv_optimization"
                assert metadata["plan"] == "pro"
                assert metadata["market"] == "brazil"
                assert metadata["language"] == "pt-br"
                assert metadata["currency"] == "brl"
                assert metadata["custom_field"] == "custom_value"

    @pytest.mark.asyncio
    async def test_create_customer_success(self):
        """Test successful customer creation."""
        with patch.dict(os.environ, self.test_env):
            service = StripeService()

            mock_customer = MagicMock()
            mock_customer.id = "cus_test_1234567890"

            with patch("stripe.Customer.create", return_value=mock_customer):
                result = await service.create_customer(
                    user_id="user_123", email="test@example.com", name="Test User"
                )

                assert result["success"] is True
                assert result["customer_id"] == "cus_test_1234567890"
                assert result["customer"] == mock_customer

    @pytest.mark.asyncio
    async def test_create_customer_with_address(self):
        """Test customer creation with Brazilian address."""
        with patch.dict(os.environ, self.test_env):
            service = StripeService()

            mock_customer = MagicMock()
            mock_customer.id = "cus_test_brazil_123"

            brazilian_address = {
                "country": "BR",
                "state": "SP",
                "city": "São Paulo",
                "line1": "Rua das Flores, 123",
                "postal_code": "01234-567",
            }

            with patch("stripe.Customer.create", return_value=mock_customer) as mock_create:
                result = await service.create_customer(
                    user_id="user_brazil_123",
                    email="usuario@exemplo.com.br",
                    name="João Silva",
                    address=brazilian_address,
                )

                assert result["success"] is True

                # Verify address was passed correctly
                call_args = mock_create.call_args[1]
                assert call_args["address"] == brazilian_address
                assert call_args["metadata"]["market"] == "brazil"
                assert call_args["metadata"]["language"] == "pt-br"

    @pytest.mark.asyncio
    async def test_create_customer_default_address(self):
        """Test customer creation with default Brazilian address."""
        with patch.dict(os.environ, self.test_env):
            service = StripeService()

            mock_customer = MagicMock()
            mock_customer.id = "cus_test_default_123"

            with patch("stripe.Customer.create", return_value=mock_customer) as mock_create:
                result = await service.create_customer(
                    user_id="user_default_123",
                    email="test@example.com",
                    name="Test User",
                    # No address provided
                )

                assert result["success"] is True

                # Verify default Brazilian address was used
                call_args = mock_create.call_args[1]
                address = call_args["address"]
                assert address["country"] == "BR"
                assert address["state"] == "SP"
                assert address["city"] == "São Paulo"
                assert address["line1"] == "Rua Exemplo, 123"
                assert address["postal_code"] == "01234-567"

    @pytest.mark.asyncio
    async def test_create_customer_stripe_error(self):
        """Test customer creation with Stripe error."""
        with patch.dict(os.environ, self.test_env):
            service = StripeService()

            with patch("stripe.Customer.create", side_effect=stripe.StripeError("Invalid email")):
                result = await service.create_customer(
                    user_id="user_123", email="invalid-email", name="Test User"
                )

                assert result["success"] is False
                assert "Invalid email" in result["error"]
                assert result["error_type"] == "stripe_error"

    @pytest.mark.asyncio
    async def test_retrieve_checkout_session_success(self):
        """Test successful checkout session retrieval."""
        with patch.dict(os.environ, self.test_env):
            service = StripeService()

            mock_session = MagicMock()
            mock_session.id = "cs_test_retrieve_123"
            mock_session.payment_status = "paid"
            mock_session.amount_total = 2990

            with patch("stripe.checkout.Session.retrieve", return_value=mock_session):
                result = await service.retrieve_checkout_session("cs_test_retrieve_123")

                assert result["success"] is True
                assert result["session"] == mock_session

    @pytest.mark.asyncio
    async def test_retrieve_checkout_session_not_found(self):
        """Test checkout session retrieval with non-existent session."""
        with patch.dict(os.environ, self.test_env):
            service = StripeService()

            with patch(
                "stripe.checkout.Session.retrieve", side_effect=stripe.StripeError("Not found")
            ):
                result = await service.retrieve_checkout_session("cs_nonexistent")

                assert result["success"] is False
                assert "Not found" in result["error"]
                assert result["error_type"] == "stripe_error"

    @pytest.mark.asyncio
    async def test_create_payment_intent_success(self):
        """Test successful payment intent creation."""
        with patch.dict(os.environ, self.test_env):
            service = StripeService()

            mock_intent = MagicMock()
            mock_intent.id = "pi_test_1234567890"
            mock_intent.client_secret = "pi_test_1234567890_secret_test"

            with patch("stripe.PaymentIntent.create", return_value=mock_intent):
                result = await service.create_payment_intent(
                    amount=2990,  # R$ 29,90
                    user_id="user_123",
                    user_email="test@example.com",
                )

                assert result["success"] is True
                assert result["client_secret"] == "pi_test_1234567890_secret_test"
                assert result["payment_intent_id"] == "pi_test_1234567890"
                assert result["amount"] == 2990
                assert result["currency"] == "brl"

    @pytest.mark.asyncio
    async def test_create_payment_intent_brazilian_settings(self):
        """Test payment intent creation includes Brazilian-specific settings."""
        with patch.dict(os.environ, self.test_env):
            service = StripeService()

            mock_intent = MagicMock()
            mock_intent.id = "pi_test_brazil_123"
            mock_intent.client_secret = "pi_test_brazil_123_secret_test"

            with patch("stripe.PaymentIntent.create", return_value=mock_intent) as mock_create:
                result = await service.create_payment_intent(
                    amount=9990,  # R$ 99,90
                    user_id="user_brazil_123",
                    user_email="usuario@exemplo.com.br",
                    metadata={"plan_type": "enterprise"},
                )

                assert result["success"] is True

                # Verify Brazilian-specific settings
                call_args = mock_create.call_args[1]
                assert call_args["currency"] == "brl"
                assert call_args["payment_method_types"] == ["card"]
                assert call_args["statement_descriptor"] == "CV-MATCH"
                assert call_args["statement_descriptor_suffix"] == "SERVICOS"

                # Verify metadata
                metadata = call_args["metadata"]
                assert metadata["user_id"] == "user_brazil_123"
                assert metadata["product"] == "cv_optimization"
                assert metadata["market"] == "brazil"
                assert metadata["currency"] == "brl"
                assert metadata["plan_type"] == "enterprise"

    @pytest.mark.asyncio
    async def test_create_payment_intent_stripe_error(self):
        """Test payment intent creation with Stripe error."""
        with patch.dict(os.environ, self.test_env):
            service = StripeService()

            with patch(
                "stripe.PaymentIntent.create", side_effect=stripe.StripeError("Insufficient funds")
            ):
                result = await service.create_payment_intent(
                    amount=9990, user_id="user_123", user_email="test@example.com"
                )

                assert result["success"] is False
                assert "Insufficient funds" in result["error"]
                assert result["error_type"] == "stripe_error"

    @pytest.mark.asyncio
    async def test_verify_webhook_signature_success(self):
        """Test successful webhook signature verification."""
        with patch.dict(os.environ, self.test_env):
            service = StripeService()

            mock_event = MagicMock()
            mock_event.type = "checkout.session.completed"
            mock_event.id = "evt_test_1234567890"

            payload = b'{"test": "data"}'
            signature = "t=1234567890,v1=signature123"

            with patch("stripe.Webhook.construct_event", return_value=mock_event):
                result = await service.verify_webhook_signature(
                    payload=payload, signature=signature
                )

                assert result["success"] is True
                assert result["event"] == mock_event
                assert result["event_type"] == "checkout.session.completed"
                assert result["event_id"] == "evt_test_1234567890"

    @pytest.mark.asyncio
    async def test_verify_webhook_signature_invalid(self):
        """Test webhook signature verification with invalid signature."""
        with patch.dict(os.environ, self.test_env):
            service = StripeService()

            payload = b'{"test": "data"}'
            signature = "invalid_signature"

            with patch(
                "stripe.Webhook.construct_event", side_effect=stripe.SignatureVerificationError
            ):
                result = await service.verify_webhook_signature(
                    payload=payload, signature=signature
                )

                assert result["success"] is False
                assert "Invalid webhook signature" in result["error"]
                assert result["error_type"] == "signature_error"

    @pytest.mark.asyncio
    async def test_verify_webhook_signature_no_secret(self):
        """Test webhook signature verification with no webhook secret configured."""
        with patch.dict(
            os.environ, {"STRIPE_SECRET_KEY": "sk_test_1234567890"}
        ):  # No webhook secret
            service = StripeService()

            payload = b'{"test": "data"}'
            signature = "t=1234567890,v1=signature123"

            result = await service.verify_webhook_signature(payload=payload, signature=signature)

            assert result["success"] is False
            assert "Webhook secret not configured" in result["error"]
            assert result["error_type"] == "configuration_error"

    @pytest.mark.asyncio
    async def test_verify_webhook_signature_system_error(self):
        """Test webhook signature verification with system error."""
        with patch.dict(os.environ, self.test_env):
            service = StripeService()

            payload = b'{"test": "data"}'
            signature = "t=1234567890,v1=signature123"

            with patch("stripe.Webhook.construct_event", side_effect=Exception("System error")):
                result = await service.verify_webhook_signature(
                    payload=payload, signature=signature
                )

                assert result["success"] is False
                assert "Webhook verification failed: System error" in result["error"]
                assert result["error_type"] == "verification_error"

    def test_get_brazilian_pricing(self):
        """Test Brazilian pricing configuration."""
        with patch.dict(os.environ, self.test_env):
            service = StripeService()

            pricing = service._get_brazilian_pricing()

            # Verify all plans are present
            assert "free" in pricing
            assert "pro" in pricing
            assert "enterprise" in pricing
            assert "lifetime" in pricing

            # Verify free plan
            assert pricing["free"]["name"] == "Plano Grátis"
            assert pricing["free"]["price"] == 0
            assert pricing["free"]["currency"] == "brl"

            # Verify pro plan
            assert pricing["pro"]["name"] == "Plano Profissional"
            assert pricing["pro"]["price"] == 2990  # R$ 29,90
            assert pricing["pro"]["currency"] == "brl"

            # Verify enterprise plan
            assert pricing["enterprise"]["name"] == "Plano Empresarial"
            assert pricing["enterprise"]["price"] == 9990  # R$ 99,90
            assert pricing["enterprise"]["currency"] == "brl"

            # Verify lifetime plan
            assert pricing["lifetime"]["name"] == "Acesso Vitalício"
            assert pricing["lifetime"]["price"] == 29700  # R$ 297,00
            assert pricing["lifetime"]["currency"] == "brl"

    @pytest.mark.asyncio
    async def test_get_test_payment_methods(self):
        """Test getting test payment methods for Brazilian market."""
        with patch.dict(os.environ, self.test_env):
            service = StripeService()

            result = await service.get_test_payment_methods()

            assert result["success"] is True
            assert "payment_methods" in result
            assert result["currency"] == "brl"
            assert result["country"] == "BR"
            assert result["locale"] == "pt-BR"

            # Verify card payment methods
            payment_methods = result["payment_methods"]
            card_method = next((pm for pm in payment_methods if pm["type"] == "card"), None)
            assert card_method is not None
            assert card_method["name"] == "Cartão de Crédito"
            assert "test_cards" in card_method

            # Verify test cards
            test_cards = card_method["test_cards"]
            success_card = next((tc for tc in test_cards if tc["status"] == "success"), None)
            assert success_card is not None
            assert success_card["number"] == "4242424242424242"
            assert success_card["brand"] == "Visa"

    def test_global_service_instance(self):
        """Test global stripe service instance."""
        assert stripe_service is not None
        assert isinstance(stripe_service, StripeService)
