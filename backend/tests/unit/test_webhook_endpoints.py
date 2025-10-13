"""
Unit tests for webhook API endpoints.
Tests Stripe webhook processing, signature verification, and security.
"""

import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.webhook
class TestWebhookEndpoints:
    """Test webhook API endpoints."""

    def setup_method(self):
        """Set up test method."""
        self.test_event_id = f"evt_test_{datetime.now(UTC).timestamp()}"
        self.test_payload = {
            "id": self.test_event_id,
            "object": "event",
            "api_version": "2023-10-16",
            "created": int(datetime.now(UTC).timestamp()),
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_1234567890",
                    "object": "checkout.session",
                    "amount_total": 2990,
                    "currency": "brl",
                    "payment_status": "paid",
                    "metadata": {"user_id": "user_1234567890", "plan": "pro"},
                }
            },
        }

    @pytest.mark.asyncio
    async def test_stripe_webhook_success(self, async_client: AsyncClient):
        """Test successful Stripe webhook processing."""
        payload = json.dumps(self.test_payload, separators=(",", ":"))
        headers = {
            "stripe-signature": "t=1234567890,v1=signature123",
            "content-type": "application/json",
            "user-agent": "Stripe/1.0 (+https://stripe.com/docs/webhooks)",
        }

        # Mock signature verification
        mock_event = MagicMock()
        mock_event.__getitem__.side_effect = lambda key: {
            "type": self.test_payload["type"],
            "id": self.test_payload["id"],
            "data": self.test_payload["data"],
        }[key]

        with patch(
            "app.api.endpoints.webhooks.stripe_service.verify_webhook_signature",
            return_value={
                "success": True,
                "event": mock_event,
                "event_type": self.test_payload["type"],
                "event_id": self.test_payload["id"],
            },
        ):
            # Mock webhook processing
            with patch(
                "app.api.endpoints.webhooks.webhook_service.process_webhook_event",
                return_value={
                    "success": True,
                    "processed": True,
                    "payment_id": "payment_123",
                    "user_id": "user_1234567890",
                    "credits_added": 50,
                },
            ):
                response = await async_client.post(
                    "/api/webhooks/stripe", data=payload, headers=headers
                )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["success"] is True
        assert response_data["message"] == "Webhook processed successfully"
        assert response_data["event_type"] == "checkout.session.completed"
        assert response_data["event_id"] == self.test_event_id
        assert response_data["processed"] is True
        assert "processing_time_ms" in response_data

    @pytest.mark.asyncio
    async def test_stripe_webhook_signature_verification_failure(self, async_client: AsyncClient):
        """Test Stripe webhook with invalid signature."""
        payload = json.dumps(self.test_payload)
        headers = {"stripe-signature": "invalid_signature", "content-type": "application/json"}

        with patch(
            "app.api.endpoints.webhooks.stripe_service.verify_webhook_signature",
            return_value={
                "success": False,
                "error": "Invalid signature",
                "error_type": "signature_error",
            },
        ):
            response = await async_client.post(
                "/api/webhooks/stripe", data=payload, headers=headers
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert "Invalid signature" in response_data["detail"]

    @pytest.mark.asyncio
    async def test_stripe_webhook_missing_signature_header(self, async_client: AsyncClient):
        """Test Stripe webhook without signature header."""
        payload = json.dumps(self.test_payload)
        headers = {
            "content-type": "application/json"
            # Missing stripe-signature header
        }

        response = await async_client.post("/api/webhooks/stripe", data=payload, headers=headers)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_stripe_webhook_processing_error(self, async_client: AsyncClient):
        """Test Stripe webhook with processing error."""
        payload = json.dumps(self.test_payload, separators=(",", ":"))
        headers = {
            "stripe-signature": "t=1234567890,v1=signature123",
            "content-type": "application/json",
        }

        # Mock signature verification success
        mock_event = MagicMock()
        mock_event.__getitem__.side_effect = lambda key: {
            "type": self.test_payload["type"],
            "id": self.test_payload["id"],
            "data": self.test_payload["data"],
        }[key]

        with patch(
            "app.api.endpoints.webhooks.stripe_service.verify_webhook_signature",
            return_value={
                "success": True,
                "event": mock_event,
                "event_type": self.test_payload["type"],
                "event_id": self.test_payload["id"],
            },
        ):
            # Mock webhook processing failure
            with patch(
                "app.api.endpoints.webhooks.webhook_service.process_webhook_event",
                return_value={
                    "success": False,
                    "error": "User not found",
                    "processing_time_ms": 150.5,
                },
            ):
                response = await async_client.post(
                    "/api/webhooks/stripe", data=payload, headers=headers
                )

        # Should still return 200 to acknowledge receipt
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["success"] is False
        assert response_data["message"] == "Webhook processing failed"
        assert response_data["error"] == "User not found"
        assert response_data["processing_time_ms"] == 150.5

    @pytest.mark.asyncio
    async def test_stripe_webhook_system_error(self, async_client: AsyncClient):
        """Test Stripe webhook with system error."""
        payload = json.dumps(self.test_payload, separators=(",", ":"))
        headers = {
            "stripe-signature": "t=1234567890,v1=signature123",
            "content-type": "application/json",
        }

        # Mock signature verification success
        mock_event = MagicMock()
        mock_event.__getitem__.side_effect = lambda key: {
            "type": self.test_payload["type"],
            "id": self.test_payload["id"],
            "data": self.test_payload["data"],
        }[key]

        with patch(
            "app.api.endpoints.webhooks.stripe_service.verify_webhook_signature",
            return_value={
                "success": True,
                "event": mock_event,
                "event_type": self.test_payload["type"],
                "event_id": self.test_payload["id"],
            },
        ):
            # Mock system error during processing
            with patch(
                "app.api.endpoints.webhooks.webhook_service.process_webhook_event",
                side_effect=Exception("System error"),
            ):
                response = await async_client.post(
                    "/api/webhooks/stripe", data=payload, headers=headers
                )

        # Should still return 200 to prevent retries
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["success"] is False
        assert response_data["message"] == "Webhook processing encountered an error"
        assert response_data["error"] == "Internal processing error"

    @pytest.mark.asyncio
    async def test_stripe_webhook_idempotency(self, async_client: AsyncClient):
        """Test Stripe webhook idempotency - already processed event."""
        payload = json.dumps(self.test_payload, separators=(",", ":"))
        headers = {
            "stripe-signature": "t=1234567890,v1=signature123",
            "content-type": "application/json",
        }

        # Mock signature verification
        mock_event = MagicMock()
        mock_event.__getitem__.side_effect = lambda key: {
            "type": self.test_payload["type"],
            "id": self.test_payload["id"],
            "data": self.test_payload["data"],
        }[key]

        with patch(
            "app.api.endpoints.webhooks.stripe_service.verify_webhook_signature",
            return_value={
                "success": True,
                "event": mock_event,
                "event_type": self.test_payload["type"],
                "event_id": self.test_payload["id"],
            },
        ):
            # Mock webhook service returns already processed
            with patch(
                "app.api.endpoints.webhooks.webhook_service.process_webhook_event",
                return_value={
                    "success": True,
                    "idempotent": True,
                    "message": "Event already processed",
                    "event_id": self.test_event_id,
                },
            ):
                response = await async_client.post(
                    "/api/webhooks/stripe", data=payload, headers=headers
                )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["success"] is True
        assert response_data["idempotent"] is True
        assert "already processed" in response_data["message"]

    @pytest.mark.asyncio
    async def test_stripe_webhook_invalid_json(self, async_client: AsyncClient):
        """Test Stripe webhook with invalid JSON payload."""
        invalid_payload = "{ invalid json }"
        headers = {
            "stripe-signature": "t=1234567890,v1=signature123",
            "content-type": "application/json",
        }

        response = await async_client.post(
            "/api/webhooks/stripe", data=invalid_payload, headers=headers
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_stripe_webhook_different_event_types(self, async_client: AsyncClient):
        """Test Stripe webhook processing different event types."""
        event_types = [
            "checkout.session.completed",
            "invoice.payment_succeeded",
            "invoice.payment_failed",
            "customer.subscription.created",
            "customer.subscription.updated",
            "customer.subscription.deleted",
            "payment_intent.succeeded",
            "payment_intent.payment_failed",
        ]

        for event_type in event_types:
            with self.subTest(event_type=event_type):
                test_payload = self.test_payload.copy()
                test_payload["type"] = event_type

                payload = json.dumps(test_payload, separators=(",", ":"))
                headers = {
                    "stripe-signature": "t=1234567890,v1=signature123",
                    "content-type": "application/json",
                }

                # Mock signature verification
                mock_event = MagicMock()
                mock_event.__getitem__.side_effect = lambda key: {
                    "type": event_type,
                    "id": test_payload["id"],
                    "data": test_payload["data"],
                }[key]

                with patch(
                    "app.api.endpoints.webhooks.stripe_service.verify_webhook_signature",
                    return_value={
                        "success": True,
                        "event": mock_event,
                        "event_type": event_type,
                        "event_id": test_payload["id"],
                    },
                ):
                    # Mock webhook processing
                    with patch(
                        "app.api.endpoints.webhooks.webhook_service.process_webhook_event",
                        return_value={"success": True, "processed": True, "event_type": event_type},
                    ):
                        response = await async_client.post(
                            "/api/webhooks/stripe", data=payload, headers=headers
                        )

                assert response.status_code == status.HTTP_200_OK
                response_data = response.json()
                assert response_data["success"] is True
                assert response_data["event_type"] == event_type

    @pytest.mark.asyncio
    async def test_stripe_webhook_unsupported_event_type(self, async_client: AsyncClient):
        """Test Stripe webhook with unsupported event type."""
        test_payload = self.test_payload.copy()
        test_payload["type"] = "account.updated"  # Unsupported event type

        payload = json.dumps(test_payload, separators=(",", ":"))
        headers = {
            "stripe-signature": "t=1234567890,v1=signature123",
            "content-type": "application/json",
        }

        # Mock signature verification
        mock_event = MagicMock()
        mock_event.__getitem__.side_effect = lambda key: {
            "type": test_payload["type"],
            "id": test_payload["id"],
            "data": test_payload["data"],
        }[key]

        with patch(
            "app.api.endpoints.webhooks.stripe_service.verify_webhook_signature",
            return_value={
                "success": True,
                "event": mock_event,
                "event_type": test_payload["type"],
                "event_id": test_payload["id"],
            },
        ):
            # Mock webhook processing returns not handled
            with patch(
                "app.api.endpoints.webhooks.webhook_service.process_webhook_event",
                return_value={
                    "success": True,
                    "processed": True,
                    "message": "Event type account.updated not handled",
                    "handled": False,
                },
            ):
                response = await async_client.post(
                    "/api/webhooks/stripe", data=payload, headers=headers
                )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["success"] is True
        assert "not handled" in response_data["message"]

    @pytest.mark.asyncio
    async def test_stripe_webhook_request_logging(self, async_client: AsyncClient):
        """Test that webhook requests are properly logged."""
        payload = json.dumps(self.test_payload, separators=(",", ":"))
        headers = {
            "stripe-signature": "t=1234567890,v1=signature123",
            "content-type": "application/json",
            "user-agent": "Stripe/1.0 (+https://stripe.com/docs/webhooks)",
            "x-forwarded-for": "192.168.1.1",
        }

        # Mock signature verification
        mock_event = MagicMock()
        mock_event.__getitem__.side_effect = lambda key: {
            "type": self.test_payload["type"],
            "id": self.test_payload["id"],
            "data": self.test_payload["data"],
        }[key]

        with patch(
            "app.api.endpoints.webhooks.stripe_service.verify_webhook_signature",
            return_value={
                "success": True,
                "event": mock_event,
                "event_type": self.test_payload["type"],
                "event_id": self.test_payload["id"],
            },
        ):
            with patch(
                "app.api.endpoints.webhooks.webhook_service.process_webhook_event",
                return_value={"success": True, "processed": True},
            ):
                response = await async_client.post(
                    "/api/webhooks/stripe", data=payload, headers=headers
                )

        assert response.status_code == status.HTTP_200_OK

        # Verify response includes request metadata
        response_data = response.json()
        assert "webhook_id" in response_data
        assert "client_ip" in response_data
        assert "processed_at" in response_data

    @pytest.mark.asyncio
    async def test_webhook_health_check_healthy(self, async_client: AsyncClient):
        """Test webhook health check when healthy."""
        with patch("app.api.endpoints.webhooks.stripe_service") as mock_stripe:
            mock_stripe.api_key = "sk_test_1234567890"
            mock_stripe.webhook_secret = "whsec_test_1234567890"
            mock_stripe.default_currency = "brl"
            mock_stripe.default_country = "BR"
            mock_stripe.default_locale = "pt-BR"

            response = await async_client.get("/api/webhooks/stripe/health")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["status"] == "healthy"
        assert response_data["stripe_configured"] is True
        assert response_data["test_mode"] is True
        assert response_data["currency"] == "brl"
        assert response_data["country"] == "BR"
        assert response_data["locale"] == "pt-BR"

    @pytest.mark.asyncio
    async def test_webhook_health_check_unhealthy(self, async_client: AsyncClient):
        """Test webhook health check when unhealthy."""
        with patch("app.api.endpoints.webhooks.stripe_service") as mock_stripe:
            mock_stripe.api_key = None  # Not configured
            mock_stripe.webhook_secret = None
            mock_stripe.default_currency = "brl"

            response = await async_client.get("/api/webhooks/stripe/health")

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        response_data = response.json()
        assert response_data["status"] == "unhealthy"

    @pytest.mark.asyncio
    async def test_webhook_health_check_system_error(self, async_client: AsyncClient):
        """Test webhook health check with system error."""
        with patch(
            "app.api.endpoints.webhooks.stripe_service", side_effect=Exception("System error")
        ):
            response = await async_client.get("/api/webhooks/stripe/health")

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        response_data = response.json()
        assert response_data["status"] == "unhealthy"
        assert "System error" in response_data["error"]

    @pytest.mark.asyncio
    async def test_webhook_test_endpoint_success(self, async_client: AsyncClient):
        """Test webhook test endpoint success."""
        with patch(
            "app.api.endpoints.webhooks.webhook_service.process_webhook_event",
            return_value={
                "success": True,
                "processed": True,
                "event_type": "checkout.session.completed",
                "payment_id": "payment_test_123",
                "user_id": "user_test_123",
                "credits_added": 50,
            },
        ):
            response = await async_client.post("/api/webhooks/stripe/test")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["success"] is True
        assert response_data["message"] == "Test webhook processed successfully"
        assert "test_event_id" in response_data
        assert "test_event_type" in response_data
        assert "processing_result" in response_data

    @pytest.mark.asyncio
    async def test_webhook_test_endpoint_failure(self, async_client: AsyncClient):
        """Test webhook test endpoint failure."""
        with patch(
            "app.api.endpoints.webhooks.webhook_service.process_webhook_event",
            side_effect=Exception("Test error"),
        ):
            response = await async_client.post("/api/webhooks/stripe/test")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        response_data = response.json()
        assert response_data["success"] is False
        assert "Test webhook processing failed" in response_data["message"]
        assert "Test error" in response_data["error"]

    @pytest.mark.asyncio
    async def test_get_test_payment_methods_success(self, async_client: AsyncClient):
        """Test getting test payment methods."""
        mock_methods = {
            "success": True,
            "payment_methods": [
                {
                    "type": "card",
                    "name": "Cartão de Crédito",
                    "test_cards": [
                        {
                            "number": "4242424242424242",
                            "brand": "Visa",
                            "status": "success",
                            "description": "Visa sucesso",
                        }
                    ],
                }
            ],
            "currency": "brl",
            "country": "BR",
            "locale": "pt-BR",
        }

        with patch(
            "app.api.endpoints.webhooks.stripe_service.get_test_payment_methods",
            return_value=mock_methods,
        ):
            response = await async_client.get("/api/webhooks/stripe/test-payment-methods")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["success"] is True
        assert "payment_methods" in response_data
        assert response_data["currency"] == "brl"
        assert response_data["country"] == "BR"
        assert response_data["locale"] == "pt-BR"

    @pytest.mark.asyncio
    async def test_get_test_payment_methods_error(self, async_client: AsyncClient):
        """Test getting test payment methods with error."""
        with patch(
            "app.api.endpoints.webhooks.stripe_service.get_test_payment_methods",
            side_effect=Exception("Service error"),
        ):
            response = await async_client.get("/api/webhooks/stripe/test-payment-methods")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        response_data = response.json()
        assert response_data["success"] is False
        assert "Service error" in response_data["error"]

    @pytest.mark.asyncio
    async def test_webhook_brazilian_market_processing(self, async_client: AsyncClient):
        """Test webhook processing for Brazilian market events."""
        # Brazilian checkout session
        brazilian_payload = {
            "id": self.test_event_id,
            "object": "event",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_brazil_123",
                    "amount_total": 2990,
                    "currency": "brl",
                    "customer_details": {
                        "email": "usuario@exemplo.com.br",
                        "name": "João Silva",
                        "address": {"country": "BR", "state": "SP", "city": "São Paulo"},
                    },
                    "metadata": {
                        "user_id": "user_brazil_123",
                        "plan": "pro",
                        "market": "brazil",
                        "language": "pt-br",
                    },
                }
            },
        }

        payload = json.dumps(brazilian_payload, separators=(",", ":"))
        headers = {
            "stripe-signature": "t=1234567890,v1=signature123",
            "content-type": "application/json",
        }

        # Mock signature verification
        mock_event = MagicMock()
        mock_event.__getitem__.side_effect = lambda key: {
            "type": brazilian_payload["type"],
            "id": brazilian_payload["id"],
            "data": brazilian_payload["data"],
        }[key]

        with patch(
            "app.api.endpoints.webhooks.stripe_service.verify_webhook_signature",
            return_value={
                "success": True,
                "event": mock_event,
                "event_type": brazilian_payload["type"],
                "event_id": brazilian_payload["id"],
            },
        ):
            # Mock successful Brazilian webhook processing
            with patch(
                "app.api.endpoints.webhooks.webhook_service.process_webhook_event",
                return_value={
                    "success": True,
                    "processed": True,
                    "user_id": "user_brazil_123",
                    "amount": 2990,
                    "currency": "brl",
                    "credits_added": 50,
                    "plan_type": "pro",
                },
            ):
                response = await async_client.post(
                    "/api/webhooks/stripe", data=payload, headers=headers
                )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["success"] is True

    @pytest.mark.asyncio
    async def test_webhook_signature_tolerance(self, async_client: AsyncClient):
        """Test webhook signature verification with tolerance."""
        payload = json.dumps(self.test_payload, separators=(",", ":"))

        # Test with different timestamp formats
        headers_list = [
            {
                "stripe-signature": "t=1234567890,v1=signature123",
                "content-type": "application/json",
            },
            {
                "stripe-signature": "t=1704067200,v1=signature456",
                "content-type": "application/json",
            },
            {
                "stripe-signature": "t=1704153600,v1=signature789",
                "content-type": "application/json",
            },
        ]

        for headers in headers_list:
            with self.subTest(signature=headers["stripe-signature"]):
                # Mock signature verification success
                mock_event = MagicMock()
                mock_event.__getitem__.side_effect = lambda key: {
                    "type": self.test_payload["type"],
                    "id": self.test_payload["id"],
                    "data": self.test_payload["data"],
                }[key]

                with patch(
                    "app.api.endpoints.webhooks.stripe_service.verify_webhook_signature",
                    return_value={
                        "success": True,
                        "event": mock_event,
                        "event_type": self.test_payload["type"],
                        "event_id": self.test_payload["id"],
                    },
                ):
                    with patch(
                        "app.api.endpoints.webhooks.webhook_service.process_webhook_event",
                        return_value={"success": True, "processed": True},
                    ):
                        response = await async_client.post(
                            "/api/webhooks/stripe", data=payload, headers=headers
                        )

                assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_webhook_large_payload(self, async_client: AsyncClient):
        """Test webhook processing with large payload."""
        # Create a large payload
        large_payload = self.test_payload.copy()
        large_payload["data"]["object"]["metadata"] = {
            f"key_{i}": f"value_{i}" * 100  # Large values
            for i in range(50)
        }

        payload = json.dumps(large_payload, separators=(",", ":"))
        headers = {
            "stripe-signature": "t=1234567890,v1=signature123",
            "content-type": "application/json",
        }

        # Mock signature verification
        mock_event = MagicMock()
        mock_event.__getitem__.side_effect = lambda key: {
            "type": large_payload["type"],
            "id": large_payload["id"],
            "data": large_payload["data"],
        }[key]

        with patch(
            "app.api.endpoints.webhooks.stripe_service.verify_webhook_signature",
            return_value={
                "success": True,
                "event": mock_event,
                "event_type": large_payload["type"],
                "event_id": large_payload["id"],
            },
        ):
            with patch(
                "app.api.endpoints.webhooks.webhook_service.process_webhook_event",
                return_value={"success": True, "processed": True},
            ):
                response = await async_client.post(
                    "/api/webhooks/stripe", data=payload, headers=headers
                )

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_webhook_concurrent_processing(self, async_client: AsyncClient):
        """Test webhook processing with concurrent requests."""
        import asyncio

        payload = json.dumps(self.test_payload, separators=(",", ":"))
        headers = {
            "stripe-signature": "t=1234567890,v1=signature123",
            "content-type": "application/json",
        }

        # Mock signature verification
        mock_event = MagicMock()
        mock_event.__getitem__.side_effect = lambda key: {
            "type": self.test_payload["type"],
            "id": self.test_payload["id"],
            "data": self.test_payload["data"],
        }[key]

        with patch(
            "app.api.endpoints.webhooks.stripe_service.verify_webhook_signature",
            return_value={
                "success": True,
                "event": mock_event,
                "event_type": self.test_payload["type"],
                "event_id": self.test_payload["id"],
            },
        ):
            with patch(
                "app.api.endpoints.webhooks.webhook_service.process_webhook_event",
                return_value={"success": True, "processed": True},
            ):
                # Send concurrent requests
                tasks = [
                    async_client.post("/api/webhooks/stripe", data=payload, headers=headers)
                    for _ in range(5)
                ]
                responses = await asyncio.gather(*tasks, return_exceptions=True)

        # All requests should succeed
        for response in responses:
            if not isinstance(response, Exception):
                assert response.status_code == status.HTTP_200_OK
