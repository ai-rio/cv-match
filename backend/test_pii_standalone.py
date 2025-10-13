#!/usr/bin/env python3
"""
Standalone PII Detection Test

Tests PII detection functionality independently to verify LGPD compliance.
This test doesn't require the full application stack.
"""

import re
import sys
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any


class PIIType(Enum):
    """Types of PII that can be detected."""

    CPF = "cpf"
    RG = "rg"
    CNPJ = "cnpj"
    EMAIL = "email"
    PHONE = "phone"
    POSTAL_CODE = "postal_code"
    ADDRESS = "address"


@dataclass
class PIIPattern:
    """Pattern definition for PII detection."""

    regex: str
    description: str
    confidence: float


@dataclass
class PIIDetectionResult:
    """Result of PII detection."""

    has_pii: bool
    pii_types_found: list[PIIType]
    detected_instances: dict[PIIType, list[dict[str, Any]]]
    confidence_score: float
    masked_text: str
    scan_duration_ms: float


class SimplePIIDetector:
    """Simple PII detection for testing."""

    def __init__(self):
        self.patterns = {
            PIIType.CPF: PIIPattern(
                regex=r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b",
                description="Brazilian CPF",
                confidence=0.95,
            ),
            PIIType.EMAIL: PIIPattern(
                regex=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
                description="Email address",
                confidence=0.98,
            ),
            PIIType.PHONE: PIIPattern(
                regex=r"\b(?:\+?55\s?)?(?:\(?\d{2}\)?[-\s]?)?\d{4,5}[-\s]?\d{4}\b",
                description="Brazilian phone",
                confidence=0.90,
            ),
            PIIType.CNPJ: PIIPattern(
                regex=r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b",
                description="Brazilian CNPJ",
                confidence=0.95,
            ),
            PIIType.POSTAL_CODE: PIIPattern(
                regex=r"\b\d{5}-?\d{3}\b", description="Brazilian CEP", confidence=0.90
            ),
        }

    def scan_text(self, text: str) -> PIIDetectionResult:
        """Scan text for PII."""
        start_time = time.time()

        detected_instances = {}
        pii_types_found = []

        for pii_type, pattern in self.patterns.items():
            matches = re.finditer(pattern.regex, text, re.IGNORECASE)
            instances = []

            for match in matches:
                instances.append(
                    {
                        "value": match.group(),
                        "start": match.start(),
                        "end": match.end(),
                        "confidence": pattern.confidence,
                    }
                )

            if instances:
                detected_instances[pii_type] = instances
                pii_types_found.append(pii_type)

        # Calculate confidence
        total_confidence = 0.0
        total_instances = 0
        for instances in detected_instances.values():
            for instance in instances:
                total_confidence += instance["confidence"]
                total_instances += 1

        confidence_score = total_confidence / total_instances if total_instances > 0 else 0.0

        # Apply masking
        masked_text = self.mask_text(text, detected_instances)

        scan_duration = (time.time() - start_time) * 1000

        return PIIDetectionResult(
            has_pii=bool(detected_instances),
            pii_types_found=pii_types_found,
            detected_instances=detected_instances,
            confidence_score=confidence_score,
            masked_text=masked_text,
            scan_duration_ms=scan_duration,
        )

    def mask_text(self, text: str, detected_instances: dict[PIIType, list[dict[str, Any]]]) -> str:
        """Apply masking to detected PII."""
        masked_text = text

        # Sort instances by end position in reverse to avoid offset issues
        all_instances = []
        for pii_type, instances in detected_instances.items():
            for instance in instances:
                all_instances.append((pii_type, instance))

        all_instances.sort(key=lambda x: x[1]["end"], reverse=True)

        for pii_type, instance in all_instances:
            start = instance["start"]
            end = instance["end"]
            original_value = instance["value"]

            # Apply masking based on type
            if pii_type == PIIType.EMAIL:
                if "@" in original_value:
                    local, domain = original_value.split("@", 1)
                    if len(local) > 2:
                        masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
                        masked_value = f"{masked_local}@{domain}"
                    else:
                        masked_value = "*" * len(original_value)
                else:
                    masked_value = "*" * len(original_value)
            elif pii_type == PIIType.PHONE:
                masked_value = (
                    original_value[:2] + "*" * (len(original_value) - 4) + original_value[-2:]
                )
            else:
                # Partial masking for other types
                if len(original_value) > 4:
                    masked_value = (
                        original_value[:2] + "*" * (len(original_value) - 4) + original_value[-2:]
                    )
                else:
                    masked_value = "*" * len(original_value)

            # Replace in text
            masked_text = masked_text[:start] + masked_value + masked_text[end:]

        return masked_text


def test_brazilian_pii():
    """Test Brazilian PII detection."""
    print("🧪 Testing Brazilian PII Detection")
    print("=" * 50)

    detector = SimplePIIDetector()

    test_cases = [
        ("CPF: 123.456.789-01", [PIIType.CPF]),
        ("Email: joao.silva@empresa.com.br", [PIIType.EMAIL]),
        ("Telefone: (11) 98765-4321", [PIIType.PHONE]),
        ("CNPJ: 12.345.678/0001-95", [PIIType.CNPJ]),
        ("CEP: 01234-567", [PIIType.POSTAL_CODE]),
        ("RG: MG-12.345.678", [PIIType.RG]),  # This won't be detected by simple patterns
    ]

    passed = 0
    total = len(test_cases)

    for text, expected_types in test_cases:
        result = detector.scan_text(text)

        print(f"\nTest: {text}")
        print(f"  Expected: {[t.value for t in expected_types]}")
        print(f"  Detected: {[t.value for t in result.pii_types_found]}")
        print(f"  Confidence: {result.confidence_score:.2f}")
        print(f"  Masked: {result.masked_text}")

        # Check if expected types are detected
        detected = set(result.pii_types_found)
        expected = set(expected_types)

        if expected.issubset(detected):
            print("  ✅ PASSED")
            passed += 1
        else:
            print(f"  ❌ FAILED - Missing: {[t.value for t in expected - detected]}")

    print(f"\nBrazilian PII Tests: {passed}/{total} passed")
    return passed == total


def test_comprehensive_text():
    """Test comprehensive text with multiple PII types."""
    print("\n🧪 Testing Comprehensive PII Detection")
    print("=" * 50)

    detector = SimplePIIDetector()

    comprehensive_text = """
    João Silva
    Email: joao.silva@empresa.com.br
    CPF: 123.456.789-01
    Telefone: (11) 98765-4321
    Empresa Tech Solutions Brasil
    CNPJ: 12.345.678/0001-95
    Endereço: Rua das Flores, 123, São Paulo, SP
    CEP: 01234-567
    Contato: maria@techsolutions.com
    """

    result = detector.scan_text(comprehensive_text)

    print(f"Original text length: {len(comprehensive_text)}")
    print(f"PII Types Found: {[t.value for t in result.pii_types_found]}")
    print(
        f"Total PII Instances: {sum(len(instances) for instances in result.detected_instances.values())}"
    )
    print(f"Confidence Score: {result.confidence_score:.2f}")
    print(f"Scan Duration: {result.scan_duration_ms:.1f}ms")
    print(f"Masked text length: {len(result.masked_text)}")

    print("\nOriginal Text Sample:")
    print(f"  {comprehensive_text[:200]}...")

    print("\nMasked Text Sample:")
    print(f"  {result.masked_text[:200]}...")

    # Verify PII is actually masked
    original_pii = ["joao.silva@empresa.com.br", "123.456.789-01", "(11) 98765-4321"]
    masked_correctly = True

    for pii in original_pii:
        if pii in result.masked_text:
            print(f"\n❌ PII not masked: {pii}")
            masked_correctly = False
        else:
            print(f"✅ PII masked: {pii}")

    if masked_correctly and len(result.pii_types_found) >= 4:  # Should detect at least 4 types
        print("\n✅ Comprehensive Test PASSED")
        return True
    else:
        print("\n❌ Comprehensive Test FAILED")
        return False


def test_performance():
    """Test PII detection performance."""
    print("\n🧪 Testing Performance")
    print("=" * 50)

    detector = SimplePIIDetector()

    # Create large text with PII
    base_text = """
    Desenvolvedor Python com experiência em Django.
    Entre em contato: desenvolvedor@empresa.com
    CPF: 987.654.321-00 para verificação.
    """

    large_text = base_text * 1000  # Repeat 1000 times

    print(f"Text length: {len(large_text)} characters")

    # Run multiple tests
    times = []
    for i in range(10):
        result = detector.scan_text(large_text)
        times.append(result.scan_duration_ms)

    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    print(f"Average scan time: {avg_time:.1f}ms")
    print(f"Min scan time: {min_time:.1f}ms")
    print(f"Max scan time: {max_time:.1f}ms")
    print(f"PII detected: {result.has_pii}")
    print(f"PII types: {[t.value for t in result.pii_types_found]}")

    # Performance should be reasonable
    if avg_time < 100.0:  # Under 100ms
        print("✅ Performance Test PASSED")
        return True
    else:
        print("❌ Performance Test FAILED - Too slow")
        return False


def test_edge_cases():
    """Test edge cases."""
    print("\n🧪 Testing Edge Cases")
    print("=" * 50)

    detector = SimplePIIDetector()

    test_cases = [
        ("", "Empty text"),
        ("   ", "Whitespace only"),
        ("Normal text without PII", "No PII"),
        ("CPF: 123.456.789", "Malformed CPF"),
        ("email@domain", "Malformed email"),
        ("Telefone: 123", "Too short phone"),
        ("123.456.789-01", "Just CPF"),
        ("joão@silva.com.br", "Unicode email"),
    ]

    passed = 0
    total = len(test_cases)

    for text, description in test_cases:
        try:
            result = detector.scan_text(text)
            print(f"  {description}: ✅ No error")

            # Check if malformed PII is not detected
            if "Malformed" in description and result.has_pii:
                print("    ⚠️  Unexpectedly detected PII")
            elif description == "Empty text" and result.has_pii:
                print("    ⚠️  PII detected in empty text")

            passed += 1

        except Exception as e:
            print(f"  {description}: ❌ Error - {e}")

    print(f"\nEdge Cases: {passed}/{total} passed")
    return passed == total


def main():
    """Run all tests."""
    print("🚀 Standalone PII Detection Test Suite")
    print("=" * 60)
    print("Testing LGPD compliance for Brazilian market")
    print("=" * 60)

    tests = [
        test_brazilian_pii,
        test_comprehensive_text,
        test_performance,
        test_edge_cases,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ {test.__name__} FAILED")
        except Exception as e:
            print(f"❌ {test.__name__} ERROR: {e}")

    print("\n" + "=" * 60)
    print(f"🎯 FINAL RESULTS: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("✅ PII detection is working correctly!")
        print("✅ System is ready for LGPD compliance!")
    else:
        print("❌ Some tests failed.")
        print("⚠️  Review PII detection implementation.")

    print("=" * 60)
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
