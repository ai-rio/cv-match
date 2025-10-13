"""
Stripe service for payment processing.
Supports Brazilian market with BRL currency and local payment methods.
"""

import os
from typing import Any

import stripe
from dotenv import load_dotenv

# Stripe error types for proper exception handling
StripeError = stripe.StripeError

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
        plan_type: str = "basic",
        success_url: str | None = None,
        cancel_url: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Create a Stripe checkout session for Brazilian market.

        Args:
            user_id: User identifier
            user_email: User email address
            plan_type: Plan type (basic, pro, enterprise)
            success_url: URL to redirect to on success
            cancel_url: URL to redirect to on cancellation
            metadata: Additional metadata

        Returns:
            Checkout session data
        """
        # Import here to avoid circular imports
        from app.config.pricing import pricing_config

        # Get pricing configuration
        pricing_tier = pricing_config.get_tier(plan_type)
        if not pricing_tier:
            raise ValueError(f"Invalid plan type: {plan_type}")

        # Default URLs for Brazilian market
        if not success_url:
            success_url = os.getenv("FRONTEND_URL", "http://localhost:3000") + "/payment/success"
        if not cancel_url:
            cancel_url = os.getenv("FRONTEND_URL", "http://localhost:3000") + "/payment/canceled"

        # Prepare metadata
        session_metadata = {
            "user_id": user_id,
            "product": "cv_optimization",
            "plan": plan_type,
            "market": "brazil",
            "language": "pt-br",
            "currency": "brl",
            "credits": str(pricing_tier.credits),
        }

        if metadata:
            session_metadata.update(metadata)

        try:
            # Create checkout session with Brazilian configuration
            session_params = {
                "payment_method_types": ["card"],  # Start with cards, add PIX later
                "mode": "payment",  # One-time payment for credit packages
                "currency": self.default_currency,
                "customer_email": user_email,
                "success_url": success_url,
                "cancel_url": cancel_url,
                "metadata": session_metadata,
                "locale": self.default_locale,
                "billing_address_collection": "auto",
                "shipping_address_collection": {"allowed_countries": [self.default_country]},
            }

            # Add price based on plan type
            if pricing_tier.price == 0:
                # Free plan - no payment required
                return {
                    "success": True,
                    "session_id": None,
                    "checkout_url": None,
                    "plan_type": plan_type,
                    "message": "Free plan activated",
                }
            else:
                # Create one-time payment for credit packages
                session_params.update(
                    {
                        "line_items": [  # type: ignore
                            {
                                "price_data": {
                                    "currency": self.default_currency,
                                    "unit_amount": pricing_tier.price,
                                    "product_data": {
                                        "name": pricing_tier.name,
                                        "description": pricing_tier.description,
                                        "images": [],
                                        "metadata": {
                                            "market": "brazil",
                                            "language": "pt-br",
                                            "credits": str(pricing_tier.credits),
                                            "plan": plan_type,
                                        },
                                    },
                                },
                                "quantity": 1,
                            }
                        ]
                    }
                )

            # Create the checkout session
            session = stripe.checkout.Session.create(session_params)  # type: ignore

            return {
                "success": True,
                "session_id": session.id,
                "checkout_url": session.url,
                "plan_type": plan_type,
                "currency": self.default_currency,
                "amount": pricing_tier.price,
                "credits": pricing_tier.credits,
            }

        except StripeError as e:
            return {"success": False, "error": str(e), "error_type": "stripe_error"}
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_type": "system_error",
            }

    async def create_customer(
        self,
        user_id: str,
        email: str,
        name: str | None = None,
        address: dict[str, str] | None = None,
    ) -> dict[str, Any]:
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
            customer_params: dict[str, Any] = {
                "email": email,
                "metadata": {"user_id": user_id, "market": "brazil", "language": "pt-br"},
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
                    "postal_code": "01234-567",
                }

            customer = stripe.Customer.create(**customer_params)

            return {"success": True, "customer_id": customer.id, "customer": customer}

        except StripeError as e:
            return {"success": False, "error": str(e), "error_type": "stripe_error"}

    async def retrieve_checkout_session(self, session_id: str) -> dict[str, Any]:
        """
        Retrieve a checkout session.

        Args:
            session_id: Stripe checkout session ID

        Returns:
            Session data
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return {"success": True, "session": session}
        except StripeError as e:
            return {"success": False, "error": str(e), "error_type": "stripe_error"}

    async def create_payment_intent(
        self, amount: int, user_id: str, user_email: str, metadata: dict[str, str] | None = None
    ) -> dict[str, Any]:
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
                "currency": "brl",
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
                statement_descriptor_suffix="SERVICOS",
            )

            return {
                "success": True,
                "client_secret": payment_intent.client_secret,
                "payment_intent_id": payment_intent.id,
                "amount": amount,
                "currency": self.default_currency,
            }

        except StripeError as e:
            return {"success": False, "error": str(e), "error_type": "stripe_error"}

    async def verify_webhook_signature(self, payload: bytes, signature: str) -> dict[str, Any]:
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
                "error_type": "configuration_error",
            }

        try:
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=signature,
                secret=self.webhook_secret,
                tolerance=300,  # 5 minutes tolerance
            )

            return {"success": True, "event": event, "event_type": event.type, "event_id": event.id}

        except stripe.SignatureVerificationError:
            return {
                "success": False,
                "error": "Invalid webhook signature",
                "error_type": "signature_error",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Webhook verification failed: {str(e)}",
                "error_type": "verification_error",
            }

    async def get_test_payment_methods(self) -> dict[str, Any]:
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
                            "description": "Visa sucesso",
                        },
                        {
                            "number": "4000002500003155",
                            "brand": "Visa",
                            "status": "requires_authentication",
                            "description": "Visa 3DS requerido",
                        },
                        {
                            "number": "4000000000009995",
                            "brand": "Visa",
                            "status": "insufficient_funds",
                            "description": "Visa fundos insuficientes",
                        },
                    ],
                }
            ],
            "currency": "brl",
            "country": "BR",
            "locale": "pt-BR",
        }


# Global service instance
stripe_service = StripeService()
