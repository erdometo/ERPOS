# E2E Test Infra: OmniGate ERP OS Website Remake

## Test Philosophy
- Opaque-box, requirement-driven. Derives strictly from `ORIGINAL_REQUEST.md`.
- Verifies DOM nodes, visual styles, interactive behaviors, state transitions, cryptographic integrity, and error resilience.

## Feature Inventory & Test Coverage Mapping
| # | Feature | Requirement Source | Tier 1 (Unit/DOM) | Tier 2 (Boundary) | Tier 3 (Integration) | Tier 4 (Workload) |
|---|---------|-------------------|:-----------------:|:-----------------:|:--------------------:|:-----------------:|
| 1 | F1.1 Bifurcated DAG Visualizer | ORIGINAL_REQUEST §R1 | 5 | 5 | ✓ | ✓ |
| 2 | F1.2 Transport Control Suite | ORIGINAL_REQUEST §R1 | 5 | 5 | ✓ | ✓ |
| 3 | F1.3 Playback Mode Toggle | ORIGINAL_REQUEST §R1 | 5 | 5 | ✓ | ✓ |
| 4 | F1.4 Telemetry Inspector | ORIGINAL_REQUEST §R1 | 5 | 5 | ✓ | ✓ |
| 5 | F2.1 6-Benchmark Dataset Ingestion | ORIGINAL_REQUEST §R2 | 5 | 5 | ✓ | ✓ |
| 6 | F2.2 Live Ingestion Throughput HUD | ORIGINAL_REQUEST §R2 | 5 | 5 | ✓ | ✓ |
| 7 | F3.1 4 Interactive ERP Scenarios | ORIGINAL_REQUEST §R3 | 5 | 5 | ✓ | ✓ |
| 8 | F3.2 Simulated sub-15ms ReAct Stream | ORIGINAL_REQUEST §R3 | 5 | 5 | ✓ | ✓ |
| 9 | F3.3 Ephemeral UI Generator | ORIGINAL_REQUEST §R3 | 5 | 5 | ✓ | ✓ |
| 10 | F4.1 Chained SHA-256 Block Visualizer | ORIGINAL_REQUEST §R4 | 5 | 5 | ✓ | ✓ |
| 11 | F4.2 Simulate Malicious Tamper | ORIGINAL_REQUEST §R4 | 5 | 5 | ✓ | ✓ |
| 12 | F4.3 Cryptographic Repair & Recalculate | ORIGINAL_REQUEST §R4 | 5 | 5 | ✓ | ✓ |
| 13 | F5.1 Enterprise Architecture Comparison | ORIGINAL_REQUEST §R5 | 5 | 5 | ✓ | ✓ |
| 14 | F5.2 Copyable MCP Developer Cards | ORIGINAL_REQUEST §R5 | 5 | 5 | ✓ | ✓ |
| 15 | F5.3 Dark Obsidian Glassmorphic Styling | ORIGINAL_REQUEST §R5 | 5 | 5 | ✓ | ✓ |
| 16 | F5.4 Zero-Dependency Client Demo | ORIGINAL_REQUEST §R5 | 5 | 5 | ✓ | ✓ |

## Test Architecture
- **Primary Automated Test Runner**: `python website/verify_suite.py` (49 test cases across 4 tiers)
- **Structural Runner**: `python website/verify_m1.py`
- **Naming Rule Scanner**: Scan for zero instances of "ActiveGraph" across `website/`

## Acceptance Criteria
1. `python website/verify_m1.py` passes with exit code 0.
2. `python website/verify_suite.py` passes with exit code 0 (40/40 client-side tests pass).
3. Zero occurrences of "ActiveGraph" in any project files (strictly SAG).
4. Full interactive features in browser: Bifurcated DAG playback, 6 benchmarks, 4 ERP scenarios, Ephemeral UI generation, Ledger tamper & repair, MCP copy cards.
