#!/usr/bin/env python3
"""
Test runner for KrishiQuery
"""

import subprocess
import sys
from pathlib import Path

def _run_pytest(target: str, label: str) -> bool:
    """Run pytest for a target path and treat missing/empty suites as non-fatal."""
    path = Path(target)
    if not path.exists():
        print(f"{label} skipped: '{target}' not found.")
        return True

    print(f"Running {label}...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", target, "-v", "--tb=short"],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print(f"{label} passed!")
        return True

    # Pytest exit code 5: no tests collected.
    if result.returncode == 5:
        print(f"{label} skipped: no tests collected.")
        return True

    print(f"{label} failed:")
    print(result.stdout)
    print(result.stderr)
    return False


def run_tests():
    """Run test suites and return True only when all required suites pass."""
    backend_ok = _run_pytest("tests", "backend tests")
    print()
    integration_ok = _run_pytest("tests/integration", "integration tests")
    return backend_ok and integration_ok

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
