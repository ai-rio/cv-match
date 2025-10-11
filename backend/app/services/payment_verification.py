"""
Payment verification service for CV-Match.

Handles linking payments to optimization jobs and triggering AI processing.
Also handles subscription upgrades for Brazilian market.
"""

import logging
import os
from datetime import UTC, datetime
from typing import Any

from app.services.stripe_service import stripe_service
from app.services.supabase.database import SupabaseDatabaseService
from app.models.payment import PaymentHistory, Subscription

logger = logging.getLogger(__name__)


class PaymentVerificationService:
    """Service for verifying payments and updating usage tracking."""

    def __init__(self):
        self.stripe_service = stripe_service
        self.payment_db = SupabaseDatabaseService("payment_history", PaymentHistory)
        self.subscription_db = SupabaseDatabaseService("subscriptions", Subscription)

    async def verify_and_activate_credits(
        self, session_id: str, user_id: str, plan_type: str = "pro"
    ) -> dict[str, Any]:
        """
        Verify payment and activate user credits.

        This method:
        1. Verifies the Stripe payment was successful
        2. Records the payment in payment_history
        3. Activates credits based on plan type
        4. Returns success/failure status

        Args:
            session_id: Stripe checkout session ID
            user_id: User's UUID
            plan_type: Plan type (pro, enterprise, lifetime)

        Returns:
            Dict containing success status and details

        Raises:
            Exception: If verification or database update fails
        """
        try:
            # 1. Verify payment with Stripe
            session_result = await self.stripe_service.retrieve_checkout_session(session_id)
            if not session_result["success"]:
                logger.error(f"Failed to retrieve session {session_id}: {session_result.get('error')}")
                return {"success": False, "error": "Invalid session"}

            session = session_result["session"]

            if session.payment_status != "paid":
                logger.error(
                    f"Payment not completed for session {session_id}: status={session.payment_status}"
                )
                return {
                    "success": False,
                    "error": "Payment not completed",
                    "status": session.payment_status
                }

            # 2. Check if payment already processed (idempotency)
            existing_payment = await self.payment_db.list(
                filters={"stripe_checkout_session_id": session_id}
            )
            if existing_payment:
                logger.info(f"Payment {session_id} already processed for user {user_id}")
                return {
                    "success": True,
                    "message": "Payment already processed",
                    "payment_id": str(existing_payment[0].id),
                }

            # 3. Record payment in payment_history
            payment_data = {
                "user_id": user_id,
                "stripe_checkout_session_id": session_id,
                "stripe_payment_intent_id": session.payment_intent,
                "amount": session.amount_total,
                "currency": session.currency,
                "status": "succeeded",
                "payment_type": "subscription" if plan_type in ["pro", "enterprise"] else "one_time",
                "description": f"CV-Match {plan_type.title()} Plan",
                "metadata": {
                    "plan_type": plan_type,
                    "market": "brazil",
                    "language": "pt-br",
                },
            }

            payment_result = await self.payment_db.create(payment_data)
            if not payment_result:
                logger.error(f"Failed to record payment for user {user_id}")
                return {"success": False, "error": "Failed to record payment"}

            logger.info(f"Payment verified and recorded for user {user_id}, plan: {plan_type}")

            return {
                "success": True,
                "user_id": user_id,
                "plan_type": plan_type,
                "payment_id": str(payment_result.id),
                "amount_paid": session.amount_total,
                "currency": session.currency,
                "credits_activated": await self._get_credits_for_plan(plan_type),
            }

        except Exception as e:
            logger.exception(f"Error verifying payment for user {user_id}: {str(e)}")
            raise e

    async def handle_checkout_completed(self, event_data: dict[str, Any]) -> dict[str, Any]:
        """
        Handle checkout.session.completed webhook event.

        Args:
            event_data: Stripe event data

        Returns:
            Dict containing processing result
        """
        try:
            session = event_data.get("object", {})
            session_id = session.get("id")
            metadata = session.get("metadata", {})
            user_id = metadata.get("user_id")
            plan_type = metadata.get("plan", "pro")

            if not user_id:
                logger.error(f"No user_id in session {session_id} metadata")
                return {"success": False, "error": "Missing user_id"}

            # Process payment and activate credits
            result = await self.verify_and_activate_credits(session_id, user_id, plan_type)
            return result

        except Exception as e:
            logger.exception(f"Error handling checkout completed: {str(e)}")
            return {"success": False, "error": str(e)}

    async def handle_payment_intent_succeeded(self, event_data: dict[str, Any]) -> dict[str, Any]:
        """
        Handle payment_intent.succeeded webhook event.

        Args:
            event_data: Stripe event data

        Returns:
            Dict containing processing result
        """
        try:
            payment_intent = event_data.get("object", {})
            payment_intent_id = payment_intent.get("id")
            metadata = payment_intent.get("metadata", {})
            user_id = metadata.get("user_id")

            if not user_id:
                logger.warning(f"No user_id in payment_intent {payment_intent_id} metadata")
                return {"success": False, "error": "Missing user_id"}

            # Log payment intent success (main processing happens in checkout.completed)
            logger.info(f"Payment intent succeeded for user {user_id}: {payment_intent_id}")

            return {
                "success": True,
                "user_id": user_id,
                "payment_intent_id": payment_intent_id
            }

        except Exception as e:
            logger.exception(f"Error handling payment intent succeeded: {str(e)}")
            return {"success": False, "error": str(e)}

    async def handle_payment_failure(self, user_id: str, error_message: str) -> None:
        """
        Handle payment failure by recording failed payment attempt.

        Args:
            user_id: User's UUID
            error_message: Error message to store
        """
        try:
            # Record failed payment attempt
            failed_payment_data = {
                "user_id": user_id,
                "status": "failed",
                "error_message": error_message,
                "metadata": {
                    "failed_at": datetime.now(UTC).isoformat(),
                    "market": "brazil",
                },
            }

            await self.payment_db.create(failed_payment_data)
            logger.info(f"Payment failure recorded for user {user_id}")

        except Exception as e:
            logger.exception(f"Error handling payment failure: {str(e)}")

    async def verify_payment_status(self, session_id: str) -> dict[str, Any]:
        """
        Verify the status of a payment session.

        Args:
            session_id: Stripe checkout session ID

        Returns:
            Dict containing payment status
        """
        try:
            session_result = await self.stripe_service.retrieve_checkout_session(session_id)
            if not session_result["success"]:
                return {"success": False, "error": "Invalid session"}

            session = session_result["session"]

            # Check if already processed
            existing_payment = await self.payment_db.list(
                filters={"stripe_checkout_session_id": session_id}
            )

            return {
                "success": True,
                "payment_status": session.payment_status,
                "amount_total": session.amount_total,
                "currency": session.currency,
                "already_processed": len(existing_payment) > 0,
                "session": {
                    "id": session.id,
                    "status": session.status,
                    "created": session.created,
                },
            }

        except Exception as e:
            logger.exception(f"Error verifying payment status for session {session_id}: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _get_credits_for_plan(self, plan_type: str) -> int:
        """
        Get the number of credits for a given plan type.

        Args:
            plan_type: Plan type (free, pro, enterprise, lifetime)

        Returns:
            Number of credits allocated
        """
        credits_map = {
            "free": 5,
            "pro": 100,
            "enterprise": 500,
            "lifetime": 1000,
        }
        return credits_map.get(plan_type, 0)

    async def get_user_payment_history(self, user_id: str, limit: int = 10) -> dict[str, Any]:
        """
        Get payment history for a user.

        Args:
            user_id: User's UUID
            limit: Maximum number of records to return

        Returns:
            Dict containing payment history
        """
        try:
            payments = await self.payment_db.list(
                filters={"user_id": user_id}, limit=limit
            )

            return {
                "success": True,
                "payments": payments,
                "total_count": len(payments),
            }

        except Exception as e:
            logger.exception(f"Error getting payment history for user {user_id}: {str(e)}")
            return {"success": False, "error": str(e)}


# Global service instance
payment_verification_service = PaymentVerificationService()