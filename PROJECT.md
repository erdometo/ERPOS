# Project: OmniGate ERP OS Website Remake

## Architecture
The OmniGate ERP OS website is a high-performance, single-page enterprise showcase built with vanilla HTML5, CSS3 (modern glassmorphic obsidian theme with custom properties), and modular ES6 JavaScript (`app.js`).
- **Frontend Stack**: Native ES Modules (`app.js`), Zero Build Step / Bundler overhead, Web Crypto API (`crypto.subtle.digest('SHA-256')`).
- **Design System**: Dark Obsidian (`#08060e`, `#0d111d`), Radiant Neon Accents (Emerald `#10b981`, Electric Cyan `#06b6d4`, Indigo `#6366f1`, Amber `#f59e0b`, Crimson `#ef4444`). Fonts: Outfit, Inter, JetBrains Mono.
- **Data Flow**:
  - `SAGStudioEngine` manages the 5-step episodic timeline for bifurcated DAG visualization and telemetry stream.
  - `SimulatorState` & `Workflows` manage the 4 operational ERP sandboxes, ReAct stream generation, and ephemeral card state.
  - Cryptographic Block Ledger manages SHA-256 linked chain with Genesis block (64 zeros), tamper simulation on Block #2, cascading invalidation, and repair/recalculation.
  - ROI Calculator dynamically updates labor savings and error recoup in real time based on slider inputs.
- **Hosting & CI**: Firebase Hosting (`omnigate-erp-os`), GitHub repository `erdometo/ERPOS` on branch `main`.

## Feature Inventory
| # | Feature | Description | Milestone | Status |
|---|---|---|---|---|
| 1 | Dark Obsidian Theme & Typography | Obsidian palette (#08060e, #0d111d), Outfit/Inter/Mono fonts, responsive glassmorphism | M1 | DONE |
| 2 | Act I: Visionary Paradigm Shift | $180B ERP disruption narrative, Zero Static UI value prop, 10x latency comparison | M1 | DONE |
| 3 | Core Engine & DOM Alignment | Fixed syntax error in app.js, unified window.* and ESM exports, aligned container IDs | M1 | DONE |
| 4 | Act II: 4 Operational Sandboxes | Invoice Anomaly, Supply Chain Saga, Dynamic P&L FX, Zero-Trust RBAC Quarantine | M2 | DONE |
| 5 | ReAct Terminal Logs | Streaming [THOUGHT], [ACTION], [OBSERVATION], [SYSTEM] traces with authentic entity graphs | M2 | DONE |
| 6 | Interactive Ephemeral Cards | Stateful cards with functional action buttons (Execute Settlement, Sync Webhooks, etc.) and toast feedback | M2 | DONE |
| 7 | Act III: Proprietary SAG Moat | Technical explanation of Agent Trajectory Problem (83% failure vs SAG t_safe steering) | M3 | DONE |
| 8 | Bifurcated DAG Visualizer | Interactive SVG DAG with synchronized node glow highlights, baseline vs steered tracks | M3 | DONE |
| 9 | Transport Controls & Scrubber | Play/Pause, Step Prev/Next, Jump to t_safe, Reset, Scrubber slider, Speed presets, Risk gauge | M3 | DONE |
| 10 | Act IV: SHA-256 Block Ledger | Real-time Web Crypto SHA-256 chain, Genesis block (64 zeros), tamper block #2, reverify | M4 | DONE |
| 11 | Enterprise ROI Calculator | Grounded enterprise math with interactive Headcount, Revenue, Ops Staff sliders & live recalculation | M4 | DONE |
| 12 | Act V: Social Proof & Benchmarks | SWE-bench 2,294 runs (99.4%), InterCode SQL (98.8%), WebArena, ALFWorld, ToolBench, ATIF | M5 | DONE |
| 13 | Dedicated Contact Section | Prominent Contact section with direct email info@omnigateos.com and 1-click mailto/copy | M5 | DONE |
| 14 | Investor Briefing Modal | Interactive modal dialog with seamless form submission and confirmation state | M5 | DONE |
| 15 | Strict SAG Branding | 100% strict SAG (Semantic Agent Graph) branding, zero occurrences of ActiveGraph | M5 | DONE |
| 16 | 100% Interactive UI & Zero Dead Clicks | Every button, slider, tab, modal, and copy snippet has working event handlers | M6 | DONE |
| 17 | Automated Verification Suite | 100% pass on verify_suite.py, verify_m1.py, test_r1_r2_stress.js, test_r3_r4_stress.js, CDP tests | M6 | DONE |
| 18 | Production Deployment & Git Sync | Deploy to Firebase Hosting (omnigateos.com) and push to GitHub origin/main | M7 | IN_PROGRESS |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|---|---|---|---|
| M1 | Unified Core Engine & UI Architecture | Fix app.js syntax error, align DOM IDs in index.html, implement Contact section, responsive styles | none | DONE |
| M2 | 4 Operational Sandboxes & Ephemeral Cards | Complete 4 ERP workflows, ReAct telemetry streaming, interactive action buttons with toast notifications | M1 | DONE |
| M3 | SAG Bifurcated DAG Visualizer & Transport Sync | SVG node glow animation sync, timeline scrubber, transport controls, risk inspector | M1 | DONE |
| M4 | SHA-256 Block Ledger & Enterprise ROI Calculator | Real-time WebCrypto SHA-256 hashing, tamper simulation, repair recalculation, dynamic ROI sliders | M1 | DONE |
| M5 | Social Proof, Contact Section & Modals | Benchmark cards, direct info@omnigateos.com channel, Investor Briefing modal, strict SAG branding audit | M1 | DONE |
| M6 | Comprehensive Verification & Testing Suite | Run and pass verify_suite.py, verify_m1.py, node stress tests, and headless Chrome CDP tests | M2, M3, M4, M5 | DONE |
| M7 | Production Deployment & Git Sync | Deploy to Firebase Hosting (omnigateos.com) and push clean working tree to GitHub origin/main | M6 | IN_PROGRESS |

## Interface Contracts
### `app.js` ↔ `index.html`
- **Global / ESM Exports**:
  - `window.SAGStudioEngine` / `export const SAGStudioEngine`: Methods `loadBenchmark(id)`, `goToStep(idx)`, `stepPrev()`, `stepNext()`, `jumpToTSafe()`, `reset()`, `togglePlay()`, `setSpeed(spd)`, `setPlaybackMode(mode)`.
  - `window.SimulatorState` / `export const SimulatorState`: Current active scenario, terminal log history, ephemeral UI state.
  - `window.Workflows` / `export const Workflows`: Definitions for `audit`, `inventory_stockout`, `sql_financial`, `rbac_quarantine`.
  - `window.calculateHash` / `export async function calculateHash(index, timestamp, data, previousHash)`.
  - `window.initLedger`, `window.tamperLedgerBlock2`, `window.repairAndRecalculateLedger`, `window.resetLedger`.
  - `window.commitLedgerRebalance`, `window.approveWaiver`, `window.dispatchPurchaseOrder`, `window.quarantineSecurityIncident`.
- **DOM Container IDs**:
  - `terminal-container`, `ledger-container`, `ephemeral-placeholder`, `ephemeral-ui-container`.
  - `dag-visualizer-container`, `dag-timeline-scrubber`, `dag-step-counter`, `dag-telemetry-inspector`, `hud-throughput`.
  - `roi-calculator-container`, `headcount-slider`, `revenue-slider`, `ops-slider`.
  - `contact`, `contact-email-link`, `investor-modal`.

## Code Layout
- `website/public/index.html`: Main SPA document containing Acts I–V, DAG SVG markup, ReAct terminal, ROI sliders, SHA-256 ledger, contact section, and investor modal.
- `website/public/styles.css`: Complete styling rules, obsidian theme custom properties, glassmorphism, pulse keyframes, and media queries.
- `website/public/app.js`: Unified client-side reactive engine, ReAct streamer, DAG visualizer controller, SHA-256 cryptographic ledger, and ROI calculator math.
- `website/builder.py`: Python generator template kept in sync with `public/index.html`.
