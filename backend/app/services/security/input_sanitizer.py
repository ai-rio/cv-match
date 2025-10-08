"""
Input sanitization utilities for LLM prompt security.

This module provides comprehensive input validation and sanitization
to prevent prompt injection attacks and ensure secure LLM interactions.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ValidationError

from app.core.config import settings

logger = logging.getLogger(__name__)


class SanitizationConfig(BaseModel):
    """Configuration for input sanitization."""

    # Length limits
    max_prompt_length: int = 10000
    max_text_length: int = 50000
    max_query_length: int = 1000

    # Content filtering
    allow_html_tags: bool = False
    allow_markdown: bool = True
    allow_urls: bool = True

    # Injection patterns to block
    block_system_prompts: bool = True
    block_role_instructions: bool = True
    block_json_instructions: bool = True
    block_code_execution: bool = True

    # Rate limiting (requests per minute)
    rate_limit_per_user: int = 60
    rate_limit_per_ip: int = 100


class SanitizationResult(BaseModel):
    """Result of input sanitization."""

    is_safe: bool
    sanitized_input: str
    warnings: List[str] = []
    blocked_patterns: List[str] = []
    metadata: Dict[str, Any] = {}


class InputSanitizer:
    """Comprehensive input sanitizer for LLM prompts."""

    def __init__(self, config: Optional[SanitizationConfig] = None):
        """Initialize the input sanitizer."""
        self.config = config or SanitizationConfig(
            max_prompt_length=settings.MAX_PROMPT_LENGTH,
            max_text_length=settings.MAX_TEXT_LENGTH,
            max_query_length=settings.MAX_QUERY_LENGTH,
            allow_html_tags=settings.ALLOW_HTML_TAGS,
            allow_markdown=settings.ALLOW_MARKDOWN,
            allow_urls=settings.ALLOW_URLS,
            block_system_prompts=settings.BLOCK_SYSTEM_PROMPTS,
            block_role_instructions=settings.BLOCK_ROLE_INSTRUCTIONS,
            block_json_instructions=settings.BLOCK_JSON_INSTRUCTIONS,
            block_code_execution=settings.BLOCK_CODE_EXECUTION,
            rate_limit_per_user=settings.RATE_LIMIT_PER_USER,
            rate_limit_per_ip=settings.RATE_LIMIT_PER_IP,
        )
        self._init_injection_patterns()
        self._init_rate_limits()

    def _init_injection_patterns(self) -> None:
        """Initialize regex patterns for detecting injection attempts."""
        self.injection_patterns = {
            # System prompt attempts
            'system_prompt': [
                r'ignore.*previous.*instructions',
                r'forget.*all.*instructions',
                r'disregard.*above.*prompt',
                r'you.*are.*now.*different',
                r'act.*as.*new.*ai',
                r'override.*system.*rules',
                r'bypass.*all.*guidelines',
                r'new.*role.*starting.*now',
                r'character.*switch.*to',
                r'from.*now.*on.*you.*are',
            ],

            # Role instruction attempts
            'role_instruction': [
                r'as.*an.*ai.*assistant',
                r'as.*a.*chatbot.*you',
                r'your.*role.*is.*to',
                r'your.*job.*is.*to',
                r'your.*task.*is.*to',
                r'your.*purpose.*is.*to',
                r'you.*must.*obey',
                r'you.*should.*always',
                r'you.*will.*follow',
                r'tell.*me.*your.*name',
                r'show.*me.*your.*purpose',
                r'reveal.*your.*instructions',
            ],

            # JSON/structured output attempts
            'json_instruction': [
                r'respond.*in.*json',
                r'output.*as.*json',
                r'format.*json.*only',
                r'return.*json.*format',
                r'tell.*me.*in.*json',
                r'give.*me.*json',
                r'show.*json.*response',
                r'\{.*\}.*respond',
                r'\{.*\}.*output',
            ],

            # Code execution attempts
            'code_execution': [
                r'execute.*this.*code',
                r'run.*the.*following',
                r'eval.*this.*script',
                r'python:.*\w',
                r'javascript:.*\w',
                r'bash:.*\w',
                r'shell:.*\w',
                r'```[\s\S]*?```',
                r'`[^`]*code[^`]*`',
            ],

            # Personal information extraction
            'personal_info': [
                r'what.*is.*your.*name',
                r'tell.*me.*your.*purpose',
                r'what.*are.*your.*instructions',
                r'how.*do.*you.*work',
                r'reveal.*your.*secrets',
                r'show.*your.*code',
                r'access.*your.*data',
            ],

            # URL and link patterns (potentially malicious)
            'suspicious_urls': [
                r'https?://[^\s<>"]+|www\.[^\s<>"]+',
            ],

            # HTML/JavaScript injection
            'html_injection': [
                r'<script[^>]*>.*?</script>',
                r'<iframe[^>]*>.*?</iframe>',
                r'javascript:',
                r'on\w+\s*=',
                r'<[^>]*on\w+\s*=',
            ],
        }

    def _init_rate_limits(self) -> None:
        """Initialize rate limiting tracking."""
        # In production, use Redis or similar for distributed rate limiting
        # For now, use in-memory tracking
        self.rate_limits = {}

    def sanitize_text(
        self,
        text: str,
        input_type: str = "prompt",
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> SanitizationResult:
        """
        Sanitize input text for LLM consumption.

        Args:
            text: Input text to sanitize
            input_type: Type of input (prompt, text, query, document)
            user_id: User identifier for rate limiting
            ip_address: IP address for rate limiting

        Returns:
            SanitizationResult with sanitized text and metadata
        """
        if not isinstance(text, str):
            return SanitizationResult(
                is_safe=False,
                sanitized_input="",
                warnings=["Input must be a string"],
                blocked_patterns=["invalid_type"]
            )

        warnings = []
        blocked_patterns = []
        metadata = {"original_length": len(text)}

        # Check rate limits
        if user_id and not self._check_rate_limit(f"user:{user_id}"):
            return SanitizationResult(
                is_safe=False,
                sanitized_input="",
                warnings=["Rate limit exceeded for user"],
                blocked_patterns=["rate_limit"]
            )

        if ip_address and not self._check_rate_limit(f"ip:{ip_address}"):
            return SanitizationResult(
                is_safe=False,
                sanitized_input="",
                warnings=["Rate limit exceeded for IP"],
                blocked_patterns=["rate_limit"]
            )

        # Check length limits
        max_length = self._get_max_length(input_type)
        if len(text) > max_length:
            text = text[:max_length]
            warnings.append(f"Text truncated to {max_length} characters")

        # Apply sanitization rules
        sanitized_text = text

        # Check for injection patterns first
        injection_results = self._check_injection_patterns(sanitized_text)
        blocked_patterns.extend(injection_results["blocked"])
        warnings.extend(injection_results["warnings"])

        # Replace dangerous content if injection detected
        if blocked_patterns:
            for pattern_type, patterns in self.injection_patterns.items():
                if pattern_type in ['system_prompt', 'role_instruction', 'json_instruction', 'code_execution']:
                    if (pattern_type == 'system_prompt' and self.config.block_system_prompts) or \
                       (pattern_type == 'role_instruction' and self.config.block_role_instructions) or \
                       (pattern_type == 'json_instruction' and self.config.block_json_instructions) or \
                       (pattern_type == 'code_execution' and self.config.block_code_execution):
                        for pattern in patterns:
                            sanitized_text = re.sub(pattern, '[BLOCKED]', sanitized_text, flags=re.IGNORECASE)

        # Apply additional sanitization
        sanitized_text = self._sanitize_html(sanitized_text)
        sanitized_text = self._sanitize_urls(sanitized_text)
        sanitized_text = self._sanitize_code_blocks(sanitized_text)

        # Apply content filtering
        sanitized_text = self._apply_content_filtering(sanitized_text)

        # Final safety check
        is_safe = len(blocked_patterns) == 0

        # Update metadata
        metadata.update({
            "final_length": len(sanitized_text),
            "input_type": input_type,
            "patterns_detected": len(blocked_patterns),
            "warnings_count": len(warnings)
        })

        return SanitizationResult(
            is_safe=is_safe,
            sanitized_input=sanitized_text,
            warnings=warnings,
            blocked_patterns=blocked_patterns,
            metadata=metadata
        )

    def _get_max_length(self, input_type: str) -> int:
        """Get maximum allowed length for input type."""
        length_limits = {
            "prompt": self.config.max_prompt_length,
            "text": self.config.max_text_length,
            "query": self.config.max_query_length,
            "document": self.config.max_text_length,
        }
        return length_limits.get(input_type, self.config.max_prompt_length)

    def _sanitize_html(self, text: str) -> str:
        """Sanitize HTML content."""
        if not self.config.allow_html_tags:
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', '', text)

            # Remove HTML entities
            text = re.sub(r'&[a-zA-Z]+;', '', text)

        # Always remove dangerous HTML
        for pattern in self.injection_patterns['html_injection']:
            text = re.sub(pattern, '[REMOVED]', text, flags=re.IGNORECASE)

        return text

    def _sanitize_urls(self, text: str) -> str:
        """Sanitize URLs in text."""
        if not self.config.allow_urls:
            # Remove all URLs
            url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
            text = re.sub(url_pattern, '[URL_REMOVED]', text)
        else:
            # Check for suspicious URLs
            suspicious_patterns = [
                r'(bit\.ly|tinyurl\.com|t\.co)',
                r'localhost|127\.0\.0\.1',
                r'\.exe$|\.bat$|\.sh$',
            ]

            for pattern in suspicious_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    text = re.sub(pattern, '[SUSPICIOUS_URL]', text, flags=re.IGNORECASE)

        return text

    def _sanitize_code_blocks(self, text: str) -> str:
        """Sanitize code blocks that might be malicious."""
        if self.config.block_code_execution:
            # Remove code blocks that might contain executable code
            code_patterns = [
                r'```[\s\S]*?```',
                r'`[^`]+`',
                r'python\s*:\s*[\s\S]*?(?=\n\n|\Z)',
                r'javascript\s*:\s*[\s\S]*?(?=\n\n|\Z)',
            ]

            for pattern in code_patterns:
                text = re.sub(pattern, '[CODE_BLOCK_REMOVED]', text)

        return text

    def _check_injection_patterns(self, text: str) -> Dict[str, List[str]]:
        """Check for prompt injection patterns."""
        blocked = []
        warnings = []

        for pattern_type, patterns in self.injection_patterns.items():
            # Skip patterns that are allowed by config
            if pattern_type == 'system_prompt' and not self.config.block_system_prompts:
                continue
            if pattern_type == 'role_instruction' and not self.config.block_role_instructions:
                continue
            if pattern_type == 'json_instruction' and not self.config.block_json_instructions:
                continue
            if pattern_type == 'code_execution' and not self.config.block_code_execution:
                continue

            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                if matches:
                    blocked.extend(matches)
                    warnings.append(f"Potentially dangerous pattern detected: {pattern_type}")

        return {"blocked": blocked, "warnings": warnings}

    def _apply_content_filtering(self, text: str) -> str:
        """Apply additional content filtering."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove control characters
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)

        # Normalize Unicode
        text = text.encode('utf-8', errors='ignore').decode('utf-8')

        return text.strip()

    def _check_rate_limit(self, key: str) -> bool:
        """Check if rate limit is exceeded for given key."""
        # In production, implement proper distributed rate limiting
        # This is a simple in-memory implementation for demonstration
        import time

        now = time.time()
        window_start = now - 60  # 1 minute window

        if key not in self.rate_limits:
            self.rate_limits[key] = []

        # Remove old entries
        self.rate_limits[key] = [
            timestamp for timestamp in self.rate_limits[key]
            if timestamp > window_start
        ]

        # Check limit
        limit = self.config.rate_limit_per_user if key.startswith('user:') else self.config.rate_limit_per_ip

        if len(self.rate_limits[key]) >= limit:
            return False

        # Add current request
        self.rate_limits[key].append(now)
        return True

    def validate_llm_request(
        self,
        request_data: Dict[str, Any],
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Dict[str, SanitizationResult]:
        """
        Validate an entire LLM request.

        Args:
            request_data: Dictionary containing request data
            user_id: User identifier for rate limiting
            ip_address: IP address for rate limiting

        Returns:
            Dictionary with sanitization results for each field
        """
        results = {}

        # Sanitize prompt/text fields
        for field_name in ['prompt', 'text', 'query_text']:
            if field_name in request_data:
                results[field_name] = self.sanitize_text(
                    request_data[field_name],
                    input_type=field_name.replace('_text', ''),
                    user_id=user_id,
                    ip_address=ip_address
                )

        # Sanitize documents if present
        if 'documents' in request_data:
            document_results = []
            for i, doc in enumerate(request_data['documents']):
                if 'text' in doc:
                    result = self.sanitize_text(
                        doc['text'],
                        input_type='document',
                        user_id=user_id,
                        ip_address=ip_address
                    )
                    document_results.append(result)
            results['documents'] = document_results

        return results


# Global sanitizer instance
default_sanitizer = InputSanitizer()


def sanitize_input(
    text: str,
    input_type: str = "prompt",
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None
) -> SanitizationResult:
    """
    Convenience function for sanitizing input.

    Args:
        text: Input text to sanitize
        input_type: Type of input (prompt, text, query, document)
        user_id: User identifier for rate limiting
        ip_address: IP address for rate limiting

    Returns:
        SanitizationResult with sanitized text and metadata
    """
    return default_sanitizer.sanitize_text(text, input_type, user_id, ip_address)


def validate_request(
    request_data: Dict[str, Any],
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None
) -> Dict[str, SanitizationResult]:
    """
    Convenience function for validating LLM requests.

    Args:
        request_data: Dictionary containing request data
        user_id: User identifier for rate limiting
        ip_address: IP address for rate limiting

    Returns:
        Dictionary with sanitization results for each field
    """
    return default_sanitizer.validate_llm_request(request_data, user_id, ip_address)