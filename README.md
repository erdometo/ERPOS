# OmniGate ERP OS: Evolutionary Agentic Kernel

Welcome to the **OmniGate ERP OS**, a prototype demonstrating the future of enterprise software: a completely "software-less", UI-less business operating system. In this architecture, autonomous AI agents interact directly with a secure, multi-model database gateway, while generating bespoke, ephemeral user interfaces on-the-fly.

## 🌟 Core Philosophy: Zero UI, Full Governance

Traditional ERPs rely on rigid front-end codebases and complex API wrappers. OmniGate flips this model:
1. **Business Logic is Data**: Workflow instructions are not hardcoded in Python/Java. They are stored natively in the Graph Database as markdown (`skill.md` nodes).
2. **Context is Localized**: Internal rules, CEO directives, and compliance laws are vectorized and strictly mapped to the specific Graph Nodes they govern.
3. **Execution is Sandboxed**: LLMs generate raw SQL and DDL, which passes through a Pydantic-enforced "Shield Gateway" ensuring zero malicious injections or destructive mutations.
4. **UX is Generative**: Based on the exact state of the ledger, a "Vibe Coder" Agent instantly compiles premium, interactive React JSX dashboards in real time.

## 🏗️ Architecture

The system is built on a hybrid data foundation managed within a unified gateway:

*   **Tabular SQL (Transactional)**: Manages fast, structured operations (Users, Products, Orders).
*   **Graph (Operational Rules)**: Nodes represent specific business capabilities (e.g., *Order Verification Workflow*). The properties contain the exact `skill.md` prompt driving the agent.
*   **Vector (Semantic Context)**: Text chunks (e.g., corporate emails, law excerpts) are vectorized and mapped explicitly to Graph Nodes, providing hyper-localized context to the executing agent.

### The Shield Gateway

The backend (`middleware.py`) sits between the LLM and the database, functioning as a multi-model router and security perimeter:
*   **Safe Read Interface**: Permits `SELECT` queries for operational audits.
*   **Safe Mutation Interface**: Validates DDL (`CREATE`, `ALTER`) through strict Pydantic parsers (`DBASchemaMutation`), hard-blocking `DROP` or `TRUNCATE` operations.
*   **Dynamic Introspection**: Exports the active schema (including LLM-created tables) back into the agent context loop.

### FinOps Circuit Breaker

To prevent runaway token consumption or infinite LLM execution loops, the system implements a strict cycle tracker. If an agent loops (e.g., executing the same query 3 times) or exceeds a hard limit, the Kernel throws a `SYSTEM_INTERRUPT`, halting execution and alerting the user.

## 🚀 Running the System

You can run OmniGate in two modes:
*   **Live AI Mode**: If an `OPENAI_API_KEY` is provided in `backend/.env`, the system utilizes GPT-4o for dynamic DDL formulation, compliance auditing, and JSX UI generation.
*   **High-Fidelity Offline Simulator**: If no key is present, the kernel falls back to a robust local simulator. It processes the exact same SQLite reads, graph traversals, and vector filtering, but outputs deterministic JSX to ensure the demo remains fully functional offline.

### 1. Start the Backend Kernel
Navigate to the `backend` directory, activate your environment, and run the FastAPI server:
```bash
cd backend
..\venv\Scripts\activate
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```
*(Note: If running for the first time, execute `python setup_db.py` to seed the hybrid database).*

### 2. Start the Frontend Terminal
Navigate to the `frontend` directory and start the Vite development server:
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173/` in your browser to access the Agentic Kernel Interface. Try triggering a schema mutation like: *"Add courier shipping details to orders table"*.

---
*Built as a prototype for the future of Agent-Native Enterprises.*
