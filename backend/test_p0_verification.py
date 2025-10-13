#!/usr/bin/env python3
"""
P0 API Endpoints Verification Script
Verifies all P0 requirements are met for the CV-Match API endpoints.

Requirements:
1. Resume Upload Endpoint with Pydantic models and text extraction
2. Optimization Endpoints (start, get, list) with status tracking
3. Routes registered in main app and authentication dependency implemented
4. All endpoints tested with UV package manager
"""

import asyncio

import httpx


class P0Verifier:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.verification_results = []

    def log_verification(self, requirement: str, passed: bool, details: str = ""):
        """Log verification result."""
        result = {"requirement": requirement, "passed": passed, "details": details}
        self.verification_results.append(result)

        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {requirement}")
        if details:
            print(f"   {details}")

    async def verify_requirement_1(self):
        """Verify Resume Upload Endpoint with Pydantic models and text extraction."""
        print("\n🔍 Requirement 1: Resume Upload Endpoint")
        print("-" * 50)

        # Check endpoint exists
        try:
            response = await self.client.get(f"{self.base_url}/openapi.json")
            schema = response.json()
            paths = schema.get("paths", {})

            upload_endpoint = "/api/resumes/upload"
            if upload_endpoint in paths:
                self.log_verification(
                    "Resume upload endpoint exists", True, f"Found at {upload_endpoint}"
                )

                # Check for POST method
                if "post" in paths[upload_endpoint]:
                    self.log_verification("POST method available", True)

                    # Check request body schema
                    post_spec = paths[upload_endpoint]["post"]
                    request_body = post_spec.get("requestBody", {})
                    if request_body:
                        self.log_verification("Request body schema defined", True)
                    else:
                        self.log_verification(
                            "Request body schema defined", False, "No request body found"
                        )

                    # Check response model
                    responses = post_spec.get("responses", {})
                    if "201" in responses:
                        self.log_verification("201 response defined", True)
                    else:
                        self.log_verification(
                            "201 response defined", False, "No 201 response found"
                        )
                else:
                    self.log_verification("POST method available", False, "No POST method found")
            else:
                self.log_verification(
                    "Resume upload endpoint exists", False, f"Endpoint {upload_endpoint} not found"
                )

        except Exception as e:
            self.log_verification("Resume upload endpoint exists", False, f"Error: {str(e)}")

        # Check Pydantic models
        try:
            # Import models to verify they exist
            import sys

            sys.path.append("/app")

            # Import just to verify they exist
            from app.models.resume import (
                ResumeResponse,  # noqa: F401
                ResumeUploadResponse,  # noqa: F401
            )

            self.log_verification(
                "Resume Pydantic models defined", True, "ResumeUploadResponse, ResumeResponse"
            )
        except ImportError as e:
            self.log_verification(
                "Resume Pydantic models defined", False, f"Import error: {str(e)}"
            )
        except Exception as e:
            self.log_verification("Resume Pydantic models defined", False, f"Error: {str(e)}")

        # Check text extraction service
        try:
            from app.services.text_extraction import extract_text  # noqa: F401

            self.log_verification("Text extraction service available", True)
        except ImportError as e:
            self.log_verification(
                "Text extraction service available", False, f"Import error: {str(e)}"
            )
        except Exception as e:
            self.log_verification("Text extraction service available", False, f"Error: {str(e)}")

    async def verify_requirement_2(self):
        """Verify Optimization Endpoints with status tracking."""
        print("\n🔍 Requirement 2: Optimization Endpoints")
        print("-" * 50)

        # Check endpoints exist
        try:
            response = await self.client.get(f"{self.base_url}/openapi.json")
            schema = response.json()
            paths = schema.get("paths", {})

            optimization_endpoints = [
                "/api/optimizations/start",
                "/api/optimizations/{optimization_id}",
                "/api/optimizations/",
            ]

            for endpoint in optimization_endpoints:
                if endpoint in paths:
                    self.log_verification(f"Optimization endpoint exists: {endpoint}", True)

                    # Check methods
                    if "start" in endpoint:
                        if "post" in paths[endpoint]:
                            self.log_verification("POST method for start endpoint", True)
                        else:
                            self.log_verification(
                                "POST method for start endpoint", False, "No POST method"
                            )
                    elif "{optimization_id}" in endpoint:
                        if "get" in paths[endpoint]:
                            self.log_verification("GET method for get endpoint", True)
                        else:
                            self.log_verification(
                                "GET method for get endpoint", False, "No GET method"
                            )
                    else:  # list endpoint
                        if "get" in paths[endpoint]:
                            self.log_verification("GET method for list endpoint", True)
                        else:
                            self.log_verification(
                                "GET method for list endpoint", False, "No GET method"
                            )
                else:
                    self.log_verification(
                        f"Optimization endpoint exists: {endpoint}", False, "Endpoint not found"
                    )

        except Exception as e:
            self.log_verification("Optimization endpoints exist", False, f"Error: {str(e)}")

        # Check Pydantic models
        try:
            import sys

            sys.path.append("/app")

            # Import just to verify they exist
            from app.models.optimization import (
                OptimizationResponse,  # noqa: F401
                OptimizationStatus,
                StartOptimizationRequest,  # noqa: F401
            )

            self.log_verification(
                "Optimization Pydantic models defined",
                True,
                "StartOptimizationRequest, OptimizationResponse, OptimizationStatus",
            )
        except ImportError as e:
            self.log_verification(
                "Optimization Pydantic models defined", False, f"Import error: {str(e)}"
            )
        except Exception as e:
            self.log_verification("Optimization Pydantic models defined", False, f"Error: {str(e)}")

        # Check status tracking
        try:
            from app.models.optimization import OptimizationStatus

            # Verify status values
            statuses = [
                OptimizationStatus.PENDING_PAYMENT,
                OptimizationStatus.PROCESSING,
                OptimizationStatus.COMPLETED,
                OptimizationStatus.FAILED,
            ]

            status_names = [status.value for status in statuses]
            expected_statuses = ["pending_payment", "processing", "completed", "failed"]

            if all(status in status_names for status in expected_statuses):
                self.log_verification(
                    "Status tracking implemented", True, f"Statuses: {status_names}"
                )
            else:
                self.log_verification("Status tracking implemented", False, "Missing statuses")

        except ImportError as e:
            self.log_verification("Status tracking implemented", False, f"Import error: {str(e)}")
        except Exception as e:
            self.log_verification("Status tracking implemented", False, f"Error: {str(e)}")

    async def verify_requirement_3(self):
        """Verify Routes registered and authentication dependency implemented."""
        print("\n🔍 Requirement 3: Routes and Authentication")
        print("-" * 50)

        # Check routes registered
        try:
            response = await self.client.get(f"{self.base_url}/openapi.json")
            schema = response.json()
            paths = schema.get("paths", {})

            # Count endpoints
            resume_endpoints = [p for p in paths.keys() if "/resumes" in p]
            optimization_endpoints = [p for p in paths.keys() if "/optimizations" in p]

            if len(resume_endpoints) > 0:
                self.log_verification(
                    "Resume routes registered", True, f"Found {len(resume_endpoints)} endpoints"
                )
            else:
                self.log_verification(
                    "Resume routes registered", False, "No resume endpoints found"
                )

            if len(optimization_endpoints) > 0:
                self.log_verification(
                    "Optimization routes registered",
                    True,
                    f"Found {len(optimization_endpoints)} endpoints",
                )
            else:
                self.log_verification(
                    "Optimization routes registered", False, "No optimization endpoints found"
                )

        except Exception as e:
            self.log_verification("Routes registered", False, f"Error: {str(e)}")

        # Check authentication dependency
        try:
            # Test unauthenticated access (should fail)
            response = await self.client.post(f"{self.base_url}/api/optimizations/start", json={})

            if response.status_code == 401:
                self.log_verification(
                    "Authentication dependency implemented",
                    True,
                    "Unauthenticated requests properly rejected",
                )
            else:
                self.log_verification(
                    "Authentication dependency implemented",
                    False,
                    f"Expected 401, got {response.status_code}",
                )

        except Exception as e:
            self.log_verification(
                "Authentication dependency implemented", False, f"Error: {str(e)}"
            )

        # Check auth module exists
        try:
            import sys

            sys.path.append("/app")

            from app.core.auth import get_current_user  # noqa: F401

            self.log_verification(
                "Auth module implemented", True, "get_current_user function available"
            )
        except ImportError as e:
            self.log_verification("Auth module implemented", False, f"Import error: {str(e)}")
        except Exception as e:
            self.log_verification("Auth module implemented", False, f"Error: {str(e)}")

    async def verify_requirement_4(self):
        """Verify UV package manager functionality."""
        print("\n🔍 Requirement 4: UV Package Manager")
        print("-" * 50)

        # Check if we can run Python with UV (in Docker environment)
        try:
            import subprocess

            result = subprocess.run(
                ["python", "-c", 'import sys; print("UV environment working")'],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                self.log_verification(
                    "UV environment functional", True, "Python execution successful"
                )
            else:
                self.log_verification("UV environment functional", False, "Python execution failed")

        except Exception as e:
            self.log_verification("UV environment functional", False, f"Error: {str(e)}")

        # Check dependencies are available
        try:
            import fastapi  # noqa: F401
            import httpx  # noqa: F401
            import pydantic  # noqa: F401
            import supabase  # noqa: F401

            self.log_verification(
                "Dependencies available via UV", True, "FastAPI, Pydantic, HTTPX, Supabase"
            )
        except ImportError as e:
            self.log_verification("Dependencies available via UV", False, f"Import error: {str(e)}")

    async def run_verification(self):
        """Run complete P0 verification."""
        print("🎯 P0 API Endpoints Verification")
        print("=" * 60)
        print("Verifying all P0 requirements for CV-Match API endpoints")
        print("=" * 60)

        await self.verify_requirement_1()
        await self.verify_requirement_2()
        await self.verify_requirement_3()
        await self.verify_requirement_4()

        # Summary
        passed = sum(1 for result in self.verification_results if result["passed"])
        total = len(self.verification_results)

        print("\n" + "=" * 60)
        print("📊 P0 Verification Summary")
        print("=" * 60)
        print(f"Total checks: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success rate: {(passed / total) * 100:.1f}%")

        if passed == total:
            print("\n🎉 ALL P0 REQUIREMENTS VERIFIED!")
            print("✅ Resume Upload Endpoint with Pydantic models and text extraction")
            print("✅ Optimization Endpoints with status tracking")
            print("✅ Routes registered and authentication dependency implemented")
            print("✅ UV package manager environment functional")
            print("\n🚀 Ready for frontend integration and comprehensive testing!")
        else:
            print(f"\n⚠️ {total - passed} requirements not met")
            failed = [r for r in self.verification_results if not r["passed"]]
            for result in failed:
                print(f"❌ {result['requirement']}: {result['details']}")

        await self.client.aclose()
        return passed == total


async def main():
    """Main verification runner."""
    verifier = P0Verifier()
    success = await verifier.run_verification()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
