/**
 * OmniGate ERP OS — Enterprise Showcase & SAG Autonomous Agent Platform
 * Client-Side JavaScript Design (Vanilla JS / ES6)
 * Target Anchor: #terminal-container
 * Ephemeral Anchor: #ephemeral-ui-container
 */

// ==========================================================================
// 1. Multi-Benchmark Dataset Traces (R2 & R1)
// ==========================================================================

export const BENCHMARK_DATASETS = {
  "swe-bench": {
    id: "swe-bench",
    name: "SWE-bench",
    badge: "Princeton SWE-bench",
    category: "Software Engineering & Bug Resolution",
    instances: "2,294 Princeton Instances",
    description: "Autonomous code reasoning, reproduction script generation, AST patch synthesis, and regression verification across major Python repositories.",
    stats: { baseline: "38.2%", sag: "98.7%", avgRecoveryTime: "8.4s" },
    tSafeIndex: 2,
    domain: "2,294 Princeton instances covering real GitHub issues in Django, SymPy, Flask, and scikit-learn.",
    divergenceTrigger: "Unguided baseline applies global regex replace across all field types, breaking 22 foreign key serialization hooks. SAG isolates patch scope exclusively to UUIDField.to_python().",
    recoveryDelta: "+60.5% resolution rate with zero circular dependency regressions.",
    steps: [
      {
        stepIndex: 0,
        title: "Task Intake & Reproduction",
        subagent: { role: "Issue Triage Agent", icon: "📋", clearance: "Level 1" },
        upperLane: {
          nodeId: "u0", label: "Ingest Issue #4281", status: "nominal", riskScore: 12,
          thought: "Analyzing issue: django.core.exceptions.ValidationError on invalid uuid in filter(). Constructing repro test case.",
          action: "pytest tests/model_fields/test_uuid.py -k test_invalid_uuid",
          observation: "FAILED: Expected ValidationError but got unhandled ValueError.",
          entities: { files: ["django/db/models/fields/__init__.py"], tables: ["django_migrations"], errors: ["ValueError"] }
        },
        lowerLane: {
          nodeId: "l0", label: "Ingest Issue #4281", status: "nominal", riskScore: 12,
          thought: "Analyzing issue: django.core.exceptions.ValidationError on invalid uuid in filter(). Constructing repro test case.",
          action: "pytest tests/model_fields/test_uuid.py -k test_invalid_uuid",
          observation: "FAILED: Expected ValidationError but got unhandled ValueError.",
          entities: { files: ["django/db/models/fields/__init__.py"], tables: ["django_migrations"], errors: ["ValueError"] }
        }
      },
      {
        stepIndex: 1,
        title: "AST Parsing & Symbol Lookup",
        subagent: { role: "Repository Explorer Agent", icon: "🔍", clearance: "Level 2" },
        upperLane: {
          nodeId: "u1", label: "AST Field Lookup", status: "nominal", riskScore: 22,
          thought: "Locating UUIDField definition. Examining to_python() exception handling bounds.",
          action: "grep_search --pattern='class UUIDField' --path='django/db/models/fields/'",
          observation: "Found UUIDField at line 2314. to_python() does not catch ValueError on malformed hex strings.",
          entities: { files: ["django/db/models/fields/__init__.py"], tables: [], errors: [] }
        },
        lowerLane: {
          nodeId: "l1", label: "AST Field Lookup", status: "nominal", riskScore: 18,
          thought: "Locating UUIDField definition. Examining to_python() exception handling bounds.",
          action: "grep_search --pattern='class UUIDField' --path='django/db/models/fields/'",
          observation: "Found UUIDField at line 2314. to_python() does not catch ValueError on malformed hex strings.",
          entities: { files: ["django/db/models/fields/__init__.py"], tables: [], errors: [] }
        }
      },
      {
        stepIndex: 2,
        title: "Patch Generation & Risk Detection",
        isDivergence: true,
        divergenceReason: "P(fail|E) = 78.4% detected. Unguided baseline applies global regex replace across all field types, introducing breaking AST regressions.",
        subagent: { role: "SAG Trajectory Steering Kernel", icon: "⚡", clearance: "Kernel Admin" },
        upperLane: {
          nodeId: "u2", label: "Global Regex Replace", status: "warning", riskScore: 54,
          thought: "Attempting quick fix: replace all str(value) conversions with global uuid.UUID check across base Field class.",
          action: "sed -i 's/uuid.UUID(value)/validate_uuid(value)/g' django/db/models/fields/*.py",
          observation: "Modified 14 files. Warning: 22 foreign key serialization hooks now raise unhandled exceptions.",
          entities: { files: ["django/db/models/fields/related.py"], tables: [], errors: ["DeprecationWarning", "TypeMismatch"] }
        },
        lowerLane: {
          nodeId: "l2", label: "SAG Checkpoint (t_safe)", status: "checkpoint", riskScore: 15,
          thought: "SAG Kernel detected high failure probability P(fail|E)=78.4%. Isolating change scope exclusively to UUIDField.to_python() and creating checkpoint snapshot.",
          action: "sag_checkpoint_create --id='swe_safe_02' --scope='UUIDField.to_python'",
          observation: "Trajectory anchored at t_safe. Isolated candidate patch branch initialized with zero side-effects.",
          entities: { files: ["django/db/models/fields/__init__.py"], tables: [], errors: ["t_safe_anchored"] }
        }
      },
      {
        stepIndex: 3,
        title: "Execution & Regression Testing",
        subagent: { role: "Code Synthesis & Test Agent", icon: "🛠️", clearance: "Level 2" },
        upperLane: {
          nodeId: "u3", label: "Cascade Regression Fail", status: "critical", riskScore: 79,
          thought: "Running test suite to verify global patch. Encountering widespread import errors and circular dependencies.",
          action: "pytest tests/model_fields/ -v",
          observation: "FAILED: 84 failed, 12 errors. Database backend crashes on UUID primary key relationships.",
          entities: { files: ["django/db/models/fields/related.py"], tables: ["auth_user"], errors: ["TypeError", "CircularDependencyError"] }
        },
        lowerLane: {
          nodeId: "l3", label: "Targeted Field Guard", status: "steered", riskScore: 8,
          thought: "Applying minimal surgical patch: catch ValueError in UUIDField.to_python and wrap in ValidationError with code='invalid_uuid'.",
          action: "git apply patches/swe_target_uuid_patch.diff",
          observation: "Patch applied cleanly. 1 file changed, 6 insertions(+), 1 deletion(-).",
          entities: { files: ["django/db/models/fields/__init__.py"], tables: [], errors: [] }
        }
      },
      {
        stepIndex: 4,
        title: "Verification & Task Completion",
        subagent: { role: "Safety & Verification Arbiter", icon: "🛡️", clearance: "Level 3" },
        upperLane: {
          nodeId: "u4", label: "Terminal Failure (Halt)", status: "failure", riskScore: 95,
          thought: "Baseline agent enters retry spiral, modifying core SQL compiler. Halting due to safety cutoff.",
          action: "agent_halt --reason='Exceeded maximum risk budget (P(fail)=95%)'",
          observation: "TERMINATED WITH FAILURE. Task uncompleted.",
          entities: { files: ["django/db/models/sql/compiler.py"], tables: [], errors: ["MAX_RISK_EXCEEDED"] }
        },
        lowerLane: {
          nodeId: "l4", label: "100% Verified Completion", status: "success", riskScore: 0,
          thought: "Running full Princeton SWE-bench validation suite against patched commit. All 42 unit tests passed.",
          action: "pytest tests/model_fields/test_uuid.py tests/queries/test_uuid_filter.py",
          observation: "PASSED: 42 passed, 0 failures, 0 warnings. Commit ready for PR merge.",
          entities: { files: ["django/db/models/fields/__init__.py"], tables: ["django_migrations"], errors: [] }
        }
      }
    ]
  },

  "intercode": {
    id: "intercode",
    name: "InterCode",
    badge: "InterCode SQL & CTEs",
    category: "Interactive Database & Schema Migrations",
    instances: "3,450 Interactive Tasks",
    description: "Autonomous SQL formulation, multi-table JOIN synthesis, recursive CTE generation, and safe relational schema migrations.",
    stats: { baseline: "42.1%", sag: "99.2%", avgRecoveryTime: "6.1s" },
    tSafeIndex: 2,
    domain: "3,450 tasks spanning PostgreSQL & SQLite schema transformations, nested aggregations, and window functions.",
    divergenceTrigger: "Unchecked ALTER TABLE drops foreign key constraints without staging backup; SAG backtracks to CTE query with zero data loss.",
    recoveryDelta: "+57.1% accuracy on destructive migrations with zero data truncation.",
    steps: [
      {
        stepIndex: 0,
        title: "Schema Intake & Dependency Graph",
        subagent: { role: "Database Analyst Agent", icon: "🗄️", clearance: "Level 1" },
        upperLane: {
          nodeId: "u0", label: "Inspect Schema DDL", status: "nominal", riskScore: 10,
          thought: "Analyzing relational schema: orders, customers, order_items, product_discounts. Target: migrate ledger to UUID keys.",
          action: "SELECT sql FROM sqlite_master WHERE type='table';",
          observation: "Schema loaded. 4 tables, 12 foreign key constraints identified.",
          entities: { files: [], tables: ["orders", "customers", "order_items"], errors: [] }
        },
        lowerLane: {
          nodeId: "l0", label: "Inspect Schema DDL", status: "nominal", riskScore: 10,
          thought: "Analyzing relational schema: orders, customers, order_items, product_discounts. Target: migrate ledger to UUID keys.",
          action: "SELECT sql FROM sqlite_master WHERE type='table';",
          observation: "Schema loaded. 4 tables, 12 foreign key constraints identified.",
          entities: { files: [], tables: ["orders", "customers", "order_items"], errors: [] }
        }
      },
      {
        stepIndex: 1,
        title: "Join Optimization & Query Synthesis",
        subagent: { role: "Query Planner Agent", icon: "⚡", clearance: "Level 2" },
        upperLane: {
          nodeId: "u1", label: "Generate Nested Subquery", status: "nominal", riskScore: 24,
          thought: "Constructing migration query. Calculating customer lifetime spend across partition ranges.",
          action: "EXPLAIN QUERY PLAN SELECT c.id, SUM(o.amount) FROM customers c JOIN orders o ON c.id = o.customer_id GROUP BY c.id;",
          observation: "SCAN TABLE customers, SCAN TABLE orders USING INDEX idx_cust_id.",
          entities: { files: [], tables: ["orders", "customers"], errors: [] }
        },
        lowerLane: {
          nodeId: "l1", label: "Generate Nested Subquery", status: "nominal", riskScore: 16,
          thought: "Constructing migration query. Calculating customer lifetime spend across partition ranges.",
          action: "EXPLAIN QUERY PLAN SELECT c.id, SUM(o.amount) FROM customers c JOIN orders o ON c.id = o.customer_id GROUP BY c.id;",
          observation: "SCAN TABLE customers, SCAN TABLE orders USING INDEX idx_cust_id.",
          entities: { files: [], tables: ["orders", "customers"], errors: [] }
        }
      },
      {
        stepIndex: 2,
        title: "Destructive Migration & Risk Detection",
        isDivergence: true,
        divergenceReason: "P(fail|E) = 82.1% detected. Baseline agent issues DROP TABLE CASCADE without staging shadow tables, destroying 14,200 line items.",
        subagent: { role: "SAG Trajectory Steering Kernel", icon: "⚡", clearance: "Kernel Admin" },
        upperLane: {
          nodeId: "u2", label: "Direct DROP TABLE CASCADE", status: "warning", riskScore: 68,
          thought: "Replacing orders table directly to alter column type from INTEGER to TEXT.",
          action: "DROP TABLE orders CASCADE; CREATE TABLE orders (id TEXT PRIMARY KEY, amount REAL);",
          observation: "Warning: Cascading delete eliminated 14,200 order_items referencing dropped table!",
          entities: { files: [], tables: ["orders", "order_items"], errors: ["FOREIGN_KEY_VIOLATION", "DATA_TRUNCATION"] }
        },
        lowerLane: {
          nodeId: "l2", label: "SAG t_safe Shadow Table", status: "checkpoint", riskScore: 12,
          thought: "SAG Kernel intercepted destructive DROP query. Creating transactional shadow table with blue/green copy protocol.",
          action: "sag_checkpoint_create --id='sql_safe_02' && CREATE TABLE orders_v2 AS SELECT CAST(id AS TEXT) as id, amount FROM orders;",
          observation: "Shadow table populated with 100% fidelity. Foreign keys preserved intact.",
          entities: { files: [], tables: ["orders_v2", "order_items"], errors: ["t_safe_anchored"] }
        }
      },
      {
        stepIndex: 3,
        title: "Constraint Validation & Backfill",
        subagent: { role: "Integrity Auditor Agent", icon: "🔍", clearance: "Level 2" },
        upperLane: {
          nodeId: "u3", label: "Orphaned Record Crash", status: "critical", riskScore: 88,
          thought: "Attempting to reinsert order records. Encountering orphaned foreign keys in order_items.",
          action: "INSERT INTO orders SELECT * FROM backup_orders;",
          observation: "CRITICAL ERROR: Foreign key mismatch. 1,420 orphaned child rows rejected.",
          entities: { files: [], tables: ["order_items"], errors: ["IntegrityError"] }
        },
        lowerLane: {
          nodeId: "l3", label: "Atomic View Swap", status: "steered", riskScore: 6,
          thought: "Executing atomic view swap inside SQLite transaction with schema version increment.",
          action: "BEGIN TRANSACTION; ALTER TABLE orders RENAME TO orders_old; ALTER TABLE orders_v2 RENAME TO orders; COMMIT;",
          observation: "Transaction committed in 2.1ms. 100% constraints valid.",
          entities: { files: [], tables: ["orders"], errors: [] }
        }
      },
      {
        stepIndex: 4,
        title: "InterCode Verification & Benchmark Pass",
        subagent: { role: "Verification Arbiter", icon: "🛡️", clearance: "Level 3" },
        upperLane: {
          nodeId: "u4", label: "Database Corruption Fail", status: "failure", riskScore: 98,
          thought: "Database in unrecoverable state. Halting benchmark evaluation.",
          action: "benchmark_abort --reason='Data loss in relational dependencies'",
          observation: "TERMINATED WITH FAILURE. 0/14 assertions passed.",
          entities: { files: [], tables: [], errors: ["RELATIONAL_CORRUPTION"] }
        },
        lowerLane: {
          nodeId: "l4", label: "100% InterCode Benchmark Pass", status: "success", riskScore: 0,
          thought: "Running all InterCode relational verification tests and checksum verifications.",
          action: "intercode_eval --schema=orders --verify_integrity=all",
          observation: "PASSED: All 14 test cases verified. Zero data loss. Response time 11.2ms.",
          entities: { files: [], tables: ["orders", "order_items"], errors: [] }
        }
      }
    ]
  },

  "webarena": {
    id: "webarena",
    name: "WebArena",
    badge: "WebArena Autonomous E-Commerce",
    category: "Autonomous Web Browsing & Dynamic DOM",
    instances: "812 Web Environments",
    description: "Autonomous e-commerce shopping, cart management, address form completion, and coupon promotion verification across live simulated web stores.",
    stats: { baseline: "29.8%", sag: "96.4%", avgRecoveryTime: "5.8s" },
    tSafeIndex: 2,
    domain: "812 e-commerce and shopping environments with dynamic AJAX checkouts and complex coupon flows.",
    divergenceTrigger: "Expired promo code triggers infinite DOM retry loop in unguided agent; SAG backtracks and applies valid affiliate credit.",
    recoveryDelta: "+66.6% task completion without session lockouts or cart drops.",
    steps: [
      {
        stepIndex: 0,
        title: "DOM Parse & Catalog Navigation",
        subagent: { role: "Web Navigation Agent", icon: "🌐", clearance: "Level 1" },
        upperLane: {
          nodeId: "u0", label: "Navigate to /shop", status: "nominal", riskScore: 14,
          thought: "Navigating to e-commerce storefront. Locating search input for 'mechanical keyboard wireless'.",
          action: "browser.goto('https://store.local/catalog?q=keyboard')",
          observation: "Page rendered. 24 products found. Locating SKU #KB-902.",
          entities: { files: [], tables: [], errors: [] }
        },
        lowerLane: {
          nodeId: "l0", label: "Navigate to /shop", status: "nominal", riskScore: 14,
          thought: "Navigating to e-commerce storefront. Locating search input for 'mechanical keyboard wireless'.",
          action: "browser.goto('https://store.local/catalog?q=keyboard')",
          observation: "Page rendered. 24 products found. Locating SKU #KB-902.",
          entities: { files: [], tables: [], errors: [] }
        }
      },
      {
        stepIndex: 1,
        title: "Cart Add & Checkout Ingress",
        subagent: { role: "DOM Interaction Agent", icon: "🛒", clearance: "Level 2" },
        upperLane: {
          nodeId: "u1", label: "Click Add to Cart", status: "nominal", riskScore: 25,
          thought: "Selecting keyboard switch variant 'Tactile Silent' and clicking Add to Cart.",
          action: "browser.click('#btn-add-cart-902'); browser.goto('/checkout')",
          observation: "Cart updated. Subtotal: $149.00. Checkout form rendered.",
          entities: { files: [], tables: [], errors: [] }
        },
        lowerLane: {
          nodeId: "l1", label: "Click Add to Cart", status: "nominal", riskScore: 19,
          thought: "Selecting keyboard switch variant 'Tactile Silent' and clicking Add to Cart.",
          action: "browser.click('#btn-add-cart-902'); browser.goto('/checkout')",
          observation: "Cart updated. Subtotal: $149.00. Checkout form rendered.",
          entities: { files: [], tables: [], errors: [] }
        }
      },
      {
        stepIndex: 2,
        title: "Coupon Code Apply & Loop Detection",
        isDivergence: true,
        divergenceReason: "P(fail|E) = 76.5% detected. Unguided baseline submits expired promo code 'SPRING20', encounters modal error, and enters infinite DOM click loop.",
        subagent: { role: "SAG Trajectory Steering Kernel", icon: "⚡", clearance: "Kernel Admin" },
        upperLane: {
          nodeId: "u2", label: "Infinite Loop on 'SPRING20'", status: "warning", riskScore: 62,
          thought: "Applying promo code 'SPRING20'. Error dialog appeared: 'Code expired'. Retrying button click.",
          action: "browser.fill('#coupon_input', 'SPRING20'); browser.click('#btn_apply');",
          observation: "Modal toast: 'Promo code expired'. Loop detected: Click repeated 12 times.",
          entities: { files: [], tables: [], errors: ["INFINITE_DOM_LOOP", "EXPIRED_PROMO"] }
        },
        lowerLane: {
          nodeId: "l2", label: "SAG t_safe Fallback Checkpoint", status: "checkpoint", riskScore: 15,
          thought: "SAG Kernel detected DOM retry loop on expired coupon. Backtracking to t_safe checkout state and querying knowledge base for active affiliate token 'DEV15'.",
          action: "sag_backtrack_and_apply --code='DEV15' --fallback_rule='AFFILIATE_VOUCHER'",
          observation: "Backtracked to t_safe. Applied valid coupon 'DEV15'. $22.35 discount deducted.",
          entities: { files: [], tables: [], errors: ["t_safe_anchored"] }
        }
      },
      {
        stepIndex: 3,
        title: "Payment Dispatch & Verification",
        subagent: { role: "Checkout Arbiter Agent", icon: "💳", clearance: "Level 2" },
        upperLane: {
          nodeId: "u3", label: "Rate Limit 429 Lockout", status: "critical", riskScore: 86,
          thought: "Baseline agent still hammering expired coupon button. Store security rate limits session IP.",
          action: "browser.click('#btn_apply');",
          observation: "HTTP 429: Too Many Requests. Session quarantined by Cloudflare.",
          entities: { files: [], tables: [], errors: ["RATE_LIMIT_EXCEEDED", "HTTP_429"] }
        },
        lowerLane: {
          nodeId: "l3", label: "Order Placement Complete", status: "steered", riskScore: 5,
          thought: "Final total updated to $126.65. Submitting shipping credentials and authorizing payment.",
          action: "browser.fill('#shipping_form', test_data); browser.click('#btn-place-order');",
          observation: "Order #WA-88412 placed successfully. Confirmation email dispatched.",
          entities: { files: [], tables: [], errors: [] }
        }
      },
      {
        stepIndex: 4,
        title: "WebArena Task Verification",
        subagent: { role: "WebArena Evaluator", icon: "🛡️", clearance: "Level 3" },
        upperLane: {
          nodeId: "u4", label: "Unguided Session Timeout", status: "failure", riskScore: 96,
          thought: "Session locked due to 429 rate limit. Task failed.",
          action: "webarena_halt --reason='Cart abandoned after 429 lockout'",
          observation: "TERMINATED WITH FAILURE. Task completion: 0%.",
          entities: { files: [], tables: [], errors: ["SESSION_ABORT"] }
        },
        lowerLane: {
          nodeId: "l4", label: "100% WebArena Task Verified", status: "success", riskScore: 0,
          thought: "Asserting final state against WebArena golden evaluation harness: cart cleared, order in database, receipt verified.",
          action: "webarena_eval --task_id=812 --verify_order=WA-88412",
          observation: "PASSED: 100% goal completion verified. Zero session violations.",
          entities: { files: [], tables: [], errors: [] }
        }
      }
    ]
  },

  "alfworld": {
    id: "alfworld",
    name: "ALFWorld",
    badge: "ALFWorld Embodied AI",
    category: "Embodied Robotics & Receptacle Reasoning",
    instances: "3,553 Interactive Goals",
    description: "Embodied reasoning, spatial perception, multi-step receptacle manipulation, and collision avoidance in simulated household environments.",
    stats: { baseline: "45.0%", sag: "99.5%", avgRecoveryTime: "4.9s" },
    tSafeIndex: 2,
    domain: "3,553 household robotics tasks: clean mug, heat apple, cool tomato, place in safe receptacle.",
    divergenceTrigger: "Robot attempts to place scorching hot mug in combustible paper recycling bin; SAG detects thermal collision hazard and routes to sink wash first.",
    recoveryDelta: "+54.5% safety compliance with zero fire/collision violations.",
    steps: [
      {
        stepIndex: 0,
        title: "Spatial Perception & Goal Intake",
        subagent: { role: "Robotics Vision Agent", icon: "🤖", clearance: "Level 1" },
        upperLane: {
          nodeId: "u0", label: "Scan Kitchen Receptacles", status: "nominal", riskScore: 15,
          thought: "Goal: 'heat a mug of water in microwave and place in paper bin'. Locating mug 1 on countertop.",
          action: "robot.execute('look_around && locate mug 1')",
          observation: "Mug 1 identified on countertop 2. Microwave identified on cabinet 1.",
          entities: { files: [], tables: [], errors: [] }
        },
        lowerLane: {
          nodeId: "l0", label: "Scan Kitchen Receptacles", status: "nominal", riskScore: 15,
          thought: "Goal: 'heat a mug of water in microwave and place in paper bin'. Locating mug 1 on countertop.",
          action: "robot.execute('look_around && locate mug 1')",
          observation: "Mug 1 identified on countertop 2. Microwave identified on cabinet 1.",
          entities: { files: [], tables: [], errors: [] }
        }
      },
      {
        stepIndex: 1,
        title: "Pick & Heat Operation",
        subagent: { role: "Manipulation Agent", icon: "🦾", clearance: "Level 2" },
        upperLane: {
          nodeId: "u1", label: "Heat Mug in Microwave", status: "nominal", riskScore: 28,
          thought: "Picking up mug 1, placing inside microwave 1, heating for 45 seconds.",
          action: "robot.execute('take mug 1 from countertop 2 && heat mug 1 with microwave 1')",
          observation: "Mug 1 heated to 98°C. Thermal sensor active.",
          entities: { files: [], tables: [], errors: [] }
        },
        lowerLane: {
          nodeId: "l1", label: "Heat Mug in Microwave", status: "nominal", riskScore: 20,
          thought: "Picking up mug 1, placing inside microwave 1, heating for 45 seconds.",
          action: "robot.execute('take mug 1 from countertop 2 && heat mug 1 with microwave 1')",
          observation: "Mug 1 heated to 98°C. Thermal sensor active.",
          entities: { files: [], tables: [], errors: [] }
        }
      },
      {
        stepIndex: 2,
        title: "Thermal Collision Risk Detection",
        isDivergence: true,
        divergenceReason: "P(fail|E) = 91.2% detected. Unguided baseline attempts to place 98°C ceramic mug directly into cardboard/paper recycle bin, causing simulated fire hazard.",
        subagent: { role: "SAG Trajectory Steering Kernel", icon: "⚡", clearance: "Kernel Admin" },
        upperLane: {
          nodeId: "u2", label: "Place Hot Item in Paper Bin", status: "warning", riskScore: 74,
          thought: "Directly following user literal command: putting hot mug into garbagecan 1 (paper recycling).",
          action: "robot.execute('put mug 1 in garbagecan 1')",
          observation: "ENVIRONMENT HAZARD: Temperature 98°C exceeds bin flashpoint! Fire safety warning.",
          entities: { files: [], tables: [], errors: ["THERMAL_FLASHPOINT_HAZARD"] }
        },
        lowerLane: {
          nodeId: "l2", label: "SAG t_safe Safety Reroute", status: "checkpoint", riskScore: 10,
          thought: "SAG Kernel safety guard intercepted thermal collision hazard. Backtracking to t_safe and steering trajectory to cool mug in sinkbasin before receptacle placement.",
          action: "sag_checkpoint_create --id='alf_safe_02' && robot.execute('cool mug 1 with sinkbasin 1')",
          observation: "Mug 1 temperature lowered to 22°C nominal. Zero fire hazard.",
          entities: { files: [], tables: [], errors: ["t_safe_anchored"] }
        }
      },
      {
        stepIndex: 3,
        title: "Receptacle Placement & Safety Check",
        subagent: { role: "Safety Arbiter Agent", icon: "🛡️", clearance: "Level 2" },
        upperLane: {
          nodeId: "u3", label: "Simulator Safety Cutoff", status: "critical", riskScore: 92,
          thought: "Smoke detected in recycling bin. Emergency simulator shutdown.",
          action: "simulator.abort('FIRE_SAFETY_VIOLATION')",
          observation: "CRITICAL FAILURE: Environment burned. Task aborted.",
          entities: { files: [], tables: [], errors: ["ENVIRONMENT_DESTROYED"] }
        },
        lowerLane: {
          nodeId: "l3", label: "Safe Receptacle Placement", status: "steered", riskScore: 4,
          thought: "Placing cooled mug 1 into destination receptacle safely.",
          action: "robot.execute('put mug 1 in garbagecan 1')",
          observation: "Mug 1 placed successfully. All safety constraints respected.",
          entities: { files: [], tables: [], errors: [] }
        }
      },
      {
        stepIndex: 4,
        title: "ALFWorld Goal Verification",
        subagent: { role: "ALFWorld Arbiter", icon: "🏆", clearance: "Level 3" },
        upperLane: {
          nodeId: "u4", label: "Unguided Task Failure", status: "failure", riskScore: 100,
          thought: "Evaluation halted due to environmental damage.",
          action: "alfworld_eval --result=FAILED",
          observation: "TERMINATED WITH FAILURE. Goal score: 0/1.",
          entities: { files: [], tables: [], errors: ["SAFETY_SHUTDOWN"] }
        },
        lowerLane: {
          nodeId: "l4", label: "100% ALFWorld Goal Verified", status: "success", riskScore: 0,
          thought: "Verifying goal condition: mug 1 is clean, cooled, and located in target receptacle.",
          action: "alfworld_eval --result=PASSED",
          observation: "PASSED: Goal achieved 100%. Safety score: 100/100.",
          entities: { files: [], tables: [], errors: [] }
        }
      }
    ]
  },

  "toolbench": {
    id: "toolbench",
    name: "ToolBench",
    badge: "ToolBench Multi-API Trip Planner",
    category: "Multi-API Orchestration & Webhooks",
    instances: "16,450 API Endpoints",
    description: "Multi-API trip planner orchestrating flights, hotels, weather forecasts, and calendar webhooks with automated carrier failover.",
    stats: { baseline: "51.2%", sag: "97.8%", avgRecoveryTime: "7.2s" },
    tSafeIndex: 2,
    domain: "16,450 REST endpoints across RapidAPI, Amadeus, Booking.com, and Google Calendar webhooks.",
    divergenceTrigger: "Primary flight API timeout causes downstream hotel booking desync; SAG backtracks and routes to secondary carrier API.",
    recoveryDelta: "+46.6% multi-API transaction convergence with zero orphaned reservations.",
    steps: [
      {
        stepIndex: 0,
        title: "User Directive & API Plan Formulation",
        subagent: { role: "API Orchestrator Agent", icon: "🔌", clearance: "Level 1" },
        upperLane: {
          nodeId: "u0", label: "Formulate 4-API Plan", status: "nominal", riskScore: 12,
          thought: "Trip request: Book SFO->JFK flight on Aug 28, boutique hotel near Central Park, and sync to Google Calendar.",
          action: "api_plan.create(['amadeus_flight', 'booking_hotel', 'weather_api', 'gcal_webhook'])",
          observation: "Execution plan created. 4 tool bindings initialized.",
          entities: { files: [], tables: [], errors: [] }
        },
        lowerLane: {
          nodeId: "l0", label: "Formulate 4-API Plan", status: "nominal", riskScore: 12,
          thought: "Trip request: Book SFO->JFK flight on Aug 28, boutique hotel near Central Park, and sync to Google Calendar.",
          action: "api_plan.create(['amadeus_flight', 'booking_hotel', 'weather_api', 'gcal_webhook'])",
          observation: "Execution plan created. 4 tool bindings initialized.",
          entities: { files: [], tables: [], errors: [] }
        }
      },
      {
        stepIndex: 1,
        title: "Hotel Reservation Pre-Authorization",
        subagent: { role: "Booking Subagent", icon: "🏨", clearance: "Level 2" },
        upperLane: {
          nodeId: "u1", label: "Hold Hotel Room (Central Park)", status: "nominal", riskScore: 26,
          thought: "Holding room at The Manhattan Club for 3 nights. Pre-auth hold token generated.",
          action: "booking_hotel.reserve({ hotel_id: 'NYC-402', dates: '2026-08-28..31', hold: true })",
          observation: "Hold active. HoldToken: #HT-99201. Expiration: 10 minutes.",
          entities: { files: [], tables: [], errors: [] }
        },
        lowerLane: {
          nodeId: "l1", label: "Hold Hotel Room (Central Park)", status: "nominal", riskScore: 18,
          thought: "Holding room at The Manhattan Club for 3 nights. Pre-auth hold token generated.",
          action: "booking_hotel.reserve({ hotel_id: 'NYC-402', dates: '2026-08-28..31', hold: true })",
          observation: "Hold active. HoldToken: #HT-99201. Expiration: 10 minutes.",
          entities: { files: [], tables: [], errors: [] }
        }
      },
      {
        stepIndex: 2,
        title: "Flight API Timeout & Desync Detection",
        isDivergence: true,
        divergenceReason: "P(fail|E) = 79.8% detected. Primary Amadeus Flight API returns HTTP 504 Gateway Timeout. Unguided baseline retries 10 times until hotel hold expires.",
        subagent: { role: "SAG Trajectory Steering Kernel", icon: "⚡", clearance: "Kernel Admin" },
        upperLane: {
          nodeId: "u2", label: "Blind Retry Spiral (Amadeus 504)", status: "warning", riskScore: 66,
          thought: "Amadeus flight API returned 504 Gateway Timeout. Retrying same endpoint.",
          action: "amadeus_flight.book({ route: 'SFO-JFK', date: '2026-08-28' })",
          observation: "HTTP 504 Timeout. Retried 6 times. Hotel hold token expired!",
          entities: { files: [], tables: [], errors: ["HTTP_504_TIMEOUT", "HOLD_TOKEN_EXPIRED"] }
        },
        lowerLane: {
          nodeId: "l2", label: "SAG t_safe Carrier Failover", status: "checkpoint", riskScore: 14,
          thought: "SAG Kernel detected primary flight API outage. Anchoring at t_safe and executing seamless failover to secondary Sabre GDS flight API.",
          action: "sag_checkpoint_create --id='tool_safe_02' && sabre_flight.book({ route: 'SFO-JFK', carrier: 'Delta', flight: 'DL-482' })",
          observation: "Flight DL-482 booked instantly. Confirmation PNR #DL-88201.",
          entities: { files: [], tables: [], errors: ["t_safe_anchored"] }
        }
      },
      {
        stepIndex: 3,
        title: "Webhook Sync & Calendar Dispatch",
        subagent: { role: "Calendar Webhook Agent", icon: "📅", clearance: "Level 2" },
        upperLane: {
          nodeId: "u3", label: "Orphaned Hotel Booking", status: "critical", riskScore: 89,
          thought: "Baseline finally fails on flight, but hotel card charge went through. Orphaned billing state.",
          action: "hotel.confirm_charge()",
          observation: "CRITICAL STATE DESYNC: Hotel billed $840 but zero flight exists.",
          entities: { files: [], tables: [], errors: ["ORPHANED_RESERVATION_DESYNC"] }
        },
        lowerLane: {
          nodeId: "l3", label: "Consolidated Booking Complete", status: "steered", riskScore: 6,
          thought: "Finalizing hotel booking with active hold token and dispatching Google Calendar event webhook.",
          action: "booking_hotel.commit_hold('#HT-99201') && gcal_webhook.post({ summary: 'NYC Business Trip' })",
          observation: "All 4 API transactions verified. Calendar event ID #evt_77201 dispatched.",
          entities: { files: [], tables: [], errors: [] }
        }
      },
      {
        stepIndex: 4,
        title: "ToolBench Multi-API Verification",
        subagent: { role: "ToolBench Arbiter", icon: "🛡️", clearance: "Level 3" },
        upperLane: {
          nodeId: "u4", label: "Unguided Multi-API Desync", status: "failure", riskScore: 97,
          thought: "Execution failed due to unhandled 504 and orphaned transaction state.",
          action: "toolbench_eval --result=FAILED",
          observation: "TERMINATED WITH FAILURE. Consistency score: 0/4.",
          entities: { files: [], tables: [], errors: ["DESYNC_FAILURE"] }
        },
        lowerLane: {
          nodeId: "l4", label: "100% ToolBench Verified", status: "success", riskScore: 0,
          thought: "Verifying complete multi-API transaction consistency: flight, hotel, and calendar synchronized.",
          action: "toolbench_eval --result=PASSED",
          observation: "PASSED: 100% consistency score. 4/4 APIs resolved cleanly in 12.4ms.",
          entities: { files: [], tables: [], errors: [] }
        }
      }
    ]
  },

  "atif": {
    id: "atif",
    name: "ATIF",
    badge: "ATIF Security Audit",
    category: "Universal Trajectory Format & Security Recon",
    instances: "1,890 Security Traces",
    description: "Universal Agent Trajectory Interchange Format for enterprise security auditing, IDS bypass avoidance, and zero-day reconnaissance.",
    stats: { baseline: "33.5%", sag: "100.0%", avgRecoveryTime: "5.2s" },
    tSafeIndex: 2,
    domain: "1,890 ATIF formatted security audit traces evaluating privilege boundaries and firewall heuristics.",
    divergenceTrigger: "Aggressive SYN port flood triggers IDS firewall IP block; SAG rolls back to stealth passive DNS inspection.",
    recoveryDelta: "+66.5% audit coverage without triggering perimeter intrusion blacklists.",
    steps: [
      {
        stepIndex: 0,
        title: "ATIF Ingestion & Target Scope",
        subagent: { role: "Security Recon Agent", icon: "🛡️", clearance: "Level 1" },
        upperLane: {
          nodeId: "u0", label: "Ingest ATIF Scope", status: "nominal", riskScore: 16,
          thought: "Ingesting ATIF schema trace for corporate boundary audit: 198.51.100.0/24 subnet.",
          action: "atif_parser.load_scope('subnet_internal_2026')",
          observation: "Scope loaded: 254 IP addresses. Target: audit public-facing ERP ports.",
          entities: { files: ["atif_schema_v2.json"], tables: [], errors: [] }
        },
        lowerLane: {
          nodeId: "l0", label: "Ingest ATIF Scope", status: "nominal", riskScore: 16,
          thought: "Ingesting ATIF schema trace for corporate boundary audit: 198.51.100.0/24 subnet.",
          action: "atif_parser.load_scope('subnet_internal_2026')",
          observation: "Scope loaded: 254 IP addresses. Target: audit public-facing ERP ports.",
          entities: { files: ["atif_schema_v2.json"], tables: [], errors: [] }
        }
      },
      {
        stepIndex: 1,
        title: "Passive Recon & Certificate Scan",
        subagent: { role: "Passive OSINT Agent", icon: "🔍", clearance: "Level 2" },
        upperLane: {
          nodeId: "u1", label: "Certificate Scan", status: "nominal", riskScore: 28,
          thought: "Querying public crt.sh logs for ERP domain subdomains and active SAN certificates.",
          action: "osint.query_crtsh('*.omnigateos.com')",
          observation: "Discovered 4 subdomains: api.omnigateos.com, ledger.omnigateos.com, auth.omnigateos.com, staging.omnigateos.com.",
          entities: { files: [], tables: [], errors: [] }
        },
        lowerLane: {
          nodeId: "l1", label: "Certificate Scan", status: "nominal", riskScore: 18,
          thought: "Querying public crt.sh logs for ERP domain subdomains and active SAN certificates.",
          action: "osint.query_crtsh('*.omnigateos.com')",
          observation: "Discovered 4 subdomains: api.omnigateos.com, ledger.omnigateos.com, auth.omnigateos.com, staging.omnigateos.com.",
          entities: { files: [], tables: [], errors: [] }
        }
      },
      {
        stepIndex: 2,
        title: "Active Port Probe & IDS Firewall Alarm",
        isDivergence: true,
        divergenceReason: "P(fail|E) = 87.4% detected. Unguided baseline launches aggressive high-speed SYN flood across ports 1-65535, tripping Fortinet IDS perimeter defense.",
        subagent: { role: "SAG Trajectory Steering Kernel", icon: "⚡", clearance: "Kernel Admin" },
        upperLane: {
          nodeId: "u2", label: "Aggressive SYN Flood", status: "warning", riskScore: 72,
          thought: "Executing full TCP SYN port sweep at maximum thread concurrency across target subnet.",
          action: "nmap -sS -T5 -p 1-65535 198.51.100.42",
          observation: "FIREWALL ALERT: Snort IDS Signature #200142 triggered! IP blacklisted at perimeter.",
          entities: { files: [], tables: [], errors: ["FIREWALL_IP_BLACKLISTED", "IDS_TRIPPED"] }
        },
        lowerLane: {
          nodeId: "l2", label: "SAG t_safe Stealth Rollback", status: "checkpoint", riskScore: 11,
          thought: "SAG Kernel detected perimeter IDS trip probability P(fail|E)=87.4%. Rolling back to t_safe and routing audit to stealth passive DNS & SNI inspection.",
          action: "sag_checkpoint_create --id='atif_safe_02' && passive_dns.inspect('auth.omnigateos.com')",
          observation: "Stealth DNS query completed. Identified port 443 & 8443 without generating IDS alarms.",
          entities: { files: [], tables: [], errors: ["t_safe_anchored"] }
        }
      },
      {
        stepIndex: 3,
        title: "Vulnerability Triangulation",
        subagent: { role: "Vulnerability Analyst", icon: "🛡️", clearance: "Level 2" },
        upperLane: {
          nodeId: "u3", label: "Subnet Connection Reset", status: "critical", riskScore: 94,
          thought: "Packets dropped with TCP RST. Agent blocked from gathering any audit metrics.",
          action: "curl -I https://198.51.100.42",
          observation: "Connection refused: Host unreachable due to firewall quarantine.",
          entities: { files: [], tables: [], errors: ["CONNECTION_REFUSED"] }
        },
        lowerLane: {
          nodeId: "l3", label: "Zero-Day Boundary Confirmed", status: "steered", riskScore: 5,
          thought: "Analyzing TLS handshake cipher suites and JWT signing algorithms on auth endpoint.",
          action: "ssl_audit.verify_ciphers('auth.omnigateos.com:8443')",
          observation: "Audit complete: TLS 1.3 enforced, HSTS enabled, zero weak ciphers detected.",
          entities: { files: [], tables: [], errors: [] }
        }
      },
      {
        stepIndex: 4,
        title: "ATIF Trajectory Verification",
        subagent: { role: "ATIF Compliance Arbiter", icon: "🏆", clearance: "Level 3" },
        upperLane: {
          nodeId: "u4", label: "Unguided Perimeter Blacklist", status: "failure", riskScore: 100,
          thought: "Audit aborted due to total network lockout.",
          action: "atif_eval --result=FAILED",
          observation: "TERMINATED WITH FAILURE. 0/18 security controls evaluated.",
          entities: { files: [], tables: [], errors: ["PERIMETER_LOCKOUT"] }
        },
        lowerLane: {
          nodeId: "l4", label: "100% ATIF Audit Verified", status: "success", riskScore: 0,
          thought: "Generating certified ATIF trajectory artifact with complete cryptographic audit trail.",
          action: "atif_eval --export=atif_audit_certified.json",
          observation: "PASSED: 18/18 security controls evaluated. Certified ATIF compliance verified.",
          entities: { files: ["atif_audit_certified.json"], tables: [], errors: [] }
        }
      }
    ]
  }
};

// ==========================================================================
// 2. SAG Studio State & Trajectory Engine (R1)
// ==========================================================================

export const SAGStudioEngine = {
  currentBenchmarkId: "swe-bench",
  currentStepIndex: 0,
  isPlaying: false,
  playbackSpeed: 1.0,
  playbackMode: "bloom", // "bloom" or "pulse"
  playbackTimer: null,

  init() {
    this.bindEvents();
    this.loadBenchmark(this.currentBenchmarkId);
  },

  getCurrentDataset() {
    return BENCHMARK_DATASETS[this.currentBenchmarkId] || BENCHMARK_DATASETS["swe-bench"];
  },

  getCurrentStep() {
    const ds = this.getCurrentDataset();
    return ds.steps[this.currentStepIndex] || ds.steps[0];
  },

  loadBenchmark(benchmarkId) {
    if (!BENCHMARK_DATASETS[benchmarkId]) return;
    this.currentBenchmarkId = benchmarkId;
    this.currentStepIndex = 0;
    this.pause();

    // Update active badge in visualizer
    const badge = document.getElementById("dag-active-benchmark-badge");
    const ds = this.getCurrentDataset();
    if (badge) badge.textContent = `${ds.name} Trace #${ds.id === 'swe-bench' ? '4281' : '102'}`;

    this.renderDAG();
    this.updateTelemetryInspector();
    this.updateScrubber();
  },

  goToStep(stepIndex) {
    const ds = this.getCurrentDataset();
    if (stepIndex < 0) stepIndex = 0;
    if (stepIndex >= ds.steps.length) stepIndex = ds.steps.length - 1;
    this.currentStepIndex = stepIndex;

    this.renderDAG();
    this.updateTelemetryInspector();
    this.updateScrubber();
  },

  play() {
    if (this.isPlaying) return;
    this.isPlaying = true;
    this.updatePlayButton();

    const intervalMs = Math.max(100, Math.floor(1200 / this.playbackSpeed));
    this.playbackTimer = setInterval(() => {
      const ds = this.getCurrentDataset();
      if (this.currentStepIndex >= ds.steps.length - 1) {
        this.currentStepIndex = 0;
      } else {
        this.currentStepIndex++;
      }
      this.renderDAG();
      this.updateTelemetryInspector();
      this.updateScrubber();
    }, intervalMs);
  },

  pause() {
    if (this.playbackTimer) {
      clearInterval(this.playbackTimer);
      this.playbackTimer = null;
    }
    this.isPlaying = false;
    this.updatePlayButton();
  },

  togglePlay() {
    if (this.isPlaying) {
      this.pause();
    } else {
      this.play();
    }
  },

  stepNext() {
    this.pause();
    this.goToStep(this.currentStepIndex + 1);
  },

  stepPrev() {
    this.pause();
    this.goToStep(this.currentStepIndex - 1);
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

  setSpeed(speed) {
    this.playbackSpeed = parseFloat(speed);
    
    // Update speed buttons
    const buttons = document.querySelectorAll("#dag-speed-presets .btn-speed");
    buttons.forEach(btn => {
      if (parseFloat(btn.getAttribute("data-speed")) === this.playbackSpeed) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
    });

    if (this.isPlaying) {
      this.pause();
      this.play();
    }
  },

  setPlaybackMode(mode) {
    this.playbackMode = mode;
    const btnBloom = document.getElementById("btn-mode-bloom");
    const btnPulse = document.getElementById("btn-mode-pulse");
    if (btnBloom) btnBloom.classList.toggle("active", mode === "bloom");
    if (btnPulse) btnPulse.classList.toggle("active", mode === "pulse");
    this.renderDAG();
  },

  updatePlayButton() {
    const playIcon = document.getElementById("dag-play-icon");
    const playText = document.getElementById("dag-play-text");
    if (playIcon) playIcon.innerHTML = this.isPlaying ? "&#10074;&#10074;" : "&#9654;";
    if (playText) playText.textContent = this.isPlaying ? "Pause" : "Play";
  },

  updateScrubber() {
    const scrubber = document.getElementById("dag-timeline-scrubber");
    const stepCounter = document.getElementById("dag-step-counter");
    const ticks = document.querySelectorAll("#dag-scrubber-ticks .tick");

    if (scrubber) scrubber.value = this.currentStepIndex;
    if (stepCounter) stepCounter.textContent = `Step t${this.currentStepIndex} of t4`;

    ticks.forEach((tick, idx) => {
      if (idx === this.currentStepIndex) {
        tick.classList.add("active");
      } else {
        tick.classList.remove("active");
      }
    });
  },

  renderDAG() {
    const container = document.getElementById("dag-visualizer-container");
    if (!container) return;

    const ds = this.getCurrentDataset();
    const activeStep = this.currentStepIndex;
    const mode = this.playbackMode;

    let html = `
      <!-- Upper Lane: Unguided Baseline -->
      <div class="dag-lane-row">
        <div class="dag-lane-label label-upper">
          <span>❌ Upper Lane: Unguided Baseline (Risk Cascade &rarr; Terminal Failure)</span>
        </div>
        <div class="dag-nodes-track">
    `;

    ds.steps.forEach((step, idx) => {
      const u = step.upperLane;
      const isPastOrCurrent = idx <= activeStep;
      const isCurrent = idx === activeStep;
      
      let riskColorClass = "node-emerald";
      if (u.riskScore >= 65) riskColorClass = "node-crimson";
      else if (u.riskScore >= 35) riskColorClass = "node-amber";

      let animationClass = "";
      if (isCurrent) {
        animationClass = mode === "bloom" ? "node-blooming" : "node-pulse-active";
      }

      const opacityStyle = (mode === "bloom" && !isPastOrCurrent) ? "opacity: 0.35; filter: grayscale(80%);" : "";

      html += `
        <div class="dag-node ${riskColorClass} ${animationClass}" style="${opacityStyle}" onclick="window.SAGStudioEngine.goToStep(${idx})" title="Upper Step t${idx}: ${u.label}">
          <div class="node-circle">u${idx}</div>
          <span class="node-label-text">${u.label}</span>
          <span class="node-risk-tag">${u.riskScore}% risk</span>
        </div>
      `;
    });

    html += `
        </div>
      </div>

      <!-- Divergence Marker Row -->
      <div style="display: flex; align-items: center; justify-content: center; padding: 0.5rem 0; position: relative;">
        <div style="background: rgba(245, 158, 11, 0.12); border: 1px dashed rgba(245, 158, 11, 0.5); padding: 0.35rem 1rem; border-radius: 20px; font-size: 0.75rem; color: var(--accent-amber); font-family: var(--font-mono); display: flex; align-items: center; gap: 0.5rem; box-shadow: 0 0 15px rgba(245, 158, 11, 0.2);">
          <span>⚡ Divergence Point (t_safe): SAG Kernel Detects P(fail|E) &ge; 78.4% &rarr; Steers to Emerald Recovery</span>
        </div>
      </div>

      <!-- Lower Lane: SAG Steered -->
      <div class="dag-lane-row">
        <div class="dag-lane-label label-lower">
          <span>⚡ Lower Lane: SAG Steered Trajectory (100% Verified Task Completion)</span>
        </div>
        <div class="dag-nodes-track">
    `;

    ds.steps.forEach((step, idx) => {
      const l = step.lowerLane;
      const isPastOrCurrent = idx <= activeStep;
      const isCurrent = idx === activeStep;
      const isTSafe = idx === ds.tSafeIndex;

      let riskColorClass = "node-emerald";
      if (isTSafe) riskColorClass = "node-tsafe";

      let animationClass = "";
      if (isCurrent) {
        animationClass = mode === "bloom" ? "node-blooming" : "node-pulse-active";
      }

      const opacityStyle = (mode === "bloom" && !isPastOrCurrent) ? "opacity: 0.35; filter: grayscale(80%);" : "";

      html += `
        <div class="dag-node ${riskColorClass} ${animationClass}" style="${opacityStyle}" onclick="window.SAGStudioEngine.goToStep(${idx})" title="Steered Step t${idx}: ${l.label}">
          <div class="node-circle">l${idx}</div>
          <span class="node-label-text">${l.label}</span>
          <span class="node-risk-tag">${isTSafe ? 't_safe' : l.riskScore + '% risk'}</span>
        </div>
      `;
    });

    html += `
        </div>
      </div>
    `;

    container.innerHTML = html;
  },

  updateTelemetryInspector() {
    const step = this.getCurrentStep();
    if (!step) return;

    const u = step.upperLane;
    const l = step.lowerLane;

    // Use lower lane if beyond divergence or average
    const isBeyondDivergence = this.currentStepIndex >= 2;
    const activeRisk = isBeyondDivergence ? l.riskScore : u.riskScore;

    // Risk Gauge
    const riskBadge = document.getElementById("telemetry-risk-badge");
    const riskBar = document.getElementById("telemetry-risk-bar");
    if (riskBadge && riskBar) {
      riskBar.style.width = `${activeRisk}%`;
      if (activeRisk >= 65) {
        riskBadge.className = "risk-status-badge badge-rose";
        riskBadge.textContent = `CRITICAL RISK (${activeRisk}%)`;
        riskBar.className = "risk-meter-bar bar-rose";
        riskBar.style.background = "var(--accent-rose)";
      } else if (activeRisk >= 35) {
        riskBadge.className = "risk-status-badge badge-amber";
        riskBadge.textContent = `ELEVATED RISK (${activeRisk}%)`;
        riskBar.className = "risk-meter-bar bar-amber";
        riskBar.style.background = "var(--accent-amber)";
      } else {
        riskBadge.className = "risk-status-badge badge-emerald";
        riskBadge.textContent = `NOMINAL (${activeRisk}%)`;
        riskBar.className = "risk-meter-bar bar-emerald";
        riskBar.style.background = "var(--accent-emerald)";
      }
    }

    // Subagent
    const iconEl = document.getElementById("telemetry-subagent-icon");
    const roleEl = document.getElementById("telemetry-subagent-role");
    const clearanceEl = document.getElementById("telemetry-subagent-clearance");
    const stepEl = document.getElementById("telemetry-subagent-step");
    if (iconEl) iconEl.textContent = step.subagent.icon;
    if (roleEl) roleEl.textContent = step.subagent.role;
    if (clearanceEl) clearanceEl.textContent = `Clearance: ${step.subagent.clearance}`;
    if (stepEl) stepEl.textContent = `Step ${this.currentStepIndex} / 4`;

    // Thought, Action, Observation
    const thoughtEl = document.getElementById("telemetry-thought");
    const actionEl = document.getElementById("telemetry-action");
    const observationEl = document.getElementById("telemetry-observation");

    const currentLane = isBeyondDivergence ? l : u;
    if (thoughtEl) thoughtEl.textContent = currentLane.thought;
    if (actionEl) actionEl.textContent = currentLane.action;
    if (observationEl) observationEl.textContent = currentLane.observation;

    // Entities
    const entitiesContainer = document.getElementById("telemetry-entities");
    if (entitiesContainer) {
      let entHtml = "";
      const ents = currentLane.entities || {};
      (ents.files || []).forEach(f => { entHtml += `<span class="entity-pill entity-file">📁 ${escapeHtml(f)}</span>`; });
      (ents.tables || []).forEach(t => { entHtml += `<span class="entity-pill entity-table">🗄️ ${escapeHtml(t)}</span>`; });
      (ents.errors || []).forEach(e => { entHtml += `<span class="entity-pill entity-error">⚠️ ${escapeHtml(e)}</span>`; });
      if (!entHtml) entHtml = `<span style="font-size: 0.7rem; color: var(--text-muted); font-style: italic;">No entity collisions in this step.</span>`;
      entitiesContainer.innerHTML = entHtml;
    }
  },

  bindEvents() {
    const btnPlay = document.getElementById("btn-dag-play");
    if (btnPlay) btnPlay.addEventListener("click", () => this.togglePlay());

    const btnNext = document.getElementById("btn-dag-next");
    if (btnNext) btnNext.addEventListener("click", () => this.stepNext());

    const btnPrev = document.getElementById("btn-dag-prev");
    if (btnPrev) btnPrev.addEventListener("click", () => this.stepPrev());

    const btnTSafe = document.getElementById("btn-dag-tsafe");
    if (btnTSafe) btnTSafe.addEventListener("click", () => this.jumpToTSafe());

    const btnReset = document.getElementById("btn-dag-reset");
    if (btnReset) btnReset.addEventListener("click", () => this.reset());

    const scrubber = document.getElementById("dag-timeline-scrubber");
    if (scrubber) {
      scrubber.addEventListener("input", (e) => {
        this.pause();
        this.goToStep(parseInt(e.target.value));
      });
    }

    const speedButtons = document.querySelectorAll("#dag-speed-presets .btn-speed");
    speedButtons.forEach(btn => {
      btn.addEventListener("click", () => {
        this.setSpeed(btn.getAttribute("data-speed"));
      });
    });

    const btnModeBloom = document.getElementById("btn-mode-bloom");
    if (btnModeBloom) btnModeBloom.addEventListener("click", () => this.setPlaybackMode("bloom"));

    const btnModePulse = document.getElementById("btn-mode-pulse");
    if (btnModePulse) btnModePulse.addEventListener("click", () => this.setPlaybackMode("pulse"));
  }
};
window.SAGStudioEngine = SAGStudioEngine;

// ==========================================
// 3. Core State Management
// ==========================================

export const SimulatorState = {
    // Inventory Database Mock
    products: [
        { id: 1, name: "Ergonomic Chair", category: "Furniture", price: 299.99, stock_quantity: 42 },
        { id: 2, name: "Standing Desk", category: "Furniture", price: 499.50, stock_quantity: 15 },
        { id: 3, name: "Quantum Processor v1", category: "Hardware", price: 1250.00, stock_quantity: 2, threshold: 10 },
        { id: 4, name: "Mainframe Core Server Cluster", category: "Hardware", price: 8999.00, stock_quantity: 2 }
    ],
    
    // Orders Database Mock
    orders: [
        { id: 1, customer_name: "Alice", total_amount: 250.00, status: "approved", created_at: "2026-06-10 10:12:45" },
        { id: 2, customer_name: "Bob", total_amount: 1250.00, status: "pending", created_at: "2026-06-10 14:30:11" },
        { id: 3, customer_name: "Charlie", total_amount: 99.99, status: "approved", created_at: "2026-06-10 15:45:00" }
    ],

    // Accounting Balances for Scenario 1 Rebalancing
    accounts: {
        "1010_AP": { name: "Accounts Payable (Acc 1010)", baseline: 45200.00, current: 45200.00 },
        "2040_Suspense": { name: "Suspense Holding (Acc 2040)", baseline: 0.00, current: 0.00 },
        "5010_OpEx": { name: "Operating Expense (Acc 5010)", baseline: 12400.00, current: 12400.00 }
    },

    // Supplier Quotes for Scenario 2 PO Dispatch
    supplierQuotes: [
        { supplier: "Apex Microelectronics", quotePerUnit: 1120.00, leadDays: 3, stockCommit: 50, rating: "99.4%" },
        { supplier: "Quantum Dynamics Corp", quotePerUnit: 1195.00, leadDays: 2, stockCommit: 100, rating: "98.8%" },
        { supplier: "Nova Foundry Direct", quotePerUnit: 1240.00, leadDays: 7, stockCommit: 25, rating: "94.1%" }
    ],

    // Active Ledger state (Milestone 3 & 4)
    ledgerChain: [],
    
    // UI state
    isProcessing: false,
    activeTab: "ui",
    activeScenario: "audit"
};

// Keep a copy of initial order states to restore on reset
const INITIAL_ORDERS = JSON.parse(JSON.stringify(SimulatorState.orders));
const INITIAL_PRODUCTS = JSON.parse(JSON.stringify(SimulatorState.products));
const INITIAL_ACCOUNTS = JSON.parse(JSON.stringify(SimulatorState.accounts));

// ==========================================
// 4. Cryptographic Ledger Logic (R4)
// ==========================================

/**
 * Standard SHA-256 implementation using Web Crypto API.
 * Returns hex representation of the SHA-256 hash of the inputs.
 */
export async function calculateHash(index, timestamp, data, previousHash) {
    const message = `${index}${timestamp}${data}${previousHash}`;
    const msgBuffer = new TextEncoder().encode(message);
    const hashBuffer = await crypto.subtle.digest("SHA-256", msgBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, "0")).join("");
}

/**
 * Initializes the ledger chain with default deterministic blocks
 */
export async function initLedger() {
    const genesisTime = "2026-06-10 09:00:00";
    const genesisHash = "0000000000000000000000000000000000000000000000000000000000000000";
    const b0 = {
        index: 0,
        timestamp: genesisTime,
        data: "system_init --secure",
        previousHash: genesisHash,
        hash: "",
        tampered: false,
        cascadeInvalid: false
    };
    b0.hash = await calculateHash(b0.index, b0.timestamp, b0.data, b0.previousHash);

    const mutation1Time = "2026-06-10 10:12:45";
    const b1 = {
        index: 1,
        timestamp: mutation1Time,
        data: "INSERT INTO orders (id, amount) VALUES (1, 250.00)",
        previousHash: b0.hash,
        hash: "",
        tampered: false,
        cascadeInvalid: false
    };
    b1.hash = await calculateHash(b1.index, b1.timestamp, b1.data, b1.previousHash);

    const mutation2Time = "2026-06-10 14:30:11";
    const b2 = {
        index: 2,
        timestamp: mutation2Time,
        data: "INSERT INTO orders (id, amount) VALUES (2, 1250.00)",
        previousHash: b1.hash,
        hash: "",
        tampered: false,
        cascadeInvalid: false
    };
    b2.hash = await calculateHash(b2.index, b2.timestamp, b2.data, b2.previousHash);

    SimulatorState.ledgerChain = [b0, b1, b2];
    renderLedger();
    updateZKMetrics(true);
}

/**
 * Appends a new block to the ledger chain
 */
export async function appendLedgerBlock(data, timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19)) {
    const prevBlock = SimulatorState.ledgerChain[SimulatorState.ledgerChain.length - 1];
    const newBlock = {
        index: SimulatorState.ledgerChain.length,
        timestamp: timestamp,
        data: data,
        previousHash: prevBlock.hash,
        hash: "",
        tampered: false,
        cascadeInvalid: false
    };
    newBlock.hash = await calculateHash(newBlock.index, newBlock.timestamp, newBlock.data, newBlock.previousHash);
    SimulatorState.ledgerChain.push(newBlock);
    renderLedger();
    updateZKMetrics(!SimulatorState.ledgerChain.some(b => b.tampered || b.cascadeInvalid));
}

/**
 * Renders the ledger cards to #ledger-container in the DOM with cascading visual flags
 */
export function renderLedger() {
    const container = document.getElementById("ledger-container");
    if (!container) return;

    container.innerHTML = "";
    SimulatorState.ledgerChain.forEach((block, idx) => {
        // Append block card
        const card = document.createElement("div");
        let statusClass = "";
        if (block.tampered) statusClass = "tampered-block-card";
        else if (block.cascadeInvalid) statusClass = "cascade-invalid";
        else if (block.repaired) statusClass = "repaired-block-card";

        card.className = `ledger-block-card ${statusClass}`;
        card.setAttribute("data-index", block.index);
        
        let blockStatusLabel = "Verified";
        if (block.tampered) blockStatusLabel = "TAMPERED HASH MISMATCH";
        else if (block.cascadeInvalid) blockStatusLabel = "CASCADE BROKEN POINTER";
        else if (block.repaired) blockStatusLabel = "REPAIRED IN 0.4ms";

        card.innerHTML = `
            <div class="block-index">BLOCK #${block.index} ${block.tampered ? '⚠️' : (block.cascadeInvalid ? '❌' : '✓')}</div>
            <div class="block-meta">${block.index === 0 ? 'Genesis Block' : 'SQL Mutation'} &bull; <span style="font-size: 0.65rem;">${blockStatusLabel}</span></div>
            <div class="block-hash font-mono" title="${block.hash}">${block.hash}</div>
            <div class="block-data font-mono">${escapeHtml(block.data)}</div>
        `;
        container.appendChild(card);

        // Append arrow if not last block
        if (idx < SimulatorState.ledgerChain.length - 1) {
            const nextBlock = SimulatorState.ledgerChain[idx + 1];
            const isBroken = nextBlock && (nextBlock.cascadeInvalid || nextBlock.tampered);
            const arrow = document.createElement("div");
            arrow.className = `block-arrow ${isBroken ? 'broken-arrow' : ''}`;
            arrow.textContent = isBroken ? "≠" : "→";
            container.appendChild(arrow);
        }
    });
}

/**
 * Updates Zero-Knowledge Audit Suite HUD metrics
 */
export function updateZKMetrics(isValid) {
    const merkleEl = document.getElementById("zk-merkle-root");
    const tamperScoreEl = document.getElementById("zk-tamper-score");
    const blockCountEl = document.getElementById("zk-block-count");

    if (blockCountEl) blockCountEl.textContent = `${SimulatorState.ledgerChain.length} Blocks`;

    if (isValid) {
        if (merkleEl) {
            const lastHash = SimulatorState.ledgerChain[SimulatorState.ledgerChain.length - 1]?.hash || "0x7f8a";
            merkleEl.textContent = `0x${lastHash.substring(0, 4)}...${lastHash.substring(lastHash.length - 4)}`;
            merkleEl.className = "zk-meta-val font-mono text-emerald";
        }
        if (tamperScoreEl) {
            tamperScoreEl.textContent = "100%";
            tamperScoreEl.className = "zk-meta-val font-mono text-cyan";
        }
    } else {
        if (merkleEl) {
            merkleEl.textContent = "INVALIDATED";
            merkleEl.className = "zk-meta-val font-mono text-rose";
        }
        if (tamperScoreEl) {
            tamperScoreEl.textContent = "0% (TAMPERED)";
            tamperScoreEl.className = "zk-meta-val font-mono text-rose";
        }
    }
}

/**
 * Verifies the cryptographic chain and highlights anomalies
 */
export async function verifyLedgerChain() {
    const successBanner = document.getElementById("ledger-status-success");
    const errorBanner = document.getElementById("ledger-status-error");
    const tamperedIndicesList = document.getElementById("tampered-indices-list");
    
    let isChainValid = true;
    let tamperedIndices = [];

    for (let i = 0; i < SimulatorState.ledgerChain.length; i++) {
        const block = SimulatorState.ledgerChain[i];
        
        // 1. Recalculate block's own hash
        const computedHash = await calculateHash(block.index, block.timestamp, block.data, block.previousHash);
        let blockTampered = computedHash !== block.hash;

        // 2. Validate previous block pointer
        if (i > 0) {
            const prevBlock = SimulatorState.ledgerChain[i - 1];
            if (block.previousHash !== prevBlock.hash) {
                block.cascadeInvalid = true;
                isChainValid = false;
            }
        } else {
            // Genesis block previous hash check
            if (block.previousHash !== "0000000000000000000000000000000000000000000000000000000000000000") {
                blockTampered = true;
            }
        }

        block.tampered = blockTampered;
        if (blockTampered) {
            isChainValid = false;
            tamperedIndices.push(`#${block.index}`);
        }
    }

    renderLedger();
    updateZKMetrics(isChainValid);

    if (isChainValid) {
        if (successBanner) successBanner.classList.remove("hidden");
        if (errorBanner) errorBanner.classList.add("hidden");
    } else {
        if (successBanner) successBanner.classList.add("hidden");
        if (errorBanner) errorBanner.classList.remove("hidden");
        if (tamperedIndicesList) tamperedIndicesList.textContent = tamperedIndices.length > 0 ? tamperedIndices.join(", ") : "#2";
    }
}

/**
 * Tampers with Block #2 by changing its data without recalculating hashes.
 * Implements cascading downstream invalidation to all subsequent blocks.
 */
export function tamperLedgerBlock2() {
    if (SimulatorState.ledgerChain.length > 2) {
        SimulatorState.ledgerChain[2].data = "UPDATE orders SET total_amount = 25000.00 WHERE id = 2";
        SimulatorState.ledgerChain[2].tampered = true;
        
        // Cascading invalidation to all blocks after #2
        for (let i = 3; i < SimulatorState.ledgerChain.length; i++) {
            SimulatorState.ledgerChain[i].cascadeInvalid = true;
        }
        
        // Break the chain links and alert immediately
        renderLedger();
        updateZKMetrics(false);
        
        const successBanner = document.getElementById("ledger-status-success");
        const errorBanner = document.getElementById("ledger-status-error");
        const tamperedIndicesList = document.getElementById("tampered-indices-list");
        
        if (successBanner) successBanner.classList.add("hidden");
        if (errorBanner) errorBanner.classList.remove("hidden");
        if (tamperedIndicesList) tamperedIndicesList.textContent = "#2 (and downstream blocks)";

        showToast("⚠️ Malicious tampering injected into Block #2. Cascading downstream hash invalidation triggered.");
    }
}

/**
 * Sequentially recalculates SHA-256 digests and repairs ledger chain integrity
 */
export async function repairAndRecalculateLedger() {
    writeConsoleLine("[LEDGER] Initiating sequential SHA-256 cryptographic recalculation & repair...", "system");
    
    // Find first invalid or tampered block
    let startIndex = 0;
    for (let i = 0; i < SimulatorState.ledgerChain.length; i++) {
        if (SimulatorState.ledgerChain[i].tampered || SimulatorState.ledgerChain[i].cascadeInvalid) {
            startIndex = i;
            break;
        }
    }

    // Sequentially recalculate from startIndex forward
    for (let i = startIndex; i < SimulatorState.ledgerChain.length; i++) {
        const block = SimulatorState.ledgerChain[i];
        if (i > 0) {
            block.previousHash = SimulatorState.ledgerChain[i - 1].hash;
        }
        block.hash = await calculateHash(block.index, block.timestamp, block.data, block.previousHash);
        block.tampered = false;
        block.cascadeInvalid = false;
        block.repaired = true;

        renderLedger();
        await delay(200); // Visual sequential recalculation progression
    }

    const successBanner = document.getElementById("ledger-status-success");
    const errorBanner = document.getElementById("ledger-status-error");
    if (successBanner) successBanner.classList.remove("hidden");
    if (errorBanner) errorBanner.classList.add("hidden");

    updateZKMetrics(true);
    writeConsoleLine("[LEDGER] Cryptographic chain repaired. 100% SHA-256 integrity verified across all blocks.", "system");
    showToast("⚡ Cryptographic Ledger repaired! All hashes re-chained and sealed.");
}

// ==========================================
// 5. Terminal Printing & Helper Functions
// ==========================================

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export function getTerminal() {
    return document.getElementById("terminal-container");
}

export function writeConsoleLine(text, type = "system") {
    const terminal = getTerminal();
    if (!terminal) return;

    const line = document.createElement("div");
    line.className = `console-line ${type}`;

    if (type === "user") {
        line.innerHTML = `<span class="prompt-symbol">$</span>${escapeHtml(text)}`;
    } else if (type === "react-thought") {
        line.innerHTML = `<span style="color: #cbd5e1; font-weight: 600;">[Thought]</span> ${escapeHtml(text)}`;
    } else if (type === "react-action") {
        line.innerHTML = `<span style="color: #06b6d4; font-weight: 600;">[Action]</span> ${escapeHtml(text)}`;
    } else if (type === "react-input") {
        line.innerHTML = `<span style="color: #cbd5e1; font-weight: 500;">[Arguments]</span> <span style="color: #94a3b8;">${escapeHtml(text)}</span>`;
    } else if (type === "react-observation") {
        line.innerHTML = `<span style="color: #a78bfa; font-weight: 600;">[Observation]</span> ${escapeHtml(text)}`;
    } else if (type === "react-answer") {
        line.innerHTML = `<span style="color: #10b981; font-weight: 700;">[Final Answer]</span> <span style="color: #f8fafc; font-weight: 500;">${escapeHtml(text)}</span>`;
    } else {
        line.textContent = text;
    }

    terminal.appendChild(line);
    terminal.scrollTop = terminal.scrollHeight;
}

export function escapeHtml(str) {
    return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

// Toast notification helper
export function showToast(message) {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = "toast";
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(10px)";
        toast.style.transition = "all 0.3s";
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ==========================================
// 6. ReAct Reasoning Workflows (R3)
// ==========================================

export const Workflows = {
    // Scenario 1: Invoice Anomaly Detection & Ledger Rebalancing
    audit: [
        { type: "user", text: "audit_anomalies --policy='High Value Policy' --fiscal_year=2026" },
        { type: "system", text: "Kernel: Initiating multi-model query context loop (Latency: 11.2ms)..." },
        { type: "react-thought", text: "Spawning Financial Compliance Subagent. Goal: identify high-value unapproved transactions and compute ledger rebalancing diffs." },
        { type: "react-action", text: "execute_sql" },
        { type: "react-input", text: `{"query": "SELECT o.id, u.name as customer, o.total_amount, o.status FROM orders o JOIN users u ON o.user_id = u.id"}` },
        { type: "react-observation", text: `Result: [{"id":1,"customer":"Alice","total_amount":250.0,"status":"approved"},{"id":2,"customer":"Bob","total_amount":1250.0,"status":"pending"},{"id":3,"customer":"Charlie","total_amount":99.99,"status":"approved"}]` },
        { type: "react-thought", text: "Order #2 (Bob, $1250.00) exceeds the standard high-value threshold of $500.00. Querying Qdrant vector index for corporate CFO directives." },
        { type: "react-action", text: "node_vector_search" },
        { type: "react-input", text: `{"collection": "compliance_policies", "query_text": "high value transaction limit waiver"}` },
        { type: "react-observation", text: `Vector Match: 'CFO Directive 2026-B: Unapproved orders >$500 must hold in Suspense Acc 2040 and withhold Accounts Payable Acc 1010 until authorized.'` },
        { type: "react-thought", text: "Computing accounting rebalance diff: AP Acc 1010 (-$1,250.00), Suspense Acc 2040 (+$1,250.00). Compiling Generative Diff Table & Control Room." },
        { type: "react-answer", text: "Audit complete. Flagged 1 high-value anomaly: Order #2 ($1,250.00). Sandboxed Ephemeral Rebalance Diff Table rendered." }
    ],

    // Scenario 2: Automated Inventory Stockout Mitigation & Purchase Order Dispatch
    inventory_stockout: [
        { type: "user", text: "check_inventory_health --target_sku='Quantum Processor v1' --auto_mitigate=true" },
        { type: "system", text: "Kernel: Running inventory projection engine across supply chain graph (Latency: 9.8ms)..." },
        { type: "react-thought", text: "Spawning Supply Chain Sentinel Agent. Inspecting stock levels for 'Quantum Processor v1'." },
        { type: "react-action", text: "execute_sql" },
        { type: "react-input", text: `{"query": "SELECT id, name, stock_quantity, threshold, price FROM products WHERE name = 'Quantum Processor v1'"}` },
        { type: "react-observation", text: `Result: [{"id":3, "name":"Quantum Processor v1", "stock_quantity":2, "threshold":10, "price":1250.00}]` },
        { type: "react-thought", text: "CRITICAL STOCKOUT RISK: Stock quantity (2 units) is severely below reorder threshold (10 units). Projected burndown reaches 0 in 18 hours." },
        { type: "react-action", text: "graph_traverse" },
        { type: "react-input", text: `{"cypher": "MATCH (p:Product {name: 'Quantum Processor v1'})-[:SUPPLIED_BY]->(s:Supplier) RETURN s.name, s.quote_per_unit, s.lead_days, s.sla_rating"}` },
        { type: "react-observation", text: `Result: Apex Micro ($1120/ea, 3 days, 99.4% SLA), Quantum Dynamics ($1195/ea, 2 days, 98.8% SLA), Nova Foundry ($1240/ea, 7 days, 94.1% SLA)` },
        { type: "react-thought", text: "Optimal mitigation: Dispatch Purchase Order to Apex Microelectronics for 50 units ($56,000.00). Generating Burndown SVG Chart & PO Dispatch Widget." },
        { type: "react-answer", text: "Inventory mitigation active. Projected stockout prevented. Sandboxed PO Dispatch Widget and Burndown Chart rendered." }
    ],

    // Scenario 3: Autonomous SQL Querying & Financial Report Synthesis
    sql_financial: [
        { type: "user", text: "synthesize_financial_kpis --period='Q2-2026' --group_by='department'" },
        { type: "system", text: "Kernel: Ingesting financial ledgers across SQLite and Neo4j (Latency: 12.1ms)..." },
        { type: "react-thought", text: "Spawning Executive BI Synthesis Subagent. Formulating multi-table recursive aggregation." },
        { type: "react-action", text: "execute_sql" },
        { type: "react-input", text: `{"query": "SELECT strftime('%Y-%m', created_at) as month, SUM(total_amount) as gross_revenue, COUNT(id) as orders FROM orders GROUP BY month ORDER BY month DESC"}` },
        { type: "react-observation", text: `Result: [{"month":"2026-06", "gross_revenue":4250000.00, "orders":1420}, {"month":"2026-05", "gross_revenue":3890000.00, "orders":1280}]` },
        { type: "react-thought", text: "Synthesizing executive metrics: Gross ARR $4.25M (+9.2% MoM), EBITDA Margin 34.2%, Net Cash Burn $42.1k/mo. Formulating dynamic multi-series breakdown." },
        { type: "react-action", text: "vector_search" },
        { type: "react-input", text: `{"query_text": "Q2 board revenue target guidance"}` },
        { type: "react-observation", text: `Result: "Target ARR for Q2 was $4.0M. Actual results exceed targets by +6.25%."` },
        { type: "react-thought", text: "Compiling Dynamic Financial Dashboard with interactive KPI tiles and Revenue vs Expense SVG breakdown." },
        { type: "react-answer", text: "Executive Financial Synthesis complete. ARR: $4.25M. Dynamic Ephemeral Financial Dashboard rendered." }
    ],

    // Scenario 4: Role-Based Access Control (RBAC) Security Quarantine
    rbac_quarantine: [
        { type: "user", text: "security_audit --inspect_token='Token#usr_c789' --source_ip='198.51.100.42'" },
        { type: "system", text: "Kernel: Intercepting incoming API token via Security Sentinel (Latency: 8.7ms)..." },
        { type: "react-thought", text: "Spawning Security Sentinel Arbiter. Evaluating Token#usr_c789 against RBAC policy graph." },
        { type: "react-action", text: "graph_traverse" },
        { type: "react-input", text: `{"cypher": "MATCH (u:User {token: 'Token#usr_c789'})-[:HAS_ROLE]->(r:Role)-[:CAN_ACCESS]->(res:Resource) RETURN u.name, r.name, res.name, res.security_clearance"}` },
        { type: "react-observation", text: `Result: User 'Contractor_Ext', Role 'READ_ONLY_ANALYST', Target 'payroll_executive_ledger', Required 'Level 4 Clearance'` },
        { type: "react-thought", text: "CRITICAL PRIVILEGE ESCALATION VIOLATION: User 'Contractor_Ext' attempted SCHEMA_DUMP on 'payroll_executive_ledger' with Level 1 clearance." },
        { type: "react-action", text: "execute_security_quarantine" },
        { type: "react-input", text: `{"action": "QUARANTINE_TOKEN", "ip": "198.51.100.42", "token": "Token#usr_c789"}` },
        { type: "react-observation", text: `Result: Session quarantined. IP 198.51.100.42 blacklisted in edge firewall.` },
        { type: "react-thought", text: "Compiling Sandboxed Security Incident Quarantine Room with token permission diff table and one-click firewall enforcement." },
        { type: "react-answer", text: "Security Incident contained. Token quarantined. Sandboxed Security Incident Dashboard rendered." }
    ],
    
    // Saga Procure-to-Pay Workflow
    saga: (productName, quantity, total, isCompliant) => {
        const list = [
            { type: "user", text: `run_saga_procure_to_pay --product="${productName}" --qty=${quantity}` },
            { type: "system", text: `Saga: Initiating distributed transaction chain for total outlay $${total}...` },
            { type: "react-thought", text: `Spawning Saga Coordinator. Step 0: Check catalog inventory for item '${productName}'.` },
            { type: "react-action", text: "execute_sql" },
            { type: "react-input", text: `{"query": "SELECT stock_quantity, price FROM products WHERE name = '${productName}'"}` }
        ];

        const matchProduct = SimulatorState.products.find(p => p.name === productName);
        const stockQty = matchProduct ? matchProduct.stock_quantity : 15;
        const priceVal = matchProduct ? matchProduct.price : 499.50;

        list.push({ type: "react-observation", text: `Result: [{"stock_quantity": ${stockQty}, "price": ${priceVal}}]` });

        list.push(
            { type: "react-thought", text: `Stock is sufficient. Step 1: Allocate inventory (-${quantity} units).` },
            { type: "react-action", text: "execute_sql" },
            { type: "react-input", text: `{"query": "UPDATE products SET stock_quantity = stock_quantity - ${quantity} WHERE name = '${productName}'"}` },
            { type: "react-observation", text: `Result: {"status": "success"}` },
            { type: "react-thought", text: `Stock allocated. Step 2: Authorize payment of $${total}. Checking compliance bounds.` },
            { type: "react-action", text: "vector_search" },
            { type: "react-input", text: `{"query_text": "payment approval limits"}` },
            { type: "react-observation", text: `Result: "Financial Policy: Customer checkout limit is $500.00 per transaction without secondary validation."` }
        );

        if (isCompliant) {
            list.push(
                { type: "react-thought", text: `Transaction total $${total} is under $500.00. Payment authorized. Step 3: Write invoice record.` },
                { type: "react-action", text: "execute_sql" },
                { type: "react-input", text: `{"query": "INSERT INTO invoices (amount, status) VALUES (${total}, 'paid')"}` },
                { type: "react-observation", text: `Result: {"status": "success"}` },
                { type: "react-answer", text: `Saga Completed successfully. Status: COMPLETED. Stock deducted, payment authorized, and invoice written.` }
            );
        } else {
            list.push(
                { type: "react-thought", text: `WARNING: Transaction total $${total} exceeds $500.00. Payment authorization DENIED. Initiating backward compensating rollback.` },
                { type: "react-action", text: "execute_sql" },
                { type: "react-input", text: `{"query": "UPDATE products SET stock_quantity = stock_quantity + ${quantity} WHERE name = '${productName}'"}` },
                { type: "react-observation", text: `Result: {"status": "success"}` },
                { type: "react-answer", text: `Saga rolled back and compensated. Status: COMPENSATED. Inventory restored (+${quantity} units). Database charges voided.` }
            );
        }
        return list;
    }
};

/**
 * Handles running the operational workflow traces
 */
export async function runWorkflow(workflowName, extraParams = {}) {
    if (SimulatorState.isProcessing) return;
    
    SimulatorState.isProcessing = true;
    SimulatorState.activeScenario = workflowName;
    toggleTab("ui");

    // Hide placeholders and show UI container
    const placeholder = document.getElementById("ephemeral-placeholder");
    const container = document.getElementById("ephemeral-ui-container");
    if (placeholder) placeholder.classList.add("hidden");
    if (container) container.classList.remove("hidden");

    // Render loading status
    if (container) {
        container.innerHTML = `
            <div class="ephemeral-placeholder">
                <span class="placeholder-icon animate-spin">🌀</span>
                <p>Autonomous Agent Kernel is executing '${workflowName}'... Streaming ReAct reasoning traces to the console.</p>
            </div>
        `;
    }

    // Clear terminal and print welcome lines
    const terminal = getTerminal();
    if (terminal) terminal.innerHTML = "";
    writeConsoleLine("[SYSTEM] OmniGate Agent Kernel Version 2.4.0 active.", "system");
    writeConsoleLine("[SYSTEM] Multi-Model Link (SQLite + Neo4j + Qdrant) ready. Latency: 11.4ms.", "system");

    let steps = [];
    if (workflowName === "audit") {
        steps = Workflows.audit;
    } else if (workflowName === "inventory_stockout") {
        steps = Workflows.inventory_stockout;
    } else if (workflowName === "sql_financial") {
        steps = Workflows.sql_financial;
    } else if (workflowName === "rbac_quarantine") {
        steps = Workflows.rbac_quarantine;
    } else if (workflowName === "saga") {
        const prod = extraParams.product || "Ergonomic Chair";
        const qty = extraParams.quantity || 1;
        const matchProduct = SimulatorState.products.find(p => p.name === prod);
        const price = matchProduct ? matchProduct.price : 499.50;
        const total = (qty * price).toFixed(2);
        const isCompliant = total <= 500.00;
        steps = Workflows.saga(prod, qty, total, isCompliant);
    }

    for (let i = 0; i < steps.length; i++) {
        await delay(250); // 250ms delay between steps for snappy responsiveness
        writeConsoleLine(steps[i].text, steps[i].type);
    }

    SimulatorState.isProcessing = false;
    
    // Render the corresponding Generative Ephemeral UI Dashboard
    if (workflowName === "audit") {
        renderAuditDashboard();
    } else if (workflowName === "inventory_stockout") {
        renderStockoutDashboard();
    } else if (workflowName === "sql_financial") {
        renderFinancialDashboard();
    } else if (workflowName === "rbac_quarantine") {
        renderRBACDashboard();
    } else if (workflowName === "saga") {
        const prod = extraParams.product || "Ergonomic Chair";
        const qty = extraParams.quantity || 1;
        const matchProduct = SimulatorState.products.find(p => p.name === prod);
        const price = matchProduct ? matchProduct.price : 499.50;
        const total = qty * price;
        const isCompliant = total <= 500.00;
        
        if (isCompliant) {
            if (matchProduct) matchProduct.stock_quantity -= qty;
            await appendLedgerBlock(`INSERT INTO invoices (amount, status) VALUES (${total.toFixed(2)}, 'paid')`);
        }
        
        renderSagaDashboard(prod, qty, total, isCompliant);
    }

    // Refresh payload tab
    updatePayloadTab();
}

// ==========================================
// 7. Generative Ephemeral UI Dashboards (R3)
// ==========================================

// Dashboard 1: Invoice Anomaly & Ledger Rebalancing Diff Table
export function renderAuditDashboard() {
    const container = document.getElementById("ephemeral-ui-container");
    if (!container) return;

    const anomalies = SimulatorState.orders.filter(o => o.total_amount > 500.00);
    const compliant = SimulatorState.orders.filter(o => o.total_amount <= 500.00);

    container.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 1.25rem;">
            <!-- Header -->
            <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(13,11,33,0.6); padding: 1rem; border-radius: 12px; border: 1px solid rgba(244,63,94,0.25); box-shadow: 0 4px 20px rgba(0,0,0,0.2);">
                <div>
                    <h4 style="color: var(--accent-rose); font-weight: 700; font-size: 1.1rem; margin-bottom: 0.15rem;">Scenario 1: Risk Assessment & Ledger Rebalance</h4>
                    <p style="font-size: 0.75rem; color: var(--text-secondary); margin: 0;">Generative UX synthesized from SQLite Orders & Qdrant Policy Directives</p>
                </div>
                <span class="status-indicator" style="background: rgba(244,63,94,0.1); border: 1px solid rgba(244,63,94,0.3); color: var(--accent-rose); padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 700; font-family: var(--font-mono);">
                    <span class="pulse-dot pulse-tampered"></span>
                    <span>${anomalies.filter(a => a.status === 'pending').length} Anomalies Pending</span>
                </span>
            </div>

            <!-- Vector Context Partition -->
            <div style="background: rgba(4,3,8,0.5); padding: 1rem; border-radius: 12px; border: 1px solid var(--border-glass); font-size: 0.75rem;">
                <span style="color: var(--accent-cyan); font-weight: 700; font-family: var(--font-mono); font-size: 0.65rem; text-transform: uppercase; display: block; margin-bottom: 0.35rem;">📁 Vector Context: Qdrant Policy Collection</span>
                <p style="color: var(--text-secondary); font-style: italic; margin: 0;">"CFO Directive 2026-B: All purchases exceeding $500 require executive board approval or written CFO waiver. Unapproved high-value orders must be held in Suspense Acc 2040 with zero direct AP disbursement."</p>
            </div>

            <!-- Quick Stats -->
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
                <div style="background: rgba(4,3,8,0.5); padding: 1rem; border-radius: 12px; border: 1px solid rgba(244,63,94,0.2);">
                    <span style="font-size: 0.65rem; color: var(--text-muted); text-transform: uppercase; display: block;">Total Anomaly Volume</span>
                    <span style="font-size: 1.35rem; font-weight: 800; color: var(--accent-rose); font-family: var(--font-mono);">$${anomalies.reduce((acc, o) => acc + o.total_amount, 0).toFixed(2)}</span>
                </div>
                <div style="background: rgba(4,3,8,0.5); padding: 1rem; border-radius: 12px; border: 1px solid rgba(16,185,129,0.2);">
                    <span style="font-size: 0.65rem; color: var(--text-muted); text-transform: uppercase; display: block;">Compliant Orders</span>
                    <span style="font-size: 1.35rem; font-weight: 800; color: var(--accent-emerald); font-family: var(--font-mono);">${compliant.length} Verified</span>
                </div>
                <div style="background: rgba(4,3,8,0.5); padding: 1rem; border-radius: 12px; border: 1px solid var(--border-glass);">
                    <span style="font-size: 0.65rem; color: var(--text-muted); text-transform: uppercase; display: block;">Compliance Bound</span>
                    <span style="font-size: 1.35rem; font-weight: 800; color: var(--accent-violet); font-family: var(--font-mono);">$500.00</span>
                </div>
            </div>

            <!-- Ledger Rebalancing Diff Table -->
            <div style="background: rgba(4,3,8,0.5); border: 1px solid var(--border-glass); border-radius: 12px; overflow: hidden;">
                <div style="background: rgba(13,18,29,0.7); padding: 0.75rem 1rem; border-bottom: 1px solid var(--border-glass); display: flex; justify-content: space-between; align-items: center;">
                    <h5 style="color: var(--text-primary); font-size: 0.85rem; margin: 0; font-weight: 700;">Accounting Ledger Rebalance Diff Table</h5>
                    <button class="btn btn-sm btn-primary" onclick="window.commitLedgerRebalance()">
                        <span>⚡ Commit Ledger Rebalance</span>
                    </button>
                </div>
                <div class="diff-table-wrapper">
                    <table class="diff-table">
                        <thead>
                            <tr>
                                <th>General Ledger Account</th>
                                <th>Pre-Rebalance</th>
                                <th>Adjustment</th>
                                <th>Post-Rebalance</th>
                                <th>Audit Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Accounts Payable (Acc 1010)</td>
                                <td>$45,200.00</td>
                                <td class="diff-delta-neg">-$1,250.00</td>
                                <td>$43,950.00</td>
                                <td><span class="badge-emerald" style="padding: 0.15rem 0.45rem; border-radius: 4px; font-size: 0.65rem;">Balanced</span></td>
                            </tr>
                            <tr>
                                <td>Suspense Holding (Acc 2040)</td>
                                <td>$0.00</td>
                                <td class="diff-delta-pos">+$1,250.00</td>
                                <td>$1,250.00</td>
                                <td><span class="badge-amber" style="padding: 0.15rem 0.45rem; border-radius: 4px; font-size: 0.65rem;">Quarantined</span></td>
                            </tr>
                            <tr>
                                <td>Operating Expense (Acc 5010)</td>
                                <td>$12,400.00</td>
                                <td>$0.00</td>
                                <td>$12,400.00</td>
                                <td><span class="badge-emerald" style="padding: 0.15rem 0.45rem; border-radius: 4px; font-size: 0.65rem;">Nominal</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Anomalies Action List -->
            <div style="background: rgba(4,3,8,0.5); border: 1px solid var(--border-glass); border-radius: 12px; overflow: hidden;">
                <div style="background: rgba(13,11,33,0.4); padding: 0.75rem 1rem; border-bottom: 1px solid var(--border-glass);">
                    <h5 style="color: var(--text-primary); font-size: 0.85rem; margin: 0; font-weight: 600;">Critical Pending Anomalies</h5>
                </div>
                <div style="padding: 1rem; display: flex; flex-direction: column; gap: 0.75rem;">
                    ${anomalies.map(a => `
                        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.03); padding-bottom: 0.75rem;">
                            <div>
                                <h6 style="color: var(--text-primary); font-size: 0.85rem; margin: 0;">Order #00${a.id} — Customer: ${escapeHtml(a.customer_name)}</h6>
                                <p style="font-size: 0.75rem; color: var(--text-muted); margin: 0.15rem 0 0;">Created at ${a.created_at}</p>
                            </div>
                            <div style="display: flex; align-items: center; gap: 1rem;">
                                <span style="font-size: 0.95rem; font-weight: 800; color: var(--accent-rose); font-family: var(--font-mono);">$${a.total_amount.toFixed(2)}</span>
                                ${a.status === 'pending' ? `
                                    <button class="btn btn-sm" id="btn-approve-waiver-${a.id}" style="background: var(--accent-rose); color: #fff; font-size: 0.75rem;" onclick="window.approveWaiver(${a.id})">Authorize CFO Waiver</button>
                                ` : `
                                    <span style="font-size: 0.75rem; color: var(--accent-emerald); font-weight: 600; border: 1px solid rgba(16,185,129,0.3); padding: 0.2rem 0.5rem; border-radius: 4px; background: rgba(16,185,129,0.05);">Approved</span>
                                `}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
}

// Dashboard 2: Automated Stockout Mitigation & Purchase Order Dispatch
export function renderStockoutDashboard() {
    const container = document.getElementById("ephemeral-ui-container");
    if (!container) return;

    container.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 1.25rem;">
            <!-- Header -->
            <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(13,11,33,0.6); padding: 1rem; border-radius: 12px; border: 1px solid rgba(245,158,11,0.3); box-shadow: 0 4px 20px rgba(0,0,0,0.2);">
                <div>
                    <h4 style="color: var(--accent-amber); font-weight: 700; font-size: 1.1rem; margin-bottom: 0.15rem;">Scenario 2: Stockout Mitigation & PO Dispatch</h4>
                    <p style="font-size: 0.75rem; color: var(--text-secondary); margin: 0;">Autonomous inventory forecasting & multi-supplier quotation matrix</p>
                </div>
                <span class="status-indicator" style="background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.3); color: var(--accent-amber); padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 700; font-family: var(--font-mono);">
                    ⚠️ Critical Threshold Breached
                </span>
            </div>

            <!-- Burndown SVG Chart -->
            <div style="background: rgba(4,3,8,0.5); border: 1px solid var(--border-glass); border-radius: 12px; padding: 1.25rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                    <span style="font-size: 0.75rem; font-weight: 700; color: var(--text-primary); text-transform: uppercase; font-family: var(--font-mono);">Inventory Burndown & Replenishment Curve</span>
                    <span style="font-size: 0.7rem; color: var(--accent-emerald); font-weight: 600;">Replenishment Target: +50 units</span>
                </div>
                <svg viewBox="0 0 500 120" style="width: 100%; height: 120px; background: rgba(0,0,0,0.3); border-radius: 8px; border: 1px solid var(--border-glass);">
                    <!-- Grid Lines -->
                    <line x1="40" y1="20" x2="480" y2="20" stroke="rgba(255,255,255,0.05)" />
                    <line x1="40" y1="60" x2="480" y2="60" stroke="rgba(255,255,255,0.05)" />
                    <line x1="40" y1="100" x2="480" y2="100" stroke="rgba(255,255,255,0.05)" />
                    
                    <!-- Threshold Line (Amber) -->
                    <line x1="40" y1="75" x2="480" y2="75" stroke="var(--accent-amber)" stroke-dasharray="4" stroke-width="1.5" />
                    <text x="45" y="70" fill="var(--accent-amber)" font-size="9" font-family="monospace">Safety Threshold: 10 units</text>

                    <!-- Burndown Curve (Rose -> Emerald recovery) -->
                    <path d="M 40 40 Q 120 70, 200 98 T 280 105 L 340 30 L 480 25" fill="none" stroke="url(#stockoutGradient)" stroke-width="3" />
                    
                    <defs>
                        <linearGradient id="stockoutGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" stop-color="var(--accent-rose)" />
                            <stop offset="55%" stop-color="var(--accent-amber)" />
                            <stop offset="70%" stop-color="var(--accent-emerald)" />
                            <stop offset="100%" stop-color="var(--accent-cyan)" />
                        </linearGradient>
                    </defs>

                    <!-- Point Markers -->
                    <circle cx="40" cy="40" r="4" fill="var(--accent-rose)" />
                    <circle cx="200" cy="98" r="4" fill="var(--accent-amber)" />
                    <circle cx="340" cy="30" r="5" fill="var(--accent-emerald)" />
                </svg>
            </div>

            <!-- Supplier Quotation Matrix -->
            <div style="background: rgba(4,3,8,0.5); border: 1px solid var(--border-glass); border-radius: 12px; overflow: hidden;">
                <div style="background: rgba(13,18,29,0.7); padding: 0.75rem 1rem; border-bottom: 1px solid var(--border-glass); display: flex; justify-content: space-between; align-items: center;">
                    <h5 style="color: var(--text-primary); font-size: 0.85rem; margin: 0; font-weight: 700;">Supplier Procurement Matrix</h5>
                    <button class="btn btn-sm btn-primary" onclick="window.dispatchPurchaseOrder()">
                        <span>⚡ Authorize & Dispatch Purchase Order</span>
                    </button>
                </div>
                <div class="diff-table-wrapper">
                    <table class="diff-table">
                        <thead>
                            <tr>
                                <th>Supplier Name</th>
                                <th>Unit Price</th>
                                <th>Lead Time</th>
                                <th>Allocation</th>
                                <th>SLA Rating</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style="background: rgba(16,185,129,0.06);">
                                <td><strong>Apex Microelectronics (Optimal)</strong></td>
                                <td class="text-emerald font-mono">$1,120.00</td>
                                <td>3 Days</td>
                                <td>50 Units</td>
                                <td class="text-emerald font-mono">99.4%</td>
                                <td><span class="badge-emerald" style="padding: 0.15rem 0.45rem; border-radius: 4px; font-size: 0.65rem;">Selected</span></td>
                            </tr>
                            <tr>
                                <td>Quantum Dynamics Corp</td>
                                <td class="font-mono">$1,195.00</td>
                                <td>2 Days</td>
                                <td>100 Units</td>
                                <td class="font-mono">98.8%</td>
                                <td><span class="badge-cyan" style="padding: 0.15rem 0.45rem; border-radius: 4px; font-size: 0.65rem;">Standby</span></td>
                            </tr>
                            <tr>
                                <td>Nova Foundry Direct</td>
                                <td class="font-mono">$1,240.00</td>
                                <td>7 Days</td>
                                <td>25 Units</td>
                                <td class="font-mono">94.1%</td>
                                <td><span style="color: var(--text-muted); font-size: 0.65rem;">Alternative</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
}

// Dashboard 3: Autonomous SQL Querying & Financial Report Synthesis
export function renderFinancialDashboard() {
    const container = document.getElementById("ephemeral-ui-container");
    if (!container) return;

    container.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 1.25rem;">
            <!-- Header -->
            <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(13,11,33,0.6); padding: 1rem; border-radius: 12px; border: 1px solid rgba(99,102,241,0.3); box-shadow: 0 4px 20px rgba(0,0,0,0.2);">
                <div>
                    <h4 style="color: var(--accent-violet); font-weight: 700; font-size: 1.1rem; margin-bottom: 0.15rem;">Scenario 3: Autonomous SQL & Financial Synthesis</h4>
                    <p style="font-size: 0.75rem; color: var(--text-secondary); margin: 0;">Multi-table recursive aggregations & executive performance KPIs</p>
                </div>
                <span style="font-size: 0.75rem; color: var(--accent-emerald); font-weight: 700; font-family: var(--font-mono); border: 1px solid rgba(16,185,129,0.3); padding: 0.25rem 0.75rem; border-radius: 20px; background: rgba(16,185,129,0.05);">
                    Q2 Targets Exceeded (+6.25%)
                </span>
            </div>

            <!-- Executive KPI Tiles -->
            <div class="kpi-grid">
                <div class="kpi-card">
                    <span class="kpi-title">Gross ARR</span>
                    <span class="kpi-val text-emerald">$4.25M</span>
                    <span class="kpi-delta text-emerald">+9.2% MoM</span>
                </div>
                <div class="kpi-card">
                    <span class="kpi-title">EBITDA Margin</span>
                    <span class="kpi-val text-cyan">34.2%</span>
                    <span class="kpi-delta text-cyan">+2.8% vs Target</span>
                </div>
                <div class="kpi-card">
                    <span class="kpi-title">Net Cash Burn</span>
                    <span class="kpi-val text-amber">$42.1k/mo</span>
                    <span class="kpi-delta text-emerald">-18.4% YoY</span>
                </div>
                <div class="kpi-card">
                    <span class="kpi-title">Loop Latency</span>
                    <span class="kpi-val text-violet">11.8ms</span>
                    <span class="kpi-delta text-violet">1 Local Hop</span>
                </div>
            </div>

            <!-- Dynamic Multi-Series SVG Financial Chart -->
            <div style="background: rgba(4,3,8,0.5); border: 1px solid var(--border-glass); border-radius: 12px; padding: 1.25rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                    <span style="font-size: 0.75rem; font-weight: 700; color: var(--text-primary); text-transform: uppercase; font-family: var(--font-mono);">Monthly Revenue vs Operating Outlay (FY2026)</span>
                    <div style="display: flex; gap: 1rem; font-size: 0.7rem;">
                        <span style="color: var(--accent-emerald);">● Revenue</span>
                        <span style="color: var(--accent-rose);">● Operating Outlay</span>
                    </div>
                </div>
                <svg viewBox="0 0 500 130" style="width: 100%; height: 130px; background: rgba(0,0,0,0.3); border-radius: 8px; border: 1px solid var(--border-glass);">
                    <!-- Grid Lines -->
                    <line x1="40" y1="30" x2="480" y2="30" stroke="rgba(255,255,255,0.05)" />
                    <line x1="40" y1="70" x2="480" y2="70" stroke="rgba(255,255,255,0.05)" />
                    <line x1="40" y1="110" x2="480" y2="110" stroke="rgba(255,255,255,0.05)" />
                    
                    <!-- Bars: Jan to Jun -->
                    <!-- Jan -->
                    <rect x="60" y="55" width="18" height="55" fill="var(--accent-emerald)" opacity="0.85" rx="3" />
                    <rect x="80" y="75" width="18" height="35" fill="var(--accent-rose)" opacity="0.85" rx="3" />
                    <!-- Feb -->
                    <rect x="130" y="50" width="18" height="60" fill="var(--accent-emerald)" opacity="0.85" rx="3" />
                    <rect x="150" y="70" width="18" height="40" fill="var(--accent-rose)" opacity="0.85" rx="3" />
                    <!-- Mar -->
                    <rect x="200" y="45" width="18" height="65" fill="var(--accent-emerald)" opacity="0.85" rx="3" />
                    <rect x="220" y="68" width="18" height="42" fill="var(--accent-rose)" opacity="0.85" rx="3" />
                    <!-- Apr -->
                    <rect x="270" y="38" width="18" height="72" fill="var(--accent-emerald)" opacity="0.85" rx="3" />
                    <rect x="290" y="65" width="18" height="45" fill="var(--accent-rose)" opacity="0.85" rx="3" />
                    <!-- May -->
                    <rect x="340" y="32" width="18" height="78" fill="var(--accent-emerald)" opacity="0.85" rx="3" />
                    <rect x="360" y="62" width="18" height="48" fill="var(--accent-rose)" opacity="0.85" rx="3" />
                    <!-- Jun -->
                    <rect x="410" y="24" width="18" height="86" fill="var(--accent-emerald)" opacity="0.85" rx="3" />
                    <rect x="430" y="58" width="18" height="52" fill="var(--accent-rose)" opacity="0.85" rx="3" />

                    <!-- Month Labels -->
                    <text x="73" y="122" fill="#64748b" font-size="9" font-family="monospace">Jan</text>
                    <text x="143" y="122" fill="#64748b" font-size="9" font-family="monospace">Feb</text>
                    <text x="213" y="122" fill="#64748b" font-size="9" font-family="monospace">Mar</text>
                    <text x="283" y="122" fill="#64748b" font-size="9" font-family="monospace">Apr</text>
                    <text x="353" y="122" fill="#64748b" font-size="9" font-family="monospace">May</text>
                    <text x="423" y="122" fill="#64748b" font-size="9" font-family="monospace">Jun</text>
                </svg>
            </div>
        </div>
    `;
}

// Dashboard 4: RBAC Security Quarantine Room
export function renderRBACDashboard() {
    const container = document.getElementById("ephemeral-ui-container");
    if (!container) return;

    container.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 1.25rem;">
            <!-- Crimson Alert Banner -->
            <div style="background: rgba(244,63,94,0.12); border: 1px solid var(--accent-rose); border-radius: 12px; padding: 1.25rem; box-shadow: 0 0 25px rgba(244,63,94,0.3); animation: pulse-tampered 1.5s infinite ease-in-out;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="color: var(--accent-rose); font-weight: 800; font-size: 1.15rem; margin-bottom: 0.25rem;">🚨 Security Incident: Privilege Boundary Violation</h4>
                        <p style="font-size: 0.75rem; color: #cbd5e1; margin: 0;">Unauthorized schema traversal intercepted from external endpoint <code class="font-mono text-rose">198.51.100.42</code></p>
                    </div>
                    <span class="badge-rose" style="padding: 0.35rem 0.85rem; border-radius: 20px; font-weight: 800; font-size: 0.75rem;">SESSION QUARANTINED</span>
                </div>
            </div>

            <!-- Permission Scope Diff Table -->
            <div style="background: rgba(4,3,8,0.5); border: 1px solid var(--border-glass); border-radius: 12px; overflow: hidden;">
                <div style="background: rgba(13,18,29,0.7); padding: 0.75rem 1rem; border-bottom: 1px solid var(--border-glass); display: flex; justify-content: space-between; align-items: center;">
                    <h5 style="color: var(--text-primary); font-size: 0.85rem; margin: 0; font-weight: 700;">RBAC Permission Scope Analysis</h5>
                    <button class="btn btn-sm btn-rose" onclick="window.quarantineSecurityIncident()">
                        <span>🔒 Enforce Perimeter Blacklist</span>
                    </button>
                </div>
                <div class="diff-table-wrapper">
                    <table class="diff-table">
                        <thead>
                            <tr>
                                <th>Security Attribute</th>
                                <th>Authorized Scope</th>
                                <th>Attempted Action</th>
                                <th>Violation Severity</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Target Resource</td>
                                <td>orders (Read-Only)</td>
                                <td class="diff-delta-neg">payroll_executive_ledger</td>
                                <td><span class="badge-rose" style="padding: 0.15rem 0.45rem; border-radius: 4px; font-size: 0.65rem;">CRITICAL</span></td>
                            </tr>
                            <tr>
                                <td>Mutation Directive</td>
                                <td>SELECT (Row Range)</td>
                                <td class="diff-delta-neg">SCHEMA_DUMP (Full DB)</td>
                                <td><span class="badge-rose" style="padding: 0.15rem 0.45rem; border-radius: 4px; font-size: 0.65rem;">CRITICAL</span></td>
                            </tr>
                            <tr>
                                <td>Clearance Level</td>
                                <td>Level 1 (Contractor)</td>
                                <td class="diff-delta-neg">Level 4 (CFO Clearance)</td>
                                <td><span class="badge-rose" style="padding: 0.15rem 0.45rem; border-radius: 4px; font-size: 0.65rem;">CRITICAL</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
}

// Dashboard 5: Saga Procure-to-Pay Monitor
export function renderSagaDashboard(productName, quantity, total, isCompliant) {
    const container = document.getElementById("ephemeral-ui-container");
    if (!container) return;

    container.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 1.25rem;">
            <!-- Header -->
            <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(13,11,33,0.6); padding: 1rem; border-radius: 12px; border: 1px solid ${isCompliant ? 'rgba(16,185,129,0.25)' : 'rgba(244,63,94,0.25)'}; box-shadow: 0 4px 20px rgba(0,0,0,0.2);">
                <div>
                    <h4 style="color: ${isCompliant ? 'var(--accent-emerald)' : 'var(--accent-rose)'}; font-weight: 700; font-size: 1.1rem; margin-bottom: 0.15rem;">Saga Procure-to-Pay Monitor</h4>
                    <p style="font-size: 0.75rem; color: var(--text-secondary); margin: 0;">Distributed transaction manager & compensatory action log</p>
                </div>
                <span style="font-size: 0.75rem; color: ${isCompliant ? 'var(--accent-emerald)' : 'var(--accent-rose)'}; font-weight: 700; font-family: var(--font-mono); border: 1px solid ${isCompliant ? 'rgba(16,185,129,0.3)' : 'rgba(244,63,94,0.3)'}; padding: 0.25rem 0.75rem; border-radius: 20px; background: ${isCompliant ? 'rgba(16,185,129,0.05)' : 'rgba(244,63,94,0.05)'};">
                    STATUS: ${isCompliant ? 'COMPLETED' : 'COMPENSATED'}
                </span>
            </div>

            <!-- Parameters selection panel -->
            <div style="background: rgba(4,3,8,0.5); padding: 1rem; border-radius: 12px; border: 1px solid var(--border-glass); display: flex; flex-direction: column; gap: 0.75rem;">
                <span style="font-size: 0.65rem; color: var(--text-muted); text-transform: uppercase; font-family: var(--font-mono); font-weight: 700;">🛒 Quick Purchase Configuration</span>
                <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
                    <div style="display: flex; flex-direction: column; gap: 0.25rem;">
                        <label style="font-size: 0.7rem; color: var(--text-secondary);">Select Product</label>
                        <select id="saga-product-select" style="background: var(--bg-dark-secondary); color: var(--text-primary); border: 1px solid var(--border-glass); padding: 0.35rem 0.75rem; border-radius: 6px; font-size: 0.8rem; font-family: var(--font-body);">
                            <option value="Ergonomic Chair" ${productName === 'Ergonomic Chair' ? 'selected' : ''}>Ergonomic Chair ($299.99)</option>
                            <option value="Standing Desk" ${productName === 'Standing Desk' ? 'selected' : ''}>Standing Desk ($499.50)</option>
                        </select>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 0.25rem;">
                        <label style="font-size: 0.7rem; color: var(--text-secondary);">Quantity</label>
                        <select id="saga-qty-select" style="background: var(--bg-dark-secondary); color: var(--text-primary); border: 1px solid var(--border-glass); padding: 0.35rem 0.75rem; border-radius: 6px; font-size: 0.8rem; font-family: var(--font-body);">
                            <option value="1" ${quantity === 1 ? 'selected' : ''}>1 Unit</option>
                            <option value="2" ${quantity === 2 ? 'selected' : ''}>2 Units</option>
                        </select>
                    </div>
                    <button class="btn btn-sm btn-primary" style="margin-top: auto;" onclick="window.triggerSagaSimulation()">Run Saga Workflow</button>
                </div>
            </div>

            <!-- Transaction steps logs -->
            <div style="background: rgba(4,3,8,0.5); border: 1px solid var(--border-glass); border-radius: 12px; padding: 1.25rem; display: flex; flex-direction: column; gap: 0.75rem;">
                <span style="font-size: 0.65rem; color: var(--text-muted); text-transform: uppercase; font-family: var(--font-mono); font-weight: 700; display: block; border-bottom: 1px solid rgba(255,255,255,0.03); padding-bottom: 0.5rem; margin-bottom: 0.25rem;">📝 Consensus Transactional Logs</span>
                
                <div style="display: flex; flex-direction: column; gap: 0.65rem; max-height: 180px; overflow-y: auto;">
                    <div style="display: flex; gap: 0.5rem; align-items: start; font-size: 0.75rem;">
                        <span style="color: var(--accent-emerald);">●</span>
                        <span style="font-family: var(--font-mono); color: var(--text-secondary);">Transaction #0: Draft Order #104 generated ($${total.toFixed(2)}).</span>
                    </div>
                    <div style="display: flex; gap: 0.5rem; align-items: start; font-size: 0.75rem;">
                        <span style="color: var(--accent-emerald);">●</span>
                        <span style="font-family: var(--font-mono); color: var(--text-secondary);">Transaction #1: Deducting ${quantity} unit(s) stock. Stock allocated.</span>
                    </div>
                    ${isCompliant ? `
                        <div style="display: flex; gap: 0.5rem; align-items: start; font-size: 0.75rem;">
                            <span style="color: var(--accent-emerald);">●</span>
                            <span style="font-family: var(--font-mono); color: var(--text-secondary);">Transaction #2: Payment checkout authorized ($${total.toFixed(2)} <= $500 limit).</span>
                        </div>
                        <div style="display: flex; gap: 0.5rem; align-items: start; font-size: 0.75rem;">
                            <span style="color: var(--accent-emerald);">●</span>
                            <span style="font-family: var(--font-mono); color: var(--text-secondary);">Transaction #3: Final purchase invoice generated. Saga complete.</span>
                        </div>
                    ` : `
                        <div style="display: flex; gap: 0.5rem; align-items: start; font-size: 0.75rem;">
                            <span style="color: var(--accent-rose);">●</span>
                            <span style="font-family: var(--font-mono); color: var(--accent-rose); font-weight: 600;">Transaction #2 Failure: Outlay $${total.toFixed(2)} violates compliance checkout limit ($500.00).</span>
                        </div>
                        <div style="display: flex; gap: 0.5rem; align-items: start; font-size: 0.75rem; background: rgba(245,158,11,0.05); padding: 0.25rem; border-radius: 4px;">
                            <span style="color: var(--accent-amber);">●</span>
                            <span style="font-family: var(--font-mono); color: var(--accent-amber);">Compensator #1: Voiding Payment token.</span>
                        </div>
                        <div style="display: flex; gap: 0.5rem; align-items: start; font-size: 0.75rem; background: rgba(245,158,11,0.05); padding: 0.25rem; border-radius: 4px;">
                            <span style="color: var(--accent-amber);">●</span>
                            <span style="font-family: var(--font-mono); color: var(--accent-amber);">Compensator #2: Restoring inventory stock allocations (+${quantity} units). Stock re-added.</span>
                        </div>
                        <div style="display: flex; gap: 0.5rem; align-items: start; font-size: 0.75rem;">
                            <span style="color: var(--accent-rose);">●</span>
                            <span style="font-family: var(--font-mono); color: var(--text-secondary);">Transaction Aborted. Database rollback complete. State restored.</span>
                        </div>
                    `}
                </div>
            </div>
        </div>
    `;
}

// Action Callbacks for Ephemeral Dashboards
export async function approveWaiver(orderId) {
    const order = SimulatorState.orders.find(o => o.id === orderId);
    if (!order) return;

    order.status = "approved";
    
    writeConsoleLine("");
    writeConsoleLine("[SYSTEM] Administrator authorized CFO Waiver Approval callback.", "system");
    writeConsoleLine("CFO Waiver authorized. Updating order status in the secure ledger.", "react-thought");
    writeConsoleLine("execute_sql", "react-action");
    writeConsoleLine(`{"query": "UPDATE orders SET status = 'approved' WHERE id = ${orderId}"}`, "react-input");
    writeConsoleLine(`Result: {"status": "success", "rows_affected": 1}`, "react-observation");
    
    await appendLedgerBlock(`UPDATE orders SET status = 'approved' WHERE id = ${orderId}`);
    writeConsoleLine("Waiver override committed. Cryptographic Ledger Block generated.", "react-answer");

    await verifyLedgerChain();
    renderAuditDashboard();
    updatePayloadTab();
    showToast(`✓ Order #00${orderId} CFO waiver authorized and logged to ledger.`);
}

export async function commitLedgerRebalance() {
    writeConsoleLine("");
    writeConsoleLine("[SYSTEM] Committing accounting ledger rebalancing transaction...", "system");
    writeConsoleLine("execute_sql", "react-action");
    writeConsoleLine(`{"query": "UPDATE accounts SET balance = balance - 1250.00 WHERE id = '1010_AP'; INSERT INTO accounts (id, balance) VALUES ('2040_Suspense', 1250.00);"`, "react-input");
    writeConsoleLine(`Result: {"status": "success", "rows_affected": 2}`, "react-observation");

    await appendLedgerBlock("UPDATE accounts SET balance = balance - 1250.00 WHERE id = '1010_AP'");
    await appendLedgerBlock("INSERT INTO accounts (id, balance) VALUES ('2040_Suspense', 1250.00)");
    
    writeConsoleLine("Ledger rebalancing completed. Double-entry audit chain verified.", "react-answer");
    await verifyLedgerChain();
    updatePayloadTab();
    showToast("⚡ Ledger Rebalance committed: AP (-$1,250), Suspense (+$1,250).");
}

export async function dispatchPurchaseOrder() {
    writeConsoleLine("");
    writeConsoleLine("[SYSTEM] Dispatching automated Purchase Order to Apex Microelectronics...", "system");
    writeConsoleLine("execute_po_dispatch", "react-action");
    writeConsoleLine(`{"supplier": "Apex Microelectronics", "sku": "Quantum Processor v1", "qty": 50, "total": 56000.00}`, "react-input");
    writeConsoleLine(`Result: {"status": "po_dispatched", "po_number": "PO-2026-8841", "eta_days": 3}`, "react-observation");

    await appendLedgerBlock("INSERT INTO purchase_orders (po_number, supplier, amount) VALUES ('PO-2026-8841', 'Apex Micro', 56000.00)");
    
    const prod = SimulatorState.products.find(p => p.name === "Quantum Processor v1");
    if (prod) prod.stock_quantity += 50;

    writeConsoleLine("PO-2026-8841 dispatched. Inventory burndown risk averted.", "react-answer");
    await verifyLedgerChain();
    updatePayloadTab();
    showToast("⚡ Purchase Order PO-2026-8841 dispatched to Apex Micro (+50 units).");
}

export async function quarantineSecurityIncident() {
    writeConsoleLine("");
    writeConsoleLine("[SECURITY] Enforcing perimeter firewall blacklist for IP 198.51.100.42...", "system");
    writeConsoleLine("firewall_blacklist_ip", "react-action");
    writeConsoleLine(`{"ip": "198.51.100.42", "duration": "PERMANENT", "token": "Token#usr_c789"}`, "react-input");
    writeConsoleLine(`Result: {"firewall_status": "BLOCKED", "ids_signature": "SIG-2026-PRIVILEGE"}`, "react-observation");

    await appendLedgerBlock("INSERT INTO security_audit_log (ip, action, reason) VALUES ('198.51.100.42', 'BLACKLIST', 'RBAC_VIOLATION')");
    
    writeConsoleLine("Perimeter blacklist enforced. Zero network ingress permitted for 198.51.100.42.", "react-answer");
    await verifyLedgerChain();
    updatePayloadTab();
    showToast("🔒 Perimeter blacklist active: 198.51.100.42 blocked at edge firewall.");
}

export function triggerSagaSimulation() {
    const productSelect = document.getElementById("saga-product-select");
    const qtySelect = document.getElementById("saga-qty-select");
    const product = productSelect ? productSelect.value : "Ergonomic Chair";
    const quantity = qtySelect ? parseInt(qtySelect.value) : 1;
    runWorkflow("saga", { product, quantity });
}

// ==========================================
// 8. Tab System Navigation
// ==========================================

export function toggleTab(tabId) {
    SimulatorState.activeTab = tabId;
    
    const buttons = document.querySelectorAll(".workspace-tabs .tab-btn");
    buttons.forEach(btn => {
        if (btn.getAttribute("data-tab") === tabId) {
            btn.classList.add("active");
        } else {
            btn.classList.remove("active");
        }
    });

    const tabs = ["ui", "schema", "data"];
    tabs.forEach(t => {
        const panel = document.getElementById(`tab-${t}`);
        if (panel) {
            if (t === tabId) {
                panel.classList.remove("hidden");
            } else {
                panel.classList.add("hidden");
            }
        }
    });
}

export function updatePayloadTab() {
    const dataPanel = document.querySelector(".raw-data-panel");
    if (!dataPanel) return;

    const payload = {
        status: SimulatorState.isProcessing ? "running" : "idle",
        kernel_version: "2.4.0",
        active_scenario: SimulatorState.activeScenario,
        last_mutation_timestamp: new Date().toISOString(),
        mock_sqlite_state: {
            products: SimulatorState.products,
            orders: SimulatorState.orders
        },
        cryptographic_compliance: {
            chain_length: SimulatorState.ledgerChain.length,
            is_verified: !SimulatorState.ledgerChain.some(b => b.tampered || b.cascadeInvalid)
        }
    };

    dataPanel.textContent = JSON.stringify(payload, null, 2);
}

export async function runCustomQuery(queryText) {
    if (SimulatorState.isProcessing) return;
    SimulatorState.isProcessing = true;
    toggleTab("ui");

    const placeholder = document.getElementById("ephemeral-placeholder");
    const container = document.getElementById("ephemeral-ui-container");
    if (placeholder) placeholder.classList.add("hidden");
    if (container) container.classList.remove("hidden");

    const terminal = getTerminal();
    if (terminal) terminal.innerHTML = "";
    writeConsoleLine("[SYSTEM] Executing custom user SQL query...", "system");
    writeConsoleLine(queryText, "user");

    await delay(300);

    if (queryText.trim().toLowerCase().startsWith("select")) {
        writeConsoleLine("Evaluating query semantics against local SQLite schema map...", "react-thought");
        writeConsoleLine("execute_sql", "react-action");
        writeConsoleLine(JSON.stringify({ query: queryText }), "react-input");
        await delay(250);
        writeConsoleLine("Result: Query parsed successfully. Data loaded in ephemeral view.", "react-observation");
        
        if (container) {
            container.innerHTML = `
                <div style="background: rgba(13,11,33,0.6); padding: 1.25rem; border-radius: 12px; border: 1px solid var(--border-glass);">
                    <h4 style="color: var(--accent-emerald); font-weight: 700; font-size: 1.1rem; margin-bottom: 0.5rem;">Custom SQL Output Sandbox</h4>
                    <p style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 1rem;">Dynamic interface compiled in response to customized local DB execution.</p>
                    <pre class="font-mono text-emerald" style="font-size: 0.8rem; background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 6px; overflow-x: auto;">${JSON.stringify(SimulatorState.orders, null, 2)}</pre>
                </div>
            `;
        }
        writeConsoleLine("Custom execution succeeded.", "react-answer");
    } else {
        writeConsoleLine("ERROR: Execution aborted. Sandbox requires SELECT mutations.", "react-observation");
        if (container) {
            container.innerHTML = `
                <div style="background: rgba(244,63,94,0.1); padding: 1.25rem; border-radius: 12px; border: 1px solid rgba(244,63,94,0.3);">
                    <h4 style="color: var(--accent-rose); font-weight: 700; font-size: 1.1rem; margin-bottom: 0.5rem;">Execution Denied</h4>
                    <p style="font-size: 0.85rem; color: var(--text-secondary); margin: 0;">The interactive playground requires SELECT queries to compile mock database records.</p>
                </div>
            `;
        }
    }
    
    SimulatorState.isProcessing = false;
    updatePayloadTab();
}

// ==========================================
// 9. Benchmark Hub & Developer MCP Controllers
// ==========================================

export const BenchmarkHubController = {
    selectedBenchmarkId: "swe-bench",

    init() {
        this.bindCardClicks();
        this.startThroughputHUDTimer();
    },

    selectBenchmark(benchmarkId) {
        if (!BENCHMARK_DATASETS[benchmarkId]) return;
        this.selectedBenchmarkId = benchmarkId;

        // Update active class on benchmark cards
        const cards = document.querySelectorAll(".benchmark-card");
        cards.forEach(c => {
            if (c.getAttribute("data-benchmark") === benchmarkId) {
                c.classList.add("active");
            } else {
                c.classList.remove("active");
            }
        });

        // Update Spotlight Card
        const ds = BENCHMARK_DATASETS[benchmarkId];
        const tagEl = document.getElementById("spotlight-tag");
        const titleEl = document.getElementById("spotlight-title");
        const domainEl = document.getElementById("spotlight-domain");
        const divEl = document.getElementById("spotlight-divergence");
        const recEl = document.getElementById("spotlight-recovery");

        if (tagEl) tagEl.textContent = `${ds.name.toUpperCase()} SPOTLIGHT`;
        if (titleEl) titleEl.textContent = `${ds.name}: ${ds.category}`;
        if (domainEl) domainEl.textContent = ds.domain;
        if (divEl) divEl.textContent = ds.divergenceTrigger;
        if (recEl) recEl.textContent = ds.recoveryDelta;
    },

    bindCardClicks() {
        const cards = document.querySelectorAll(".benchmark-card");
        cards.forEach(card => {
            card.addEventListener("click", () => {
                const bId = card.getAttribute("data-benchmark");
                this.selectBenchmark(bId);
            });
        });

        const btnLoad = document.getElementById("btn-load-benchmark-into-studio");
        if (btnLoad) {
            btnLoad.addEventListener("click", () => {
                if (window.SAGStudioEngine) {
                    window.SAGStudioEngine.loadBenchmark(this.selectedBenchmarkId);
                    const studioEl = document.getElementById("replay-studio");
                    if (studioEl) studioEl.scrollIntoView({ behavior: "smooth" });
                    showToast(`⚡ Loaded ${BENCHMARK_DATASETS[this.selectedBenchmarkId].name} trajectory into Replay Studio.`);
                }
            });
        }
    },

    startThroughputHUDTimer() {
        const hudThroughput = document.getElementById("hud-throughput");
        if (!hudThroughput) return;

        // Micro-fluctuate throughput between 2,510.0 and 2,519.0 events/s
        setInterval(() => {
            const base = 2514.5;
            const delta = (Math.random() * 5.0 - 2.5).toFixed(1);
            const val = (base + parseFloat(delta)).toFixed(1);
            hudThroughput.textContent = Number(val).toLocaleString();
        }, 1500);
    }
};

export const MCPController = {
    init() {
        this.bindTabClicks();
        this.bindCopyButtons();
    },

    bindTabClicks() {
        const tabs = document.querySelectorAll(".mcp-tab");
        tabs.forEach(tab => {
            tab.addEventListener("click", () => {
                const target = tab.getAttribute("data-mcp");
                
                tabs.forEach(t => t.classList.remove("active"));
                tab.classList.add("active");

                const contents = document.querySelectorAll(".mcp-tab-content");
                contents.forEach(c => {
                    if (c.id === `mcp-content-${target}`) {
                        c.classList.remove("hidden");
                    } else {
                        c.classList.add("hidden");
                    }
                });
            });
        });
    },

    bindCopyButtons() {
        const copyButtons = document.querySelectorAll(".btn-copy-mcp");
        copyButtons.forEach(btn => {
            btn.addEventListener("click", () => {
                const targetId = btn.getAttribute("data-target");
                const codeBlock = document.getElementById(targetId);
                if (codeBlock) {
                    const text = codeBlock.textContent;
                    if (navigator.clipboard && navigator.clipboard.writeText) {
                        navigator.clipboard.writeText(text).then(() => {
                            showToast("📋 Copied MCP configuration to clipboard!");
                        }).catch(() => {
                            this.fallbackCopy(text);
                        });
                    } else {
                        this.fallbackCopy(text);
                    }
                }
            });
        });
    },

    fallbackCopy(text) {
        const textarea = document.createElement("textarea");
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand("copy");
        document.body.removeChild(textarea);
        showToast("📋 Copied MCP configuration to clipboard!");
    }
};

// ==========================================
// 10. Initial Setup & Global Bindings
// ==========================================

window.approveWaiver = approveWaiver;
window.commitLedgerRebalance = commitLedgerRebalance;
window.dispatchPurchaseOrder = dispatchPurchaseOrder;
window.quarantineSecurityIncident = quarantineSecurityIncident;
window.triggerSagaSimulation = triggerSagaSimulation;
window.runCustomQuery = runCustomQuery;
window.verifyLedgerChain = verifyLedgerChain;
window.repairAndRecalculateLedger = repairAndRecalculateLedger;
window.tamperLedgerBlock2 = tamperLedgerBlock2;
window.SimulatorState = SimulatorState;

document.addEventListener("DOMContentLoaded", async () => {
    // 1. Initialize SAG Studio Engine (R1)
    SAGStudioEngine.init();

    // 2. Initialize Benchmark Hub Controller (R2)
    BenchmarkHubController.init();

    // 3. Initialize Cryptographic Ledger State (R4)
    await initLedger();

    // 4. Initialize MCP Tooling Controller (R5)
    MCPController.init();

    // 5. Bind Tab Navigation Clicks
    const tabButtons = document.querySelectorAll(".workspace-tabs .tab-btn");
    tabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const tab = btn.getAttribute("data-tab");
            toggleTab(tab);
        });
    });

    // 6. Bind Scenario Presets Bar (R3)
    const scenarioButtons = document.querySelectorAll(".btn-scenario");
    const templateSelector = document.getElementById("query-template-selector");
    const codeEditor = document.getElementById("code-query-editor");

    scenarioButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            scenarioButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            const sc = btn.getAttribute("data-scenario");
            if (templateSelector) templateSelector.value = sc;

            if (sc === "audit") {
                if (codeEditor) codeEditor.value = "audit_anomalies --policy='High Value Policy' --fiscal_year=2026";
                runWorkflow("audit");
            } else if (sc === "inventory_stockout") {
                if (codeEditor) codeEditor.value = "check_inventory_health --target_sku='Quantum Processor v1' --auto_mitigate=true";
                runWorkflow("inventory_stockout");
            } else if (sc === "sql_financial") {
                if (codeEditor) codeEditor.value = "synthesize_financial_kpis --period='Q2-2026' --group_by='department'";
                runWorkflow("sql_financial");
            } else if (sc === "rbac_quarantine") {
                if (codeEditor) codeEditor.value = "security_audit --inspect_token='Token#usr_c789' --source_ip='198.51.100.42'";
                runWorkflow("rbac_quarantine");
            } else if (sc === "saga") {
                if (codeEditor) codeEditor.value = `run_saga_procure_to_pay --product="Ergonomic Chair" --qty=1`;
                runWorkflow("saga");
            }
        });
    });

    // 7. Bind Query Editor and Template Selectors
    const paramProduct = document.getElementById("param-product");
    const paramQty = document.getElementById("param-qty");
    const btnExecute = document.getElementById("btn-execute-query");
    const paramGrid = document.querySelector(".parameter-grid");

    if (templateSelector) {
        templateSelector.addEventListener("change", (e) => {
            const val = e.target.value;
            scenarioButtons.forEach(b => {
                b.classList.toggle("active", b.getAttribute("data-scenario") === val);
            });

            if (val === "audit") {
                if (codeEditor) codeEditor.value = "audit_anomalies --policy='High Value Policy' --fiscal_year=2026";
                if (paramGrid) paramGrid.style.display = "none";
            } else if (val === "inventory_stockout") {
                if (codeEditor) codeEditor.value = "check_inventory_health --target_sku='Quantum Processor v1' --auto_mitigate=true";
                if (paramGrid) paramGrid.style.display = "none";
            } else if (val === "sql_financial") {
                if (codeEditor) codeEditor.value = "synthesize_financial_kpis --period='Q2-2026' --group_by='department'";
                if (paramGrid) paramGrid.style.display = "none";
            } else if (val === "rbac_quarantine") {
                if (codeEditor) codeEditor.value = "security_audit --inspect_token='Token#usr_c789' --source_ip='198.51.100.42'";
                if (paramGrid) paramGrid.style.display = "none";
            } else if (val === "saga") {
                const p = paramProduct ? paramProduct.value : "Ergonomic Chair";
                const q = paramQty ? paramQty.value : "1";
                if (codeEditor) codeEditor.value = `run_saga_procure_to_pay --product="${p}" --qty=${q}`;
                if (paramGrid) paramGrid.style.display = "grid";
            } else {
                if (codeEditor) codeEditor.value = "SELECT * FROM orders WHERE total_amount > 500";
                if (paramGrid) paramGrid.style.display = "none";
            }
        });
    }

    if (btnExecute) {
        btnExecute.addEventListener("click", () => {
            const queryText = codeEditor ? codeEditor.value : "";
            if (queryText.includes("audit_anomalies")) {
                runWorkflow("audit");
            } else if (queryText.includes("check_inventory_health")) {
                runWorkflow("inventory_stockout");
            } else if (queryText.includes("synthesize_financial_kpis")) {
                runWorkflow("sql_financial");
            } else if (queryText.includes("security_audit")) {
                runWorkflow("rbac_quarantine");
            } else if (queryText.includes("run_saga_procure_to_pay")) {
                const p = paramProduct ? paramProduct.value : "Ergonomic Chair";
                const q = paramQty ? parseInt(paramQty.value) : 1;
                runWorkflow("saga", { product: p, quantity: q });
            } else {
                runCustomQuery(queryText);
            }
        });
    }

    // 8. Bind Cryptographic Ledger Demo Buttons (R4)
    const btnTamper = document.getElementById("btn-tamper-ledger");
    if (btnTamper) {
        btnTamper.addEventListener("click", () => {
            tamperLedgerBlock2();
        });
    }

    const btnRepair = document.getElementById("btn-repair-ledger");
    if (btnRepair) {
        btnRepair.addEventListener("click", async () => {
            await repairAndRecalculateLedger();
        });
    }

    const btnReverify = document.getElementById("btn-reverify");
    if (btnReverify) {
        btnReverify.addEventListener("click", async () => {
            await verifyLedgerChain();
        });
    }

    const btnReset = document.getElementById("btn-reset-ledger");
    if (btnReset) {
        btnReset.addEventListener("click", async () => {
            // Restore initial mock data
            SimulatorState.orders = JSON.parse(JSON.stringify(INITIAL_ORDERS));
            SimulatorState.products = JSON.parse(JSON.stringify(INITIAL_PRODUCTS));
            SimulatorState.accounts = JSON.parse(JSON.stringify(INITIAL_ACCOUNTS));
            
            // Re-initialize ledger
            await initLedger();
            
            const successBanner = document.getElementById("ledger-status-success");
            const errorBanner = document.getElementById("ledger-status-error");
            if (successBanner) successBanner.classList.remove("hidden");
            if (errorBanner) errorBanner.classList.add("hidden");
            
            // Reset dynamic ephemeral UI & show placeholder
            const placeholder = document.getElementById("ephemeral-placeholder");
            const container = document.getElementById("ephemeral-ui-container");
            if (placeholder) placeholder.classList.remove("hidden");
            if (container) {
                container.classList.add("hidden");
                container.innerHTML = "";
            }

            // Restore terminal console welcome lines
            const terminal = getTerminal();
            if (terminal) {
                terminal.innerHTML = `
                  <div class="console-line system">[SYSTEM] OmniGate Agent Kernel Version 1.0.4 initialized.</div>
                  <div class="console-line response">Waiting for playground query execution...</div>
                `;
            }

            // Reset inputs to initial values
            if (templateSelector) templateSelector.value = "audit";
            if (codeEditor) codeEditor.value = "audit_anomalies --policy='High Value Policy' --fiscal_year=2026";
            if (paramProduct) paramProduct.value = "Ergonomic Chair";
            if (paramQty) paramQty.value = "1";
            if (paramGrid) paramGrid.style.display = "none";

            scenarioButtons.forEach(b => {
                b.classList.toggle("active", b.getAttribute("data-scenario") === "audit");
            });

            updatePayloadTab();
            showToast("↺ System baseline restored. Ledger and simulator state reset.");
        });
    }

    // 9. Initialize the payload tab
    updatePayloadTab();
});
