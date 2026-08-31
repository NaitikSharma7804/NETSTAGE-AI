"""Unified Runner Script for NetSage AI Application."""

import sys
import os
import subprocess
import argparse
from pathlib import Path


def run_backend():
    """Launches FastAPI backend using Uvicorn."""
    print("🚀 Starting NetSage AI FastAPI Backend on http://127.0.0.1:8000 ...")
    cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"]
    subprocess.run(cmd)


def run_frontend():
    """Launches Streamlit dashboard."""
    print("🌐 Starting NetSage AI Streamlit Dashboard on http://127.0.0.1:8501 ...")
    dashboard_path = Path(__file__).parent / "dashboard" / "app.py"
    cmd = [sys.executable, "-m", "streamlit", "run", str(dashboard_path), "--server.port", "8501"]
    subprocess.run(cmd)


def main():
    parser = argparse.ArgumentParser(description="NetSage AI Application Runner")
    parser.add_argument("--backend", action="store_true", help="Run FastAPI backend server only")
    parser.add_argument("--frontend", action="store_true", help="Run Streamlit dashboard only")
    args = parser.parse_args()

    if args.backend:
        run_backend()
    elif args.frontend:
        run_frontend()
    else:
        print("⚡ Starting NetSage AI (Both Backend and Dashboard concurrently)...")
        # Launch backend in separate process
        backend_proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"])
        try:
            # Run frontend in main process
            run_frontend()
        finally:
            print("Shutting down backend process...")
            backend_proc.terminate()


if __name__ == "__main__":
    main()
