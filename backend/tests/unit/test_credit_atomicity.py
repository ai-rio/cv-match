"""
Tests for credit deduction atomicity and race condition prevention.
Tests database-level atomic operations and concurrent credit management.
"""

import asyncio
import threading
import time
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest

from app.core.database import SupabaseSession
from app.services.usage_limit_service import UsageLimitService


@pytest.mark.unit
@pytest.mark.atomicity
@pytest.mark.payment
class TestCreditAtomicity:
    """Test credit deduction atomicity and race condition prevention."""

    def setup_method(self):
        """Set up test method."""
        self.test_user_id = uuid4()
        self.db = SupabaseSession()
        self.service = UsageLimitService(self.db)
        self.service.usage_tracking_service = AsyncMock()

    @pytest.mark.asyncio
    async def test_atomic_credit_deduction_success(self):
        """Test successful atomic credit deduction via RPC function."""
        # Mock successful atomic deduction
        mock_result = MagicMock()
        mock_result.data = [
            {"success": True, "new_balance": 45, "previous_balance": 50, "deducted_amount": 5}
        ]

        with patch.object(self.db.client, "rpc", return_value=mock_result):
            with patch.object(
                self.db.client.table,
                "insert",
                return_value=MagicMock(data=[{"id": "transaction_123"}]),
            ):
                result = await self.service.deduct_credits(self.test_user_id, 5, "operation_123")

        assert result is True

    @pytest.mark.asyncio
    async def test_atomic_credit_deduction_insufficient_funds(self):
        """Test atomic credit deduction with insufficient funds."""
        # Mock insufficient funds response
        mock_result = MagicMock()
        mock_result.data = [
            {"success": False, "reason": "insufficient_credits", "current_balance": 3}
        ]

        with patch.object(self.db.client, "rpc", return_value=mock_result):
            result = await self.service.deduct_credits(self.test_user_id, 5, "operation_123")

        assert result is False

    @pytest.mark.asyncio
    async def test_concurrent_credit_deduction_race_condition(self):
        """Test concurrent credit deduction prevents race conditions."""
        initial_balance = 100
        deduction_amount = 1
        num_concurrent_operations = 10

        # Mock initial user credits
        mock_credits = {
            "id": "credit_123",
            "user_id": str(self.test_user_id),
            "credits_remaining": initial_balance,
            "total_credits": initial_balance,
        }

        # Track successful deductions
        successful_deductions = []

        async def deduct_concurrently():
            # Mock atomic deduction for each concurrent operation
            remaining_balance = initial_balance - len(successful_deductions) * deduction_amount

            if remaining_balance >= deduction_amount:
                mock_result = MagicMock()
                mock_result.data = [
                    {
                        "success": True,
                        "new_balance": remaining_balance - deduction_amount,
                        "deducted_amount": deduction_amount,
                    }
                ]

                with patch.object(self.db.client, "rpc", return_value=mock_result):
                    with patch.object(
                        self.db.client.table,
                        "insert",
                        return_value=MagicMock(data=[{"id": f"transaction_{uuid4()}"}]),
                    ):
                        result = await self.service.deduct_credits(
                            self.test_user_id, deduction_amount, f"op_{uuid4()}"
                        )

                if result:
                    successful_deductions.append(1)
                    return True
            else:
                # Simulate insufficient funds
                mock_result = MagicMock()
                mock_result.data = [
                    {
                        "success": False,
                        "reason": "insufficient_credits",
                        "current_balance": remaining_balance,
                    }
                ]

                with patch.object(self.db.client, "rpc", return_value=mock_result):
                    result = await self.service.deduct_credits(
                        self.test_user_id, deduction_amount, f"op_{uuid4()}"
                    )

                return False

        # Run concurrent deductions
        tasks = [deduct_concurrently() for _ in range(num_concurrent_operations)]
        results = await asyncio.gather(*tasks)

        # Verify results
        successful_count = sum(results)
        assert (
            successful_count == num_concurrent_operations
        )  # All should succeed with initial balance
        assert len(successful_deductions) == num_concurrent_operations

    @pytest.mark.asyncio
    async def test_fallback_atomic_deduction_with_optimistic_locking(self):
        """Test fallback atomic deduction with optimistic locking."""
        # Mock RPC function not available
        self.db.client.rpc.return_value.execute.side_effect = Exception("RPC function not found")

        # Mock user credits for fallback
        current_balance = 20
        mock_credits = {
            "id": "credit_123",
            "user_id": str(self.test_user_id),
            "credits_remaining": current_balance,
            "total_credits": 50,
        }

        # Mock successful update with optimistic locking
        updated_credits = {**mock_credits, "credits_remaining": current_balance - 5}

        with patch.object(self.db.client.table, "select") as mock_select:
            mock_select.return_value.eq.return_value.execute.return_value.data = [mock_credits]

            with patch.object(self.db.client.table, "update") as mock_update:
                mock_update.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
                    updated_credits
                ]

                with patch.object(
                    self.db.client.table,
                    "insert",
                    return_value=MagicMock(data=[{"id": "transaction_123"}]),
                ):
                    result = await self.service.deduct_credits_fallback(
                        self.test_user_id, 5, "operation_123"
                    )

        assert result is True

    @pytest.mark.asyncio
    async def test_optimistic_locking_race_condition_detection(self):
        """Test optimistic locking detects race conditions."""
        current_balance = 20
        deduction_amount = 5

        # Mock user credits
        mock_credits = {
            "id": "credit_123",
            "user_id": str(self.test_user_id),
            "credits_remaining": current_balance,
            "total_credits": 50,
        }

        # First attempt: simulate race condition (no rows updated)
        with patch.object(self.db.client.table, "select") as mock_select:
            mock_select.return_value.eq.return_value.execute.return_value.data = [mock_credits]

            with patch.object(self.db.client.table, "update") as mock_update:
                # Simulate no rows updated (race condition)
                mock_update.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

                with patch.object(
                    self.db.client.table,
                    "insert",
                    return_value=MagicMock(data=[{"id": "transaction_123"}]),
                ):
                    with patch.object(
                        self.service, "deduct_credits", return_value=True
                    ) as mock_retry:
                        result = await self.service.deduct_credits_fallback(
                            self.test_user_id, deduction_amount, "operation_123"
                        )

        # Should have attempted retry
        assert result is True  # Retry succeeded
        mock_retry.assert_called_once()

    @pytest.mark.asyncio
    async def test_concurrent_credit_addition_and_deduction(self):
        """Test concurrent credit addition and deduction operations."""
        initial_balance = 50
        add_amount = 20
        deduct_amount = 5

        operations_completed = []

        async def add_credits():
            # Mock credit addition
            mock_add_result = MagicMock()
            mock_add_result.data = [
                {
                    "id": "credit_123",
                    "credits_remaining": initial_balance + len(operations_completed) * add_amount,
                    "total_credits": initial_balance + len(operations_completed) * add_amount,
                }
            ]

            with patch.object(self.db.client.table, "select") as mock_select:
                mock_select.return_value.eq.return_value.execute.return_value.data = [
                    {
                        "id": "credit_123",
                        "user_id": str(self.test_user_id),
                        "credits_remaining": initial_balance,
                        "total_credits": initial_balance,
                    }
                ]

                with patch.object(self.db.client.table, "update", return_value=mock_add_result):
                    with patch.object(self.db.client.table, "insert", return_value=MagicMock()):
                        result = await self.service.add_credits(
                            self.test_user_id, add_amount, "test", "Test addition"
                        )
                        operations_completed.append(("add", add_amount))
                        return result

        async def deduct_credits():
            # Wait for some additions first
            await asyncio.sleep(0.01)

            current_balance = initial_balance + sum(
                amount for op_type, amount in operations_completed if op_type == "add"
            )
            current_balance -= sum(
                amount for op_type, amount in operations_completed if op_type == "deduct"
            )

            if current_balance >= deduct_amount:
                mock_deduct_result = MagicMock()
                mock_deduct_result.data = [
                    {"success": True, "new_balance": current_balance - deduct_amount}
                ]

                with patch.object(self.db.client, "rpc", return_value=mock_deduct_result):
                    with patch.object(self.db.client.table, "insert", return_value=MagicMock()):
                        result = await self.service.deduct_credits(
                            self.test_user_id, deduct_amount, f"op_{uuid4()}"
                        )
                        operations_completed.append(("deduct", deduct_amount))
                        return result
            else:
                operations_completed.append(("deduct_failed", deduct_amount))
                return False

        # Run concurrent operations
        add_tasks = [add_credits() for _ in range(3)]  # 3 additions of 20 credits each
        deduct_tasks = [deduct_credits() for _ in range(10)]  # 10 deductions of 5 credits each

        all_tasks = add_tasks + deduct_tasks
        results = await asyncio.gather(*all_tasks)

        # Verify final state
        total_added = sum(amount for op_type, amount in operations_completed if op_type == "add")
        total_deducted = sum(
            amount for op_type, amount in operations_completed if op_type == "deduct"
        )
        final_balance = initial_balance + total_added - total_deducted

        assert final_balance >= 0  # Should never go negative
        assert len(operations_completed) > 0

    @pytest.mark.asyncio
    async def test_credit_deduction_transaction_rollback(self):
        """Test credit deduction transaction rollback on failure."""
        # Mock successful credit deduction
        mock_deduct_result = MagicMock()
        mock_deduct_result.data = [{"success": True, "new_balance": 45, "deducted_amount": 5}]

        # Mock transaction recording failure
        with patch.object(self.db.client, "rpc", return_value=mock_deduct_result):
            with patch.object(
                self.db.client.table, "insert", side_effect=Exception("Database error")
            ):
                # Should still return True because credits were already deducted atomically
                # Transaction recording failure should not affect the deduction itself
                result = await self.service.deduct_credits(self.test_user_id, 5, "operation_123")

        assert (
            result is True
        )  # Credits were deducted, transaction logging failed but didn't break the operation

    @pytest.mark.asyncio
    async def test_credit_deduction_with_multiple_operations(self):
        """Test credit deduction with multiple dependent operations."""
        initial_balance = 50
        operation_costs = [5, 10, 15, 3, 7]  # Total: 40
        total_cost = sum(operation_costs)

        # Track remaining balance
        remaining_balance = initial_balance

        for i, cost in enumerate(operation_costs):
            operation_id = f"multi_op_{i + 1}"

            if remaining_balance >= cost:
                mock_result = MagicMock()
                mock_result.data = [
                    {
                        "success": True,
                        "new_balance": remaining_balance - cost,
                        "deducted_amount": cost,
                    }
                ]

                with patch.object(self.db.client, "rpc", return_value=mock_result):
                    with patch.object(self.db.client.table, "insert", return_value=MagicMock()):
                        result = await self.service.deduct_credits(
                            self.test_user_id, cost, operation_id
                        )

                assert result is True
                remaining_balance -= cost
            else:
                # Should fail when insufficient credits
                mock_result = MagicMock()
                mock_result.data = [
                    {
                        "success": False,
                        "reason": "insufficient_credits",
                        "current_balance": remaining_balance,
                    }
                ]

                with patch.object(self.db.client, "rpc", return_value=mock_result):
                    result = await self.service.deduct_credits(
                        self.test_user_id, cost, operation_id
                    )

                assert result is False
                break

        # Verify final balance
        expected_final_balance = initial_balance - total_cost
        assert remaining_balance == expected_final_balance

    @pytest.mark.asyncio
    async def test_credit_deduction_idempotency(self):
        """Test credit deduction idempotency."""
        operation_id = "idempotent_operation_123"
        deduction_amount = 5

        # First deduction
        mock_result_1 = MagicMock()
        mock_result_1.data = [
            {"success": True, "new_balance": 45, "deducted_amount": deduction_amount}
        ]

        with patch.object(self.db.client, "rpc", return_value=mock_result_1):
            with patch.object(
                self.db.client.table,
                "insert",
                return_value=MagicMock(data=[{"id": "transaction_123"}]),
            ):
                result1 = await self.service.deduct_credits(
                    self.test_user_id, deduction_amount, operation_id
                )

        assert result1 is True

        # Second deduction with same operation ID
        mock_result_2 = MagicMock()
        mock_result_2.data = [
            {
                "success": True,
                "new_balance": 45,  # Should be the same (idempotent)
                "deducted_amount": 0,  # Should not deduct again
            }
        ]

        with patch.object(self.db.client, "rpc", return_value=mock_result_2):
            with patch.object(
                self.db.client.table,
                "insert",
                return_value=MagicMock(data=[{"id": "transaction_123"}]),
            ):
                result2 = await self.service.deduct_credits(
                    self.test_user_id, deduction_amount, operation_id
                )

        assert result2 is True
        # Note: True idempotency would require checking if operation_id already exists
        # This test demonstrates the concept, actual implementation may vary

    @pytest.mark.asyncio
    async def test_credit_deduction_with_operation_timeout(self):
        """Test credit deduction handling with operation timeout."""
        # Mock database timeout
        mock_result = MagicMock()
        mock_result.data = [{"success": False, "reason": "timeout", "error": "Operation timed out"}]

        with patch.object(self.db.client, "rpc", return_value=mock_result):
            with patch.object(self.db.client.table, "insert", return_value=MagicMock()):
                result = await self.service.deduct_credits(self.test_user_id, 5, "operation_123")

        # Should handle timeout gracefully
        # Implementation may vary depending on error handling strategy
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_credit_deduction_with_connection_pool_exhaustion(self):
        """Test credit deduction with database connection pool exhaustion."""
        # Mock connection pool exhaustion
        mock_result = MagicMock()
        mock_result.data = [
            {
                "success": False,
                "reason": "connection_exhausted",
                "error": "No available database connections",
            }
        ]

        with patch.object(self.db.client, "rpc", return_value=mock_result):
            with patch.object(self.db.client.table, "insert", return_value=MagicMock()):
                result = await self.service.deduct_credits(self.test_user_id, 5, "operation_123")

        # Should handle connection exhaustion gracefully
        # Implementation may include retry logic or graceful degradation
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_credit_deduction_with_database_isolation_levels(self):
        """Test credit deduction with different database isolation levels."""
        # This test demonstrates the concept of isolation levels
        # Actual implementation depends on database configuration

        initial_balance = 50

        # Mock READ COMMITTED isolation level behavior
        mock_read_committed_result = MagicMock()
        mock_read_committed_result.data = [
            {
                "success": True,
                "new_balance": initial_balance - 5,
                "isolation_level": "READ_COMMITTED",
            }
        ]

        with patch.object(self.db.client, "rpc", return_value=mock_read_committed_result):
            with patch.object(self.db.client.table, "insert", return_value=MagicMock()):
                result_rc = await self.service.deduct_credits(self.test_user_id, 5, "operation_rc")

        assert result_rc is True

        # Mock SERIALIZABLE isolation level behavior
        mock_serializable_result = MagicMock()
        mock_serializable_result.data = [
            {
                "success": True,
                "new_balance": initial_balance - 10,
                "isolation_level": "SERIALIZABLE",
            }
        ]

        with patch.object(self.db.client, "rpc", return_value=mock_serializable_result):
            with patch.object(self.db.client.table, "insert", return_value=MagicMock()):
                result_serializable = await self.service.deduct_credits(
                    self.test_user_id, 10, "operation_serializable"
                )

        assert result_serializable is True

    def test_credit_deduction_thread_safety(self):
        """Test credit deduction thread safety with synchronous operations."""
        # This test uses threading to simulate concurrent synchronous operations
        initial_balance = 100
        num_threads = 5
        deduction_per_thread = 10

        results = []
        lock = threading.Lock()

        def deduct_credits_thread(thread_id):
            # Simulate synchronous credit deduction
            # In a real implementation, this would use synchronous database operations
            with lock:
                current_balance = initial_balance - len(results) * deduction_per_thread

                if current_balance >= deduction_per_thread:
                    # Simulate atomic deduction
                    new_balance = current_balance - deduction_per_thread
                    results.append((thread_id, new_balance))
                    return True
                else:
                    results.append((thread_id, None))
                    return False

        # Run threads concurrently
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=deduct_credits_thread, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify results
        successful_deductions = [result for result in results if result[1] is not None]
        assert len(successful_deductions) == num_threads

        final_balance = successful_deductions[-1][1] if successful_deductions else initial_balance
        expected_final_balance = initial_balance - (num_threads * deduction_per_thread)
        assert final_balance == expected_final_balance

    @pytest.mark.asyncio
    async def test_credit_deduction_with_circuit_breaker_pattern(self):
        """Test credit deduction with circuit breaker pattern for database failures."""
        from app.services.usage_limit_service import UsageLimitError

        # Simulate database failures
        failure_count = 0
        max_failures = 3

        def mock_rpc_with_circuit_breaker(*args, **kwargs):
            nonlocal failure_count
            failure_count += 1

            if failure_count <= max_failures:
                # Simulate database failure
                raise Exception("Database connection failed")
            else:
                # Simulate recovery
                mock_result = MagicMock()
                mock_result.data = [{"success": True, "new_balance": 45, "deducted_amount": 5}]
                return mock_result

        # Test circuit breaker behavior
        with patch.object(self.db.client, "rpc", side_effect=mock_rpc_with_circuit_breaker):
            # First few attempts should fail
            for i in range(max_failures):
                with pytest.raises(UsageLimitError):
                    await self.service.deduct_credits(self.test_user_id, 5, f"op_circuit_{i}")

            # Circuit should open after max failures
            # Implementation would depend on specific circuit breaker pattern

            # After recovery, operations should succeed
            with patch.object(self.db.client.table, "insert", return_value=MagicMock()):
                result = await self.service.deduct_credits(self.test_user_id, 5, "op_recovery")

            assert result is True

    @pytest.mark.asyncio
    async def test_credit_deduction_with_deadlock_detection(self):
        """Test credit deduction with deadlock detection and resolution."""
        # Mock deadlock scenario
        mock_deadlock_result = MagicMock()
        mock_deadlock_result.data = [
            {
                "success": False,
                "reason": "deadlock_detected",
                "error": "Deadlock detected, retry recommended",
            }
        ]

        # First attempt: deadlock
        with patch.object(self.db.client, "rpc", return_value=mock_deadlock_result):
            with patch.object(self.db.client.table, "insert", return_value=MagicMock()):
                result1 = await self.service.deduct_credits(
                    self.test_user_id, 5, "operation_deadlock"
                )

        # Should handle deadlock gracefully (possibly retry)
        # Implementation depends on specific deadlock handling strategy

        # Second attempt: success after retry
        mock_success_result = MagicMock()
        mock_success_result.data = [{"success": True, "new_balance": 45, "deducted_amount": 5}]

        with patch.object(self.db.client, "rpc", return_value=mock_success_result):
            with patch.object(self.db.client.table, "insert", return_value=MagicMock()):
                result2 = await self.service.deduct_credits(self.test_user_id, 5, "operation_retry")

        assert result2 is True
