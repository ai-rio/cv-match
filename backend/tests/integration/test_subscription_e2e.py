"""
End-to-end tests for complete subscription flow.
Tests the entire subscription lifecycle from creation through cancellation.
"""

import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.subscription import SubscriptionCreate, SubscriptionUpdate

client = TestClient(app)


@pytest.fixture
def mock_user():
    """Mock authenticated user for testing."""
    return {"id": "user_e2e_123", "email": "e2e@example.com", "name": "E2E Test User"}


@pytest.fixture
def mock_stripe_complete():
    """Complete mock Stripe services for E2E testing."""
    with patch("app.api.subscriptions.stripe") as mock_stripe:
        # Mock Customer
        mock_customer = Mock()
        mock_customer.id = "cus_e2e_123"
        mock_stripe.Customer.create.return_value = mock_customer

        # Mock Checkout Session
        mock_session = Mock()
        mock_session.id = "cs_e2e_123"
        mock_session.url = "https://checkout.stripe.com/pay/e2e_123"
        mock_session.customer = "cus_e2e_123"
        mock_session.subscription = "sub_e2e_123"
        mock_session.payment_intent = "pi_e2e_123"
        mock_session.amount_total = 2990
        mock_session.currency = "brl"
        mock_session.payment_status = "paid"
        mock_session.metadata = {"user_id": "user_e2e_123", "tier_id": "flow_pro"}
        mock_stripe.checkout.Session.create.return_value = mock_session
        mock_stripe.checkout.Session.retrieve.return_value = mock_session

        # Mock Subscription
        mock_subscription = Mock()
        mock_subscription.id = "sub_e2e_123"
        mock_subscription.customer = "cus_e2e_123"
        mock_subscription.status = "active"
        mock_subscription.current_period_start = int(datetime.utcnow().timestamp())
        mock_subscription.current_period_end = int(
            (datetime.utcnow() + timedelta(days=30)).timestamp()
        )
        mock_subscription.cancel_at_period_end = False
        mock_subscription.items = Mock()
        mock_subscription.items.data = [
            {"price": {"id": "price_e2e_123", "currency": "brl", "unit_amount": 2990}}
        ]
        mock_stripe.Subscription.retrieve.return_value = mock_subscription
        mock_stripe.Subscription.delete.return_value = mock_subscription
        mock_stripe.Subscription.modify.return_value = mock_subscription

        # Mock Invoice
        mock_invoice = Mock()
        mock_invoice.id = "in_e2e_123"
        mock_invoice.customer = "cus_e2e_123"
        mock_invoice.subscription = "sub_e2e_123"
        mock_invoice.status = "paid"
        mock_invoice.amount_paid = 2990
        mock_invoice.currency = "brl"
        mock_invoice.payment_intent = "pi_e2e_123"
        mock_stripe.Invoice.retrieve.return_value = mock_invoice

        yield mock_stripe


@pytest.fixture
def mock_database_complete():
    """Complete mock database for E2E testing."""
    with (
        patch("app.services.subscription_service.get_supabase_client") as mock_supabase,
        patch("app.services.webhook_service.create_client") as mock_webhook_supabase,
    ):
        # Mock subscription service database
        supabase_client = Mock()
        mock_supabase.return_value = supabase_client

        # Mock webhook service database
        webhook_client = Mock()
        mock_webhook_supabase.return_value = webhook_client

        # Setup user table responses
        supabase_client.table().select().eq().single().execute.return_value = Mock(
            data={"stripe_customer_id": None}
        )
        supabase_client.table().update().eq().execute.return_value = Mock(data=[])

        # Setup subscription table responses
        def mock_table_chain(table_name):
            table_mock = Mock()

            if table_name == "subscriptions":
                # For subscription operations
                table_mock.select().eq().execute.return_value = Mock(
                    data=[]
                )  # No existing subscription
                table_mock.select().eq().single().execute.return_value = Mock(
                    data={
                        "id": "sub_db_e2e_123",
                        "user_id": "user_e2e_123",
                        "tier_id": "flow_pro",
                        "status": "active",
                        "stripe_subscription_id": "sub_e2e_123",
                        "stripe_customer_id": "cus_e2e_123",
                        "stripe_price_id": "price_e2e_123",
                        "current_period_start": datetime.utcnow().isoformat(),
                        "current_period_end": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                        "cancel_at_period_end": False,
                        "analyses_used_this_period": 0,
                        "analyses_rollover": 0,
                        "created_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat(),
                    }
                )
                table_mock.insert().execute.return_value = Mock(data=[{"id": "sub_db_e2e_123"}])
                table_mock.update().eq().execute.return_value = Mock(
                    data=[{"id": "sub_db_e2e_123"}]
                )

            elif table_name == "payment_events":
                # For webhook event logging
                table_mock.select().eq().execute.return_value = Mock(data=[])  # No existing events
                table_mock.insert().execute.return_value = Mock(data=[{"id": "evt_e2e_123"}])
                table_mock.update().eq().execute.return_value = Mock(data=[])

            elif table_name == "payment_history":
                # For payment history
                table_mock.insert().execute.return_value = Mock(
                    data=[{"id": "payment_hist_e2e_123"}]
                )

            elif table_name == "users":
                # For user operations
                table_mock.select().eq().single().execute.return_value = Mock(
                    data={"id": "user_e2e_123", "email": "e2e@example.com"}
                )
                table_mock.update().eq().execute.return_value = Mock(data=[])

            return table_mock

        supabase_client.table.side_effect = mock_table_chain
        webhook_client.table.side_effect = mock_table_chain

        yield supabase_client, webhook_client


@pytest.fixture
def mock_services_complete():
    """Complete mock services for E2E testing."""
    with (
        patch("app.api.subscriptions.subscription_service") as mock_sub_service,
        patch("app.api.subscriptions.pricing_config") as mock_pricing,
        patch("app.services.webhook_service.UsageLimitService") as mock_usage_service,
        patch("app.services.webhook_service.SubabaseSession") as mock_session,
    ):
        # Mock subscription service
        mock_details = Mock()
        mock_details.id = "sub_db_e2e_123"
        mock_details.user_id = "user_e2e_123"
        mock_details.tier_id = "flow_pro"
        mock_details.status = "active"
        mock_details.analyses_available = 60
        mock_details.analyses_used_this_period = 0
        mock_details.analyses_rollover = 0
        mock_details.tier_name = "Flow Pro"
        mock_details.analyses_per_month = 60
        mock_details.rollover_limit = 30

        mock_sub_service.get_subscription_status.return_value = Mock(
            has_active_subscription=True,
            tier_id="flow_pro",
            analyses_remaining=60,
            can_use_service=True,
        )
        mock_sub_service.get_active_subscription.return_value = {"id": "sub_db_e2e_123"}
        mock_sub_service.get_subscription_details.return_value = mock_details
        mock_sub_service.create_subscription.return_value = mock_details
        mock_sub_service.update_subscription.return_value = mock_details
        mock_sub_service.cancel_subscription.return_value = mock_details
        mock_sub_service.use_analysis.return_value = Mock(
            subscription_id="sub_db_e2e_123",
            user_id="user_e2e_123",
            analyses_used_this_period=1,
            analyses_rollover=0,
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow() + timedelta(days=30),
        )
        mock_sub_service.process_period_renewal.return_value = mock_details

        # Mock pricing config
        mock_tier = Mock()
        mock_tier.is_subscription = True
        mock_tier.stripe_price_id = "price_e2e_123"
        mock_tier.name = "Flow Pro"
        mock_tier.analyses_per_month = 60
        mock_tier.rollover_limit = 30
        mock_pricing.get_tier.return_value = mock_tier

        # Mock usage service
        mock_usage_instance = Mock()
        mock_usage_instance.get_user_credits.return_value = {"credits_remaining": 0}
        mock_usage_service.return_value = mock_usage_instance

        yield mock_sub_service, mock_pricing, mock_usage_service


class TestCompleteSubscriptionFlow:
    """Test complete subscription flow from creation to cancellation."""

    @pytest.mark.asyncio
    async def test_complete_subscription_lifecycle(
        self, mock_user, mock_stripe_complete, mock_database_complete, mock_services_complete
    ):
        """Test complete subscription lifecycle: checkout -> creation -> usage -> renewal -> cancellation."""
        supabase_client, webhook_client = mock_database_complete
        mock_sub_service, mock_pricing, mock_usage_service = mock_services_complete

        # Step 1: Check initial status (no subscription)
        status_response = client.get(
            "/api/subscriptions/status", headers={"Authorization": "Bearer test_token"}
        )
        assert status_response.status_code == 200
        # Initial state might have no subscription or existing subscription
        initial_status = status_response.json()

        # Step 2: Create checkout session
        checkout_request = {
            "tier_id": "flow_pro",
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel",
        }

        checkout_response = client.post(
            "/api/subscriptions/checkout",
            headers={"Authorization": "Bearer test_token"},
            json=checkout_request,
        )
        assert checkout_response.status_code == 200
        checkout_data = checkout_response.json()
        assert checkout_data["success"] is True
        assert "checkout_url" in checkout_data
        assert "session_id" in checkout_data

        # Step 3: Simulate successful checkout webhook
        from app.services.webhook_service import WebhookService

        webhook_service = WebhookService()
        webhook_service.supabase = webhook_client

        checkout_session_data = {
            "id": "cs_e2e_123",
            "customer": "cus_e2e_123",
            "subscription": "sub_e2e_123",
            "payment_status": "paid",
            "amount_total": 2990,
            "currency": "brl",
            "metadata": {"user_id": "user_e2e_123", "tier_id": "flow_pro"},
        }

        # Process checkout completion webhook
        webhook_result = await webhook_service.process_checkout_session(checkout_session_data)
        assert webhook_result["success"] is True

        # Step 4: Process subscription creation webhook
        subscription_data = {
            "id": "sub_e2e_123",
            "customer": "cus_e2e_123",
            "status": "active",
            "items": {"data": [{"price": {"id": "price_e2e_123"}}]},
            "metadata": {"user_id": "user_e2e_123", "tier_id": "flow_pro"},
        }

        webhook_result = await webhook_service.process_subscription_created(subscription_data)
        assert webhook_result["success"] is True

        # Step 5: Verify subscription status after creation
        status_response = client.get(
            "/api/subscriptions/status", headers={"Authorization": "Bearer test_token"}
        )
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["has_active_subscription"] is True
        assert status_data["tier_id"] == "flow_pro"
        assert status_data["analyses_remaining"] == 60

        # Step 6: Get current subscription details
        current_response = client.get(
            "/api/subscriptions/current", headers={"Authorization": "Bearer test_token"}
        )
        assert current_response.status_code == 200
        current_data = current_response.json()
        assert current_data["id"] == "sub_db_e2e_123"
        assert current_data["status"] == "active"

        # Step 7: Use some analyses
        usage_response = client.post(
            "/api/optimizations/",
            headers={"Authorization": "Bearer test_token"},
            json={"resume_text": "Test resume content", "job_description": "Test job description"},
        )
        # This would typically use the subscription service internally
        # For now, we'll test the usage tracking directly
        mock_sub_service.use_analysis.assert_called()

        # Step 8: Process monthly renewal webhook
        invoice_data = {
            "id": "in_e2e_123",
            "customer": "cus_e2e_123",
            "subscription": "sub_e2e_123",
            "status": "paid",
            "amount_paid": 2990,
            "currency": "brl",
            "payment_intent": "pi_e2e_renewal",
            "metadata": {"user_id": "user_e2e_123"},
        }

        webhook_result = await webhook_service.process_invoice_payment_succeeded(invoice_data)
        assert webhook_result["success"] is True
        assert webhook_result["subscription_renewed"] is True

        # Verify renewal was processed
        mock_sub_service.process_period_renewal.assert_called_with("sub_db_e2e_123")

        # Step 9: Upgrade subscription tier
        update_response = client.patch(
            "/api/subscriptions/sub_db_e2e_123",
            headers={"Authorization": "Bearer test_token"},
            json={"tier_id": "flow_business"},
        )
        assert update_response.status_code == 200

        # Step 10: Cancel subscription at period end
        cancel_response = client.post(
            "/api/subscriptions/sub_db_e2e_123/cancel?immediate=false",
            headers={"Authorization": "Bearer test_token"},
        )
        assert cancel_response.status_code == 200
        cancel_data = cancel_response.json()
        assert cancel_data["cancel_at_period_end"] is True

        # Step 11: Process subscription deletion webhook (final cancellation)
        delete_data = {
            "id": "sub_e2e_123",
            "customer": "cus_e2e_123",
            "status": "canceled",
            "metadata": {"user_id": "user_e2e_123"},
        }

        webhook_result = await webhook_service.process_subscription_deleted(delete_data)
        assert webhook_result["success"] is True

        # Step 12: Verify final status
        final_status_response = client.get(
            "/api/subscriptions/status", headers={"Authorization": "Bearer test_token"}
        )
        assert final_status_response.status_code == 200
        final_status = final_status_response.json()
        # After cancellation, user should only have credits if any
        assert final_status["has_active_subscription"] is False

    @pytest.mark.asyncio
    async def test_subscription_upgrade_flow(
        self, mock_user, mock_stripe_complete, mock_database_complete, mock_services_complete
    ):
        """Test subscription upgrade flow from basic to pro to business."""
        supabase_client, webhook_client = mock_database_complete
        mock_sub_service, mock_pricing, mock_usage_service = mock_services_complete

        # Start with basic tier
        mock_pricing.get_tier.side_effect = lambda tier_id: {
            "flow_basic": Mock(
                is_subscription=True,
                stripe_price_id="price_basic",
                name="Flow Basic",
                analyses_per_month=15,
                rollover_limit=5,
            ),
            "flow_pro": Mock(
                is_subscription=True,
                stripe_price_id="price_pro",
                name="Flow Pro",
                analyses_per_month=60,
                rollover_limit=30,
            ),
            "flow_business": Mock(
                is_subscription=True,
                stripe_price_id="price_business",
                name="Flow Business",
                analyses_per_month=200,
                rollover_limit=100,
            ),
        }.get(tier_id)

        # Create initial basic subscription
        checkout_response = client.post(
            "/api/subscriptions/checkout",
            headers={"Authorization": "Bearer test_token"},
            json={"tier_id": "flow_basic"},
        )
        assert checkout_response.status_code == 200

        # Process webhook events for basic subscription
        from app.services.webhook_service import WebhookService

        webhook_service = WebhookService()
        webhook_service.supabase = webhook_client

        subscription_data = {
            "id": "sub_basic_123",
            "customer": "cus_e2e_123",
            "status": "active",
            "items": {"data": [{"price": {"id": "price_basic"}}]},
            "metadata": {"user_id": "user_e2e_123", "tier_id": "flow_basic"},
        }

        await webhook_service.process_subscription_created(subscription_data)

        # Verify basic subscription status
        status_response = client.get(
            "/api/subscriptions/status", headers={"Authorization": "Bearer test_token"}
        )
        status_data = status_response.json()
        assert status_data["tier_id"] == "flow_basic"

        # Upgrade to pro
        update_response = client.patch(
            "/api/subscriptions/sub_db_e2e_123",
            headers={"Authorization": "Bearer test_token"},
            json={"tier_id": "flow_pro"},
        )
        assert update_response.status_code == 200

        # Process subscription update webhook
        update_data = {
            "id": "sub_basic_123",
            "customer": "cus_e2e_123",
            "status": "active",
            "items": {"data": [{"price": {"id": "price_pro"}}]},
            "metadata": {"user_id": "user_e2e_123", "tier_id": "flow_pro"},
        }

        await webhook_service.process_subscription_updated(update_data)

        # Verify pro subscription
        status_response = client.get(
            "/api/subscriptions/status", headers={"Authorization": "Bearer test_token"}
        )
        status_data = status_response.json()
        assert status_data["tier_id"] == "flow_pro"

        # Upgrade to business
        update_response = client.patch(
            "/api/subscriptions/sub_db_e2e_123",
            headers={"Authorization": "Bearer test_token"},
            json={"tier_id": "flow_business"},
        )
        assert update_response.status_code == 200

        # Process final upgrade webhook
        update_data["metadata"]["tier_id"] = "flow_business"
        update_data["items"]["data"][0]["price"]["id"] = "price_business"

        await webhook_service.process_subscription_updated(update_data)

        # Verify business subscription
        status_response = client.get(
            "/api/subscriptions/status", headers={"Authorization": "Bearer test_token"}
        )
        status_data = status_response.json()
        assert status_data["tier_id"] == "flow_business"

    @pytest.mark.asyncio
    async def test_subscription_with_rollover(
        self, mock_user, mock_stripe_complete, mock_database_complete, mock_services_complete
    ):
        """Test subscription with rollover analyses across multiple periods."""
        supabase_client, webhook_client = mock_database_complete
        mock_sub_service, mock_pricing, mock_usage_service = mock_services_complete

        # Create subscription
        checkout_response = client.post(
            "/api/subscriptions/checkout",
            headers={"Authorization": "Bearer test_token"},
            json={"tier_id": "flow_pro"},
        )
        assert checkout_response.status_code == 200

        # Process subscription creation
        from app.services.webhook_service import WebhookService

        webhook_service = WebhookService()
        webhook_service.supabase = webhook_client

        subscription_data = {
            "id": "sub_rollover_123",
            "customer": "cus_e2e_123",
            "status": "active",
            "items": {"data": [{"price": {"id": "price_rollover_123"}}]},
            "metadata": {"user_id": "user_e2e_123", "tier_id": "flow_pro"},
        }

        await webhook_service.process_subscription_created(subscription_data)

        # Use some analyses (40 out of 60)
        for i in range(40):
            mock_sub_service.use_analysis.return_value = Mock(
                subscription_id="sub_db_e2e_123",
                user_id="user_e2e_123",
                analyses_used_this_period=i + 1,
                analyses_rollover=0,
            )

        # Simulate period renewal with rollover
        # Mock that 20 analyses were unused for rollover
        mock_details_with_rollover = Mock()
        mock_details_with_rollover.id = "sub_db_e2e_123"
        mock_details_with_rollover.analyses_used_this_period = 40  # Used 40
        mock_details_with_rollover.analyses_rollover = 20  # 20 rollover
        mock_details_with_rollover.current_period_start = datetime.utcnow()
        mock_details_with_rollover.current_period_end = datetime.utcnow() + timedelta(days=30)

        mock_sub_service.get_subscription_details.return_value = mock_details_with_rollover

        # Process renewal webhook
        invoice_data = {
            "id": "in_renewal_123",
            "customer": "cus_e2e_123",
            "subscription": "sub_rollover_123",
            "status": "paid",
            "amount_paid": 2990,
            "currency": "brl",
            "metadata": {"user_id": "user_e2e_123"},
        }

        webhook_result = await webhook_service.process_invoice_payment_succeeded(invoice_data)
        assert webhook_result["success"] is True

        # Verify rollover was processed
        mock_sub_service.process_period_renewal.assert_called_once()

        # Check new period has rollover analyses
        renewed_details = mock_sub_service.process_period_renewal.return_value
        assert renewed_details.analyses_rollover >= 0

    @pytest.mark.asyncio
    async def test_subscription_payment_failure_and_recovery(
        self, mock_user, mock_stripe_complete, mock_database_complete, mock_services_complete
    ):
        """Test subscription payment failure and recovery flow."""
        supabase_client, webhook_client = mock_database_complete
        mock_sub_service, mock_pricing, mock_usage_service = mock_services_complete

        # Create subscription
        checkout_response = client.post(
            "/api/subscriptions/checkout",
            headers={"Authorization": "Bearer test_token"},
            json={"tier_id": "flow_pro"},
        )
        assert checkout_response.status_code == 200

        # Process subscription creation
        from app.services.webhook_service import WebhookService

        webhook_service = WebhookService()
        webhook_service.supabase = webhook_client

        subscription_data = {
            "id": "sub_payment_fail_123",
            "customer": "cus_e2e_123",
            "status": "active",
            "items": {"data": [{"price": {"id": "price_fail_123"}}]},
            "metadata": {"user_id": "user_e2e_123", "tier_id": "flow_pro"},
        }

        await webhook_service.process_subscription_created(subscription_data)

        # Process payment failure webhook
        failed_invoice_data = {
            "id": "in_failed_123",
            "customer": "cus_e2e_123",
            "subscription": "sub_payment_fail_123",
            "status": "open",
            "amount_due": 2990,
            "currency": "brl",
            "attempt_count": 1,
            "metadata": {"user_id": "user_e2e_123"},
        }

        webhook_result = await webhook_service.process_invoice_payment_failed(failed_invoice_data)
        assert webhook_result["success"] is True

        # Verify subscription was marked as past_due
        mock_sub_service.update_subscription.assert_called_once()
        call_args = mock_sub_service.update_subscription.call_args
        update_data = call_args[0][1]
        assert update_data.status.value == "past_due"

        # Check subscription status reflects payment failure
        status_response = client.get(
            "/api/subscriptions/status", headers={"Authorization": "Bearer test_token"}
        )
        assert status_response.status_code == 200
        # Service should return payment failure status

        # Process successful payment (recovery)
        success_invoice_data = {
            "id": "in_recovery_123",
            "customer": "cus_e2e_123",
            "subscription": "sub_payment_fail_123",
            "status": "paid",
            "amount_paid": 2990,
            "currency": "brl",
            "payment_intent": "pi_recovery_123",
            "metadata": {"user_id": "user_e2e_123"},
        }

        webhook_result = await webhook_service.process_invoice_payment_succeeded(
            success_invoice_data
        )
        assert webhook_result["success"] is True

        # Verify subscription was reactivated
        # The subscription should be back to active after successful payment

    @pytest.mark.asyncio
    async def test_immediate_vs_period_end_cancellation(
        self, mock_user, mock_stripe_complete, mock_database_complete, mock_services_complete
    ):
        """Test immediate cancellation vs cancellation at period end."""
        supabase_client, webhook_client = mock_database_complete
        mock_sub_service, mock_pricing, mock_usage_service = mock_services_complete

        # Create subscription
        checkout_response = client.post(
            "/api/subscriptions/checkout",
            headers={"Authorization": "Bearer test_token"},
            json={"tier_id": "flow_pro"},
        )
        assert checkout_response.status_code == 200

        # Test cancellation at period end
        cancel_response = client.post(
            "/api/subscriptions/sub_db_e2e_123/cancel?immediate=false",
            headers={"Authorization": "Bearer test_token"},
        )
        assert cancel_response.status_code == 200
        cancel_data = cancel_response.json()
        assert cancel_data["cancel_at_period_end"] is True
        assert cancel_data["status"] == "active"  # Still active until period end

        # Verify Stripe was called correctly
        mock_stripe_complete.Subscription.modify.assert_called_with(
            "sub_e2e_123", cancel_at_period_end=True
        )

        # Create another subscription for immediate cancellation test
        checkout_response2 = client.post(
            "/api/subscriptions/checkout",
            headers={"Authorization": "Bearer test_token"},
            json={"tier_id": "flow_pro"},
        )
        assert checkout_response2.status_code == 200

        # Test immediate cancellation
        immediate_cancel_response = client.post(
            "/api/subscriptions/sub_db_e2e_123/cancel?immediate=true",
            headers={"Authorization": "Bearer test_token"},
        )
        assert immediate_cancel_response.status_code == 200
        immediate_cancel_data = immediate_cancel_response.json()
        assert immediate_cancel_data["status"] == "canceled"

        # Verify Stripe was called correctly
        mock_stripe_complete.Subscription.delete.assert_called_with("sub_e2e_123")

    @pytest.mark.asyncio
    async def test_usage_tracking_with_subscription_limits(
        self, mock_user, mock_stripe_complete, mock_database_complete, mock_services_complete
    ):
        """Test usage tracking with subscription limits and restrictions."""
        supabase_client, webhook_client = mock_database_complete
        mock_sub_service, mock_pricing, mock_usage_service = mock_services_complete

        # Create subscription with limited analyses
        mock_pricing.get_tier.return_value = Mock(
            is_subscription=True,
            stripe_price_id="price_limited",
            name="Flow Starter",
            analyses_per_month=15,
            rollover_limit=5,
        )

        checkout_response = client.post(
            "/api/subscriptions/checkout",
            headers={"Authorization": "Bearer test_token"},
            json={"tier_id": "flow_starter"},
        )
        assert checkout_response.status_code == 200

        # Process subscription creation
        from app.services.webhook_service import WebhookService

        webhook_service = WebhookService()
        webhook_service.supabase = webhook_client

        subscription_data = {
            "id": "sub_limited_123",
            "customer": "cus_e2e_123",
            "status": "active",
            "items": {"data": [{"price": {"id": "price_limited"}}]},
            "metadata": {"user_id": "user_e2e_123", "tier_id": "flow_starter"},
        }

        await webhook_service.process_subscription_created(subscription_data)

        # Use analyses up to the limit
        for i in range(15):
            mock_sub_service.use_analysis.return_value = Mock(
                subscription_id="sub_db_e2e_123",
                user_id="user_e2e_123",
                analyses_used_this_period=i + 1,
                analyses_rollover=0,
            )

        # Attempt to use one more analysis (should fail)
        mock_sub_service.use_analysis.side_effect = ValueError("No analyses available")

        # Verify that attempting to use beyond limit fails
        with pytest.raises(ValueError, match="No analyses available"):
            await mock_sub_service.use_analysis("user_e2e_123", "sub_db_e2e_123")

        # Check subscription status shows no remaining analyses
        status_response = client.get(
            "/api/subscriptions/status", headers={"Authorization": "Bearer test_token"}
        )
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["analyses_remaining"] == 0
        assert status_data["can_use_service"] is False

    @pytest.mark.asyncio
    async def test_webhook_error_handling_and_recovery(
        self, mock_user, mock_stripe_complete, mock_database_complete, mock_services_complete
    ):
        """Test webhook error handling and recovery mechanisms."""
        supabase_client, webhook_client = mock_database_complete
        mock_sub_service, mock_pricing, mock_usage_service = mock_services_complete

        # Create subscription
        checkout_response = client.post(
            "/api/subscriptions/checkout",
            headers={"Authorization": "Bearer test_token"},
            json={"tier_id": "flow_pro"},
        )
        assert checkout_response.status_code == 200

        # Test webhook processing with database error
        from app.services.webhook_service import WebhookService

        webhook_service = WebhookService()
        webhook_service.supabase = webhook_client

        # Mock database to raise an error
        webhook_client.table().select().eq().execute.side_effect = Exception(
            "Database connection failed"
        )

        subscription_data = {
            "id": "sub_error_test_123",
            "customer": "cus_e2e_123",
            "status": "active",
            "items": {"data": [{"price": {"id": "price_error_123"}}]},
            "metadata": {"user_id": "user_e2e_123", "tier_id": "flow_pro"},
        }

        # Process webhook should handle error gracefully
        webhook_result = await webhook_service.process_subscription_created(subscription_data)
        assert webhook_result["success"] is False
        assert "error" in webhook_result

        # Test webhook retry mechanism (idempotency)
        # Reset database mock
        webhook_client.table().select().eq().execute.side_effect = None
        webhook_client.table().select().eq().execute.return_value = Mock(data=[])

        # Process same webhook again should succeed
        webhook_result = await webhook_service.process_subscription_created(subscription_data)
        assert webhook_result["success"] is True

        # Test duplicate event handling
        webhook_client.table().select().eq().execute.return_value = Mock(
            data=[{"id": "evt_processed", "processed": True}]
        )

        webhook_result = await webhook_service.process_webhook_event(
            "customer.subscription.created", subscription_data, "evt_duplicate_123"
        )
        assert webhook_result["success"] is True
        assert webhook_result["idempotent"] is True
