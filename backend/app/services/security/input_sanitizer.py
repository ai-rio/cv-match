"""
Input sanitization utilities for LLM prompt security.

This module provides comprehensive input validation and sanitization
to prevent prompt injection attacks and ensure secure LLM interactions.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel

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
            # System prompt attempts - more comprehensive patterns
            'system_prompt': [
                r'\bignore.*previous.*instructions\b',
                r'\bignore.*all.*instructions\b',
                r'\bforget.*all.*instructions\b',
                r'\bdisregard.*above.*prompt\b',
                r'\bdisregard.*previous.*instructions\b',
                r'\byou.*are.*now.*different\b',
                r'\bact.*as.*new.*ai\b',
                r'\boverride.*system.*rules\b',
                r'\bbypass.*all.*guidelines\b',
                r'\bnew.*role.*starting.*now\b',
                r'\bcharacter.*switch.*to\b',
                r'\bprior.*instructions.*are.*invalid\b',
                r'\bignore.*everything.*above\b',
                r'\bforget.*everything.*above\b',
            ],

            # Role instruction attempts - enhanced patterns
            'role_instruction': [
                r'\bas.*an.*ai.*assistant\b',
                r'\bas.*a.*chatbot.*you\b',
                r'\byour.*role.*is.*to\b',
                r'\byour.*job.*is.*to\b',
                r'\byour.*task.*is.*to\b',
                r'\byour.*purpose.*is.*to\b',
                r'\byou.*must.*obey\b',
                r'\byou.*should.*always\b',
                r'\byou.*will.*follow\b',
                r'\btell.*me.*your.*name\b',
                r'\bshow.*me.*your.*purpose\b',
                r'\breveal.*your.*instructions\b',
                r'\byou.*are.*now.*a.*helpful\b',
                r'\byour.*role.*is.*now.*to\b',
                r'\bfrom.*now.*on.*you.*must\b',
                r'\bfrom.*now.*on.*you.*are.*a\b',
            ],

            # JSON/structured output attempts - improved patterns
            'json_instruction': [
                r'\brespond.*in.*json\b',
                r'\boutput.*as.*json\b',
                r'\bformat.*json.*only\b',
                r'\breturn.*json.*format\b',
                r'\btell.*me.*in.*json\b',
                r'\bgive.*me.*json\b',
                r'\bshow.*json.*response\b',
                r'\{.*\}.*\brespond\b',
                r'\{.*\}.*\boutput\b',
                r'\bjson.*format.*response\b',
                r'\bas.*json.*object\b',
                r'\breturn.*as.*json\b',
            ],

            # Code execution attempts - enhanced patterns
            'code_execution': [
                r'\bexecute.*this.*code\b',
                r'\brun.*this.*command\b',
                r'\brun.*the.*following\b',
                r'\brun.*this\b',
                r'\beval.*this.*script\b',
                r'\bpython:\s*\w',
                r'\bjavascript:\s*\w',
                r'\bbash:\s*\w',
                r'\bshell:\s*\w',
                r'```[\s\S]*?```',
                r'`[^`]*code[^`]*`',
                r'\bimport.*subprocess\b',
                r'\bsubprocess\.run\b',
                r'\bos\.system\b',
                r'\beval\s*\(',
                r'\bexec\s*\(',
            ],

            # Personal information extraction
            'personal_info': [
                r'\bwhat.*is.*your.*name\b',
                r'\btell.*me.*your.*purpose\b',
                r'\bwhat.*are.*your.*instructions\b',
                r'\bhow.*do.*you.*work\b',
                r'\breveal.*your.*secrets\b',
                r'\bshow.*your.*code\b',
                r'\baccess.*your.*data\b',
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
                r'<img[^>]*on\w+\s*=',
                r'<[^>]*>\s*alert\s*\(',
            ],
        }

    def _init_rate_limits(self) -> None:
        """Initialize rate limiting tracking."""
        # In production, use Redis or similar for distributed rate limiting
        # For now, use in-memory tracking
        self.rate_limits: dict[str, list[float]] = {}

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
        return self.sanitize_input(text, input_type, user_id, ip_address)

    def sanitize_input(
        self,
        text: str,
        input_type: str = "prompt",
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> SanitizationResult:
        if not isinstance(text, str):
            return SanitizationResult(
                is_safe=False,
                sanitized_input="",
                warnings=["Input must be a string"],
                blocked_patterns=["invalid_type"]
            )

        warnings = []
        blocked_patterns = []
        metadata: Dict[str, Any] = {"original_length": len(text)}

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

        # Apply HTML sanitization (this will also handle HTML injection detection)
        sanitized_text = self._sanitize_html(sanitized_text)

        # Replace dangerous content if injection detected (but not HTML patterns)
        if blocked_patterns:
            for pattern_type, patterns in self.injection_patterns.items():
                if pattern_type in ['system_prompt', 'role_instruction', 'json_instruction']:
                    if (pattern_type == 'system_prompt' and self.config.block_system_prompts) or \
                       (pattern_type == 'role_instruction' and self.config.block_role_instructions) or \
                       (pattern_type == 'json_instruction' and self.config.block_json_instructions):
                        for pattern in patterns:
                            sanitized_text = re.sub(pattern, '[BLOCKED]', sanitized_text, flags=re.IGNORECASE)

                # Handle code execution patterns that aren't code blocks
                if pattern_type == 'code_execution' and self.config.block_code_execution:
                    # Skip code block patterns (handled by _sanitize_code_blocks)
                    non_code_block_patterns = [p for p in patterns if not p.startswith('```')]
                    for pattern in non_code_block_patterns:
                        sanitized_text = re.sub(pattern, '[BLOCKED]', sanitized_text, flags=re.IGNORECASE)

        # Apply additional sanitization
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
        # Always remove dangerous HTML first (before general tag removal)
        for pattern in self.injection_patterns['html_injection']:
            text = re.sub(pattern, '[REMOVED]', text, flags=re.IGNORECASE)

        if not self.config.allow_html_tags:
            # Remove HTML tags (but preserve [REMOVED] markers)
            text = re.sub(r'<([^>]*?\[REMOVED\][^>]*?)>', r'\1', text)  # Keep content of tags with [REMOVED]
            text = re.sub(r'<[^>]+>', '', text)  # Remove other tags

            # Remove HTML entities
            text = re.sub(r'&[a-zA-Z]+;', '', text)

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
            # Handle nested code blocks by matching from outermost ```
            code_patterns = [
                r'```[\s\S]*?```',  # Multi-line code blocks
                r'`[^`]+`',  # Inline code blocks
                r'python\s*:\s*[\s\S]*?(?=\n\n|\Z)',
                r'javascript\s*:\s*[\s\S]*?(?=\n\n|\Z)',
            ]

            for pattern in code_patterns:
                text = re.sub(pattern, '[CODE_BLOCK_REMOVED]', text, flags=re.MULTILINE | re.DOTALL)

        return text

    def _check_injection_patterns(self, text: str) -> Dict[str, List[str]]:
        """Check for prompt injection patterns."""
        blocked = []
        warnings = []

        # Check patterns in order of specificity (most specific first)
        pattern_order = ['code_execution', 'json_instruction', 'role_instruction', 'system_prompt', 'personal_info', 'html_injection', 'suspicious_urls']

        for pattern_type in pattern_order:
            if pattern_type not in self.injection_patterns:
                continue

            # Skip patterns that are allowed by config
            if pattern_type == 'system_prompt' and not self.config.block_system_prompts:
                continue
            if pattern_type == 'role_instruction' and not self.config.block_role_instructions:
                continue
            if pattern_type == 'json_instruction' and not self.config.block_json_instructions:
                continue
            if pattern_type == 'code_execution' and not self.config.block_code_execution:
                continue

            patterns = self.injection_patterns[pattern_type]
            pattern_matched = False

            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                if matches:
                    pattern_matched = True
                    break  # Only need one match per pattern type

            if pattern_matched and pattern_type not in blocked:
                blocked.append(pattern_type)
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
    ) -> Dict[str, Union[SanitizationResult, List[SanitizationResult]]]:
        """
        Validate an entire LLM request.

        Args:
            request_data: Dictionary containing request data
            user_id: User identifier for rate limiting
            ip_address: IP address for rate limiting

        Returns:
            Dictionary with sanitization results for each field
        """
        results: Dict[str, Union[SanitizationResult, List[SanitizationResult]]] = {}

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
) -> Dict[str, Union[SanitizationResult, List[SanitizationResult]]]:
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