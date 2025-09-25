# Agent Tools - Backend API Client Alignment Issues

## Overview
Analysis of alignment between agent tools in `agents.py`, backend API client methods in `backend_api_client.py`, and backend router endpoints in `transaction_router.py`.

## Backend Router ✅ Backend API Client Alignment
**Status: PERFECT ALIGNMENT**

All backend router endpoints have corresponding API client methods:
- `GET /transactions/count` → `get_transaction_count()`
- `GET /transactions/filtered/count` → `get_transaction_count_filtered()`
- `GET /transactions/stats` → `get_transactions_stats()`
- `GET /transactions/{transaction_id}/predict` → `predict_transaction()`
- `GET /transactions/` → `get_transactions()`
- `GET /transactions/{transaction_id}` → `get_transaction_by_id()`

## Agent Tools ❌ Backend API Client Issues

### ✅ Working Tools
- `get_transaction_stats_tool` (line 192) ✅
- `get_all_transactions_tool` (line 123) ✅
- `predict_transaction_fraud_tool` (line 215) ✅
- `get_transaction_by_id_tool` (line 278) ✅
- `check_backend_connection_tool` (line 304) ✅

### ❌ Broken Tools

#### 1. `get_all_transactions_by_no_params_tool` (line 78)
**Issue:** Calls `self.backend_client.get_transaction_count()` but description says it should get count by params
**Fix Needed:** Should call `get_transaction_count_filtered()` or rename tool

#### 2. `get_all_transactions_by_params_tool` (line 99-102)
**Issue:** Calls `self.backend_client.get_transaction_count_filtered(column, value)`
**Problem:** API client expects `TransactionFilter` object, not `(column, value)` parameters
**Fix Needed:** Construct proper `TransactionFilter` object

#### 3. `get_transactions_by_customer_tool` (line 146)
**Issue:** Calls `self.backend_client.get_transactions_filtered(customer_id, limit, skip)`
**Problem:** API client expects `(filters: TransactionFilter, limit, skip)`
**Fix Needed:** Create `TransactionFilter` with customer_id filter

#### 4. `get_fraud_transactions_tool` (line 169)
**Issue:** Calls `self.backend_client.get_transactions_filtered(is_fraud, limit, skip)`
**Problem:** API client expects `(filters: TransactionFilter, limit, skip)`
**Fix Needed:** Create `TransactionFilter` with is_fraud filter

#### 5. `search_transactions_by_pararms_tool` (line 255)
**Issue:** Calls `self.backend_client.get_transactions_filtered(column, value, limit, skip)`
**Problem:** API client expects `(filters: TransactionFilter, limit, skip)`
**Fix Needed:** Create `TransactionFilter` with column/value filter

## Root Cause
The main issue is a mismatch between:
- **Agent tools:** Expect to pass individual parameters (`column`, `value`, etc.)
- **API client methods:** Expect structured `TransactionFilter` objects

## Recommended Solutions

### Option 1: Update Agent Tools
Modify agent tools to construct proper `TransactionFilter` objects before calling API client methods.

### Option 2: Add Convenience Methods to API Client
Add wrapper methods in `BackendAPIClient` that accept individual parameters and construct `TransactionFilter` objects internally.

### Option 3: Hybrid Approach
Keep existing API client methods for structured calls, add convenience methods for simple parameter-based calls.

## Impact
- 5 out of 9 agent tools are currently broken
- Agent functionality is significantly impacted
- Users may experience errors when using filtering and search features

## Priority
**HIGH** - Critical functionality is broken and needs immediate attention.