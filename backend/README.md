# OmniGate ERP OS: Agentic Kernel Backend

This is the core execution kernel of the **OmniGate ERP OS**. It is powered by a FastAPI server, a multi-model SQLite database (SQL + Graph + Vector), and an autonomous ReAct agent loop wrapper.

## 🚀 Key Modules

### 1. Multi-Model Shield Gateway (`middleware.py`)
Provides a sandboxed SQL, Graph, and Vector gateway enforcing strict governance policies on LLM queries:
*   **SQL Guardrail**: Evaluates and parses SQL statements via `sqlparse`. Restricts queries to safe, read-only `SELECT` statements for general operational agents.
*   **DBA Schema Evolution**: Safe, additive DDL schema mutations (`CREATE`, `ALTER`). Strictly blocks destructive commands (`DROP`, `DELETE`, `TRUNCATE`, `RENAME TO`).
*   **Graph Traverser**: Traverses the business workflow ledger. Loads Markdown instructions (`skill.md`) governing specific transaction paths.
*   **Vector Search & Localized Partitions**: Maps policy memos, emails, and regulatory documentation to specific graph nodes to give executing agents localized compliance context.

### 2. Autonomous ReAct Execution Engine (`main.py`)
Orchestrates agent reasoning and tool executions:
*   **ReAct Loop**: Runs a step-by-step reasoning cycle (Thought, Action, Arguments, Observation) utilizing GPT-4o if an API key is configured.
*   **7 Integrated Multi-Model Tools**:
    1. `execute_sql` (Read-only transactional table queries)
    2. `execute_ddl` (Additive schema modification)
    3. `traverse_graph` (Retrieve node edges and workflows)
    4. `vector_search` (Global policy search)
    5. `node_vector_search` (Node-specific contextual search)
    6. `evolve_graph_node` (Evolve/insert Graph nodes/edges)
    7. `vectorize_document` (Vectorize and map documents to nodes)
*   **FinOps Circuit Breaker**: Integrates safety thresholds mapping tool execution history. Detects query repetition loops and halts runaway token consumption with a `SYSTEM_INTERRUPT` and diagnostic UI response.
*   **Offline Simulator**: If no OpenAI API Key is present, automatically falls back to an offline simulated engine replicating all database updates, graph alterations, and vector insertions.

### 3. Database Initialization & Seeding (`setup_db.py`)
Sets up the SQLite database (`erp_database.db`) fresh with initial:
*   SQL Tabular tables (`users`, `products`, `orders`, `order_items`)
*   Graph Nodes and edges representing compliance work rules (like *Order Verification Workflow* and *High Value Transaction Policy*)
*   Vector Partitions mapping CEO cashflow emails and regulatory logs directly to Graph nodes.

## ⚙️ Requirements & Installation

1. Create and activate a Python 3.10+ virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```
2. Install python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.template` to `.env` and optionally provide your `OPENAI_API_KEY`:
   ```bash
   cp .env.template .env
   ```

## 🧪 Integration Testing
Verify the backend behavior by running the comprehensive test script:
```bash
python test_api.py
```
This script resets the SQLite file, seeds the database, and sequentially exercises all 5 core tracks:
1. Operational Anomalies Auditing
2. Database Schema DDL Evolution
3. Graph Workflow Node/Edge Evolution
4. Vector Mapped Document Insertion
5. FinOps Circuit Breaker safety loop prevention
