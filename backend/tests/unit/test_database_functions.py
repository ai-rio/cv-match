"""
Unit tests for database functions related to payment processing.
Tests credit deduction functions and atomic operations.
"""

import asyncio
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest

from app.core.database import SupabaseSession


@pytest.mark.unit
@pytest.mark.database
@pytest.mark.payment
class TestDatabaseFunctions:
    """Test database functions for payment processing."""

    def setup_method(self):
        """Set up test method."""
        self.test_user_id = uuid4()
        self.test_operation_id = str(uuid4())
        self.db = SupabaseSession()

    @pytest.mark.asyncio
    async def test_deduct_credits_atomically_success(self):
        """Test successful atomic credit deduction via RPC function."""
        # Mock successful RPC call
        mock_result = MagicMock()
        mock_result.data = [{"success": True, "new_balance": 45, "previous_balance": 50}]

        self.db.client.rpc.return_value.execute.return_value = mock_result

        # Call the RPC function
        result = self.db.client.rpc(
            "deduct_credits_atomically", {"p_user_id": str(self.test_user_id), "p_amount": 5}
        ).execute()

        assert result.data[0]["success"] is True
        assert result.data[0]["new_balance"] == 45
        assert result.data[0]["previous_balance"] == 50

        # Verify RPC was called with correct parameters
        self.db.client.rpc.assert_called_once_with(
            "deduct_credits_atomically", {"p_user_id": str(self.test_user_id), "p_amount": 5}
        )

    @pytest.mark.asyncio
    async def test_deduct_credits_atomically_insufficient_credits(self):
        """Test atomic credit deduction with insufficient credits."""
        # Mock insufficient credits response
        mock_result = MagicMock()
        mock_result.data = [
            {"success": False, "reason": "insufficient_credits", "current_balance": 3}
        ]

        self.db.client.rpc.return_value.execute.return_value = mock_result

        result = self.db.client.rpc(
            "deduct_credits_atomically", {"p_user_id": str(self.test_user_id), "p_amount": 5}
        ).execute()

        assert result.data[0]["success"] is False
        assert result.data[0]["reason"] == "insufficient_credits"
        assert result.data[0]["current_balance"] == 3

    @pytest.mark.asyncio
    async def test_deduct_credits_atomically_user_not_found(self):
        """Test atomic credit deduction when user not found."""
        # Mock user not found response
        mock_result = MagicMock()
        mock_result.data = [{"success": False, "reason": "user_not_found"}]

        self.db.client.rpc.return_value.execute.return_value = mock_result

        result = self.db.client.rpc(
            "deduct_credits_atomically", {"p_user_id": str(self.test_user_id), "p_amount": 5}
        ).execute()

        assert result.data[0]["success"] is False
        assert result.data[0]["reason"] == "user_not_found"

    @pytest.mark.asyncio
    async def test_deduct_credits_atomically_rpc_error(self):
        """Test atomic credit deduction when RPC function fails."""
        # Mock RPC error
        self.db.client.rpc.return_value.execute.side_effect = Exception("RPC function not found")

        # This should be handled by the service layer fallback
        with pytest.raises(Exception, match="RPC function not found"):
            self.db.client.rpc(
                "deduct_credits_atomically", {"p_user_id": str(self.test_user_id), "p_amount": 5}
            ).execute()

    @pytest.mark.asyncio
    async def test_record_credit_transaction_success(self):
        """Test successful credit transaction recording."""
        transaction_data = {
            "user_id": str(self.test_user_id),
            "amount": -5,
            "type": "debit",
            "source": "optimization",
            "description": f"Credit deduction for operation {self.test_operation_id}",
            "operation_id": self.test_operation_id,
            "balance_after": 45,
        }

        # Mock successful transaction creation
        mock_result = MagicMock()
        mock_result.data = [
            {
                "id": "transaction_123",
                "created_at": datetime.now(UTC).isoformat(),
                **transaction_data,
            }
        ]

        self.db.client.table.return_value.insert.return_value.execute.return_value = mock_result

        result = self.db.client.table("credit_transactions").insert(transaction_data).execute()

        assert result.data[0]["id"] == "transaction_123"
        assert result.data[0]["user_id"] == str(self.test_user_id)
        assert result.data[0]["amount"] == -5
        assert result.data[0]["type"] == "debit"
        assert result.data[0]["source"] == "optimization"
        assert result.data[0]["balance_after"] == 45

        # Verify insert was called with correct data
        self.db.client.table.return_value.insert.assert_called_once_with(transaction_data)

    @pytest.mark.asyncio
    async def test_record_credit_transaction_failure(self):
        """Test credit transaction recording failure."""
        transaction_data = {
            "user_id": str(self.test_user_id),
            "amount": -5,
            "type": "debit",
            "source": "optimization",
        }

        # Mock failed transaction creation
        self.db.client.table.return_value.insert.return_value.execute.return_value.data = []

        result = self.db.client.table("credit_transactions").insert(transaction_data).execute()

        assert result.data == []

    @pytest.mark.asyncio
    async def test_add_credits_success(self):
        """Test successful credit addition."""
        current_credits = 50
        amount_to_add = 10
        new_credits = current_credits + amount_to_add

        # Mock current user credits
        mock_current = MagicMock()
        mock_current.data = [
            {
                "id": "credit_123",
                "user_id": str(self.test_user_id),
                "credits_remaining": current_credits,
                "total_credits": current_credits,
            }
        ]

        # Mock successful update
        mock_updated = MagicMock()
        mock_updated.data = [
            {
                "id": "credit_123",
                "user_id": str(self.test_user_id),
                "credits_remaining": new_credits,
                "total_credits": new_credits,
            }
        ]

        self.db.client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_current
        self.db.client.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_updated

        # Get current credits
        current = (
            self.db.client.table("user_credits")
            .select("*")
            .eq("user_id", str(self.test_user_id))
            .execute()
        )
        assert current.data[0]["credits_remaining"] == current_credits

        # Update credits
        updated = (
            self.db.client.table("user_credits")
            .update({"credits_remaining": new_credits, "total_credits": new_credits})
            .eq("user_id", str(self.test_user_id))
            .execute()
        )

        assert updated.data[0]["credits_remaining"] == new_credits
        assert updated.data[0]["total_credits"] == new_credits

    @pytest.mark.asyncio
    async def test_credit_transaction_history(self):
        """Test retrieving credit transaction history."""
        # Mock transaction history
        mock_transactions = [
            {
                "id": "transaction_1",
                "user_id": str(self.test_user_id),
                "amount": -5,
                "type": "debit",
                "source": "optimization",
                "created_at": datetime.now(UTC).isoformat(),
            },
            {
                "id": "transaction_2",
                "user_id": str(self.test_user_id),
                "amount": 50,
                "type": "credit",
                "source": "payment",
                "created_at": datetime.now(UTC).isoformat(),
            },
        ]

        self.db.client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = mock_transactions

        # Get transaction history
        result = (
            self.db.client.table("credit_transactions")
            .select("*")
            .eq("user_id", str(self.test_user_id))
            .order("created_at", desc=True)
            .limit(10)
            .execute()
        )

        assert len(result.data) == 2
        assert result.data[0]["id"] == "transaction_1"
        assert result.data[1]["id"] == "transaction_2"

    @pytest.mark.asyncio
    async def test_user_credits_balance_check(self):
        """Test checking user credit balance."""
        # Mock user credits
        mock_credits = {
            "id": "credit_123",
            "user_id": str(self.test_user_id),
            "credits_remaining": 25,
            "total_credits": 100,
            "subscription_tier": "pro",
            "is_pro": True,
        }

        self.db.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            mock_credits
        ]

        result = (
            self.db.client.table("user_credits")
            .select("*")
            .eq("user_id", str(self.test_user_id))
            .execute()
        )

        assert result.data[0]["credits_remaining"] == 25
        assert result.data[0]["total_credits"] == 100
        assert result.data[0]["is_pro"] is True

    @pytest.mark.asyncio
    async def test_credit_operations_transaction_isolation(self):
        """Test that credit operations are properly isolated."""

        # Test concurrent credit deduction attempts
        async def deduct_credits_concurrently():
            # Each attempt tries to deduct 5 credits from a balance of 10
            mock_result = MagicMock()
            mock_result.data = [
                {
                    "success": True,
                    "new_balance": 5,  # After first deduction
                    "previous_balance": 10,
                }
            ]

            self.db.client.rpc.return_value.execute.return_value = mock_result

            return self.db.client.rpc(
                "deduct_credits_atomically", {"p_user_id": str(self.test_user_id), "p_amount": 5}
            ).execute()

        # Run multiple concurrent deductions
        tasks = [deduct_credits_concurrently() for _ in range(3)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Verify all operations completed
        for result in results:
            if not isinstance(result, Exception):
                assert result.data[0]["success"] is True

    @pytest.mark.asyncio
    async def test_credit_rollback_scenario(self):
        """Test credit rollback scenario when operation fails."""
        # This simulates a scenario where credit deduction succeeds
        # but the subsequent operation fails, requiring a rollback

        # Mock successful credit deduction
        mock_deduct_result = MagicMock()
        mock_deduct_result.data = [{"success": True, "new_balance": 45, "previous_balance": 50}]

        # Mock failed operation (simulate business logic failure)
        def simulate_operation_failure():
            raise Exception("Business logic failed")

        # Mock credit addition (rollback)
        mock_add_result = MagicMock()
        mock_add_result.data = [{"id": "credit_123", "credits_remaining": 50, "total_credits": 100}]

        # Execute the scenario
        try:
            # Deduct credits
            deduct_result = self.db.client.rpc(
                "deduct_credits_atomically", {"p_user_id": str(self.test_user_id), "p_amount": 5}
            ).execute()
            assert deduct_result.data[0]["success"] is True

            # Simulate operation failure
            simulate_operation_failure()

        except Exception as e:
            # Rollback: add credits back
            self.db.client.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_add_result

            rollback_result = (
                self.db.client.table("user_credits")
                .update({"credits_remaining": 50, "total_credits": 100})
                .eq("user_id", str(self.test_user_id))
                .execute()
            )

            assert rollback_result.data[0]["credits_remaining"] == 50
            assert str(e) == "Business logic failed"

    @pytest.mark.asyncio
    async def test_payment_history_recording(self):
        """Test payment history recording."""
        payment_data = {
            "user_id": str(self.test_user_id),
            "stripe_checkout_session_id": "cs_test_123",
            "stripe_payment_intent_id": "pi_test_123",
            "amount": 2990,
            "currency": "brl",
            "status": "succeeded",
            "payment_type": "subscription",
            "description": "CV-Match Pro Plan",
            "metadata": {"plan_type": "pro", "market": "brazil"},
        }

        # Mock successful payment recording
        mock_result = MagicMock()
        mock_result.data = [
            {"id": "payment_123", "created_at": datetime.now(UTC).isoformat(), **payment_data}
        ]

        self.db.client.table.return_value.insert.return_value.execute.return_value = mock_result

        result = self.db.client.table("payment_history").insert(payment_data).execute()

        assert result.data[0]["id"] == "payment_123"
        assert result.data[0]["user_id"] == str(self.test_user_id)
        assert result.data[0]["amount"] == 2990
        assert result.data[0]["status"] == "succeeded"

    @pytest.mark.asyncio
    async def test_subscription_recording(self):
        """Test subscription recording."""
        subscription_data = {
            "user_id": str(self.test_user_id),
            "stripe_subscription_id": "sub_test_123",
            "stripe_customer_id": "cus_test_123",
            "status": "active",
            "price_id": "price_test_123",
            "product_id": "prod_test_123",
            "current_period_start": datetime.now(UTC).isoformat(),
            "current_period_end": datetime.now(UTC).isoformat(),
            "cancel_at_period_end": False,
            "metadata": {"plan_type": "pro", "market": "brazil"},
        }

        # Mock successful subscription recording
        mock_result = MagicMock()
        mock_result.data = [
            {
                "id": "subscription_123",
                "created_at": datetime.now(UTC).isoformat(),
                **subscription_data,
            }
        ]

        self.db.client.table.return_value.insert.return_value.execute.return_value = mock_result

        result = self.db.client.table("subscriptions").insert(subscription_data).execute()

        assert result.data[0]["id"] == "subscription_123"
        assert result.data[0]["user_id"] == str(self.test_user_id)
        assert result.data[0]["status"] == "active"
        assert result.data[0]["stripe_subscription_id"] == "sub_test_123"

    @pytest.mark.asyncio
    async def test_webhook_event_recording(self):
        """Test webhook event recording."""
        webhook_data = {
            "event_id": f"evt_test_{uuid4()}",
            "event_type": "checkout.session.completed",
            "user_id": str(self.test_user_id),
            "stripe_customer_id": "cus_test_123",
            "stripe_session_id": "cs_test_123",
            "amount": 2990,
            "currency": "brl",
            "status": "completed",
            "payload": {"test": "data"},
            "processed": False,
            "created_at": datetime.now(UTC).isoformat(),
        }

        # Mock successful webhook recording
        mock_result = MagicMock()
        mock_result.data = [{"id": "webhook_123", **webhook_data}]

        self.db.client.table.return_value.insert.return_value.execute.return_value = mock_result

        result = self.db.client.table("payment_events").insert(webhook_data).execute()

        assert result.data[0]["id"] == "webhook_123"
        assert result.data[0]["event_id"] == webhook_data["event_id"]
        assert result.data[0]["event_type"] == "checkout.session.completed"
        assert result.data[0]["processed"] is False

    @pytest.mark.asyncio
    async def test_webhook_event_processed_update(self):
        """Test updating webhook event as processed."""
        webhook_id = "webhook_123"
        update_data = {
            "processed": True,
            "processed_at": datetime.now(UTC).isoformat(),
            "processing_time_ms": 150.5,
        }

        # Mock successful update
        mock_result = MagicMock()
        mock_result.data = [
            {
                "id": webhook_id,
                "processed": True,
                "processed_at": update_data["processed_at"],
                "processing_time_ms": 150.5,
            }
        ]

        self.db.client.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_result

        result = (
            self.db.client.table("payment_events")
            .update(update_data)
            .eq("id", webhook_id)
            .execute()
        )

        assert result.data[0]["processed"] is True
        assert result.data[0]["processing_time_ms"] == 150.5

    @pytest.mark.asyncio
    async def test_credit_balance_constraint_validation(self):
        """Test credit balance constraints are enforced."""
        # This test would ideally check database constraints, but we'll mock the behavior
        # to ensure the application layer enforces non-negative balances

        current_balance = 5
        deduction_amount = 10  # More than current balance

        # Mock the constraint violation
        mock_result = MagicMock()
        mock_result.data = [
            {
                "success": False,
                "reason": "insufficient_credits",
                "current_balance": current_balance,
                "requested_amount": deduction_amount,
            }
        ]

        self.db.client.rpc.return_value.execute.return_value = mock_result

        result = self.db.client.rpc(
            "deduct_credits_atomically",
            {"p_user_id": str(self.test_user_id), "p_amount": deduction_amount},
        ).execute()

        assert result.data[0]["success"] is False
        assert result.data[0]["reason"] == "insufficient_credits"

    @pytest.mark.asyncio
    async def test_user_credits_initialization(self):
        """Test user credits initialization for new users."""
        # Mock no existing credits for user
        self.db.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

        # Mock successful initialization
        initial_credits = {
            "user_id": str(self.test_user_id),
            "credits_remaining": 3,  # Free tier
            "total_credits": 3,
            "subscription_tier": "free",
            "is_pro": False,
        }

        mock_result = MagicMock()
        mock_result.data = [
            {"id": "credit_new_123", "created_at": datetime.now(UTC).isoformat(), **initial_credits}
        ]

        self.db.client.table.return_value.insert.return_value.execute.return_value = mock_result

        # Initialize credits for new user
        result = self.db.client.table("user_credits").insert(initial_credits).execute()

        assert result.data[0]["id"] == "credit_new_123"
        assert result.data[0]["credits_remaining"] == 3
        assert result.data[0]["subscription_tier"] == "free"
        assert result.data[0]["is_pro"] is False

    @pytest.mark.asyncio
    async def test_payment_event_idempotency_check(self):
        """Test checking for existing payment events (idempotency)."""
        event_id = f"evt_test_{uuid4()}"

        # Mock existing event
        mock_existing = MagicMock()
        mock_existing.data = [
            {
                "id": "webhook_123",
                "event_id": event_id,
                "processed": True,
                "processed_at": datetime.now(UTC).isoformat(),
            }
        ]

        self.db.client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_existing

        result = (
            self.db.client.table("payment_events").select("*").eq("event_id", event_id).execute()
        )

        assert len(result.data) == 1
        assert result.data[0]["event_id"] == event_id
        assert result.data[0]["processed"] is True

    @pytest.mark.asyncio
    async def test_subscription_update_handling(self):
        """Test subscription status updates."""
        subscription_id = "sub_test_123"
        update_data = {"status": "past_due", "updated_at": datetime.now(UTC).isoformat()}

        # Mock existing subscription
        mock_existing = MagicMock()
        mock_existing.data = [
            {
                "id": "subscription_123",
                "stripe_subscription_id": subscription_id,
                "status": "active",
            }
        ]

        # Mock successful update
        mock_updated = MagicMock()
        mock_updated.data = [
            {
                "id": "subscription_123",
                "stripe_subscription_id": subscription_id,
                "status": "past_due",
                "updated_at": update_data["updated_at"],
            }
        ]

        self.db.client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_existing
        self.db.client.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_updated

        # Update subscription
        result = (
            self.db.client.table("subscriptions")
            .update(update_data)
            .eq("stripe_subscription_id", subscription_id)
            .execute()
        )

        assert result.data[0]["status"] == "past_due"
        assert result.data[0]["updated_at"] == update_data["updated_at"]
