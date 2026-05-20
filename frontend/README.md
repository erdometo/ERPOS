# OmniGate ERP OS: Generative Frontend Terminal

This directory houses the React + TypeScript + Vite frontend client for the **OmniGate ERP OS**. It serves as an interactive glassmorphic terminal where users submit natural language commands to the Agentic Kernel and inspect the dynamically generated interfaces returned in real time.

## 🚀 Key Features

1. **Zero-UI Generative Dashboard Container**:
   - The interface is not static; it contains a placeholder for dynamic, code-compiled React dashboards.
   - When the agent returns code (JSX), the frontend compiles and mounts it on-the-fly.

2. **In-Browser Babel Standalone Sandboxing**:
   - Compiles agent-formulated JSX code directly in the browser environment utilizing the `@babel/standalone` compiler.
   - Dynamically executes custom event callbacks (`onAction`) so generated interactive buttons (e.g., *Approve Waiver*, *Restock 50 Units*) run queries against the backend ledger.

3. **Active Schema Explorer**:
   - Provides a live tab to visualize both tabular relational tables (with data types) and the graph workflow ledger (`skill.md` rules and edge connections) updated dynamically.

4. **Multi-Track Suggestion Command Palette**:
   - Includes test chips to run Operational Audits, SQL Schema Evolution, Graph Workflow Evolution, Vector Document Partitioning, and FinOps Circuit Breaker loops.

5. **Agent Log Stream Terminal**:
   - Displays chronological multi-agent execution traces detailing thoughts, tool invocations, inputs, and observations for deep inspectability and trust auditing.

## 🛠️ Tech Stack & Setup

*   **Core**: React 19, TypeScript 5, Vite 8
*   **Styling**: Modern CSS + TailwindCSS (for utility layout structure)
*   **Icons**: `lucide-react`
*   **Dynamic Compiler**: `@babel/standalone` (loaded via script header in `index.html`)

### Running the Terminal

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Run dev server**:
   ```bash
   npm run dev
   ```

3. **Access UI**:
   Open [http://localhost:5173](http://localhost:5173) in your browser.

## 📁 Key File Structure

*   `src/App.tsx`: The primary container managing system layout, query requests, action callback execution, and log streams. Contains the `DynamicRenderer` component which evaluates Babel-transpiled JSX code inside a sandboxed execution frame.
*   `index.html`: Bootstraps the application, fetching TailwindCSS reset and Babel standalone via CDN for browser-side script compiling.
