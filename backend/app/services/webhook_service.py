"""
Webhook service for processing Stripe events.
Handles payment webhooks with Brazilian market support and idempotency.
"""

import logging
from datetime import UTC, datetime
from typing import Any, Dict, Optional

from app.services.supabase.database import SupabaseDatabaseService

logger = logging.getLogger(__name__)


class WebhookService:
    """Service for processing Stripe webhook events."""

    def __init__(self):
        """Initialize webhook service."""
        self.db_service = SupabaseDatabaseService("stripe_webhook_events")
        self.payment_db = SupabaseDatabaseService("payment_history")
        self.subscription_db = SupabaseDatabaseService("subscriptions")
        self.user_db = SupabaseDatabaseService("users")

    async def process_webhook_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        stripe_event_id: str
    ) -> Dict[str, Any]:
        """
        Process a webhook event with idempotency protection.

        Args:
            event_type: Type of Stripe event
            event_data: Event data payload
            stripe_event_id: Stripe event ID

        Returns:
            Processing result
        """
        # Start timing
        start_time = datetime.now(UTC)

        try:
            # Check idempotency - has this event been processed?
            if await self.is_event_processed(stripe_event_id):
                logger.info(f"Event {stripe_event_id} already processed, skipping")
                return {
                    "success": True,
                    "message": "Event already processed",
                    "event_id": stripe_event_id,
                    "idempotent": True
                }

            # Log the webhook event
            await self.log_webhook_event(
                stripe_event_id=stripe_event_id,
                event_type=event_type,
                data=event_data,
                processed=False
            )

            # Process based on event type
            result = await self._process_specific_event(event_type, event_data)

            # Calculate processing time
            processing_time = (datetime.now(UTC) - start_time).total_seconds() * 1000

            # Mark event as processed
            await self._mark_event_processed(
                stripe_event_id=stripe_event_id,
                processing_time_ms=processing_time,
                error_message=None if result.get("success") else result.get("error")
            )

            return {
                "success": result.get("success", True),
                "event_id": stripe_event_id,
                "event_type": event_type,
                "processed": True,
                "processing_time_ms": processing_time,
                **result
            }

        except Exception as e:
            processing_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
            error_message = f"Webhook processing failed: {str(e)}"
            logger.error(f"Error processing webhook {stripe_event_id}: {error_message}")

            # Mark event as failed
            await self._mark_event_processed(
                stripe_event_id=stripe_event_id,
                processing_time_ms=processing_time,
                error_message=error_message
            )

            return {
                "success": False,
                "event_id": stripe_event_id,
                "event_type": event_type,
                "error": error_message,
                "processing_time_ms": processing_time
            }

    async def is_event_processed(self, stripe_event_id: str) -> bool:
        """
        Check if a webhook event has already been processed.

        Args:
            stripe_event_id: Stripe event ID

        Returns:
            True if event has been processed, False otherwise
        """
        try:
            existing_event = await self.db_service.get_by_field(
                field_name="stripe_event_id",
                field_value=stripe_event_id
            )
            return existing_event is not None and existing_event.get("processed", False)
        except Exception as e:
            logger.error(f"Error checking event processing status: {str(e)}")
            # If we can't check, assume not processed to be safe
            return False

    async def log_webhook_event(
        self,
        stripe_event_id: str,
        event_type: str,
        data: Dict[str, Any],
        processed: bool = False
    ) -> Dict[str, Any]:
        """
        Log a webhook event to the database.

        Args:
            stripe_event_id: Stripe event ID
            event_type: Type of event
            data: Event data
            processed: Whether event has been processed

        Returns:
            Logging result
        """
        try:
            event_log = {
                "stripe_event_id": stripe_event_id,
                "event_type": event_type,
                "processed": processed,
                "processing_started_at": datetime.now(UTC).isoformat(),
                "data": data,
                "created_at": datetime.now(UTC).isoformat()
            }

            result = await self.db_service.create(event_log)
            return {
                "success": True,
                "webhook_event_id": result.get("id"),
                "stripe_event_id": stripe_event_id
            }
        except Exception as e:
            logger.error(f"Error logging webhook event: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _process_specific_event(
        self,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a specific webhook event type.

        Args:
            event_type: Type of Stripe event
            event_data: Event data payload

        Returns:
            Processing result
        """
        if event_type == "checkout.session.completed":
            return await self.process_checkout_session(event_data)
        elif event_type == "invoice.payment_succeeded":
            return await self.process_invoice_payment_succeeded(event_data)
        elif event_type == "invoice.payment_failed":
            return await self.process_invoice_payment_failed(event_data)
        elif event_type == "customer.subscription.created":
            return await self.process_subscription_created(event_data)
        elif event_type == "customer.subscription.updated":
            return await self.process_subscription_updated(event_data)
        elif event_type == "customer.subscription.deleted":
            return await self.process_subscription_deleted(event_data)
        elif event_type == "payment_intent.succeeded":
            return await self.process_payment_intent_succeeded(event_data)
        elif event_type == "payment_intent.payment_failed":
            return await self.process_payment_intent_failed(event_data)
        else:
            logger.info(f"Event type {event_type} not handled")
            return {
                "success": True,
                "message": f"Event type {event_type} not handled",
                "handled": False
            }

    async def process_checkout_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process checkout.session.completed event.

        Args:
            session_data: Checkout session data

        Returns:
            Processing result
        """
        try:
            user_id = session_data.get("metadata", {}).get("user_id")
            if not user_id:
                return {
                    "success": False,
                    "error": "User ID not found in session metadata"
                }

            # Get user information
            user = await self.user_db.get_by_field("id", user_id)
            if not user:
                return {
                    "success": False,
                    "error": f"User {user_id} not found"
                }

            # Create payment history record
            payment_record = {
                "user_id": user_id,
                "stripe_payment_id": session_data.get("payment_intent"),
                "stripe_checkout_session_id": session_data.get("id"),
                "stripe_customer_id": session_data.get("customer"),
                "amount": session_data.get("amount_total", 0),
                "currency": session_data.get("currency", "brl"),
                "status": "completed",
                "payment_type": "subscription" if session_data.get("subscription") else "one_time",
                "description": self._get_payment_description(session_data),
                "metadata": session_data.get("metadata", {}),
                "created_at": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat()
            }

            payment_result = await self.payment_db.create(payment_record)

            # Update user with Stripe customer ID if not set
            if not user.get("stripe_customer_id") and session_data.get("customer"):
                await self.user_db.update(
                    user_id,
                    {"stripe_customer_id": session_data.get("customer")}
                )

            # If it's a subscription, create subscription record
            if session_data.get("subscription"):
                await self._create_subscription_record(session_data, user_id)

            return {
                "success": True,
                "payment_id": payment_result.get("id"),
                "user_id": user_id,
                "amount": session_data.get("amount_total"),
                "currency": session_data.get("currency")
            }

        except Exception as e:
            logger.error(f"Error processing checkout session: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def process_subscription_created(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process customer.subscription.created event.

        Args:
            subscription_data: Subscription data

        Returns:
            Processing result
        """
        try:
            user_id = subscription_data.get("metadata", {}).get("user_id")
            if not user_id:
                return {
                    "success": False,
                    "error": "User ID not found in subscription metadata"
                }

            subscription_record = await self._create_subscription_record(subscription_data, user_id)

            return {
                "success": True,
                "subscription_id": subscription_record.get("id"),
                "user_id": user_id,
                "status": subscription_data.get("status")
            }

        except Exception as e:
            logger.error(f"Error processing subscription created: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def process_subscription_updated(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process customer.subscription.updated event.

        Args:
            subscription_data: Updated subscription data

        Returns:
            Processing result
        """
        try:
            stripe_subscription_id = subscription_data.get("id")
            if not stripe_subscription_id:
                return {
                    "success": False,
                    "error": "Subscription ID not found"
                }

            # Find existing subscription
            existing_sub = await self.subscription_db.get_by_field(
                "stripe_subscription_id",
                stripe_subscription_id
            )

            if not existing_sub:
                return {
                    "success": False,
                    "error": f"Subscription {stripe_subscription_id} not found"
                }

            # Update subscription
            update_data = {
                "status": subscription_data.get("status"),
                "current_period_start": datetime.fromtimestamp(
                    subscription_data.get("current_period_start")
                ).isoformat(),
                "current_period_end": datetime.fromtimestamp(
                    subscription_data.get("current_period_end")
                ).isoformat(),
                "cancel_at_period_end": subscription_data.get("cancel_at_period_end", False),
                "updated_at": datetime.now(UTC).isoformat()
            }

            if subscription_data.get("canceled_at"):
                update_data["canceled_at"] = datetime.fromtimestamp(
                    subscription_data.get("canceled_at")
                ).isoformat()

            await self.subscription_db.update(existing_sub["id"], update_data)

            return {
                "success": True,
                "subscription_id": existing_sub["id"],
                "status": subscription_data.get("status")
            }

        except Exception as e:
            logger.error(f"Error processing subscription updated: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def process_subscription_deleted(self, subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process customer.subscription.deleted event.

        Args:
            subscription_data: Deleted subscription data

        Returns:
            Processing result
        """
        try:
            stripe_subscription_id = subscription_data.get("id")
            if not stripe_subscription_id:
                return {
                    "success": False,
                    "error": "Subscription ID not found"
                }

            # Find and update existing subscription
            existing_sub = await self.subscription_db.get_by_field(
                "stripe_subscription_id",
                stripe_subscription_id
            )

            if existing_sub:
                await self.subscription_db.update(
                    existing_sub["id"],
                    {
                        "status": "canceled",
                        "canceled_at": datetime.fromtimestamp(
                            subscription_data.get("canceled_at", datetime.now(UTC).timestamp())
                        ).isoformat(),
                        "updated_at": datetime.now(UTC).isoformat()
                    }
                )
                return {
                    "success": True,
                    "subscription_id": existing_sub["id"],
                    "status": "canceled"
                }
            else:
                return {
                    "success": False,
                    "error": f"Subscription {stripe_subscription_id} not found"
                }

        except Exception as e:
            logger.error(f"Error processing subscription deleted: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def process_invoice_payment_succeeded(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process invoice.payment_succeeded event.

        Args:
            invoice_data: Invoice data

        Returns:
            Processing result
        """
        try:
            user_id = invoice_data.get("metadata", {}).get("user_id")
            if not user_id and invoice_data.get("subscription"):
                # Try to get user_id from subscription
                subscription = await self.subscription_db.get_by_field(
                    "stripe_subscription_id",
                    invoice_data.get("subscription")
                )
                if subscription:
                    user_id = subscription.get("user_id")

            if not user_id:
                return {
                    "success": False,
                    "error": "User ID not found"
                }

            # Create payment history record
            payment_record = {
                "user_id": user_id,
                "stripe_payment_id": invoice_data.get("payment_intent"),
                "stripe_subscription_id": invoice_data.get("subscription"),
                "amount": invoice_data.get("amount_paid", 0),
                "currency": invoice_data.get("currency", "brl"),
                "status": "completed",
                "payment_type": "subscription_payment",
                "description": f"Pagamento da assinatura - {invoice_data.get('id')}",
                "metadata": invoice_data.get("metadata", {}),
                "created_at": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat()
            }

            payment_result = await self.payment_db.create(payment_record)

            return {
                "success": True,
                "payment_history_id": payment_result.get("id"),
                "user_id": user_id,
                "amount": invoice_data.get("amount_paid")
            }

        except Exception as e:
            logger.error(f"Error processing invoice payment succeeded: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def process_invoice_payment_failed(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process invoice.payment_failed event.

        Args:
            invoice_data: Failed invoice data

        Returns:
            Processing result
        """
        try:
            subscription_id = invoice_data.get("subscription")
            if not subscription_id:
                return {
                    "success": False,
                    "error": "Subscription ID not found in invoice"
                }

            # Find and update subscription status
            subscription = await self.subscription_db.get_by_field(
                "stripe_subscription_id",
                subscription_id
            )

            if subscription:
                await self.subscription_db.update(
                    subscription["id"],
                    {
                        "status": "past_due",
                        "updated_at": datetime.now(UTC).isoformat()
                    }
                )
                return {
                    "success": True,
                    "subscription_id": subscription["id"],
                    "status": "past_due"
                }
            else:
                return {
                    "success": False,
                    "error": f"Subscription {subscription_id} not found"
                }

        except Exception as e:
            logger.error(f"Error processing invoice payment failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def process_payment_intent_succeeded(self, intent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process payment_intent.succeeded event.

        Args:
            intent_data: Payment intent data

        Returns:
            Processing result
        """
        try:
            user_id = intent_data.get("metadata", {}).get("user_id")
            if not user_id:
                return {
                    "success": False,
                    "error": "User ID not found in payment intent metadata"
                }

            # Create payment history record
            payment_record = {
                "user_id": user_id,
                "stripe_payment_id": intent_data.get("id"),
                "stripe_customer_id": intent_data.get("customer"),
                "amount": intent_data.get("amount", 0),
                "currency": intent_data.get("currency", "brl"),
                "status": "completed",
                "payment_type": "one_time",
                "description": f"Pagamento único - {intent_data.get('id')}",
                "metadata": intent_data.get("metadata", {}),
                "created_at": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat()
            }

            payment_result = await self.payment_db.create(payment_record)

            return {
                "success": True,
                "payment_id": payment_result.get("id"),
                "user_id": user_id,
                "amount": intent_data.get("amount")
            }

        except Exception as e:
            logger.error(f"Error processing payment intent succeeded: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def process_payment_intent_failed(self, intent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process payment_intent.payment_failed event.

        Args:
            intent_data: Failed payment intent data

        Returns:
            Processing result
        """
        try:
            user_id = intent_data.get("metadata", {}).get("user_id")
            if not user_id:
                return {
                    "success": False,
                    "error": "User ID not found in payment intent metadata"
                }

            # Create failed payment record
            payment_record = {
                "user_id": user_id,
                "stripe_payment_id": intent_data.get("id"),
                "stripe_customer_id": intent_data.get("customer"),
                "amount": intent_data.get("amount", 0),
                "currency": intent_data.get("currency", "brl"),
                "status": "failed",
                "payment_type": "one_time",
                "description": f"Pagamento falhou - {intent_data.get('id')}",
                "metadata": intent_data.get("metadata", {}),
                "created_at": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat()
            }

            payment_result = await self.payment_db.create(payment_record)

            return {
                "success": True,
                "payment_id": payment_result.get("id"),
                "user_id": user_id,
                "status": "failed"
            }

        except Exception as e:
            logger.error(f"Error processing payment intent failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _create_subscription_record(
        self,
        subscription_data: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Create a subscription record in the database."""
        subscription_record = {
            "user_id": user_id,
            "stripe_subscription_id": subscription_data.get("id"),
            "stripe_customer_id": subscription_data.get("customer"),
            "status": subscription_data.get("status"),
            "price_id": subscription_data.get("items", {}).get("data", [{}])[0].get("price", {}).get("id"),
            "product_id": subscription_data.get("items", {}).get("data", [{}])[0].get("price", {}).get("product"),
            "current_period_start": datetime.fromtimestamp(
                subscription_data.get("current_period_start")
            ).isoformat(),
            "current_period_end": datetime.fromtimestamp(
                subscription_data.get("current_period_end")
            ).isoformat(),
            "cancel_at_period_end": subscription_data.get("cancel_at_period_end", False),
            "metadata": subscription_data.get("metadata", {}),
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat()
        }

        return await self.subscription_db.create(subscription_record)

    async def _mark_event_processed(
        self,
        stripe_event_id: str,
        processing_time_ms: float,
        error_message: Optional[str] = None
    ):
        """Mark a webhook event as processed."""
        try:
            update_data = {
                "processed": True,
                "processing_completed_at": datetime.now(UTC).isoformat(),
                "processed_at": datetime.now(UTC).isoformat(),
                "processing_time_ms": processing_time_ms
            }

            if error_message:
                update_data["error_message"] = error_message

            # Find and update the event
            existing_event = await self.db_service.get_by_field(
                "stripe_event_id",
                stripe_event_id
            )

            if existing_event:
                await self.db_service.update(existing_event["id"], update_data)
        except Exception as e:
            logger.error(f"Error marking event as processed: {str(e)}")

    def _get_payment_description(self, session_data: Dict[str, Any]) -> str:
        """Generate payment description based on session data."""
        plan = session_data.get("metadata", {}).get("plan", "unknown")
        amount = session_data.get("amount_total", 0)
        currency = session_data.get("currency", "brl")

        # Convert amount from cents to reais
        amount_brl = amount / 100

        plan_names = {
            "pro": "Plano Profissional",
            "enterprise": "Plano Empresarial",
            "lifetime": "Acesso Vitalício",
            "free": "Plano Grátis"
        }

        plan_name = plan_names.get(plan, f"Plano {plan}")

        return f"{plan_name} - R$ {amount_brl:,.2f}"