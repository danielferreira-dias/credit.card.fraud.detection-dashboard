# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Architecture

This is a full-stack credit card fraud detection dashboard with AI agent capabilities:

- **Backend**: FastAPI (Python 3.11) with machine learning fraud prediction
- **Agent Service**: FastAPI (Python 3.11) with LangGraph and Azure OpenAI integration
- **Frontend**: React + TypeScript with Vite and TailwindCSS
- **Database**: PostgreSQL with pgAdmin for management
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

### Agent Service Structure

The Agent Service is a separate FastAPI service for AI-powered fraud analysis:

- `agent-service/src/app/main.py`: FastAPI app entrypoint with WebSocket support
- `agent-service/src/app/agents/`: LangGraph agent implementation (TransactionAgent)
- `agent-service/src/app/services/`: Backend API client for fetching transaction data
- `agent-service/src/app/schemas/`: Agent prompts and Pydantic models
- `agent-service/src/app/database/`: Database models and repositories for chat history
- `agent-service/src/app/tools/`: LangChain tools for agent capabilities
- `agent-service/infra/`: Infrastructure concerns (logging, exceptions)

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

### Agent Service (from `agent-service/` directory)

- **Install dependencies**: `uv sync` (or `uv sync --group dev` for dev deps)
- **Run development server**: `uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8001`
- **Run tests**: `uv run pytest -q`

### Frontend (from `frontend/` directory)

- **Install dependencies**: `npm install`
- **Run development server**: `npm run dev`
- **Build for production**: `npm run build`
- **Lint code**: `npm run lint`
- **Preview production build**: `npm run preview`

### Docker Development

- **Start all services**: `docker compose up --build`
- **Backend only**: `docker compose up backend postgres --build`
- **Agent service only**: `docker compose up agent-service postgres backend --build`
- **View logs**: `docker compose logs -f [service_name]`

## Development Environment Setup

### Prerequisites
- Python 3.11.13 (exact version specified in pyproject.toml)
- Node.js and npm for frontend
- Docker Desktop for containerized development
- `uv` package manager for Python dependencies

### Environment Configuration
- Copy `.env.example` to `.env` and configure:
  - Database credentials (PostgreSQL)
  - Azure OpenAI credentials (for agent service)
  - LangSmith API key (for agent tracing/monitoring)
- **Service Ports**:
  - Backend: port 8000 (local) or port 80 (Docker)
  - Agent Service: port 8001
  - Frontend: port 5173 (Vite default)
  - PostgreSQL: port 5432
  - pgAdmin: port 5050

## Key Technologies

### Backend Stack
- FastAPI with async support
- SQLAlchemy 2.0 for ORM
- Pydantic v2 for data validation
- XGBoost and scikit-learn for ML models
- PostgreSQL with psycopg2
- pytest with asyncio support
- Prometheus instrumentation

### Agent Service Stack
- FastAPI with WebSocket support
- LangGraph for agent orchestration
- LangChain with Azure OpenAI integration
- PostgreSQL for chat history persistence
- LangSmith for agent tracing and monitoring
- In-memory and PostgreSQL checkpointing

### Frontend Stack
- React 19 with TypeScript
- Vite for build tooling
- TailwindCSS v4 for styling
- React Router for navigation
- ESLint for code quality

### Infrastructure
- Docker Compose with health checks and multi-service networking
- PostgreSQL shared across backend and agent service
- Volume mounts for hot-reloading during development
- Service-to-service communication (backend ↔ agent-service)

## Testing

### Backend Tests
Located in `backend/tests/` and cover:
- API route handlers with FastAPI TestClient
- Service layer business logic
- Repository data access patterns

Run tests from the backend directory using pytest with the configured logging and path settings in `pytest.ini`.

### Agent Service Tests
Can be run from the `agent-service/` directory using pytest (structure may vary based on current implementation).

## Key Features

### Transaction Fraud Detection
- Real-time fraud prediction using XGBoost ML model
- Transaction history tracking and analysis
- REST API endpoints for transaction management

### AI Agent Chat Interface
- WebSocket-based real-time chat with AI agent
- LangGraph-powered reasoning and tool use
- Access to transaction data through backend API integration
- Chat history persistence with PostgreSQL
- Reasoning steps tracking for transparency

### Frontend Dashboard
- Dashboard with fraud statistics and visualizations
- Transaction list and detail views
- Interactive agent chat interface with message history
- Real-time updates via WebSocket connection