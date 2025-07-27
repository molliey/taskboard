#!/usr/bin/env python3
"""
Simplified and Intelligent Test Runner
Automatically selects appropriate tests based on project changes and context
"""

import os
import sys
import subprocess
import argparse
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

class IntelligentTestRunner:
    """Smart test runner that adapts to changes and context"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.backend_root = self.project_root / "backend"
        self.test_results = {}
        
    def detect_changes(self) -> Dict[str, List[str]]:
        """Detect changed files to determine which tests to run"""
        try:
            # Get changed files from git
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                # If git fails, run all tests
                return {"all": ["all"]}
            
            changed_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            # Categorize changes
            changes = {
                "models": [],
                "api": [],
                "services": [],
                "auth": [],
                "frontend": [],
                "config": [],
                "tests": []
            }
            
            for file in changed_files:
                if "backend/app/models" in file:
                    changes["models"].append(file)
                elif "backend/app/api" in file:
                    changes["api"].append(file)
                elif "backend/app/services" in file:
                    changes["services"].append(file)
                elif "backend/app/utils/auth" in file:
                    changes["auth"].append(file)
                elif "frontend/" in file:
                    changes["frontend"].append(file)
                elif any(x in file for x in ["requirements.txt", "docker", "yml", "yaml"]):
                    changes["config"].append(file)
                elif "test" in file:
                    changes["tests"].append(file)
            
            return changes
            
        except Exception as e:
            print(f"Error detecting changes: {e}")
            return {"all": ["all"]}
    
    def select_tests(self, changes: Dict[str, List[str]], test_type: str = "auto") -> List[str]:
        """Select which tests to run based on changes"""
        if test_type != "auto":
            return [test_type]
        
        selected_tests = set()
        
        # If config changes, run all tests
        if changes["config"]:
            return ["all"]
        
        # Map changes to test categories
        if changes["models"]:
            selected_tests.add("unit")
            selected_tests.add("integration")
        
        if changes["api"]:
            selected_tests.add("e2e")
            selected_tests.add("integration")
        
        if changes["services"]:
            selected_tests.add("unit")
        
        if changes["auth"]:
            selected_tests.add("unit")
            selected_tests.add("e2e")
        
        if changes["frontend"]:
            selected_tests.add("e2e")
        
        if changes["tests"]:
            # If only test files changed, run those specific tests
            if not any(changes[k] for k in changes if k != "tests"):
                return ["unit", "integration"]
        
        # If no specific changes detected or too many changes, run core tests
        if not selected_tests or len(selected_tests) >= 3:
            return ["unit", "integration"]
        
        return list(selected_tests)
    
    def run_unit_tests(self, fast: bool = False) -> bool:
        """Run unit tests"""
        print("🧪 Running Unit Tests...")
        
        cmd = [
            "python", "-m", "pytest", "tests/unit/",
            "--tb=short",
            "-q" if fast else "-v",
        ]
        
        if not fast:
            cmd.extend([
                "--cov=app",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov",
                "--cov-fail-under=70"
            ])
        
        if fast:
            cmd.extend(["-x", "--maxfail=3"])
        
        return self._run_test_command(cmd, "unit_tests")
    
    def run_integration_tests(self, fast: bool = False) -> bool:
        """Run integration tests"""
        print("🔗 Running Integration Tests...")
        
        cmd = [
            "python", "-m", "pytest", "tests/integration/", "tests/e2e/",
            "--tb=short",
            "-v" if not fast else "-q",
        ]
        
        if fast:
            cmd.extend(["-x", "--maxfail=2"])
        
        return self._run_test_command(cmd, "integration_tests")
    
    def run_e2e_tests(self, fast: bool = False) -> bool:
        """Run E2E tests"""
        print("🌐 Running E2E Tests...")
        
        cmd = [
            "python", "-m", "pytest", "tests/e2e/",
            "--tb=short",
            "-v" if not fast else "-q",
        ]
        
        if fast:
            cmd.extend(["-x", "--maxfail=1"])
        
        return self._run_test_command(cmd, "e2e_tests")
    
    def run_performance_tests(self) -> bool:
        """Run performance tests"""
        print("⚡ Running Performance Tests...")
        
        cmd = [
            "python", "-m", "pytest", "tests/performance/",
            "--benchmark-only",
            "--benchmark-json=benchmark.json",
            "-v"
        ]
        
        return self._run_test_command(cmd, "performance_tests")
    
    def run_security_tests(self) -> bool:
        """Run security tests"""
        print("🔒 Running Security Scan...")
        
        # Run bandit
        bandit_cmd = ["bandit", "-r", "app/", "-f", "json", "-o", "bandit-report.json"]
        bandit_success = self._run_test_command(bandit_cmd, "security_bandit", check=False)
        
        # Run safety
        safety_cmd = ["safety", "check", "--json", "--output", "safety-report.json"]
        safety_success = self._run_test_command(safety_cmd, "security_safety", check=False)
        
        return bandit_success and safety_success
    
    def _run_test_command(self, cmd: List[str], test_name: str, check: bool = True) -> bool:
        """Run a test command and record results"""
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.backend_root,
                capture_output=True,
                text=True,
                check=check
            )
            
            execution_time = time.time() - start_time
            success = result.returncode == 0
            
            self.test_results[test_name] = {
                "success": success,
                "execution_time": execution_time,
                "returncode": result.returncode,
                "stdout": result.stdout[-1000:] if result.stdout else "",  # Last 1000 chars
                "stderr": result.stderr[-1000:] if result.stderr else ""   # Last 1000 chars
            }
            
            if success:
                print(f"✅ {test_name} passed in {execution_time:.2f}s")
            else:
                print(f"❌ {test_name} failed in {execution_time:.2f}s")
                if result.stderr:
                    print(f"Error: {result.stderr}")
            
            return success
            
        except subprocess.CalledProcessError as e:
            execution_time = time.time() - start_time
            self.test_results[test_name] = {
                "success": False,
                "execution_time": execution_time,
                "returncode": e.returncode,
                "stdout": e.stdout[-1000:] if e.stdout else "",
                "stderr": e.stderr[-1000:] if e.stderr else ""
            }
            
            print(f"❌ {test_name} failed in {execution_time:.2f}s")
            print(f"Error: {e.stderr}")
            return False
        
        except Exception as e:
            print(f"❌ Unexpected error running {test_name}: {e}")
            return False
    
    def generate_coverage_report(self):
        """Generate and display coverage report"""
        print("\n📊 Generating Coverage Report...")
        
        try:
            # Generate HTML coverage report
            subprocess.run(
                ["python", "-m", "coverage", "html"],
                cwd=self.backend_root,
                check=True
            )
            
            # Generate XML for CI
            subprocess.run(
                ["python", "-m", "coverage", "xml"],
                cwd=self.backend_root,
                check=True
            )
            
            print("✅ Coverage reports generated:")
            print(f"  - HTML: {self.backend_root}/htmlcov/index.html")
            print(f"  - XML: {self.backend_root}/coverage.xml")
            
        except Exception as e:
            print(f"❌ Error generating coverage report: {e}")
    
    def print_summary(self):
        """Print test execution summary"""
        print("\n" + "="*60)
        print("📋 TEST EXECUTION SUMMARY")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results.values() if r["success"])
        total_time = sum(r["execution_time"] for r in self.test_results.values())
        
        print(f"Total test suites: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Total execution time: {total_time:.2f}s")
        print()
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} {test_name} ({result['execution_time']:.2f}s)")
        
        print("="*60)
        
        # Save results to JSON
        results_file = self.backend_root / "test-results.json"
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"📄 Detailed results saved to: {results_file}")
    
    def run_tests(self, test_types: List[str], fast: bool = False, 
                  with_coverage: bool = True, with_security: bool = False):
        """Run selected test types"""
        print("🚀 Starting Intelligent Test Runner")
        print(f"Test types: {', '.join(test_types)}")
        print(f"Fast mode: {fast}")
        print(f"Coverage: {with_coverage}")
        print()
        
        success_count = 0
        
        for test_type in test_types:
            if test_type == "unit":
                if self.run_unit_tests(fast):
                    success_count += 1
            elif test_type == "integration":
                if self.run_integration_tests(fast):
                    success_count += 1
            elif test_type == "e2e":
                if self.run_e2e_tests(fast):
                    success_count += 1
            elif test_type == "performance":
                if self.run_performance_tests():
                    success_count += 1
            elif test_type == "all":
                # Run core test suite
                for core_test in ["unit", "integration", "e2e"]:
                    if core_test == "unit" and self.run_unit_tests(fast):
                        success_count += 1
                    elif core_test == "integration" and self.run_integration_tests(fast):
                        success_count += 1
                    elif core_test == "e2e" and self.run_e2e_tests(fast):
                        success_count += 1
        
        if with_security:
            if self.run_security_tests():
                success_count += 1
        
        if with_coverage and not fast:
            self.generate_coverage_report()
        
        self.print_summary()
        
        # Return success if all tests passed
        return success_count == len(self.test_results)

def main():
    parser = argparse.ArgumentParser(
        description="Intelligent Test Runner for GenSpark Board",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_runner.py                    # Auto-detect tests based on changes
  python test_runner.py unit               # Run only unit tests
  python test_runner.py integration e2e    # Run integration and E2E tests
  python test_runner.py all --fast         # Run all tests in fast mode
  python test_runner.py unit --security    # Run unit tests + security scan
        """
    )
    
    parser.add_argument(
        "test_types", 
        nargs="*", 
        choices=["auto", "unit", "integration", "e2e", "performance", "all"],
        default=["auto"],
        help="Types of tests to run (default: auto-detect)"
    )
    
    parser.add_argument(
        "--fast", "-f",
        action="store_true",
        help="Run tests in fast mode (skip coverage, fail fast)"
    )
    
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Skip coverage reporting"
    )
    
    parser.add_argument(
        "--security", "-s",
        action="store_true",
        help="Include security scan"
    )
    
    parser.add_argument(
        "--changed-only",
        action="store_true",
        help="Only run tests for changed files"
    )
    
    args = parser.parse_args()
    
    runner = IntelligentTestRunner()
    
    # Determine test types to run
    if args.test_types == ["auto"] or args.changed_only:
        changes = runner.detect_changes()
        test_types = runner.select_tests(changes, "auto")
        print(f"🔍 Detected changes, running: {', '.join(test_types)}")
    else:
        test_types = args.test_types
    
    # Run tests
    success = runner.run_tests(
        test_types=test_types,
        fast=args.fast,
        with_coverage=not args.no_coverage,
        with_security=args.security
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()