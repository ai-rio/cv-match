"""
Security configuration verification utility.

This module provides utilities to verify that security configurations
are properly set up and working as expected.
"""

import logging
from typing import Any

from fastapi import FastAPI

from app.core.config import settings
from app.services.security.input_sanitizer import default_sanitizer

logger = logging.getLogger(__name__)


class SecurityCheckResult:
    """Result of security configuration check."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.results: list[dict[str, Any]] = []

    def add_result(self, name: str, status: str, message: str, details: dict[str, Any] = None):
        """Add a security check result."""
        self.results.append(
            {
                "name": name,
                "status": status,  # "PASS", "FAIL", "WARN"
                "message": message,
                "details": details or {},
            }
        )

        if status == "PASS":
            self.passed += 1
        elif status == "FAIL":
            self.failed += 1
        else:
            self.warnings += 1

    def get_summary(self) -> dict[str, Any]:
        """Get summary of security check results."""
        return {
            "total_checks": len(self.results),
            "passed": self.passed,
            "failed": self.failed,
            "warnings": self.warnings,
            "overall_status": "PASS" if self.failed == 0 else "FAIL",
        }


class SecurityChecker:
    """Security configuration checker."""

    def __init__(self, app: FastAPI):
        """Initialize security checker."""
        self.app = app
        self.result = SecurityCheckResult()

    def run_all_checks(self) -> SecurityCheckResult:
        """Run all security configuration checks."""
        logger.info("Starting security configuration checks...")

        # Check input validation
        self._check_input_validation()

        # Check rate limiting
        self._check_rate_limiting()

        # Check security headers
        self._check_security_headers()

        # Check file upload security
        self._check_file_upload_security()

        # Check CORS configuration
        self._check_cors_configuration()

        # Check logging configuration
        self._check_logging_configuration()

        # Check environment variables
        self._check_environment_variables()

        # Check middleware configuration
        self._check_middleware_configuration()

        logger.info(f"Security checks completed: {self.result.get_summary()}")
        return self.result

    def _check_input_validation(self):
        """Check input validation configuration."""
        # Check if input sanitizer is configured
        try:
            config = default_sanitizer.config
            self.result.add_result(
                "Input Validation Configuration",
                "PASS",
                "Input sanitizer is properly configured",
                {
                    "max_prompt_length": config.max_prompt_length,
                    "max_text_length": config.max_text_length,
                    "block_system_prompts": config.block_system_prompts,
                    "block_role_instructions": config.block_role_instructions,
                    "block_code_execution": config.block_code_execution,
                },
            )
        except Exception as e:
            self.result.add_result(
                "Input Validation Configuration",
                "FAIL",
                f"Input sanitizer configuration error: {str(e)}",
            )

        # Check Pydantic models
        try:
            from app.models.secure import SecureFileUploadRequest, SecureLoginRequest

            self.result.add_result(
                "Secure Pydantic Models", "PASS", "Secure Pydantic models are available"
            )
        except ImportError as e:
            self.result.add_result(
                "Secure Pydantic Models", "FAIL", f"Secure Pydantic models not available: {str(e)}"
            )

    def _check_rate_limiting(self):
        """Check rate limiting configuration."""
        if settings.ENABLE_RATE_LIMITING:
            self.result.add_result(
                "Rate Limiting",
                "PASS",
                "Rate limiting is enabled",
                {
                    "rate_limit_per_user": settings.RATE_LIMIT_PER_USER,
                    "rate_limit_per_ip": settings.RATE_LIMIT_PER_IP,
                },
            )
        else:
            self.result.add_result("Rate Limiting", "WARN", "Rate limiting is disabled")

    def _check_security_headers(self):
        """Check security headers configuration."""
        required_headers = [
            "X-Frame-Options",
            "X-Content-Type-Options",
            "X-XSS-Protection",
            "Content-Security-Policy",
            "Referrer-Policy",
            "Strict-Transport-Security",
        ]

        # Check if middleware is configured to add security headers
        try:
            # Try to find security middleware in app middleware stack
            has_security_middleware = any(
                isinstance(middleware.cls, type) and "SecurityMiddleware" in str(middleware.cls)
                for middleware in self.app.user_middleware
            )

            if has_security_middleware:
                self.result.add_result(
                    "Security Headers Middleware", "PASS", "Security middleware is configured"
                )
            else:
                self.result.add_result(
                    "Security Headers Middleware", "WARN", "Security middleware not found in stack"
                )
        except Exception as e:
            self.result.add_result(
                "Security Headers Middleware",
                "FAIL",
                f"Error checking security middleware: {str(e)}",
            )

    def _check_file_upload_security(self):
        """Check file upload security configuration."""
        try:
            from app.utils.file_security import FileSecurityConfig, default_validator

            config = default_validator.config

            security_features = {
                "max_file_size": config.max_file_size,
                "scan_for_malware": config.scan_for_malware,
                "validate_content_signature": config.validate_content_signature,
                "check_for_embedded_scripts": config.check_for_embedded_scripts,
                "allowed_mime_types": list(config.allowed_mime_types),
                "allowed_extensions": list(config.allowed_extensions),
            }

            self.result.add_result(
                "File Upload Security",
                "PASS",
                "File upload security is configured",
                security_features,
            )
        except ImportError as e:
            self.result.add_result(
                "File Upload Security", "FAIL", f"File security utilities not available: {str(e)}"
            )
        except Exception as e:
            self.result.add_result(
                "File Upload Security", "FAIL", f"File security configuration error: {str(e)}"
            )

    def _check_cors_configuration(self):
        """Check CORS configuration."""
        try:
            # Check CORS middleware configuration
            cors_configured = False
            allowed_origins = []

            for middleware in self.app.user_middleware:
                if "CORSMiddleware" in str(middleware.cls):
                    cors_configured = True
                    # Try to extract CORS configuration
                    if hasattr(middleware, "kwargs"):
                        options = middleware.kwargs
                        allowed_origins = options.get("allow_origins", [])
                    break

            if cors_configured:
                self.result.add_result(
                    "CORS Configuration",
                    "PASS",
                    "CORS middleware is configured",
                    {"allowed_origins": allowed_origins},
                )
            else:
                self.result.add_result("CORS Configuration", "WARN", "CORS middleware not found")
        except Exception as e:
            self.result.add_result(
                "CORS Configuration", "FAIL", f"Error checking CORS configuration: {str(e)}"
            )

    def _check_logging_configuration(self):
        """Check logging configuration."""
        if settings.ENABLE_SECURITY_LOGGING:
            self.result.add_result(
                "Security Logging",
                "PASS",
                "Security logging is enabled",
                {"log_level": settings.SECURITY_LOG_LEVEL},
            )
        else:
            self.result.add_result("Security Logging", "WARN", "Security logging is disabled")

    def _check_environment_variables(self):
        """Check security-related environment variables."""
        security_env_vars = {
            "ENABLE_RATE_LIMITING": settings.ENABLE_RATE_LIMITING,
            "ENABLE_SECURITY_LOGGING": settings.ENABLE_SECURITY_LOGGING,
            "MAX_PROMPT_LENGTH": settings.MAX_PROMPT_LENGTH,
            "MAX_TEXT_LENGTH": settings.MAX_TEXT_LENGTH,
            "BLOCK_SYSTEM_PROMPTS": settings.BLOCK_SYSTEM_PROMPTS,
            "BLOCK_ROLE_INSTRUCTIONS": settings.BLOCK_ROLE_INSTRUCTIONS,
            "BLOCK_CODE_EXECUTION": settings.BLOCK_CODE_EXECUTION,
        }

        # Check for sensitive environment variables that should be set
        sensitive_vars = ["SUPABASE_SERVICE_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
        sensitive_config = {}

        for var in sensitive_vars:
            value = getattr(settings, var, None)
            sensitive_config[var] = "SET" if value else "NOT_SET"

        self.result.add_result(
            "Environment Variables",
            "PASS" if all(security_env_vars.values()) else "WARN",
            "Security environment variables checked",
            {**security_env_vars, **sensitive_config},
        )

    def _check_middleware_configuration(self):
        """Check overall middleware configuration."""
        middleware_count = len(self.app.user_middleware)
        middleware_types = []

        for middleware in self.app.user_middleware:
            middleware_types.append(str(middleware.cls))

        security_middleware_count = sum(
            1 for mtype in middleware_types if "Security" in mtype or "security" in mtype.lower()
        )

        self.result.add_result(
            "Middleware Configuration",
            "PASS" if security_middleware_count > 0 else "WARN",
            f"Found {security_middleware_count} security-related middleware out of {middleware_count} total",
            {
                "total_middleware": middleware_count,
                "security_middleware": security_middleware_count,
                "middleware_types": middleware_types,
            },
        )


def run_security_checks(app: FastAPI) -> dict[str, Any]:
    """
    Run comprehensive security configuration checks.

    Args:
        app: FastAPI application instance

    Returns:
        Dictionary with security check results
    """
    checker = SecurityChecker(app)
    result = checker.run_all_checks()

    return {
        "timestamp": logger.info("Security checks completed"),
        "summary": result.get_summary(),
        "detailed_results": result.results,
        "recommendations": _generate_recommendations(result),
    }


def _generate_recommendations(result: SecurityCheckResult) -> list[str]:
    """Generate security recommendations based on check results."""
    recommendations = []

    for check_result in result.results:
        if check_result["status"] == "FAIL":
            if "Input Validation" in check_result["name"]:
                recommendations.append(
                    "Implement proper input validation and sanitization for all user inputs"
                )
            elif "File Upload" in check_result["name"]:
                recommendations.append(
                    "Configure comprehensive file upload security with malware scanning"
                )
            elif "Rate Limiting" in check_result["name"]:
                recommendations.append("Enable rate limiting to prevent abuse and DoS attacks")
            elif "Security Headers" in check_result["name"]:
                recommendations.append(
                    "Configure security headers to prevent XSS, clickjacking, and other attacks"
                )
            elif "CORS" in check_result["name"]:
                recommendations.append("Configure CORS to restrict cross-origin requests")
            elif "Logging" in check_result["name"]:
                recommendations.append("Enable security logging to monitor and detect attacks")

        elif check_result["status"] == "WARN":
            if "Rate Limiting" in check_result["name"]:
                recommendations.append(
                    "Consider enabling rate limiting for production environments"
                )
            elif "Logging" in check_result["name"]:
                recommendations.append("Consider enabling security logging for better monitoring")

    # Add general recommendations
    if not recommendations:
        recommendations.append(
            "Security configuration looks good! Consider regular security audits"
        )

    # Add production recommendations
    recommendations.extend(
        [
            "Regularly update dependencies and security patches",
            "Implement automated security testing in CI/CD pipeline",
            "Monitor security logs for suspicious activity",
            "Conduct regular security assessments and penetration testing",
        ]
    )

    return recommendations


def print_security_report(check_results: dict[str, Any]):
    """Print a formatted security report."""
    print("\n" + "=" * 60)
    print("CV-MATCH SECURITY CONFIGURATION REPORT")
    print("=" * 60)

    summary = check_results["summary"]
    print("\nSUMMARY:")
    print(f"  Total Checks: {summary['total_checks']}")
    print(f"  Passed: {summary['passed']}")
    print(f"  Failed: {summary['failed']}")
    print(f"  Warnings: {summary['warnings']}")
    print(f"  Overall Status: {summary['overall_status']}")

    print("\nDETAILED RESULTS:")
    for result in check_results["detailed_results"]:
        status_symbol = {"PASS": "✓", "FAIL": "✗", "WARN": "⚠"}.get(result["status"], "?")

        print(f"  {status_symbol} {result['name']}: {result['message']}")
        if result["details"]:
            for key, value in result["details"].items():
                print(f"    - {key}: {value}")

    print("\nRECOMMENDATIONS:")
    for i, rec in enumerate(check_results["recommendations"], 1):
        print(f"  {i}. {rec}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    from app.main import app

    results = run_security_checks(app)
    print_security_report(results)
