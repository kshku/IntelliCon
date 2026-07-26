# IntelliCon

Conversational AI platform for the Karnataka State Police (KSP) Crime Database. An intelligent assistant that lets investigators query, analyze, and visualize crime data using natural language — in English and Kannada.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 Frontend (React + Vite)                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐ │
│  │ Chat UI  │ │Dashboard │ │Network   │ │ PDF Export │ │
│  │          │ │(Trends,  │ │Graph View│ │            │ │
│  │          │ │ Hotspots)│ │(Neo4j)   │ │            │ │
│  └──────────┘ └──────────┘ └──────────┘ └────────────┘ │
└─────────────────────┬───────────────────────────────────┘
                      │ REST / WebSocket
┌─────────────────────┴───────────────────────────────────┐
│                   Backend (FastAPI)                       │
│  ┌─────────────────────────────────────────────────────┐ │
│  │             LangGraph ReAct Agent                    │ │
│  │    reason → tool call → observe → reason → ...       │ │
│  ├─────────────────────────────────────────────────────┤ │
│  │  Skill Index (always in context)                     │ │
│  │  Skill Loader (full content on demand)               │ │
│  ├─────────────────────────────────────────────────────┤ │
│  │  Tools:                                              │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐            │ │
│  │  │SQL Query │ │Graph     │ │Chart     │            │ │
│  │  │(Postgres)│ │(Neo4j)   │ │(Plotly)  │            │ │
│  │  └──────────┘ └──────────┘ └──────────┘            │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐            │ │
│  │  │Analytics │ │PDF       │ │Voice     │            │ │
│  │  │Fetch     │ │Export    │ │(STT/TTS) │            │ │
│  │  └──────────┘ └──────────┘ └──────────┘            │ │
│  └─────────────────────────────────────────────────────┘ │
└──────┬──────────┬──────────┬────────────────────────────┘
       │          │          │
  ┌────┴───┐ ┌───┴────┐ ┌──┴──────┐
  │Postgres│ │ Neo4j  │ │ Redis   │
  │(FIR    │ │(Graph  │ │(Session │
  │ Data)  │ │ Data)  │ │ Cache)  │
  └────────┘ └────────┘ └─────────┘
       ↑
  ┌────┴──────────────┐
  │ Cron Analytics    │
  │ (hotspots, trends,│
  │  predictions)     │
  └───────────────────┘
```

### Core Design Principles

- **Single agent, many tools** — One LangGraph ReAct agent reasons over composable tools. Not multi-agent — one reasoning loop, one context, lower latency.
- **Skills as loaded context** — Modular `.md` files with YAML frontmatter define investigation workflows. Agent loads a lightweight index always, full skill content on demand.
- **Pre-computed analytics** — Hotspot detection, trend analysis, and predictive scoring run as batch jobs. The agent fetches and explains results — it doesn't compute them live.
- **Audit by default** — Every reasoning step, tool call, and SQL query is logged. Explainability comes free from the tool trace.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Agent** | LangGraph (ReAct pattern) |
| **LLM** | Provider-agnostic (OpenAI, Anthropic, Gemini — configurable via env vars) |
| **Backend** | Python 3.11+ / FastAPI |
| **Frontend** | React 18 / Vite / TypeScript / Tailwind CSS |
| **Primary DB** | PostgreSQL (FIR data, ~25 tables) |
| **Graph DB** | Neo4j (criminal networks, connections) |
| **Cache** | Redis (sessions, conversation history) |
| **Analytics** | APScheduler (cron jobs) / statsmodels / Prophet |
| **Visualization** | Plotly.js (charts) / D3.js (network graphs) / Leaflet (maps) |
| **Voice** | Web Speech API (browser) / OpenAI Whisper (fallback) |
| **PDF** | WeasyPrint / ReportLab |
| **Deployment** | Docker Compose (self-hosted) |

## Project Structure

```
IntelliCon/
├── backend/                    # Python (FastAPI + LangGraph)
│   ├── app/
│   │   ├── agent/             # LangGraph ReAct agent
│   │   │   ├── core.py        # Agent loop, state management
│   │   │   ├── llm.py         # Provider-agnostic LLM wrapper
│   │   │   └── state.py       # Agent state schema
│   │   ├── tools/             # Tool registry + individual tools
│   │   │   ├── registry.py    # Tool registration and discovery
│   │   │   ├── sql_query.py   # Text-to-SQL tool
│   │   │   ├── graph_query.py # Neo4j Cypher tool
│   │   │   ├── chart.py       # Chart generation tool
│   │   │   ├── analytics.py   # Pre-computed analytics fetch
│   │   │   ├── pdf_export.py  # PDF generation tool
│   │   │   └── voice.py       # STT/TTS tool
│   │   ├── skills/            # Skills (YAML frontmatter + markdown)
│   │   │   ├── index.py       # Skill index generator
│   │   │   ├── loader.py      # On-demand skill loader
│   │   │   └── *.md           # Individual skill files
│   │   ├── api/               # FastAPI routes
│   │   │   ├── chat.py        # Chat endpoint (WebSocket)
│   │   │   ├── analytics.py   # Analytics data endpoints
│   │   │   ├── auth.py        # Authentication endpoints
│   │   │   └── audit.py       # Audit trail endpoints
│   │   ├── db/                # Database layer
│   │   │   ├── postgres.py    # PostgreSQL connection
│   │   │   ├── neo4j.py       # Neo4j connection
│   │   │   └── redis.py       # Redis connection
│   │   ├── models/            # SQLAlchemy/Pydantic models
│   │   ├── auth/              # JWT auth, RBAC
│   │   └── config.py          # Settings (env vars)
│   ├── migrations/            # Alembic migrations
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # React + Vite
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Route pages (chat, dashboard, network)
│   │   ├── hooks/             # Custom React hooks
│   │   ├── stores/            # Zustand state management
│   │   ├── api/               # Backend API client
│   │   ├── i18n/              # Internationalization (en, kn)
│   │   └── utils/
│   ├── package.json
│   └── Dockerfile
├── analytics/                  # Batch analytics pipelines
│   ├── pipelines/
│   │   ├── hotspots.py        # Crime hotspot detection (DBSCAN)
│   │   ├── trends.py          # Crime trend analysis
│   │   └── predictions.py     # Predictive analytics
│   ├── scheduler.py           # APScheduler config
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Database Schema

The system is built on the Karnataka Police FIR database with ~25 tables centered on `CaseMaster`:

### Core Tables
- **CaseMaster** — Central case/FIR records with dates, locations, status, crime classification
- **ComplainantDetails** — Complainant information (name, age, occupation, religion, caste)
- **Victim** — Victim records linked to cases
- **Accused** — Accused persons with case linkage
- **ArrestSurrender** — Arrest/surrender events with court and IO references
- **ActSectionAssociation** — Legal acts and sections invoked per case
- **ChargesheetDetails** — Chargesheet filings (Chargesheet / False Case / Undetected)

### Reference Tables
- **Act**, **Section** — Legal framework
- **CrimeHead**, **CrimeSubHead** — Crime classification hierarchy
- **CaseCategory**, **GravityOffence**, **CaseStatusMaster** — Case metadata
- **CasteMaster**, **ReligionMaster**, **OccupationMaster** — Demographics

### Geography
- **State** → **District** → **Unit** (Police Station) hierarchy
- **Court** linked to districts

### Personnel
- **Employee** with **Rank** and **Designation**

See `data/Police_FIR_ER_Diagram.pdf` for the complete ER diagram with all columns and relationships.

## Features

### Phase 1: Core Agent & Infrastructure
- Natural language querying against the FIR database (Text-to-SQL)
- LangGraph ReAct agent with composable tools
- Skill system for investigation workflows
- Chat interface with streaming responses
- Provider-agnostic LLM support

### Phase 2: Graph & Network Analysis
- Criminal network visualization (Neo4j + D3.js)
- Connection discovery (co-accused, shared cases)
- Multi-hop network traversal

### Phase 3: Analytics Dashboard
- Crime hotspot detection (DBSCAN clustering)
- Crime trend analysis (monthly counts, YoY comparison)
- Dashboard with charts, maps, and key metrics

### Phase 4: Advanced Features
- Voice interaction (English + Kannada)
- PDF export of investigation reports
- Role-based access control (Investigator / Supervisor / Admin)
- Predictive analytics (crime forecasting, recidivism scoring)
- Explainable AI with full audit trails
- Kannada language support

## Getting Started

### Prerequisites
- Docker Engine with the Docker Compose plugin (`docker compose version`)
- Git

### Run with Docker Compose

Docker Compose starts the frontend, backend, analytics service, PostgreSQL,
Neo4j, and Redis. PostgreSQL, Neo4j, and Redis data are stored in named Docker
volumes, so they persist when the stack is stopped.

```bash
# Clone the repository
git clone git@github.com:kshku/IntelliCon.git
cd IntelliCon

# Create your local environment configuration
cp .env.example .env

# Set a strong JWT secret and the API key for the selected LLM provider.
# Do not use the placeholder values from .env.example in a real environment.
# You can generate secrets with: python -c "import secrets; print(secrets.token_hex(32))"
nano .env

# Build the application images and start the full stack in the background
docker compose up --build -d

# Confirm that the services are running
docker compose ps
```

Database migrations run automatically on backend startup. The backend will not report as healthy until all migrations are complete.

The first build can take a few minutes while Docker downloads base images and
installs dependencies. Once the services are ready, open:

- Frontend: <http://localhost:3000>
- Backend health check: <http://localhost:8000/health>

To follow startup logs or stop the stack:

```bash
# Follow logs from all services, or replace with a service name (for example, backend)
docker compose logs -f

# Stop containers while keeping database data
docker compose down

# Stop containers and permanently remove the named data volumes
docker compose down -v
```

`docker compose down -v` deletes the local PostgreSQL, Neo4j, and Redis data.
Use it only when a clean local environment is intended.

### Exposed Ports

Only the frontend and backend are exposed to the host. Data services
(PostgreSQL, Neo4j, Redis) are internal to the Docker network and are **not**
accessible from the host by default.

| Port | Service | Purpose |
|------|---------|---------|
| 3000 | Frontend | React UI |
| 8000 | Backend | FastAPI REST API |

To temporarily expose a data service for debugging (e.g., connecting a local
client), override the port mapping:

```bash
docker compose up -d postgres
docker compose run --rm -p 5432:5432 postgres
```

### Secrets

All credentials must be set in `.env` before running `docker compose up`. The
stack will refuse to start if any required secret is missing. See `.env.example`
for the full list. **Do not use placeholder values in production.**

### Configuration

Key environment variables (see `.env.example` for full list):

| Variable | Description | Default |
|----------|-------------|---------|
| `JWT_SECRET_KEY` | HMAC key for JWT signing | — (required) |
| `LLM_PROVIDER` | LLM provider (`openai`, `anthropic`, `gemini`) | `openai` |
| `LLM_MODEL` | Model name | `gpt-4o` |
| `LLM_API_KEY` | API key for the chosen provider | — |
| `POSTGRES_PASSWORD` | PostgreSQL password | — (required) |
| `NEO4J_PASSWORD` | Neo4j password | — (required) |
| `REDIS_PASSWORD` | Redis password | — (required) |
| `DATABASE_URL` | PostgreSQL connection string | — (set by compose) |
| `NEO4J_URI` | Neo4j connection URI | `bolt://localhost:7687` |
| `REDIS_URL` | Redis connection string | — (set by compose) |

## Development

```bash
# Backend (with hot-reload)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (with hot-reload)
cd frontend
npm install
npm run dev

# Analytics scheduler
cd analytics
python scheduler.py
```

## Production Deployment

### HTTPS Setup

The production deployment uses Caddy as an edge proxy for TLS termination.

1. Set your domain and email in `.env`:

```bash
DOMAIN=your-domain.com
ACME_EMAIL=your-email@domain.com
CORS_ORIGINS=["https://your-domain.com"]
```

2. Start the stack:

```bash
docker compose up -d
```

Caddy will automatically provision a TLS certificate via Let's Encrypt and redirect all HTTP traffic to HTTPS.

### TLS Certificate Provisioning

Caddy handles certificate provisioning and renewal automatically:

- **Automatic (Let's Encrypt):** When `DOMAIN` is set to a real domain, Caddy requests a certificate via ACME HTTP-01 challenge, stores it in the `caddy_data` volume, and auto-renews before expiry.
- **Local development:** When `DOMAIN=localhost` (default), Caddy uses its internal CA for self-signed certificates. Browsers will show a warning — this is expected.
- **Custom certificates:** Mount certificate files and update the Caddyfile with a `tls` directive:

```caddyfile
example.com {
    tls /certs/cert.pem /certs/key.pem
    # ... rest of config
}
```

### Rate Limits

| Route | Limit | Window |
|-------|-------|--------|
| All (global) | 100 requests | 1 minute |
| `/api/*` | 30 requests | 1 minute |
| `/api/chat/ws` | None (WebSocket) | — |

### Forwarded Headers

Caddy sets the following headers on all proxied requests:

- `X-Forwarded-For`: Client IP address
- `X-Forwarded-Proto`: Original protocol (http/https)
- `X-Forwarded-Host`: Original host header

These headers are set by Caddy and passed through the Nginx reverse proxy to the backend.

### Exposed Ports

| Port | Service | Purpose |
|------|---------|---------|
| 80 | Caddy | HTTP (redirects to HTTPS) |
| 443 | Caddy | HTTPS (production) |

All other services (frontend, backend, databases) are internal to the Docker network and not directly accessible from the host.
