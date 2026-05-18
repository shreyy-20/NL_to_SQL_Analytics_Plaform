"""Legacy wrapper: full setup using canonical scripts."""

import subprocess
import sys


def main() -> None:
    subprocess.run([sys.executable, "scripts/setup_database.py", "--drop"], check=True)
    subprocess.run([sys.executable, "scripts/seed_data.py"], check=True)
    print("Setup complete. Start server with:")
    print("python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000")


if __name__ == "__main__":
    main()
