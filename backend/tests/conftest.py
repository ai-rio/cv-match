"""
pytest configuration and shared fixtures for payment webhook tests.
"""

import asyncio
import json
import os
from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timezone
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock

import pytest
import stripe
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_stripe() -> MagicMock:
    """Mock Stripe client."""
    mock = MagicMock()
    mock.api_key = "sk_test_1234567890"
    return mock


@pytest.fixture
def mock_supabase() -> AsyncMock:
    """Mock Supabase client."""
    mock = AsyncMock()
    mock.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    mock.table.return_value.insert.return_value.execute.return_value.data = [{"id": "test-id"}]
    mock.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{"id": "test-id"}]
    return mock


@pytest.fixture
def webhook_headers() -> dict[str, str]:
    """Default webhook headers."""
    return {
        "stripe-signature": "whsec_test_signature",
        "content-type": "application/json",
    }


@pytest.fixture
def sample_user() -> dict[str, Any]:
    """Sample user data for testing."""
    return {
        "id": "user_1234567890",
        "email": "test@example.com",
        "name": "Test User",
        "stripe_customer_id": "cus_test1234567890",
    }


@pytest.fixture
def sample_checkout_session() -> dict[str, Any]:
    """Sample Stripe checkout session data."""
    return {
        "id": "cs_test_1234567890",
        "object": "checkout.session",
        "created": 1704067200,  # 2024-01-01 00:00:00 UTC
        "currency": "brl",
        "amount_total": 2990,  # R$ 29.90 in cents
        "customer": "cus_test1234567890",
        "payment_intent": "pi_test1234567890",
        "payment_status": "paid",
        "status": "complete",
        "success_url": "https://example.com/success",
        "cancel_url": "https://example.com/cancel",
        "metadata": {
            "user_id": "user_1234567890",
            "product": "cv_optimization",
            "plan": "pro_monthly"
        },
        "subscription": "sub_test1234567890",
    }


@pytest.fixture
def sample_subscription() -> dict[str, Any]:
    """Sample Stripe subscription data."""
    return {
        "id": "sub_test1234567890",
        "object": "subscription",
        "created": 1704067200,
        "current_period_start": 1704067200,
        "current_period_end": 1706745600,  # +30 days
        "customer": "cus_test1234567890",
        "status": "active",
        "items": {
            "data": [
                {
                    "id": "si_test1234567890",
                    "price": {
                        "id": "price_test1234567890",
                        "currency": "brl",
                        "unit_amount": 2990,
                        "recurring": {
                            "interval": "month",
                            "interval_count": 1,
                        },
                        "product": "prod_test1234567890",
                    },
                    "quantity": 1,
                }
            ]
        },
        "metadata": {
            "user_id": "user_1234567890",
            "plan": "pro_monthly"
        },
    }


@pytest.fixture
def sample_invoice() -> dict[str, Any]:
    """Sample Stripe invoice data."""
    return {
        "id": "in_test1234567890",
        "object": "invoice",
        "created": 1704067200,
        "customer": "cus_test1234567890",
        "subscription": "sub_test1234567890",
        "status": "paid",
        "amount_paid": 2990,
        "currency": "brl",
        "period_start": 1704067200,
        "period_end": 1706745600,
        "payment_intent": "pi_test1234567890",
        "metadata": {
            "user_id": "user_1234567890"
        },
    }


@pytest.fixture
def sample_payment_intent() -> dict[str, Any]:
    """Sample Stripe payment intent data."""
    return {
        "id": "pi_test1234567890",
        "object": "payment_intent",
        "created": 1704067200,
        "amount": 2990,
        "currency": "brl",
        "customer": "cus_test1234567890",
        "status": "succeeded",
        "payment_method": "pm_test1234567890",
        "metadata": {
            "user_id": "user_1234567890",
            "product": "cv_optimization"
        },
    }


@pytest.fixture
def webhook_events_base() -> dict[str, Any]:
    """Base structure for webhook events."""
    return {
        "id": "evt_test1234567890",
        "object": "event",
        "api_version": "2023-10-16",
        "created": int(datetime.now(UTC).timestamp()),
        "livemode": False,
        "pending_webhooks": 0,
        "request": {
            "id": "req_test1234567890",
            "idempotency_key": "test_key_1234567890"
        },
        "type": "",
        "data": {
            "object": {}
        }
    }


@pytest.fixture
def brazilian_pricing() -> dict[str, Any]:
    """Brazilian pricing configuration."""
    return {
        "free": {
            "name": "Grátis",
            "price": 0,
            "currency": "brl",
            "credits": 5,
            "features": [
                "5 análises de currículo por mês",
                "Matching básico",
                "Download em PDF"
            ]
        },
        "pro": {
            "name": "Profissional",
            "price": 2990,  # R$ 29,90
            "currency": "brl",
            "credits": 50,
            "features": [
                "50 análises de currículo por mês",
                "Matching avançado com IA",
                "Templates brasileiros",
                "Suporte prioritário",
                "Análise de compatibilidade com vagas"
            ]
        },
        "enterprise": {
            "name": "Empresarial",
            "price": 9990,  # R$ 99,90
            "currency": "brl",
            "credits": 200,
            "features": [
                "Análises ilimitadas",
                "Dashboard de recrutamento",
                "API de integração",
                "Múltiplos usuários",
                "Relatórios avançados",
                "Suporte dedicado"
            ]
        }
    }


# Environment setup for tests
@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_1234567890")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test_1234567890")
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("SUPABASE_URL", "http://localhost:54321")
    monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test_service_key")
