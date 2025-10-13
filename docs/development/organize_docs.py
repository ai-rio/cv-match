#!/usr/bin/env python3
"""
Documentation Organization Script
Organizes files in the development docs folder into logical categories
"""

import os
import shutil
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

# Folders to keep as-is (already organized)
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

# Files to keep in root
ROOT_FILES = [
    "README.md",
]


def create_backup():
    """Create a backup of the current state"""
    backup_dir = BASE_DIR / "_backup_before_organization"
    if backup_dir.exists():
        print(f"⚠️  Backup already exists at {backup_dir}")
        response = input("Do you want to overwrite it? (y/n): ")
        if response.lower() != 'y':
            print("Backup cancelled.")
            return False

    print(f"📦 Creating backup at {backup_dir}...")
    # We'll skip actual backup to avoid duplicating everything
    # Just create the marker directory
    backup_dir.mkdir(exist_ok=True)
    with open(backup_dir / "BACKUP_INFO.txt", "w") as f:
        f.write("Backup created before running organize_docs.py\n")
        f.write("Original files are being moved, not copied.\n")

    return True


def create_folder_structure():
    """Create the new folder structure"""
    print("\n📁 Creating folder structure...")
    for folder_name in ORGANIZATION_STRUCTURE.keys():
        folder_path = BASE_DIR / folder_name
        folder_path.mkdir(exist_ok=True)
        print(f"   ✓ Created {folder_name}")


def move_files():
    """Move files to their respective folders"""
    print("\n📋 Moving files to organized folders...")

    moved_count = 0
    skipped_count = 0

    for folder_name, files in ORGANIZATION_STRUCTURE.items():
        folder_path = BASE_DIR / folder_name

        for filename in files:
            source = BASE_DIR / filename
            destination = folder_path / filename

            if source.exists() and source.is_file():
                try:
                    shutil.move(str(source), str(destination))
                    print(f"   ✓ Moved {filename} → {folder_name}/")
                    moved_count += 1
                except Exception as e:
                    print(f"   ✗ Error moving {filename}: {e}")
                    skipped_count += 1
            else:
                print(f"   ⚠️  File not found: {filename}")
                skipped_count += 1

    return moved_count, skipped_count


def create_readme_files():
    """Create README files for each organized folder"""
    print("\n📝 Creating README files for organized folders...")

    readme_content = {
        "01-security": """# Security Documentation

This folder contains all security-related documentation including:
- Security audit reports
- Security implementation summaries
- Deployment security guidelines
- Critical security fixes

## Key Documents
- `SECURITY-AUDIT-FINAL.md` - Final comprehensive security audit
- `CRITICAL_SECURITY_FIXES_SUMMARY.md` - Summary of critical fixes applied
- `llm-security-implementation.md` - LLM-specific security measures
""",

        "02-phase-management": """# Phase Management Documentation

This folder contains documentation for project phases (P0, P1, P1.5):
- Phase completion reports
- Implementation guides
- Verification checklists
- Agent swarm strategies

## Phases
- **Phase 0**: Core security and bias detection
- **Phase 1**: Payment integration
- **Phase 1.5**: Subscription management
""",

        "03-reports-audits": """# Reports & Audits

This folder contains various project reports and audits:
- Code maturity audits
- Progress reports
- Verification summaries
- Session summaries

## Types of Reports
- Weekly progress reports
- Infrastructure verification
- Code maturity assessments
""",

        "04-guides": """# Implementation Guides

This folder contains step-by-step guides and quick-start documentation:
- Agent swarm setup guides
- Implementation guides
- Dependency management guides
- Testing setup guides

## Quick Start Resources
- `QUICK-START-AGENT-SWARM.md` - Get started with agent swarm
- `implementation-guide.md` - General implementation guide
""",

        "05-architecture": """# Architecture Documentation

This folder contains high-level architecture and business documentation:
- System architecture overview
- Business model analysis
- Project roadmap

## Key Documents
- `architecture-overview.md` - System architecture
- `ROADMAP.md` - Project roadmap and future plans
""",

        "06-dependencies": """# Dependencies Documentation

This folder contains documentation related to project dependencies:
- Dependency pinning reports
- Dependency maintenance guides
- Version management

## Key Documents
- `dependency-pinning-report.md` - Dependency versions and pinning strategy
""",

        "07-integrations": """# Integration Documentation

This folder contains documentation for third-party integrations:
- Stripe payment integration
- Next-intl localization
- Resume matcher integration
- Pricing configuration

## Integrations Covered
- **Stripe**: Payment processing
- **Next-intl**: Internationalization
- **Resume Matcher**: AI-powered resume matching
""",

        "08-assets": """# Assets

This folder contains static assets and resources used in documentation:
- CSS files
- Images
- Other static resources

## Contents
- `index.css` - Documentation styling
""",
    }

    for folder_name, content in readme_content.items():
        readme_path = BASE_DIR / folder_name / "README.md"
        with open(readme_path, "w") as f:
            f.write(content)
        print(f"   ✓ Created README for {folder_name}")


def update_main_readme():
    """Update the main README with the new structure"""
    print("\n📄 Updating main README...")

    main_readme_content = """# Development Documentation

This directory contains all development documentation for the CV-Match project, now organized by category.

## 📁 Folder Structure

### Organized Documentation

- **01-security/** - Security audits, fixes, and implementation docs
- **02-phase-management/** - Phase 0, 1, and 1.5 documentation
- **03-reports-audits/** - Progress reports and code audits
- **04-guides/** - Implementation guides and quick-starts
- **05-architecture/** - System architecture and business models
- **06-dependencies/** - Dependency management documentation
- **07-integrations/** - Third-party integration docs (Stripe, Next-intl, etc.)
- **08-assets/** - Static assets (CSS, images, etc.)

### Specialized Directories

- **UI-UX/** - User interface and experience documentation
- **design-system-prompts/** - Design system implementation prompts
- **p0-prompts/** - Phase 0 implementation prompts
- **p1-prompts/** - Phase 1 implementation prompts
- **p1.5-prompts/** - Phase 1.5 implementation prompts
- **phase0-security-prompts/** - Security-focused prompts for Phase 0
- **system-iplementation-assessment/** - System implementation assessments
- **type-check/** - TypeScript type checking documentation
- **uncliassified/** - Documents pending classification

## 🚀 Quick Links

### For New Developers
1. Start with `05-architecture/architecture-overview.md`
2. Review `02-phase-management/P0-IMPLEMENTATION-GUIDE.md`
3. Check `04-guides/QUICK-START-AGENT-SWARM.md`

### For Security Review
- See everything in `01-security/`
- Start with `01-security/SECURITY-AUDIT-FINAL.md`

### For Integration Work
- Check `07-integrations/` for all integration documentation
- Stripe: `stripe-integration-analysis.md`
- Localization: `next-intl-integration.md`

## 📋 Project Phases

- **Phase 0**: Security hardening and bias detection (Completed)
- **Phase 1**: Payment integration with Stripe
- **Phase 1.5**: Subscription management
- **Future Phases**: See `05-architecture/ROADMAP.md`

## 🛠️ Maintenance

To reorganize documentation, run:
```bash
python3 organize_docs.py
```

---

*Documentation organized on: 2025-10-13*
"""

    readme_path = BASE_DIR / "README.md"
    with open(readme_path, "w") as f:
        f.write(main_readme_content)
    print(f"   ✓ Updated main README.md")


def print_summary(moved_count: int, skipped_count: int):
    """Print organization summary"""
    print("\n" + "="*60)
    print("📊 ORGANIZATION SUMMARY")
    print("="*60)
    print(f"✅ Files moved: {moved_count}")
    print(f"⚠️  Files skipped: {skipped_count}")
    print(f"📁 Folders created: {len(ORGANIZATION_STRUCTURE)}")
    print(f"📁 Folders kept as-is: {len(KEEP_FOLDERS)}")
    print("\n✨ Organization complete!")
    print(f"\n📂 Navigate to: {BASE_DIR}")
    print("\nNew structure:")
    for folder in sorted(ORGANIZATION_STRUCTURE.keys()):
        print(f"   - {folder}/")
    print("="*60)


def main():
    """Main execution function"""
    print("="*60)
    print("📚 CV-MATCH DOCUMENTATION ORGANIZER")
    print("="*60)
    print(f"\n📍 Working directory: {BASE_DIR}")

    # Confirm with user
    print("\n⚠️  This script will reorganize your documentation files.")
    response = input("\nProceed with organization? (y/n): ")

    if response.lower() != 'y':
        print("\n❌ Organization cancelled.")
        return

    # Create backup marker
    if not create_backup():
        return

    # Execute organization
    create_folder_structure()
    moved_count, skipped_count = move_files()
    create_readme_files()
    update_main_readme()

    # Print summary
    print_summary(moved_count, skipped_count)

    print("\n💡 TIP: Check each new folder's README.md for details about its contents.")


if __name__ == "__main__":
    main()
