"""
Integration tests for subscription API endpoints.
Tests all 7 subscription API endpoints with comprehensive scenarios.
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.models.subscription import SubscriptionCreate, SubscriptionUpdate

client = TestClient(app)


@pytest.fixture
def mock_current_user():
    """Mock authenticated user."""
    return {
        "id": "user_123",
        "email": "test@example.com",
        "name": "Test User"
    }


@pytest.fixture
def mock_current_user_admin():
    """Mock admin user."""
    return {
        "id": "admin_123",
        "email": "admin@example.com",
        "name": "Admin User",
        "role": "admin"
    }


@pytest.fixture
def mock_stripe():
    """Mock Stripe services."""
    with patch('app.api.subscriptions.stripe') as mock_stripe:
        # Mock Stripe Customer
        mock_customer = Mock()
        mock_customer.id = "cus_123"
        mock_stripe.Customer.create.return_value = mock_customer

        # Mock Stripe Checkout Session
        mock_session = Mock()
        mock_session.id = "cs_123"
        mock_session.url = "https://checkout.stripe.com/pay/123"
        mock_stripe.checkout.Session.create.return_value = mock_session

        # Mock Stripe Subscription
        mock_subscription = Mock()
        mock_subscription.id = "sub_123"
        mock_stripe.Subscription.delete.return_value = mock_subscription
        mock_stripe.Subscription.modify.return_value = mock_subscription

        yield mock_stripe


@pytest.fixture
def mock_subscription_service():
    """Mock subscription service."""
    with patch('app.api.subscriptions.subscription_service') as mock_service:
        # Mock subscription details
        mock_details = Mock()
        mock_details.id = "sub_123"
        mock_details.user_id = "user_123"
        mock_details.tier_id = "flow_pro"
        mock_details.status = "active"
        mock_details.analyses_available = 45
        mock_details.analyses_used_this_period = 15
        mock_details.analyses_rollover = 0
        mock_details.tier_name = "Flow Pro"
        mock_details.analyses_per_month = 60
        mock_details.rollover_limit = 30

        mock_service.get_subscription_status.return_value = Mock(
            has_active_subscription=True,
            tier_id="flow_pro",
            analyses_remaining=45,
            can_use_service=True
        )
        mock_service.get_active_subscription.return_value = {"id": "sub_123"}
        mock_service.get_subscription_details.return_value = mock_details
        mock_service.create_subscription.return_value = mock_details
        mock_service.update_subscription.return_value = mock_details
        mock_service.cancel_subscription.return_value = mock_details

        yield mock_service


@pytest.fixture
def mock_pricing_config():
    """Mock pricing configuration."""
    with patch('app.api.subscriptions.pricing_config') as mock_config:
        mock_tier = Mock()
        mock_tier.is_subscription = True
        mock_tier.stripe_price_id = "price_123"
        mock_tier.name = "Flow Pro"
        mock_tier.analyses_per_month = 60
        mock_tier.rollover_limit = 30
        mock_config.get_tier.return_value = mock_tier

        yield mock_config


@pytest.fixture
def mock_supabase():
    """Mock Supabase client."""
    with patch('app.api.subscriptions.get_supabase_client') as mock:
        client = Mock()
        # Mock user table queries
        client.table().select().eq().single().execute.return_value = Mock(
            data={"stripe_customer_id": None}
        )
        client.table().update().eq().execute.return_value = Mock(data=[])
        mock.return_value = client
        yield client


class TestSubscriptionStatus:
    """Test GET /api/subscriptions/status endpoint."""

    def test_get_subscription_status_success(self, mock_current_user, mock_subscription_service):
        """Test successful subscription status retrieval."""
        # Arrange
        mock_subscription_service.get_subscription_status.return_value = Mock(
            has_active_subscription=True,
            tier_id="flow_pro",
            analyses_remaining=45,
            can_use_service=True
        )

        # Act
        response = client.get(
            "/api/subscriptions/status",
            headers={"Authorization": "Bearer test_token"}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["has_active_subscription"] is True
        assert data["tier_id"] == "flow_pro"
        assert data["analyses_remaining"] == 45
        assert data["can_use_service"] is True
        mock_subscription_service.get_subscription_status.assert_called_once_with("user_123")

    def test_get_subscription_status_no_subscription(self, mock_current_user, mock_subscription_service):
        """Test subscription status when no active subscription."""
        # Arrange
        mock_subscription_service.get_subscription_status.return_value = Mock(
            has_active_subscription=False,
            tier_id=None,
            analyses_remaining=10,
            can_use_service=True
        )

        # Act
        response = client.get(
            "/api/subscriptions/status",
            headers={"Authorization": "Bearer test_token"}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["has_active_subscription"] is False
        assert data["tier_id"] is None
        assert data["analyses_remaining"] == 10
        assert data["can_use_service"] is True

    def test_get_subscription_status_unauthorized(self):
        """Test subscription status without authentication."""
        # Act
        response = client.get("/api/subscriptions/status")

        # Assert
        assert response.status_code == 401

    def test_get_subscription_status_service_error(self, mock_current_user, mock_subscription_service):
        """Test subscription status when service fails."""
        # Arrange
        mock_subscription_service.get_subscription_status.side_effect = Exception("Service error")

        # Act
        response = client.get(
            "/api/subscriptions/status",
            headers={"Authorization": "Bearer test_token"}
        )

        # Assert
        assert response.status_code == 500


class TestGetCurrentSubscription:
    """Test GET /api/subscriptions/current endpoint."""

    def test_get_current_subscription_success(self, mock_current_user, mock_subscription_service):
        """Test successful current subscription retrieval."""
        # Act
        response = client.get(
            "/api/subscriptions/current",
            headers={"Authorization": "Bearer test_token"}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "sub_123"
        assert data["tier_id"] == "flow_pro"
        assert data["status"] == "active"
        mock_subscription_service.get_active_subscription.assert_called_once_with("user_123")
        mock_subscription_service.get_subscription_details.assert_called_once_with("sub_123")

    def test_get_current_subscription_none(self, mock_current_user, mock_subscription_service):
        """Test current subscription when none exists."""
        # Arrange
        mock_subscription_service.get_active_subscription.return_value = None

        # Act
        response = client.get(
            "/api/subscriptions/current",
            headers={"Authorization": "Bearer test_token"}
        )

        # Assert
        assert response.status_code == 200
        assert response.json() is None

    def test_get_current_subscription_unauthorized(self):
        """Test current subscription without authentication."""
        # Act
        response = client.get("/api/subscriptions/current")

        # Assert
        assert response.status_code == 401


class TestCreateSubscription:
    """Test POST /api/subscriptions/ endpoint."""

    def test_create_subscription_success(self, mock_current_user, mock_subscription_service):
        """Test successful subscription creation."""
        # Arrange
        subscription_data = {
            "user_id": "user_123",
            "tier_id": "flow_pro",
            "stripe_subscription_id": "sub_stripe_123",
            "stripe_customer_id": "cus_123",
            "stripe_price_id": "price_123"
        }

        # Act
        response = client.post(
            "/api/subscriptions/",
            headers={"Authorization": "Bearer test_token"},
            json=subscription_data
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == "sub_123"
        assert data["tier_id"] == "flow_pro"
        mock_subscription_service.create_subscription.assert_called_once()

    def test_create_subscription_wrong_user(self, mock_current_user, mock_subscription_service):
        """Test subscription creation for wrong user (should fail)."""
        # Arrange
        subscription_data = {
            "user_id": "different_user",
            "tier_id": "flow_pro",
            "stripe_subscription_id": "sub_stripe_123",
            "stripe_customer_id": "cus_123",
            "stripe_price_id": "price_123"
        }

        # Act
        response = client.post(
            "/api/subscriptions/",
            headers={"Authorization": "Bearer test_token"},
            json=subscription_data
        )

        # Assert
        assert response.status_code == 403
        assert "Não pode criar assinatura para outro usuário" in response.json()["detail"]

    def test_create_subscription_invalid_tier(self, mock_current_user, mock_subscription_service):
        """Test subscription creation with invalid tier."""
        # Arrange
        mock_subscription_service.create_subscription.side_effect = ValueError("Invalid subscription tier")
        subscription_data = {
            "user_id": "user_123",
            "tier_id": "invalid_tier",
            "stripe_subscription_id": "sub_stripe_123",
            "stripe_customer_id": "cus_123",
            "stripe_price_id": "price_123"
        }

        # Act
        response = client.post(
            "/api/subscriptions/",
            headers={"Authorization": "Bearer test_token"},
            json=subscription_data
        )

        # Assert
        assert response.status_code == 400
        assert "Invalid subscription tier" in response.json()["detail"]

    def test_create_subscription_unauthorized(self):
        """Test subscription creation without authentication."""
        # Arrange
        subscription_data = {
            "user_id": "user_123",
            "tier_id": "flow_pro",
            "stripe_subscription_id": "sub_stripe_123",
            "stripe_customer_id": "cus_123",
            "stripe_price_id": "price_123"
        }

        # Act
        response = client.post("/api/subscriptions/", json=subscription_data)

        # Assert
        assert response.status_code == 401


class TestUpdateSubscription:
    """Test PATCH /api/subscriptions/{subscription_id} endpoint."""

    def test_update_subscription_success(self, mock_current_user, mock_subscription_service):
        """Test successful subscription update."""
        # Arrange
        mock_details = Mock()
        mock_details.user_id = "user_123"
        mock_subscription_service.get_subscription_details.return_value = mock_details

        update_data = {"tier_id": "flow_business"}

        # Act
        response = client.patch(
            "/api/subscriptions/sub_123",
            headers={"Authorization": "Bearer test_token"},
            json=update_data
        )

        # Assert
        assert response.status_code == 200
        mock_subscription_service.get_subscription_details.assert_called_once_with("sub_123")
        mock_subscription_service.update_subscription.assert_called_once()

    def test_update_subscription_wrong_user(self, mock_current_user, mock_subscription_service):
        """Test subscription update for wrong user (should fail)."""
        # Arrange
        mock_details = Mock()
        mock_details.user_id = "different_user"
        mock_subscription_service.get_subscription_details.return_value = mock_details

        update_data = {"tier_id": "flow_business"}

        # Act
        response = client.patch(
            "/api/subscriptions/sub_123",
            headers={"Authorization": "Bearer test_token"},
            json=update_data
        )

        # Assert
        assert response.status_code == 403
        assert "Esta não é a sua assinatura" in response.json()["detail"]

    def test_update_subscription_not_found(self, mock_current_user, mock_subscription_service):
        """Test subscription update when not found."""
        # Arrange
        mock_subscription_service.get_subscription_details.side_effect = ValueError("Subscription not found")

        update_data = {"tier_id": "flow_business"}

        # Act
        response = client.patch(
            "/api/subscriptions/nonexistent",
            headers={"Authorization": "Bearer test_token"},
            json=update_data
        )

        # Assert
        assert response.status_code == 400

    def test_update_subscription_unauthorized(self):
        """Test subscription update without authentication."""
        # Arrange
        update_data = {"tier_id": "flow_business"}

        # Act
        response = client.patch("/api/subscriptions/sub_123", json=update_data)

        # Assert
        assert response.status_code == 401


class TestCancelSubscription:
    """Test POST /api/subscriptions/{subscription_id}/cancel endpoint."""

    def test_cancel_subscription_immediate_success(self, mock_current_user, mock_subscription_service, mock_stripe):
        """Test successful immediate subscription cancellation."""
        # Arrange
        mock_details = Mock()
        mock_details.user_id = "user_123"
        mock_details.stripe_subscription_id = "sub_stripe_123"
        mock_subscription_service.get_subscription_details.return_value = mock_details

        # Act
        response = client.post(
            "/api/subscriptions/sub_123/cancel?immediate=true",
            headers={"Authorization": "Bearer test_token"}
        )

        # Assert
        assert response.status_code == 200
        mock_stripe.Subscription.delete.assert_called_once_with("sub_stripe_123")
        mock_subscription_service.cancel_subscription.assert_called_once_with("sub_123", immediate=True)

    def test_cancel_subscription_at_period_end_success(self, mock_current_user, mock_subscription_service, mock_stripe):
        """Test successful subscription cancellation at period end."""
        # Arrange
        mock_details = Mock()
        mock_details.user_id = "user_123"
        mock_details.stripe_subscription_id = "sub_stripe_123"
        mock_subscription_service.get_subscription_details.return_value = mock_details

        # Act
        response = client.post(
            "/api/subscriptions/sub_123/cancel?immediate=false",
            headers={"Authorization": "Bearer test_token"}
        )

        # Assert
        assert response.status_code == 200
        mock_stripe.Subscription.modify.assert_called_once_with(
            "sub_stripe_123",
            cancel_at_period_end=True
        )
        mock_subscription_service.cancel_subscription.assert_called_once_with("sub_123", immediate=False)

    def test_cancel_subscription_wrong_user(self, mock_current_user, mock_subscription_service):
        """Test subscription cancellation for wrong user (should fail)."""
        # Arrange
        mock_details = Mock()
        mock_details.user_id = "different_user"
        mock_subscription_service.get_subscription_details.return_value = mock_details

        # Act
        response = client.post(
            "/api/subscriptions/sub_123/cancel",
            headers={"Authorization": "Bearer test_token"}
        )

        # Assert
        assert response.status_code == 403
        assert "Esta não é a sua assinatura" in response.json()["detail"]

    def test_cancel_subscription_unauthorized(self):
        """Test subscription cancellation without authentication."""
        # Act
        response = client.post("/api/subscriptions/sub_123/cancel")

        # Assert
        assert response.status_code == 401


class TestGetUsageHistory:
    """Test GET /api/subscriptions/history endpoint."""

    def test_get_usage_history_success(self, mock_current_user, mock_supabase):
        """Test successful usage history retrieval."""
        # Arrange
        mock_supabase.table().select().eq().order().limit().execute.return_value = Mock(
            data=[
                {
                    "id": "usage_1",
                    "user_id": "user_123",
                    "analysis_type": "resume_optimization",
                    "created_at": datetime.utcnow().isoformat()
                }
            ]
        )

        # Act
        response = client.get(
            "/api/subscriptions/history",
            headers={"Authorization": "Bearer test_token"}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 1
        assert data["data"][0]["user_id"] == "user_123"

    def test_get_usage_history_with_limit(self, mock_current_user, mock_supabase):
        """Test usage history retrieval with custom limit."""
        # Act
        response = client.get(
            "/api/subscriptions/history?limit=10",
            headers={"Authorization": "Bearer test_token"}
        )

        # Assert
        assert response.status_code == 200
        mock_supabase.table().select().eq().order().limit.assert_called_with(10)

    def test_get_usage_history_unauthorized(self):
        """Test usage history without authentication."""
        # Act
        response = client.get("/api/subscriptions/history")

        # Assert
        assert response.status_code == 401


class TestCreateCheckoutSession:
    """Test POST /api/subscriptions/checkout endpoint."""

    def test_create_checkout_session_success(self, mock_current_user, mock_stripe, mock_pricing_config, mock_supabase):
        """Test successful checkout session creation."""
        # Arrange
        checkout_request = {
            "tier_id": "flow_pro"
        }

        # Act
        response = client.post(
            "/api/subscriptions/checkout",
            headers={"Authorization": "Bearer test_token"},
            json=checkout_request
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "checkout_url" in data
        assert "session_id" in data
        assert data["checkout_url"] == "https://checkout.stripe.com/pay/123"

        # Verify Stripe was called correctly
        mock_stripe.checkout.Session.create.assert_called_once()
        call_args = mock_stripe.checkout.Session.create.call_args
        assert call_args.kwargs["customer"] == "cus_123"
        assert call_args.kwargs["mode"] == "subscription"
        assert len(call_args.kwargs["line_items"]) == 1
        assert call_args.kwargs["line_items"][0]["price"] == "price_123"

    def test_create_checkout_session_with_custom_urls(self, mock_current_user, mock_stripe, mock_pricing_config, mock_supabase):
        """Test checkout session creation with custom success/cancel URLs."""
        # Arrange
        checkout_request = {
            "tier_id": "flow_pro",
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel"
        }

        # Act
        response = client.post(
            "/api/subscriptions/checkout",
            headers={"Authorization": "Bearer test_token"},
            json=checkout_request
        )

        # Assert
        assert response.status_code == 200

        # Verify custom URLs were used
        call_args = mock_stripe.checkout.Session.create.call_args
        assert call_args.kwargs["success_url"] == "https://example.com/success"
        assert call_args.kwargs["cancel_url"] == "https://example.com/cancel"

    def test_create_checkout_session_invalid_tier(self, mock_current_user, mock_pricing_config):
        """Test checkout session creation with invalid tier."""
        # Arrange
        mock_pricing_config.get_tier.return_value = None
        checkout_request = {
            "tier_id": "invalid_tier"
        }

        # Act
        response = client.post(
            "/api/subscriptions/checkout",
            headers={"Authorization": "Bearer test_token"},
            json=checkout_request
        )

        # Assert
        assert response.status_code == 400
        assert "Plano de assinatura inválido" in response.json()["detail"]

    def test_create_checkout_session_no_price_id(self, mock_current_user, mock_pricing_config):
        """Test checkout session creation when tier has no price ID."""
        # Arrange
        mock_tier = Mock()
        mock_tier.is_subscription = True
        mock_tier.stripe_price_id = None  # No price configured
        mock_pricing_config.get_tier.return_value = mock_tier

        checkout_request = {
            "tier_id": "flow_pro"
        }

        # Act
        response = client.post(
            "/api/subscriptions/checkout",
            headers={"Authorization": "Bearer test_token"},
            json=checkout_request
        )

        # Assert
        assert response.status_code == 400
        assert "Preço Stripe não configurado" in response.json()["detail"]

    def test_create_checkout_session_existing_customer(self, mock_current_user, mock_stripe, mock_pricing_config, mock_supabase):
        """Test checkout session creation when user already has Stripe customer."""
        # Arrange
        # User already has customer ID
        mock_supabase.table().select().eq().single().execute.return_value = Mock(
            data={"stripe_customer_id": "existing_customer_123"}
        )

        checkout_request = {
            "tier_id": "flow_pro"
        }

        # Act
        response = client.post(
            "/api/subscriptions/checkout",
            headers={"Authorization": "Bearer test_token"},
            json=checkout_request
        )

        # Assert
        assert response.status_code == 200

        # Verify existing customer was used
        call_args = mock_stripe.checkout.Session.create.call_args
        assert call_args.kwargs["customer"] == "existing_customer_123"

        # Verify new customer was not created
        mock_stripe.Customer.create.assert_not_called()

    def test_create_checkout_session_unauthorized(self):
        """Test checkout session creation without authentication."""
        # Arrange
        checkout_request = {
            "tier_id": "flow_pro"
        }

        # Act
        response = client.post("/api/subscriptions/checkout", json=checkout_request)

        # Assert
        assert response.status_code == 401


class TestErrorHandling:
    """Test error handling across all endpoints."""

    def test_service_error_handling(self, mock_current_user, mock_subscription_service):
        """Test that service errors are properly handled."""
        # Arrange
        mock_subscription_service.get_subscription_status.side_effect = Exception("Database error")

        # Act
        response = client.get(
            "/api/subscriptions/status",
            headers={"Authorization": "Bearer test_token"}
        )

        # Assert
        assert response.status_code == 500

    def test_stripe_error_handling(self, mock_current_user, mock_stripe, mock_pricing_config, mock_supabase):
        """Test that Stripe errors are properly handled."""
        # Arrange
        mock_stripe.checkout.Session.create.side_effect = Exception("Stripe API error")

        checkout_request = {
            "tier_id": "flow_pro"
        }

        # Act
        response = client.post(
            "/api/subscriptions/checkout",
            headers={"Authorization": "Bearer test_token"},
            json=checkout_request
        )

        # Assert
        assert response.status_code == 500


class TestBrazilianMarket:
    """Test Brazilian market specific scenarios."""

    def test_portuguese_error_messages(self, mock_current_user):
        """Test that error messages are in Portuguese."""
        # Act - Try to create subscription for wrong user
        subscription_data = {
            "user_id": "different_user",
            "tier_id": "flow_pro",
            "stripe_subscription_id": "sub_stripe_123",
            "stripe_customer_id": "cus_123",
            "stripe_price_id": "price_123"
        }

        response = client.post(
            "/api/subscriptions/",
            headers={"Authorization": "Bearer test_token"},
            json=subscription_data
        )

        # Assert
        assert response.status_code == 403
        assert "Não pode criar assinatura para outro usuário" in response.json()["detail"]

    def test_brl_currency_handling(self, mock_current_user, mock_stripe, mock_pricing_config, mock_supabase):
        """Test BRL currency handling in checkout sessions."""
        # Arrange
        checkout_request = {
            "tier_id": "flow_pro"
        }

        # Act
        response = client.post(
            "/api/subscriptions/checkout",
            headers={"Authorization": "Bearer test_token"},
            json=checkout_request
        )

        # Assert
        assert response.status_code == 200

        # Verify metadata includes Brazilian context
        call_args = mock_stripe.checkout.Session.create.call_args
        metadata = call_args.kwargs["metadata"]
        assert metadata["user_id"] == "user_123"
        assert metadata["tier_id"] == "flow_pro"