# FastAPI Lifespan & Async Context Managers

## Overview

This document explains FastAPI's lifespan context manager pattern and how it's used to manage expensive resources (database connections, ML models, agent instances) throughout the application lifecycle.

## Table of Contents

1. [Python Context Managers](#python-context-managers)
2. [FastAPI Lifespan Pattern](#fastapi-lifespan-pattern)
3. [Our Implementation](#our-implementation)
4. [Async Context Managers](#async-context-managers)
5. [Common Patterns](#common-patterns)
6. [Troubleshooting](#troubleshooting)

---

## Python Context Managers

### Basic Concept: The `with` Statement

Context managers handle **setup and cleanup** automatically using the `with` statement:

```python
# Without context manager (manual cleanup)
file = open("data.txt", "r")
try:
    content = file.read()
    # Do something with content
finally:
    file.close()  # Must remember to close!

# With context manager (automatic cleanup)
with open("data.txt", "r") as file:
    content = file.read()
    # Do something with content
# File automatically closed here, even if exception occurs!
```

### How Context Managers Work

Behind the scenes, the `with` statement calls special methods:

```python
class FileManager:
    def __init__(self, filename):
        self.filename = filename
        self.file = None

    def __enter__(self):
        """Called when entering 'with' block"""
        print("Opening file...")
        self.file = open(self.filename, "r")
        return self.file  # This becomes the 'as' variable

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Called when exiting 'with' block"""
        print("Closing file...")
        if self.file:
            self.file.close()
        # Return False to propagate exceptions, True to suppress

# Usage
with FileManager("data.txt") as f:
    content = f.read()
```

**Execution Flow:**
```
1. FileManager("data.txt") creates instance
2. __enter__() called → opens file → returns file object
3. Code inside 'with' block executes
4. __exit__() called → closes file (even if error occurred!)
```

### The `@contextmanager` Decorator

Python's `contextlib` provides a simpler way to create context managers:

```python
from contextlib import contextmanager

@contextmanager
def file_manager(filename):
    # SETUP (before yield)
    print("Opening file...")
    file = open(filename, "r")

    try:
        yield file  # This value is returned to 'with' block
    finally:
        # CLEANUP (after yield)
        print("Closing file...")
        file.close()

# Usage (identical to class-based version)
with file_manager("data.txt") as f:
    content = f.read()
```

**Key Insight:** `yield` divides the function into:
- **Before yield** = `__enter__()` logic (setup)
- **After yield** = `__exit__()` logic (cleanup)

---

## FastAPI Lifespan Pattern

### The Problem: Where to Initialize Resources?

In web applications, you often need resources that:
1. Are **expensive to create** (database pools, ML models)
2. Should be **created once** at startup
3. Should be **shared across all requests**
4. Must be **cleaned up** on shutdown

**Bad Approach:**
```python
# ❌ Creates new connection for EVERY request (slow!)
@app.get("/data")
async def get_data():
    db = Database.connect()  # Expensive!
    result = db.query("SELECT * FROM data")
    db.close()
    return result
```

**Good Approach with Lifespan:**
```python
# ✅ Creates connection ONCE at startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    db = Database.connect()  # Created once
    app.state.db = db  # Store in app state

    yield  # App runs and handles requests

    # SHUTDOWN
    db.close()  # Clean up

app = FastAPI(lifespan=lifespan)

@app.get("/data")
async def get_data():
    db = app.state.db  # Reuse existing connection
    return db.query("SELECT * FROM data")
```

### Lifespan Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Startup                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  lifespan() Context Manager                                 │
│  ────────────────────────────────────────                   │
│                                                             │
│  BEFORE yield:                                              │
│  ─────────────                                              │
│  • Load ML models                                           │
│  • Connect to databases                                     │
│  • Initialize API clients                                   │
│  • Setup logging                                            │
│  • Warm up caches                                           │
│                                                             │
│  yield  ← Control returns to FastAPI                        │
│  ─────                                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Application Running                            │
│              ─────────────────────                          │
│              Handling HTTP Requests                         │
│              • GET /health                                  │
│              • POST /user_message/stream                    │
│              • GET /conversation_history/{id}               │
│                                                             │
│              All endpoints can access:                      │
│              • app.state.db                                 │
│              • app.state.agent                              │
│              • app.state.cache                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                  (User presses Ctrl+C)
                  (Docker stop signal)
                  (Kubernetes terminates pod)
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  lifespan() Context Manager (continued)                     │
│  ────────────────────────────────────────                   │
│                                                             │
│  AFTER yield:                                               │
│  ────────────                                               │
│  • Close database connections                               │
│  • Save any pending data                                    │
│  • Cleanup temporary files                                  │
│  • Close API clients                                        │
│  • Flush logs                                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Application Shutdown                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Our Implementation

### File: `agent-service/src/app/main.py`

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle with startup and shutdown logic.

    FastAPI's lifespan context manager allows initialization of expensive resources
    (database connections, ML models, API clients) once at startup, rather than on
    every request. This pattern ensures efficient resource management and proper cleanup.
    """

    # ═══════════════════════════════════════════════════════════
    #                    STARTUP PHASE
    # ═══════════════════════════════════════════════════════════
    logger.info("🚀 Starting up...")

    # 1. Get configuration from environment
    model_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
    backend_client = get_backend_client()

    # 2. Create TransactionAgent (not yet connected to DB)
    agent_instance = TransactionAgent(
        model_name=model_name,
        backend_client=backend_client
    )

    # 3. Initialize PostgreSQL checkpoint saver
    #    - Opens database connection pool
    #    - Creates necessary tables
    #    - Initializes LangGraph agent
    await agent_instance.setup()

    # 4. Store in global state for request handlers
    agent_state.agent = agent_instance

    logger.info("✅ Ready to handle requests")

    # ═══════════════════════════════════════════════════════════
    #                    RUNTIME PHASE
    # ═══════════════════════════════════════════════════════════
    yield  # FastAPI runs here, handling requests
    #      All endpoints can now use agent_state.agent

    # ═══════════════════════════════════════════════════════════
    #                    SHUTDOWN PHASE
    # ═══════════════════════════════════════════════════════════
    logger.info("🛑 Shutting down...")

    # 1. Close PostgreSQL connections gracefully
    if agent_state.agent is not None:
        await agent_state.agent.cleanup()

    logger.info("👋 Goodbye")

# Attach lifespan to FastAPI app
app = FastAPI(
    title="Agent Service",
    version="1.0.0",
    lifespan=lifespan  # ← Registers our context manager
)
```

### Why Not Use Startup/Shutdown Events?

**Old Pattern (Deprecated in FastAPI 0.93+):**
```python
@app.on_event("startup")
async def startup_event():
    # Initialize resources
    pass

@app.on_event("shutdown")
async def shutdown_event():
    # Cleanup resources
    pass
```

**Problems:**
1. ❌ Harder to share state between startup and shutdown
2. ❌ No guaranteed cleanup on exceptions
3. ❌ Can't use context manager benefits
4. ❌ Deprecated in newer FastAPI versions

**Modern Pattern (Lifespan):**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    resource = await initialize()
    yield
    # Shutdown - guaranteed to run
    await resource.cleanup()
```

**Benefits:**
1. ✅ Shared scope (same variables in startup and shutdown)
2. ✅ Guaranteed cleanup via context manager protocol
3. ✅ Cleaner, more readable code
4. ✅ Better IDE support and type checking

---

## Async Context Managers

### Regular vs Async Context Managers

**Regular Context Manager** (synchronous):
```python
class DatabaseConnection:
    def __enter__(self):
        self.conn = db.connect()  # Blocking I/O
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()  # Blocking I/O

with DatabaseConnection() as conn:
    data = conn.query("SELECT * FROM users")  # Blocking
```

**Async Context Manager** (non-blocking):
```python
class AsyncDatabaseConnection:
    async def __aenter__(self):
        self.conn = await db.connect()  # Non-blocking I/O
        return self.conn

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.conn.close()  # Non-blocking I/O

async with AsyncDatabaseConnection() as conn:
    data = await conn.query("SELECT * FROM users")  # Non-blocking
```

**Key Differences:**
| Regular | Async |
|---------|-------|
| `__enter__()` | `async def __aenter__()` |
| `__exit__()` | `async def __aexit__()` |
| `with` | `async with` |
| Blocking I/O | Non-blocking I/O |

### `@asynccontextmanager` Decorator

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def async_file_manager(filename):
    # SETUP (async operations allowed)
    file = await async_open(filename)
    print(f"Opened {filename}")

    try:
        yield file
    finally:
        # CLEANUP (async operations allowed)
        await file.aclose()
        print(f"Closed {filename}")

# Usage
async with async_file_manager("data.txt") as f:
    content = await f.read()
```

### Our PostgreSQL Checkpointer Example

**File:** `agent-service/src/app/agents/agents.py`

```python
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

async def setup(self):
    """Setup using async context manager"""

    # 1. Create the async context manager
    self._checkpointer_cm = AsyncPostgresSaver.from_conn_string(
        os.getenv("DATABASE_URL")
    )

    # 2. Enter the context manager (opens connection)
    self.checkpointer = await self._checkpointer_cm.__aenter__()
    #                          ↑
    #                    Non-blocking connection

    # 3. Setup database tables
    await self.checkpointer.setup()

    # Context stays open until cleanup()

async def cleanup(self):
    """Exit context manager properly"""
    if self._checkpointer_cm is not None:
        # Exit the async context manager (closes connection)
        await self._checkpointer_cm.__aexit__(None, None, None)
        #                                      ↑
        #                                No exception to propagate
```

**Why Manual Context Manager Entry?**

```python
# ❌ WRONG - Connection closes immediately!
async def setup(self):
    async with AsyncPostgresSaver.from_conn_string(...) as checkpointer:
        self.checkpointer = checkpointer
    # __aexit__() called here - connection CLOSED!
    # self.checkpointer is now useless

# ✅ CORRECT - Connection stays open
async def setup(self):
    self._cm = AsyncPostgresSaver.from_conn_string(...)
    self.checkpointer = await self._cm.__aenter__()
    # Connection stays open until we call __aexit__()

async def cleanup(self):
    await self._cm.__aexit__(None, None, None)
    # Now connection closes
```

**When to Use Manual Entry:**
- Resource needs to stay alive beyond the function scope
- Resource lifetime tied to application lifecycle, not function execution
- In our case: checkpointer must live from startup to shutdown

---

## Common Patterns

### Pattern 1: Database Connection Pool

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP - Create connection pool
    pool = await asyncpg.create_pool(
        dsn="postgresql://user:pass@localhost/db",
        min_size=10,
        max_size=100
    )
    app.state.db_pool = pool

    yield

    # SHUTDOWN - Close all connections
    await pool.close()

# Use in endpoints
@app.get("/users")
async def get_users(request: Request):
    async with request.app.state.db_pool.acquire() as conn:
        users = await conn.fetch("SELECT * FROM users")
        return users
```

### Pattern 2: ML Model Loading

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP - Load heavy ML model (slow!)
    logger.info("Loading XGBoost model...")
    model = joblib.load("fraud_model.pkl")  # Takes 5 seconds
    app.state.ml_model = model
    logger.info("Model loaded!")

    yield

    # SHUTDOWN - Free memory
    del app.state.ml_model
    import gc
    gc.collect()

# Use in endpoints (instant access to pre-loaded model)
@app.post("/predict")
async def predict(data: TransactionData, request: Request):
    model = request.app.state.ml_model  # Already loaded!
    prediction = model.predict(data.to_numpy())
    return {"fraud_probability": float(prediction[0])}
```

### Pattern 3: Multiple Resources

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP - Initialize multiple resources
    logger.info("Initializing resources...")

    # Database
    db_pool = await create_db_pool()

    # Redis cache
    redis = await aioredis.create_redis_pool("redis://localhost")

    # HTTP client
    http_client = httpx.AsyncClient(timeout=30.0)

    # ML model
    model = load_model("model.pkl")

    # Store all in app state
    app.state.db = db_pool
    app.state.cache = redis
    app.state.http = http_client
    app.state.model = model

    logger.info("All resources ready!")

    yield

    # SHUTDOWN - Clean up in reverse order
    logger.info("Cleaning up resources...")

    await http_client.aclose()
    redis.close()
    await redis.wait_closed()
    await db_pool.close()

    logger.info("Cleanup complete!")
```

### Pattern 4: Dependency Injection

```python
# Global state holder
class AppState:
    def __init__(self):
        self.agent: Optional[TransactionAgent] = None

app_state = AppState()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    agent = TransactionAgent(...)
    await agent.setup()
    app_state.agent = agent

    yield

    # SHUTDOWN
    await app_state.agent.cleanup()

# Dependency function
def get_agent() -> TransactionAgent:
    if app_state.agent is None:
        raise RuntimeError("Agent not initialized")
    return app_state.agent

# Use in endpoint
@app.post("/query")
async def query_agent(
    query: str,
    agent: TransactionAgent = Depends(get_agent)  # Injected!
):
    result = await agent.query(query)
    return result
```

---

## Troubleshooting

### Issue: Resources Not Initialized

**Symptom:**
```
RuntimeError: Agent not initialized
```

**Cause:** Endpoint called before lifespan completed startup

**Solution:** Check logs for startup completion
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    # ... initialization ...
    logger.info("✅ Startup complete!")  # Wait for this message
    yield
```

### Issue: Resources Not Cleaned Up

**Symptom:** Database connections remain open after shutdown

**Cause:** Exception in cleanup code or cleanup not awaited

**Solution:** Wrap cleanup in try/except
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    resource = await initialize()

    yield

    try:
        await resource.cleanup()
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        # Still attempt other cleanup
```

### Issue: Slow Startup

**Symptom:** Application takes 30+ seconds to start

**Cause:** Loading heavy resources sequentially

**Solution:** Load resources concurrently
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ❌ SLOW - Sequential (10s + 15s + 5s = 30s)
    db = await connect_db()      # 10 seconds
    model = await load_model()    # 15 seconds
    cache = await init_cache()    # 5 seconds

    # ✅ FAST - Concurrent (max(10s, 15s, 5s) = 15s)
    db, model, cache = await asyncio.gather(
        connect_db(),
        load_model(),
        init_cache()
    )

    yield
```

### Issue: Context Manager Exit Not Called

**Symptom:** `__aexit__()` never runs, resources leak

**Cause:** Process killed with SIGKILL (kill -9)

**Solution:** Use proper shutdown signals
```bash
# ❌ Immediate kill - no cleanup
docker stop -t 0 my-container

# ✅ Graceful shutdown - cleanup runs
docker stop -t 30 my-container  # 30 second grace period
```

---

## Best Practices

### ✅ DO

1. **Initialize expensive resources in lifespan**
   ```python
   @asynccontextmanager
   async def lifespan(app: FastAPI):
       ml_model = load_model()  # ✅ Load once
       yield
   ```

2. **Use dependency injection for resources**
   ```python
   def get_db() -> Database:
       return app.state.db

   @app.get("/data")
   async def get_data(db: Database = Depends(get_db)):
       return db.query()
   ```

3. **Log startup and shutdown steps**
   ```python
   logger.info("🚀 Starting up...")
   logger.info("✅ Ready!")
   logger.info("🛑 Shutting down...")
   logger.info("👋 Goodbye!")
   ```

4. **Handle cleanup errors gracefully**
   ```python
   try:
       await resource.cleanup()
   except Exception as e:
       logger.error(f"Cleanup error: {e}")
   ```

### ❌ DON'T

1. **Don't create resources in endpoints**
   ```python
   @app.get("/data")
   async def get_data():
       db = Database()  # ❌ Created on EVERY request!
       return db.query()
   ```

2. **Don't use global variables without proper initialization**
   ```python
   agent = TransactionAgent()  # ❌ Created at import time!

   @app.get("/query")
   async def query():
       return agent.query()  # What if agent needs async setup?
   ```

3. **Don't forget to cleanup async resources**
   ```python
   @asynccontextmanager
   async def lifespan(app: FastAPI):
       pool = await create_pool()
       yield
       # ❌ Missing: await pool.close()
   ```

4. **Don't block the event loop in lifespan**
   ```python
   @asynccontextmanager
   async def lifespan(app: FastAPI):
       model = joblib.load("huge_model.pkl")  # ❌ Blocks for 30s!
       yield

   # ✅ Better: Use run_in_executor for blocking I/O
   loop = asyncio.get_event_loop()
   model = await loop.run_in_executor(None, joblib.load, "model.pkl")
   ```

---

## Summary

| Concept | Purpose | Example |
|---------|---------|---------|
| Context Manager | Automatic setup/cleanup | `with open() as f:` |
| `@contextmanager` | Create context managers easily | `@contextmanager def fn(): yield` |
| `@asynccontextmanager` | Async version | `@asynccontextmanager async def fn(): yield` |
| FastAPI Lifespan | Manage app lifecycle | `app = FastAPI(lifespan=lifespan)` |
| `yield` | Divide setup/cleanup | Code before = setup, after = cleanup |
| `__aenter__()` | Async context entry | Called on `async with` |
| `__aexit__()` | Async context exit | Called when leaving `async with` |

**Key Takeaway:** Lifespan context managers ensure expensive resources are:
1. ✅ Initialized **once** at startup
2. ✅ **Shared** across all requests
3. ✅ **Cleaned up** properly on shutdown
4. ✅ Exception-safe (cleanup runs even on errors)

---

**Last Updated:** 2025-10-01
**Author:** Agent Service Development Team
