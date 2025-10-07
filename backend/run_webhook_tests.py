#!/usr/bin/env python3
"""
Test runner script for payment webhook tests.
Provides convenient commands for running webhook test suites.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list, description: str) -> int:
    """Run a command and return the exit code."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")

    result = subprocess.run(cmd)
    return result.returncode


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test runner for payment webhook tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_webhook_tests.py all                    # Run all tests
  python run_webhook_tests.py integration            # Run integration tests only
  python run_webhook_tests.py unit                   # Run unit tests only
  python run_webhook_tests.py coverage               # Run with coverage report
  python run_webhook_tests.py brazilian             # Run Brazilian market tests
  python run_webhook_tests.py --verbose              # Verbose output
        """
    )

    parser.add_argument(
        "test_type",
        choices=["all", "integration", "unit", "coverage", "brazilian"],
        help="Type of tests to run",
        default="all"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "-k", "--keyword",
        help="Filter tests by keyword"
    )

    parser.add_argument(
        "--cov",
        action="store_true",
        help="Generate coverage report"
    )

    parser.add_argument(
        "--html",
        action="store_true",
        help="Generate HTML coverage report"
    )

    args = parser.parse_args()

    # Base pytest command
    cmd = ["python", "-m", "pytest"]

    # Add verbosity
    if args.verbose:
        cmd.append("-v")

    # Add coverage if requested
    if args.cov or args.html:
        cmd.extend(["--cov=app"])
        if args.html:
            cmd.extend(["--cov-report=html"])

    # Determine which tests to run
    if args.test_type == "all":
        cmd.append("tests/")
    elif args.test_type == "integration":
        cmd.extend(["-m", "integration", "tests/integration/"])
    elif args.test_type == "unit":
        cmd.extend(["-m", "unit", "tests/unit/"])
    elif args.test_type == "brazilian":
        cmd.extend(["-k", "brazilian", "tests/"])
    elif args.test_type == "coverage":
        cmd.extend(["--cov=app", "--cov-report=term-missing", "--cov-report=html", "tests/"])

    # Add keyword filter if provided
    if args.keyword:
        cmd.extend(["-k", args.keyword])

    # Run the tests
    exit_code = run_command(cmd, f"{args.test_type} tests")

    # Print additional information
    if args.html and exit_code == 0:
        print(f"\nCoverage report generated: {Path('htmlcov/index.html').absolute()}")

    # Print quick stats
    if exit_code == 0:
        print(f"\n✅ All {args.test_type} tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code: {exit_code}")
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
