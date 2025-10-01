# Database Update Log

## Date: 2025-10-01

### PostgreSQL Collation Version Mismatch Fix

Fixed collation version mismatch warning in the `fraud_detection` database.

**Issue:**
```
WARNING: database "fraud_detection" has a collation version mismatch
DETAIL: The database was created using collation version 2.41, but the operating system provides version 2.36.
```

**Resolution Steps:**

1. **Reindex the database:**
   ```sql
   REINDEX DATABASE fraud_detection;
   ```

2. **Refresh collation version:**
   ```sql
   ALTER DATABASE fraud_detection REFRESH COLLATION VERSION;
   ```

### pgvector Extension Setup

Enabled the pgvector extension for vector similarity search capabilities (required for RAG implementation).

**Command executed:**
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### How to Connect to PostgreSQL

To run these commands in the future, connect to the PostgreSQL container:

```bash
docker exec -it fraud-detection-postgres psql -U <POSTGRES_USER> -d fraud_detection
```

Replace `<POSTGRES_USER>` with your actual PostgreSQL username from the `.env` file.
