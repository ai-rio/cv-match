"""
PII Detection Service for Brazilian LGPD Compliance

This service provides comprehensive detection of Personally Identifiable Information (PII)
with specific patterns for Brazilian data (CPF, RG, etc.) and implements real-time
scanning and masking capabilities for LGPD compliance.

Critical for CV-Match Brazilian market deployment - PII exposure is illegal under LGPD.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class PIIType(Enum):
    """Types of PII that can be detected."""

    # Brazilian specific PII
    CPF = "cpf"  # Cadastro de Pessoas Físicas (Brazilian tax ID)
    RG = "rg"    # Registro Geral (Brazilian ID)
    CNPJ = "cnpj"  # Cadastro Nacional da Pessoa Jurídica

    # Standard PII
    EMAIL = "email"
    PHONE = "phone"
    PASSPORT = "passport"
    DRIVER_LICENSE = "driver_license"

    # Financial
    CREDIT_CARD = "credit_card"
    BANK_ACCOUNT = "bank_account"

    # Location
    ADDRESS = "address"
    POSTAL_CODE = "postal_code"

    # Identifiers
    SOCIAL_SECURITY = "social_security"
    PASSPORT_NUMBER = "passport_number"


@dataclass
class PIIPattern:
    """Pattern definition for PII detection."""

    regex: str
    description: str
    confidence: float  # 0.0 to 1.0
    examples: List[str]
    masking_strategy: str = "partial"


class PIIDetectionResult(BaseModel):
    """Result of PII detection."""

    has_pii: bool
    pii_types_found: List[PIIType] = Field(default_factory=list)
    detected_instances: Dict[PIIType, List[Dict[str, Any]]] = Field(default_factory=dict)
    confidence_score: float = 0.0
    masked_text: Optional[str] = None
    scan_duration_ms: Optional[float] = None


class PIIMaskingStrategy:
    """Strategies for masking detected PII."""

    @staticmethod
    def partial_mask(value: str, mask_char: str = "*", show_first: int = 2, show_last: int = 2) -> str:
        """Partially mask a value showing only first and last characters."""
        if len(value) <= show_first + show_last:
            return mask_char * len(value)

        return (
            value[:show_first] +
            mask_char * (len(value) - show_first - show_last) +
            value[-show_last:]
        )

    @staticmethod
    def full_mask(value: str, mask_char: str = "*") -> str:
        """Completely mask a value."""
        return mask_char * len(value)

    @staticmethod
    def email_mask(email: str) -> str:
        """Mask email address while preserving domain structure."""
        if "@" not in email:
            return email

        local, domain = email.split("@", 1)
        if len(local) <= 2:
            masked_local = "*" * len(local)
        else:
            masked_local = local[0] + "*" * (len(local) - 2) + local[-1]

        return f"{masked_local}@{domain}"

    @staticmethod
    def phone_mask(phone: str) -> str:
        """Mask phone number while preserving format."""
        # Remove non-numeric characters
        digits = re.sub(r'\D', '', phone)
        if len(digits) <= 4:
            return "*" * len(phone)

        # Keep first 2 and last 2 digits
        return (
            phone[:2] +
            "*" * (len(phone) - 4) +
            phone[-2:]
        )


class PIIDetectionService:
    """Service for detecting and masking PII in text data."""

    def __init__(self):
        """Initialize PII detection service with Brazilian patterns."""
        self._init_brazilian_patterns()
        self._init_standard_patterns()
        self._init_financial_patterns()
        self._init_location_patterns()
        self.masking_strategy = PIIMaskingStrategy()

    def _init_brazilian_patterns(self) -> None:
        """Initialize Brazilian-specific PII patterns."""

        # CPF Pattern: XXX.XXX.XXX-XX or XXXXXXXXXXX
        self.brazilian_patterns = {
            PIIType.CPF: PIIPattern(
                regex=r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b',
                description="Brazilian CPF (Cadastro de Pessoas Físicas)",
                confidence=0.95,
                examples=["123.456.789-01", "12345678901", "111.222.333-44"],
                masking_strategy="partial"
            ),

            # RG Pattern: XX.XXX.XXX-X or XXXXXXXXXX
            PIIType.RG: PIIPattern(
                regex=r'\b\d{1,2}\.?\d{3}\.?\d{3}-?[A-Z0-9]?\b',
                description="Brazilian RG (Registro Geral)",
                confidence=0.85,
                examples=["12.345.678-9", "123456789", "MG-12.345.678"],
                masking_strategy="partial"
            ),

            # CNPJ Pattern: XX.XXX.XXX/XXXX-XX or XXXXXXXXXXXXXX
            PIIType.CNPJ: PIIPattern(
                regex=r'\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b',
                description="Brazilian CNPJ (Cadastro Nacional da Pessoa Jurídica)",
                confidence=0.95,
                examples=["12.345.678/0001-95", "12345678000195"],
                masking_strategy="partial"
            ),
        }

    def _init_standard_patterns(self) -> None:
        """Initialize standard PII patterns."""

        self.standard_patterns = {
            PIIType.EMAIL: PIIPattern(
                regex=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
                description="Email address",
                confidence=0.98,
                examples=["user@example.com", "joao.silva@empresa.com.br"],
                masking_strategy="email"
            ),

            PIIType.PHONE: PIIPattern(
                regex=r'\b(?:\+?55\s?)?(?:\(?\d{2}\)?[-\s]?)?\d{4,5}[-\s]?\d{4}\b',
                description="Phone number (Brazilian format)",
                confidence=0.90,
                examples=["+55 11 98765-4321", "(11) 98765-4321", "11987654321"],
                masking_strategy="phone"
            ),

            PIIType.PASSPORT: PIIPattern(
                regex=r'\b[A-Z]{2}\d{7}\b',
                description="Passport number",
                confidence=0.75,
                examples=["AB1234567", "CD9876543"],
                masking_strategy="partial"
            ),
        }

    def _init_financial_patterns(self) -> None:
        """Initialize financial PII patterns."""

        self.financial_patterns = {
            PIIType.CREDIT_CARD: PIIPattern(
                regex=r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
                description="Credit card number",
                confidence=0.95,
                examples=["4111 1111 1111 1111", "4111-1111-1111-1111", "4111111111111111"],
                masking_strategy="partial"
            ),

            PIIType.BANK_ACCOUNT: PIIPattern(
                regex=r'\b(?:\d{6,7}-?\d{1,2}-?\d{1,6})\b',
                description="Brazilian bank account",
                confidence=0.80,
                examples=["12345-6", "123456-7", "12345-6-X"],
                masking_strategy="partial"
            ),
        }

    def _init_location_patterns(self) -> None:
        """Initialize location-based PII patterns."""

        self.location_patterns = {
            PIIType.POSTAL_CODE: PIIPattern(
                regex=r'\b\d{5}-?\d{3}\b',
                description="Brazilian CEP (Código de Endereçamento Postal)",
                confidence=0.90,
                examples=["01310-100", "01310100"],
                masking_strategy="partial"
            ),

            PIIType.ADDRESS: PIIPattern(
                regex=r'\b(?:Rua|Avenida|Alameda|Travessa|Praia|Praça)\s+[^,]+,\s*\d+[^,]*',
                description="Street address",
                confidence=0.70,
                examples=["Rua das Flores, 123", "Avenida Paulista, 1000"],
                masking_strategy="partial"
            ),
        }

    def _get_all_patterns(self) -> Dict[PIIType, PIIPattern]:
        """Get all PII patterns."""
        patterns = {}
        patterns.update(self.brazilian_patterns)
        patterns.update(self.standard_patterns)
        patterns.update(self.financial_patterns)
        patterns.update(self.location_patterns)
        return patterns

    def scan_text(self, text: str) -> PIIDetectionResult:
        """
        Scan text for PII and return detection results.

        Args:
            text: Text to scan for PII

        Returns:
            PIIDetectionResult with detected PII information
        """
        import time
        start_time = time.time()

        patterns = self._get_all_patterns()
        detected_instances: Dict[PIIType, List[Dict[str, Any]]] = {}
        pii_types_found: List[PIIType] = []

        for pii_type, pattern in patterns.items():
            matches = re.finditer(pattern.regex, text, re.IGNORECASE | re.MULTILINE)

            if matches:
                instances = []
                for match in matches:
                    instance = {
                        "value": match.group(),
                        "start": match.start(),
                        "end": match.end(),
                        "confidence": pattern.confidence,
                        "description": pattern.description
                    }
                    instances.append(instance)

                if instances:
                    detected_instances[pii_type] = instances
                    pii_types_found.append(pii_type)

        # Calculate overall confidence score
        confidence_score = self._calculate_confidence_score(detected_instances)

        # Generate masked text
        masked_text = self.mask_text(text, detected_instances) if detected_instances else text

        scan_duration = (time.time() - start_time) * 1000  # Convert to milliseconds

        return PIIDetectionResult(
            has_pii=bool(detected_instances),
            pii_types_found=pii_types_found,
            detected_instances=detected_instances,
            confidence_score=confidence_score,
            masked_text=masked_text,
            scan_duration_ms=scan_duration
        )

    def mask_text(self, text: str, detected_instances: Optional[Dict[PIIType, List[Dict[str, Any]]]] = None) -> str:
        """
        Apply masking to detected PII in text.

        Args:
            text: Text to mask
            detected_instances: Pre-detected PII instances (optional)

        Returns:
            Text with PII masked
        """
        if detected_instances is None:
            # Scan for PII if not provided
            result = self.scan_text(text)
            detected_instances = result.detected_instances

        masked_text = text

        # Sort instances by start position in reverse order to avoid offset issues
        all_instances = []
        for pii_type, instances in detected_instances.items():
            for instance in instances:
                all_instances.append((pii_type, instance))

        all_instances.sort(key=lambda x: x[1]["end"], reverse=True)

        for pii_type, instance in all_instances:
            start = instance["start"]
            end = instance["end"]
            original_value = instance["value"]

            # Apply appropriate masking strategy
            masked_value = self._apply_masking_strategy(pii_type, original_value)

            # Replace in text
            masked_text = masked_text[:start] + masked_value + masked_text[end:]

        return masked_text

    def _apply_masking_strategy(self, pii_type: PIIType, value: str) -> str:
        """Apply the appropriate masking strategy for a PII type."""

        if pii_type == PIIType.EMAIL:
            return self.masking_strategy.email_mask(value)
        elif pii_type == PIIType.PHONE:
            return self.masking_strategy.phone_mask(value)
        elif pii_type in [PIIType.CPF, PIIType.RG, PIIType.CNPJ, PIIType.CREDIT_CARD]:
            return self.masking_strategy.partial_mask(value, show_first=2, show_last=2)
        elif pii_type == PIIType.POSTAL_CODE:
            return self.masking_strategy.partial_mask(value, show_first=2, show_last=1)
        else:
            return self.masking_strategy.partial_mask(value, show_first=1, show_last=1)

    def _calculate_confidence_score(self, detected_instances: Dict[PIIType, List[Dict[str, Any]]]) -> float:
        """Calculate overall confidence score for detected PII."""
        if not detected_instances:
            return 0.0

        total_confidence = 0.0
        total_instances = 0

        for instances in detected_instances.values():
            for instance in instances:
                total_confidence += instance["confidence"]
                total_instances += 1

        return min(total_confidence / total_instances, 1.0) if total_instances > 0 else 0.0

    def get_pii_summary(self, text: str) -> Dict[str, Any]:
        """
        Get a summary of PII detected in text.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with PII summary information
        """
        result = self.scan_text(text)

        summary = {
            "has_pii": result.has_pii,
            "total_pii_types": len(result.pii_types_found),
            "pii_types": [pii_type.value for pii_type in result.pii_types_found],
            "total_instances": sum(len(instances) for instances in result.detected_instances.values()),
            "confidence_score": result.confidence_score,
            "scan_duration_ms": result.scan_duration_ms,
            "lgpd_compliant": not result.has_pii or result.confidence_score < 0.8
        }

        # Add breakdown by type
        for pii_type, instances in result.detected_instances.items():
            summary[f"{pii_type.value}_count"] = len(instances)

        return summary

    def validate_lgpd_compliance(self, text: str) -> Dict[str, Any]:
        """
        Validate if text complies with LGPD requirements.

        Args:
            text: Text to validate

        Returns:
            Dictionary with LGPD compliance results
        """
        result = self.scan_text(text)

        # LGPD compliance rules
        critical_pii_types = [PIIType.CPF, PIIType.RG, PIIType.EMAIL]
        has_critical_pii = any(pii_type in result.pii_types_found for pii_type in critical_pii_types)

        compliance_issues = []
        if has_critical_pii:
            compliance_issues.append("Critical PII detected (CPF/RG/Email)")

        if result.confidence_score > 0.8:
            compliance_issues.append("High confidence PII detection")

        return {
            "is_compliant": not compliance_issues,
            "compliance_score": 1.0 - result.confidence_score,
            "issues": compliance_issues,
            "requires_masking": result.has_pii,
            "recommended_action": "mask_pii" if result.has_pii else "proceed",
            "pii_detected": result.has_pii,
            "critical_pii_detected": has_critical_pii
        }


# Global PII detection service instance
pii_detector = PIIDetectionService()


def scan_for_pii(text: str) -> PIIDetectionResult:
    """
    Convenience function to scan text for PII.

    Args:
        text: Text to scan

    Returns:
        PIIDetectionResult with detection results
    """
    return pii_detector.scan_text(text)


def mask_pii(text: str) -> str:
    """
    Convenience function to mask PII in text.

    Args:
        text: Text to mask

    Returns:
        Text with PII masked
    """
    return pii_detector.mask_text(text)


def validate_lgpd_compliance(text: str) -> Dict[str, Any]:
    """
    Convenience function to validate LGPD compliance.

    Args:
        text: Text to validate

    Returns:
        LGPD compliance results
    """
    return pii_detector.validate_lgpd_compliance(text)