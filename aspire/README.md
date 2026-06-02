# 🚀 OmniGate ERP OS: .NET Aspire Orchestration

This directory contains the **.NET Aspire** orchestration solution used to manage the microservices lifecycle, environment configuration, and service discovery across the OmniGate ERP OS application stack.

---

## 🏗️ Project Structure

The solution consists of two main orchestrated projects:

1.  **`Aspire.AppHost`**:
    *   Acts as the central coordinator and entry point.
    *   Defines project references and dependencies for the FastAPI python backend, the background worker daemon, and the Vite React frontend.
    *   Manages environment variables, port bindings, and service-to-service discovery (e.g. routing the React client actions to the python API).
2.  **`Aspire.ServiceDefaults`**:
    *   Provides standard C# extensions for configuring telemetry, metrics, and tracing using **OpenTelemetry**.
    *   Aggregates microservice logs dynamically inside the central Aspire Developer Dashboard.

---

## ⚙️ Developer Environment Overrides

To run the orchestrated stack on environments with manual or localized SDK installations, `Aspire.AppHost/Program.cs` defines a custom configuration helper class (`MyConfigureOptions<T>`). This helper uses C# reflection to intercept Aspire's DCP (Developer Control Plane) options and manually override bin paths to resolve from local NuGet caches:

*   **DCP Executable (`dcp.exe`)**: Resolved directly from:
    `C:\Users\ASUS\.nuget\packages\aspire.hosting.orchestration.win-x64\8.1.0\tools\dcp.exe`
*   **Aspire Dashboard (`Aspire.Dashboard.exe`)**: Resolved directly from:
    `C:\Users\ASUS\.nuget\packages\aspire.dashboard.sdk.win-x64\8.0.0\tools\Aspire.Dashboard.exe`

This ensures full orchestration capabilities work seamlessly without requiring global environment path edits or full Visual Studio integrations.

---

## 🔌 Standalone Database Bindings

Unlike traditional containerized setups, the AppHost orchestrates python projects to bind directly to **standalone host databases** to ensure optimal developer speed and avoid Docker layer virtualization overheads.

The following environmental variables are injected dynamically by the AppHost into both `backend` (FastAPI) and `worker` (python worker) processes:
*   `NEO4J_URI`: `bolt://localhost:7687` (Graph Database connection)
*   `NEO4J_USER`: `neo4j`
*   `NEO4J_PASSWORD`: `password`
*   `QDRANT_HOST`: `localhost` (Vector Database connection)
*   `QDRANT_PORT`: `6333`

*Note: The standalone Neo4j and Qdrant database servers must be active on the host machine before launching the AppHost.*

---

## 💻 Launching the Orchestrated Stack

To start all microservices (backend, background worker, React UI, and telemetry logger) concurrently:

1.  Start the standalone local databases:
    *   Ensure Qdrant is running on port `6333`.
    *   Ensure Neo4j is running on port `7687` (and HTTP console on `7474`).
2.  Navigate to the AppHost directory and run the project:
    ```bash
    cd aspire/Aspire.AppHost/
    dotnet run
    ```
3.  Open the **Aspire Dashboard** at **[http://localhost:18888](http://localhost:18888)** to view live console logs, container states, OTLP tracing tables, and system performance metrics.
