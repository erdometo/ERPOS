# Project: OmniGate ERP OS Website Remake (SAG Showcase)

## Architecture
- **Tech Stack**: Vanilla HTML5, CSS3 (Modern Glassmorphism & Custom Properties), ES6+ JavaScript (Pure Client-Side State, Web Crypto API, SVG/Canvas Rendering).
- **Runtime Model**: 100% Self-contained client-side single-page application (SPA). Zero external backend dependencies for showcase mode.
- **Core Systems**:
  1. `SAG Studio Engine`: Hardware-accelerated Bifurcated DAG Visualizer, multi-benchmark trajectory replay, transport controls, synchronized telemetry inspector.
  2. `Multi-Benchmark Ingestion Hub`: Dynamic ingestion of 6 standard agent benchmark traces with live throughput telemetry.
  3. `Zero-UI Sandbox & Ephemeral Generator`: 4 enterprise ERP workflow simulations, sub-15ms ReAct streaming, runtime compilation of approval widgets, diff tables, and SVG charts.
  4. `Cryptographic Ledger & ZK Audit Suite`: Chained SHA-256 block ledger, cascading downstream invalidation on tamper, sequential cryptographic repair engine.
  5. `Enterprise Architecture & Developer Hub`: Latency comparison matrix (Legacy 850ms/6 hops vs OmniGate 12ms/1 local hop) and copyable MCP integration cards for Claude Code, Cursor, and Google Antigravity.

## Code Layout
- `website/public/index.html`: Unified DOM structure with semantic sections, accessible ARIA roles, and verified test anchors (`#terminal-container`, `#ledger-container`, `#ephemeral-placeholder`, `#ephemeral-ui-container`).
- `website/public/styles.css`: Dark obsidian theme (`#07090e`, `#0d121d`), radiant neon accents (Emerald, Electric Cyan, Indigo, Amber, Crimson), glassmorphic backdrops, glowing node keyframes, and responsive layouts (1024px, 768px, 480px).
- `website/public/app.js`: Modular client-side architecture containing `SAGStudioState`, `BenchmarkRegistry`, `ReActEngine`, `EphemeralUIGenerator`, `CryptoLedgerEngine`, and `MCPCardController`.
- `website/verify_suite.py`: Automated 4-tier verification test suite.
- `website/verify_m1.py`: Structural & layout verification suite.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | F1.1 Bifurcated DAG Visualizer | Upper unguided lane (<35% Emerald, 35-65% Amber, >=65% Crimson), Divergence Point (t_safe), Lower Emerald lane (100% completion) | M2 | ORIGINAL_REQUEST §R1 |
| 2 | F1.2 Transport Control Suite | Play, Pause, Step Next, Step Prev, Jump to t_safe, Reset, Timeline Scrubber, Speed presets (0.25x–10x) | M2 | ORIGINAL_REQUEST §R1 |
| 3 | F1.3 Playback Mode Toggle | Progressive Bloom mode vs Pulse Highlight mode | M2 | ORIGINAL_REQUEST §R1 |
| 4 | F1.4 Telemetry Inspector | Real-time risk gauge, subagent step roles, LLM thoughts, tool/bash actions, stdout observations, semantic entities | M2 | ORIGINAL_REQUEST §R1 |
| 5 | F2.1 6-Benchmark Dataset Ingestion Hub | Switcher & pre-packaged trajectory traces: SWE-bench, InterCode, WebArena, ALFWorld, ToolBench, ATIF | M2 | ORIGINAL_REQUEST §R2 |
| 6 | F2.2 Live Ingestion Throughput HUD | 2,514.5 events/sec, 23,610 episodic events, 15,318 test cases, 1,236 semantic entities | M2 | ORIGINAL_REQUEST §R2 |
| 7 | F3.1 4 Interactive ERP Scenarios | Invoice Anomaly Detection, Inventory Stockout Mitigation, Autonomous SQL Querying, RBAC Security Quarantine | M3 | ORIGINAL_REQUEST §R3 |
| 8 | F3.2 Simulated sub-15ms ReAct Stream | Sub-15ms agent loop latency streaming with subagent role badges & live token stream | M3 | ORIGINAL_REQUEST §R3 |
| 9 | F3.3 Ephemeral UI Generator | On-the-fly interactive approval widgets, before/after diff tables, and dynamic SVG/Canvas charts | M3 | ORIGINAL_REQUEST §R3 |
| 10 | F4.1 Chained SHA-256 Ledger Visualizer | Chained cryptographic blocks with hash pointer inspection | M3 | ORIGINAL_REQUEST §R4 |
| 11 | F4.2 Simulate Malicious Tamper | Modifies historical block payload, causing cascading downstream crimson invalidation | M3 | ORIGINAL_REQUEST §R4 |
| 12 | F4.3 Cryptographic Repair & Recalculate | Sequentially re-hashes downstream blocks and restores emerald integrity | M3 | ORIGINAL_REQUEST §R4 |
| 13 | F5.1 Enterprise Architecture Comparison | Legacy Multi-Tier (850ms, 6 hops) vs OmniGate SAG Agent Link (12ms, 1 local hop) | M1 | ORIGINAL_REQUEST §R5 |
| 14 | F5.2 Copyable MCP Developer Cards | One-click copyable configuration snippets for Claude Code, Cursor, and Google Antigravity | M1 | ORIGINAL_REQUEST §R5 |
| 15 | F5.3 Dark Obsidian Glassmorphic Aesthetics | #07090e, #0d121d, radiant neon accents, responsive across desktop and mobile | M1 | ORIGINAL_REQUEST §R5 |
| 16 | F5.4 Zero-Dependency Client-Side Demo | 100% self-contained demo without backend crashes or console errors; strictly SAG branded | M4 | ORIGINAL_REQUEST §R5 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Shell, Design System, Architecture & MCP Cards | HTML layout structure, dark obsidian CSS tokens, R5 Architecture Matrix, Copyable MCP Cards | None | DONE |
| M2 | SAG Studio & Ingestion Hub | Bifurcated DAG Visualizer, Transport Controls, 6 Benchmark Datasets, Telemetry Inspector | M1 | DONE |
| M3 | Zero-UI Sandbox & Cryptographic Ledger | 4 ERP Scenarios, Ephemeral UI Generator (Widgets, Diffs, Charts), SHA-256 Cascading Tamper & Repair | M1 | DONE |
| M4 | Integration, State Synchronization & Polishing | Full cross-module wiring, keyboard shortcuts, tooltips, responsive polish, zero console errors | M2, M3 | DONE |
| M5 | Final Milestone: 100% E2E Pass & Forensic Audit | Verification against 49 test cases in `verify_suite.py` + Adversarial hardening + Forensic Integrity Audit | M4 | DONE |
