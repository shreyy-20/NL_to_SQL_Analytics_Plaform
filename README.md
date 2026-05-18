# KrishiQuery

KrishiQuery is a voice-enabled natural language query platform for Indian agriculture workflows (currently Odisha-focused sample data). It lets users query farmer records, payment history, mandi prices, and soil health using Hindi, Odia, or English inputs.

## Live Demo (Public)

This repository now includes a Render Blueprint at `render.yaml`, so you can publish a public demo website from GitHub.

Deploy button:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/shreyy-20/NL_to_SQL_Analytics_Plaform)

After first deploy, share these links with anyone:

- Frontend demo URL: `https://<your-frontend-service>.onrender.com`
- API docs URL: `https://<your-backend-service>.onrender.com/docs`

Notes:

- Free-tier services can sleep when idle and take ~30-60 seconds to wake up.
- Voice/IVR are disabled by default in this demo deployment.

## What This Project Includes

- FastAPI backend with modular API routers
- SQLAlchemy data access layer with SQLite/PostgreSQL support
- Natural language query pipeline:
  - intent classification
  - SQL generation
  - safe SQL execution (SELECT-only guardrails)
  - localized response formatting
- Optional voice services (Bhashini STT/TTS) and IVR hooks (Twilio)
- React frontend for dashboard, farmer search, and query interaction
- Docker assets for local containerized deployment
- GitHub Actions CI workflow for basic validation on push

## Tech Stack

- Backend: Python, FastAPI, SQLAlchemy, Pydantic, Uvicorn
- Data: SQLite (default local) or PostgreSQL (container/production path)
- Frontend: React (Create React App), Axios
- Optional integrations: Redis, Bhashini, Twilio
- Monitoring: Prometheus metrics endpoint (`/metrics`)
- CI: GitHub Actions (`.github/workflows/ci.yml`)

## Repository Structure

```text
.
|-- ai/                         # Intent + SQL generation helpers
|-- backend/
|   |-- api/                    # FastAPI routers
|   |-- models/                 # Pydantic models
|   |-- services/               # ORM models + business logic
|   |-- config.py               # Environment-driven settings
|   `-- main.py                 # FastAPI entrypoint
|-- voice/                      # Bhashini/Twilio wrappers
|-- frontend/                   # React app
|-- data/
|   |-- databases/schema.sql
|   `-- sample_data/            # Odisha-focused seed CSVs
|-- scripts/
|   |-- setup_database.py
|   |-- seed_data.py
|   `-- run_tests.py
|-- deployment/                 # Dockerfiles + compose + nginx config
`-- .github/workflows/ci.yml
```

## Quick Start (Windows PowerShell)

1. Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install backend dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Create your local environment file:

```powershell
Copy-Item .env.example .env
```

4. Initialize and seed the database:

```powershell
python scripts/setup_database.py --drop
python scripts/seed_data.py
```

5. Start backend:

```powershell
.\start_backend.ps1 -Reload
```

6. In a new terminal, start frontend:

```powershell
cd frontend
npm install
npm start
```

7. Open:

- API docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`
- Frontend: `http://localhost:3000`

## API Overview

Base API groups:

- `/api/farmers`
- `/api/queries`
- `/api/dashboard`
- `/api/voice`

Platform endpoints:

- `GET /` basic service metadata
- `GET /health` health check (database/model/redis status)
- `GET /metrics` Prometheus metrics

Key examples:

- `GET /api/farmers/{phone}`
- `GET /api/farmers/{farmer_id}/payments`
- `GET /api/farmers/{farmer_id}/soil-health`
- `POST /api/queries/`
- `GET /api/dashboard/stats`
- `POST /api/voice/stt` (when voice is enabled)

Example query request:

```bash
curl -X POST "http://127.0.0.1:8000/api/queries/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Did my PM-KISAN installment come?",
    "phone_number": "9876543210",
    "language": "en"
  }'
```

## Configuration

Primary settings are loaded from `.env` via `backend/config.py`.

Important variables:

- `DATABASE_URL` required, defaults to local SQLite in `.env.example`
- `API_KEY` required
- `JWT_SECRET_KEY` required
- `ENVIRONMENT` `development` or `production`
- `DEBUG` `true`/`false`
- `CORS_ORIGINS` JSON array or comma-separated list
- `ALLOWED_HOSTS` JSON array or comma-separated list
- `ENABLE_VOICE` toggle voice APIs
- `ENABLE_IVR` toggle IVR APIs
- `REDIS_URL` optional cache backend
- `BHASHINI_API_KEY` optional for live STT/TTS
- `TWILIO_*` optional for IVR calling

## Running with Docker Compose

From repository root:

```bash
docker compose -f deployment/docker-compose.yml up --build
```

This composes:

- PostgreSQL
- Redis
- FastAPI backend
- Frontend (Nginx container)
- Optional reverse proxy service

Before production-style runs, set secure values for DB credentials and secrets in environment variables.

## Deploy on Render

1. Push latest code to GitHub (including `render.yaml`).
2. Open the Deploy to Render button above.
3. Select your Render workspace and create resources.
4. Wait for first deploy to finish for both services:
   - `krishiquery-backend`
   - `krishiquery-frontend`
5. Open the frontend `.onrender.com` URL and test the demo.

The Blueprint provisions:

- Public static frontend service
- Public FastAPI backend service
- Managed Postgres database
- Automatic DB setup and sample data seeding on backend startup

## CI/CD

GitHub Actions workflow: `.github/workflows/ci.yml`

Current behavior on push to `main`:

1. Checkout source
2. Set up Python 3.10
3. Install `requirements.txt`
4. Run `python scripts/run_tests.py`

## Developer Utilities

- `scripts/setup_database.py` create/drop tables
- `scripts/seed_data.py` load sample CSV data
- `complete_setup.py` legacy wrapper for setup + seed
- `create_tables.py` legacy wrapper for table recreation
- `start_backend.ps1` standard backend launcher using project `venv`

## Notes and Operational Guidance

- Voice and IVR are disabled by default in `.env.example`.
- If intent model files are not present, the app falls back to rule-based intent handling.
- SQL generation includes validator checks and runtime SELECT-only safety guards.
- If your repo is inside OneDrive, keep SQLite DB files in a non-synced temp path (as shown in `.env.example`) to reduce lock conflicts.

## Troubleshooting

- `git push` says up-to-date but changes are missing:
  - run `git add .`
  - run `git commit -m "your message"`
  - run `git push origin main`
- Backend fails to start:
  - verify `.env` exists
  - verify `DATABASE_URL`
  - run `python scripts/setup_database.py --drop` again
- Frontend cannot reach backend:
  - ensure backend is on port `8000`
  - ensure frontend runs from `frontend/` on port `3000`

## License

No license file is currently included in this repository.
