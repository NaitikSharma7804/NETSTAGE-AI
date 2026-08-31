# NetSage AI - Setup & Installation Guide

## Prerequisites
- Python 3.10+ (Tested on Python 3.10, 3.11, 3.12, 3.14)
- Git (optional)
- Modern web browser

## 1. Environment Setup
Clone or navigate to the repository directory:
```bash
cd c:\cisco
```

Create and activate a virtual environment (optional if using global Python):
```bash
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## 2. Environment Variables Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Configuration Options in `.env`:
```ini
# Operating mode: development | production | test
APP_ENV=development

# Database URL (SQLite default)
DATABASE_URL=sqlite:///./netsage.db

# LLM Configuration
# Options: mock | gemini | openai | anthropic | local
LLM_PROVIDER=mock
LLM_MODEL=mock-netsage-v1
LLM_API_KEY=

# Demo Mode: Set to true for 100% offline operation without API keys
DEMO_MODE=true
```

## 3. Database Initialization
Seed the SQLite database with 40 canonical troubleshooting cases and historical reviews:
```bash
python scripts/seed_db.py
```

## 4. Running the Application

### Start the FastAPI Backend:
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive Swagger API documentation will be available at: `http://127.0.0.1:8000/docs`

### Start the Streamlit Dashboard:
```bash
streamlit run dashboard/app.py --server.port 8501
```
The dashboard interface will open at: `http://localhost:8501`