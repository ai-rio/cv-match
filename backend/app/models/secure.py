"""
Enhanced Pydantic models with comprehensive security validation.

This module provides secure request/response models with input validation,
sanitization, and injection attack prevention for all API endpoints.
"""

import re
import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class SecureBaseModel(BaseModel):
    """Base model with security features for all request models."""

    class Config:
        # Enable strict validation
        strict = True
        # Prevent extra fields
        extra = "forbid"
        # Validate assignment
        validate_assignment = True


class SecureLoginRequest(SecureBaseModel):
    """Secure login request with injection protection."""

    email: EmailStr = Field(..., max_length=254, description="User email address")
    password: str = Field(
        ..., min_length=8, max_length=128, description="User password (8-128 characters)"
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email against injection patterns."""
        # Check for suspicious email patterns
        dangerous_patterns = [
            r"<script",
            r"javascript:",
            r"data:text/html",
            r"vbscript:",
            r"onload=",
            r"onerror=",
        ]

        email_lower = v.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, email_lower):
                raise ValueError("Invalid email format detected")

        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password against injection patterns."""
        # Check for SQL injection patterns
        sql_injection_patterns = [
            r"'|\"|;|--|/\*|\*/|xp_|sp_|drop\s+table|insert\s+into",
            r"union\s+select|delete\s+from|update\s+set",
        ]

        # Check for script injection
        script_patterns = [
            r"<script|</script|javascript:|vbscript:|onload=|onerror=",
        ]

        password_lower = v.lower()
        for pattern in sql_injection_patterns + script_patterns:
            if re.search(pattern, password_lower):
                raise ValueError("Invalid password format detected")

        return v


class SecureUserRegistrationRequest(SecureBaseModel):
    """Secure user registration request with comprehensive validation."""

    email: EmailStr = Field(..., max_length=254)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=100)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        """Validate full name against injection patterns."""
        # Remove excessive whitespace
        v = " ".join(v.split())

        # Check for dangerous patterns
        dangerous_patterns = [
            r"<script|</script|javascript:|vbscript:",
            r"onload=|onerror=|onclick=|onmouseover=",
        ]

        name_lower = v.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, name_lower):
                raise ValueError("Invalid name format detected")

        # Check for name format (allow letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-Z\u00C0-\u017F\s\-'\.]+$", v):
            raise ValueError("Name contains invalid characters")

        return v


class SecureFileUploadRequest(SecureBaseModel):
    """Secure file upload request with comprehensive validation."""

    filename: str = Field(..., min_length=1, max_length=255)
    file_size: int = Field(..., ge=1, le=10 * 1024 * 1024)  # 1 byte to 10MB
    content_type: str = Field(
        ...,
        pattern=r"^(application/pdf|application/vnd\.openxmlformats-officedocument\.wordprocessingml\.document|text/plain)$",
    )

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, v: str) -> str:
        """Validate filename against path traversal and injection attacks."""
        # Check for path traversal attempts
        if ".." in v or "/" in v or "\\" in v:
            raise ValueError("Invalid filename: path traversal detected")

        # Check for null bytes
        if "\x00" in v:
            raise ValueError("Invalid filename: null bytes detected")

        # Check for reserved names (Windows)
        reserved_names = [
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM7",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9",
        ]

        name_without_ext = v.split(".")[0].upper()
        if name_without_ext in reserved_names:
            raise ValueError("Invalid filename: reserved name detected")

        # Check for dangerous characters
        dangerous_chars = ["<", ">", ":", '"', "|", "?", "*"]
        if any(char in v for char in dangerous_chars):
            raise ValueError("Invalid filename: contains illegal characters")

        # Check file extension
        allowed_extensions = [".pdf", ".docx", ".txt"]
        if not any(v.lower().endswith(ext) for ext in allowed_extensions):
            raise ValueError("Invalid file extension. Allowed: .pdf, .docx, .txt")

        return v


class SecurePaymentRequest(SecureBaseModel):
    """Secure payment request with validation."""

    tier: Literal["basic", "pro", "enterprise"] = Field(..., description="Subscription tier")
    amount: int = Field(..., ge=50, le=999900)  # R$ 0,50 to R$ 9.999,00
    currency: str = Field(default="brl", pattern=r"^[A-Z]{3}$")
    user_email: EmailStr = Field(..., max_length=254)

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: int) -> int:
        """Validate payment amount to prevent injection and fraud."""
        # Check for reasonable limits for Brazilian market
        if v < 50:  # R$ 0,50 minimum
            raise ValueError("Amount too small")
        if v > 999900:  # R$ 9.999,00 maximum for single transaction
            raise ValueError("Amount too large")

        return v

    @model_validator(mode="after")
    def validate_payment_consistency(self) -> "SecurePaymentRequest":
        """Validate payment consistency for tier pricing."""
        tier_prices = {
            "basic": 2990,  # R$ 29,90
            "pro": 7900,  # R$ 79,00
            "enterprise": 9990,  # R$ 99,90
        }

        expected_price = tier_prices.get(self.tier)
        if expected_price and abs(self.amount - expected_price) > 100:  # Allow R$ 1,00 variance
            raise ValueError(f"Amount does not match expected price for tier {self.tier}")

        return self


class SecureWebhookRequest(SecureBaseModel):
    """Secure webhook request with validation."""

    event_type: str = Field(..., min_length=1, max_length=100)
    event_id: str = Field(..., min_length=1, max_length=100)
    signature: str = Field(..., min_length=1, max_length=500)
    payload: dict[str, Any] = Field(default_factory=dict)

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, v: str) -> str:
        """Validate webhook event type against allowed types."""
        allowed_event_types = [
            "checkout.session.completed",
            "checkout.session.expired",
            "invoice.payment_succeeded",
            "invoice.payment_failed",
            "customer.subscription.created",
            "customer.subscription.updated",
            "customer.subscription.deleted",
            "payment_intent.succeeded",
            "payment_intent.payment_failed",
            "payment_intent.canceled",
        ]

        if v not in allowed_event_types:
            raise ValueError(f"Invalid event type: {v}")

        return v

    @field_validator("signature")
    @classmethod
    def validate_signature(cls, v: str) -> str:
        """Validate webhook signature format."""
        # Basic signature format validation (Stripe signatures)
        if not re.match(r"^whsec_[a-zA-Z0-9]{24,}$", v):
            raise ValueError("Invalid signature format")

        return v


class SecureUUIDRequest(SecureBaseModel):
    """Secure UUID parameter request with validation."""

    resource_id: str = Field(..., min_length=36, max_length=36)

    @field_validator("resource_id")
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        """Validate UUID format to prevent injection."""
        try:
            # Try to parse as UUID
            uuid.UUID(v)
        except ValueError:
            raise ValueError("Invalid UUID format")

        return v


class SecurePaginationRequest(SecureBaseModel):
    """Secure pagination request with validation."""

    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0, le=1000)

    @field_validator("limit")
    @classmethod
    def validate_limit(cls, v: int) -> int:
        """Validate pagination limit to prevent resource exhaustion."""
        if v > 100:
            raise ValueError("Limit too large")
        return v

    @field_validator("offset")
    @classmethod
    def validate_offset(cls, v: int) -> int:
        """Validate pagination offset."""
        if v > 1000:
            raise ValueError("Offset too large")
        return v


class SecureSearchRequest(SecureBaseModel):
    """Secure search request with injection protection."""

    query: str = Field(..., min_length=1, max_length=500)
    search_type: Literal["resume", "job", "user"] = Field(default="resume")

    @field_validator("query")
    @classmethod
    def validate_search_query(cls, v: str) -> str:
        """Validate search query against injection attacks."""
        # Check for SQL injection patterns
        sql_patterns = [
            r"'|\"|;|--|/\*|\*/|xp_|sp_|drop\s+table|insert\s+into",
            r"union\s+select|delete\s+from|update\s+set",
        ]

        # Check for NoSQL injection patterns
        nosql_patterns = [
            r"\$where|\$ne|\$gt|\$lt|\$in|\$nin",
            r"\{.*\$.*\}",
        ]

        query_lower = v.lower()
        for pattern in sql_patterns + nosql_patterns:
            if re.search(pattern, query_lower):
                raise ValueError("Invalid search query detected")

        # Remove excessive whitespace
        v = " ".join(v.split())

        return v


class SecureTextContentRequest(SecureBaseModel):
    """Secure text content request with comprehensive validation."""

    content: str = Field(..., min_length=1, max_length=50000)
    content_type: Literal["text", "markdown", "html"] = Field(default="text")

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate content against injection attacks."""
        # Check for script injection
        script_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"vbscript:",
            r"onload\s*=",
            r"onerror\s*=",
            r"onclick\s*=",
        ]

        content_lower = v.lower()
        for pattern in script_patterns:
            if re.search(pattern, content_lower, re.IGNORECASE | re.DOTALL):
                raise ValueError("Invalid content: script injection detected")

        # Check for excessive repetition (potential DoS)
        if len(set(v.split())) < len(v.split()) * 0.1:  # Less than 10% unique words
            raise ValueError("Content appears to be spam")

        return v


class SecureMetadataRequest(SecureBaseModel):
    """Secure metadata request with validation."""

    metadata: dict[str, str] = Field(default_factory=lambda: dict[str, str], max_items=50)

    @model_validator(mode="after")
    def validate_metadata(self) -> "SecureMetadataRequest":
        """Validate metadata fields against injection."""
        if not self.metadata:
            return self

        for key, value in self.metadata.items():
            # Validate key format
            if not re.match(r"^[a-zA-Z0-9_-]+$", key):
                raise ValueError(f"Invalid metadata key: {key}")

            # Validate key length
            if len(key) > 50:
                raise ValueError(f"Metadata key too long: {key}")

            # Validate value length
            if len(value) > 500:
                raise ValueError(f"Metadata value too long for key: {key}")

            # Check for injection patterns in values
            dangerous_patterns = [
                r"<script|</script|javascript:|vbscript:",
                r"onload=|onerror=|onclick=",
                r"\x00|\x0a|\x0d",  # Null bytes and newlines
            ]

            for pattern in dangerous_patterns:
                if re.search(pattern, value, re.IGNORECASE):
                    raise ValueError(f"Invalid metadata value for key: {key}")

        return self


# Response models with security
class SecureResponse(SecureBaseModel):
    """Base secure response model."""

    success: bool = Field(default=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str | None = None


class SecureErrorResponse(SecureBaseModel):
    """Secure error response model."""

    success: bool = Field(default=False)
    error: str = Field(..., min_length=1, max_length=500)
    error_code: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str | None = None


class SecureValidationResponse(SecureBaseModel):
    """Secure validation response model."""

    is_valid: bool
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    sanitized_data: dict[str, Any] | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
