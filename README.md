# Credit Card Fraud Detection Dashboard

An API backend for a fraud detection dashboard. It lists credit card transactions and provides a prediction endpoint backed by a model to classify whether a transaction is fraudulent.

This repository currently ships the FastAPI backend, ready to run via Docker or locally with `uv` (Astral’s Python package manager). Tests use `pytest`.

## Tech Stack

- FastAPI (Python 3.12)
- Package manager: `uv` with `pyproject.toml` + `uv.lock`
- Containerization: Docker + Docker Compose
- Testing: `pytest`

## Repository Layout

- `backend/app/main.py`: FastAPI app entrypoint (`app`) and root route.
- `backend/app/routers/transaction.py`: Transactions router (list/get/create/delete + predict endpoint).
- `backend/app/schemas/transaction_schema.py`: Pydantic models for requests/responses.
- `backend/models/`: Place serialized model artifacts if/when used by the prediction service.
- `backend/dockerfile`: Backend container image (installs deps via `uv sync`; serves with `uv run uvicorn`).
- `docker-compose.yml`: Orchestrates the backend service on `http://localhost:80` and mounts `backend/models`.
- `backend/pyproject.toml`: Project metadata and runtime/dev dependencies for `uv`.
- `backend/requirements.txt`: Plain requirements list (kept alongside `pyproject.toml`).
- `backend/tests/`: Pytest test suite (routes, services, repos).

## Running the Backend

You can run with Docker (recommended) or locally using `uv`.

### Option A — Docker Compose

Prerequisites: Docker Desktop or a compatible Docker/Compose setup.

```
docker compose up --build
```

- Builds from `backend/dockerfile` and exposes the API at `http://localhost:80`.
- Healthcheck hits `GET /` and expects a 200.
- Model artifacts, if present, are mounted from `./backend/models` to `/app/models` in the container.

Quick smoke test:

```
curl http://localhost:80/
```

### Option B — Local Dev with uv

Prerequisites: Python 3.12+, `uv` installed. Install `uv` (one-time):

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Set up and run:

```
cd backend
uv sync                # install main dependencies
uv sync --group dev    # (optional) include dev deps like pytest

# Run the API in dev mode (reload on changes)
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Open http://localhost:8000/
```

For a non-reload run:

```
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Overview

Base URL depends on how you run the app:

- Docker: `http://localhost:80`
- Local dev (uv): `http://localhost:8000`

Endpoints (from `app/routers/transaction.py`):

- `GET /`: Healthcheck — returns `{"message": "Hello from credit-card-fraud-detection-dashboard!"}`.
- `GET /transactions/`: List transactions.
- `GET /transactions/{transaction_id}`: Get a transaction by id.
- `GET /transactions/{transaction_id}/predict`: Predict fraud for a transaction id.
- `POST /transactions/`: Create a transaction (expects `TransactionRequest` fields).
- `DELETE /transactions/{transaction_id}`: Delete a transaction by id.

Example (truncated payload; include all required fields):

```
curl -X POST http://localhost:80/transactions/ \
  -H 'Content-Type: application/json' \
  -d '{
        "channel_large": 0,
        "channel_medium": 1,
        "device_Android_App": 0,
        "device_Safari": 0,
        "device_Firefox": 0,
        "USD_converted_total_amount": 123.45,
        "device_Chrome": 1,
        "device_iOS_App": 0,
        "city_Unknown_City": 0,
        "country_USA": 1,
        "country_Australia": 0,
        "country_Germany": 0,
        "country_UK": 0,
        "country_Canada": 0,
        "country_Japan": 0,
        "country_France": 0,
        "device_Edge": 0,
        "country_Singapore": 0,
        "channel_mobile": 0,
        "country_Nigeria": 0,
        "country_Brazil": 0,
        "country_Russia": 0,
        "country_Mexico": 0,
        "is_off_hours": 0,
        "max_single_amount": 200.0,
        "USD_converted_amount": 50.0,
        "channel_web": 1,
        "is_high_amount": 0,
        "is_low_amount": 1,
        "transaction_hour": 14,
        "hour": 14,
        "device_NFC_Payment": 0,
        "device_Magnetic_Stripe": 0,
        "device_Chip_Reader": 1,
        "high_risk_transaction": 0,
        "channel_pos": 0,
        "card_present": 1,
        "distance_from_home": 5.0
      }'
```

Note: The current example router returns static data and a fixed prediction response. You can swap in a real trained model and scaler later, reading artifacts from `backend/models/`.

## Testing

Run the test suite from the `backend` directory:

```
cd backend
uv sync --group dev  # ensure dev deps are installed
uv run pytest -q
```

Tests cover:

- Route handlers with FastAPI `TestClient`.
- Service delegation to the repository.
- Repository query plumbing via a fake session.

## Notes on Configuration

- Python version: `>=3.12` (see `backend/pyproject.toml`).
- Container build installs using `uv sync --frozen` from `uv.lock` for reproducible builds.
- Compose mounts `./backend/models` to `/app/models` inside the container for model artifacts.
- The root route `GET /` is kept lightweight for healthchecks.
