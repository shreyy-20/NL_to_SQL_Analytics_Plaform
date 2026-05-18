"""Legacy wrapper: create DB tables using the canonical setup script."""

import subprocess
import sys


def main() -> None:
    subprocess.run([sys.executable, "scripts/setup_database.py", "--drop"], check=True)
    print("Tables created successfully.")


if __name__ == "__main__":
    main()
