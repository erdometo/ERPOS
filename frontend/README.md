# 🖥️ OmniGate ERP OS: Generative Frontend Terminal

This is the React + TypeScript + Vite frontend client for the **OmniGate ERP OS**. It serves as a glassmorphic terminal interface where users submit commands to the Agentic Kernel, view agent traces, and interact with dynamically compiled dashboards.

---

## 🎨 Phase 2 UI Upgrades

The terminal is designed with sleek glassmorphic aesthetics, neon indicators, and interactive micro-animations to support Phase 2 functionalities:

### 1. Generative UI Sandbox (`DynamicRenderer`)
*   **Babel Standalone Compilation**: Leverages browser-side `@babel/standalone` to compile agent-formulated JSX code on-the-fly.
*   **Action Intercept System**: Mounts the compiled component with an `onAction` callback. When the user interacts with generated buttons (like *Approve Order* or *Reorder Stock*), the application compiles parameter-mapped SQL updates and submits them to the backend sandbox API at `/api/action/execute`.

### 2. Interactive Schema Explorer & Governance Graph
*   **Visual SVG Topology Map**: A custom SVG canvas rendering the business rules and policy nodes in a live node-link diagram.
    *   **Workflow & Regulation Nodes**: Hover and click interactions to inspect specific nodes.
    *   **Governance Details**: Displays description, active parameters, and bound markdown directives (`skill.md`) immediately on selection.
*   **Active Table Schemas**: Displays SQLite schemas next to the visual topology for side-by-side database structure and agent rule monitoring.

### 3. Append-Only Cryptographic Ledger Timeline
*   **Real-time Chain Verification**: Displays a visual timeline of transaction blocks recorded in the database ledger.
*   **Cryptographic Status Banners**:
    *   🟢 **Green Banner**: Success banner when all blocks have matching, chained SHA-256 signatures.
    *   🔴 **Red Alert Banner**: Glow-shake banner flagging database tampering out-of-band, listing the exact corrupted block indices.
*   **Verification Payload Details**: Clickable panels showing transaction details, timestamps, executing agent, and raw cryptographic signatures (`prev_hash` & `row_hash`).

### 4. Interactive Suggestion Chips
Includes shortcuts to trigger compliance audits, evolutionary schema creations, infinite loop tests (verifying FinOps breakers), and direct cryptographic ledger verifications.

---

## 🛠️ Technology Stack

*   **Framework**: React 19 + Vite 8 (TypeScript)
*   **Styling**: Vanilla CSS (Premium dark mode assets) + TailwindCSS (Play CDN structure)
*   **Icons**: `lucide-react`
*   **Compiler**: In-browser `@babel/standalone`

---

## 🚀 Running the Terminal

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Start Dev Server**:
   ```bash
   npm run dev
   ```

3. **Access Application**:
   Open [http://localhost:5173](http://localhost:5173) in your browser.
