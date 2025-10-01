# LangGraph Checkpoint Persistence with PostgreSQL

## Overview

This document explains how LangGraph automatically manages conversation state persistence using PostgreSQL checkpoints in our fraud detection agent service.

## Key Concept: Automatic Checkpoint Management

**Important:** You never manually save or load checkpoints. LangGraph handles all persistence automatically when you:
1. Pass a `checkpointer` to `create_react_agent()`
2. Provide a `thread_id` in the agent invocation config

## Architecture Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Sends Message                           │
│                    (Frontend → Backend → Agent Service)         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  main.py: stream_agent_query()                                  │
│  ────────────────────────────────────────                       │
│  thread_id = user_query.thread_id or "default"                  │
│  agent._stream_query(agent_input, thread_id)                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  agents.py: _stream_query()                                     │
│  ────────────────────────────────────────────                   │
│  self.agent.astream(                                            │
│      agent_input,                                               │
│      {'configurable': {'thread_id': thread_id}}  ← KEY!         │
│  )                                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│         LangGraph Internal Processing (Automatic)               │
│  ────────────────────────────────────────────                   │
│                                                                 │
│  STEP 1: LOAD CHECKPOINT (Before Processing)                   │
│  ───────────────────────────────────────                        │
│  SQL: SELECT * FROM checkpoints                                 │
│       WHERE thread_id = 'user_123_1234567890'                  │
│                                                                 │
│  • If found: Load previous conversation state                   │
│  • If not found: Start fresh conversation                       │
│                                                                 │
│  ▼                                                              │
│                                                                 │
│  STEP 2: MERGE & PROCESS                                       │
│  ───────────────────────────────────────                        │
│  • Merge loaded history + new user message                      │
│  • Run LLM reasoning                                            │
│  • Execute tools                                                │
│  • Generate response                                            │
│                                                                 │
│  ▼                                                              │
│                                                                 │
│  STEP 3: SAVE CHECKPOINT (After Each Step)                     │
│  ───────────────────────────────────────                        │
│  SQL: INSERT INTO checkpoints (                                 │
│         thread_id,                                              │
│         checkpoint_id,      -- Auto-generated UUID              │
│         checkpoint,         -- JSONB with full state            │
│         metadata,                                               │
│         parent_checkpoint_id                                    │
│       ) VALUES (...)                                            │
│                                                                 │
│  Saved JSONB Structure:                                         │
│  {                                                              │
│    "channel_values": {                                          │
│      "messages": [                                              │
│        {                                                        │
│          "type": "human",                                       │
│          "content": "Show me fraudulent transactions"           │
│        },                                                       │
│        {                                                        │
│          "type": "ai",                                          │
│          "content": "Here are the results..."                   │
│        }                                                        │
│      ]                                                          │
│    }                                                            │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    [Stream Updates to Frontend]
```

## Code Implementation

### 1. Checkpoint Setup (agents.py:77-104)

```python
async def setup(self):
    """Initialize PostgreSQL checkpoint saver"""
    if self.checkpointer is None:
        conn_string = os.getenv("DATABASE_URL")

        # Create async context manager
        self._checkpointer_cm = AsyncPostgresSaver.from_conn_string(conn_string)

        # Enter context manager to get checkpointer instance
        self.checkpointer = await self._checkpointer_cm.__aenter__()

        # Create necessary PostgreSQL tables
        await self.checkpointer.setup()

        # Create agent with checkpointer
        self.agent = create_react_agent(
            model=self.model,
            tools=self.tools,
            checkpointer=self.checkpointer  # ← Enables automatic persistence
        )
```

**Key Point:** By passing `checkpointer` to `create_react_agent()`, all subsequent agent invocations will automatically save/load checkpoints.

### 2. Agent Invocation with thread_id (agents.py:505)

```python
async def _stream_query(self, agent_input, thread_id: str):
    """Stream agent responses with automatic checkpoint management"""

    # LangGraph uses thread_id to:
    # 1. Load previous checkpoints from PostgreSQL
    # 2. Save new checkpoints after each step
    async for stream_mode, chunk in self.agent.astream(
        agent_input,
        {'configurable': {'thread_id': f"{thread_id}"}},  # ← Critical config
        stream_mode=["updates", "custom"]
    ):
        yield update
```

**Key Point:** The `thread_id` in the config tells LangGraph:
- Which conversation to load from PostgreSQL
- Where to save new checkpoints

### 3. Cleanup (agents.py:118-132)

```python
async def cleanup(self):
    """Properly close database connections"""
    if self.checkpointer is not None:
        # Exit the async context manager
        await self._checkpointer_cm.__aexit__(None, None, None)
        self.checkpointer = None
```

## PostgreSQL Schema

### Tables Created by `checkpointer.setup()`

```sql
-- Main checkpoint table
CREATE TABLE checkpoints (
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    checkpoint_id TEXT NOT NULL,
    parent_checkpoint_id TEXT,
    type TEXT,
    checkpoint JSONB NOT NULL,        -- Full conversation state
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
);
CREATE INDEX ON checkpoints (thread_id);

-- Supporting tables
CREATE TABLE checkpoint_blobs (...)      -- Large binary data
CREATE TABLE checkpoint_writes (...)     -- Write tracking
CREATE TABLE checkpoint_migrations (...) -- Schema versioning
```

### Example Checkpoint Data

```sql
SELECT
    thread_id,
    checkpoint_id,
    jsonb_array_length(checkpoint->'channel_values'->'messages') as msg_count,
    checkpoint->'channel_values'->'messages'->-1->>'content' as last_message
FROM checkpoints
WHERE thread_id = 'user_123_1234567890'
ORDER BY checkpoint_id DESC
LIMIT 1;
```

**Result:**
```
 thread_id             | checkpoint_id | msg_count | last_message
-----------------------|---------------|-----------|------------------
 user_123_1234567890   | abc-123-xyz   | 4         | Here are the...
```

## When Are Checkpoints Saved?

Checkpoints are saved **automatically after each graph node execution**:

| Event | Checkpoint Created? | Contains |
|-------|-------------------|----------|
| User sends message | ✅ Yes | User message added to history |
| Agent reasoning starts | ✅ Yes | Agent's thinking process |
| Tool is called | ✅ Yes | Tool invocation details |
| Tool returns result | ✅ Yes | Tool output |
| Agent generates response | ✅ Yes | Final answer |

**Result:** A single user query may create **3-5 checkpoints** depending on complexity.

## Thread ID Management

### Where thread_id is Created

**Backend:** `backend/app/service/message_service.py:144`

```python
async def websocket_conversation_handle(...):
    if not current_conversation_id:
        # NEW CONVERSATION - Generate thread_id
        thread_id = f"user_{user_id}_{int(datetime.now().timestamp())}"

        current_conversation_id = await conversation_service.create_conversation(
            ConversationCreate(
                user_id=user_id,
                title="New Fraud Investigation Session",
                thread_id=thread_id,  # Saved in conversations table
                created_at=datetime.now(),
                metadata_info=initial_metadata
            )
        )
        return current_conversation_id, thread_id
    else:
        # EXISTING CONVERSATION - Retrieve thread_id
        conversation = await conversation_service.get_conversation_by_conversation_id(
            current_conversation_id
        )
        thread_id = conversation.thread_id
        return current_conversation_id, thread_id
```

### Thread ID Flow

```
Frontend                Backend              Agent Service        PostgreSQL
   │                       │                        │                  │
   │  New Chat            │                        │                  │
   │────────────────────>│                        │                  │
   │                       │                        │                  │
   │                       │ Generate thread_id    │                  │
   │                       │ "user_5_1234567890"   │                  │
   │                       │                        │                  │
   │                       │ Save to conversations  │                  │
   │                       │────────────────────────────────────────>│
   │                       │                        │                  │
   │  conversation_started │                        │                  │
   │  {thread_id: ...}    │                        │                  │
   │<─────────────────────│                        │                  │
   │                       │                        │                  │
   │  User Message         │                        │                  │
   │  {thread_id: ...}    │                        │                  │
   │────────────────────>│────────────────────>│                  │
   │                       │                        │                  │
   │                       │                        │ Load checkpoint   │
   │                       │                        │ WHERE thread_id=..│
   │                       │                        │<──────────────────│
   │                       │                        │                  │
   │                       │                        │ Process message   │
   │                       │                        │                  │
   │                       │                        │ Save checkpoint   │
   │                       │                        │ thread_id=...    │
   │                       │                        │───────────────────>│
   │                       │                        │                  │
   │  Agent Response      │                        │                  │
   │<─────────────────────│<─────────────────────│                  │
```

## Conversation Isolation

Each `thread_id` maintains **completely isolated** conversation state:

```python
# Thread 1: user_5_1234567890
# Checkpoints: [msg1, msg2, msg3, msg4]

# Thread 2: user_5_9876543210
# Checkpoints: [msgA, msgB]

# Thread 3: user_7_1111111111
# Checkpoints: [msgX, msgY, msgZ]
```

**Important:** Same user can have multiple independent conversations (different thread_ids).

## Benefits of Automatic Checkpointing

1. ✅ **Conversation Continuity** - Full context preserved across requests
2. ✅ **Crash Recovery** - Agent can resume from last checkpoint after restart
3. ✅ **Multi-turn Conversations** - Agent remembers previous exchanges
4. ✅ **Conversation Branching** - Can explore different reasoning paths
5. ✅ **Debugging** - Inspect exact agent state at any point
6. ✅ **Time-Travel** - Can replay or fork conversations from any checkpoint

## Debugging Checkpoints

### View All Checkpoints for a Thread

```python
# agents.py - Already implemented
async def list_thread_checkpoints(self, thread_id: str):
    """List all checkpoints for debugging"""
    config = {"configurable": {"thread_id": thread_id}}
    checkpoints = list(self.checkpointer.list(config))
    return checkpoints
```

**API Endpoint:** `GET /thread_checkpoints/{thread_id}`

### Get Conversation History

```python
# agents.py - Already implemented
async def get_conversation_history(self, thread_id: str, limit: int = 10):
    """Retrieve conversation history from latest checkpoint"""
    config = {"configurable": {"thread_id": thread_id}}
    checkpoint = await self.checkpointer.aget(config)

    if checkpoint:
        messages = checkpoint.get("channel_values", {}).get("messages", [])
        return messages[-limit:]
    return []
```

**API Endpoint:** `GET /conversation_history/{thread_id}?limit=10`

### SQL Inspection

```sql
-- Count checkpoints per thread
SELECT
    thread_id,
    COUNT(*) as checkpoint_count,
    MAX(checkpoint_id) as latest_checkpoint
FROM checkpoints
GROUP BY thread_id
ORDER BY checkpoint_count DESC;

-- View latest conversation state
SELECT
    thread_id,
    checkpoint->'channel_values'->'messages' as full_conversation
FROM checkpoints
WHERE thread_id = 'user_5_1234567890'
ORDER BY checkpoint_id DESC
LIMIT 1;
```

## Common Patterns

### Pattern 1: New Conversation
```python
# Frontend sends no thread_id
thread_id = "default"  # Fallback in main.py

# LangGraph:
# - No checkpoint found for "default"
# - Starts fresh conversation
# - Saves first checkpoint
```

### Pattern 2: Continuing Conversation
```python
# Frontend sends existing thread_id
thread_id = "user_5_1234567890"

# LangGraph:
# - Finds 5 existing checkpoints
# - Loads latest checkpoint state
# - Merges with new message
# - Saves updated checkpoint
```

### Pattern 3: Multiple Users
```python
# User 5 conversation
thread_id = "user_5_1234567890"  # Isolated state

# User 7 conversation
thread_id = "user_7_9999999999"  # Completely separate state
```

## Performance Considerations

### Checkpoint Size Growth

Each checkpoint contains **full conversation history**. As conversations get longer:

- ✅ **Good:** LangGraph efficiently stores as JSONB (compressed)
- ⚠️ **Watch:** Very long conversations (100+ messages) may slow down
- 💡 **Solution:** Implement conversation summarization or truncation

### Database Load

- Each user message → 3-5 checkpoint writes
- High traffic → Significant PostgreSQL write load
- 💡 **Solution:** Use connection pooling, consider read replicas

## Troubleshooting

### Issue: Checkpoints Not Saving

**Symptoms:** New messages don't have context from previous messages

**Diagnosis:**
```python
# Check if checkpointer is initialized
if self.checkpointer is None:
    raise RuntimeError("Checkpointer not initialized!")

# Check thread_id is being passed
logger.info(f"Using thread_id: {thread_id}")

# Verify PostgreSQL connection
await self.checkpointer.setup()  # Should not raise error
```

### Issue: Connection Closed Error

**Symptoms:** `Error: the connection is closed`

**Cause:** Context manager exited prematurely

**Fix:** Keep context manager open during app lifetime
```python
# WRONG - Connection closes after 'with' block
async with AsyncPostgresSaver.from_conn_string(...) as cp:
    self.checkpointer = cp  # ❌ Connection closed!

# CORRECT - Keep context manager alive
self._checkpointer_cm = AsyncPostgresSaver.from_conn_string(...)
self.checkpointer = await self._checkpointer_cm.__aenter__()  # ✅ Stays open
```

### Issue: Checkpoints for Wrong Thread

**Symptoms:** User sees someone else's conversation

**Cause:** thread_id not passed correctly

**Fix:** Always pass thread_id in config
```python
# WRONG
self.agent.astream(agent_input)  # ❌ Uses default thread

# CORRECT
self.agent.astream(
    agent_input,
    {'configurable': {'thread_id': thread_id}}  # ✅ Explicit thread
)
```

## References

- [LangGraph Checkpointing Docs](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- [PostgreSQL Checkpointer API](https://langchain-ai.github.io/langgraph/reference/checkpoints/#langgraph.checkpoint.postgres.PostgresSaver)
- Our implementation: `agent-service/src/app/agents/agents.py`

---

**Last Updated:** 2025-10-01
**Author:** Agent Service Development Team
