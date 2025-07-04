#!/usr/bin/env python3
"""
Test runner script for the Zotero automation project.
"""

import subprocess
import sys


def run_tests():
    """Run the test suite."""
    print("Running tests for Zotero automation project...")
    print("=" * 50)

    # Run pytest with coverage
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "--cov=.",
        "--cov-report=term-missing",
        "--cov-report=html",
        "-v",
    ]

    try:
        subprocess.run(cmd, check=True)
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        print("Coverage report generated in htmlcov/index.html")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return e.returncode


def run_specific_test(test_path):
    """Run a specific test file or test function."""
    cmd = [sys.executable, "-m", "pytest", test_path, "-v"]

    try:
        subprocess.run(cmd, check=True)
        print(f"\n✅ Test {test_path} passed!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Test {test_path} failed!")
        return e.returncode


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test
        test_path = sys.argv[1]
        exit_code = run_specific_test(test_path)
    else:
        # Run all tests
        exit_code = run_tests()

    sys.exit(exit_code)
