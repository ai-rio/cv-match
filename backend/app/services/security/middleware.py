"""
Security middleware for LLM endpoints.

This module provides middleware functions to automatically apply
input sanitization and security monitoring to LLM API calls.
"""

import logging
import time
from typing import Any, Dict, Optional
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.services.security.input_sanitizer import (
    SanitizationResult,
    validate_request
)

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware to apply security measures to LLM endpoints."""

    def __init__(self, app, enable_rate_limiting: bool = True):
        """Initialize security middleware."""
        super().__init__(app)
        self.enable_rate_limiting = enable_rate_limiting
        self.request_times: dict[str, list[float]] = {}  # Simple in-memory tracking

    async def dispatch(self, request: Request, call_next):
        """Process request through security middleware."""
        start_time = time.time()

        # Only apply to LLM endpoints
        if not self._is_llm_endpoint(request.url.path):
            return await call_next(request)

        try:
            # Log request for security monitoring
            await self._log_security_event(request, "REQUEST_RECEIVED")

            # Get client info for rate limiting
            client_ip = self._get_client_ip(request)
            await self._extract_user_id(request)

            # Apply rate limiting if enabled
            if self.enable_rate_limiting and not self._check_request_rate(client_ip):
                await self._log_security_event(
                    request,
                    "RATE_LIMIT_EXCEEDED",
                    {"client_ip": client_ip}
                )
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Rate limit exceeded"}
                )

            # Process the request
            response = await call_next(request)

            # Log response for security monitoring
            process_time = time.time() - start_time
            await self._log_security_event(
                request,
                "REQUEST_COMPLETED",
                {
                    "status_code": response.status_code,
                    "process_time": process_time
                }
            )

            return response

        except Exception as e:
            await self._log_security_event(
                request,
                "SECURITY_ERROR",
                {"error": str(e), "client_ip": client_ip}
            )
            raise

    def _is_llm_endpoint(self, path: str) -> bool:
        """Check if the path is an LLM endpoint."""
        llm_endpoints = [
            "/api/llm/generate",
            "/api/llm/embedding",
            "/api/vectordb/documents",
            "/api/vectordb/search"
        ]
        return any(path.startswith(endpoint) for endpoint in llm_endpoints)

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fall back to client host
        return request.client.host if request.client else "unknown"

    async def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request if available."""
        try:
            # This would need to be implemented based on your auth system
            # For now, return None - in production, extract from JWT token
            return None
        except Exception:
            return None

    def _check_request_rate(self, client_ip: str) -> bool:
        """Check if client has exceeded request rate."""
        current_time = time.time()
        window_start = current_time - 60  # 1 minute window

        if client_ip not in self.request_times:
            self.request_times[client_ip] = []

        # Clean old entries
        self.request_times[client_ip] = [
            timestamp for timestamp in self.request_times[client_ip]
            if timestamp > window_start
        ]

        # Check rate limit (100 requests per minute by default)
        if len(self.request_times[client_ip]) >= 100:
            return False

        # Add current request
        self.request_times[client_ip].append(current_time)
        return True

    async def _log_security_event(
        self,
        request: Request,
        event_type: str,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log security-related events."""
        log_data = {
            "event_type": event_type,
            "path": request.url.path,
            "method": request.method,
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", ""),
            "timestamp": time.time()
        }

        if extra_data:
            log_data.update(extra_data)

        if event_type in ["RATE_LIMIT_EXCEEDED", "SECURITY_ERROR"]:
            logger.warning(f"Security event: {event_type}", extra=log_data)
        else:
            logger.info(f"Security event: {event_type}", extra=log_data)


async def validate_and_sanitize_request(
    request_data: Dict[str, Any],
    credentials: Optional[HTTPAuthorizationCredentials] = None,
    request: Optional[Request] = None
) -> Dict[str, Any]:
    """
    Validate and sanitize request data for LLM endpoints.

    Args:
        request_data: Raw request data
        credentials: Authentication credentials
        request: FastAPI request object

    Returns:
        Sanitized request data

    Raises:
        HTTPException: If validation fails
    """
    try:
        # Extract user info for rate limiting
        user_id = None
        client_ip = None

        if request:
            client_ip = request.client.host if request.client else "unknown"

        # Validate and sanitize request
        validation_results = validate_request(
            request_data,
            user_id=user_id,
            ip_address=client_ip
        )

        # Check if any validation failed
        unsafe_results = []
        for field, result in validation_results.items():
            if isinstance(result, list):
                # For documents, check if any document is unsafe
                if any(not doc_result.is_safe for doc_result in result):
                    unsafe_results.append(field)
            elif not result.is_safe:
                unsafe_results.append(field)

        if unsafe_results:
            error_messages = []
            for field in unsafe_results:
                result = validation_results[field]
                if isinstance(result, list):  # For documents
                    for i, doc_result in enumerate(result):
                        if not doc_result.is_safe:
                            error_messages.extend(doc_result.warnings)
                else:
                    error_messages.extend(result.warnings)

            await log_security_validation_failure(request_data, validation_results, client_ip)

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Input validation failed",
                    "unsafe_fields": unsafe_results,
                    "warnings": error_messages[:5]  # Limit to first 5 warnings
                }
            )

        # Replace original data with sanitized data
        sanitized_data = request_data.copy()

        for field, result in validation_results.items():
            if field == 'documents' and isinstance(result, list):
                # Handle documents array
                for i, doc_result in enumerate(result):
                    if i < len(sanitized_data['documents']):
                        sanitized_data['documents'][i]['text'] = doc_result.sanitized_input
            elif field in sanitized_data and isinstance(result, SanitizationResult):
                sanitized_data[field] = result.sanitized_input

        # Log successful validation
        await log_security_validation_success(request_data, validation_results, client_ip)

        return sanitized_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during request validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during request validation"
        )


async def log_security_validation_failure(
    request_data: Dict[str, Any],
    validation_results: Dict[str, Any],
    client_ip: Optional[str]
) -> None:
    """Log failed security validation."""
    logger.warning(
        "Security validation failed",
        extra={
            "event_type": "VALIDATION_FAILURE",
            "client_ip": client_ip,
            "validation_results": {
                field: {
                    "is_safe": (
                            result.is_safe if hasattr(result, 'is_safe')
                            else all(r.is_safe for r in result)
                        ),
                        "warnings": (
                            result.warnings if hasattr(result, 'warnings')
                            else [r.warnings for r in result]
                        ),
                        "blocked_patterns": (
                            result.blocked_patterns if hasattr(result, 'blocked_patterns')
                            else [r.blocked_patterns for r in result]
                        )
                }
                for field, result in validation_results.items()
            }
        }
    )


async def log_security_validation_success(
    request_data: Dict[str, Any],
    validation_results: Dict[str, Any],
    client_ip: Optional[str]
) -> None:
    """Log successful security validation."""
    logger.info(
        "Security validation passed",
        extra={
            "event_type": "VALIDATION_SUCCESS",
            "client_ip": client_ip,
            "fields_validated": list(validation_results.keys())
        }
    )


def create_security_error_response(
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Create a standardized security error response."""
    content = {
        "error": "Security validation failed",
        "message": message
    }

    if details:
        content.update(details)

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=content
    )