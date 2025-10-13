"""
Comprehensive security middleware for all API endpoints.

This module provides security middleware functions to protect against
common web vulnerabilities including injection attacks, rate limiting,
and request validation.
"""

import logging
import time
from typing import Any, Dict, List, Optional
from urllib.parse import unquote

from fastapi import HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
from app.services.security.input_sanitizer import SanitizationResult
from app.utils.validation import validate_dict, validate_string

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive security middleware for all API endpoints.

    Provides protection against:
    - Rate limiting
    - Request size limits
    - Input validation
    - HTTP security headers
    - IP-based blocking
    - Request logging
    """

    def __init__(
        self,
        app,
        enable_rate_limiting: bool = True,
        enable_input_validation: bool = True,
        enable_security_headers: bool = True,
        max_request_size: int = 10 * 1024 * 1024,  # 10MB
    ):
        """Initialize security middleware."""
        super().__init__(app)
        self.enable_rate_limiting = enable_rate_limiting
        self.enable_input_validation = enable_input_validation
        self.enable_security_headers = enable_security_headers
        self.max_request_size = max_request_size

        # Rate limiting storage (in production, use Redis)
        self.rate_limits: Dict[str, List[float]] = {}
        self.blocked_ips: Dict[str, float] = {}

        # Security configuration
        self.rate_limits_config = {
            "default": {"requests": 100, "window": 60},  # 100 requests per minute
            "auth": {"requests": 5, "window": 300},      # 5 requests per 5 minutes for auth
            "upload": {"requests": 10, "window": 3600},  # 10 uploads per hour
            "llm": {"requests": 60, "window": 60},       # 60 LLM requests per minute
        }

        # Blocked user agents and patterns
        self.blocked_user_agents = [
            "sqlmap", "nikto", "nmap", "masscan", "zap", "burp",
            "sqlninja", "havij", "pangolin", "bbscan", "netsparker"
        ]

        self.suspicious_patterns = [
            r"\.\./", r"\.\.\\",           # Path traversal
            r"<script", r"javascript:",     # XSS
            r"union.*select", r"drop.*table",  # SQL injection
            r"cmd\.exe", r"powershell",    # Command injection
        ]

    async def dispatch(self, request: Request, call_next):
        """Process request through security middleware."""
        start_time = time.time()
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "").lower()

        # Step 1: Check if IP is blocked
        if self._is_ip_blocked(client_ip):
            return self._create_security_response(
                "Access denied: IP address blocked",
                status.HTTP_403_FORBIDDEN,
                {"blocked_ip": client_ip}
            )

        # Step 2: Check user agent
        if self._is_user_agent_blocked(user_agent):
            return self._create_security_response(
                "Access denied: User agent blocked",
                status.HTTP_403_FORBIDDEN,
                {"blocked_user_agent": user_agent}
            )

        # Step 3: Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_request_size:
            return self._create_security_response(
                "Request too large",
                status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                {"max_size": self.max_request_size}
            )

        # Step 4: Rate limiting
        if self.enable_rate_limiting and not self._check_rate_limit(request, client_ip):
            await self._log_security_event(
                request, "RATE_LIMIT_EXCEEDED", {"client_ip": client_ip}
            )
            return self._create_security_response(
                "Rate limit exceeded",
                status.HTTP_429_TOO_MANY_REQUESTS,
                {"retry_after": "60"}
            )

        # Step 5: Log request for security monitoring
        await self._log_security_event(
            request, "REQUEST_RECEIVED", {"client_ip": client_ip, "user_agent": user_agent}
        )

        try:
            # Step 6: Process the request
            response = await call_next(request)

            # Step 7: Add security headers
            if self.enable_security_headers:
                response = self._add_security_headers(response)

            # Step 8: Log response for security monitoring
            process_time = time.time() - start_time
            await self._log_security_event(
                request,
                "REQUEST_COMPLETED",
                {
                    "status_code": response.status_code,
                    "process_time": process_time,
                    "client_ip": client_ip,
                },
            )

            return response

        except HTTPException as e:
            # Log HTTP exceptions
            await self._log_security_event(
                request,
                "HTTP_EXCEPTION",
                {
                    "status_code": e.status_code,
                    "detail": str(e.detail),
                    "client_ip": client_ip,
                },
            )
            raise

        except Exception as e:
            # Log unexpected errors
            await self._log_security_event(
                request,
                "SECURITY_ERROR",
                {"error": str(e), "client_ip": client_ip},
            )
            raise

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

    def _is_ip_blocked(self, client_ip: str) -> bool:
        """Check if IP address is blocked."""
        if client_ip in self.blocked_ips:
            # Check if block has expired (24 hours)
            block_time = self.blocked_ips[client_ip]
            if time.time() - block_time < 24 * 3600:  # 24 hours
                return True
            else:
                # Block expired, remove it
                del self.blocked_ips[client_ip]

        return False

    def _is_user_agent_blocked(self, user_agent: str) -> bool:
        """Check if user agent is blocked."""
        for blocked_agent in self.blocked_user_agents:
            if blocked_agent in user_agent:
                return True

        # Check for suspicious patterns
        for pattern in self.suspicious_patterns:
            import re
            if re.search(pattern, user_agent, re.IGNORECASE):
                return True

        return False

    def _check_rate_limit(self, request: Request, client_ip: str) -> bool:
        """Check if client has exceeded request rate."""
        # Determine rate limit category
        path = request.url.path.lower()
        if "/auth/" in path or "/login" in path:
            category = "auth"
        elif "/upload" in path:
            category = "upload"
        elif "/llm/" in path:
            category = "llm"
        else:
            category = "default"

        # Get rate limit configuration
        config = self.rate_limits_config.get(category, self.rate_limits_config["default"])
        max_requests = config["requests"]
        window = config["window"]

        # Create rate limit key
        rate_limit_key = f"{client_ip}:{category}"

        # Initialize rate limit tracking if needed
        if rate_limit_key not in self.rate_limits:
            self.rate_limits[rate_limit_key] = []

        # Clean old entries
        current_time = time.time()
        window_start = current_time - window
        self.rate_limits[rate_limit_key] = [
            timestamp for timestamp in self.rate_limits[rate_limit_key] if timestamp > window_start
        ]

        # Check rate limit
        if len(self.rate_limits[rate_limit_key]) >= max_requests:
            # Block IP temporarily if severely abusive
            if len(self.rate_limits[rate_limit_key]) > max_requests * 2:
                self.blocked_ips[client_ip] = current_time
            return False

        # Add current request
        self.rate_limits[rate_limit_key].append(current_time)
        return True

    def _add_security_headers(self, response: Response) -> Response:
        """Add security headers to response."""
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
        response.headers["Content-Security-Policy"] = csp

        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # HSTS (HTTPS only)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Permissions policy
        permissions_policy = (
            "geolocation=(), microphone=(), camera=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=()"
        )
        response.headers["Permissions-Policy"] = permissions_policy

        return response

    async def _log_security_event(
        self, request: Request, event_type: str, extra_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log security-related events."""
        log_data = {
            "event_type": event_type,
            "path": request.url.path,
            "method": request.method,
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", ""),
            "timestamp": time.time(),
        }

        if extra_data:
            log_data.update(extra_data)

        if event_type in ["RATE_LIMIT_EXCEEDED", "SECURITY_ERROR", "HTTP_EXCEPTION"]:
            logger.warning(f"Security event: {event_type}", extra=log_data)
        else:
            logger.info(f"Security event: {event_type}", extra=log_data)

    def _create_security_response(
        self, message: str, status_code: int, extra_data: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """Create a standardized security error response."""
        content = {
            "error": "Security validation failed",
            "message": message,
            "timestamp": time.time(),
        }

        if extra_data:
            content.update(extra_data)

        return JSONResponse(status_code=status_code, content=content)


class InputValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for automatic input validation and sanitization.

    This middleware automatically validates and sanitizes request bodies
    to prevent injection attacks and ensure input security.
    """

    def __init__(self, app, enable_validation: bool = True):
        """Initialize input validation middleware."""
        super().__init__(app)
        self.enable_validation = enable_validation

    async def dispatch(self, request: Request, call_next):
        """Process request through input validation."""
        if not self.enable_validation:
            return await call_next(request)

        # Skip validation for certain endpoints
        if self._should_skip_validation(request):
            return await call_next(request)

        try:
            # Validate and sanitize request body if present
            if request.method in ["POST", "PUT", "PATCH"] and (
                "application/json" in request.headers.get("content-type", "")
                or "multipart/form-data" in request.headers.get("content-type", "")
            ):
                # Store the original body for validation
                body = await request.body()

                # For JSON requests, validate the content
                if "application/json" in request.headers.get("content-type", ""):
                    validation_result = await self._validate_json_body(body, request)
                    if not validation_result["valid"]:
                        return JSONResponse(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            content={
                                "error": "Input validation failed",
                                "details": validation_result["errors"],
                                "warnings": validation_result.get("warnings", []),
                            },
                        )

            return await call_next(request)

        except Exception as e:
            logger.error(f"Input validation error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Input validation failed", "message": str(e)},
            )

    def _should_skip_validation(self, request: Request) -> bool:
        """Check if validation should be skipped for this endpoint."""
        skip_patterns = [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
            "/static/",
        ]

        path = request.url.path
        return any(pattern in path for pattern in skip_patterns)

    async def _validate_json_body(self, body: bytes, request: Request) -> Dict[str, Any]:
        """Validate JSON request body."""
        try:
            import json

            if not body.strip():
                return {"valid": True, "errors": []}

            json_data = json.loads(body.decode('utf-8'))

            # Validate the JSON data structure
            validation_result = validate_dict(json_data, max_items=100, max_value_length=10000)

            return {
                "valid": validation_result.is_valid,
                "errors": validation_result.errors,
                "warnings": validation_result.warnings,
                "sanitized_data": validation_result.sanitized_input,
            }

        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "errors": [f"Invalid JSON: {str(e)}"],
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
            }


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for comprehensive request logging.

    This middleware logs all requests for security monitoring and
    debugging purposes.
    """

    def __init__(self, app, log_body: bool = False, max_body_size: int = 1024):
        """Initialize request logging middleware."""
        super().__init__(app)
        self.log_body = log_body
        self.max_body_size = max_body_size

    async def dispatch(self, request: Request, call_next):
        """Process request with logging."""
        start_time = time.time()

        # Collect request information
        request_info = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", ""),
            "timestamp": start_time,
        }

        # Log request body if enabled (be careful with sensitive data)
        if self.log_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    # Truncate body if too large
                    body_str = body.decode('utf-8', errors='ignore')
                    if len(body_str) > self.max_body_size:
                        body_str = body_str[:self.max_body_size] + "... [truncated]"

                    # Remove sensitive data
                    body_str = self._sanitize_body_for_logging(body_str)
                    request_info["body"] = body_str
            except Exception as e:
                logger.warning(f"Failed to log request body: {str(e)}")

        # Log the request
        logger.info("Request received", extra=request_info)

        try:
            # Process the request
            response = await call_next(request)

            # Log response information
            process_time = time.time() - start_time
            response_info = {
                "status_code": response.status_code,
                "process_time": process_time,
                "response_headers": dict(response.headers),
            }

            logger.info("Request completed", extra={**request_info, **response_info})

            return response

        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            error_info = {
                "error": str(e),
                "process_time": process_time,
            }

            logger.error("Request failed", extra={**request_info, **error_info})
            raise

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"

    def _sanitize_body_for_logging(self, body: str) -> str:
        """Remove sensitive information from request body for logging."""
        import re

        # Remove common sensitive fields
        sensitive_patterns = [
            r'"password"\s*:\s*"[^"]*"',
            r'"token"\s*:\s*"[^"]*"',
            r'"api_key"\s*:\s*"[^"]*"',
            r'"secret"\s*:\s*"[^"]*"',
            r'"authorization"\s*:\s*"[^"]*"',
            r'"credit_card"\s*:\s*"[^"]*"',
            r'"ssn"\s*:\s*"[^"]*"',
        ]

        sanitized_body = body
        for pattern in sensitive_patterns:
            sanitized_body = re.sub(pattern, r'"\1": "[REDACTED]"', sanitized_body, flags=re.IGNORECASE)

        return sanitized_body


# Factory function for creating security middleware
def create_security_middleware(
    app,
    enable_rate_limiting: bool = True,
    enable_input_validation: bool = True,
    enable_security_headers: bool = True,
    enable_request_logging: bool = True,
    max_request_size: int = 10 * 1024 * 1024,
):
    """
    Create and configure security middleware stack.

    Args:
        app: FastAPI application
        enable_rate_limiting: Enable rate limiting middleware
        enable_input_validation: Enable input validation middleware
        enable_security_headers: Enable security headers middleware
        enable_request_logging: Enable request logging middleware
        max_request_size: Maximum request size in bytes

    Returns:
        FastAPI application with security middleware
    """
    # Add middleware in reverse order (last added runs first)

    if enable_request_logging:
        app.add_middleware(RequestLoggingMiddleware, log_body=False, max_body_size=1024)

    if enable_input_validation:
        app.add_middleware(InputValidationMiddleware, enable_validation=True)

    if enable_rate_limiting or enable_security_headers:
        app.add_middleware(
            SecurityMiddleware,
            enable_rate_limiting=enable_rate_limiting,
            enable_input_validation=False,  # Separate middleware handles this
            enable_security_headers=enable_security_headers,
            max_request_size=max_request_size,
        )

    return app