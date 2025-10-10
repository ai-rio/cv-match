"""
Webhook endpoints for processing Stripe events.
Brazilian market payment webhooks with signature verification.
"""

import logging
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.services.stripe_service import stripe_service
from app.services.webhook_service import WebhookService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

# Initialize webhook service
webhook_service = WebhookService()


@router.post("/stripe")
async def stripe_webhook(
    request: Request, stripe_signature: str = Header(..., alias="stripe-signature")
) -> JSONResponse:
    """
    Process Stripe webhook events.

    This endpoint handles all Stripe webhook events for the Brazilian market:
    - checkout.session.completed
    - invoice.payment_succeeded
    - invoice.payment_failed
    - customer.subscription.created
    - customer.subscription.updated
    - customer.subscription.deleted
    - payment_intent.succeeded
    - payment_intent.payment_failed

    Security features:
    - Webhook signature verification with 300s tolerance
    - Idempotency protection
    - Comprehensive error handling
    - Request logging and audit trail

    Args:
        request: FastAPI request object
        stripe_signature: Stripe signature header for verification

    Returns:
        JSON response with processing status
    """
    try:
        # Read raw request body
        body = await request.body()

        # Log webhook request
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        content_type = request.headers.get("content-type", "unknown")

        logger.info(
            f"Stripe webhook received - "
            f"IP: {client_ip}, "
            f"User-Agent: {user_agent}, "
            f"Content-Type: {content_type}, "
            f"Signature: {stripe_signature[:50]}..."
        )

        # Verify webhook signature
        verification_result = await stripe_service.verify_webhook_signature(
            payload=body, signature=stripe_signature
        )

        if not verification_result["success"]:
            logger.error(f"Webhook signature verification failed: {verification_result['error']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid signature: {verification_result['error']}",
            )

        # Extract event data
        event = verification_result["event"]
        event_type = event["type"]
        event_id = event["id"]
        event_data = event["data"]["object"]

        logger.info(f"Processing webhook event: {event_type} (ID: {event_id})")

        # Process the webhook event
        processing_result = await webhook_service.process_webhook_event(
            event_type=event_type, event_data=event_data, stripe_event_id=event_id
        )

        # Add request metadata to result
        processing_result.update(
            {
                "webhook_id": event_id,
                "client_ip": client_ip,
                "processed_at": stripe_service.webhook_secret
                is not None,  # Verify webhook is configured
            }
        )

        # Return appropriate response based on processing result
        if processing_result["success"]:
            logger.info(f"Webhook event {event_type} processed successfully")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Webhook processed successfully",
                    "event_type": event_type,
                    "event_id": event_id,
                    "processed": processing_result.get("processed", True),
                    "processing_time_ms": processing_result.get("processing_time_ms"),
                    "idempotent": processing_result.get("idempotent", False),
                },
            )
        else:
            logger.error(
                f"Webhook event {event_type} processing failed: {processing_result['error']}"
            )
            # Even if processing fails, we return 200 to acknowledge receipt
            # Stripe will retry if we don't return 200
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": False,
                    "message": "Webhook processing failed",
                    "event_type": event_type,
                    "event_id": event_id,
                    "error": processing_result["error"],
                    "processing_time_ms": processing_result.get("processing_time_ms"),
                },
            )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        logger.error(f"Unexpected error processing webhook: {str(e)}", exc_info=True)
        # Return 200 to prevent Stripe retries for system errors
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": False,
                "message": "Webhook processing encountered an error",
                "error": "Internal processing error",
            },
        )


@router.get("/stripe/health")
async def webhook_health_check() -> JSONResponse:
    """
    Health check endpoint for webhook processing.

    Returns:
        Health status of webhook processing system
    """
    try:
        # Check if Stripe is properly configured
        stripe_configured = bool(stripe_service.api_key and stripe_service.webhook_secret)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "healthy",
                "stripe_configured": stripe_configured,
                "test_mode": stripe_service.api_key.startswith("sk_test_")
                if stripe_service.api_key
                else False,
                "currency": stripe_service.default_currency,
                "country": stripe_service.default_country,
                "locale": stripe_service.default_locale,
            },
        )
    except Exception as e:
        logger.error(f"Webhook health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "error": str(e)},
        )


@router.post("/stripe/test")
async def test_webhook_endpoint() -> JSONResponse:
    """
    Test endpoint for webhook processing.

    This endpoint creates a test webhook event to verify
    the webhook processing pipeline is working correctly.

    Returns:
        Test webhook processing result
    """
    try:
        # Create a test checkout session event
        test_event = {
            "id": "evt_test_1234567890",
            "object": "event",
            "api_version": "2023-10-16",
            "created": 1704067200,
            "livemode": False,
            "pending_webhooks": 0,
            "request": {"id": "req_test_1234567890", "idempotency_key": "test_key_1234567890"},
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_1234567890",
                    "object": "checkout.session",
                    "created": 1704067200,
                    "currency": "brl",
                    "amount_total": 2990,  # R$ 29,90
                    "customer": "cus_test_1234567890",
                    "payment_intent": "pi_test_1234567890",
                    "payment_status": "paid",
                    "status": "complete",
                    "success_url": "https://cv-match.com/sucesso",
                    "cancel_url": "https://cv-match.com/cancelar",
                    "metadata": {
                        "user_id": "user_test_1234567890",
                        "product": "cv_optimization",
                        "plan": "pro",
                        "market": "brazil",
                        "language": "pt-br",
                    },
                    "customer_details": {
                        "email": "usuario@exemplo.com.br",
                        "name": "João Silva",
                        "address": {"country": "BR", "state": "SP", "city": "São Paulo"},
                    },
                    "subscription": "sub_test_1234567890",
                }
            },
        }

        # Process the test event
        event_type = str(test_event.get("type", ""))
        data_obj = test_event.get("data", {})
        data_dict: dict[str, Any] = data_obj if isinstance(data_obj, dict) else {}
        event_data: dict[str, Any] = data_dict.get("object", {})
        stripe_event_id = str(test_event.get("id", ""))

        result = await webhook_service.process_webhook_event(
            event_type=event_type, event_data=event_data, stripe_event_id=stripe_event_id
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": "Test webhook processed successfully",
                "test_event_id": test_event["id"],
                "test_event_type": test_event["type"],
                "processing_result": result,
            },
        )

    except Exception as e:
        logger.error(f"Test webhook processing failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Test webhook processing failed",
                "error": str(e),
            },
        )


@router.get("/stripe/test-payment-methods")
async def get_test_payment_methods() -> JSONResponse:
    """
    Get available test payment methods for Brazilian market.

    Returns:
        Available test payment methods
    """
    try:
        test_methods = await stripe_service.get_test_payment_methods()
        return JSONResponse(status_code=status.HTTP_200_OK, content=test_methods)
    except Exception as e:
        logger.error(f"Error getting test payment methods: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": str(e)},
        )
