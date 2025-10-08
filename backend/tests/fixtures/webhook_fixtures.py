"""
Webhook test fixtures and utilities for payment testing.
"""

import hashlib
import hmac
import json
from datetime import UTC, datetime, timezone
from typing import Any, Dict, List
from unittest.mock import MagicMock

import stripe


class WebhookFixtureGenerator:
    """Generates webhook event payloads for testing."""

    def __init__(self):
        self.event_counter = 0

    def generate_event_id(self) -> str:
        """Generate unique event ID."""
        self.event_counter += 1
        return f"evt_test_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}_{self.event_counter:04d}"

    def create_checkout_session_completed_event(
        self,
        session_data: dict[str, Any],
        event_id: str = None
    ) -> dict[str, Any]:
        """Create checkout.session.completed webhook event."""
        return {
            "id": event_id or self.generate_event_id(),
            "object": "event",
            "api_version": "2023-10-16",
            "created": int(datetime.now(UTC).timestamp()),
            "livemode": False,
            "pending_webhooks": 0,
            "request": {
                "id": f"req_test_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
                "idempotency_key": f"checkout_key_{datetime.now(UTC).timestamp()}"
            },
            "type": "checkout.session.completed",
            "data": {
                "object": session_data
            }
        }

    def create_invoice_payment_succeeded_event(
        self,
        invoice_data: dict[str, Any],
        event_id: str = None
    ) -> dict[str, Any]:
        """Create invoice.payment_succeeded webhook event."""
        return {
            "id": event_id or self.generate_event_id(),
            "object": "event",
            "api_version": "2023-10-16",
            "created": int(datetime.now(UTC).timestamp()),
            "livemode": False,
            "pending_webhooks": 0,
            "request": {
                "id": f"req_test_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
                "idempotency_key": f"invoice_key_{datetime.now(UTC).timestamp()}"
            },
            "type": "invoice.payment_succeeded",
            "data": {
                "object": invoice_data
            }
        }

    def create_invoice_payment_failed_event(
        self,
        invoice_data: dict[str, Any],
        event_id: str = None
    ) -> dict[str, Any]:
        """Create invoice.payment_failed webhook event."""
        return {
            "id": event_id or self.generate_event_id(),
            "object": "event",
            "api_version": "2023-10-16",
            "created": int(datetime.now(UTC).timestamp()),
            "livemode": False,
            "pending_webhooks": 0,
            "request": {
                "id": f"req_test_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
                "idempotency_key": f"invoice_failed_key_{datetime.now(UTC).timestamp()}"
            },
            "type": "invoice.payment_failed",
            "data": {
                "object": invoice_data
            }
        }

    def create_customer_subscription_created_event(
        self,
        subscription_data: dict[str, Any],
        event_id: str = None
    ) -> dict[str, Any]:
        """Create customer.subscription.created webhook event."""
        return {
            "id": event_id or self.generate_event_id(),
            "object": "event",
            "api_version": "2023-10-16",
            "created": int(datetime.now(UTC).timestamp()),
            "livemode": False,
            "pending_webhooks": 0,
            "request": {
                "id": f"req_test_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
                "idempotency_key": f"sub_create_key_{datetime.now(UTC).timestamp()}"
            },
            "type": "customer.subscription.created",
            "data": {
                "object": subscription_data
            }
        }

    def create_customer_subscription_updated_event(
        self,
        subscription_data: dict[str, Any],
        event_id: str = None
    ) -> dict[str, Any]:
        """Create customer.subscription.updated webhook event."""
        return {
            "id": event_id or self.generate_event_id(),
            "object": "event",
            "api_version": "2023-10-16",
            "created": int(datetime.now(UTC).timestamp()),
            "livemode": False,
            "pending_webhooks": 0,
            "request": {
                "id": f"req_test_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
                "idempotency_key": f"sub_update_key_{datetime.now(UTC).timestamp()}"
            },
            "type": "customer.subscription.updated",
            "data": {
                "object": subscription_data
            }
        }

    def create_customer_subscription_deleted_event(
        self,
        subscription_data: dict[str, Any],
        event_id: str = None
    ) -> dict[str, Any]:
        """Create customer.subscription.deleted webhook event."""
        return {
            "id": event_id or self.generate_event_id(),
            "object": "event",
            "api_version": "2023-10-16",
            "created": int(datetime.now(UTC).timestamp()),
            "livemode": False,
            "pending_webhooks": 0,
            "request": {
                "id": f"req_test_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
                "idempotency_key": f"sub_delete_key_{datetime.now(UTC).timestamp()}"
            },
            "type": "customer.subscription.deleted",
            "data": {
                "object": subscription_data
            }
        }


class WebhookSignatureGenerator:
    """Generates webhook signatures for testing."""

    def __init__(self, webhook_secret: str = "whsec_test_1234567890"):
        self.webhook_secret = webhook_secret

    def generate_signature(self, payload: str, timestamp: int = None) -> str:
        """Generate Stripe webhook signature."""
        if timestamp is None:
            timestamp = int(datetime.now(UTC).timestamp())

        signed_payload = f"{timestamp}.{payload}"
        signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return f"t={timestamp},v1={signature}"

    def generate_headers(self, payload: str) -> dict[str, str]:
        """Generate complete webhook headers with signature."""
        timestamp = int(datetime.now(UTC).timestamp())
        signature = self.generate_signature(payload, timestamp)

        return {
            "stripe-signature": signature,
            "content-type": "application/json",
            "stripe-request-id": f"req_test_{timestamp}",
        }


class BrazilianWebhookFixtures:
    """Brazilian-specific webhook fixtures."""

    @staticmethod
    def create_brazilian_checkout_session(
        user_id: str,
        plan_type: str = "pro",
        amount: int = 2990
    ) -> dict[str, Any]:
        """Create Brazilian checkout session data with unique IDs."""
        plan_configs = {
            "pro": {
                "name": "Plano Profissional",
                "description": "Análise avançada de currículo com IA",
                "price": 2990,
            },
            "enterprise": {
                "name": "Plano Empresarial",
                "description": "Solução completa para recrutamento",
                "price": 9990,
            },
            "lifetime": {
                "name": "Acesso Vitalício",
                "description": "Acesso vitalício ao plano profissional",
                "price": 29700,
            }
        }

        config = plan_configs.get(plan_type, plan_configs["pro"])
        timestamp = int(datetime.now(UTC).timestamp())

        return {
            "id": f"cs_test_brazilian_{timestamp}",
            "object": "checkout.session",
            "created": timestamp,
            "currency": "brl",
            "amount_total": config["price"],
            "customer": f"cus_brazilian_{timestamp}",
            "payment_intent": f"pi_brazilian_{timestamp}",
            "payment_status": "paid",
            "status": "complete",
            "success_url": "https://cv-match.com/sucesso",
            "cancel_url": "https://cv-match.com/cancelar",
            "metadata": {
                "user_id": user_id,
                "product": "cv_optimization",
                "plan": plan_type,
                "market": "brazil",
                "language": "pt-br"
            },
            "customer_details": {
                "email": "usuario@exemplo.com.br",
                "name": "João Silva",
                "address": {
                    "country": "BR",
                    "state": "SP",
                    "city": "São Paulo"
                }
            },
            "subscription": f"sub_brazilian_{timestamp}" if plan_type in ["pro", "enterprise"] else None,
        }

    @staticmethod
    def create_brazilian_subscription(
        user_id: str,
        plan_type: str = "pro"
    ) -> dict[str, Any]:
        """Create Brazilian subscription data with unique IDs."""
        price_configs = {
            "pro": {
                "unit_amount": 2990,  # R$ 29,90
                "recurring": {"interval": "month"}
            },
            "enterprise": {
                "unit_amount": 9990,  # R$ 99,90
                "recurring": {"interval": "month"}
            }
        }

        config = price_configs.get(plan_type, price_configs["pro"])
        timestamp = int(datetime.now(UTC).timestamp())

        return {
            "id": f"sub_brazilian_{timestamp}",
            "object": "subscription",
            "created": timestamp,
            "current_period_start": timestamp,
            "current_period_end": timestamp + (30 * 24 * 60 * 60),
            "customer": f"cus_brazilian_{timestamp}",
            "status": "active",
            "items": {
                "data": [
                    {
                        "id": f"si_brazilian_{timestamp}",
                        "price": {
                            "id": f"price_brazilian_{plan_type}_{timestamp}",
                            "currency": "brl",
                            "unit_amount": config["unit_amount"],
                            "recurring": config["recurring"],
                            "product": f"prod_brazilian_cv_optimization_{timestamp}",
                            "nickname": f"CV-Match {plan_type.title()} (BRL)"
                        },
                        "quantity": 1,
                    }
                ]
            },
            "metadata": {
                "user_id": user_id,
                "plan": plan_type,
                "market": "brazil",
                "language": "pt-br",
                "tax_region": "BR"
            },
            "default_payment_method": f"pm_brazilian_card_{timestamp}",
        }


# Mock data generators
class MockDataGenerator:
    """Generates mock data for testing."""

    @staticmethod
    def create_mock_user(**overrides) -> dict[str, Any]:
        """Create mock user data."""
        defaults = {
            "id": "user_test_1234567890",
            "email": "test@example.com",
            "name": "Test User",
            "stripe_customer_id": "cus_test_1234567890",
            "plan": "free",
            "credits": 5,
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
        }
        defaults.update(overrides)
        return defaults

    @staticmethod
    def create_mock_payment_history(**overrides) -> dict[str, Any]:
        """Create mock payment history record."""
        defaults = {
            "id": "payment_test_1234567890",
            "user_id": "user_test_1234567890",
            "stripe_payment_id": "pi_test_1234567890",
            "stripe_checkout_session_id": "cs_test_1234567890",
            "amount": 2990,
            "currency": "brl",
            "status": "completed",
            "payment_type": "subscription",
            "description": "Plano Profissional Mensal",
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
        }
        defaults.update(overrides)
        return defaults

    @staticmethod
    def create_mock_subscription(**overrides) -> dict[str, Any]:
        """Create mock subscription record."""
        defaults = {
            "id": "sub_test_1234567890",
            "user_id": "user_test_1234567890",
            "stripe_subscription_id": "sub_stripe_1234567890",
            "stripe_customer_id": "cus_stripe_1234567890",
            "status": "active",
            "price_id": "price_test_1234567890",
            "product_id": "prod_test_1234567890",
            "current_period_start": datetime.now(UTC).isoformat(),
            "current_period_end": datetime.now(UTC).isoformat(),
            "cancel_at_period_end": False,
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
        }
        defaults.update(overrides)
        return defaults

    @staticmethod
    def create_mock_webhook_event(**overrides) -> dict[str, Any]:
        """Create mock webhook event record."""
        defaults = {
            "id": "webhook_test_1234567890",
            "stripe_event_id": "evt_test_1234567890",
            "event_type": "checkout.session.completed",
            "processed": False,
            "processing_started_at": None,
            "processing_completed_at": None,
            "processed_at": None,
            "error_message": None,
            "processing_time_ms": None,
            "data": {},
            "created_at": datetime.now(UTC).isoformat(),
            "request_id": "req_test_1234567890",
            "client_ip": "127.0.0.1",
        }
        defaults.update(overrides)
        return defaults
