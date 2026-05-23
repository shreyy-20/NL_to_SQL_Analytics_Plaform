# KrishiQuery 🌾

### AI-Powered Agricultural Intelligence Platform for Indian Farmers

KrishiQuery is a multilingual, voice-enabled agricultural analytics platform designed to simplify access to farmer records, payment history, mandi prices, and soil health insights through natural language interactions.

Built with a scalable FastAPI + React architecture, the platform enables farmers and agricultural operators to query structured agricultural datasets using Hindi, Odia, or English — without requiring technical expertise.

Currently optimized with Odisha-focused sample datasets, the system demonstrates how AI-driven natural language interfaces can modernize rural agricultural workflows and government scheme accessibility.

---

# ✨ Key Features

## 🌐 Multilingual Natural Language Queries

Ask questions in:

* English
* Hindi
* Odia

Example:

> “Did my PM-KISAN installment arrive?”

The platform automatically:

1. Detects intent
2. Generates safe SQL queries
3. Retrieves structured data
4. Returns localized responses

---

## 🎙 Voice-Enabled Query System

Integrated voice workflow support using:

* Speech-to-Text (STT)
* Text-to-Speech (TTS)
* Optional IVR integrations

Supported through:

* Bhashini APIs
* Twilio IVR hooks

---

## 📊 Agricultural Data Intelligence

The platform provides access to:

* Farmer profile records
* Government payment history
* Soil health reports
* Mandi pricing insights
* Dashboard analytics

---

## 🔐 Secure AI-to-SQL Pipeline

KrishiQuery includes a protected natural language to SQL engine with:

* Intent classification
* SQL validation
* SELECT-only execution guardrails
* Safe runtime query handling

This prevents unsafe database mutations while enabling flexible querying capabilities.

---

# 🏗 System Architecture

```text
User Query (Voice/Text)
        │
        ▼
Intent Classification
        │
        ▼
AI SQL Generation
        │
        ▼
SQL Validation Layer
        │
        ▼
Database Execution
        │
        ▼
Localized Response Formatting
        │
        ▼
Frontend Dashboard / Voice Output
```

---

# 🚀 Tech Stack

## Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic
* Uvicorn

## Frontend

* React.js
* Axios

## Database

* SQLite
* PostgreSQL

## AI & Voice Services

* Bhashini APIs
* Twilio IVR
* Rule-based fallback NLP pipeline

## DevOps & Monitoring

* Docker
* GitHub Actions
* Redis
* Prometheus Metrics

---

# 📂 Repository Structure

```text
.
├── ai/                          # Intent classification & SQL generation
├── backend/
│   ├── api/                     # FastAPI route handlers
│   ├── models/                  # Pydantic schemas
│   ├── services/                # ORM models & business logic
│   ├── config.py                # Environment configuration
│   └── main.py                  # FastAPI entrypoint
├── frontend/                    # React frontend application
├── voice/                       # Bhashini & Twilio integrations
├── data/
│   ├── databases/schema.sql
│   └── sample_data/             # Odisha-focused seed datasets
├── scripts/
│   ├── setup_database.py
│   ├── seed_data.py
│   └── run_tests.py
├── deployment/                  # Docker & deployment assets
└── .github/workflows/ci.yml
```

---

# ⚡ Quick Start

## 1️⃣ Clone Repository

```bash
git clone https://github.com/shreyy-20/NL_to_SQL_Analytics_Plaform.git
cd NL_to_SQL_Analytics_Plaform
```

---

## 2️⃣ Create Virtual Environment

### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Configure Environment Variables

```powershell
Copy-Item .env.example .env
```

Update required variables:

```env
DATABASE_URL=
API_KEY=
JWT_SECRET_KEY=
ENVIRONMENT=development
```

---

## 5️⃣ Initialize Database

```bash
python scripts/setup_database.py --drop
python scripts/seed_data.py
```

---

## 6️⃣ Start Backend Server

```powershell
.\start_backend.ps1 -Reload
```

Backend runs at:

```text
http://127.0.0.1:8000
```

---

## 7️⃣ Start Frontend

```bash
cd frontend
npm install
npm start
```

Frontend runs at:

```text
http://localhost:3000
```

---

# 📡 API Endpoints

## Core APIs

| Endpoint         | Description                   |
| ---------------- | ----------------------------- |
| `/api/farmers`   | Farmer records                |
| `/api/queries`   | Natural language query engine |
| `/api/dashboard` | Dashboard analytics           |
| `/api/voice`     | Voice APIs                    |

---

## Platform Endpoints

| Endpoint       | Purpose            |
| -------------- | ------------------ |
| `GET /`        | Service metadata   |
| `GET /health`  | Health monitoring  |
| `GET /metrics` | Prometheus metrics |

---

## Example Query Request

```bash
curl -X POST "http://127.0.0.1:8000/api/queries/" \
-H "Content-Type: application/json" \
-d '{
  "question": "Did my PM-KISAN installment come?",
  "phone_number": "9876543210",
  "language": "en"
}'
```

---

# 🐳 Docker Deployment

Run the full platform using Docker Compose:

```bash
docker compose -f deployment/docker-compose.yml up --build
```

This provisions:

* FastAPI backend
* React frontend
* PostgreSQL
* Redis
* Optional reverse proxy

---

# ☁ Deployment on Render

The repository includes a ready-to-deploy `render.yaml` blueprint.

## Deployment Steps

1. Push repository to GitHub
2. Open Render Blueprint deploy
3. Create Render services
4. Wait for deployment completion

Generated services:

* `krishiquery-backend`
* `krishiquery-frontend`

---

# 🔄 CI/CD Pipeline

GitHub Actions workflow automatically:

* Installs dependencies
* Validates builds
* Runs project tests on push

Workflow file:

```text
.github/workflows/ci.yml
```

---

# 📈 Monitoring & Observability

KrishiQuery includes:

* Health monitoring APIs
* Prometheus metrics endpoint
* Redis cache support
* Runtime validation systems

Metrics endpoint:

```text
/metrics
```

---

# 🛡 Security Features

* SQL Injection prevention
* SELECT-only SQL execution
* Runtime query validation
* Environment-based secret management
* CORS & host restrictions

---

# 🧪 Developer Utilities

| Script              | Purpose               |
| ------------------- | --------------------- |
| `setup_database.py` | Create/reset database |
| `seed_data.py`      | Load seed datasets    |
| `run_tests.py`      | Execute tests         |
| `start_backend.ps1` | Backend launcher      |

---

# ⚠ Notes

* Voice and IVR modules are disabled by default.
* Free-tier deployments may enter sleep mode when idle.
* SQLite is recommended only for local development.
* PostgreSQL is recommended for production deployments.

---

# 🔧 Troubleshooting

## Backend Not Starting

* Verify `.env` configuration
* Validate `DATABASE_URL`
* Re-run database setup scripts

---

## Frontend Cannot Connect to Backend

Ensure:

* Backend runs on port `8000`
* Frontend runs on port `3000`

---

## Git Changes Not Reflecting

```bash
git add .
git commit -m "Update"
git push origin main
```

---

# 🌱 Future Enhancements

* Real AI/LLM-powered query generation
* Regional language expansion
* Live mandi API integrations
* Farmer recommendation engine
* Mobile application support
* AI-based crop advisory system

---

# 📜 License

This repository currently does not include a license file.

---

# 👨‍💻 Author

Developed as an AI-powered agricultural analytics solution focused on improving accessibility, transparency, and operational efficiency in Indian agricultural ecosystems.
