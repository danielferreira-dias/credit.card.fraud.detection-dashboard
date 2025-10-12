# Credit Card Fraud Detection Dashboard

A full-stack fraud detection platform featuring real-time transaction monitoring, ML-powered fraud prediction, and an intelligent AI agent with RAG (Retrieval-Augmented Generation) capabilities for advanced data analysis. The system combines a FastAPI backend with machine learning capabilities, a modern React frontend with persistent WebSocket connections, and a comprehensive AI agent service with vector search and knowledge base integration.

This repository ships both the FastAPI backend and React frontend, with WebSocket-based real-time communication, an integrated AI agent service for natural language queries about fraud data, and enterprise-grade vector search capabilities powered by Azure AI Search with PGVector fallback.

[![Watch the video](https://img.youtube.com/vi/WGl6gelmvoA/maxresdefault.jpg)](https://youtu.be/WGl6gelmvoA)

## Tech Stack

### Backend
- **FastAPI** (Python 3.11) with async support
- **SQLAlchemy 2.0** for ORM with PostgreSQL
- **XGBoost & scikit-learn** for ML fraud detection
- **WebSocket** support for real-time agent communication
- **Azure OpenAI** for LLM-powered agent capabilities
- **LangChain & LangGraph** for agent workflow orchestration
- **Azure AI Search** for enterprise vector search and knowledge retrieval
- **PGVector** as fallback vector database for embeddings
- **HuggingFace Embeddings** for semantic similarity matching
- **RAG (Retrieval-Augmented Generation)** for context-aware responses
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
- **Azure AI Search** for vector search and knowledge base
- **Agent Service** powered by LangChain/LangGraph workflows
- **Vector Database Layer** with Azure AI Search primary and PGVector fallback
- **Persistent WebSocket Connections** across frontend navigation

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

React SPA using modern TypeScript patterns with persistent WebSocket connections:

- `frontend/src/App.tsx`: Main application component with routing and global context providers
- `frontend/src/pages/`: Page components
  - `Dashboard.tsx`: Main dashboard with transaction overview
  - `Transactions.tsx`: Transaction listing and management
  - `Agent.tsx`: AI agent chat interface with real-time communication
  - `Personal.tsx`: User profile and report management
- `frontend/src/components/`: Reusable UI components
  - `Layout.tsx`, `Navbar.tsx`: Application shell
  - `ReasoningFlowComponent.tsx`: Agent reasoning visualization
  - `Modal.tsx`: Global notification system with agent alerts
  - Various transaction and dashboard components
- `frontend/src/context/`: Global state management
  - `WebSocketContext.tsx`: Persistent WebSocket connection management
  - `UserContext.tsx`, `NotificationContext.tsx`: User and notification state
- `frontend/src/style.css`: Global TailwindCSS styles with custom animations

### Agent Service

AI-powered analysis service built with Azure AI, LangChain, and RAG capabilities:

- `agent-service/src/app/agents/`: Multiple specialized AI agent implementations
  - **TransactionAgent**: Interactive conversational agent with comprehensive tool suite
  - **AnalystAgent**: Specialized report generation agent with structured outputs
  - **TitleNLP**: Conversation title generation for chat organization
- `agent-service/src/app/services/vector_service.py`: RAG implementation
  - **Azure AI Search integration** for enterprise vector search
  - **PGVector fallback** for local vector database operations
  - **HuggingFace embeddings** with semantic similarity search
  - **Hybrid search** combining vector and keyword matching
- `agent-service/src/app/schemas/`: Agent prompts, structured response models, and validation schemas
- **LangChain framework** for agent orchestration and tool integration
- **LangGraph workflows** for complex reasoning and decision-making flows
- **Azure AI integration** for enterprise-grade LLM capabilities
- **Knowledge base integration** with fraud detection domain expertise
- **Real-time analysis** of transactions with contextual insights

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

### 🤖 AI Agent Chat & Analysis
- **Multiple Specialized Agents**:
  - **TransactionAgent**: Interactive chat with comprehensive transaction analysis tools
  - **AnalystAgent**: Automated report generation with structured insights
  - **TitleNLP**: Intelligent conversation organization
- **RAG (Retrieval-Augmented Generation)**:
  - **Azure AI Search** integration for enterprise knowledge retrieval
  - **PGVector fallback** for local vector database operations
  - **Semantic search** through fraud detection knowledge base
  - **Context-aware responses** with domain-specific expertise
- **Advanced Analytics**:
  - **Transaction-specific analysis** with fraud pattern detection
  - **Automated report generation** for comprehensive fraud assessment
  - **Statistical insights** and trend analysis
  - **Personalized recommendations** based on transaction history
- **Real-time Communication**:
  - **Persistent WebSocket connections** that survive page navigation
  - **Cross-page notifications** with message previews
  - **Typing animations** and reasoning transparency
  - **Tool usage visualization** showing agent's analytical steps

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
- `WebSocket /chat/ws/agent/{client_id}`: Real-time agent communication with persistent connections
- `POST /chat/{conversation_id}/message`: Send message to conversation
- `GET /chat/{user_id}`: Get user's conversation history
- `DELETE /chat/{user_id}/{conversation_id}`: Delete conversation

### Advanced Analysis API
- `POST /transactions/analysis/{user_id}`: Generate AI-powered transaction analysis
- `GET /transactions/analysis/transaction_id`: Retrieve existing transaction analysis
- `POST /users/reports/{user_id}`: Generate comprehensive fraud reports
- `GET /users/reports/{user_id}`: Get user's report history
- `GET /users/reports/{user_id}/latest`: Get latest fraud report

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
4. **Interact with the AI agent**: Experience advanced AI capabilities including:
   - **Interactive Chat**: Natural language queries with persistent WebSocket connections
   - **Transaction Analysis**: AI-powered fraud assessment for specific transactions
   - **Automated Reports**: Comprehensive fraud analysis reports with structured insights
   - **Knowledge Base Queries**: RAG-powered responses using fraud detection expertise
   - **Cross-page Notifications**: Stay informed about agent responses while navigating
   - **Pattern Recognition**: Advanced fraud pattern detection and statistical analysis
   - **Personalized Recommendations**: Tailored insights based on transaction history

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
- **Type-safe frontend** using React 19 and TypeScript with persistent state management
- **Enterprise AI integration** with Azure OpenAI and LangChain/LangGraph workflows
- **RAG Implementation** with Azure AI Search and PGVector for intelligent knowledge retrieval
- **Multi-agent Architecture** with specialized agents for different analysis tasks
- **Persistent WebSocket connections** that survive frontend navigation with cross-page notifications
- **Vector search capabilities** with hybrid semantic and keyword matching
- **Advanced agent reasoning** with transparent decision-making and tool usage
- **Automated report generation** with structured outputs and domain expertise
- **Knowledge base integration** with fraud detection domain knowledge
- **Containerized deployment** with Docker Compose for scalable infrastructure
- **Production-ready architecture** with proper security, authentication, and comprehensive testing
