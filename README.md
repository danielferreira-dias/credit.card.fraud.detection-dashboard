# Credit Card Fraud Detection Dashboard

A full-stack fraud detection platform featuring real-time transaction monitoring, ML-powered fraud prediction, and an intelligent AI agent for interactive data analysis. The system combines a FastAPI backend with machine learning capabilities and a modern React frontend with real-time chat functionality.

This repository ships both the FastAPI backend and React frontend, with WebSocket-based real-time communication and an integrated AI agent service for natural language queries about fraud data.

## Tech Stack

### Backend
- **FastAPI** (Python 3.11) with async support
- **SQLAlchemy 2.0** for ORM with PostgreSQL
- **XGBoost & scikit-learn** for ML fraud detection
- **WebSocket** support for real-time agent communication
- **Azure OpenAI** for LLM-powered agent capabilities
- **LangChain & LangGraph** for agent workflow orchestration
- **uv** package manager with `pyproject.toml` + `uv.lock`
- **pytest** with asyncio support for testing

### Frontend
- **React 19** with TypeScript
- **Vite** for build tooling and development
- **TailwindCSS v4** for modern styling
- **WebSocket** integration for real-time chat
- **React Router** for navigation

### Infrastructure
- **Docker Compose** orchestration
- **PostgreSQL** with pgAdmin for database management
- **Azure AI Services** for enterprise-grade AI capabilities
- **Agent Service** powered by LangChain/LangGraph workflows

## Project Architecture

This is a full-stack credit card fraud detection dashboard with:

- **Backend**: FastAPI (Python 3.11) with machine learning fraud prediction
- **Frontend**: React + TypeScript with Vite and TailwindCSS
- **Database**: PostgreSQL with pgAdmin for management
- **Infrastructure**: Docker Compose orchestration

### Backend Structure

The FastAPI backend follows a layered architecture:

- `backend/app/main.py`: FastAPI app entrypoint and root route
- `backend/app/routers/`: API route handlers
  - `transaction_router.py`: Transaction CRUD and fraud prediction
  - `chat_router.py`: WebSocket endpoints for AI agent chat
  - `auth_router.py`: Authentication and user management
- `backend/app/schemas/`: Pydantic models for request/response validation
- `backend/app/models/`: SQLAlchemy database models
- `backend/app/service/`: Business logic layer
- `backend/app/repositories/`: Data access layer
- `backend/app/settings/`: Configuration management (database, base settings)
- `backend/app/infra/`: Infrastructure concerns (logging, model loading)
- `backend/app/ws/`: WebSocket connection management
- `backend/app/security/`: Authentication and security utilities

### Frontend Structure

React SPA using modern TypeScript patterns:

- `frontend/src/App.tsx`: Main application component with routing
- `frontend/src/pages/`: Page components
  - `Dashboard.tsx`: Main dashboard with transaction overview
  - `Transactions.tsx`: Transaction listing and management
  - `Agent.tsx`: AI agent chat interface with real-time communication
- `frontend/src/components/`: Reusable UI components
  - `Layout.tsx`, `Navbar.tsx`: Application shell
  - `ReasoningFlowComponent.tsx`: Agent reasoning visualization
  - Various transaction and dashboard components
- `frontend/src/style.css`: Global TailwindCSS styles with custom animations

### Agent Service

AI-powered analysis service built with Azure AI and LangChain:

- `agent-service/src/app/agents/`: AI agent implementations using Azure OpenAI
- `agent-service/src/app/schemas/`: Agent request/response models
- **LangChain framework** for agent orchestration and tool integration
- **LangGraph workflows** for complex reasoning and decision-making flows
- **Azure AI integration** for enterprise-grade LLM capabilities
- Integration with transaction data for natural language queries

## Development Environment Setup

### Prerequisites
- Python 3.11.13 (exact version specified in pyproject.toml)
- Node.js and npm for frontend development
- Docker Desktop for containerized development
- `uv` package manager for Python dependencies

### Quick Start with Docker

The entire stack can be run with Docker Compose:

```bash
docker compose up --build
```

This starts:
- **Backend API**: `http://localhost:80` (or port 8000 for local dev)
- **Frontend**: `http://localhost:5173` (Vite dev server)
- **PostgreSQL**: Port 5432
- **pgAdmin**: `http://localhost:5050`

### Environment Configuration
- Copy `.env.example` to `.env` and configure database credentials
- Model artifacts are mounted from `./backend/models` to `/app/models`

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

## Key Features

### 🎯 Fraud Detection
- **Real-time ML predictions** using XGBoost and scikit-learn models
- **Transaction monitoring** with comprehensive fraud scoring
- **Historical analysis** of transaction patterns

### 🤖 AI Agent Chat
- **Azure OpenAI-powered** natural language queries about transaction data and fraud patterns
- **LangChain framework** for intelligent tool selection and workflow orchestration
- **LangGraph workflows** for complex multi-step reasoning and decision trees
- **Real-time WebSocket communication** with typing animations
- **Reasoning transparency** showing agent's analytical steps and tool usage
- **Interactive data exploration** through conversational interface

### 📊 Dashboard & Analytics
- **Transaction overview** with fraud statistics
- **Real-time updates** via WebSocket connections
- **Responsive design** optimized for all devices
- **Data visualization** of fraud trends and patterns

### 🔐 Security & Authentication
- **JWT-based authentication** for secure access
- **User session management** with role-based permissions
- **Secure WebSocket connections** for real-time features

## API Endpoints

### Core Transaction API
- `GET /`: Application healthcheck
- `GET /transactions/`: List all transactions with pagination
- `GET /transactions/{transaction_id}`: Get specific transaction details
- `POST /transactions/`: Create new transaction
- `GET /transactions/{transaction_id}/predict`: Get fraud prediction for transaction
- `DELETE /transactions/{transaction_id}`: Remove transaction

### Real-time Chat API
- `WebSocket /chat/ws/agent/{client_id}`: Real-time agent communication
- `POST /chat/{conversation_id}/message`: Send message to conversation
- `GET /chat/{user_id}`: Get user's conversation history
- `DELETE /chat/{user_id}/{conversation_id}`: Delete conversation

### Authentication API
- `POST /auth/login`: User authentication
- `POST /auth/register`: User registration
- `GET /auth/me`: Get current user profile

## Usage

1. **Start the application**: `docker compose up --build`
2. **Access the frontend**: Open `http://localhost:5173`
3. **Navigate to different sections**:
   - **Dashboard**: Overview of transactions and fraud statistics
   - **Transactions**: Detailed transaction management and analysis
   - **Agent**: AI-powered chat for interactive data exploration
4. **Interact with the AI agent**: Ask natural language questions about:
   - Fraud patterns and trends
   - Transaction analysis and filtering
   - Data insights and recommendations
   - Statistical queries about your dataset

## Testing

Backend tests are located in `backend/tests/` and cover:
- API route handlers with FastAPI TestClient
- Service layer business logic
- Repository data access patterns
- WebSocket connection handling
- Authentication and security flows

Run tests from the backend directory:

```bash
cd backend
uv sync --group dev  # ensure dev deps are installed
uv run pytest -q    # quick test run
uv run pytest -v    # verbose output with details
```

Frontend testing can be added with React Testing Library and Jest for component and integration testing.

## Data & Models

- **Synthetic fraud data** included in `data/` directory for development and testing
- **ML model artifacts** stored in `backend/models/` directory
- **Database migrations** handled automatically via SQLAlchemy
- **Real-time data processing** through WebSocket connections
- **Model training pipeline** can be extended for custom fraud detection models

## Technology Highlights

- **Modern Python stack** with FastAPI, SQLAlchemy 2.0, and async support
- **Type-safe frontend** using React 19 and TypeScript
- **Enterprise AI integration** with Azure OpenAI and LangChain/LangGraph workflows
- **Real-time features** via WebSocket communication with intelligent agent responses
- **Advanced agent reasoning** with transparent decision-making and tool usage
- **Containerized deployment** with Docker Compose for scalable infrastructure
- **Production-ready architecture** with proper security, authentication, and testing
