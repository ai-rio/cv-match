"""
End-to-end integration tests for CV-Match API endpoints.

This script tests the complete optimization workflow including:
- Health checks
- Resume upload
- Optimization start/retrieval/list
- Error handling
"""

import asyncio
import httpx
import json
import base64
from typing import Dict, Any, Optional

# Test configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

# Sample test data
SAMPLE_RESUME_TEXT = """
JOÃO SILVA
São Paulo, SP | (11) 99999-9999 | joao.silva@email.com | linkedin.com/in/joaosilva

RESUMO PROFISSIONAL
Desenvolvedor Python com 5 anos de experiência em desenvolvimento de aplicações web
e análise de dados. Especializado em Django, FastAPI e ciência de dados.

EXPERIÊNCIA PROFISSIONAL
Desenvolvedor Python Senior | Tech Corp | 2021-Presente
- Desenvolvimento de APIs REST com FastAPI e Django
- Implementação de pipelines de dados com Apache Airflow
- Mentoria para equipe júnior

Desenvolvedor Python | StartupXYZ | 2019-2021
- Desenvolvimento de aplicações web com Django
- Análise de dados com Pandas e NumPy
- Integração com bancos de dados PostgreSQL e MongoDB

EDUCAÇÃO
Bacharel em Ciência da Computação | USP | 2015-2019

HABILIDADES TÉCNICAS
- Linguagens: Python, JavaScript, SQL
- Frameworks: Django, FastAPI, React
- Banco de Dados: PostgreSQL, MongoDB, Redis
- Ferramentas: Docker, Git, AWS
"""

SAMPLE_JOB_DESCRIPTION = """
Vaga: Desenvolvedor Python Pleno
Empresa: Tech Innovations SA
Local: São Paulo, SP (Remoto/Híbrido)

Descrição:
Buscamos um Desenvolvedor Python Pleno para juntar-se à nossa equipe de tecnologia.
O candidato ideal terá experiência sólida em desenvolvimento de aplicações web
e APIs REST usando frameworks modernos.

Requisitos:
- 3+ anos de experiência em desenvolvimento Python
- Experiência com FastAPI ou Django
- Conhecimento em bancos de dados SQL (PostgreSQL preferencialmente)
- Experiência com Docker e contêineres
- Inglês intermediário

Desejável:
- Experiência com microserviços
- Conhecimento em Cloud (AWS/GCP)
- Experiência com testes automatizados

Benefícios:
- Salário competitivo
- Plano de saúde e odontológico
- Auxílio home office
- Horário flexível
- Oportunidades de crescimento
"""


class CVMatchAPITester:
    """End-to-end tester for CV-Match API endpoints."""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.auth_token: Optional[str] = None
        self.test_results = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        message = f"{status} - {test_name}"
        if details:
            message += f": {details}"
        print(message)
        self.test_results.append({"test": test_name, "passed": passed, "details": details})

    async def test_health_check(self):
        """Test health check endpoint."""
        try:
            response = await self.client.get(f"{BASE_URL}/health")
            success = response.status_code == 200
            details = response.json() if success else f"Status: {response.status_code}"
            self.log_test("Health Check", success, json.dumps(details))
            return success
        except Exception as e:
            self.log_test("Health Check", False, str(e))
            return False

    async def test_security_health(self):
        """Test security health check endpoint."""
        try:
            response = await self.client.get(f"{BASE_URL}/health/security")
            success = response.status_code == 200
            details = "Security configuration loaded" if success else f"Status: {response.status_code}"
            self.log_test("Security Health Check", success, details)
            return success
        except Exception as e:
            self.log_test("Security Health Check", False, str(e))
            return False

    async def test_resume_upload_no_auth(self):
        """Test resume upload without authentication (should fail)."""
        try:
            # Create a dummy file content
            file_content = SAMPLE_RESUME_TEXT.encode('utf-8')
            files = {'file': ('test_resume.txt', file_content, 'text/plain')}

            response = await self.client.post(
                f"{API_BASE}/resumes/upload",
                files=files
            )

            # Should return 401 (unauthorized) or 403 (forbidden)
            success = response.status_code in [401, 403]
            details = f"Correctly rejected with status {response.status_code}"
            self.log_test("Resume Upload (No Auth)", success, details)
            return success
        except Exception as e:
            self.log_test("Resume Upload (No Auth)", False, str(e))
            return False

    async def test_optimization_start_no_auth(self):
        """Test optimization start without authentication (should fail)."""
        try:
            request_data = {
                "resume_id": "test-resume-id",
                "job_description": SAMPLE_JOB_DESCRIPTION,
                "job_title": "Desenvolvedor Python",
                "company": "Tech Company"
            }

            response = await self.client.post(
                f"{API_BASE}/optimizations/start",
                json=request_data
            )

            # Should return 401 (unauthorized) or 403 (forbidden)
            success = response.status_code in [401, 403]
            details = f"Correctly rejected with status {response.status_code}"
            self.log_test("Optimization Start (No Auth)", success, details)
            return success
        except Exception as e:
            self.log_test("Optimization Start (No Auth)", False, str(e))
            return False

    async def test_get_optimization_no_auth(self):
        """Test get optimization without authentication (should fail)."""
        try:
            response = await self.client.get(f"{API_BASE}/optimizations/test-id")

            # Should return 401 (unauthorized) or 404 (not found)
            success = response.status_code in [401, 403, 404]
            details = f"Correctly rejected with status {response.status_code}"
            self.log_test("Get Optimization (No Auth)", success, details)
            return success
        except Exception as e:
            self.log_test("Get Optimization (No Auth)", False, str(e))
            return False

    async def test_list_optimizations_no_auth(self):
        """Test list optimizations without authentication (should fail)."""
        try:
            response = await self.client.get(f"{API_BASE}/optimizations/")

            # Should return 401 (unauthorized) or 403 (forbidden)
            success = response.status_code in [401, 403]
            details = f"Correctly rejected with status {response.status_code}"
            self.log_test("List Optimizations (No Auth)", success, details)
            return success
        except Exception as e:
            self.log_test("List Optimizations (No Auth)", False, str(e))
            return False

    async def test_api_docs_accessible(self):
        """Test that API documentation is accessible."""
        try:
            response = await self.client.get(f"{BASE_URL}/docs")
            success = response.status_code == 200
            details = "Swagger UI accessible" if success else f"Status: {response.status_code}"
            self.log_test("API Docs Access", success, details)
            return success
        except Exception as e:
            self.log_test("API Docs Access", False, str(e))
            return False

    async def test_openapi_schema(self):
        """Test OpenAPI schema endpoint."""
        try:
            response = await self.client.get(f"{BASE_URL}/openapi.json")
            success = response.status_code == 200

            if success:
                schema = response.json()
                # Check if our endpoints are in the schema
                paths = schema.get("paths", {})
                has_resumes = any("/resumes" in path for path in paths.keys())
                has_optimizations = any("/optimizations" in path for path in paths.keys())

                details = f"Schema loaded, endpoints found: resumes={has_resumes}, optimizations={has_optimizations}"
                success = success and has_resumes and has_optimizations
            else:
                details = f"Status: {response.status_code}"

            self.log_test("OpenAPI Schema", success, details)
            return success
        except Exception as e:
            self.log_test("OpenAPI Schema", False, str(e))
            return False

    async def test_validation_errors(self):
        """Test validation error handling."""
        try:
            # Test invalid request data
            invalid_data = {"resume_id": 123, "job_description": ""}  # Invalid types

            response = await self.client.post(
                f"{API_BASE}/optimizations/start",
                json=invalid_data
            )

            # Should return 422 (validation error) even without auth
            success = response.status_code == 422
            details = f"Validation error handled correctly: {response.status_code}"
            self.log_test("Validation Error Handling", success, details)
            return success
        except Exception as e:
            self.log_test("Validation Error Handling", False, str(e))
            return False

    async def test_cors_headers(self):
        """Test CORS headers are present."""
        try:
            response = await self.client.options(
                f"{API_BASE}/resumes/upload",
                headers={"Origin": "http://localhost:3000"}
            )

            # Check for CORS headers
            cors_headers = [
                "access-control-allow-origin",
                "access-control-allow-methods",
                "access-control-allow-headers"
            ]

            has_cors = any(header in response.headers for header in cors_headers)
            details = f"CORS headers present: {has_cors}"
            self.log_test("CORS Headers", has_cors, details)
            return has_cors
        except Exception as e:
            self.log_test("CORS Headers", False, str(e))
            return False

    async def run_all_tests(self):
        """Run all integration tests."""
        print("🧪 Running CV-Match API Integration Tests")
        print("=" * 50)

        tests = [
            self.test_health_check,
            self.test_security_health,
            self.test_api_docs_accessible,
            self.test_openapi_schema,
            self.test_resume_upload_no_auth,
            self.test_optimization_start_no_auth,
            self.test_get_optimization_no_auth,
            self.test_list_optimizations_no_auth,
            self.test_validation_errors,
            self.test_cors_headers,
        ]

        passed = 0
        total = len(tests)

        for test in tests:
            if await test():
                passed += 1
            print()  # Add spacing between tests

        print("=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")

        # Summary
        failed_tests = [result for result in self.test_results if not result["passed"]]
        if failed_tests:
            print("\n❌ Failed Tests:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        else:
            print("\n🎉 All tests passed!")

        return passed == total


async def main():
    """Main test runner."""
    async with CVMatchAPITester() as tester:
        success = await tester.run_all_tests()
        return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)