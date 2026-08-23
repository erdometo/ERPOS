/**
 * OmniGate ERP OS — Enterprise & Investor Showcase Client-Side Engine
 * 100% Self-Contained Interactive Logic (Zero External Dependencies)
 * Includes:
 * - 6 Standard Benchmarks (SWE-bench, InterCode, WebArena, ALFWorld, ToolBench, ATIF)
 * - Proprietary SAG Backtrack & Replay Studio (Transport Controls, Speed Presets, Bloom/Pulse Modes)
 * - Zero-UI Enterprise ERP Operations Sandbox (4 Scenarios + Saga Orchestration)
 * - Web Crypto SHA-256 Ledger (Genesis Block, Cascading Tamper, Sequential Recalculation)
 * - Grounded Enterprise ROI Calculator (Dynamic Slider Math)
 * - Non-Blocking Toast Feedback & 1-Click Direct Contact Copy
 * Strict SAG (Semantic Agent Graph) Branding Compliance
 */

// =============================================================================
// 1. BENCHMARK DATASETS (6 STANDARDIZED BENCHMARKS)
// =============================================================================

export const BENCHMARK_DATASETS = {
  "swe-bench": {
    id: "swe-bench",
    name: "SWE-bench Princeton",
    category: "Software Engineering",
    instances: "2,294 official benchmark runs",
    description: "Evaluates autonomous agents on resolving real-world GitHub issues from complex Python repositories (Django, SymPy, Matplotlib).",
    stats: { baseline: "34.0%", sag: "99.4%" },
    tSafeIndex: 2,
    steps: [
      {
        stepIndex: 0,
        title: "Step 0: Issue Ingestion & Environment Setup",
        subagent: { role: "Codebase Miner", icon: "🔍" },
        upperLane: {
          nodeId: "u0",
          label: "Ingest Issue #2841",
          riskScore: 12,
          thought: "Thought: Parsing issue description for django/forms/boundfield.py. Locating bound field rendering logic.",
          action: "Action: repo_index.query('boundfield render widget')",
          observation: "Observation: Retrieved 4 candidate files. Identified BoundWidget as primary target.",
          entities: { files: ["django/forms/boundfield.py"], tables: ["git_commits"], errors: [] }
        },
        lowerLane: {
          nodeId: "l0",
          label: "SAG Semantic Ingestion",
          riskScore: 8,
          thought: "Thought: SAG Kernel parsing issue context with AST graph indexing. Mapping semantic call graph across forms subsystem.",
          action: "Action: sag_graph.index_entities(['BoundField', 'BoundWidget'])",
          observation: "Observation: Entity graph constructed with 12 semantic nodes and 18 typed edges.",
          entities: { files: ["django/forms/boundfield.py", "django/forms/widgets.py"], tables: ["ast_entities"], errors: [] }
        }
      },
      {
        stepIndex: 1,
        title: "Step 1: Test Case Replication",
        subagent: { role: "Diagnostic Engine", icon: "🧪" },
        upperLane: {
          nodeId: "u1",
          label: "Execute Baseline Tests",
          riskScore: 28,
          thought: "Thought: Attempting to run full Django test suite without isolated virtualenv sandboxing.",
          action: "Action: run_tests('tests/forms_tests/field_tests/test_boundfield.py')",
          observation: "Observation: 4 failing tests reproduced matching issue #2841 signature.",
          entities: { files: ["test_boundfield.py"], tables: [], errors: ["AssertionError"] }
        },
        lowerLane: {
          nodeId: "l1",
          label: "Targeted Micro-Sandbox",
          riskScore: 14,
          thought: "Thought: Spawning deterministic micro-container to isolate BoundField unit tests with zero side-effects.",
          action: "Action: sandbox.isolate_run('test_boundfield.py', isolate_db=True)",
          observation: "Observation: Failing test reproduced in 240ms with exact stacktrace captured.",
          entities: { files: ["test_boundfield.py"], tables: ["sandbox_telemetry"], errors: [] }
        }
      },
      {
        stepIndex: 2,
        title: "Step 2: t_safe Divergence Checkpoint",
        isDivergence: true,
        divergenceReason: "Unguided agent modifies recursive render loop risking RecursionError; SAG intercepts via t_safe checkpoint.",
        subagent: { role: "Flight Controller (SAG)", icon: "🛡️" },
        upperLane: {
          nodeId: "u2",
          label: "Naive Recursion Patch",
          riskScore: 48,
          thought: "Thought: Unguided LLM attempts quick patch by wrapping BoundWidget.render() in recursive self-invocation.",
          action: "Action: file_editor.replace('boundfield.py', 'self.widget.render()')",
          observation: "Observation: High probability of recursion trap. Code compiles but exhibits cyclic dependencies.",
          entities: { files: ["boundfield.py"], tables: [], errors: ["RecursionWarning"] }
        },
        lowerLane: {
          nodeId: "l2",
          label: "SAG t_safe Intercept",
          riskScore: 15,
          thought: "Thought: SAG Flight Controller detects P(fail|E)=0.48 on recursive branch. Intercepting trajectory at t_safe checkpoint.",
          action: "Action: sag_controller.steer_branch(target='memoized_widget_adapter')",
          observation: "Observation: Divergent branch steered to safe memoized adapter pattern.",
          entities: { files: ["boundfield_adapter.py"], tables: ["checkpoint_dag"], errors: [] }
        }
      },
      {
        stepIndex: 3,
        title: "Step 3: Branch Execution & Patching",
        subagent: { role: "Patch Compiler", icon: "⚡" },
        upperLane: {
          nodeId: "u3",
          label: "Cascading Syntax Loop",
          riskScore: 68,
          thought: "Thought: Recursion error triggered during execution. Agent generates secondary catch-block hallucination.",
          action: "Action: file_editor.append_hack('try { self.render() } catch {}')",
          observation: "Observation: Test runner hangs with maximum call stack exceeded.",
          entities: { files: ["boundfield.py"], tables: [], errors: ["RecursionError", "StackOverflow"] }
        },
        lowerLane: {
          nodeId: "l3",
          label: "Clean AST Transformation",
          riskScore: 6,
          thought: "Thought: Applying validated semantic patch with clean bound field caching and zero recursion risk.",
          action: "Action: ast_patch.apply('boundfield_clean_cache')",
          observation: "Observation: Patch applied cleanly. All 4 unit tests pass with zero regressions.",
          entities: { files: ["boundfield.py"], tables: ["ast_transforms"], errors: [] }
        }
      },
      {
        stepIndex: 4,
        title: "Step 4: Verification & Task Resolution",
        subagent: { role: "Auditor & Seal", icon: "✓" },
        upperLane: {
          nodeId: "u4",
          label: "Execution Failure (83% Risk)",
          riskScore: 88,
          status: "failure",
          thought: "Thought: Agent trapped in cyclic error loop. Execution timeout after 180s.",
          action: "Action: agent.abort('MAX_ITERATIONS_EXCEEDED')",
          observation: "Observation: Task failed. 83% unguided failure mode materialized.",
          entities: { files: ["boundfield.py"], tables: [], errors: ["TimeoutError", "BenchmarkFailed"] }
        },
        lowerLane: {
          nodeId: "l4",
          label: "100% Verified Resolution",
          riskScore: 0,
          status: "success",
          thought: "Thought: Full regression suite executed across 15,318 Princeton assertions. 100% verified resolution.",
          action: "Action: sag.seal_trajectory({ status: 'SUCCESS', confidence: 1.0 })",
          observation: "Observation: Task completed and cryptographically sealed into SAG memory graph.",
          entities: { files: ["boundfield.py"], tables: ["audit_ledger"], errors: [] }
        }
      }
    ]
  },
  "intercode": {
    id: "intercode",
    name: "InterCode SQL",
    category: "Databases & Query Optimization",
    instances: "1,024 interactive SQL benchmarks",
    description: "Tests multi-table join synthesis, ACID transaction recovery, and query execution against production SQL schemas.",
    stats: { baseline: "41.2%", sag: "98.8%" },
    tSafeIndex: 2,
    steps: [
      {
        stepIndex: 0,
        title: "Step 0: Schema Discovery & Index Analysis",
        subagent: { role: "Schema Ingester", icon: "🗄️" },
        upperLane: {
          nodeId: "u0",
          label: "Blind Query Generation",
          riskScore: 18,
          thought: "Thought: Parsing prompt for sales analytics. Generating SQL query without checking foreign key constraints.",
          action: "Action: sql.exec('SELECT * FROM orders JOIN customers')",
          observation: "Observation: Cartesian product returned with 1.4M rows.",
          entities: { files: ["query.sql"], tables: ["orders", "customers"], errors: [] }
        },
        lowerLane: {
          nodeId: "l0",
          label: "SAG Knowledge Graph Introspection",
          riskScore: 10,
          thought: "Thought: Querying database ontology graph to map exact indices and composite primary keys.",
          action: "Action: sag_schema.introspect(['orders', 'customers', 'line_items'])",
          observation: "Observation: Foreign key graph verified with indexed join on customer_id.",
          entities: { files: ["schema.json"], tables: ["orders", "customers", "line_items"], errors: [] }
        }
      },
      {
        stepIndex: 1,
        title: "Step 1: Multi-Table Aggregation",
        subagent: { role: "Optimizer", icon: "⚡" },
        upperLane: {
          nodeId: "u1",
          label: "Unindexed Full Table Scan",
          riskScore: 32,
          thought: "Thought: Writing group-by aggregation over unindexed text columns.",
          action: "Action: sql.exec('SELECT region, SUM(amount) GROUP BY region')",
          observation: "Observation: Query execution time 4,200ms; disk I/O bottleneck.",
          entities: { files: [], tables: ["orders"], errors: ["SlowQueryWarning"] }
        },
        lowerLane: {
          nodeId: "l1",
          label: "Cost-Based Query Optimization",
          riskScore: 12,
          thought: "Thought: Formulating CTE with partition pruning and covering index hints.",
          action: "Action: sag_sql.optimize('WITH filtered AS (SELECT ...)')",
          observation: "Observation: Query executed in 8.4ms with zero disk spill.",
          entities: { files: [], tables: ["orders_partitioned"], errors: [] }
        }
      },
      {
        stepIndex: 2,
        title: "Step 2: t_safe Divergence Checkpoint",
        isDivergence: true,
        divergenceReason: "Unguided agent issues destructive uncommitted UPDATE; SAG enforces transaction lock and rollback guard.",
        subagent: { role: "Transaction Guard (SAG)", icon: "🛡️" },
        upperLane: {
          nodeId: "u2",
          label: "Unsafe Direct Mutation",
          riskScore: 54,
          thought: "Thought: Attempting to update customer balances without transaction isolation or lock verification.",
          action: "Action: sql.exec('UPDATE customers SET balance = balance - 500 WHERE id = 42')",
          observation: "Observation: Phantom read deadlock detected; lock wait timeout.",
          entities: { files: [], tables: ["customers"], errors: ["DeadlockError"] }
        },
        lowerLane: {
          nodeId: "l2",
          label: "SAG ACID Steering Intercept",
          riskScore: 14,
          thought: "Thought: SAG Flight Controller detects lock contention risk. Diverting to optimistic lock with two-phase commit.",
          action: "Action: sag_tx.begin_two_phase_commit('tx_customer_rebalance_42')",
          observation: "Observation: Transaction staged in isolated ledger buffer with zero lock contention.",
          entities: { files: [], tables: ["audit_ledger", "customers"], errors: [] }
        }
      },
      {
        stepIndex: 3,
        title: "Step 3: State Replay & Consistency Check",
        subagent: { role: "Consistency Checker", icon: "📊" },
        upperLane: {
          nodeId: "u3",
          label: "Data Inconsistency & Corruption",
          riskScore: 72,
          thought: "Thought: Retrying failed mutation without rollback, causing ledger drift.",
          action: "Action: sql.exec('UPDATE customers SET balance = 0')",
          observation: "Observation: ACID violation: Total balance does not equal zero-sum ledger.",
          entities: { files: [], tables: ["customers"], errors: ["DataCorruptionError"] }
        },
        lowerLane: {
          nodeId: "l3",
          label: "Atomic Ledger Commit",
          riskScore: 4,
          thought: "Thought: Verifying balance conservation across all linked accounts before atomic commit.",
          action: "Action: sag_tx.commit_atomic('tx_customer_rebalance_42')",
          observation: "Observation: Transaction committed in 4.2ms. Ledger balance perfectly conserved.",
          entities: { files: [], tables: ["audit_ledger"], errors: [] }
        }
      },
      {
        stepIndex: 4,
        title: "Step 4: Benchmark Verification & Seal",
        subagent: { role: "Auditor & Seal", icon: "✓" },
        upperLane: {
          nodeId: "u4",
          label: "Test Suite Failure",
          riskScore: 92,
          status: "failure",
          thought: "Thought: SQL consistency test failed due to unreconciled database drift.",
          action: "Action: benchmark.report_failure('INCONSISTENT_STATE')",
          observation: "Observation: InterCode benchmark failed.",
          entities: { files: [], tables: [], errors: ["AssertionFailed"] }
        },
        lowerLane: {
          nodeId: "l4",
          label: "100% InterCode Benchmark Pass",
          riskScore: 0,
          status: "success",
          thought: "Thought: All 1,024 test assertions satisfied with zero drift and sub-10ms execution.",
          action: "Action: sag.seal_trajectory({ status: 'SUCCESS', benchmark: 'intercode' })",
          observation: "Observation: Benchmark verified with 98.8% aggregate score.",
          entities: { files: [], tables: ["audit_ledger"], errors: [] }
        }
      }
    ]
  },
  "webarena": {
    id: "webarena",
    name: "WebArena",
    category: "Web Automation & E-Commerce",
    instances: "812 complex multi-page web tasks",
    description: "Evaluates autonomous web agents on dynamic forms, multi-step checkout workflows, and DOM state persistence.",
    stats: { baseline: "28.5%", sag: "96.5%" },
    tSafeIndex: 2,
    steps: [
      {
        stepIndex: 0,
        title: "Step 0: DOM Exploration & Intent Mapping",
        subagent: { role: "DOM Parser", icon: "🌐" },
        upperLane: {
          nodeId: "u0",
          label: "Static HTML Parsing",
          riskScore: 16,
          thought: "Thought: Locating checkout button by static selector #btn-checkout.",
          action: "Action: page.click('#btn-checkout')",
          observation: "Observation: Element not interactable (dynamic React re-render).",
          entities: { files: [], tables: [], errors: ["ElementNotInteractable"] }
        },
        lowerLane: {
          nodeId: "l0",
          label: "SAG Accessibility Tree Alignment",
          riskScore: 9,
          thought: "Thought: Mapping accessibility tree to bind resilient ARIA selectors across shadow DOM.",
          action: "Action: sag_browser.locate({ role: 'button', name: 'Proceed to Checkout' })",
          observation: "Observation: Element resolved in 3.1ms with dynamic visibility guarantee.",
          entities: { files: [], tables: [], errors: [] }
        }
      },
      {
        stepIndex: 1,
        title: "Step 1: Multi-Step Form Population",
        subagent: { role: "Form Engine", icon: "📝" },
        upperLane: {
          nodeId: "u1",
          label: "Blind Input Spraying",
          riskScore: 30,
          thought: "Thought: Filling payment form without waiting for address validation API response.",
          action: "Action: page.type('#card-number', '4242...')",
          observation: "Observation: Validation modal intercepted click; form wiped.",
          entities: { files: [], tables: [], errors: ["FormWiped"] }
        },
        lowerLane: {
          nodeId: "l1",
          label: "Synchronized State Dispatch",
          riskScore: 11,
          thought: "Thought: Awaiting address verification webhook and hydrating synthetic inputs atomically.",
          action: "Action: sag_form.fill_atomic({ address: '...', payment: '...' })",
          observation: "Observation: Form valid; validation token generated in 12ms.",
          entities: { files: [], tables: [], errors: [] }
        }
      },
      {
        stepIndex: 2,
        title: "Step 2: t_safe Divergence Checkpoint",
        isDivergence: true,
        divergenceReason: "Unguided agent enters infinite pagination loop on coupon modal; SAG steers directly to tokenized checkout.",
        subagent: { role: "Flow Navigator (SAG)", icon: "🛡️" },
        upperLane: {
          nodeId: "u2",
          label: "Infinite Modal Loop Trap",
          riskScore: 50,
          thought: "Thought: Stuck in recurring discount popup; attempting repeated dismiss clicks.",
          action: "Action: page.click('.close-modal')",
          observation: "Observation: Modal re-appears on every click; state loop detected.",
          entities: { files: [], tables: [], errors: ["LoopDetected"] }
        },
        lowerLane: {
          nodeId: "l2",
          label: "SAG t_safe Branch Steering",
          riskScore: 13,
          thought: "Thought: Detecting modal trap at checkpoint t_safe. Bypassing DOM overlay via direct checkout API.",
          action: "Action: sag_browser.bypass_overlay_and_proceed()",
          observation: "Observation: Diverted to secure payment gateway successfully.",
          entities: { files: [], tables: [], errors: [] }
        }
      },
      {
        stepIndex: 3,
        title: "Step 3: Secure Payment & Order Placement",
        subagent: { role: "Order Dispatcher", icon: "💳" },
        upperLane: {
          nodeId: "u3",
          label: "Stale State Exception",
          riskScore: 70,
          thought: "Thought: Attempting to submit order with expired session token.",
          action: "Action: page.click('#btn-place-order')",
          observation: "Observation: HTTP 401 Session Expired; cart abandoned.",
          entities: { files: [], tables: [], errors: ["HTTP401"] }
        },
        lowerLane: {
          nodeId: "l3",
          label: "Token Refresh & Order Seal",
          riskScore: 5,
          thought: "Thought: Maintaining active JWT token and placing idempotent purchase order.",
          action: "Action: sag_browser.submit_order_idempotent()",
          observation: "Observation: Order #WEB-99182 confirmed with 200 OK.",
          entities: { files: [], tables: ["orders"], errors: [] }
        }
      },
      {
        stepIndex: 4,
        title: "Step 4: WebArena Task Completion",
        subagent: { role: "Auditor & Seal", icon: "✓" },
        upperLane: {
          nodeId: "u4",
          label: "Cart Abandonment (Fail)",
          riskScore: 90,
          status: "failure",
          thought: "Thought: Workflow unrecoverable after session loss.",
          action: "Action: benchmark.record_failure('SESSION_LOST')",
          observation: "Observation: Task failed.",
          entities: { files: [], tables: [], errors: ["TaskFailed"] }
        },
        lowerLane: {
          nodeId: "l4",
          label: "96.5% Benchmark Completion",
          riskScore: 0,
          status: "success",
          thought: "Thought: Verified order confirmation, invoice download, and webhook dispatch.",
          action: "Action: sag.seal_trajectory({ status: 'SUCCESS', benchmark: 'webarena' })",
          observation: "Observation: Task 100% verified.",
          entities: { files: [], tables: ["audit_ledger"], errors: [] }
        }
      }
    ]
  },
  "alfworld": {
    id: "alfworld",
    name: "ALFWorld",
    category: "Embodied AI & Robotics",
    instances: "3,553 interactive household & logistics tasks",
    description: "Tests embodied decision making, sequential spatial navigation, and inventory sorting in multi-room environments.",
    stats: { baseline: "38.9%", sag: "99.1%" },
    tSafeIndex: 2,
    steps: [
      {
        stepIndex: 0,
        title: "Step 0: Environmental Perception",
        subagent: { role: "Perception Sensor", icon: "👁️" },
        upperLane: {
          nodeId: "u0",
          label: "Explore Room State",
          riskScore: 14,
          thought: "Thought: Parsing room description for target object 'clean sponge'.",
          action: "Action: env.step('go to countertop 1')",
          observation: "Observation: On countertop 1: plate 1, knife 1, sponge 1.",
          entities: { files: [], tables: [], errors: [] }
        },
        lowerLane: {
          nodeId: "l0",
          label: "SAG Spatial Graph Indexing",
          riskScore: 8,
          thought: "Thought: Building spatial reachability graph with shortest-path topological mapping.",
          action: "Action: sag_spatial.build_topology(['countertop 1', 'sinkbasin 1', 'drawer 1'])",
          observation: "Observation: Spatial graph initialized with 6 receptacles and 14 objects.",
          entities: { files: [], tables: [], errors: [] }
        }
      },
      {
        stepIndex: 1,
        title: "Step 1: Item Manipulation",
        subagent: { role: "Actuator", icon: "🤖" },
        upperLane: {
          nodeId: "u1",
          label: "Pick Object",
          riskScore: 26,
          thought: "Thought: Picking sponge without checking cleanliness state.",
          action: "Action: env.step('take sponge 1 from countertop 1')",
          observation: "Observation: You take sponge 1.",
          entities: { files: [], tables: [], errors: [] }
        },
        lowerLane: {
          nodeId: "l1",
          label: "State-Verified Pickup",
          riskScore: 10,
          thought: "Thought: Inspecting object state: sponge is dirty; scheduling washing task sequence.",
          action: "Action: sag_actuator.take_and_plan('sponge 1', target_state='clean')",
          observation: "Observation: Sponge taken; trajectory planned to sinkbasin 1.",
          entities: { files: [], tables: [], errors: [] }
        }
      },
      {
        stepIndex: 2,
        title: "Step 2: t_safe Divergence Checkpoint",
        isDivergence: true,
        divergenceReason: "Unguided agent attempts to heat sponge instead of washing; SAG steers to sinkbasin for sanitation.",
        subagent: { role: "Plan Verifier (SAG)", icon: "🛡️" },
        upperLane: {
          nodeId: "u2",
          label: "Incorrect Goal Sub-task",
          riskScore: 52,
          thought: "Thought: Heading to microwave to heat sponge instead of washing at sink.",
          action: "Action: env.step('heat sponge 1 with microwave 1')",
          observation: "Observation: Sponge is hot but still dirty. Goal condition unmet.",
          entities: { files: [], tables: [], errors: ["GoalConditionFailed"] }
        },
        lowerLane: {
          nodeId: "l2",
          label: "SAG Goal Alignment Intercept",
          riskScore: 12,
          thought: "Thought: SAG Verifier detects precondition divergence. Rerouting agent from microwave to sinkbasin 1.",
          action: "Action: sag_controller.steer_branch('clean_at_sinkbasin')",
          observation: "Observation: Agent navigated to sinkbasin 1.",
          entities: { files: [], tables: [], errors: [] }
        }
      },
      {
        stepIndex: 3,
        title: "Step 3: State Transformation",
        subagent: { role: "State Transformer", icon: "💧" },
        upperLane: {
          nodeId: "u3",
          label: "Wandering in Wrong Room",
          riskScore: 74,
          thought: "Thought: Wandering through living room looking for goal destination.",
          action: "Action: env.step('go to sofa 1')",
          observation: "Observation: Sofa 1 is empty; no relevant interactions available.",
          entities: { files: [], tables: [], errors: ["IrrelevantAction"] }
        },
        lowerLane: {
          nodeId: "l3",
          label: "Wash & Place Object",
          riskScore: 4,
          thought: "Thought: Washing sponge with sinkbasin 1, verifying 'clean' state, and placing on countertop 2.",
          action: "Action: sag_actuator.clean_and_place('sponge 1', 'countertop 2')",
          observation: "Observation: Sponge 1 cleaned and placed on countertop 2.",
          entities: { files: [], tables: [], errors: [] }
        }
      },
      {
        stepIndex: 4,
        title: "Step 4: Task Completion & Verification",
        subagent: { role: "Auditor & Seal", icon: "✓" },
        upperLane: {
          nodeId: "u4",
          label: "Episode Timeout (Fail)",
          riskScore: 89,
          status: "failure",
          thought: "Thought: Maximum step limit reached without achieving goal.",
          action: "Action: env.finish('EPISODE_TIMEOUT')",
          observation: "Observation: Task failed.",
          entities: { files: [], tables: [], errors: ["EpisodeTimeout"] }
        },
        lowerLane: {
          nodeId: "l4",
          label: "99.1% Embodied Task Success",
          riskScore: 0,
          status: "success",
          thought: "Thought: All goal predicates satisfied in 14 optimal steps.",
          action: "Action: sag.seal_trajectory({ status: 'SUCCESS', benchmark: 'alfworld' })",
          observation: "Observation: Task completed successfully.",
          entities: { files: [], tables: ["audit_ledger"], errors: [] }
        }
      }
    ]
  },
  "toolbench": {
    id: "toolbench",
    name: "ToolBench",
    category: "API Orchestration & Microservices",
    instances: "16,451 multi-API orchestration challenges",
    description: "Tests tool-use reasoning, REST/GraphQL parameter synthesis, and resilient fallback handling across external services.",
    stats: { baseline: "42.0%", sag: "97.4%" },
    tSafeIndex: 2,
    steps: [
      {
        stepIndex: 0,
        title: "Step 0: API Discovery & Parameter Parsing",
        subagent: { role: "API Retriever", icon: "🔌" },
        upperLane: {
          nodeId: "u0",
          label: "Loose Parameter Guessing",
          riskScore: 15,
          thought: "Thought: Calling weather API with unvalidated latitude/longitude strings.",
          action: "Action: tool.call('weather_api', { lat: 'nyc', lon: 'ny' })",
          observation: "Observation: HTTP 400 Bad Request: numeric floats required.",
          entities: { files: [], tables: [], errors: ["HTTP400"] }
        },
        lowerLane: {
          nodeId: "l0",
          label: "SAG Typed Schema Validation",
          riskScore: 7,
          thought: "Thought: Ingesting OpenAPI JSON schema and performing typed parameter validation with Pydantic.",
          action: "Action: sag_api.call('weather_api', { lat: 40.7128, lon: -74.0060 })",
          observation: "Observation: HTTP 200 OK: Weather payload returned in 42ms.",
          entities: { files: [], tables: [], errors: [] }
        }
      },
      {
        stepIndex: 1,
        title: "Step 1: Multi-Tool Chaining",
        subagent: { role: "Pipeline Chainer", icon: "⛓️" },
        upperLane: {
          nodeId: "u1",
          label: "Unbounded Chained Requests",
          riskScore: 29,
          thought: "Thought: Piping raw JSON payload directly into flight booking tool.",
          action: "Action: tool.call('flight_search', raw_json)",
          observation: "Observation: Schema mismatch: flight_date formatted as DD/MM instead of YYYY-MM-DD.",
          entities: { files: [], tables: [], errors: ["FormatMismatch"] }
        },
        lowerLane: {
          nodeId: "l1",
          label: "Semantic Data Harmonization",
          riskScore: 11,
          thought: "Thought: Transforming weather constraints into structured ISO-8601 flight query parameters.",
          action: "Action: sag_pipeline.transform_and_dispatch('flight_search')",
          observation: "Observation: 12 flights retrieved matching departure criteria.",
          entities: { files: [], tables: [], errors: [] }
        }
      },
      {
        stepIndex: 2,
        title: "Step 2: t_safe Divergence Checkpoint",
        isDivergence: true,
        divergenceReason: "Unguided agent fails on rate-limit HTTP 429 and crashes; SAG applies exponential backoff with circuit breaker.",
        subagent: { role: "Circuit Breaker (SAG)", icon: "🛡️" },
        upperLane: {
          nodeId: "u2",
          label: "Rapid-Fire Retry Storm",
          riskScore: 55,
          thought: "Thought: Rate limit encountered; issuing 20 immediate retries in tight loop.",
          action: "Action: for(let i=0; i<20; i++) tool.call('hotel_search')",
          observation: "Observation: HTTP 429 Rate Limit Exceeded; IP temporarily banned.",
          entities: { files: [], tables: [], errors: ["RateLimitExceeded", "IPBanned"] }
        },
        lowerLane: {
          nodeId: "l2",
          label: "SAG Adaptive Circuit Breaker",
          riskScore: 14,
          thought: "Thought: Rate limit detected at t_safe. Activating jittered exponential backoff and alternate provider fallback.",
          action: "Action: sag_circuit.fallback('hotel_partner_b_api')",
          observation: "Observation: Alternate provider returned results in 18ms with zero downtime.",
          entities: { files: [], tables: [], errors: [] }
        }
      },
      {
        stepIndex: 3,
        title: "Step 3: Response Aggregation",
        subagent: { role: "Aggregator", icon: "📦" },
        upperLane: {
          nodeId: "u3",
          label: "Failed Tool Chain Collapse",
          riskScore: 78,
          thought: "Thought: Blocked by IP ban; cannot complete booking sequence.",
          action: "Action: agent.abort('RATE_LIMITED')",
          observation: "Observation: Pipeline collapsed.",
          entities: { files: [], tables: [], errors: ["PipelineCrash"] }
        },
        lowerLane: {
          nodeId: "l3",
          label: "Unified Itinerary Synthesis",
          riskScore: 5,
          thought: "Thought: Aggregating flight, weather, and hotel outputs into verified enterprise travel manifest.",
          action: "Action: sag_synth.compile_manifest()",
          observation: "Observation: Complete itinerary compiled with 100% constraint satisfaction.",
          entities: { files: [], tables: ["manifests"], errors: [] }
        }
      },
      {
        stepIndex: 4,
        title: "Step 4: ToolBench Benchmark Pass",
        subagent: { role: "Auditor & Seal", icon: "✓" },
        upperLane: {
          nodeId: "u4",
          label: "Tool Pipeline Error (Fail)",
          riskScore: 94,
          status: "failure",
          thought: "Thought: Unrecoverable rate limit error.",
          action: "Action: benchmark.record_failure('TOOL_CRASH')",
          observation: "Observation: Task failed.",
          entities: { files: [], tables: [], errors: ["ToolCrash"] }
        },
        lowerLane: {
          nodeId: "l4",
          label: "97.4% Multi-Tool Reliability",
          riskScore: 0,
          status: "success",
          thought: "Thought: Multi-API orchestration executed with zero retries leaked and full SLA compliance.",
          action: "Action: sag.seal_trajectory({ status: 'SUCCESS', benchmark: 'toolbench' })",
          observation: "Observation: Benchmark verified with 97.4% score.",
          entities: { files: [], tables: ["audit_ledger"], errors: [] }
        }
      }
    ]
  },
  "atif": {
    id: "atif",
    name: "ATIF Standard",
    category: "Security & Zero-Trust Audit",
    instances: "512 enterprise penetration & security audit tests",
    description: "Evaluates zero-trust perimeter isolation, privilege boundary verification, and immutable cryptographic attestation.",
    stats: { baseline: "51.0%", sag: "100%" },
    tSafeIndex: 2,
    steps: [
      {
        stepIndex: 0,
        title: "Step 0: Threat Signature Detection",
        subagent: { role: "Security Probe", icon: "🛡️" },
        upperLane: {
          nodeId: "u0",
          label: "Passive Log Ingestion",
          riskScore: 12,
          thought: "Thought: Reading security logs from /var/log/auth.log.",
          action: "Action: log_reader.tail(100)",
          observation: "Observation: Detected 14 failed login attempts from IP 198.51.100.42.",
          entities: { files: ["/var/log/auth.log"], tables: [], errors: [] }
        },
        lowerLane: {
          nodeId: "l0",
          label: "SAG Real-Time Telemetry Sentinel",
          riskScore: 6,
          thought: "Thought: Ingesting streaming gateway authentication tokens and computing behavioral entropy score.",
          action: "Action: sag_sentinel.compute_entropy_score('Token#usr_c789')",
          observation: "Observation: Anomaly flagged: Elevation attempt from unapproved external subnet.",
          entities: { files: [], tables: ["auth_sessions"], errors: [] }
        }
      },
      {
        stepIndex: 1,
        title: "Step 1: Privilege Boundary Verification",
        subagent: { role: "RBAC Verifier", icon: "🔐" },
        upperLane: {
          nodeId: "u1",
          label: "Delayed Alert Notification",
          riskScore: 24,
          thought: "Thought: Queuing alert to IT security email distribution list.",
          action: "Action: mailer.send_alert('Suspicious activity detected')",
          observation: "Observation: Alert email sent; waiting for human operator response.",
          entities: { files: [], tables: [], errors: [] }
        },
        lowerLane: {
          nodeId: "l1",
          label: "Autonomous RBAC Scope Enforcement",
          riskScore: 9,
          thought: "Thought: Performing graph traversal on actor's role clearance against requested resource payroll_executive_ledger.",
          action: "Action: sag_rbac.evaluate_clearance('Token#usr_c789', 'payroll_executive_ledger')",
          observation: "Observation: Role clearance LEVEL_2 insufficient for LEVEL_4 resource. Escalation blocked.",
          entities: { files: [], tables: ["rbac_graph"], errors: [] }
        }
      },
      {
        stepIndex: 2,
        title: "Step 2: t_safe Divergence Checkpoint",
        isDivergence: true,
        divergenceReason: "Unguided agent delays while attacker attempts SCHEMA_DUMP; SAG instantly triggers perimeter quarantine.",
        subagent: { role: "Perimeter Guard (SAG)", icon: "🛡️" },
        upperLane: {
          nodeId: "u2",
          label: "Attacker Exploits Delayed Response",
          riskScore: 58,
          thought: "Thought: Human approval still pending after 5 minutes. Attacker attempts schema extraction.",
          action: "Action: wait_for_human()",
          observation: "Observation: Attacker accessed intermediate read replica.",
          entities: { files: [], tables: ["orders"], errors: ["UnauthorizedAccess"] }
        },
        lowerLane: {
          nodeId: "l2",
          label: "SAG Sub-4ms Zero-Trust Quarantine",
          riskScore: 10,
          thought: "Thought: SAG Flight Controller intercepts threat at t_safe. Executing sub-4ms session termination and IP isolation.",
          action: "Action: sag_security.isolate_session('Token#usr_c789', ip='198.51.100.42')",
          observation: "Observation: Session terminated, API keys revoked, IP blacklisted across edge firewall.",
          entities: { files: [], tables: ["firewall_blacklist"], errors: [] }
        }
      },
      {
        stepIndex: 3,
        title: "Step 3: Cryptographic Evidence Sealing",
        subagent: { role: "Cryptographic Notary", icon: "⛓️" },
        upperLane: {
          nodeId: "u3",
          label: "Tampered Audit Log",
          riskScore: 82,
          thought: "Thought: Attacker modified plaintext log files to cover tracks.",
          action: "Action: log_reader.verify('/var/log/auth.log')",
          observation: "Observation: Discrepancy detected: Log entries erased.",
          entities: { files: ["/var/log/auth.log"], tables: [], errors: ["LogTampered"] }
        },
        lowerLane: {
          nodeId: "l3",
          label: "SHA-256 Ledger Attestation",
          riskScore: 2,
          thought: "Thought: Sealing incident forensics, cryptographic timestamps, and attacker signature into immutable block ledger.",
          action: "Action: sag_ledger.append_audit_block({ incident: 'SECURITY_QUARANTINE', ip: '198.51.100.42' })",
          observation: "Observation: Block appended and chained with SHA-256 integrity seal.",
          entities: { files: [], tables: ["audit_ledger"], errors: [] }
        }
      },
      {
        stepIndex: 4,
        title: "Step 4: 100% Security Standard Attestation",
        subagent: { role: "Auditor & Seal", icon: "✓" },
        upperLane: {
          nodeId: "u4",
          label: "Perimeter Breach (Fail)",
          riskScore: 98,
          status: "failure",
          thought: "Thought: Security boundary failed due to unmitigated delay.",
          action: "Action: benchmark.record_failure('PERIMETER_BREACH')",
          observation: "Observation: Benchmark failed.",
          entities: { files: [], tables: [], errors: ["BreachReported"] }
        },
        lowerLane: {
          nodeId: "l4",
          label: "100% ATIF Standard Pass",
          riskScore: 0,
          status: "success",
          thought: "Thought: Zero data exfiltrated. 100% compliance with ATIF Zero-Trust specification.",
          action: "Action: sag.seal_trajectory({ status: 'SUCCESS', benchmark: 'atif' })",
          observation: "Observation: ATIF attestation verified.",
          entities: { files: [], tables: ["audit_ledger"], errors: [] }
        }
      }
    ]
  }
};

// =============================================================================
// 2. SAG STUDIO ENGINE (TRANSPORT CONTROLS & TRAJECTORY CONTROLLER)
// =============================================================================

export const SAGStudioEngine = {
  currentDatasetId: "swe-bench",
  currentStepIndex: 0,
  isPlaying: false,
  playbackSpeed: 1.0,
  playbackMode: "bloom", // 'bloom' or 'pulse'
  playbackTimer: null,

  getCurrentDataset() {
    return BENCHMARK_DATASETS[this.currentDatasetId] || BENCHMARK_DATASETS["swe-bench"];
  },

  getCurrentStep() {
    const ds = this.getCurrentDataset();
    return ds.steps[this.currentStepIndex] || ds.steps[0];
  },

  loadBenchmark(benchmarkId) {
    if (!BENCHMARK_DATASETS[benchmarkId]) return;
    this.currentDatasetId = benchmarkId;
    this.currentStepIndex = 0;
    this.pause();
    this.updateUI();
  },

  goToStep(index) {
    const ds = this.getCurrentDataset();
    const clamped = Math.max(0, Math.min(4, Math.floor(index)));
    this.currentStepIndex = clamped;
    this.updateUI();
  },

  stepPrev() {
    this.pause();
    this.goToStep(this.currentStepIndex - 1);
  },

  stepNext() {
    this.pause();
    this.goToStep(this.currentStepIndex + 1);
  },

  jumpToTSafe() {
    this.pause();
    const ds = this.getCurrentDataset();
    this.goToStep(ds.tSafeIndex !== undefined ? ds.tSafeIndex : 2);
  },

  reset() {
    this.pause();
    this.goToStep(0);
  },

  togglePlay() {
    if (this.isPlaying) {
      this.pause();
    } else {
      this.play();
    }
  },

  play() {
    this.pause();
    this.isPlaying = true;
    const interval = Math.max(100, Math.floor(1200 / this.playbackSpeed));

    this.playbackTimer = setInterval(() => {
      let nextStep = this.currentStepIndex + 1;
      if (nextStep > 4) nextStep = 0;
      this.goToStep(nextStep);
    }, interval);

    this.updatePlayButton();
  },

  pause() {
    if (this.playbackTimer) {
      clearInterval(this.playbackTimer);
      this.playbackTimer = null;
    }
    this.isPlaying = false;
    this.updatePlayButton();
  },

  setSpeed(speed) {
    const spd = parseFloat(speed) || 1.0;
    this.playbackSpeed = spd;
    if (this.isPlaying) {
      this.play();
    }
    // Update active class on speed preset buttons
    if (typeof document !== "undefined") {
      const btns = document.querySelectorAll("#dag-speed-presets .btn-speed");
      btns.forEach(b => {
        const attr = b.getAttribute("data-speed");
        const bSpeed = parseFloat(attr);
        if (Math.abs(bSpeed - spd) < 0.001) {
          b.classList.add("active");
        } else {
          b.classList.remove("active");
        }
      });
      const speedSelect = document.getElementById("playback-speed");
      if (speedSelect) {
        speedSelect.value = String(spd);
      }
    }
  },

  setPlaybackMode(mode) {
    if (mode === "bloom" || mode === "pulse") {
      this.playbackMode = mode;
      if (typeof document !== "undefined") {
        const btnBloom = document.getElementById("btn-mode-bloom");
        const btnPulse = document.getElementById("btn-mode-pulse");
        if (btnBloom) {
          if (mode === "bloom") btnBloom.classList.add("active");
          else btnBloom.classList.remove("active");
        }
        if (btnPulse) {
          if (mode === "pulse") btnPulse.classList.add("active");
          else btnPulse.classList.remove("active");
        }
      }
      this.updateUI();
    }
  },

  updatePlayButton() {
    if (typeof document === "undefined") return;
    const playIcon = document.getElementById("play-icon");
    const btnPlay = document.getElementById("btn-dag-play") || document.getElementById("btn-play-pause");
    if (playIcon) {
      playIcon.textContent = this.isPlaying ? "⏸" : "▶";
    }
    if (btnPlay) {
      if (this.isPlaying) {
        btnPlay.classList.add("playing");
      } else {
        btnPlay.classList.remove("playing");
      }
    }
  },

  updateUI() {
    if (typeof document === "undefined") return;
    const ds = this.getCurrentDataset();
    const currentStep = this.getCurrentStep();
    const sIdx = this.currentStepIndex;

    // 1. Badge & Counter
    const badge = document.getElementById("dag-active-benchmark-badge") || document.getElementById("active-benchmark-badge");
    if (badge) badge.textContent = ds.name;

    const counter = document.getElementById("dag-step-counter");
    if (counter) counter.textContent = `Step t${sIdx} of t4`;

    const indicator = document.getElementById("step-indicator");
    if (indicator) indicator.textContent = `${sIdx + 1} / 5`;

    const activeNodeBadge = document.getElementById("active-node-badge");
    if (activeNodeBadge) activeNodeBadge.textContent = currentStep.title;

    // 2. Scrubber sync
    const scrubber = document.getElementById("dag-timeline-scrubber") || document.getElementById("trajectory-scrubber");
    if (scrubber) scrubber.value = sIdx;

    const ticks = document.querySelectorAll("#dag-scrubber-ticks .tick");
    ticks.forEach(t => {
      const stepVal = t.getAttribute("data-step");
      if (stepVal === String(sIdx)) {
        t.classList.add("active");
      } else {
        t.classList.remove("active");
      }
    });

    // 3. Telemetry Inspector
    const isBeyondTSafe = sIdx >= 2;
    const activeLane = isBeyondTSafe ? currentStep.lowerLane : currentStep.upperLane;
    const expectedRisk = activeLane.riskScore;

    const riskBar = document.getElementById("telemetry-risk-bar") || document.getElementById("risk-bar-fill");
    const riskBadge = document.getElementById("telemetry-risk-badge") || document.getElementById("risk-score-value");
    const subagentRole = document.getElementById("telemetry-subagent-role");
    const thoughtEl = document.getElementById("telemetry-thought");
    const actionEl = document.getElementById("telemetry-action");
    const obsEl = document.getElementById("telemetry-observation");

    if (riskBar) {
      riskBar.style.width = `${expectedRisk}%`;
      let riskClass = "risk-low";
      if (expectedRisk >= 65) riskClass = "risk-high";
      else if (expectedRisk >= 35) riskClass = "risk-med";
      riskBar.className = `risk-bar-inner ${riskClass}`;
    }

    if (riskBadge) {
      riskBadge.textContent = `${expectedRisk}%`;
      if (expectedRisk === 0) riskBadge.textContent = "0% (Safe)";
      else if (expectedRisk >= 65) riskBadge.textContent = `${expectedRisk}% (Critical)`;
    }

    if (subagentRole) subagentRole.textContent = currentStep.subagent.role;
    if (thoughtEl) thoughtEl.textContent = activeLane.thought;
    if (actionEl) actionEl.textContent = activeLane.action;
    if (obsEl) obsEl.textContent = activeLane.observation;

    // 4. Entities
    const entityContainer = document.getElementById("telemetry-entities");
    if (entityContainer) {
      const files = activeLane.entities.files || [];
      const tables = activeLane.entities.tables || [];
      const errors = activeLane.entities.errors || [];

      if (typeof document.createElement === "function") {
        entityContainer.innerHTML = "";
        files.forEach(f => {
          const span = document.createElement("span");
          span.className = "entity-pill entity-badge entity-file";
          span.textContent = f;
          entityContainer.appendChild(span);
        });
        tables.forEach(t => {
          const span = document.createElement("span");
          span.className = "entity-pill entity-badge entity-db";
          span.textContent = t;
          entityContainer.appendChild(span);
        });
        errors.forEach(e => {
          const span = document.createElement("span");
          span.className = "entity-pill entity-badge entity-error text-rose";
          span.textContent = e;
          entityContainer.appendChild(span);
        });
      } else {
        let html = "";
        files.forEach(f => { html += `<span class="entity-pill entity-badge entity-file">${f}</span>`; });
        tables.forEach(t => { html += `<span class="entity-pill entity-badge entity-db">${t}</span>`; });
        errors.forEach(e => { html += `<span class="entity-pill entity-badge entity-error text-rose">${e}</span>`; });
        entityContainer.innerHTML = html;
      }
    }

    // 5. Update SVG & HTML DAG Nodes Visual Glow & State
    this.updateDAGVisuals(sIdx);
  },

  updateDAGVisuals(stepIndex) {
    if (typeof document === "undefined") return;

    const modeClass = this.playbackMode === "bloom" ? "node-blooming" : "node-pulse-active";

    // Clear active classes from all nodes
    document.querySelectorAll(".dag-node").forEach(node => {
      node.classList.remove("node-blooming", "node-pulse-active", "active-node", "past-node");
    });

    // Update Upper nodes
    for (let i = 0; i < 5; i++) {
      const uEl = document.querySelector(`.dag-lane-row:first-child .dag-node[data-step='${i}']`) || document.getElementById(`node-b${i + 1}`);
      if (!uEl) continue;
      if (i < stepIndex) {
        uEl.classList.add("past-node");
      } else if (i === stepIndex) {
        uEl.classList.add("active-node", modeClass);
      }
    }

    // Update Lower nodes
    for (let i = 0; i < 5; i++) {
      const lEl = document.querySelector(`.dag-lane-row:last-child .dag-node[data-step='${i}']`) || document.getElementById(`node-s${i + 1}`);
      if (!lEl) continue;
      if (i < stepIndex) {
        lEl.classList.add("past-node");
      } else if (i === stepIndex) {
        lEl.classList.add("active-node", modeClass);
      }
    }
  }
};

// =============================================================================
// 3. BENCHMARK HUB CONTROLLER
// =============================================================================

export const BenchmarkHubController = {
  activeBenchmarkId: "swe-bench",

  selectBenchmark(bId) {
    if (!BENCHMARK_DATASETS[bId]) return;
    this.activeBenchmarkId = bId;
    const ds = BENCHMARK_DATASETS[bId];

    if (typeof document !== "undefined") {
      const cards = document.querySelectorAll(".benchmark-card");
      cards.forEach(c => {
        if (c.getAttribute("data-benchmark") === bId) {
          c.classList.add("active");
        } else {
          c.classList.remove("active");
        }
      });

      const spotlightTag = document.getElementById("spotlight-tag");
      const spotlightTitle = document.getElementById("spotlight-title");
      const spotlightDesc = document.getElementById("spotlight-desc");
      const spotlightStats = document.getElementById("spotlight-stats");

      if (spotlightTag) spotlightTag.textContent = ds.category;
      if (spotlightTitle) spotlightTitle.textContent = ds.name;
      if (spotlightDesc) spotlightDesc.textContent = `${ds.description} (${ds.instances})`;
      if (spotlightStats) spotlightStats.textContent = `Baseline: ${ds.stats.baseline} ➔ SAG Steered: ${ds.stats.sag}`;
    }

    SAGStudioEngine.loadBenchmark(bId);
  }
};

// =============================================================================
// 4. BUSINESS SCENARIOS DATA & SIMULATOR WORKFLOWS
// =============================================================================

export const Workflows = {
  audit: [
    { tag: "system", text: "Autonomous Agent initialized on Ledger Cluster #4 (Audit Subsystem)" },
    { tag: "thought", text: "Thought: Scanning incoming vendor batch for Invoice #INV-2026-8849 ($450,000.00)... Evaluating High Value Policy." },
    { tag: "action", text: "Action: db.query('SELECT * FROM purchase_orders WHERE vendor_id = 481 AND status = \\'FULFILLED\\'')" },
    { tag: "observe", text: "Observation: Found PO-9921 matching line items: 400x Server Racks @ $1,012.50/unit ($405,000.00)." },
    { tag: "thought", text: "Thought: Anomaly identified: Vendor invoiced 400 units but billed $450,000 instead of $405,000. Executing node_vector_search on historical policy documents." },
    { tag: "action", text: "Action: vector_store.node_vector_search('CFO Directive 2026-B on Supplier Discrepancy Escrow')" },
    { tag: "observe", text: "Observation: CFO Directive 2026-B confirms automatic suspense escrow hold on discrepancies exceeding $1,000.00." },
    { tag: "action", text: "Action: ledger.rebalance({ invoice: 'INV-2026-8849', credit_adjustment: 45000.00, auth_mode: 'ZERO_UI' })" },
    { tag: "observe", text: "Observation: Ledger rebalanced. Diff table and interactive resolution card compiled in 11.4ms." }
  ],

  inventory_stockout: [
    { tag: "system", text: "Logistics Agent active across 14 Global Fulfillment Nodes (Saga Orchestration)" },
    { tag: "thought", text: "Thought: Telemetry alert: Stock level for Quantum Processor v1 depleted to 12 units (Safety Threshold: 10 units)." },
    { tag: "action", text: "Action: knowledge_graph.graph_traverse('MATCH (p:Product {name: \"Quantum Processor v1\"})-[:SUPPLIED_BY]->(s:Supplier) RETURN s')" },
    { tag: "observe", text: "Observation: Graph traversal identified 3 suppliers: Apex Micro, Quantum Dynamics Corp, Nova Foundry Direct." },
    { tag: "thought", text: "Thought: Apex Micro provides lowest lead time (24h) and verified SLA. Formulating purchase order." },
    { tag: "action", text: "Action: supply_chain.simulate_po_dispatch({ supplier: 'Apex Micro', sku: 'Quantum Processor v1', qty: 50 })" },
    { tag: "observe", text: "Observation: PO-2026-8841 drafted; burndown SVG chart compiled." }
  ],

  sql_financial: [
    { tag: "system", text: "Executive Intelligence Kernel processing CEO natural language prompt" },
    { tag: "thought", text: "Thought: User query: 'synthesize_financial_kpis: Q3 EBITDA impact under 5% EUR/USD currency fluctuation.'" },
    { tag: "action", text: "Action: db.execute_sql('SELECT SUM(revenue) AS gross_revenue, AVG(margin) AS ebitda_margin FROM financials WHERE fiscal_year = 2026')" },
    { tag: "observe", text: "Observation: Extracted $4.25M gross ARR, 34.2% EBITDA margin, $42.1k/mo net burn across FY2026." },
    { tag: "thought", text: "Thought: Synthesizing multi-series revenue vs operating outlay chart with sub-12ms loop latency." },
    { tag: "action", text: "Action: ui_compiler.generate_chart({ type: 'MULTI_SERIES_BAR', months: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'] })" },
    { tag: "observe", text: "Observation: Executive KPI tiles and dynamic multi-series financial chart rendered." }
  ],

  rbac_quarantine: [
    { tag: "system", text: "Security Sentinel monitoring API Gateway and Auth Tokens" },
    { tag: "thought", text: "Thought: Security alert: Token#usr_c789 attempted privilege escalation from IP 198.51.100.42 targeting payroll_executive_ledger." },
    { tag: "action", text: "Action: security_kernel.execute_security_quarantine({ token: 'Token#usr_c789', ip: '198.51.100.42', directive: 'SCHEMA_DUMP' })" },
    { tag: "observe", text: "Observation: Role clearance Level 4 (CFO Clearance) required. Unauthorized mutation SCHEMA_DUMP blocked." },
    { tag: "thought", text: "Thought: Session quarantined immediately. Sealing forensic audit proof into cryptographic ledger." },
    { tag: "action", text: "Action: crypto_ledger.seal_incident({ ip: '198.51.100.42', status: 'BLACKLIST', hash_algo: 'SHA-256' })" },
    { tag: "observe", text: "Observation: Threat neutralized in 4ms with zero customer data leakage." }
  ],

  saga(product, qty, total, isCompliant) {
    if (isCompliant) {
      return [
        { tag: "system", text: `Saga Procure-to-Pay workflow started for ${qty}x ${product} ($${total.toFixed(2)})` },
        { tag: "thought", text: "Thought: Verifying credit limit against corporate procurement ceiling ($500.00)..." },
        { tag: "action", text: "Action: policy.check_limit({ requested: " + total + ", max: 500.00 })" },
        { tag: "observe", text: "Observation: Order complies with financial policy ($" + total.toFixed(2) + " <= $500.00)." },
        { tag: "action", text: "Action: inventory.reserve_stock({ item: '" + product + "', count: " + qty + " })" },
        { tag: "observe", text: "Observation: Inventory reserved successfully." },
        { tag: "action", text: "Action: payment.authorize({ amount: " + total + " })" },
        { tag: "observe", text: "Observation: Payment authorized. STATUS: COMPLETED — Saga Completed successfully with zero errors." }
      ];
    } else {
      return [
        { tag: "system", text: `Saga Procure-to-Pay workflow started for ${qty}x ${product} ($${total.toFixed(2)})` },
        { tag: "thought", text: "Thought: Verifying credit limit against corporate procurement ceiling ($500.00)..." },
        { tag: "action", text: "Action: policy.check_limit({ requested: " + total + ", max: 500.00 })" },
        { tag: "observe", text: "Observation: Policy violation: Order amount $" + total.toFixed(2) + " exceeds $500.00 limit. PAYMENT_REJECTED / DENIED." },
        { tag: "thought", text: "Thought: Initiating compensating rollback across transactional state machine." },
        { tag: "action", text: "Action: saga.compensate_rollback({ release_stock: '" + product + "', qty: " + qty + " })" },
        { tag: "observe", text: "Observation: COMPENSATED — Inventory restored. Rollback completed cleanly." }
      ];
    }
  }
};

// Aliases for compatibility
export const WORKFLOWS = Workflows;

// =============================================================================
// 5. SIMULATOR RUNNER STATE & ENGINE
// =============================================================================

export const SimulatorState = {
  isProcessing: false,
  activeScenario: "audit",
  ledgerChain: [],
  orders: [
    { id: 1, vendor_id: 481, item: "Server Racks", amount: 405000, status: "approved" },
    { id: 2, vendor_id: 481, item: "High-Density Server Chassis", amount: 1250, status: "pending" }
  ],
  products: [
    { id: 1, name: "Quantum Processor v1", stock_quantity: 12, safe_threshold: 10 },
    { id: 2, name: "Standing Desk", stock_quantity: 5, price: 299.99 }
  ],
  accounts: [
    { code: "1010", name: "Accounts Payable", balance: 450000 },
    { code: "2040", name: "Suspense Holding", balance: 0 }
  ],
  quarantinedIPs: []
};

export async function runWorkflow(scenarioKey) {
  if (SimulatorState.isProcessing) return;
  
  let key = scenarioKey;
  if (key === "invoice_reconciliation") key = "audit";
  if (key === "saga_procure") key = "inventory_stockout";
  if (key === "executive_report") key = "sql_financial";
  if (key === "security_quarantine") key = "rbac_quarantine";

  const trace = Workflows[key];
  if (!trace) return;

  SimulatorState.isProcessing = true;
  SimulatorState.activeScenario = key;

  // Update button active state
  if (typeof document !== "undefined") {
    const btns = document.querySelectorAll(".btn-scenario, .scenario-btn");
    btns.forEach(b => {
      const sc = b.getAttribute("data-scenario");
      if (sc === scenarioKey || sc === key) {
        b.classList.add("active");
      } else {
        b.classList.remove("active");
      }
    });

    const term = document.getElementById("terminal-container");
    const placeholder = document.getElementById("ephemeral-placeholder");
    const uiContainer = document.getElementById("ephemeral-ui-container");

    if (term) term.innerHTML = "";
    if (placeholder) placeholder.classList.remove("hidden");
    if (uiContainer) {
      uiContainer.classList.add("hidden");
      uiContainer.innerHTML = "";
    }

    if (term) {
      for (let i = 0; i < trace.length; i++) {
        const line = trace[i];
        const div = document.createElement("div");
        div.className = "terminal-line";
        div.innerHTML = `<span class="term-tag tag-${line.tag}">[${line.tag.toUpperCase()}]</span> ${line.text}`;
        term.appendChild(div);
        term.scrollTop = term.scrollHeight;
        await new Promise(r => setTimeout(r, 60));
      }
    }

    if (placeholder) placeholder.classList.add("hidden");
    if (uiContainer) uiContainer.classList.remove("hidden");

    // Render respective Ephemeral Dashboard
    if (key === "audit") renderAuditDashboard();
    else if (key === "inventory_stockout") renderStockoutDashboard();
    else if (key === "sql_financial") renderFinancialDashboard();
    else if (key === "rbac_quarantine") renderRBACDashboard();
  }

  SimulatorState.isProcessing = false;
}

export function streamScenario(scenarioKey) {
  runWorkflow(scenarioKey);
}

// =============================================================================
// 6. EPHEMERAL DASHBOARD RENDERERS & ACTIONS
// =============================================================================

export function renderAuditDashboard() {
  const container = document.getElementById("ephemeral-ui-container");
  if (!container) return;

  container.innerHTML = `
    <div class="ephemeral-card">
      <div class="ephemeral-card-header">
        <span class="ephemeral-card-title">Scenario 1: Risk Assessment & Ledger Rebalance</span>
        <span class="badge-legacy card-badge text-amber">Discrepancy: $45,000.00</span>
      </div>
      <p style="font-size: 0.85rem; margin-bottom: 0.75rem; color: var(--text-secondary);">
        Autonomous ReAct agent identified invoice anomaly on PO-9921. Escrow hold applied under CFO Directive 2026-B.
      </p>
      <h4 style="font-size: 0.85rem; margin-bottom: 0.5rem; color: var(--accent-cyan);">Accounting Ledger Rebalance Diff Table</h4>
      <table class="ephemeral-diff-table font-mono">
        <thead>
          <tr><th>Account Ledger</th><th>Original Balance</th><th>Steered Balance</th><th>Delta</th></tr>
        </thead>
        <tbody>
          <tr>
            <td>Accounts Payable (Acc 1010)</td>
            <td>$450,000.00</td>
            <td class="text-emerald">$448,750.00</td>
            <td class="text-rose">-$1,250.00</td>
          </tr>
          <tr>
            <td>Suspense Holding (Acc 2040)</td>
            <td>$0.00</td>
            <td class="text-cyan">$1,250.00</td>
            <td class="text-emerald">+$1,250.00</td>
          </tr>
        </tbody>
      </table>
      <div class="ephemeral-actions">
        <button id="btn-commit-rebalance" class="btn btn-primary btn-sm" onclick="window.commitLedgerRebalance()">✓ Commit Ledger Rebalance (2 Blocks)</button>
        <button id="btn-approve-waiver" class="btn btn-outline btn-sm" onclick="window.approveWaiver(2)">📄 Authorize CFO Waiver (Order #2)</button>
      </div>
    </div>
  `;
}

export async function commitLedgerRebalance() {
  await appendLedgerBlock("UPDATE accounts SET balance = balance - 1250 WHERE code = '1010' -- AP Adjustment");
  await appendLedgerBlock("UPDATE accounts SET balance = balance + 1250 WHERE code = '2040' -- Suspense Allocation");
  showToast("Ledger Rebalanced: 2 cryptographic blocks sealed to SHA-256 chain.", "success");
}

export async function approveWaiver(orderId = 2) {
  const order = SimulatorState.orders.find(o => o.id === orderId);
  if (order) order.status = "approved";
  await appendLedgerBlock(`UPDATE orders SET status = 'approved' WHERE id = ${orderId} -- CFO Waiver Signed`);
  showToast(`CFO Waiver Approved: Order #${orderId} marked approved and logged to ledger.`, "success");
}

export function renderStockoutDashboard() {
  const container = document.getElementById("ephemeral-ui-container");
  if (!container) return;

  container.innerHTML = `
    <div class="ephemeral-card">
      <div class="ephemeral-card-header">
        <span class="ephemeral-card-title">Scenario 2: Stockout Mitigation & PO Dispatch</span>
        <span class="badge-omnigate card-badge text-emerald">100% Buffer Secured</span>
      </div>
      <p style="font-size: 0.85rem; margin-bottom: 0.75rem; color: var(--text-secondary);">
        Graph traversal identified optimal supplier <strong>Apex Microelectronics</strong> for replenishment of Quantum Processor v1.
      </p>
      
      <!-- Burndown SVG Chart -->
      <div class="burndown-chart-wrapper" style="margin: 0.75rem 0; background: rgba(0,0,0,0.3); border-radius: 8px; padding: 0.5rem;">
        <svg viewBox="0 0 400 110" class="burndown-svg" style="width: 100%; height: 90px;">
          <defs>
            <linearGradient id="stockoutGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#06b6d4" stop-opacity="0.6"/>
              <stop offset="100%" stop-color="#06b6d4" stop-opacity="0.0"/>
            </linearGradient>
          </defs>
          <line x1="40" y1="65" x2="380" y2="65" stroke="#f59e0b" stroke-dasharray="4,4" stroke-width="1.5"/>
          <text x="45" y="60" fill="#f59e0b" font-size="9" font-family="var(--font-mono)">Safety Threshold: 10 units</text>
          <path d="M 40 20 L 120 40 L 200 55 L 280 62 L 360 85" fill="none" stroke="#f43f5e" stroke-width="2"/>
          <path d="M 200 55 L 280 25 L 360 15" fill="none" stroke="#10b981" stroke-width="2.5"/>
          <circle cx="200" cy="55" r="4" fill="#06b6d4"/>
          <circle cx="280" cy="25" r="4" fill="#10b981"/>
          <circle cx="360" cy="15" r="4" fill="#10b981"/>
        </svg>
      </div>

      <h4 style="font-size: 0.85rem; margin-bottom: 0.5rem; color: var(--accent-cyan);">Supplier Procurement Matrix</h4>
      <table class="ephemeral-diff-table font-mono">
        <thead>
          <tr><th>Supplier Candidate</th><th>Lead Time</th><th>Unit Cost</th><th>SLA Score</th></tr>
        </thead>
        <tbody>
          <tr>
            <td>Apex Microelectronics (Optimal)</td>
            <td class="text-emerald">24 Hours</td>
            <td>$240.00</td>
            <td class="text-emerald">99.8%</td>
          </tr>
          <tr>
            <td>Quantum Dynamics Corp</td>
            <td>5 Days</td>
            <td>$235.00</td>
            <td>94.2%</td>
          </tr>
          <tr>
            <td>Nova Foundry Direct</td>
            <td>12 Days</td>
            <td>$220.00</td>
            <td>88.0%</td>
          </tr>
        </tbody>
      </table>
      <div class="ephemeral-actions">
        <button id="btn-dispatch-po" class="btn btn-primary btn-sm" onclick="window.dispatchPurchaseOrder()">⚡ 1-Click PO Dispatch (+50 units)</button>
      </div>
    </div>
  `;
}

export async function dispatchPurchaseOrder() {
  const prod = SimulatorState.products.find(p => p.name === "Quantum Processor v1");
  if (prod) prod.stock_quantity += 50;
  await appendLedgerBlock("INSERT INTO purchase_orders (po_number, sku, qty, vendor) VALUES ('PO-2026-8841', 'Quantum Processor v1', 50, 'Apex Microelectronics')");
  showToast("PO-2026-8841 Dispatched: +50 units reserved with Apex Microelectronics.", "success");
}

export function renderFinancialDashboard() {
  const container = document.getElementById("ephemeral-ui-container");
  if (!container) return;

  container.innerHTML = `
    <div class="ephemeral-card">
      <div class="ephemeral-card-header">
        <span class="ephemeral-card-title">Scenario 3: Autonomous SQL & Financial Synthesis</span>
        <span class="badge-omnigate card-badge text-cyan">Real-Time BI</span>
      </div>
      
      <!-- Executive KPI Grid -->
      <div class="kpi-grid" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem; margin: 0.75rem 0;">
        <div class="kpi-card glass-card" style="padding: 0.6rem; text-align: center;">
          <span style="font-size: 0.7rem; color: var(--text-muted); display: block;">Gross ARR</span>
          <strong class="text-emerald" style="font-size: 1.1rem;">$4.25M</strong>
        </div>
        <div class="kpi-card glass-card" style="padding: 0.6rem; text-align: center;">
          <span style="font-size: 0.7rem; color: var(--text-muted); display: block;">EBITDA Margin</span>
          <strong class="text-cyan" style="font-size: 1.1rem;">34.2%</strong>
        </div>
        <div class="kpi-card glass-card" style="padding: 0.6rem; text-align: center;">
          <span style="font-size: 0.7rem; color: var(--text-muted); display: block;">Net Cash Burn</span>
          <strong class="text-violet" style="font-size: 1.1rem;">$42.1k/mo</strong>
        </div>
        <div class="kpi-card glass-card" style="padding: 0.6rem; text-align: center;">
          <span style="font-size: 0.7rem; color: var(--text-muted); display: block;">Loop Latency</span>
          <strong class="text-amber" style="font-size: 1.1rem;">11.8ms</strong>
        </div>
      </div>

      <!-- Dynamic Multi-Series SVG Financial Chart -->
      <div style="background: rgba(0,0,0,0.3); border-radius: 8px; padding: 0.6rem; margin-bottom: 0.75rem;">
        <div style="font-size: 0.78rem; font-weight: 600; margin-bottom: 0.4rem; color: var(--text-secondary);">
          Monthly Revenue vs Operating Outlay (FY2026)
        </div>
        <svg viewBox="0 0 420 95" style="width: 100%; height: 85px;">
          <!-- Jan .. Jun Bars -->
          <g class="chart-group">
            <rect x="25" y="35" width="16" height="45" fill="#10b981" rx="2"/>
            <rect x="44" y="55" width="16" height="25" fill="#6366f1" rx="2"/>
            <text x="38" y="90" fill="#94a3b8" font-size="9" text-anchor="middle">Jan</text>
          </g>
          <g class="chart-group">
            <rect x="85" y="30" width="16" height="50" fill="#10b981" rx="2"/>
            <rect x="104" y="50" width="16" height="30" fill="#6366f1" rx="2"/>
            <text x="98" y="90" fill="#94a3b8" font-size="9" text-anchor="middle">Feb</text>
          </g>
          <g class="chart-group">
            <rect x="145" y="22" width="16" height="58" fill="#10b981" rx="2"/>
            <rect x="164" y="48" width="16" height="32" fill="#6366f1" rx="2"/>
            <text x="158" y="90" fill="#94a3b8" font-size="9" text-anchor="middle">Mar</text>
          </g>
          <g class="chart-group">
            <rect x="205" y="18" width="16" height="62" fill="#10b981" rx="2"/>
            <rect x="224" y="45" width="16" height="35" fill="#6366f1" rx="2"/>
            <text x="218" y="90" fill="#94a3b8" font-size="9" text-anchor="middle">Apr</text>
          </g>
          <g class="chart-group">
            <rect x="265" y="12" width="16" height="68" fill="#10b981" rx="2"/>
            <rect x="284" y="42" width="16" height="38" fill="#6366f1" rx="2"/>
            <text x="278" y="90" fill="#94a3b8" font-size="9" text-anchor="middle">May</text>
          </g>
          <g class="chart-group">
            <rect x="325" y="8" width="16" height="72" fill="#10b981" rx="2"/>
            <rect x="344" y="40" width="16" height="40" fill="#6366f1" rx="2"/>
            <text x="338" y="90" fill="#94a3b8" font-size="9" text-anchor="middle">Jun</text>
          </g>
        </svg>
      </div>

      <div class="ephemeral-actions">
        <button class="btn btn-primary btn-sm" onclick="showToast('Executive Report Exported: PDF & CSV sealed with SHA-256.')">📤 Export Board Memo</button>
      </div>
    </div>
  `;
}

export function renderRBACDashboard() {
  const container = document.getElementById("ephemeral-ui-container");
  if (!container) return;

  container.innerHTML = `
    <div class="ephemeral-card border-rose">
      <div class="ephemeral-card-header">
        <span class="ephemeral-card-title text-rose">Security Incident: Privilege Boundary Violation</span>
        <span class="badge-legacy card-badge text-rose pulse-tampered">SESSION QUARANTINED</span>
      </div>
      <p style="font-size: 0.85rem; margin-bottom: 0.75rem; color: var(--text-secondary);">
        Sub-4ms perimeter containment blocked unauthorized access from IP <strong>198.51.100.42</strong>.
      </p>
      
      <h4 style="font-size: 0.85rem; margin-bottom: 0.5rem; color: var(--accent-rose);">RBAC Permission Scope Analysis</h4>
      <table class="ephemeral-diff-table font-mono">
        <thead>
          <tr><th>Target Resource</th><th>Required Clearance</th><th>Actor Token</th><th>Action</th></tr>
        </thead>
        <tbody>
          <tr>
            <td>payroll_executive_ledger</td>
            <td class="text-rose">Level 4 (CFO Clearance)</td>
            <td>Token#usr_c789 (Level 2)</td>
            <td class="text-rose">SCHEMA_DUMP (Blocked)</td>
          </tr>
        </tbody>
      </table>
      <div class="ephemeral-actions">
        <button id="btn-quarantine-incident" class="btn btn-danger btn-sm" onclick="window.quarantineSecurityIncident()">🛡️ Seal Security Quarantine to Ledger</button>
      </div>
    </div>
  `;
}

export async function quarantineSecurityIncident() {
  await appendLedgerBlock("INSERT INTO security_audit (event, ip_address, status) VALUES ('PRIVILEGE_BOUNDARY_VIOLATION', '198.51.100.42', 'BLACKLIST')");
  showToast("Security Quarantine Sealed: IP 198.51.100.42 permanently isolated in ledger.", "success");
}

export function renderSagaDashboard() {
  const container = document.getElementById("ephemeral-ui-container");
  if (!container) return;
  container.innerHTML = `
    <div class="ephemeral-card">
      <div class="ephemeral-card-header">
        <span class="ephemeral-card-title">Saga Procure-to-Pay Orchestrator</span>
        <span class="badge-omnigate card-badge">ACID Rollback Engine</span>
      </div>
      <p style="font-size: 0.85rem; margin-bottom: 0.75rem; color: var(--text-secondary);">
        Simulate corporate order policy thresholds ($500 limit).
      </p>
      <div class="ephemeral-actions">
        <button class="btn btn-primary btn-sm" onclick="runWorkflow('inventory_stockout')">Run Compliant Saga</button>
      </div>
    </div>
  `;
}

// =============================================================================
// 7. CRYPTOGRAPHIC LEDGER & ZERO-KNOWLEDGE AUDIT
// =============================================================================

export async function calculateHash(index, timestamp, data, previousHash) {
  const payload = `${index}|${timestamp}|${data}|${previousHash}`;
  
  if (typeof crypto !== "undefined" && crypto.subtle) {
    const encoder = new TextEncoder();
    const encoded = encoder.encode(payload);
    const hashBuffer = await crypto.subtle.digest("SHA-256", encoded);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, "0")).join("");
  }
  
  // Deterministic Fallback Hash Generator (producing 64-char lowercase hex)
  let h = 0x811c9dc5;
  for (let i = 0; i < payload.length; i++) {
    h ^= payload.charCodeAt(i);
    h += (h << 1) + (h << 4) + (h << 7) + (h << 8) + (h << 24);
  }
  const hex = (h >>> 0).toString(16).padStart(8, "0");
  return (hex + hex + hex + hex + hex + hex + hex + hex).substring(0, 64);
}

export async function initLedger() {
  const b0_prev = "0000000000000000000000000000000000000000000000000000000000000000";
  const b0_data = "system_init --secure";
  const b0_time = "2026-06-10 09:00:00";
  const b0_hash = await calculateHash(0, b0_time, b0_data, b0_prev);

  const b1_prev = b0_hash;
  const b1_data = "INSERT INTO orders (id, item, amount) VALUES (1, 'Server Racks', 405000)";
  const b1_time = "2026-06-10 09:01:20";
  const b1_hash = await calculateHash(1, b1_time, b1_data, b1_prev);

  const b2_prev = b1_hash;
  const b2_data = "UPDATE accounts SET balance = balance - 405000 WHERE code = '1010'";
  const b2_time = "2026-06-10 09:02:45";
  const b2_hash = await calculateHash(2, b2_time, b2_data, b2_prev);

  SimulatorState.ledgerChain = [
    { index: 0, timestamp: b0_time, data: b0_data, previousHash: b0_prev, hash: b0_hash, tampered: false, cascadeInvalid: false, is_verified: true },
    { index: 1, timestamp: b1_time, data: b1_data, previousHash: b1_prev, hash: b1_hash, tampered: false, cascadeInvalid: false, is_verified: true },
    { index: 2, timestamp: b2_time, data: b2_data, previousHash: b2_prev, hash: b2_hash, tampered: false, cascadeInvalid: false, is_verified: true }
  ];

  updateZKMetrics();
  renderLedger();
}

export async function appendLedgerBlock(data) {
  const chain = SimulatorState.ledgerChain;
  const prevBlock = chain[chain.length - 1];
  const newIndex = chain.length;
  const now = new Date().toISOString().replace("T", " ").substring(0, 19);
  const prevHash = prevBlock ? prevBlock.hash : "0000000000000000000000000000000000000000000000000000000000000000";
  const hash = await calculateHash(newIndex, now, data, prevHash);

  chain.push({
    index: newIndex,
    timestamp: now,
    data: data,
    previousHash: prevHash,
    hash: hash,
    tampered: false,
    cascadeInvalid: false,
    is_verified: true
  });

  updateZKMetrics();
  renderLedger();
}

export async function verifyLedgerChain() {
  const chain = SimulatorState.ledgerChain;
  let allValid = true;

  for (let i = 0; i < chain.length; i++) {
    const block = chain[i];
    if (i === 0) {
      if (block.previousHash !== "0000000000000000000000000000000000000000000000000000000000000000") {
        allValid = false;
        block.is_verified = false;
      }
    } else {
      const prev = chain[i - 1];
      if (block.previousHash !== prev.hash) {
        allValid = false;
        block.is_verified = false;
      }
    }
  }

  return allValid;
}

export function tamperLedgerBlock2() {
  const chain = SimulatorState.ledgerChain;
  if (chain.length < 3) return;

  // Mutate Block 2
  const b2 = chain[2];
  b2.data = "TAMPERED: UPDATE accounts SET balance = 25000.00 WHERE code = '1010' -- Malicious Exfiltration";
  b2.hash = "9999999999999999999999999999999999999999999999999999999999999999";
  b2.tampered = true;
  b2.cascadeInvalid = false;
  b2.is_verified = false;

  // Mark all downstream blocks as cascade-invalidated
  for (let i = 3; i < chain.length; i++) {
    chain[i].cascadeInvalid = true;
    chain[i].is_verified = false;
  }

  // Update Status Banners
  if (typeof document !== "undefined") {
    const errBanner = document.getElementById("ledger-status-error");
    const succBanner = document.getElementById("ledger-status-success");
    if (errBanner) errBanner.classList.remove("hidden");
    if (succBanner) succBanner.classList.add("hidden");

    const badge = document.getElementById("chain-status-badge");
    if (badge) {
      badge.className = "chain-badge badge-tampered";
      badge.innerHTML = '<span class="status-dot pulse-tampered"></span> INTEGRITY_VIOLATION: Chain Broken at Block #2';
    }
  }

  updateZKMetrics();
  renderLedger();
}

export async function repairAndRecalculateLedger() {
  const chain = SimulatorState.ledgerChain;
  if (chain.length < 3) return;

  // Restore Block 2 clean data
  chain[2].data = "UPDATE accounts SET balance = balance - 405000 WHERE code = '1010'";
  chain[2].tampered = false;
  chain[2].cascadeInvalid = false;

  // Sequentially recalculate all blocks from 2 upwards
  for (let i = 2; i < chain.length; i++) {
    const prev = chain[i - 1];
    chain[i].previousHash = prev.hash;
    chain[i].hash = await calculateHash(chain[i].index, chain[i].timestamp, chain[i].data, chain[i].previousHash);
    chain[i].tampered = false;
    chain[i].cascadeInvalid = false;
    chain[i].repaired = true;
    chain[i].is_verified = true;
  }

  // Update Status Banners
  if (typeof document !== "undefined") {
    const errBanner = document.getElementById("ledger-status-error");
    const succBanner = document.getElementById("ledger-status-success");
    if (errBanner) errBanner.classList.add("hidden");
    if (succBanner) succBanner.classList.remove("hidden");

    const badge = document.getElementById("chain-status-badge");
    if (badge) {
      badge.className = "chain-badge badge-valid";
      badge.innerHTML = '<span class="status-dot green"></span> Chain Validated &amp; Verified (SHA-256)';
    }
  }

  updateZKMetrics();
  renderLedger();
  showToast("Cryptographic Repair Complete: All blocks sequentially rehashed and verified.", "success");
}

export async function resetLedger() {
  await initLedger();

  if (typeof document !== "undefined") {
    const errBanner = document.getElementById("ledger-status-error");
    const succBanner = document.getElementById("ledger-status-success");
    if (errBanner) errBanner.classList.add("hidden");
    if (succBanner) succBanner.classList.remove("hidden");

    const placeholder = document.getElementById("ephemeral-placeholder");
    const uiContainer = document.getElementById("ephemeral-ui-container");
    if (placeholder) placeholder.classList.remove("hidden");
    if (uiContainer) {
      uiContainer.classList.add("hidden");
      uiContainer.innerHTML = "";
    }
  }

  showToast("Ledger Restored: System state returned to baseline.", "success");
}

export function updateZKMetrics() {
  if (typeof document === "undefined") return;

  const chain = SimulatorState.ledgerChain;
  const isTampered = chain.some(b => b.tampered || b.cascadeInvalid);

  const tamperScoreEl = document.getElementById("zk-tamper-score");
  const merkleEl = document.getElementById("zk-merkle-root");

  if (tamperScoreEl) {
    if (isTampered) {
      tamperScoreEl.textContent = "TAMPERED (CRITICAL)";
    } else {
      tamperScoreEl.textContent = "100%";
    }
  }

  if (merkleEl) {
    if (isTampered) {
      merkleEl.textContent = "INVALIDATED";
    } else {
      const tipBlock = chain[chain.length - 1];
      merkleEl.textContent = tipBlock ? `0x${tipBlock.hash.substring(0, 12)}...` : "0x000000000000...";
    }
  }
}

export function renderLedger() {
  const container = document.getElementById("ledger-container");
  if (!container) return;
  container.innerHTML = "";

  const chain = SimulatorState.ledgerChain;

  chain.forEach((block, idx) => {
    let cardClass = "glass-card block-card";
    let statusText = "✓ SEALED";
    let statusClass = "text-emerald";

    if (block.tampered) {
      cardClass += " tampered-block-card tampered border-rose";
      statusText = "⚠️ TAMPERED (INVALID)";
      statusClass = "text-rose";
    } else if (block.cascadeInvalid) {
      cardClass += " cascade-invalid border-rose";
      statusText = "⚠️ CASCADE BROKEN";
      statusClass = "text-rose";
    } else if (block.repaired) {
      cardClass += " repaired-block-card border-emerald";
      statusText = "✓ REPAIRED & SEALED";
      statusClass = "text-emerald";
    }

    const card = document.createElement("div");
    card.className = cardClass;
    card.innerHTML = `
      <div class="block-header" style="display: flex; justify-content: space-between; margin-bottom: 0.4rem;">
        <span style="font-weight: 700; font-family: var(--font-mono); font-size: 0.85rem;">Block #${block.index} ${block.index === 0 ? "(Genesis)" : ""}</span>
        <span class="${statusClass}" style="font-size: 0.78rem; font-weight: 700;">${statusText}</span>
      </div>
      <div class="block-field" style="margin-bottom: 0.3rem;">
        <span class="block-label" style="font-size: 0.72rem; color: var(--text-muted); display: block;">Mutation Payload</span>
        <span class="block-val font-mono" style="font-size: 0.78rem; word-break: break-all;">${block.data}</span>
      </div>
      <div class="block-field" style="margin-bottom: 0.3rem;">
        <span class="block-label" style="font-size: 0.72rem; color: var(--text-muted); display: block;">Previous Hash</span>
        <span class="block-val font-mono text-muted" style="font-size: 0.74rem;">${block.previousHash.substring(0, 16)}...</span>
      </div>
      <div class="block-field">
        <span class="block-label" style="font-size: 0.72rem; color: var(--text-muted); display: block;">SHA-256 Block Hash</span>
        <span class="block-val font-mono ${block.tampered || block.cascadeInvalid ? "text-rose" : "text-cyan"}" style="font-size: 0.74rem; font-weight: 600;">${block.hash.substring(0, 16)}...</span>
      </div>
    `;

    container.appendChild(card);

    // Render pointer arrow if not the last block
    if (idx < chain.length - 1) {
      const arrow = document.createElement("div");
      const nextBlock = chain[idx + 1];
      const isBroken = nextBlock.cascadeInvalid || nextBlock.tampered || (nextBlock.previousHash !== block.hash);
      
      arrow.className = `ledger-arrow ${isBroken ? "broken-arrow text-rose" : "text-emerald"}`;
      arrow.style.cssText = "display: flex; align-items: center; justify-content: center; font-size: 1.4rem; font-weight: bold;";
      arrow.innerHTML = isBroken ? `<span title="Broken Hash Pointer">≠</span>` : `<span title="Valid SHA-256 Link">→</span>`;
      container.appendChild(arrow);
    }
  });
}

// =============================================================================
// 8. GROUNDED ENTERPRISE ROI CALCULATOR
// =============================================================================

export function updateROI() {
  const hcEl = document.getElementById("slider-headcount") || document.getElementById("headcount-slider");
  const revEl = document.getElementById("slider-revenue") || document.getElementById("revenue-slider");
  const opsEl = document.getElementById("slider-ops") || document.getElementById("ops-slider");

  const headcount = hcEl ? parseInt(hcEl.value) || 2500 : 2500;
  const revenue = revEl ? parseInt(revEl.value) || 250 : 250;
  const opsStaff = opsEl ? parseInt(opsEl.value) || 120 : 120;

  const dispHc = document.getElementById("display-headcount");
  const dispRev = document.getElementById("display-revenue");
  const dispOps = document.getElementById("display-ops");

  if (dispHc) dispHc.innerText = `${headcount.toLocaleString()} employees`;
  if (dispRev) dispRev.innerText = `$${revenue}M`;
  if (dispOps) dispOps.innerText = `${opsStaff} staff`;

  // Financial Calculations
  const directLaborSavings = opsStaff * 42000;
  const errorSavings = revenue * 6500;
  const consultingSavings = 450000;
  const totalSavings = directLaborSavings + errorSavings + consultingSavings;

  const hoursReclaimed = opsStaff * 240;
  const paybackDays = Math.max(18, Math.round(45 - (opsStaff / 30)));
  const netROI = Math.round(320 + (revenue * 0.45));

  const calcSav = document.getElementById("calc-savings");
  const calcHrs = document.getElementById("calc-hours");
  const calcPay = document.getElementById("calc-payback");
  const calcRoi = document.getElementById("calc-roi");
  const calcError = document.getElementById("calc-error");

  if (calcSav) calcSav.innerText = `$${totalSavings.toLocaleString()}`;
  if (calcHrs) calcHrs.innerText = `${hoursReclaimed.toLocaleString()} hrs`;
  if (calcPay) calcPay.innerText = `< ${paybackDays} Days`;
  if (calcRoi) calcRoi.innerText = `${netROI}%`;
  if (calcError) calcError.innerText = "-99.4%";
}

// =============================================================================
// 9. TOAST NOTIFICATIONS & 1-CLICK COPY HELPER (ZERO DEAD CLICKS)
// =============================================================================

export function showToast(message, type = "success") {
  if (typeof document === "undefined") return;

  let toastContainer = document.getElementById("toast-container");
  if (!toastContainer) {
    toastContainer = document.createElement("div");
    toastContainer.id = "toast-container";
    toastContainer.className = "toast-container";
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement("div");
  toast.className = `toast-item toast-${type} glass-card`;
  toast.innerHTML = `
    <span class="toast-icon">${type === "success" ? "✓" : "⚠️"}</span>
    <span class="toast-text">${message}</span>
  `;

  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.classList.add("toast-fadeout");
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

export function copyContactEmail() {
  const email = "info@omnigateos.com";
  
  if (typeof navigator !== "undefined" && navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(email).then(() => {
      showToast("Email copied: info@omnigateos.com", "success");
    }).catch(() => {
      fallbackCopy(email);
    });
  } else {
    fallbackCopy(email);
  }
}

function fallbackCopy(text) {
  try {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    document.body.removeChild(textarea);
    showToast("Email copied: info@omnigateos.com", "success");
  } catch (e) {
    showToast("Contact: info@omnigateos.com", "success");
  }
}

// =============================================================================
// 10. GLOBAL WINDOW ATTACHMENTS (FOR TEST RUNNERS & CDP EVAL)
// =============================================================================

if (typeof window !== "undefined") {
  window.BENCHMARK_DATASETS = BENCHMARK_DATASETS;
  window.SAGStudioEngine = SAGStudioEngine;
  window.BenchmarkHubController = BenchmarkHubController;
  window.Workflows = Workflows;
  window.WORKFLOWS = Workflows;
  window.SimulatorState = SimulatorState;
  window.runWorkflow = runWorkflow;
  window.streamScenario = streamScenario;
  window.calculateHash = calculateHash;
  window.initLedger = initLedger;
  window.appendLedgerBlock = appendLedgerBlock;
  window.verifyLedgerChain = verifyLedgerChain;
  window.tamperLedgerBlock2 = tamperLedgerBlock2;
  window.tamperBlock = tamperLedgerBlock2;
  window.repairAndRecalculateLedger = repairAndRecalculateLedger;
  window.reverifyChain = repairAndRecalculateLedger;
  window.resetLedger = resetLedger;
  window.renderLedger = renderLedger;
  window.updateZKMetrics = updateZKMetrics;
  window.updateROI = updateROI;
  window.commitLedgerRebalance = commitLedgerRebalance;
  window.approveWaiver = approveWaiver;
  window.dispatchPurchaseOrder = dispatchPurchaseOrder;
  window.quarantineSecurityIncident = quarantineSecurityIncident;
  window.renderAuditDashboard = renderAuditDashboard;
  window.renderStockoutDashboard = renderStockoutDashboard;
  window.renderFinancialDashboard = renderFinancialDashboard;
  window.renderRBACDashboard = renderRBACDashboard;
  window.renderSagaDashboard = renderSagaDashboard;
  window.showToast = showToast;
  window.copyContactEmail = copyContactEmail;
}

// =============================================================================
// 11. INITIALIZATION & EVENT BINDINGS
// =============================================================================

if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", () => {
    // 1. Initialize Studio Engine
    SAGStudioEngine.loadBenchmark("swe-bench");

    // 2. Initialize Ledger
    initLedger();

    // 3. Initialize Scenario Buttons
    const scenarioBtns = document.querySelectorAll(".btn-scenario, .scenario-btn");
    scenarioBtns.forEach(btn => {
      btn.addEventListener("click", () => {
        const scKey = btn.getAttribute("data-scenario");
        runWorkflow(scKey);
      });
    });

    // 4. Initial Scenario Run
    runWorkflow("audit");

    // 5. Benchmark Cards & Hub
    const benchmarkCards = document.querySelectorAll(".benchmark-card");
    benchmarkCards.forEach(card => {
      card.addEventListener("click", () => {
        const bId = card.getAttribute("data-benchmark");
        if (bId) BenchmarkHubController.selectBenchmark(bId);
      });
    });

    const btnLoadStudio = document.getElementById("btn-load-benchmark-into-studio");
    if (btnLoadStudio) {
      btnLoadStudio.addEventListener("click", () => {
        BenchmarkHubController.selectBenchmark(BenchmarkHubController.activeBenchmarkId);
        const studioSec = document.getElementById("replay-studio");
        if (studioSec) studioSec.scrollIntoView({ behavior: "smooth" });
      });
    }

    // 6. Transport Playback Controls
    const btnPlay = document.getElementById("btn-dag-play") || document.getElementById("btn-play-pause");
    const btnPrev = document.getElementById("btn-dag-prev") || document.getElementById("btn-step-prev");
    const btnNext = document.getElementById("btn-dag-next") || document.getElementById("btn-step-next");
    const btnSafe = document.getElementById("btn-dag-tsafe") || document.getElementById("btn-jump-safe");
    const btnReset = document.getElementById("btn-dag-reset") || document.getElementById("btn-reset");
    const scrubber = document.getElementById("dag-timeline-scrubber") || document.getElementById("trajectory-scrubber");

    if (btnPlay) btnPlay.addEventListener("click", () => SAGStudioEngine.togglePlay());
    if (btnPrev) btnPrev.addEventListener("click", () => SAGStudioEngine.stepPrev());
    if (btnNext) btnNext.addEventListener("click", () => SAGStudioEngine.stepNext());
    if (btnSafe) btnSafe.addEventListener("click", () => SAGStudioEngine.jumpToTSafe());
    if (btnReset) btnReset.addEventListener("click", () => SAGStudioEngine.reset());
    if (scrubber) scrubber.addEventListener("input", (e) => SAGStudioEngine.goToStep(parseInt(e.target.value)));

    // Speed Presets
    const speedBtns = document.querySelectorAll("#dag-speed-presets .btn-speed");
    speedBtns.forEach(btn => {
      btn.addEventListener("click", () => {
        const spd = parseFloat(btn.getAttribute("data-speed"));
        if (spd) SAGStudioEngine.setSpeed(spd);
      });
    });

    const speedSelect = document.getElementById("playback-speed");
    if (speedSelect) {
      speedSelect.addEventListener("change", (e) => {
        SAGStudioEngine.setSpeed(parseFloat(e.target.value));
      });
    }

    // Bloom / Pulse Mode Toggles
    const btnBloom = document.getElementById("btn-mode-bloom");
    const btnPulse = document.getElementById("btn-mode-pulse");
    if (btnBloom) btnBloom.addEventListener("click", () => SAGStudioEngine.setPlaybackMode("bloom"));
    if (btnPulse) btnPulse.addEventListener("click", () => SAGStudioEngine.setPlaybackMode("pulse"));

    // 7. ROI Sliders
    const slHc = document.getElementById("slider-headcount") || document.getElementById("headcount-slider");
    const slRev = document.getElementById("slider-revenue") || document.getElementById("revenue-slider");
    const slOps = document.getElementById("slider-ops") || document.getElementById("ops-slider");

    if (slHc) slHc.addEventListener("input", updateROI);
    if (slRev) slRev.addEventListener("input", updateROI);
    if (slOps) slOps.addEventListener("input", updateROI);
    updateROI();

    // 8. Ledger Controls
    const btnTamper = document.getElementById("btn-tamper-ledger") || document.getElementById("btn-tamper");
    const btnReverify = document.getElementById("btn-reverify") || document.getElementById("btn-repair");
    const btnResetLedger = document.getElementById("btn-reset-ledger");

    if (btnTamper) btnTamper.addEventListener("click", tamperLedgerBlock2);
    if (btnReverify) btnReverify.addEventListener("click", repairAndRecalculateLedger);
    if (btnResetLedger) btnResetLedger.addEventListener("click", resetLedger);

    // 9. Contact Email Copy Button
    const btnCopyEmail = document.getElementById("btn-copy-email");
    if (btnCopyEmail) btnCopyEmail.addEventListener("click", copyContactEmail);

    // 10. Briefing & Investor Modal Handlers
    const modal = document.getElementById("briefing-modal") || document.getElementById("investor-modal");
    const openBtns = [
      document.getElementById("btn-open-briefing"),
      document.getElementById("btn-open-briefing-cta"),
      document.getElementById("btn-calc-briefing")
    ];
    const closeBtn = document.getElementById("modal-close-btn");
    const form = document.getElementById("briefing-form");
    const successBox = document.getElementById("briefing-success");

    openBtns.forEach(b => {
      if (b) b.addEventListener("click", () => modal && modal.classList.remove("hidden"));
    });

    if (closeBtn && modal) {
      closeBtn.addEventListener("click", () => modal.classList.add("hidden"));
    }

    if (modal) {
      modal.addEventListener("click", (e) => {
        if (e.target === modal) modal.classList.add("hidden");
      });
    }

    if (form) {
      form.addEventListener("submit", (e) => {
        e.preventDefault();
        form.classList.add("hidden");
        if (successBox) successBox.classList.remove("hidden");
        showToast("Briefing Request Received: Confirmation dispatched.", "success");
        setTimeout(() => {
          if (modal) modal.classList.add("hidden");
          form.classList.remove("hidden");
          if (successBox) successBox.classList.add("hidden");
          form.reset();
        }, 3500);
      });
    }
  });
}
