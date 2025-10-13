"""
PII Masking Utilities for LGPD Compliance

This module provides comprehensive PII masking functionality to ensure that
personally identifiable information is protected in logs, outputs, and error messages.
Critical for LGPD compliance in the Brazilian market.
"""

import hashlib
import logging
import re
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class MaskingLevel(Enum):
    """Levels of PII masking."""

    NONE = "none"          # No masking (development only)
    PARTIAL = "partial"    # Partial masking (show some characters)
    FULL = "full"         # Full masking (complete replacement)
    HASH = "hash"         # Hash the value (irreversible)


@dataclass
class MaskingRule:
    """Rule for masking specific types of data."""

    pattern: str
    mask_char: str = "*"
    show_first: int = 0
    show_last: int = 0
    preserve_format: bool = False
    masking_level: MaskingLevel = MaskingLevel.PARTIAL


class PIIMasker:
    """Advanced PII masking utility with multiple strategies."""

    def __init__(self):
        """Initialize PII masker with comprehensive rules."""
        self._init_brazilian_rules()
        self._init_standard_rules()
        self._init_financial_rules()
        self._init_context_rules()

    def _init_brazilian_rules(self) -> None:
        """Initialize Brazilian-specific masking rules."""

        self.brazilian_rules = {
            "cpf": MaskingRule(
                pattern=r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b',
                mask_char="*",
                show_first=2,
                show_last=2,
                preserve_format=True
            ),
            "rg": MaskingRule(
                pattern=r'\b\d{1,2}\.?\d{3}\.?\d{3}-?[A-Z0-9]?\b',
                mask_char="*",
                show_first=1,
                show_last=1,
                preserve_format=True
            ),
            "cnpj": MaskingRule(
                pattern=r'\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b',
                mask_char="*",
                show_first=2,
                show_last=2,
                preserve_format=True
            ),
        }

    def _init_standard_rules(self) -> None:
        """Initialize standard masking rules."""

        self.standard_rules = {
            "email": MaskingRule(
                pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
                mask_char="*",
                show_first=1,
                show_last=1,
                preserve_format=True
            ),
            "phone": MaskingRule(
                pattern=r'\b(?:\+?55\s?)?(?:\(?\d{2}\)?[-\s]?)?\d{4,5}[-\s]?\d{4}\b',
                mask_char="*",
                show_first=2,
                show_last=2,
                preserve_format=True
            ),
            "cep": MaskingRule(
                pattern=r'\b\d{5}-?\d{3}\b',
                mask_char="*",
                show_first=2,
                show_last=1,
                preserve_format=True
            ),
        }

    def _init_financial_rules(self) -> None:
        """Initialize financial data masking rules."""

        self.financial_rules = {
            "credit_card": MaskingRule(
                pattern=r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
                mask_char="*",
                show_first=4,
                show_last=4,
                preserve_format=True
            ),
            "bank_account": MaskingRule(
                pattern=r'\b\d{6,}-?\d{1,}-?\d{1,}\b',
                mask_char="*",
                show_first=2,
                show_last=1,
                preserve_format=True
            ),
        }

    def _init_context_rules(self) -> None:
        """Initialize context-aware masking rules."""

        self.context_rules = {
            "address": MaskingRule(
                pattern=r'\b(?:Rua|Avenida|Alameda|Travessa|Praia|Praça)\s+[^,\n]+,\s*\d+[^,\n]*',
                mask_char="*",
                show_first=0,
                show_last=0,
                preserve_format=False
            ),
            "full_name": MaskingRule(
                pattern=r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\s*(?:[A-Z][a-z]+)?\b',
                mask_char="*",
                show_first=1,
                show_last=1,
                preserve_format=False
            ),
        }

    def mask_text(self, text: str, masking_level: MaskingLevel = MaskingLevel.PARTIAL) -> str:
        """
        Apply PII masking to text based on the specified level.

        Args:
            text: Text to mask
            masking_level: Level of masking to apply

        Returns:
            Masked text
        """
        if masking_level == MaskingLevel.NONE:
            return text

        masked_text = text

        # Apply all masking rules
        all_rules = {}
        all_rules.update(self.brazilian_rules)
        all_rules.update(self.standard_rules)
        all_rules.update(self.financial_rules)
        all_rules.update(self.context_rules)

        # Sort rules by specificity (more specific patterns first)
        sorted_rules = sorted(all_rules.items(), key=lambda x: len(x[1].pattern), reverse=True)

        for rule_name, rule in sorted_rules:
            if masking_level == MaskingLevel.FULL:
                masked_text = self._apply_full_mask(masked_text, rule)
            elif masking_level == MaskingLevel.HASH:
                masked_text = self._apply_hash_mask(masked_text, rule)
            else:  # PARTIAL
                masked_text = self._apply_partial_mask(masked_text, rule)

        return masked_text

    def _apply_partial_mask(self, text: str, rule: MaskingRule) -> str:
        """Apply partial masking based on rule configuration."""

        def mask_match(match: re.Match) -> str:
            original = match.group()
            if rule.preserve_format:
                return self._mask_preserving_format(original, rule)
            else:
                return self._mask_simple(original, rule)

        return re.sub(rule.pattern, mask_match, text, flags=re.IGNORECASE | re.MULTILINE)

    def _apply_full_mask(self, text: str, rule: MaskingRule) -> str:
        """Apply full masking (complete replacement)."""

        def mask_match(match: re.Match) -> str:
            return rule.mask_char * len(match.group())

        return re.sub(rule.pattern, mask_match, text, flags=re.IGNORECASE | re.MULTILINE)

    def _apply_hash_mask(self, text: str, rule: MaskingRule) -> str:
        """Apply hash masking (irreversible)."""

        def mask_match(match: re.Match) -> str:
            original = match.group()
            return hashlib.sha256(original.encode()).hexdigest()[:len(original)]

        return re.sub(rule.pattern, mask_match, text, flags=re.IGNORECASE | re.MULTILINE)

    def _mask_preserving_format(self, value: str, rule: MaskingRule) -> str:
        """Mask value while preserving original format."""

        if len(value) <= rule.show_first + rule.show_last:
            return rule.mask_char * len(value)

        # Extract non-digit characters for format preservation
        non_digits = [c for c in value if not c.isdigit()]
        digits = [c for c in value if c.isdigit()]

        if len(digits) <= rule.show_first + rule.show_last:
            return rule.mask_char * len(value)

        # Mask digits
        masked_digits = (
            digits[:rule.show_first] +
            [rule.mask_char] * (len(digits) - rule.show_first - rule.show_last) +
            digits[-rule.show_last:]
        )

        # Reconstruct with original format
        result = []
        digit_idx = 0
        for char in value:
            if char.isdigit():
                if digit_idx < len(masked_digits):
                    result.append(masked_digits[digit_idx])
                    digit_idx += 1
                else:
                    result.append(rule.mask_char)
            else:
                result.append(char)

        return ''.join(result)

    def _mask_simple(self, value: str, rule: MaskingRule) -> str:
        """Simple masking without format preservation."""

        if len(value) <= rule.show_first + rule.show_last:
            return rule.mask_char * len(value)

        return (
            value[:rule.show_first] +
            rule.mask_char * (len(value) - rule.show_first - rule.show_last) +
            value[-rule.show_last:]
        )

    def mask_dict(self, data: Dict[str, Any], masking_level: MaskingLevel = MaskingLevel.PARTIAL) -> Dict[str, Any]:
        """
        Recursively mask PII in dictionary values.

        Args:
            data: Dictionary to mask
            masking_level: Level of masking to apply

        Returns:
            Dictionary with masked values
        """
        if not isinstance(data, dict):
            return data

        masked_data = {}

        for key, value in data.items():
            if isinstance(value, str):
                # Check if key suggests sensitive data
                sensitive_keys = ['email', 'cpf', 'rg', 'cnpj', 'phone', 'cep', 'address', 'name']
                if any(sensitive_key in key.lower() for sensitive_key in sensitive_keys):
                    masked_data[key] = self.mask_text(value, masking_level)
                else:
                    masked_data[key] = self.mask_text(value, masking_level)
            elif isinstance(value, dict):
                masked_data[key] = self.mask_dict(value, masking_level)
            elif isinstance(value, list):
                masked_data[key] = [
                    self.mask_dict(item, masking_level) if isinstance(item, dict) else
                    self.mask_text(item, masking_level) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                masked_data[key] = value

        return masked_data

    def mask_log_message(self, message: str, masking_level: MaskingLevel = MaskingLevel.PARTIAL) -> str:
        """
        Mask PII in log messages.

        Args:
            message: Log message to mask
            masking_level: Level of masking to apply

        Returns:
            Masked log message
        """
        return self.mask_text(message, masking_level)

    def create_safe_error_message(self, error: Exception, masking_level: MaskingLevel = MaskingLevel.PARTIAL) -> str:
        """
        Create a safe error message with PII masked.

        Args:
            error: Exception to create message for
            masking_level: Level of masking to apply

        Returns:
            Safe error message with PII masked
        """
        error_message = str(error)
        masked_message = self.mask_text(error_message, masking_level)

        # Add context without revealing sensitive details
        return f"Error occurred: {masked_message}"

    def mask_json_response(self, data: Dict[str, Any], masking_level: MaskingLevel = MaskingLevel.PARTIAL) -> Dict[str, Any]:
        """
        Mask PII in JSON response data.

        Args:
            data: JSON data to mask
            masking_level: Level of masking to apply

        Returns:
            JSON data with PII masked
        """
        return self.mask_dict(data, masking_level)

    def validate_masking(self, original: str, masked: str) -> Dict[str, Any]:
        """
        Validate that masking was applied correctly.

        Args:
            original: Original text
            masked: Masked text

        Returns:
            Validation results
        """
        # Check if PII patterns still exist
        all_rules = {}
        all_rules.update(self.brazilian_rules)
        all_rules.update(self.standard_rules)
        all_rules.update(self.financial_rules)

        validation_results = {
            "is_masked": False,
            "remaining_pii": [],
            "masking_quality": "poor"
        }

        for rule_name, rule in all_rules.items():
            original_matches = re.findall(rule.pattern, original, re.IGNORECASE | re.MULTILINE)
            masked_matches = re.findall(rule.pattern, masked, re.IGNORECASE | re.MULTILINE)

            if original_matches:
                if len(masked_matches) < len(original_matches):
                    validation_results["is_masked"] = True
                    validation_results["masking_quality"] = "good"
                elif len(masked_matches) == len(original_matches):
                    validation_results["remaining_pii"].append(rule_name)

        if not validation_results["remaining_pii"] and validation_results["is_masked"]:
            validation_results["masking_quality"] = "excellent"

        return validation_results


# Global masker instance
pii_masker = PIIMasker()


def mask_text(text: str, masking_level: MaskingLevel = MaskingLevel.PARTIAL) -> str:
    """
    Convenience function to mask PII in text.

    Args:
        text: Text to mask
        masking_level: Level of masking to apply

    Returns:
        Masked text
    """
    return pii_masker.mask_text(text, masking_level)


def mask_log_message(message: str) -> str:
    """
    Convenience function to mask PII in log messages.

    Args:
        message: Log message to mask

    Returns:
        Masked log message
    """
    return pii_masker.mask_log_message(message)


def mask_dict(data: Dict[str, Any], masking_level: MaskingLevel = MaskingLevel.PARTIAL) -> Dict[str, Any]:
    """
    Convenience function to mask PII in dictionary.

    Args:
        data: Dictionary to mask
        masking_level: Level of masking to apply

    Returns:
        Dictionary with masked values
    """
    return pii_masker.mask_dict(data, masking_level)