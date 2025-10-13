"""
Comprehensive input validation utilities for API security.

This module provides validation functions for various input types to prevent
injection attacks, validate data formats, and ensure input security.
"""

import hashlib
import logging
import os
import re
import uuid
from typing import Any, List, Optional, Set, Union

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ValidationResult(BaseModel):
    """Result of input validation."""

    is_valid: bool
    sanitized_input: Any
    warnings: List[str] = []
    errors: List[str] = []
    blocked_patterns: List[str] = []
    metadata: dict = {}


class InjectionPatterns:
    """Patterns for detecting injection attacks."""

    # SQL Injection patterns
    SQL_INJECTION = [
        r"'|\"|;|--|/\*|\*/|xp_|sp_|drop\s+table|insert\s+into",
        r"union\s+select|delete\s+from|update\s+set",
        r"exec\s*\(|execute\s*\(",
        r"cast\s*\(|convert\s*\(",
        r"substring\s*\(|char\s*\(",
        r"waitfor\s+delay|benchmark\s*\(",
    ]

    # NoSQL Injection patterns
    NOSQL_INJECTION = [
        r'\$where|\$ne|\$gt|\$lt|\$in|\$nin|\$exists|\$regex',
        r'\{.*\$.*\}',
        r'\$or|\$and|\$not|\$nor',
    ]

    # XSS patterns
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'vbscript:',
        r'onload\s*=',
        r'onerror\s*=',
        r'onclick\s*=',
        r'onmouseover\s*=',
        r'onfocus\s*=',
        r'onblur\s*=',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
    ]

    # Command injection patterns
    COMMAND_INJECTION = [
        r';|\||&|`|\$\(',
        r'rm\s+-rf|del\s+/f/s/q',
        r'cat\s+/etc/passwd|type\s+c:\\windows\\system32\\drivers\\etc\\hosts',
        r'nc\s+-l|netcat\s+-l',
        r'wget\s+|curl\s+',
        r'eval\s*\(|exec\s*\(',
        r'system\s*\(|passthru\s*\(',
        r'shell_exec\s*\(',
    ]

    # Path traversal patterns
    PATH_TRAVERSAL = [
        r'\.\./|\.\.\\',
        r'%2e%2e%2f|%2e%2e%5c',
        r'\x2e\x2e\x2f|\x2e\x2e\x5c',
        r'\.\.%c0%af|\.\.%c1%9c',
    ]

    # LDAP injection patterns
    LDAP_INJECTION = [
        r'\*\)|\(\*',
        r'\)\(.*\*\)|\(\|.*\)',
        r'&\(|\)&',
    ]


class InputValidator:
    """Comprehensive input validator."""

    def __init__(self):
        """Initialize the input validator."""
        self.injection_patterns = InjectionPatterns()
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for better performance."""
        self.compiled_patterns = {}

        for category, patterns in self.injection_patterns.__dict__.items():
            if not category.startswith('_') and isinstance(patterns, list):
                self.compiled_patterns[category.lower()] = [
                    re.compile(pattern, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                    for pattern in patterns
                ]

    def validate_string(
        self,
        input_str: str,
        input_type: str = "general",
        max_length: int = 1000,
        allow_html: bool = False,
        allow_urls: bool = True,
    ) -> ValidationResult:
        """
        Validate string input against injection attacks.

        Args:
            input_str: String to validate
            input_type: Type of input (general, email, name, etc.)
            max_length: Maximum allowed length
            allow_html: Whether HTML is allowed
            allow_urls: Whether URLs are allowed

        Returns:
            ValidationResult with validation details
        """
        if not isinstance(input_str, str):
            return ValidationResult(
                is_valid=False,
                sanitized_input="",
                errors=["Input must be a string"],
                blocked_patterns=["invalid_type"]
            )

        result = ValidationResult(
            is_valid=True,
            sanitized_input=input_str,
            warnings=[],
            errors=[],
            blocked_patterns=[]
        )

        # Length validation
        if len(input_str) > max_length:
            result.sanitized_input = input_str[:max_length]
            result.warnings.append(f"Input truncated to {max_length} characters")

        # Null byte check
        if '\x00' in result.sanitized_input:
            result.sanitized_input = result.sanitized_input.replace('\x00', '')
            result.warnings.append("Null bytes removed from input")

        # Check for injection patterns
        self._check_injection_patterns(result.sanitized_input, result)

        # HTML validation
        if not allow_html:
            result.sanitized_input = self._sanitize_html(result.sanitized_input, result)

        # URL validation
        if not allow_urls:
            result.sanitized_input = self._sanitize_urls(result.sanitized_input, result)

        # Apply content filtering
        result.sanitized_input = self._apply_content_filtering(result.sanitized_input)

        # Final validation based on input type
        self._validate_by_type(result.sanitized_input, input_type, result)

        result.metadata.update({
            "original_length": len(input_str),
            "final_length": len(result.sanitized_input),
            "input_type": input_type,
            "patterns_detected": len(result.blocked_patterns),
        })

        return result

    def _check_injection_patterns(self, input_str: str, result: ValidationResult):
        """Check for injection patterns in input."""
        input_lower = input_str.lower()

        for category, patterns in self.compiled_patterns.items():
            category_matched = False

            for pattern in patterns:
                if pattern.search(input_str):
                    category_matched = True
                    break

            if category_matched:
                result.blocked_patterns.append(category)
                result.errors.append(f"Potentially dangerous pattern detected: {category}")
                result.is_valid = False

    def _sanitize_html(self, text: str, result: ValidationResult) -> str:
        """Sanitize HTML content."""
        # Remove dangerous HTML tags and attributes
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'<iframe[^>]*>.*?</iframe>',
            r'<object[^>]*>.*?</object>',
            r'<embed[^>]*>.*?</embed>',
            r'<applet[^>]*>.*?</applet>',
            r'<meta[^>]*>',
            r'<link[^>]*>',
            r'<style[^>]*>.*?</style>',
            r'on\w+\s*=\s*["\'][^"\']*["\']',
            r'javascript:',
            r'vbscript:',
        ]

        sanitized = text
        for pattern in dangerous_patterns:
            matches = re.findall(pattern, sanitized, re.IGNORECASE | re.DOTALL)
            if matches:
                result.warnings.append(f"Dangerous HTML content removed")
                result.blocked_patterns.append("html_injection")
                sanitized = re.sub(pattern, "[REMOVED]", sanitized, flags=re.IGNORECASE | re.DOTALL)

        return sanitized

    def _sanitize_urls(self, text: str, result: ValidationResult) -> str:
        """Sanitize URLs in text."""
        # Remove suspicious URLs
        url_patterns = [
            r'(https?://|www\.)[^\s<>"]+',
            r'localhost:\d+|127\.0\.0\.1:\d+',
            r'(bit\.ly|tinyurl\.com|t\.co)/[^\s]+',
        ]

        sanitized = text
        for pattern in url_patterns:
            matches = re.findall(pattern, sanitized, re.IGNORECASE)
            if matches:
                result.warnings.append("URLs removed from input")
                result.blocked_patterns.append("suspicious_urls")
                sanitized = re.sub(pattern, "[URL_REMOVED]", sanitized, flags=re.IGNORECASE)

        return sanitized

    def _apply_content_filtering(self, text: str) -> str:
        """Apply additional content filtering."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove control characters (except newline, tab, carriage return)
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)

        # Normalize Unicode
        text = text.encode('utf-8', errors='ignore').decode('utf-8')

        return text.strip()

    def _validate_by_type(self, input_str: str, input_type: str, result: ValidationResult):
        """Validate input based on specific type."""
        if input_type == "email":
            if not self._validate_email_format(input_str):
                result.is_valid = False
                result.errors.append("Invalid email format")

        elif input_type == "name":
            if not self._validate_name_format(input_str):
                result.is_valid = False
                result.errors.append("Invalid name format")

        elif input_type == "uuid":
            if not self._validate_uuid_format(input_str):
                result.is_valid = False
                result.errors.append("Invalid UUID format")

        elif input_type == "phone":
            if not self._validate_phone_format(input_str):
                result.is_valid = False
                result.errors.append("Invalid phone format")

    def _validate_email_format(self, email: str) -> bool:
        """Validate email format."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))

    def _validate_name_format(self, name: str) -> bool:
        """Validate name format."""
        # Allow letters, spaces, hyphens, apostrophes, and accented characters
        name_pattern = r"^[a-zA-Z\u00C0-\u017F\s\-'\.]+$"
        return bool(re.match(name_pattern, name)) and len(name.strip()) > 0

    def _validate_uuid_format(self, uuid_str: str) -> bool:
        """Validate UUID format."""
        try:
            uuid.UUID(uuid_str)
            return True
        except ValueError:
            return False

    def _validate_phone_format(self, phone: str) -> bool:
        """Validate phone format (Brazilian and international)."""
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)

        # Brazilian phone: 10-11 digits (with DDD)
        # International phone: 7-15 digits
        return 7 <= len(digits_only) <= 15

    def validate_dict(
        self,
        input_dict: dict,
        allowed_keys: Optional[Set[str]] = None,
        max_items: int = 50,
        max_key_length: int = 50,
        max_value_length: int = 1000,
    ) -> ValidationResult:
        """
        Validate dictionary input.

        Args:
            input_dict: Dictionary to validate
            allowed_keys: Set of allowed keys (None for any)
            max_items: Maximum number of items
            max_key_length: Maximum key length
            max_value_length: Maximum value length

        Returns:
            ValidationResult with validation details
        """
        if not isinstance(input_dict, dict):
            return ValidationResult(
                is_valid=False,
                sanitized_input={},
                errors=["Input must be a dictionary"],
                blocked_patterns=["invalid_type"]
            )

        result = ValidationResult(
            is_valid=True,
            sanitized_input={},
            warnings=[],
            errors=[],
            blocked_patterns=[]
        )

        # Check item count
        if len(input_dict) > max_items:
            result.is_valid = False
            result.errors.append(f"Too many items: {len(input_dict)} (max: {max_items})")
            return result

        # Validate each key-value pair
        for key, value in input_dict.items():
            # Validate key
            if not isinstance(key, str):
                result.warnings.append(f"Non-string key converted: {key}")
                key = str(key)

            if len(key) > max_key_length:
                result.warnings.append(f"Key too long, truncated: {key}")
                key = key[:max_key_length]

            if allowed_keys and key not in allowed_keys:
                result.warnings.append(f"Unexpected key removed: {key}")
                continue

            # Validate value
            if isinstance(value, str):
                if len(value) > max_value_length:
                    result.warnings.append(f"Value too long for key {key}, truncated")
                    value = value[:max_value_length]

                # Validate string values for injection
                string_result = self.validate_string(
                    value,
                    input_type="general",
                    max_length=max_value_length
                )

                if not string_result.is_valid:
                    result.errors.extend([f"Key {key}: {error}" for error in string_result.errors])
                    result.blocked_patterns.extend(string_result.blocked_patterns)
                    result.is_valid = False
                else:
                    result.warnings.extend([f"Key {key}: {warning}" for warning in string_result.warnings])
                    value = string_result.sanitized_input

            elif isinstance(value, (dict, list)):
                # Recursively validate nested structures
                if isinstance(value, dict):
                    nested_result = self.validate_dict(
                        value,
                        allowed_keys,
                        max_items=max_items,
                        max_key_length=max_key_length,
                        max_value_length=max_value_length
                    )
                else:  # list
                    nested_result = self.validate_list(
                        value,
                        max_items=max_items,
                        max_item_length=max_value_length
                    )

                if not nested_result.is_valid:
                    result.errors.extend([f"Key {key}: {error}" for error in nested_result.errors])
                    result.blocked_patterns.extend(nested_result.blocked_patterns)
                    result.is_valid = False
                else:
                    result.warnings.extend([f"Key {key}: {warning}" for warning in nested_result.warnings])
                    value = nested_result.sanitized_input

            # Add validated key-value pair
            result.sanitized_input[key] = value

        result.metadata.update({
            "item_count": len(result.sanitized_input),
            "original_item_count": len(input_dict),
        })

        return result

    def validate_list(
        self,
        input_list: list,
        max_items: int = 100,
        max_item_length: int = 1000,
    ) -> ValidationResult:
        """
        Validate list input.

        Args:
            input_list: List to validate
            max_items: Maximum number of items
            max_item_length: Maximum item length

        Returns:
            ValidationResult with validation details
        """
        if not isinstance(input_list, list):
            return ValidationResult(
                is_valid=False,
                sanitized_input=[],
                errors=["Input must be a list"],
                blocked_patterns=["invalid_type"]
            )

        result = ValidationResult(
            is_valid=True,
            sanitized_input=[],
            warnings=[],
            errors=[],
            blocked_patterns=[]
        )

        # Check item count
        if len(input_list) > max_items:
            result.is_valid = False
            result.errors.append(f"Too many items: {len(input_list)} (max: {max_items})")
            return result

        # Validate each item
        for i, item in enumerate(input_list):
            if isinstance(item, str):
                # Validate string items
                string_result = self.validate_string(
                    item,
                    input_type="general",
                    max_length=max_item_length
                )

                if not string_result.is_valid:
                    result.errors.extend([f"Item {i}: {error}" for error in string_result.errors])
                    result.blocked_patterns.extend(string_result.blocked_patterns)
                    result.is_valid = False
                else:
                    result.warnings.extend([f"Item {i}: {warning}" for warning in string_result.warnings])
                    result.sanitized_input.append(string_result.sanitized_input)

            elif isinstance(item, dict):
                # Validate dictionary items
                dict_result = self.validate_dict(
                    item,
                    max_items=max_items,
                    max_key_length=50,
                    max_value_length=max_item_length
                )

                if not dict_result.is_valid:
                    result.errors.extend([f"Item {i}: {error}" for error in dict_result.errors])
                    result.blocked_patterns.extend(dict_result.blocked_patterns)
                    result.is_valid = False
                else:
                    result.warnings.extend([f"Item {i}: {warning}" for warning in dict_result.warnings])
                    result.sanitized_input.append(dict_result.sanitized_input)

            else:
                # Other types, just add as-is
                result.sanitized_input.append(item)

        result.metadata.update({
            "item_count": len(result.sanitized_input),
            "original_item_count": len(input_list),
        })

        return result


# Global validator instance
default_validator = InputValidator()


def validate_string(
    input_str: str,
    input_type: str = "general",
    max_length: int = 1000,
    allow_html: bool = False,
    allow_urls: bool = True,
) -> ValidationResult:
    """
    Validate string input using default validator.

    Args:
        input_str: String to validate
        input_type: Type of input
        max_length: Maximum allowed length
        allow_html: Whether HTML is allowed
        allow_urls: Whether URLs are allowed

    Returns:
        ValidationResult with validation details
    """
    return default_validator.validate_string(
        input_str, input_type, max_length, allow_html, allow_urls
    )


def validate_dict(
    input_dict: dict,
    allowed_keys: Optional[Set[str]] = None,
    max_items: int = 50,
    max_key_length: int = 50,
    max_value_length: int = 1000,
) -> ValidationResult:
    """
    Validate dictionary input using default validator.

    Args:
        input_dict: Dictionary to validate
        allowed_keys: Set of allowed keys
        max_items: Maximum number of items
        max_key_length: Maximum key length
        max_value_length: Maximum value length

    Returns:
        ValidationResult with validation details
    """
    return default_validator.validate_dict(
        input_dict, allowed_keys, max_items, max_key_length, max_value_length
    )


def validate_uuid(uuid_str: str) -> ValidationResult:
    """
    Validate UUID format.

    Args:
        uuid_str: UUID string to validate

    Returns:
        ValidationResult with validation details
    """
    return default_validator.validate_string(uuid_str, input_type="uuid")


def validate_email(email: str) -> ValidationResult:
    """
    Validate email format.

    Args:
        email: Email string to validate

    Returns:
        ValidationResult with validation details
    """
    return default_validator.validate_string(email, input_type="email")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for secure storage.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove dangerous characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)

    # Remove null bytes and control characters
    sanitized = re.sub(r'[\x00-\x1f\x7f]', '', sanitized)

    # Remove path traversal
    sanitized = sanitized.replace('..', '').replace('/', '').replace('\\', '')

    # Limit length
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:255-len(ext)] + ext

    # Ensure it's not empty
    if not sanitized:
        sanitized = "upload"

    return sanitized.strip()


def generate_safe_hash(content: str) -> str:
    """
    Generate a safe hash for content.

    Args:
        content: Content to hash

    Returns:
        SHA-256 hash
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()