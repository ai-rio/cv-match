"""
Webhook service for processing Stripe events.
Handles payment webhooks with Brazilian market support and idempotency.
"""

import logging
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.core.config import settings
from app.core.database import SupabaseSession
from app.services.usage_limit_service import UsageLimitService
from supabase import create_client

logger = logging.getLogger(__name__)


class WebhookService:
    """Service for processing Stripe webhook events."""

    def __init__(self):
        """Initialize webhook service."""
        self.supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
        self.db = SupabaseSession()
        self.usage_limit_service = UsageLimitService(self.db)

    def _safe_fromtimestamp(self, timestamp: Any) -> str | None:
        """Safely convert timestamp to ISO string."""
        if timestamp is not None:
            return datetime.fromtimestamp(float(timestamp)).isoformat()
        return None

    async def process_webhook_event(
        self, event_type: str, event_data: dict[str, Any], stripe_event_id: str
    ) -> dict[str, Any]:
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
                    "idempotent": True,
                }

            # Log the webhook event
            await self.log_webhook_event(
                stripe_event_id=stripe_event_id,
                event_type=event_type,
                data=event_data,
                processed=False,
            )

            # Process based on event type
            result = await self._process_specific_event(event_type, event_data)

            # Calculate processing time
            processing_time = (datetime.now(UTC) - start_time).total_seconds() * 1000

            # Mark event as processed
            await self._mark_event_processed(
                stripe_event_id=stripe_event_id,
                processing_time_ms=processing_time,
                error_message=None if result.get("success") else result.get("error"),
            )

            return {
                "success": result.get("success", True),
                "event_id": stripe_event_id,
                "event_type": event_type,
                "processed": True,
                "processing_time_ms": processing_time,
                **result,
            }

        except Exception as e:
            processing_time = (datetime.now(UTC) - start_time).total_seconds() * 1000
            error_message = f"Webhook processing failed: {str(e)}"
            logger.error(f"Error processing webhook {stripe_event_id}: {error_message}")

            # Mark event as failed
            await self._mark_event_processed(
                stripe_event_id=stripe_event_id,
                processing_time_ms=processing_time,
                error_message=error_message,
            )

            return {
                "success": False,
                "event_id": stripe_event_id,
                "event_type": event_type,
                "error": error_message,
                "processing_time_ms": processing_time,
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
            existing_event = await self._get_by_field(
                "payment_events", field_name="event_id", field_value=stripe_event_id
            )
            return existing_event is not None and existing_event.get("processed", False)
        except Exception as e:
            logger.error(f"Error checking event processing status: {str(e)}")
            # If we can't check, assume not processed to be safe
            return False

    async def log_webhook_event(
        self, stripe_event_id: str, event_type: str, data: dict[str, Any], processed: bool = False
    ) -> dict[str, Any]:
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
            # Extract user_id and payment details from event data
            user_id = None
            stripe_customer_id = None
            stripe_session_id = None
            amount = None
            currency = "brl"
            status = "pending"

            if event_type == "checkout.session.completed":
                user_id = data.get("metadata", {}).get("user_id")
                stripe_customer_id = data.get("customer")
                stripe_session_id = data.get("id")
                amount = data.get("amount_total", 0)
                currency = data.get("currency", "brl")
                status = data.get("payment_status", "unknown")

            event_log = {
                "event_id": stripe_event_id,
                "event_type": event_type,
                "user_id": user_id,
                "stripe_customer_id": stripe_customer_id,
                "stripe_session_id": stripe_session_id,
                "amount": amount,
                "currency": currency,
                "status": status,
                "payload": data,
                "processed": processed,
                "created_at": datetime.now(UTC).isoformat(),
            }

            result = await self._create("payment_events", event_log)
            return {
                "success": True,
                "webhook_event_id": result.get("id"),
                "stripe_event_id": stripe_event_id,
            }
        except Exception as e:
            logger.error(f"Error logging webhook event: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _process_specific_event(
        self, event_type: str, event_data: dict[str, Any]
    ) -> dict[str, Any]:
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
                "handled": False,
            }

    async def process_checkout_session(self, session_data: dict[str, Any]) -> dict[str, Any]:
        """
        Process checkout.session.completed event.

        This method handles successful payments and adds credits to user accounts
        based on the plan purchased.

        Args:
            session_data: Checkout session data

        Returns:
            Processing result
        """
        try:
            user_id = session_data.get("metadata", {}).get("user_id")
            if not user_id:
                return {"success": False, "error": "User ID not found in session metadata"}

            # Get user payment profile information
            user_payment_profile = await self._get_by_field(
                "user_payment_profiles", "user_id", user_id
            )
            if not user_payment_profile:
                return {"success": False, "error": f"User payment profile {user_id} not found"}

            # Extract payment details
            amount = session_data.get("amount_total", 0)
            currency = session_data.get("currency", "brl")
            plan_type = session_data.get("metadata", {}).get("plan", "unknown")

            # Add credits based on plan type
            credits_added = 0
            if plan_type in ["pro", "basic"]:
                credits_added = 50 if plan_type == "pro" else 10
                try:
                    await self.usage_limit_service.add_credits(
                        user_id=UUID(user_id),
                        amount=credits_added,
                        source="payment",
                        description=f"Credits from {plan_type} plan purchase",
                    )
                    logger.info(
                        f"Added {credits_added} credits to user {user_id} for {plan_type} plan"
                    )
                except Exception as e:
                    logger.error(f"Failed to add credits to user {user_id}: {str(e)}")
                    return {"success": False, "error": f"Failed to add credits: {str(e)}"}

            # Update user payment profile with Stripe customer ID if not set
            if not user_payment_profile.get("stripe_customer_id") and session_data.get("customer"):
                try:
                    await self._update(
                        "user_payment_profiles",
                        user_payment_profile["id"],
                        {"stripe_customer_id": session_data.get("customer")},
                    )
                except Exception as e:
                    # If update fails due to duplicate customer ID, it's already set - continue
                    logger.warning(f"Could not update stripe_customer_id (may already exist): {e}")

            # Create payment history record
            payment_record = {
                "user_id": user_id,
                "stripe_payment_id": session_data.get("payment_intent"),
                "stripe_checkout_session_id": session_data.get("id"),
                "stripe_customer_id": session_data.get("customer"),
                "amount": amount,
                "currency": currency,
                "status": "completed",
                "payment_type": (
                    "subscription_setup" if session_data.get("subscription") else "one_time"
                ),
                "description": self._get_payment_description(session_data),
                "metadata": session_data.get("metadata", {}),
                "created_at": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat(),
            }

            payment_result = await self._create("payment_history", payment_record)

            # If it's a subscription, create subscription record
            if session_data.get("subscription"):
                await self._create_subscription_record(session_data, user_id)

            return {
                "success": True,
                "payment_id": payment_result.get("id"),
                "user_id": user_id,
                "amount": amount,
                "currency": currency,
                "credits_added": credits_added,
                "plan_type": plan_type,
            }

        except Exception as e:
            logger.error(f"Error processing checkout session: {str(e)}")
            return {"success": False, "error": str(e)}

    async def process_subscription_created(
        self, subscription_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Process customer.subscription.created event.

        Args:
            subscription_data: Subscription data

        Returns:
            Processing result
        """
        try:
            user_id = subscription_data.get("metadata", {}).get("user_id")
            tier_id = subscription_data.get("metadata", {}).get("tier_id")

            if not user_id:
                return {"success": False, "error": "User ID not found in subscription metadata"}

            # Use subscription service to create subscription record
            from app.models.subscription import SubscriptionCreate
            from app.services.subscription_service import subscription_service

            # Extract price ID from subscription items
            price_id = None
            if subscription_data.get("items", {}).get("data"):
                price_id = subscription_data["items"]["data"][0].get("price", {}).get("id")

            # Create subscription using service
            subscription_create = SubscriptionCreate(
                user_id=user_id,
                tier_id=tier_id or "flow_pro",  # Default if not specified
                status=subscription_data.get("status", "active"),
                stripe_subscription_id=subscription_data.get("id") or "",
                stripe_customer_id=subscription_data.get("customer") or "",
                stripe_price_id=price_id or "",
            )

            subscription_details = await subscription_service.create_subscription(
                subscription_create
            )

            logger.info(f"Created subscription {subscription_details.id} for user {user_id}")

            return {
                "success": True,
                "subscription_id": subscription_details.id,
                "user_id": user_id,
                "tier_id": tier_id,
                "status": subscription_data.get("status"),
            }

        except Exception as e:
            logger.error(f"Error processing subscription created: {str(e)}")
            return {"success": False, "error": str(e)}

    async def process_subscription_updated(
        self, subscription_data: dict[str, Any]
    ) -> dict[str, Any]:
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
                return {"success": False, "error": "Subscription ID not found"}

            # Use subscription service to handle updates
            from app.models.subscription import SubscriptionUpdate
            from app.services.subscription_service import subscription_service

            # Find existing subscription to get local ID
            existing_sub = await self._get_by_field(
                "subscriptions", "stripe_subscription_id", stripe_subscription_id
            )

            if not existing_sub:
                return {
                    "success": False,
                    "error": f"Subscription {stripe_subscription_id} not found",
                }

            # Check for tier changes
            new_price_id = None
            if subscription_data.get("items", {}).get("data"):
                new_price_id = subscription_data["items"]["data"][0].get("price", {}).get("id")

            # Determine tier_id from price_id or metadata
            tier_id = subscription_data.get("metadata", {}).get("tier_id")

            # Update subscription
            update_data = SubscriptionUpdate(
                status=subscription_data.get("status"),
                stripe_price_id=new_price_id,
                tier_id=tier_id,
                cancel_at_period_end=subscription_data.get("cancel_at_period_end", False),
            )

            await subscription_service.update_subscription(existing_sub["id"], update_data)

            logger.info(
                f"Updated subscription {existing_sub['id']}: status={subscription_data.get('status')}"
            )

            return {
                "success": True,
                "subscription_id": existing_sub["id"],
                "status": subscription_data.get("status"),
                "tier_id": tier_id,
            }

        except Exception as e:
            logger.error(f"Error processing subscription updated: {str(e)}")
            return {"success": False, "error": str(e)}

    async def process_subscription_deleted(
        self, subscription_data: dict[str, Any]
    ) -> dict[str, Any]:
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
                return {"success": False, "error": "Subscription ID not found"}

            # Use subscription service to handle cancellation
            from app.services.subscription_service import subscription_service

            # Find existing subscription to get local ID
            existing_sub = await self._get_by_field(
                "subscriptions", "stripe_subscription_id", stripe_subscription_id
            )

            if existing_sub:
                # Cancel subscription immediately (deleted in Stripe)
                await subscription_service.cancel_subscription(existing_sub["id"], immediate=True)

                logger.info(f"Canceled subscription {existing_sub['id']} (deleted in Stripe)")

                return {
                    "success": True,
                    "subscription_id": existing_sub["id"],
                    "status": "canceled",
                }
            else:
                return {
                    "success": False,
                    "error": f"Subscription {stripe_subscription_id} not found",
                }

        except Exception as e:
            logger.error(f"Error processing subscription deleted: {str(e)}")
            return {"success": False, "error": str(e)}

    async def process_invoice_payment_succeeded(
        self, invoice_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Process invoice.payment_succeeded event.

        Args:
            invoice_data: Invoice data

        Returns:
            Processing result
        """
        try:
            user_id = invoice_data.get("metadata", {}).get("user_id")
            subscription_id = invoice_data.get("subscription")

            if not user_id and subscription_id:
                # Try to get user_id from subscription
                subscription = await self._get_by_field(
                    "subscriptions", "stripe_subscription_id", subscription_id
                )
                if subscription:
                    user_id = subscription.get("user_id")

            if not user_id:
                return {"success": False, "error": "User ID not found"}

            # Process subscription renewal if it's a subscription invoice
            if subscription_id:
                # Find local subscription
                local_subscription = await self._get_by_field(
                    "subscriptions", "stripe_subscription_id", subscription_id
                )

                if local_subscription:
                    # Use subscription service to process renewal
                    from app.services.subscription_service import subscription_service

                    try:
                        await subscription_service.process_period_renewal(local_subscription["id"])
                        logger.info(
                            f"Processed renewal for subscription {local_subscription['id']}"
                        )
                    except Exception as e:
                        logger.error(f"Failed to process subscription renewal: {str(e)}")

            # Create payment history record
            payment_record = {
                "user_id": user_id,
                "stripe_payment_id": invoice_data.get("payment_intent"),
                "stripe_subscription_id": subscription_id,
                "amount": invoice_data.get("amount_paid", 0),
                "currency": invoice_data.get("currency", "brl"),
                "status": "completed",
                "payment_type": "subscription_payment" if subscription_id else "one_time",
                "description": f"Pagamento da assinatura - {invoice_data.get('id')}"
                if subscription_id
                else f"Pagamento único - {invoice_data.get('id')}",
                "metadata": invoice_data.get("metadata", {}),
                "created_at": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat(),
            }

            payment_result = await self._create("payment_history", payment_record)

            return {
                "success": True,
                "payment_history_id": payment_result.get("id"),
                "user_id": user_id,
                "amount": invoice_data.get("amount_paid"),
                "subscription_renewed": bool(local_subscription),
            }

        except Exception as e:
            logger.error(f"Error processing invoice payment succeeded: {str(e)}")
            return {"success": False, "error": str(e)}

    async def process_invoice_payment_failed(self, invoice_data: dict[str, Any]) -> dict[str, Any]:
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
                return {"success": False, "error": "Subscription ID not found in invoice"}

            # Find and update subscription status using subscription service
            subscription = await self._get_by_field(
                "subscriptions", "stripe_subscription_id", subscription_id
            )

            if subscription:
                from app.models.subscription import SubscriptionUpdate
                from app.services.subscription_service import subscription_service

                # Update subscription status to past_due
                await subscription_service.update_subscription(
                    subscription["id"], SubscriptionUpdate(status="past_due")
                )

                logger.warning(
                    f"Subscription {subscription['id']} marked as past_due due to payment failure"
                )

                return {
                    "success": True,
                    "subscription_id": subscription["id"],
                    "status": "past_due",
                }
            else:
                return {"success": False, "error": f"Subscription {subscription_id} not found"}

        except Exception as e:
            logger.error(f"Error processing invoice payment failed: {str(e)}")
            return {"success": False, "error": str(e)}

    async def process_payment_intent_succeeded(self, intent_data: dict[str, Any]) -> dict[str, Any]:
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
                return {"success": False, "error": "User ID not found in payment intent metadata"}

            # Add credits for one-time payments
            amount = intent_data.get("amount", 0)
            if amount >= 29900:  # R$ 297,00 - Lifetime plan
                credits_to_add = 1000  # Enterprise tier equivalent
            elif amount >= 9990:  # R$ 99,90 - Enterprise monthly
                credits_to_add = 1000
            elif amount >= 2990:  # R$ 29,90 - Pro plan
                credits_to_add = 50
            elif amount >= 990:  # R$ 9,90 - Basic plan
                credits_to_add = 10
            else:
                credits_to_add = 0

            if credits_to_add > 0:
                try:
                    await self.usage_limit_service.add_credits(
                        user_id=UUID(user_id),
                        amount=credits_to_add,
                        source="payment",
                        description=f"Credits from one-time payment of R$ {amount / 100:.2f}",
                    )
                    logger.info(
                        f"Added {credits_to_add} credits to user {user_id} for one-time payment"
                    )
                except Exception as e:
                    logger.error(f"Failed to add credits for one-time payment: {str(e)}")

            # Create payment history record
            payment_record = {
                "user_id": user_id,
                "stripe_payment_id": intent_data.get("id"),
                "stripe_customer_id": intent_data.get("customer"),
                "amount": amount,
                "currency": intent_data.get("currency", "brl"),
                "status": "completed",
                "payment_type": "one_time",
                "description": f"Pagamento único - {intent_data.get('id')}",
                "metadata": intent_data.get("metadata", {}),
                "created_at": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat(),
            }

            payment_result = await self._create("payment_history", payment_record)

            return {
                "success": True,
                "payment_id": payment_result.get("id"),
                "user_id": user_id,
                "amount": amount,
                "credits_added": credits_to_add,
            }

        except Exception as e:
            logger.error(f"Error processing payment intent succeeded: {str(e)}")
            return {"success": False, "error": str(e)}

    async def process_payment_intent_failed(self, intent_data: dict[str, Any]) -> dict[str, Any]:
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
                return {"success": False, "error": "User ID not found in payment intent metadata"}

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
                "updated_at": datetime.now(UTC).isoformat(),
            }

            payment_result = await self._create("payment_history", payment_record)

            return {
                "success": True,
                "payment_id": payment_result.get("id"),
                "user_id": user_id,
                "status": "failed",
            }

        except Exception as e:
            logger.error(f"Error processing payment intent failed: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _create_subscription_record(
        self, subscription_data: dict[str, Any], user_id: str
    ) -> dict[str, Any]:
        """Create a subscription record in the database."""
        # Handle missing timestamp data for test scenarios
        current_period_start = subscription_data.get("current_period_start")
        current_period_end = subscription_data.get("current_period_end")

        # If no timestamps provided, create defaults (for test scenarios)
        if not current_period_start:
            current_period_start = datetime.now(UTC).timestamp()
        if not current_period_end:
            # Default to 30 days from now for monthly subscription
            from datetime import timedelta

            current_period_end = (datetime.now(UTC) + timedelta(days=30)).timestamp()

        subscription_record = {
            "user_id": user_id,
            "stripe_subscription_id": subscription_data.get("id"),
            "stripe_customer_id": subscription_data.get("customer"),
            "status": "active",  # Subscriptions should always be "active"
            # when created from checkout
            "price_id": (
                subscription_data.get("items", {}).get("data", [{}])[0].get("price", {}).get("id")
            ),
            "product_id": (
                subscription_data.get("items", {})
                .get("data", [{}])[0]
                .get("price", {})
                .get("product")
            ),
            "current_period_start": self._safe_fromtimestamp(current_period_start),
            "current_period_end": self._safe_fromtimestamp(current_period_end),
            "cancel_at_period_end": subscription_data.get("cancel_at_period_end", False),
            "metadata": subscription_data.get("metadata", {}),
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
        }

        return await self._create("subscriptions", subscription_record)

    async def _mark_event_processed(
        self, stripe_event_id: str, processing_time_ms: float, error_message: str | None = None
    ):
        """Mark a webhook event as processed."""
        try:
            update_data = {
                "processed": True,
                "processed_at": datetime.now(UTC).isoformat(),
                "processing_time_ms": processing_time_ms,
            }

            if error_message:
                update_data["error_message"] = error_message

            # Find and update the event
            existing_event = await self._get_by_field("payment_events", "event_id", stripe_event_id)

            if existing_event:
                await self._update("payment_events", existing_event["id"], update_data)
        except Exception as e:
            logger.error(f"Error marking event as processed: {str(e)}")

    async def _get_by_field(
        self, table_name: str, field_name: str, field_value: Any
    ) -> dict[str, Any] | None:
        """Get a record by field name and value."""
        response = self.supabase.table(table_name).select("*").eq(field_name, field_value).execute()
        return response.data[0] if response.data else None

    async def _create(self, table_name: str, data: dict[str, Any]) -> dict[str, Any]:
        """Create a record in a table."""
        response = self.supabase.table(table_name).insert(data).execute()
        return response.data[0] if response.data else {}

    async def _update(
        self, table_name: str, record_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update a record in a table."""
        response = self.supabase.table(table_name).update(data).eq("id", record_id).execute()
        return response.data[0] if response.data else {}

    def _get_payment_description(self, session_data: dict[str, Any]) -> str:
        """Generate payment description based on session data."""
        plan = session_data.get("metadata", {}).get("plan", "unknown")
        amount = session_data.get("amount_total", 0)
        session_data.get("currency", "brl")

        # Convert amount from cents to reais
        amount_brl = amount / 100

        plan_names = {
            "pro": "Plano Profissional",
            "enterprise": "Plano Empresarial",
            "lifetime": "Acesso Vitalício",
            "free": "Plano Grátis",
            "basic": "Plano Básico",
        }

        plan_name = plan_names.get(plan, f"Plano {plan}")

        return f"{plan_name} - R$ {amount_brl:,.2f}"
