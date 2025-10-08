"""
Stripe service for payment processing.
Supports Brazilian market with BRL currency and local payment methods.
"""

import os
from datetime import UTC, datetime
from typing import Any, Dict, Optional

import stripe
from dotenv import load_dotenv

load_dotenv()


class StripeService:
    """Service for Stripe payment operations with Brazilian market support."""

    def __init__(self):
        """Initialize Stripe service with test mode configuration."""
        self.api_key = os.getenv("STRIPE_SECRET_KEY")
        if not self.api_key:
            raise ValueError("STRIPE_SECRET_KEY environment variable is required")

        stripe.api_key = self.api_key

        # Configure for Brazilian market
        self.default_currency = "brl"
        self.default_country = "BR"
        self.default_locale = "pt-BR"

        # Test mode webhook secret
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

        # Verify we're in test mode
        if not self.api_key.startswith("sk_test_"):
            raise ValueError("Stripe must be configured in test mode for development")

    async def create_checkout_session(
        self,
        user_id: str,
        user_email: str,
        plan_type: str = "pro",
        success_url: Optional[str] = None,
        cancel_url: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe checkout session for Brazilian market.

        Args:
            user_id: User identifier
            user_email: User email address
            plan_type: Plan type (free, pro, enterprise)
            success_url: URL to redirect to on success
            cancel_url: URL to redirect to on cancellation
            metadata: Additional metadata

        Returns:
            Checkout session data
        """
        # Brazilian pricing configuration
        pricing_config = self._get_brazilian_pricing()

        if plan_type not in pricing_config:
            raise ValueError(f"Invalid plan type: {plan_type}")

        plan_config = pricing_config[plan_type]

        # Default URLs for Brazilian market
        if not success_url:
            success_url = os.getenv("FRONTEND_URL", "http://localhost:3000") + "/sucesso"
        if not cancel_url:
            cancel_url = os.getenv("FRONTEND_URL", "http://localhost:3000") + "/cancelar"

        # Prepare metadata
        session_metadata = {
            "user_id": user_id,
            "product": "cv_optimization",
            "plan": plan_type,
            "market": "brazil",
            "language": "pt-br",
            "currency": "brl"
        }

        if metadata:
            session_metadata.update(metadata)

        try:
            # Create checkout session with Brazilian configuration
            session_params = {
                "payment_method_types": ["card"],  # Start with cards, add PIX later
                "mode": "subscription" if plan_type in ["pro", "enterprise"] else "payment",
                "currency": self.default_currency,
                "customer_email": user_email,
                "success_url": success_url,
                "cancel_url": cancel_url,
                "metadata": session_metadata,
                "locale": self.default_locale,
                "billing_address_collection": "required",
                "shipping_address_collection": {"allowed_countries": [self.default_country]},
            }

            # Add price based on plan type
            if plan_type == "free":
                # Free plan - no payment required
                return {
                    "success": True,
                    "session_id": None,
                    "checkout_url": None,
                    "plan_type": "free",
                    "message": "Free plan activated"
                }
            elif plan_type in ["pro", "enterprise"]:
                # Create recurring price for subscription plans
                session_params.update({
                    "line_items": [{
                        "price_data": {
                            "currency": self.default_currency,
                            "unit_amount": plan_config["price"],
                            "product_data": {
                                "name": plan_config["name"],
                                "description": plan_config["description"],
                                "images": [],
                                "metadata": {
                                    "market": "brazil",
                                    "language": "pt-br"
                                }
                            },
                            "recurring": {
                                "interval": "month",
                                "interval_count": 1
                            }
                        },
                        "quantity": 1,
                    }]
                })
            else:
                # One-time payment for lifetime plan
                session_params.update({
                    "line_items": [{
                        "price_data": {
                            "currency": self.default_currency,
                            "unit_amount": plan_config["price"],
                            "product_data": {
                                "name": plan_config["name"],
                                "description": plan_config["description"],
                                "images": [],
                                "metadata": {
                                    "market": "brazil",
                                    "language": "pt-br"
                                }
                            }
                        },
                        "quantity": 1,
                    }]
                })

            # Create the checkout session
            session = stripe.checkout.Session.create(**session_params)

            return {
                "success": True,
                "session_id": session.id,
                "checkout_url": session.url,
                "plan_type": plan_type,
                "currency": self.default_currency,
                "amount": plan_config["price"]
            }

        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "stripe_error"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_type": "system_error"
            }

    async def create_customer(
        self,
        user_id: str,
        email: str,
        name: Optional[str] = None,
        address: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe customer for Brazilian market.

        Args:
            user_id: User identifier
            email: User email
            name: User name
            address: User address (Brazilian format)

        Returns:
            Customer creation result
        """
        try:
            customer_params = {
                "email": email,
                "metadata": {
                    "user_id": user_id,
                    "market": "brazil",
                    "language": "pt-br"
                }
            }

            if name:
                customer_params["name"] = name

            if address:
                customer_params["address"] = address
            else:
                # Default Brazilian address format
                customer_params["address"] = {
                    "country": "BR",
                    "state": "SP",
                    "city": "São Paulo",
                    "line1": "Rua Exemplo, 123",
                    "postal_code": "01234-567"
                }

            customer = stripe.Customer.create(**customer_params)

            return {
                "success": True,
                "customer_id": customer.id,
                "customer": customer
            }

        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "stripe_error"
            }

    async def retrieve_checkout_session(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve a checkout session.

        Args:
            session_id: Stripe checkout session ID

        Returns:
            Session data
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return {
                "success": True,
                "session": session
            }
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "stripe_error"
            }

    async def create_payment_intent(
        self,
        amount: int,
        user_id: str,
        user_email: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a payment intent for Brazilian market.

        Args:
            amount: Amount in cents (BRL)
            user_id: User identifier
            user_email: User email
            metadata: Additional metadata

        Returns:
            Payment intent data
        """
        try:
            intent_metadata = {
                "user_id": user_id,
                "product": "cv_optimization",
                "market": "brazil",
                "currency": "brl"
            }

            if metadata:
                intent_metadata.update(metadata)

            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=self.default_currency,
                receipt_email=user_email,
                metadata=intent_metadata,
                payment_method_types=["card"],  # Start with cards
                # Add Brazilian-specific settings
                statement_descriptor="CV-MATCH",
                statement_descriptor_suffix="SERVICOS"
            )

            return {
                "success": True,
                "client_secret": payment_intent.client_secret,
                "payment_intent_id": payment_intent.id,
                "amount": amount,
                "currency": self.default_currency
            }

        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "stripe_error"
            }

    async def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str
    ) -> Dict[str, Any]:
        """
        Verify Stripe webhook signature.

        Args:
            payload: Raw webhook payload
            signature: Stripe signature header

        Returns:
            Verification result with event data
        """
        if not self.webhook_secret:
            return {
                "success": False,
                "error": "Webhook secret not configured",
                "error_type": "configuration_error"
            }

        try:
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=signature,
                secret=self.webhook_secret,
                tolerance=300  # 5 minutes tolerance
            )

            return {
                "success": True,
                "event": event,
                "event_type": event.type,
                "event_id": event.id
            }

        except stripe.error.SignatureVerificationError:
            return {
                "success": False,
                "error": "Invalid webhook signature",
                "error_type": "signature_error"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Webhook verification failed: {str(e)}",
                "error_type": "verification_error"
            }

    def _get_brazilian_pricing(self) -> Dict[str, Dict[str, Any]]:
        """
        Get Brazilian pricing configuration.

        Returns:
            Pricing configuration for Brazilian market
        """
        return {
            "free": {
                "name": "Plano Grátis",
                "description": "Análise básica de currículo",
                "price": 0,
                "currency": "brl",
                "features": [
                    "5 análises por mês",
                    "Matching básico",
                    "Download em PDF"
                ]
            },
            "pro": {
                "name": "Plano Profissional",
                "description": "Análise avançada com IA para o mercado brasileiro",
                "price": 2990,  # R$ 29,90
                "currency": "brl",
                "features": [
                    "Análises ilimitadas",
                    "Matching avançado com IA",
                    "Templates brasileiros",
                    "Suporte prioritário",
                    "Análise de compatibilidade com vagas"
                ]
            },
            "enterprise": {
                "name": "Plano Empresarial",
                "description": "Solução completa para recrutamento no Brasil",
                "price": 9990,  # R$ 99,90
                "currency": "brl",
                "features": [
                    "Recrutamento ilimitado",
                    "Dashboard avançado",
                    "API de integração",
                    "Múltiplos usuários",
                    "Relatórios detalhados",
                    "Suporte dedicado"
                ]
            },
            "lifetime": {
                "name": "Acesso Vitalício",
                "description": "Acesso vitalício ao plano profissional",
                "price": 29700,  # R$ 297,00
                "currency": "brl",
                "features": [
                    "Todos os recursos do plano Pro",
                    "Acesso vitalício",
                    "Atualizações gratuitas",
                    "Suporte prioritário vitalício"
                ]
            }
        }

    async def get_test_payment_methods(self) -> Dict[str, Any]:
        """
        Get available test payment methods for Brazilian market.

        Returns:
            Available test payment methods
        """
        return {
            "success": True,
            "payment_methods": [
                {
                    "type": "card",
                    "name": "Cartão de Crédito",
                    "test_cards": [
                        {
                            "number": "4242424242424242",
                            "brand": "Visa",
                            "status": "success",
                            "description": "Visa sucesso"
                        },
                        {
                            "number": "4000002500003155",
                            "brand": "Visa",
                            "status": "requires_authentication",
                            "description": "Visa 3DS requerido"
                        },
                        {
                            "number": "4000000000009995",
                            "brand": "Visa",
                            "status": "insufficient_funds",
                            "description": "Visa fundos insuficientes"
                        }
                    ]
                }
            ],
            "currency": "brl",
            "country": "BR",
            "locale": "pt-BR"
        }


# Global service instance
stripe_service = StripeService()