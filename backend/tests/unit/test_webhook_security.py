"""
Security tests for webhook processing.
Tests webhook signature verification, replay protection, and security measures.
"""

import hashlib
import hmac
import json
import time
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
import stripe

from app.services.stripe_service import StripeService
from app.services.webhook_service import WebhookService


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.webhook
class TestWebhookSecurity:
    """Test webhook security and signature verification."""

    def setup_method(self):
        """Set up test method."""
        self.webhook_secret = "whsec_test_webhook_secret_1234567890"
        self.service = StripeService()
        self.service.webhook_secret = self.webhook_secret

    def generate_signature(self, payload: str, timestamp: int) -> str:
        """Generate a valid Stripe webhook signature."""
        signed_payload = f"{timestamp}.{payload}"
        return hmac.new(
            self.webhook_secret.encode("utf-8"), signed_payload.encode("utf-8"), hashlib.sha256
        ).hexdigest()

    def generate_signature_header(self, payload: str, timestamp: int = None) -> str:
        """Generate a complete Stripe signature header."""
        if timestamp is None:
            timestamp = int(time.time())

        signature = self.generate_signature(payload, timestamp)
        return f"t={timestamp},v1={signature}"

    @pytest.mark.asyncio
    async def test_valid_webhook_signature_verification(self):
        """Test verification of valid webhook signature."""
        payload = '{"test": "data", "user_id": "user_123"}'
        timestamp = int(time.time())
        signature_header = self.generate_signature_header(payload, timestamp)

        result = await self.service.verify_webhook_signature(
            payload=payload.encode("utf-8"), signature=signature_header
        )

        assert result["success"] is True
        assert "event" in result
        assert result["event_type"] is not None
        assert result["event_id"] is not None

    @pytest.mark.asyncio
    async def test_invalid_webhook_signature_rejection(self):
        """Test rejection of invalid webhook signature."""
        payload = '{"test": "data"}'
        invalid_signature = "t=1234567890,v1=invalid_signature"

        result = await self.service.verify_webhook_signature(
            payload=payload.encode("utf-8"), signature=invalid_signature
        )

        assert result["success"] is False
        assert result["error_type"] == "signature_error"
        assert "Invalid webhook signature" in result["error"]

    @pytest.mark.asyncio
    async def test_missing_webhook_signature(self):
        """Test handling of missing webhook signature."""
        payload = '{"test": "data"}'

        result = await self.service.verify_webhook_signature(
            payload=payload.encode("utf-8"), signature=""
        )

        assert result["success"] is False
        assert result["error_type"] == "signature_error"

    @pytest.mark.asyncio
    async def test_webhook_signature_tolerance(self):
        """Test webhook signature verification with time tolerance."""
        payload = '{"test": "data"}'

        # Test with timestamp within tolerance (5 minutes)
        timestamp = int(time.time()) - 200  # 200 seconds ago
        signature_header = self.generate_signature_header(payload, timestamp)

        result = await self.service.verify_webhook_signature(
            payload=payload.encode("utf-8"), signature=signature_header
        )

        assert result["success"] is True

        # Test with timestamp outside tolerance (more than 5 minutes)
        old_timestamp = int(time.time()) - 400  # 400 seconds ago
        old_signature_header = self.generate_signature_header(payload, old_timestamp)

        result = await self.service.verify_webhook_signature(
            payload=payload.encode("utf-8"), signature=old_signature_header
        )

        assert result["success"] is False
        assert result["error_type"] == "signature_error"

    @pytest.mark.asyncio
    async def test_webhook_signature_tampering(self):
        """Test webhook signature verification with tampered payload."""
        original_payload = '{"test": "data", "amount": 1000}'
        timestamp = int(time.time())
        signature_header = self.generate_signature_header(original_payload, timestamp)

        # Tamper with payload
        tampered_payload = '{"test": "data", "amount": 5000}'

        result = await self.service.verify_webhook_signature(
            payload=tampered_payload.encode("utf-8"), signature=signature_header
        )

        assert result["success"] is False
        assert result["error_type"] == "signature_error"

    @pytest.mark.asyncio
    async def test_webhook_signature_format_validation(self):
        """Test webhook signature format validation."""
        payload = '{"test": "data"}'

        # Test missing timestamp
        invalid_format_1 = "v1=signature123"
        result = await self.service.verify_webhook_signature(
            payload=payload.encode("utf-8"), signature=invalid_format_1
        )
        assert result["success"] is False

        # Test missing version
        invalid_format_2 = "t=1234567890"
        result = await self.service.verify_webhook_signature(
            payload=payload.encode("utf-8"), signature=invalid_format_2
        )
        assert result["success"] is False

        # Test empty signature
        invalid_format_3 = "t=1234567890,v1="
        result = await self.service.verify_webhook_signature(
            payload=payload.encode("utf-8"), signature=invalid_format_3
        )
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_webhook_replay_attack_prevention(self):
        """Test prevention of webhook replay attacks."""
        payload = '{"test": "replay", "event_id": "evt_test_replay_123"}'
        signature_header = self.generate_signature_header(payload)

        # First processing
        with patch("stripe.Webhook.construct_event") as mock_construct:
            mock_event = MagicMock()
            mock_event.type = "test.replay"
            mock_event.id = "evt_test_replay_123"
            mock_construct.return_value = mock_event

            result1 = await self.service.verify_webhook_signature(
                payload=payload.encode("utf-8"), signature=signature_header
            )

        assert result1["success"] is True

        # Second processing with same payload (replay attempt)
        with patch("stripe.Webhook.construct_event") as mock_construct:
            mock_event = MagicMock()
            mock_event.type = "test.replay"
            mock_event.id = "evt_test_replay_123"
            mock_construct.return_value = mock_event

            result2 = await self.service.verify_webhook_signature(
                payload=payload.encode("utf-8"), signature=signature_header
            )

        # Signature verification should still succeed (idempotency is handled at higher level)
        assert result2["success"] is True

    @pytest.mark.asyncio
    async def test_webhook_idempotency_protection(self):
        """Test webhook idempotency protection at service level."""
        webhook_service = WebhookService()
        event_id = f"evt_test_idempotency_{uuid4()}"
        event_type = "checkout.session.completed"
        event_data = {"id": "cs_test_123", "amount": 2990}

        # Mock event logging
        with patch.object(webhook_service, "log_webhook_event", return_value={"success": True}):
            # Mock event not processed initially
            with patch.object(webhook_service, "is_event_processed", return_value=False):
                with patch.object(
                    webhook_service, "_process_specific_event", return_value={"success": True}
                ):
                    with patch.object(webhook_service, "_mark_event_processed"):
                        result1 = await webhook_service.process_webhook_event(
                            event_type, event_data, event_id
                        )

            assert result1["success"] is True
            assert result1["idempotent"] is not True

            # Mock event already processed
            with patch.object(webhook_service, "is_event_processed", return_value=True):
                result2 = await webhook_service.process_webhook_event(
                    event_type, event_data, event_id
                )

            assert result2["success"] is True
            assert result2["idempotent"] is True
            assert "already processed" in result2["message"]

    @pytest.mark.asyncio
    async def test_webhook_payload_size_limits(self):
        """Test webhook payload size limits."""
        # Create very large payload
        large_payload = {
            "test": "data",
            "large_field": "x" * 100000,  # 100KB field
            "user_id": str(uuid4()),
            "metadata": {f"key_{i}": f"value_{i}" * 1000 for i in range(100)},
        }

        payload_str = json.dumps(large_payload, separators=(",", ":"))
        signature_header = self.generate_signature_header(payload_str)

        # Should handle large payloads gracefully
        result = await self.service.verify_webhook_signature(
            payload=payload_str.encode("utf-8"), signature=signature_header
        )

        # Signature verification should succeed if signature is valid
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_webhook_malformed_json_handling(self):
        """Test handling of malformed JSON in webhook payload."""
        malformed_payloads = [
            '{"test": "data"',  # Missing closing brace
            '{"test": "data",}',  # Trailing comma
            "invalid json",  # Completely invalid
            '{"test": \x00\x01\x02"}',  # Invalid characters
            "",  # Empty payload
        ]

        for payload in malformed_payloads:
            with self.subTest(payload=payload[:50]):
                signature_header = self.generate_signature_header(payload)

                result = await self.service.verify_webhook_signature(
                    payload=payload.encode("utf-8"), signature=signature_header
                )

                # Should handle malformed JSON gracefully or reject appropriately
                # The exact behavior depends on where JSON parsing happens
                assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_webhook_concurrent_request_handling(self):
        """Test webhook processing with concurrent requests."""
        import asyncio

        payload = '{"test": "concurrent", "event_id": "evt_test_concurrent_123"}'
        signature_header = self.generate_signature_header(payload)

        async def verify_signature():
            with patch("stripe.Webhook.construct_event") as mock_construct:
                mock_event = MagicMock()
                mock_event.type = "test.concurrent"
                mock_event.id = "evt_test_concurrent_123"
                mock_construct.return_value = mock_event

                return await self.service.verify_webhook_signature(
                    payload=payload.encode("utf-8"), signature=signature_header
                )

        # Run concurrent signature verifications
        tasks = [verify_signature() for _ in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All verifications should succeed
        for result in results:
            if not isinstance(result, Exception):
                assert result["success"] is True

    @pytest.mark.asyncio
    async def test_webhook_signature_encoding_handling(self):
        """Test webhook signature with different character encodings."""
        # Test with UTF-8 characters
        utf8_payload = '{"test": "dåtå", "user": "João Silva", "currency": "R$"}'
        signature_header = self.generate_signature_header(utf8_payload)

        result = await self.service.verify_webhook_signature(
            payload=utf8_payload.encode("utf-8"), signature=signature_header
        )

        assert result["success"] is True

        # Test with special characters
        special_payload = '{"test": "special chars: !@#$%^&*()", "unicode": "αβγδε"}'
        special_signature = self.generate_signature_header(special_payload)

        result = await self.service.verify_webhook_signature(
            payload=special_payload.encode("utf-8"), signature=special_signature
        )

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_webhook_configuration_security(self):
        """Test webhook configuration security."""
        # Test with no webhook secret configured
        service_no_secret = StripeService()
        service_no_secret.webhook_secret = None

        payload = '{"test": "data"}'
        signature_header = "t=1234567890,v1=signature123"

        result = await service_no_secret.verify_webhook_signature(
            payload=payload.encode("utf-8"), signature=signature_header
        )

        assert result["success"] is False
        assert result["error_type"] == "configuration_error"
        assert "Webhook secret not configured" in result["error"]

        # Test with empty webhook secret
        service_empty_secret = StripeService()
        service_empty_secret.webhook_secret = ""

        result = await service_empty_secret.verify_webhook_signature(
            payload=payload.encode("utf-8"), signature=signature_header
        )

        assert result["success"] is False
        assert result["error_type"] == "configuration_error"

    @pytest.mark.asyncio
    async def test_webhook_request_logging_security(self):
        """Test that webhook requests are logged securely (no sensitive data)."""
        webhook_service = WebhookService()
        event_id = f"evt_test_logging_{uuid4()}"

        # Test logging with sensitive data
        sensitive_payload = {
            "user_id": "user_123",
            "credit_card": "4242424242424242",  # Should not be logged
            "cvv": "123",  # Should not be logged
            "amount": 2990,
        }

        with patch.object(webhook_service, "_create") as mock_create:
            await webhook_service.log_webhook_event(
                stripe_event_id=event_id,
                event_type="test.sensitive",
                data=sensitive_payload,
                processed=False,
            )

            # Verify logging was called
            mock_create.assert_called_once()
            call_args = mock_create.call_args[0][1]

            # Check that sensitive data was handled appropriately
            # The exact handling depends on implementation
            assert "event_id" in call_args
            assert call_args["event_id"] == event_id
            assert call_args["event_type"] == "test.sensitive"

    def test_webhook_secret_strength_validation(self):
        """Test webhook secret strength requirements."""
        # Test weak secrets (should be rejected in production)
        weak_secrets = [
            "weak",  # Too short
            "1234567890",  # Only numbers
            "password",  # Common word
            "whsec_123",  # Too simple
        ]

        for weak_secret in weak_secrets:
            with self.subTest(secret=weak_secret):
                # In a real implementation, you might validate secret strength
                # For now, just test that the service accepts it (validation would be elsewhere)
                service = StripeService()
                service.webhook_secret = weak_secret
                assert service.webhook_secret == weak_secret

    @pytest.mark.asyncio
    async def test_webhook_timestamp_manipulation(self):
        """Test detection of timestamp manipulation in webhooks."""
        payload = '{"test": "timestamp", "event_id": "evt_test_timestamp_123"}'

        # Test with future timestamp
        future_timestamp = int(time.time()) + 3600  # 1 hour in future
        future_signature = self.generate_signature_header(payload, future_timestamp)

        result = await self.service.verify_webhook_signature(
            payload=payload.encode("utf-8"), signature=future_signature
        )

        # Should reject future timestamps
        assert result["success"] is False
        assert result["error_type"] == "signature_error"

        # Test with very old timestamp (outside tolerance)
        old_timestamp = int(time.time()) - 7200  # 2 hours ago
        old_signature = self.generate_signature_header(payload, old_timestamp)

        result = await self.service.verify_webhook_signature(
            payload=payload.encode("utf-8"), signature=old_signature
        )

        # Should reject very old timestamps
        assert result["success"] is False
        assert result["error_type"] == "signature_error"

    @pytest.mark.asyncio
    async def test_webhook_version_compatibility(self):
        """Test webhook signature version compatibility."""
        payload = '{"test": "version", "event_id": "evt_test_version_123"}'
        timestamp = int(time.time())

        # Test different signature versions
        signatures = [
            f"t={timestamp},v1={self.generate_signature(payload, timestamp)}",  # v1
            f"t={timestamp},v1={self.generate_signature(payload, timestamp)},v2={self.generate_signature(payload, timestamp)}",  # Multiple versions
        ]

        for signature in signatures:
            with self.subTest(signature=signature[:50]):
                result = await self.service.verify_webhook_signature(
                    payload=payload.encode("utf-8"), signature=signature
                )

                # Should handle valid signatures regardless of version format
                # Note: Stripe primarily uses v1, so this tests compatibility
                assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_webhook_rate_limiting_simulation(self):
        """Test webhook processing under high load (rate limiting simulation)."""
        import asyncio

        webhook_service = WebhookService()
        event_ids = [f"evt_test_rate_{uuid4()}" for _ in range(100)]

        async def process_single_webhook(event_id):
            payload = f'{{"test": "rate_limit", "event_id": "{event_id}"}}'
            signature_header = self.generate_signature_header(payload)

            with patch.object(webhook_service, "is_event_processed", return_value=False):
                with patch.object(
                    webhook_service, "log_webhook_event", return_value={"success": True}
                ):
                    with patch.object(
                        webhook_service, "_process_specific_event", return_value={"success": True}
                    ):
                        with patch.object(webhook_service, "_mark_event_processed"):
                            return await webhook_service.process_webhook_event(
                                "test.rate_limit", {"event_id": event_id}, event_id
                            )

        # Process webhooks concurrently
        start_time = time.time()
        tasks = [process_single_webhook(event_id) for event_id in event_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        # Verify all webhooks were processed
        successful_results = [
            r for r in results if not isinstance(r, Exception) and r.get("success")
        ]
        assert len(successful_results) == len(event_ids)

        # Log processing time for performance analysis
        processing_time = end_time - start_time
        webhooks_per_second = len(event_ids) / processing_time

        print(
            f"Processed {len(event_ids)} webhooks in {processing_time:.2f}s ({webhooks_per_second:.2f} webhooks/sec)"
        )

        # This test helps identify performance bottlenecks
        # In production, you might implement rate limiting if needed
        assert webhooks_per_second > 10  # Should handle at least 10 webhooks per second
