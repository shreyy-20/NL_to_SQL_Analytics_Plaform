#!/usr/bin/env python3
"""
Test runner for KrishiQuery
"""

import subprocess
import sys
from pathlib import Path

def run_tests():
    """Run all tests"""
    tests_passed = True
    
    # Run backend tests
    print("Running backend tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Backend tests failed:")
        print(result.stdout)
        print(result.stderr)
        tests_passed = False
    else:
        print("Backend tests passed!")
    
    # Run integration tests (if any)
    print("\nRunning integration tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", "tests/integration/", "-v"
    ], capture_output=True, text=True)
    
    if result.returncode != 0 and result.returncode != 5:  # 5 means no tests found
        print("Integration tests failed:")
        print(result.stdout)
        print(result.stderr)
        tests_passed = False
    elif result.returncode == 0:
        print("Integration tests passed!")
    else:
        print("No integration tests found.")
    
    return tests_passed

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)