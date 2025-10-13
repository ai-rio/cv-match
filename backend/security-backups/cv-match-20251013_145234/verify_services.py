#!/usr/bin/env python3
"""
Verification script for all backend services.

Tests that all core services can be imported and instantiated.
"""

import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_service_imports():
    """Test that all services can be imported."""
    try:
        logger.info("Testing service imports...")

        # Test resume service
        from app.services.resume_service import ResumeService  # noqa: F401

        logger.info("✅ ResumeService imported successfully")

        # Test job service
        from app.services.job_service import JobService  # noqa: F401

        logger.info("✅ JobService imported successfully")

        # Test text extraction service
        from app.services.text_extraction import (  # noqa: F401
            TextExtractionService,
            extract_text,
        )

        logger.info("✅ text_extraction functions imported successfully")

        return True
    except Exception as e:
        logger.error(f"❌ Service import failed: {e}")
        return False


def test_service_instantiation():
    """Test that all services can be instantiated."""
    try:
        logger.info("Testing service instantiation...")

        # Test ResumeService
        from app.services.resume_service import ResumeService

        resume_service = ResumeService()  # noqa: F841
        logger.info("✅ ResumeService instantiated successfully")

        # Test JobService
        from app.services.job_service import JobService

        job_service = JobService()  # noqa: F841
        logger.info("✅ JobService instantiated successfully")

        # Test TextExtractionService
        from app.services.text_extraction import TextExtractionService

        text_service = TextExtractionService()  # noqa: F841
        logger.info("✅ TextExtractionService instantiated successfully")

        return True
    except Exception as e:
        logger.error(f"❌ Service instantiation failed: {e}")
        return False


def test_service_methods():
    """Test that service methods are callable."""
    try:
        logger.info("Testing service methods...")

        # Test ResumeService methods
        from app.services.resume_service import ResumeService

        resume_service = ResumeService()

        # Check that methods exist
        assert hasattr(resume_service, "convert_and_store_resume")
        assert hasattr(resume_service, "get_resume_with_processed_data")
        logger.info("✅ ResumeService methods available")

        # Test JobService methods
        from app.services.job_service import JobService

        job_service = JobService()

        # Check that methods exist
        assert hasattr(job_service, "create_and_store_job")
        assert hasattr(job_service, "get_job_with_processed_data")
        logger.info("✅ JobService methods available")

        # Test TextExtractionService methods
        from app.services.text_extraction import TextExtractionService

        text_service = TextExtractionService()

        # Check that methods exist
        assert hasattr(text_service, "extract_text")
        assert hasattr(text_service, "extract_text_from_pdf")
        assert hasattr(text_service, "extract_text_from_docx")
        logger.info("✅ TextExtractionService methods available")

        return True
    except Exception as e:
        logger.error(f"❌ Service method test failed: {e}")
        return False


def main():
    """Run all verification tests."""
    logger.info("🚀 Starting backend services verification...")

    tests = [
        ("Service Imports", test_service_imports),
        ("Service Instantiation", test_service_instantiation),
        ("Service Methods", test_service_methods),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        logger.info(f"\n📋 Running {test_name} test...")
        if test_func():
            logger.info(f"✅ {test_name} test PASSED")
            passed += 1
        else:
            logger.error(f"❌ {test_name} test FAILED")

    logger.info(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All tests passed! Backend services are ready.")
        return 0
    else:
        logger.error("💥 Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
