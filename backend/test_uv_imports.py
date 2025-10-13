#!/usr/bin/env python3
"""
UV package manager import tests for CV-Match backend.
Tests that all modules can be imported correctly.
"""

import importlib
import sys


def test_import(module_name: str, description: str = ""):
    """Test importing a module."""
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name} imported successfully {description}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import {module_name}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error importing {module_name}: {e}")
        return False


def main():
    """Run all import tests."""
    print("🧪 Testing CV-Match Backend Imports")
    print("=" * 50)

    # Test core dependencies
    core_modules = [
        ("fastapi", ""),
        ("pydantic", ""),
        ("httpx", ""),
        ("supabase", ""),
        ("openai", ""),
        ("anthropic", ""),
    ]

    # Test app modules
    app_modules = [
        ("app.main", ""),
        ("app.core.auth", ""),
        ("app.models.resume", ""),
        ("app.models.optimization", ""),
        ("app.api.endpoints.resumes", ""),
        ("app.api.endpoints.optimizations", ""),
        ("app.services.resume_service", ""),
        ("app.services.score_improvement_service", ""),
        ("app.services.job_service", ""),
        ("app.services.supabase.database", ""),
    ]

    passed = 0
    total = len(core_modules) + len(app_modules)

    print("📦 Testing Core Dependencies:")
    for module, desc in core_modules:
        if test_import(module, desc):
            passed += 1

    print("\n🏗️ Testing App Modules:")
    for module, desc in app_modules:
        if test_import(module, desc):
            passed += 1

    print("\n" + "=" * 50)
    print(f"📊 Import Test Results: {passed}/{total} modules imported successfully")

    if passed == total:
        print("🎉 All imports successful!")
        return True
    else:
        print(f"⚠️ {total - passed} modules failed to import")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
