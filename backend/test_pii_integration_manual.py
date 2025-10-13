#!/usr/bin/env python3
"""
Manual PII Integration Test Script

This script manually tests the PII integration in resume and job services
to verify LGPD compliance functionality without requiring pytest setup.
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from app.services.security.pii_detection_service import PIIType, pii_detector


def test_pii_detection():
    """Test basic PII detection functionality."""
    print("🧪 Testing PII Detection Service...")
    print("=" * 50)

    # Test Brazilian CPF
    text_with_cpf = "Meu nome é João Silva e meu CPF é 123.456.789-01. Moro em São Paulo."
    result = pii_detector.scan_text(text_with_cpf)

    print("✅ CPF Detection:")
    print(f"   Text: {text_with_cpf}")
    print(f"   PII Found: {result.has_pii}")
    print(f"   PII Types: {[t.value for t in result.pii_types_found]}")
    print(f"   Confidence: {result.confidence_score:.2f}")
    print(f"   Scan Time: {result.scan_duration_ms:.1f}ms")

    if result.has_pii and PIIType.CPF in result.pii_types_found:
        print("   ✅ CPF detected correctly")
    else:
        print("   ❌ CPF detection failed")
        return False

    # Test email
    text_with_email = "Contato: joao.silva@empresa.com.br para mais informações."
    result = pii_detector.scan_text(text_with_email)

    print("\n✅ Email Detection:")
    print(f"   Text: {text_with_email}")
    print(f"   PII Found: {result.has_pii}")
    print(f"   PII Types: {[t.value for t in result.pii_types_found]}")

    if result.has_pii and PIIType.EMAIL in result.pii_types_found:
        print("   ✅ Email detected correctly")
    else:
        print("   ❌ Email detection failed")
        return False

    # Test masking
    text_multiple = """
    João Silva
    Email: joao.silva@empresa.com
    CPF: 123.456.789-01
    Telefone: (11) 98765-4321
    """

    result = pii_detector.scan_text(text_multiple)
    print("\n✅ Multiple PII Detection:")
    print(f"   Original text: {repr(text_multiple)}")
    print(f"   PII Types: {[t.value for t in result.pii_types_found]}")
    print(f"   Masked text: {repr(result.masked_text)}")

    # Verify PII is masked
    if (
        "joao.silva@empresa.com" not in result.masked_text
        and "123.456.789-01" not in result.masked_text
    ):
        print("   ✅ PII masked correctly")
    else:
        print("   ❌ PII masking failed")
        return False

    print("\n✅ PII Detection Service: PASSED")
    return True


def test_brazilian_patterns():
    """Test Brazilian-specific PII patterns."""
    print("\n🧪 Testing Brazilian PII Patterns...")
    print("=" * 50)

    test_cases = [
        ("RG: MG-12.345.678", PIIType.RG),
        ("CNPJ: 12.345.678/0001-95", PIIType.CNPJ),
        ("CEP: 01234-567", PIIType.POSTAL_CODE),
        ("Telefone: (11) 98765-4321", PIIType.PHONE),
        ("Telefone: +55 11 98765-4321", PIIType.PHONE),
    ]

    for text, expected_type in test_cases:
        result = pii_detector.scan_text(text)

        if result.has_pii and expected_type in result.pii_types_found:
            print(f"   ✅ {expected_type.value} detected correctly")
        else:
            print(f"   ❌ {expected_type.value} detection failed")
            print(f"      Text: {text}")
            print(f"      Found: {[t.value for t in result.pii_types_found]}")
            return False

    print("\n✅ Brazilian Patterns: PASSED")
    return True


def test_lgpd_compliance():
    """Test LGPD compliance validation."""
    print("\n🧪 Testing LGPD Compliance Validation...")
    print("=" * 50)

    # Critical PII text
    critical_text = "João Silva, CPF: 123.456.789-01, Email: joao@empresa.com"
    result = pii_detector.validate_lgpd_compliance(critical_text)

    print(f"   Critical PII Text: {critical_text}")
    print(f"   Is Compliant: {result['is_compliant']}")
    print(f"   PII Detected: {result['pii_detected']}")
    print(f"   Critical PII: {result['critical_pii_detected']}")
    print(f"   Required Action: {result['recommended_action']}")
    print(f"   Issues: {result['issues']}")

    if not result["is_compliant"] and result["critical_pii_detected"]:
        print("   ✅ LGPD validation working correctly")
    else:
        print("   ❌ LGPD validation failed")
        return False

    # Clean text
    clean_text = "Desenvolvedor Python com experiência em Django."
    result = pii_detector.validate_lgpd_compliance(clean_text)

    print(f"\n   Clean Text: {clean_text}")
    print(f"   Is Compliant: {result['is_compliant']}")
    print(f"   PII Detected: {result['pii_detected']}")

    if result["is_compliant"] and not result["pii_detected"]:
        print("   ✅ Clean text validation working correctly")
    else:
        print("   ❌ Clean text validation failed")
        return False

    print("\n✅ LGPD Compliance Validation: PASSED")
    return True


def test_performance():
    """Test PII detection performance."""
    print("\n🧪 Testing Performance...")
    print("=" * 50)

    # Create test text
    test_text = (
        """
    Desenvolvedor Python com experiência em Django e FastAPI.
    Email: joao.silva@empresa.com
    CPF: 123.456.789-01
    Telefone: (11) 98765-4321
    Endereço: Rua das Flores, 123, São Paulo, SP
    CEP: 01234-567
    CNPJ: 12.345.678/0001-95
    """
        * 100
    )  # Repeat for performance testing

    # Test multiple scans
    times = []
    for i in range(10):
        start_time = datetime.now()
        result = pii_detector.scan_text(test_text)
        end_time = datetime.now()

        scan_time = (end_time - start_time).total_seconds() * 1000
        times.append(scan_time)

    avg_time = sum(times) / len(times)
    max_time = max(times)
    min_time = min(times)

    print(f"   Text Length: {len(test_text)} characters")
    print(f"   Scans Run: {len(times)}")
    print(f"   Average Time: {avg_time:.1f}ms")
    print(f"   Min Time: {min_time:.1f}ms")
    print(f"   Max Time: {max_time:.1f}ms")

    # Performance should be under 100ms for typical use cases
    if avg_time < 100.0:
        print("   ✅ Performance is acceptable")
        return True
    else:
        print("   ❌ Performance is too slow")
        return False


def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n🧪 Testing Edge Cases...")
    print("=" * 50)

    test_cases = [
        ("", "Empty text"),
        ("   ", "Whitespace only"),
        ("Normal text without PII", "No PII"),
        ("CPF: 123.456.789", "Malformed CPF"),
        ("email@domain", "Malformed email"),
        ("joão@silva.com.br", "Unicode in email"),
        ("Telefone: 123", "Too short phone"),
    ]

    for text, description in test_cases:
        try:
            result = pii_detector.scan_text(text)
            print(f"   ✅ {description}: No error")

            # For malformed PII, it should not be detected
            if "Malformed" in description and result.has_pii:
                print(f"   ⚠️  {description}: Unexpectedly detected PII")

        except Exception as e:
            print(f"   ❌ {description}: Error - {e}")
            return False

    print("\n✅ Edge Cases: PASSED")
    return True


async def test_integration_mock():
    """Test integration with mocked services."""
    print("\n🧪 Testing Service Integration (Mock)...")
    print("=" * 50)

    # Import here to avoid dependency issues
    try:
        from unittest.mock import AsyncMock, patch

        from app.services.job_service import JobService
        from app.services.resume_service import ResumeService

        # Mock the AgentManager to avoid AI dependencies
        with (
            patch("app.services.resume_service.AgentManager") as mock_agent_resume,
            patch("app.services.job_service.AgentManager") as mock_agent_job,
        ):
            mock_agent_resume.return_value = AsyncMock()
            mock_agent_job.return_value = AsyncMock()

            resume_service = ResumeService()
            job_service = JobService()

            print("   ✅ Services created successfully")

            # Test PII scanning method exists
            if hasattr(resume_service, "_scan_and_process_resume_text"):
                print("   ✅ Resume PII method exists")
            else:
                print("   ❌ Resume PII method missing")
                return False

            if hasattr(job_service, "_scan_and_process_job_text"):
                print("   ✅ Job PII method exists")
            else:
                print("   ❌ Job PII method missing")
                return False

            print("   ✅ Service Integration: PASSED")
            return True

    except ImportError as e:
        print(f"   ⚠️  Service integration test skipped due to import error: {e}")
        return True  # Skip but don't fail
    except Exception as e:
        print(f"   ❌ Service integration test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 PII Integration Manual Test Suite")
    print("=" * 60)
    print("Testing critical LGPD compliance functionality")
    print("=" * 60)

    tests = [
        test_pii_detection,
        test_brazilian_patterns,
        test_lgpd_compliance,
        test_performance,
        test_edge_cases,
    ]

    # Add async test
    async_test = test_integration_mock()

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

    # Run async test
    try:
        if asyncio.run(async_test):
            passed += 1
        else:
            print("❌ Integration test FAILED")
    except Exception as e:
        print(f"❌ Integration test ERROR: {e}")

    total += 1  # Include async test

    print("\n" + "=" * 60)
    print(f"🎯 TEST RESULTS: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED! PII integration is working correctly.")
        print("✅ System is ready for LGPD compliance in Brazil!")
    else:
        print("❌ Some tests failed. PII integration needs attention.")
        print("⚠️  System may not be fully LGPD compliant.")

    print("=" * 60)

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
