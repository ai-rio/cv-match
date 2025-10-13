#!/usr/bin/env python3
"""
Documentation Organization Preview Script
Shows what will happen without actually moving files
"""

import os
from pathlib import Path
from typing import Dict, List

# Base directory
BASE_DIR = Path("/home/carlos/projects/cv-match/docs/development")

# Define folder structure and file mappings
ORGANIZATION_STRUCTURE: Dict[str, List[str]] = {
    "01-security": [
        "SECURITY-AUDIT-FINAL.md",
        "SECURITY-AUDIT-REPORT-UPDATED.md",
        "SECURITY-AUDIT-REPORT.md",
        "SECURITY-DOCUMENTATION-SUMMARY.md",
        "CRITICAL_SECURITY_FIXES_SUMMARY.md",
        "deployment-security.md",
        "llm-security-implementation.md",
        "critical-findings-verification.md",
    ],

    "02-phase-management": [
        "P0-COMPLETION-AUDIT.md",
        "P0-FINAL-REPORT.md",
        "P0-IMPLEMENTATION-GUIDE.md",
        "P0-TO-P1-QUICK-START.md",
        "P0-VERIFICATION-CHECKLIST.md",
        "P0-VERIFICATION-COMPLETE.md",
        "PHASE0-BIAS-DETECTION-COMPLETION-SUMMARY.md",
        "p0-agent-swarm-strategy.md",
        "p1-agent-swarm-strategy.md",
        "BIAS-DETECTION-IMPLEMENTATION-REPORT.md",
    ],

    "03-reports-audits": [
        "CODE_MATURITY_AUDIT.md",
        "CODE_MATURITY_AUDIT_ORIGINAL.md",
        "INFRASTRUCTURE-VERIFICATION-COMPLETE.md",
        "VERIFICATION-PACKAGE-SUMMARY.md",
        "WEEK_0_PROGRESS_REPORT_CORRECTED.md",
        "STATUS-UPDATE-SUMMARY.md",
        "SESSION-SUMMARY-2025-10-09.md",
    ],

    "04-guides": [
        "QUICK-START-AGENT-SWARM.md",
        "AGENT-SWARM-EXECUTIVE-SUMMARY.md",
        "implementation-guide.md",
        "dependency-maintenance-guide.md",
        "stripe-test-setup-guide.md",
    ],

    "05-architecture": [
        "architecture-overview.md",
        "business-model-analysis.md",
        "ROADMAP.md",
    ],

    "06-dependencies": [
        "dependency-pinning-report.md",
    ],

    "07-integrations": [
        "stripe-integration-analysis.md",
        "stripe-validation-report.md",
        "pricing-configuration-fix.md",
        "next-intl-integration.md",
        "resume-matcher-integration.md",
    ],

    "08-assets": [
        "index.css",
    ],
}

# Folders to keep as-is
KEEP_FOLDERS = [
    "UI-UX",
    "design-system-prompts",
    "p0-prompts",
    "p1-prompts",
    "p1.5-prompts",
    "phase0-security-prompts",
    "system-iplementation-assessment",
    "type-check",
    "uncliassified",
]

ROOT_FILES = ["README.md"]


def preview_organization():
    """Show what will happen without making changes"""
    print("="*70)
    print("📋 DOCUMENTATION ORGANIZATION PREVIEW")
    print("="*70)
    print(f"\n📍 Target directory: {BASE_DIR}\n")

    # Count statistics
    total_files_to_move = 0
    files_exist = 0
    files_missing = 0

    print("📁 NEW FOLDER STRUCTURE:")
    print("-" * 70)

    for folder_name, files in sorted(ORGANIZATION_STRUCTURE.items()):
        print(f"\n{folder_name}/")

        for filename in files:
            source = BASE_DIR / filename
            total_files_to_move += 1

            if source.exists() and source.is_file():
                status = "✅"
                files_exist += 1
            else:
                status = "❌ NOT FOUND"
                files_missing += 1

            print(f"  {status} {filename}")

    print("\n" + "-" * 70)
    print("\n📂 FOLDERS TO KEEP AS-IS:")
    for folder in KEEP_FOLDERS:
        folder_path = BASE_DIR / folder
        exists = "✅" if folder_path.exists() else "❌"
        print(f"  {exists} {folder}/")

    print("\n" + "-" * 70)
    print("\n📄 FILES TO KEEP IN ROOT:")
    for filename in ROOT_FILES:
        file_path = BASE_DIR / filename
        exists = "✅" if file_path.exists() else "❌"
        print(f"  {exists} {filename}")

    print("\n" + "="*70)
    print("📊 STATISTICS")
    print("="*70)
    print(f"  Total files to organize:  {total_files_to_move}")
    print(f"  Files found:              {files_exist} ✅")
    print(f"  Files missing:            {files_missing} ❌")
    print(f"  New folders to create:    {len(ORGANIZATION_STRUCTURE)}")
    print(f"  Existing folders to keep: {len(KEEP_FOLDERS)}")
    print("="*70)

    if files_missing > 0:
        print(f"\n⚠️  WARNING: {files_missing} file(s) not found!")
        print("   These files may have been moved or deleted.")

    print("\n💡 TO PROCEED:")
    print("   Run: python3 organize_docs.py")
    print("\n💡 TO CANCEL:")
    print("   No changes have been made yet.")
    print("\n" + "="*70)


def main():
    preview_organization()


if __name__ == "__main__":
    main()
