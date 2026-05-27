# 🧠 OmniGate ERP OS: Agentic Kernel Backend

This is the core execution kernel of the **OmniGate ERP OS**, powered by a FastAPI server, a multi-model database gateway, and an autonomous ReAct agent loop. It coordinates database operations across SQL, Graph, and Vector databases with asynchronous task workers.

---

## 🚀 Key Modules & Architecture

### 1. Decoupled Asynchronous Worker (`worker.py` / `local_worker`)
To avoid blocking the HTTP thread, all agent reasoning cycles are executed asynchronously:
*   **Decoupled Worker (`worker.py`)**: A standalone python process configured to run inside a Docker container. It connects to **RabbitMQ**, consumes enqueued tasks from `agent_tasks`, sets execution contexts, and evaluates queries against Neo4j, Qdrant, and SQLite.
*   **In-Process Fallback (`local_worker`)**: If RabbitMQ is not available, the FastAPI application automatically spins up a background thread that monitors an in-memory thread-safe `queue.Queue`. This guarantees asynchronous polling capabilities without any container infrastructure dependencies.

### 2. Multi-Model Shield Gateway (`middleware.py`)
Acts as a sandbox proxy between executing AI agents and the database layers, enforcing strict security protocols:
*   **Generalized Action Mutation Parser**: Captures database requests through Pydantic (`GeneralizedActionMutation`). It restricts query verbs to safe mutations (`INSERT` and `UPDATE`), preventing execution of destructive actions (`DELETE`, `DROP`, `TRUNCATE`, `RENAME TO`).
*   **Database Schema Evolution Gate**: Allows DBA agents to perform additive schema mutations (`CREATE TABLE`, `ALTER TABLE`) to adapt the system dynamically while blocking table drops.
*   **System Integrity Guard**: Blocks queries targeting system metadata tables or the compliance ledger (`audit_ledger`).
*   **Qdrant Vector Adapter**: Integrates similarity search queries using the unified `query_points` method. Supports localized searches targeting a specific `node_id` via payload field matching. Falls back to a local persistent client under `./qdrant_db` when no server is present.
*   **Neo4j Graph Adapter**: Translates traversal instructions to Cypher statements using the official python driver. Falls back to a local file-based JSON database (`graph_db.json`) that translates Cypher query actions on-the-fly.
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

## 🧪 Safety & Integrity Testing

Verify the security proxy, cryptographic audit ledger, and circuit breaker protections by running:
```bash
python test_api.py
```

The script performs the following validation steps:
1. **Safe Action Verification**: Executes a valid database update and confirms successful storage.
2. **Safety Sandboxing**: Proposes a destructive `DELETE` statement and confirms it is blocked.
3. **Internal Protection**: Proposes updating the `audit_ledger` directly and confirms it is blocked.
4. **Ledger Audit Checks**: Confirms a clean database logs as valid and verified.
5. **Tamper Intercept**: Updates a ledger row directly in SQLite (simulating an attacker) and confirms the `/api/ledger` endpoint flags the record and fails validation.
6. **RBAC Blocks**: Validates that Customer role is blocked from executing queries, and Employee role is blocked from running database DDL schema modifications.
7. **Asynchronous Execution & Polling**: Dispatches multiple task requests, verifies `/api/query` enqueues them instantly, polls `/api/tasks/{task_id}` until completed, and validates the returned React JSX code.
