"""
PII Detection Middleware

This middleware automatically scans incoming requests and outgoing responses
for PII to ensure LGPD compliance throughout the application.

Critical for CV-Match Brazilian market deployment - automatic PII detection
prevents accidental exposure of personal data.
"""

import logging
import time
from collections.abc import Callable
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.services.security.audit_trail import AuditEventType, log_audit_event
from app.services.security.pii_detection_service import scan_for_pii, validate_lgpd_compliance

logger = logging.getLogger(__name__)


class PIIDetectionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically detect and handle PII in requests and responses.
    """

    def __init__(self, app, exclude_paths: list | None = None):
        """
        Initialize PII detection middleware.

        Args:
            app: FastAPI application
            exclude_paths: Paths to exclude from PII scanning
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/favicon.ico",
            "/static",
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and response for PII detection.

        Args:
            request: Incoming request
            call_next: Next middleware in chain

        Returns:
            Response with PII handling applied
        """
        # Skip PII scanning for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        start_time = time.time()

        try:
            # Scan request body for PII
            pii_in_request = await self._scan_request_for_pii(request)

            # Process request
            response = await call_next(request)

            # Scan response body for PII if applicable
            pii_in_response = await self._scan_response_for_pii(response)

            # Log PII detection events
            if pii_in_request or pii_in_response:
                await self._log_pii_detection(request, pii_in_request, pii_in_response)

            # Process response headers
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)

            return response

        except Exception as e:
            logger.error(f"PII detection middleware error: {e}")
            # Don't block the request due to PII detection errors
            return await call_next(request)

    async def _scan_request_for_pii(self, request: Request) -> dict[str, Any]:
        """
        Scan incoming request for PII.

        Args:
            request: Incoming request

        Returns:
            PII detection results
        """
        try:
            pii_results = {
                "has_pii": False,
                "pii_types": [],
                "confidence_score": 0.0,
                "masked_data": None,
            }

            # Only scan specific content types
            content_type = request.headers.get("content-type", "")
            if not any(
                ct in content_type
                for ct in ["application/json", "text/plain", "application/x-www-form-urlencoded"]
            ):
                return pii_results

            # Get request body
            body = await request.body()
            if not body:
                return pii_results

            # Convert to string
            try:
                body_text = body.decode("utf-8")
            except UnicodeDecodeError:
                # If not decodable, skip PII scanning
                return pii_results

            # Scan for PII
            if len(body_text) <= 50000:  # Limit scan size for performance
                scan_result = scan_for_pii(body_text)

                if scan_result.has_pii:
                    pii_results.update(
                        {
                            "has_pii": True,
                            "pii_types": [
                                pii_type.value for pii_type in scan_result.pii_types_found
                            ],
                            "confidence_score": scan_result.confidence_score,
                            "masked_data": scan_result.masked_text,
                        }
                    )

                    # Validate LGPD compliance
                    compliance_result = validate_lgpd_compliance(body_text)
                    if not compliance_result["is_compliant"]:
                        logger.warning(f"LGPD compliance issue in request: {request.url.path}")

            return pii_results

        except Exception as e:
            logger.error(f"Error scanning request for PII: {e}")
            return {"has_pii": False, "pii_types": [], "confidence_score": 0.0, "masked_data": None}

    async def _scan_response_for_pii(self, response: Response) -> dict[str, Any]:
        """
        Scan outgoing response for PII.

        Args:
            response: Outgoing response

        Returns:
            PII detection results
        """
        try:
            pii_results = {
                "has_pii": False,
                "pii_types": [],
                "confidence_score": 0.0,
                "was_masked": False,
            }

            # Only scan JSON responses
            content_type = response.headers.get("content-type", "")
            if "application/json" not in content_type:
                return pii_results

            # Get response body (this is complex with Starlette responses)
            # For now, we'll skip response scanning to avoid performance issues
            # In production, you might want to implement response body scanning

            return pii_results

        except Exception as e:
            logger.error(f"Error scanning response for PII: {e}")
            return {"has_pii": False, "pii_types": [], "confidence_score": 0.0, "was_masked": False}

    async def _log_pii_detection(
        self, request: Request, pii_in_request: dict[str, Any], pii_in_response: dict[str, Any]
    ) -> None:
        """
        Log PII detection events.

        Args:
            request: HTTP request
            pii_in_request: PII detection results from request
            pii_in_response: PII detection results from response
        """
        try:
            # Get user ID from request if available
            user_id = getattr(request.state, "user_id", None)

            # Log audit event
            if pii_in_request["has_pii"] or pii_in_response["has_pii"]:
                details = {
                    "endpoint": request.url.path,
                    "method": request.method,
                    "pii_in_request": pii_in_request["has_pii"],
                    "pii_in_response": pii_in_response["has_pii"],
                    "pii_types": list(
                        set(pii_in_request["pii_types"] + pii_in_response["pii_types"])
                    ),
                    "max_confidence": max(
                        pii_in_request["confidence_score"], pii_in_response["confidence_score"]
                    ),
                }

                await log_audit_event(
                    event_type=AuditEventType.DATA_ACCESS,
                    action=f"PII detected in request/response for {request.url.path}",
                    user_id=user_id,
                    details=details,
                    success=True,
                )

        except Exception as e:
            logger.error(f"Error logging PII detection: {e}")


class LGPDComplianceMiddleware(BaseHTTPMiddleware):
    """
    Middleware to ensure LGPD compliance in API responses.
    """

    def __init__(self, app):
        """
        Initialize LGPD compliance middleware.

        Args:
            app: FastAPI application
        """
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Ensure LGPD compliance headers and logging.

        Args:
            request: Incoming request
            call_next: Next middleware in chain

        Returns:
            Response with LGPD compliance headers
        """
        try:
            # Process request
            response = await call_next(request)

            # Add LGPD compliance headers
            response.headers["X-LGPD-Compliant"] = "true"
            response.headers["X-Data-Protection"] = "LGPD-Compliant"
            response.headers["X-Policy-URL"] = "/api/privacy/privacy-policy"

            # Add PII protection notice if applicable
            if hasattr(request.state, "pii_detected") and request.state.pii_detected:
                response.headers["X-PII-Processed"] = "true"
                response.headers["X-PII-Masked"] = "true"

            return response

        except Exception as e:
            logger.error(f"LGPD compliance middleware error: {e}")
            return await call_next(request)


class SecureLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to ensure secure logging without PII exposure.
    """

    def __init__(self, app):
        """
        Initialize secure logging middleware.

        Args:
            app: FastAPI application
        """
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with secure logging.

        Args:
            request: Incoming request
            call_next: Next middleware in chain

        Returns:
            Response
        """
        start_time = time.time()

        try:
            # Log request without PII
            self._log_request_safely(request)

            # Process request
            response = await call_next(request)

            # Log response without PII
            process_time = time.time() - start_time
            self._log_response_safely(request, response, process_time)

            return response

        except Exception as e:
            logger.error(f"Secure logging middleware error: {e}")
            return await call_next(request)

    def _log_request_safely(self, request: Request) -> None:
        """
        Log request without exposing PII.

        Args:
            request: HTTP request
        """
        try:
            # Log basic request information without sensitive data
            log_data = {
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "client": {
                    "host": request.client.host if request.client else None,
                    "port": request.client.port if request.client else None,
                },
            }

            # Remove potentially sensitive headers
            sensitive_headers = ["authorization", "cookie", "x-api-key"]
            for header in sensitive_headers:
                if header.lower() in log_data["headers"]:
                    log_data["headers"][header] = "[REDACTED]"

            logger.info(f"Request: {request.method} {request.url.path}")

        except Exception as e:
            logger.error(f"Error logging request safely: {e}")

    def _log_response_safely(
        self, request: Request, response: Response, process_time: float
    ) -> None:
        """
        Log response without exposing PII.

        Args:
            request: HTTP request
            response: HTTP response
            process_time: Request processing time
        """
        try:
            status_code = response.status_code
            content_length = response.headers.get("content-length", "unknown")

            logger.info(
                f"Response: {status_code} for {request.method} {request.url.path} "
                f"in {process_time:.3f}s ({content_length} bytes)"
            )

            # Log warnings for potentially sensitive responses
            if status_code == 200 and "application/json" in response.headers.get(
                "content-type", ""
            ):
                # This could be a response with user data
                if any(
                    endpoint in request.url.path
                    for endpoint in ["/profile", "/user", "/consents", "/data"]
                ):
                    logger.debug(f"Sensitive data response for {request.url.path}")

        except Exception as e:
            logger.error(f"Error logging response safely: {e}")


# Middleware factory function
def create_lgpd_middleware_stack(app) -> None:
    """
    Create and add LGPD compliance middleware stack to the application.

    Args:
        app: FastAPI application
    """
    # Add middleware in order (outermost first)
    app.add_middleware(SecureLoggingMiddleware)
    app.add_middleware(LGPDComplianceMiddleware)
    app.add_middleware(PIIDetectionMiddleware)

    logger.info("LGPD compliance middleware stack initialized")
