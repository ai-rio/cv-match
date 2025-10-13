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
    mock.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
        {"id": "test-id"}
    ]
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
        "id": "8b73efd7-50ae-4d41-b8b7-7edb69ff11f6",
        "email": "carlos@ai.rio.br",
        "name": "Test User",
        "stripe_customer_id": "cus_test1234567890",
    }


@pytest.fixture
def sample_checkout_session() -> dict[str, Any]:
    """Sample Stripe checkout session data with unique IDs."""
    timestamp = int(datetime.now(UTC).timestamp())
    return {
        "id": f"cs_test_{timestamp}",
        "object": "checkout.session",
        "created": timestamp,
        "currency": "brl",
        "amount_total": 2990,  # R$ 29.90 in cents
        "customer": f"cus_test_{timestamp}",
        "payment_intent": f"pi_test_{timestamp}",
        "payment_status": "paid",
        "status": "complete",
        "success_url": "https://example.com/success",
        "cancel_url": "https://example.com/cancel",
        "metadata": {
            "user_id": "8b73efd7-50ae-4d41-b8b7-7edb69ff11f6",
            "product": "cv_optimization",
            "plan": "pro_monthly",
        },
        "subscription": f"sub_test_{timestamp}",
    }


@pytest.fixture
def sample_subscription() -> dict[str, Any]:
    """Sample Stripe subscription data with unique IDs."""
    timestamp = int(datetime.now(UTC).timestamp())
    return {
        "id": f"sub_test_{timestamp}",
        "object": "subscription",
        "created": timestamp,
        "current_period_start": timestamp,
        "current_period_end": timestamp + (30 * 24 * 60 * 60),  # +30 days
        "customer": f"cus_test_{timestamp}",
        "status": "active",
        "items": {
            "data": [
                {
                    "id": f"si_test_{timestamp}",
                    "price": {
                        "id": f"price_test_{timestamp}",
                        "currency": "brl",
                        "unit_amount": 2990,
                        "recurring": {
                            "interval": "month",
                            "interval_count": 1,
                        },
                        "product": f"prod_test_{timestamp}",
                    },
                    "quantity": 1,
                }
            ]
        },
        "metadata": {"user_id": "8b73efd7-50ae-4d41-b8b7-7edb69ff11f6", "plan": "pro_monthly"},
    }


@pytest.fixture
def sample_invoice() -> dict[str, Any]:
    """Sample Stripe invoice data with unique IDs."""
    timestamp = int(datetime.now(UTC).timestamp())
    return {
        "id": f"in_test_{timestamp}",
        "object": "invoice",
        "created": timestamp,
        "customer": f"cus_test_{timestamp}",
        "subscription": f"sub_test_{timestamp}",
        "status": "paid",
        "amount_paid": 2990,
        "currency": "brl",
        "period_start": timestamp,
        "period_end": timestamp + (30 * 24 * 60 * 60),
        "payment_intent": f"pi_test_{timestamp}",
        "metadata": {"user_id": "8b73efd7-50ae-4d41-b8b7-7edb69ff11f6"},
    }


@pytest.fixture
def sample_payment_intent() -> dict[str, Any]:
    """Sample Stripe payment intent data with unique IDs."""
    timestamp = int(datetime.now(UTC).timestamp())
    return {
        "id": f"pi_test_{timestamp}",
        "object": "payment_intent",
        "created": timestamp,
        "amount": 2990,
        "currency": "brl",
        "customer": f"cus_test_{timestamp}",
        "status": "succeeded",
        "payment_method": f"pm_test_{timestamp}",
        "metadata": {
            "user_id": "8b73efd7-50ae-4d41-b8b7-7edb69ff11f6",
            "product": "cv_optimization",
        },
    }


@pytest.fixture
def webhook_events_base() -> dict[str, Any]:
    """Base structure for webhook events with unique IDs."""
    timestamp = int(datetime.now(UTC).timestamp())
    return {
        "id": f"evt_test_{timestamp}",
        "object": "event",
        "api_version": "2023-10-16",
        "created": timestamp,
        "livemode": False,
        "pending_webhooks": 0,
        "request": {"id": f"req_test_{timestamp}", "idempotency_key": f"test_key_{timestamp}"},
        "type": "",
        "data": {"object": {}},
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
            "features": ["5 análises de currículo por mês", "Matching básico", "Download em PDF"],
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
                "Análise de compatibilidade com vagas",
            ],
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
                "Suporte dedicado",
            ],
        },
    }


@pytest.fixture
async def cleanup_test_data():
    """Cleanup test data before and after each test."""
    # Define test patterns to clean up (dynamic IDs generated with timestamps)
    # We'll clean up any test data created in the last hour to avoid conflicts

    # Clean up before test
    await _cleanup_test_records()

    yield

    # Clean up after test
    await _cleanup_test_records()


async def _cleanup_test_records():
    """Clean up test records from all relevant tables."""
    try:
        from supabase import create_client

        from app.core.config import settings

        # Create Supabase client
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

        # Clean up payment_history - remove test records
        result = (
            supabase.table("payment_history")
            .select("*")
            .ilike("stripe_payment_id", "pi_test_%")
            .execute()
        )
        for record in result.data or []:
            supabase.table("payment_history").delete().eq("id", record["id"]).execute()

        # Clean up stripe_webhook_events - remove test records
        result = (
            supabase.table("stripe_webhook_events")
            .select("*")
            .ilike("stripe_event_id", "evt_test_%")
            .execute()
        )
        for record in result.data or []:
            supabase.table("stripe_webhook_events").delete().eq("id", record["id"]).execute()

        # Clean up old static test data (legacy)
        static_patterns = [
            "pi_test1234567890",
            "cs_test1234567890",
            "cus_test1234567890",
            "sub_test1234567890",
            "in_test1234567890",
            "evt_test1234567890",
            "req_test1234567890",
        ]

        for pattern in static_patterns:
            # Clean up payment_history
            supabase.table("payment_history").delete().or_(
                f"stripe_payment_id.eq.{pattern},stripe_checkout_session_id.eq.{pattern}"
            ).execute()

            # Clean up webhook events
            supabase.table("stripe_webhook_events").delete().or_(
                f"stripe_event_id.eq.{pattern},request_id.eq.{pattern}"
            ).execute()

            # Clean up subscriptions
            supabase.table("subscriptions").delete().or_(
                f"stripe_subscription_id.eq.{pattern},stripe_customer_id.eq.{pattern}"
            ).execute()

    except Exception as e:
        # Log error but don't fail tests for cleanup issues
        print(f"Warning: Cleanup failed: {e}")


# Environment setup for tests
@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_1234567890")
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test_1234567890")
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("SUPABASE_URL", "http://localhost:54321")
    monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test_service_key")
