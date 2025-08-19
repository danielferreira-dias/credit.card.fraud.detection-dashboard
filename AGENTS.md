# Repository Guidelines

## Project Structure & Module Organization

- `backend/app/main.py`: FastAPI app entrypoint (`app` instance, root route).
- `backend/app/routers/`: Place API route modules (e.g., `transactions.py`).
- `backend/app/schemas/`: Pydantic request/response models (e.g., `transaction_schema.py`).
- `backend/models/`: Serialized artifacts (e.g., `*.pkl`) mounted in Docker.
- `backend/dockerfile`: Backend container image definition.
- `docker-compose.yml`: Orchestrates the backend service (exposes `:80`).
- `backend/pyproject.toml`, `backend/requirements.txt`: Dependencies (Python ≥3.12).

## Build, Test, and Development Commands

- Run with Docker (recommended):
  ```bash
  docker compose up --build
  ```
  Builds from `backend/dockerfile` and serves FastAPI on `http://localhost:80`.
- Local dev (no Docker):
  ```bash
  cd backend
  python -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  ```
  App available at `http://localhost:8000`.

## Coding Style & Naming Conventions

- Python 3.12, PEP 8, 4‑space indentation, type hints required.
- Files/modules: `snake_case.py`; classes (Pydantic models): `PascalCase`.
- Routers: group by domain (e.g., `app/routers/transactions.py`) and import into `main.py`.
- Request/response models live in `app/schemas/` and are imported by routers.

## Testing Guidelines

- Framework: pytest (add tests under `backend/tests/`).
- Naming: files `test_*.py`, functions `test_*`.
- Run tests:
  ```bash
  cd backend && pytest -q
  ```
  Aim for coverage on schemas validation and route handlers.

## Commit & Pull Request Guidelines

- Commits: Make sure the commits are descritive with medium-short descriptions.
- Scope your changes; separate refactors from features.
- PRs must include:
  - Clear description and rationale; link related issues.
  - Summary of changes and any breaking impacts.
  - How to test (commands, sample cURL/json). Example:
    ```bash
    curl http://localhost:80/
    ```
  - Screenshots or response samples when relevant.

## Security & Configuration Tips

- Do not commit secrets. Prefer environment variables (`python-dotenv` supported).
- Large model files belong in `backend/models/`; they are mounted via Compose.
- Healthcheck expects `GET /` to succeed; keep a lightweight root route available.

## Function Documentation & Flow

Below is a concise reference for key functions in the backend, what each does exactly, and how they fit into the request flow.

**App Entry**

- `app.main.read_root`: Returns a simple JSON payload for healthchecks and smoke tests. Flow: request hits `/` → FastAPI invokes `read_root` → JSON `{"message": "Hello from credit-card-fraud-detection-dashboard!"}` is returned.

**Schemas**

- `app.schemas.transaction_schema.Transaction`: Request model describing a single transaction with engineered features. Used by the transactions router to validate incoming JSON and guarantee correct types before prediction.
- `app.schemas.transaction_response.TransactionPrediction`: Response model for predictions. Fields: `is_fraud` (bool), optional `probability` (float), and `feature_order` (list[str]) indicating the feature ordering used to build the input vector.

**Transactions Router**

- `app.routers.transactions._models_dir`: Resolves the absolute path to `backend/models/` from the router location. Flow: called by loaders to find `fraud_detection_model.pkl` and `fraud_detection_scaler.pkl` mounted by Docker.
- `app.routers.transactions._load_artifacts`: Lazily loads and caches the scaler and model from disk using `pickle`. Flow: first prediction request → attempts to open the scaler and model files → caches them in module-level variables. Subsequent calls are no-ops. Any exception during load is raised for the caller to translate into an HTTP error.
- `app.routers.transactions.predict`: Predicts whether a transaction is fraudulent.
  - Input: JSON body validated against `Transaction`.
  - Flow:
    1) Ensure artifacts are loaded via `_load_artifacts` (HTTP 503 if unavailable).
    2) Build feature vector preserving the schema field order.
    3) Apply scaler transform when available; otherwise use raw features.
    4) Call model `.predict` to get the class; attempt `.predict_proba` for probability.
    5) Return `TransactionPrediction` with `is_fraud`, optional `probability`, and `feature_order` for transparency/debugging.

## Transactions Router Usage

- `POST /transactions/predict`: Submit a transaction to receive a fraud prediction.
  - Request model: `Transaction` (see `app/schemas/transaction_schema.py`).
  - Response model: `TransactionPrediction` with `is_fraud` and optional `probability`.
  - Example (truncated for brevity; include all required fields in practice):
    ```bash
    curl -X POST http://localhost:80/transactions/predict \
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

Notes:
- The router attempts to load pickled artifacts; if dependencies like scikit-learn are missing, the endpoint returns HTTP 503. Ensure `backend/models/*.pkl` exist and required libs are installed in the image.
- Feature order is derived from the schema to maintain consistency between training and inference.
