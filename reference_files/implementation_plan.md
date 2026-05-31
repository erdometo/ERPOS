# Implementation Plan: Strictly Containerized .NET Aspire Integration

This plan transitions ERPOS from using local file-based database failovers (SQLite mock graphs, JSON files, local Qdrant directory paths) to a production-grade containerized environment managed entirely by the **.NET Aspire orchestrator**.

---

## Proposed Sub-Agents and Roles

To execute this architecture shift efficiently, we will define and spawn **3 specialized sub-agents** to work in parallel:

1.  **`aspire_configurator` (Role: Aspire Container Engineer)**
    *   **Scope**: Modifies `aspire/Aspire.AppHost/Program.cs` to enforce password authentication for the `neo4j` container (`neo4j/password`), and explicitly routes connection endpoints (Host, Port, URI) to the python API `backend` and `worker` environment parameters.
2.  **`python_refactorer` (Role: Database Adapter Engineer)**
    *   **Scope**: Modifies [middleware.py](file:///c:/Users/ASUS/Desktop/ERPOS/backend/middleware.py), [neo4j_client.py](file:///c:/Users/ASUS/Desktop/ERPOS/backend/storage/neo4j_client.py), and [qdrant_client.py](file:///c:/Users/ASUS/Desktop/ERPOS/backend/storage/qdrant_client.py). Removes `JSONGraphAdapter`, SQLite-based graph fallbacks, and local `qdrant_db` directory paths. Forces connections to fail loudly if standalone Neo4j or Qdrant servers are unavailable.
3.  **`seeder_and_verifier` (Role: Seeder & Validation Engineer)**
    *   **Scope**: Updates database setup and crawling scripts (`setup_db.py`, `seed_enterprise_data.py`, `scrape_and_seed_knowledge.py`) to connect exclusively via container environment endpoints, updates integration tests, runs the seeder, boots Aspire, and confirms visual graphs and vector searches function cleanly.

---

## Proposed Changes

### 1. Aspire AppHost Configuration

#### [MODIFY] [Program.cs](file:///c:/Users/ASUS/Desktop/ERPOS/aspire/Aspire.AppHost/Program.cs)
*   Update `neo4j` to use password authentication: `.WithEnvironment("NEO4J_AUTH", "neo4j/password")`.
*   Link neo4j and qdrant container endpoints directly to backend and worker environment configurations:
    ```csharp
    .WithEnvironment("NEO4J_URI", () => $"bolt://{neo4j.GetEndpoint("bolt").Host}:{neo4j.GetEndpoint("bolt").Port}")
    .WithEnvironment("NEO4J_USER", "neo4j")
    .WithEnvironment("NEO4J_PASSWORD", "password")
    .WithEnvironment("QDRANT_HOST", () => qdrant.GetEndpoint("http").Host)
    .WithEnvironment("QDRANT_PORT", () => qdrant.GetEndpoint("http").Port.ToString());
    ```

### 2. Python Database Adapters Refactoring

#### [MODIFY] [neo4j_client.py](file:///c:/Users/ASUS/Desktop/ERPOS/backend/storage/neo4j_client.py)
*   Delete `JSONGraphAdapter` class completely.
*   Enforce that `Neo4jGraphAdapter` is the only graph client, raising exceptions if connection fails.

#### [MODIFY] [qdrant_client.py](file:///c:/Users/ASUS/Desktop/ERPOS/backend/storage/qdrant_client.py)
*   Remove path-based Qdrant constructor fallback (`client = QdrantClient(path=qdrant_db_path)`).
*   Enforce that it strictly utilizes `QDRANT_HOST` and `QDRANT_PORT` parameters, raising a ConnectionError if they are missing or if client connection fails.

#### [MODIFY] [middleware.py](file:///c:/Users/ASUS/Desktop/ERPOS/backend/middleware.py)
*   Remove `try-except` block falling back to `JSONGraphAdapter`.
*   Ensure initialization of `ShieldGateway` fails loudly if container database connections are absent.

### 3. Setup and Seeding Refactoring

#### [MODIFY] [setup_db.py](file:///c:/Users/ASUS/Desktop/ERPOS/backend/setup_db.py)
*   Remove local file cleanup statements for Qdrant and JSON graph database.
*   Configure setup to strictly connect and verify container database status.

#### [MODIFY] [scrape_and_seed_knowledge.py](file:///c:/Users/ASUS/Desktop/ERPOS/backend/scrape_and_seed_knowledge.py)
*   Enforce exclusive standalone container database updates.

---

## Verification Plan

### Containerized Execution Verification
1.  **Start Aspire orchestrator**: Execute `dotnet run` inside the `aspire/Aspire.AppHost` directory.
2.  **Verify container services**: Monitor startup metrics via Aspire Dashboard. Verify `neo4j` (port 7474/7687) and `qdrant` (port 6333) are up.
3.  **Run Seeder inside container context**: Access backend terminal environment and execute the crawl seeder to ensure it completes without local fallback outputs.
4.  **E2E UI Test**: Load the Vite dashboard at **[http://localhost:5173/](http://localhost:5173/)** and confirm the graph governance topology and audit ledger display correctly from Neo4j container endpoints.
