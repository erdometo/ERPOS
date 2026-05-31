# 🧠 OmniGate ERP OS: Agentic Kernel Backend

This is the core execution kernel of the **OmniGate ERP OS**, powered by a FastAPI server, a multi-model database gateway, and an autonomous ReAct agent loop. It coordinates database operations across SQL, Graph, and Vector databases with asynchronous task workers.

This backend supports two run modes: **Local Failover Mode** (zero-dependency, disk-based SQLite/JSON databases) and **Production Orchestration Mode** (.NET Aspire running with standalone host databases).

---

## 🚀 Key Modules & Architecture

### 1. Decoupled Asynchronous Worker (`worker.py` / `local_worker`)
To avoid blocking the HTTP thread, all agent reasoning cycles are executed asynchronously:
*   **Decoupled Worker (`worker.py`)**: A python process launched either standalone or via .NET Aspire. It connects to the shared graph and vector databases, consumes tasks, runs the ReAct execution kernel, and updates SQLite task statuses.
*   **In-Process Fallback (`local_worker`)**: If a message queue broker is not configured, the FastAPI application automatically spins up a background thread that monitors an in-memory thread-safe `queue.Queue`. This guarantees asynchronous execution capabilities without any container infrastructure dependencies.

### 2. Multi-Model Shield Gateway (`middleware.py`)
Acts as a sandbox proxy between executing AI agents and the database layers, enforcing strict security protocols:
*   **Generalized Action Mutation Parser**: Captures database requests through Pydantic (`GeneralizedActionMutation`). It restricts query verbs to safe mutations (`INSERT` and `UPDATE`), preventing execution of destructive actions (`DELETE`, `DROP`, `TRUNCATE`, `RENAME TO`).
*   **Database Schema Evolution Gate**: Allows DBA agents to perform additive schema mutations (`CREATE TABLE`, `ALTER TABLE`) to adapt the system dynamically while blocking table drops.
*   **System Integrity Guard**: Blocks queries targeting system metadata tables or the compliance ledger (`audit_ledger`).
*   **Qdrant Vector Adapter**: Integrates similarity search queries using the unified `query_points` method. Supports localized searches targeting a specific `node_id` via payload field matching. It connects to the standalone Qdrant database (port 6333) and automatically falls back to a local persistent client under `./qdrant_db` when the server is unavailable.
*   **Neo4j Graph Adapter**: Translates traversal instructions to Cypher statements using the official python driver. It connects to the standalone Neo4j database (port 7687) and automatically falls back to a local file-based JSON database (`graph_db.json`) that translates Cypher query actions on-the-fly when the server is unavailable.
*   **Cryptographic Ledger Builder**: Computes SHA-256 signatures for every state change. Each transaction block is signed using:
    `row_hash = SHA256(id + timestamp + action_type + agent_name + action_details + governing_node_id + prev_hash)`

### 3. API Router (`main.py`)
Decouples request ingestion from task execution:
*   `POST /api/query`: Immediately generates a unique task UUID, registers the task in the database with status `pending`, pushes the payload to the queue (RabbitMQ or Local Queue), and returns the `task_id` with HTTP 200.
*   `GET /api/tasks/{task_id}`: Allows the React frontend to poll the execution progress and fetch the final generated Gen-UI dashboard code upon task completion.
*   `POST /api/action/execute`: Executes parameter-mapped SQL updates governed by graph nodes.
*   `GET /api/ledger`: Performs cryptographic verification and returns the audit trail.
*   `GET /api/schema`: Introspects SQL, Graph nodes, and Vector counts to build a dynamic schema overview.

---

## ⚙️ Configuration & Environment Setup

1. **Virtual Environment Setup**:
   Create and activate a python environment:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

2. **Dependencies**:
   Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Keys**:
   Create a `.env` file from the template and optionally configure your key:
   ```bash
   cp .env.template .env
   ```
   *Note: If no API key is specified, the system starts in a simulated mode, allowing full functionality of graph, vector, and ledger updates without calling external LLMs.*

---

## 🗄️ Database Setup & Seeding

We provide three seeding scripts to populate the database layers with structured enterprise records and compliance logic:

1. **Primary Setup (`setup_db.py`)**:
   Clears old sqlite records and initializes the base SQL schemas (`users`, `products`, `orders`, `order_items`, `audit_ledger`, `tasks`, etc.) in `backend/erp_database.db`.
   ```bash
   python setup_db.py
   ```

2. **Enterprise Mock Seeder (`seed_enterprise_data.py`)**:
   Seeds diverse customer and employee accounts, master products, baseline graph workflow nodes, regulatory safety vectors, mock sales orders, and a cryptographically chained audit history ledger.
   ```bash
   python seed_enterprise_data.py
   ```

3. **Wikipedia ERP Knowledge Crawler (`scrape_and_seed_knowledge.py`)**:
   Crawls 19 core ERP business topics from Wikipedia (utilizing built-in offline failover summaries if network requests fail) to populate vector chunks and establish complex relational Neo4j graph nodes. This embeds real-world business logic directly into the gateway.
   ```bash
   python scrape_and_seed_knowledge.py
   ```

---

## 🧪 Safety & Integrity Testing

We provide two separate test suites to verify system boundaries, security sandboxing, role-based clearances, and transaction rollbacks:

### 1. Primary API & Sandbox Tests (`test_api.py`)
Verify the security proxy, cryptographic audit ledger, and circuit breaker protections by running:
```bash
python test_api.py
```
This script performs the following validation steps:
*   **Safe Action Verification**: Executes a valid database update and confirms successful storage.
*   **Safety Sandboxing**: Proposes a destructive `DELETE` statement and confirms it is blocked.
*   **Internal Protection**: Proposes updating the `audit_ledger` directly and confirms it is blocked.
*   **Ledger Audit Checks**: Confirms a clean database logs as valid and verified.
*   **Tamper Intercept**: Updates a ledger row directly in SQLite (simulating an attacker) and confirms the `/api/ledger` endpoint flags the record and fails validation.
*   **RBAC Blocks**: Validates that Customer role is blocked from executing queries, and Employee role is blocked from running database DDL schema modifications.
*   **Asynchronous Execution & Polling**: Dispatches multiple task requests, verifies `/api/query` enqueues them instantly, polls `/api/tasks/{task_id}` until completed, and validates the returned React JSX code.

### 2. Saga Transaction & Clearance Level Tests (`test_saga_rbac.py`)
Verify distributed transaction integrity and role clearance restrictions by running:
```bash
python test_saga_rbac.py
```
This script performs the following validation steps:
*   **Dynamic Clearance Control**: Verifies that users see only data matching their level. Customer (Charlie, level 1) sees only public furniture; Employee (Bob, level 2) sees internal chipsets but no admin software; Admin (Alice, level 3) can access all products.
*   **Distributed Saga (Procure-to-Pay)**: Tests compliant purchases (below $500 spending limit) which auto-deduct stock and complete.
*   **Compensating Rollback Execution**: Tests non-compliant purchases (above $500 limit) which trigger a simulated payment denial, executing backward compensation logic that restores reserved inventory stock and voids the transaction.

