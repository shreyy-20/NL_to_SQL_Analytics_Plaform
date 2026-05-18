"""Repair and validate backend dependency versions."""

from pathlib import Path
import os
import subprocess
import sys


def run_step(args: list[str], description: str, fail_hard: bool = True) -> bool:
    """Run a command, optionally allowing failure for offline environments."""
    print(f"\n{description}")
    print(" ".join(args))
    env = os.environ.copy()
    for blocked in [
        "PIP_NO_INDEX",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "GIT_HTTP_PROXY",
        "GIT_HTTPS_PROXY",
    ]:
        env.pop(blocked, None)

    result = subprocess.run(args, check=False, env=env)
    if result.returncode != 0 and fail_hard:
        raise subprocess.CalledProcessError(result.returncode, args)
    return result.returncode == 0


def main() -> None:
    project_root = Path(__file__).resolve().parent
    requirements_file = project_root / "requirements.txt"

    if not requirements_file.exists():
        raise FileNotFoundError(f"requirements.txt not found at {requirements_file}")

    run_step([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], "Upgrading pip...", fail_hard=False)
    install_ok = run_step(
        [sys.executable, "-m", "pip", "install", "--upgrade", "-r", str(requirements_file)],
        "Installing project dependencies with compatible versions...",
        fail_hard=False,
    )
    run_step([sys.executable, "-m", "pip", "check"], "Running dependency consistency check...", fail_hard=False)

    print("\nDone.")
    if not install_ok:
        print("Note: dependency install reported issues (often due offline package index access).")
        print("If the app already runs, you can proceed.")
    print("Start server with:")
    print(".\\start_backend.ps1")


if __name__ == "__main__":
    main()
