#!/usr/bin/env python3
"""
Simple Test Runner for GenSpark Board Backend

This script provides easy commands to run different types of tests with
intelligent test selection and fast feedback.

Usage:
    python run_tests.py             # Auto-detect and run relevant tests
    python run_tests.py unit        # Run only unit tests
    python run_tests.py integration # Run integration tests
    python run_tests.py e2e         # Run E2E tests
    python run_tests.py all         # Run all tests
    python run_tests.py --fast      # Quick mode for development
    python run_tests.py --coverage  # Run with coverage report
"""

import sys
import subprocess
import argparse
import os
from pathlib import Path

def run_command(cmd, description, capture_output=False):
    """Run a command and handle output"""
    print(f"🚀 {description}...")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=capture_output, text=True)
        print(f"✅ {description} completed successfully!")
        return True, result.stdout if capture_output else ""
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        if capture_output and e.stderr:
            print(f"Error: {e.stderr}")
        return False, e.stderr if capture_output else ""

def run_unit_tests(fast=False):
    """Run unit tests"""
    cmd = ["python", "-m", "pytest", "tests/unit/", "--tb=short"]
    if fast:
        cmd.extend(["-q", "-x", "--maxfail=3"])
    else:
        cmd.extend(["-v", "--cov=app", "--cov-report=term-missing"])
    return run_command(cmd, "Unit Tests")

def run_integration_tests(fast=False):
    """Run integration and E2E tests"""
    cmd = ["python", "-m", "pytest", "tests/integration/", "tests/e2e/", "--tb=short"]
    if fast:
        cmd.extend(["-q", "-x", "--maxfail=2"])
    else:
        cmd.extend(["-v"])
    return run_command(cmd, "Integration & E2E Tests")

def run_e2e_tests(fast=False):
    """Run E2E tests only"""
    cmd = ["python", "-m", "pytest", "tests/e2e/", "--tb=short"]
    if fast:
        cmd.extend(["-q", "-x", "--maxfail=1"])
    else:
        cmd.extend(["-v"])
    return run_command(cmd, "E2E Tests")

def run_all_tests(fast=False):
    """Run all tests"""
    cmd = ["python", "-m", "pytest", "tests/", "--tb=short"]
    if fast:
        cmd.extend(["-q", "-x", "--maxfail=5"])
    else:
        cmd.extend(["-v", "--cov=app", "--cov-report=html", "--cov-report=term-missing"])
    return run_command(cmd, "All Tests")

def run_smart_tests():
    """Run smart test selection based on file changes"""
    try:
        # Use the intelligent test runner
        cmd = ["python", "scripts/test_runner.py", "auto"]
        return run_command(cmd, "Smart Test Selection")
    except:
        # Fallback to unit tests
        return run_unit_tests(fast=True)

def show_test_structure():
    """Show the test directory structure"""
    print("\n📁 Test Directory Structure:")
    print("=" * 40)
    
    if os.path.exists("tests"):
        for root, dirs, files in os.walk("tests"):
            level = root.replace("tests", "").count(os.sep)
            indent = " " * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = " " * 2 * (level + 1)
            for file in files:
                if file.endswith('.py'):
                    print(f"{subindent}{file}")
    else:
        print("Tests directory not found!")

def main():
    parser = argparse.ArgumentParser(
        description="Test runner for genspark-board backend",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Smart test selection
  python run_tests.py unit               # Unit tests only
  python run_tests.py unit --fast        # Fast unit tests
  python run_tests.py all --coverage     # All tests with coverage
  python run_tests.py --structure        # Show test structure
        """
    )
    
    parser.add_argument(
        "test_type",
        nargs="?",
        choices=["unit", "integration", "e2e", "all", "smart"],
        default="smart",
        help="Type of tests to run (default: smart)"
    )
    
    parser.add_argument(
        "--fast", "-f",
        action="store_true",
        help="Run tests in fast mode (fail fast, no coverage)"
    )
    
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Run with coverage report"
    )
    
    parser.add_argument(
        "--structure", "-s",
        action="store_true",
        help="Show test directory structure"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Change to backend directory if not already there
    if not os.path.exists("app") and os.path.exists("backend"):
        os.chdir("backend")
    
    # Show structure if requested
    if args.structure:
        show_test_structure()
        return
    
    # Run appropriate test suite
    success = False
    
    if args.test_type == "unit":
        success, _ = run_unit_tests(fast=args.fast)
    elif args.test_type == "integration":
        success, _ = run_integration_tests(fast=args.fast)
    elif args.test_type == "e2e":
        success, _ = run_e2e_tests(fast=args.fast)
    elif args.test_type == "all":
        success, _ = run_all_tests(fast=args.fast)
    elif args.test_type == "smart":
        success, _ = run_smart_tests()
    
    # Print summary
    if success:
        print(f"\n🎉 {args.test_type.title()} tests passed!")
    else:
        print(f"\n💥 Some {args.test_type} tests failed!")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()