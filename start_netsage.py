"""
NetSage AI Unified Service Launcher.
Launches both FastAPI Backend (Port 8000) and Streamlit Dashboard (Port 8501) simultaneously.
"""

import os
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main():
    print("""
================================================================================
                     STARTING NETSAGE AI SERVICES
================================================================================
    """)

    # 1. Initialize SQLite Database
    print("[1/3] Initializing and seeding SQLite database...")
    subprocess.run([sys.executable, "scripts/seed_db.py"], check=True)

    # 2. Launch FastAPI in subprocess
    print("[2/3] Starting FastAPI Backend on http://127.0.0.1:8000 ...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    time.sleep(2)

    # 3. Launch Streamlit UI
    print("[3/3] Starting Streamlit Dashboard on http://localhost:8501 ...")
    print("\nPress Ctrl+C to stop all services.\n")

    try:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", "dashboard/app.py", "--server.port", "8501", "--server.headless", "true"]
        )
    except KeyboardInterrupt:
        print("\nStopping services...")
    finally:
        backend_proc.terminate()
        print("NetSage AI shutdown cleanly.")


if __name__ == "__main__":
    main()