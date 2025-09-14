# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Architecture

This is a full-stack credit card fraud detection dashboard with:

- **Backend**: FastAPI (Python 3.11) with machine learning fraud prediction
- **Frontend**: React + TypeScript with Vite and TailwindCSS
- **Database**: PostgreSQL with pgAdmin for management
- **Monitoring**: Prometheus, Grafana, and Loki stack
- **Infrastructure**: Docker Compose orchestration

### Backend Structure

The FastAPI backend follows a layered architecture:

- `backend/app/main.py`: FastAPI app entrypoint and root route
- `backend/app/routers/`: API route handlers (transactions, prediction)
- `backend/app/schemas/`: Pydantic models for request/response validation
- `backend/app/models/`: SQLAlchemy database models
- `backend/app/service/`: Business logic layer
- `backend/app/repositories/`: Data access layer
- `backend/app/settings/`: Configuration management (database, base settings)
- `backend/app/infra/`: Infrastructure concerns (logging, model loading)
- `backend/app/exception/`: Custom exception handling
- `backend/app/utils/`: Utility functions and helpers

### Frontend Structure

React SPA using modern TypeScript patterns:

- `frontend/src/App.tsx`: Main application component with routing
- `frontend/src/pages/`: Page components (Dashboard, Transactions, Agent)
- `frontend/src/components/`: Reusable UI components (Layout, Navbar, Lists, Cards)
- `frontend/src/style.css`: Global TailwindCSS styles

## Common Development Commands

### Backend (from `backend/` directory)

- **Install dependencies**: `uv sync` (or `uv sync --group dev` for dev deps)
- **Run development server**: `uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- **Run tests**: `uv run pytest -q`
- **Run tests with verbose output**: `uv run pytest -v`

### Frontend (from `frontend/` directory)

- **Install dependencies**: `npm install`
- **Run development server**: `npm run dev`
- **Build for production**: `npm run build`
- **Lint code**: `npm run lint`
- **Preview production build**: `npm run preview`

### Docker Development

- **Start all services**: `docker compose up --build`
- **Backend only**: `docker compose up backend postgres --build`
- **View logs**: `docker compose logs -f [service_name]`

## Development Environment Setup

### Prerequisites
- Python 3.11.13 (exact version specified in pyproject.toml)
- Node.js and npm for frontend
- Docker Desktop for containerized development
- `uv` package manager for Python dependencies

### Environment Configuration
- Copy `.env.example` to `.env` and configure database credentials
- Backend serves on port 8000 (local) or port 80 (Docker)
- Frontend serves on port 5173 (Vite default)
- PostgreSQL on port 5432, pgAdmin on port 5050
- Monitoring: Grafana (3000), Prometheus (9090), Loki (3100)

## Key Technologies

### Backend Stack
- FastAPI with async support
- SQLAlchemy 2.0 for ORM
- Pydantic v2 for data validation
- XGBoost and scikit-learn for ML models
- PostgreSQL with psycopg2
- pytest with asyncio support
- Prometheus instrumentation

### Frontend Stack
- React 19 with TypeScript
- Vite for build tooling
- TailwindCSS v4 for styling
- React Router for navigation
- ESLint for code quality

### Infrastructure
- Docker Compose with health checks
- Grafana/Prometheus/Loki observability stack
- Volume mounts for model artifacts (`./backend/models` → `/app/models`)

## Testing

Backend tests are located in `backend/tests/` and cover:
- API route handlers with FastAPI TestClient
- Service layer business logic
- Repository data access patterns

Run tests from the backend directory using pytest with the configured logging and path settings in `pytest.ini`.