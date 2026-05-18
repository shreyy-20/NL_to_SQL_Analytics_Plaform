# KrishiQuery

Voice-based natural language query system for Indian agriculture (Odisha focus).

## What it does

- PM-KISAN and KALIA payment status lookups
- Mandi price lookups
- Soil health report lookups
- Weather and dashboard APIs

## Backend stack

- FastAPI
- SQLAlchemy
- SQLite/PostgreSQL
- Optional AI fallback for intent classification

## Quick start (Windows)

1. Create/activate virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Configure environment:

```powershell
Copy-Item .env.example .env
```

If your project is inside OneDrive, keep `DATABASE_URL` in `.env` pointed to a local temp path (already set in `.env.example`) to avoid SQLite file-lock I/O issues.

4. Initialize database and seed sample data:

```powershell
python scripts/setup_database.py --drop
python scripts/seed_data.py
```

5. Run API server:

```powershell
.\start_backend.ps1
```

6. Verify:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

## Useful scripts

- `fix_versions.py` - dependency repair/check script
- `start_backend.ps1` - always runs backend with the project `venv` interpreter
- `complete_setup.py` - wrapper for DB setup + seeding
- `create_tables.py` - wrapper for DB table recreation
