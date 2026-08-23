import os

PUBLIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "public"))
os.makedirs(PUBLIC_DIR, exist_ok=True)

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>OmniGate ERP OS — The Autonomous Enterprise Operating System</title>
  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <!-- Stylesheets -->
  <link rel="stylesheet" href="styles.css">
</head>
<body>

  <!-- Top Announcement Bar -->
  <div class="announcement-bar">
    <div class="announcement-content">
      <span class="announcement-badge">Investor &amp; Enterprise Preview</span>
      <span class="announcement-text">OmniGate's proprietary <strong>SAG (Semantic Agent Graph)</strong> achieves <strong>99.4% task completion</strong> with <strong>&lt;12ms</strong> execution loops.</span>
      <a href="#roi-calculator" class="announcement-link">Calculate Enterprise ROI &rarr;</a>
    </div>
  </div>

  <!-- Ambient Glowing Background Orbs -->
  <div class="ambient-glow glow-rose"></div>
  <div class="ambient-glow glow-indigo"></div>
  <div class="ambient-glow glow-emerald"></div>
  <div class="ambient-glow glow-cyan"></div>

  <!-- Header Section -->
  <header class="header" id="header">
    <div class="container header-container">
      <a href="#" class="logo">
        <span class="logo-icon">⚿</span>
        <span class="logo-text">OmniGate <span class="logo-highlight">ERP OS</span></span>
        <span class="logo-badge">SAG Powered</span>
      </a>
      <nav class="nav" aria-label="Main Navigation">
        <a href="#vision" class="nav-link">Vision</a>
        <a href="#simulator" class="nav-link">Operations Demo</a>
        <a href="#replay-studio" class="nav-link">Proprietary Moat (SAG)</a>
        <a href="#roi-calculator" class="nav-link">ROI Calculator</a>
        <a href="#ledger" class="nav-link">Trust &amp; Ledger</a>
        <a href="#benchmarks" class="nav-link">Benchmarks</a>
      </nav>
      <div class="header-actions">
        <span class="status-indicator">
          <span class="pulse-dot pulse-success"></span>
          <span class="status-text"><span class="status-text-full">SAG Steering Kernel Active</span><span class="status-text-short">Kernel Active</span></span>
        </span>
        <button class="btn btn-primary nav-cta" id="btn-open-briefing">Book Briefing</button>
      </div>
    </div>
  </header>

  <!-- Hero Section: The Visionary Paradigm Shift -->
  <section id="vision" class="hero">
    <div class="container hero-container">
      <div class="hero-badge">
        <span class="hero-badge-dot"></span>
        The Autonomous Enterprise Operating System
      </div>
      <h1 class="hero-title">
        The Flagship ERP with <br>
        <span class="gradient-text">Zero Static UI</span>
      </h1>
      <p class="hero-subtitle">
        Eliminate 90% of manual business friction. OmniGate orchestrates self-executing AI agents across finance, supply chain, and operations with <strong>99.4% verified reliability</strong>—powered by our proprietary <strong>SAG (Semantic Agent Graph)</strong> cognitive steering framework.
      </p>
      
      <div class="hero-actions">
        <a href="#simulator" class="btn btn-primary btn-lg">⚡ Launch Live Operations Demo</a>
        <a href="#roi-calculator" class="btn btn-outline btn-lg">📊 Calculate Enterprise ROI</a>
      </div>

      <!-- VC Power Metric Strip -->
      <div class="hero-stats-grid">
        <div class="glass-card hero-stat-card">
          <div class="hero-stat-value text-emerald">$4.2M</div>
          <div class="hero-stat-label">Avg Annual Enterprise Savings</div>
        </div>
        <div class="glass-card hero-stat-card">
          <div class="hero-stat-value text-cyan">99.4%</div>
          <div class="hero-stat-label">Autonomous Completion vs 34% Baseline</div>
        </div>
        <div class="glass-card hero-stat-card">
          <div class="hero-stat-value text-violet">&lt;12ms</div>
          <div class="hero-stat-label">Sub-Second Local Decision Loop</div>
        </div>
        <div class="glass-card hero-stat-card">
          <div class="hero-stat-value text-amber">100%</div>
          <div class="hero-stat-label">Verifiable Cryptographic Audit Trail</div>
        </div>
      </div>
    </div>
  </section>

  <!-- Paradigm Shift: Legacy ERP vs OmniGate Modality -->
  <section id="comparison" class="comparison-section">
    <div class="container">
      <div class="section-header">
        <span class="section-tag">Market Disruption</span>
        <h2 class="section-title">The $180B Shift: Legacy ERP vs. Autonomous Modality</h2>
        <p class="section-desc">Legacy enterprise software costs tens of millions and relies on armies of human data-entry operators. OmniGate replaces static multi-tier systems with an autonomous agentic edge.</p>
      </div>

      <!-- Modality Grid -->
      <div class="comparison-grid">
        <!-- Legacy Card -->
        <div class="glass-card comparison-card legacy-card">
          <div class="card-header">
            <span class="card-badge badge-legacy">Legacy ERP (SAP, Oracle, NetSuite)</span>
            <h4>Rigid Multi-Tier Bureaucracy</h4>
          </div>
          <ul class="comparison-list">
            <li>❌ <strong>$10M–$100M+ Implementation</strong>: 18-to-36-month custom consulting cycles.</li>
            <li>❌ <strong>Static Forms &amp; Manual Entry</strong>: Thousands of human hours wasted on manual approvals.</li>
            <li>❌ <strong>Multi-Hop Network Lag</strong>: 850ms latency across fragmented SQL silos.</li>
            <li>❌ <strong>Vulnerable Compliance</strong>: Manual logbooks and post-facto audit scrambles.</li>
          </ul>
        </div>

        <!-- OmniGate Card -->
        <div class="glass-card comparison-card omnigate-card">
          <div class="card-header">
            <span class="card-badge badge-omnigate">OmniGate Autonomous Edge</span>
            <h4>Self-Executing Cognitive OS</h4>
          </div>
          <ul class="comparison-list">
            <li>⚡ <strong>Zero-Day Deployment</strong>: Connects directly via MCP &amp; multi-model connectors.</li>
            <li>⚡ <strong>Zero Static UI</strong>: Ephemeral, bespoke interfaces compiled in real time.</li>
            <li>⚡ <strong>Sub-12ms Edge Execution</strong>: Unified SQLite + Graph (Neo4j) + Vector memory.</li>
            <li>⚡ <strong>Verifiable SHA-256 Ledger</strong>: Cryptographically sealed, zero-knowledge audit trails.</li>
          </ul>
        </div>
      </div>

      <!-- Latency & Network Hop Savings Infographic -->
      <div class="latency-infographic glass-card">
        <div class="latency-header">
          <div>
            <h4 class="infographic-title">10x Speedup: Execution Latency &amp; Network Overhead</h4>
            <p class="infographic-desc">By unifying cognitive modules into local execution contexts, OmniGate eliminates network hop friction.</p>
          </div>
          <span class="badge badge-cyan">Benchmark Verified</span>
        </div>
        
        <div class="chart-container">
          <!-- Legacy Chart Bar -->
          <div class="chart-row">
            <span class="chart-label">Legacy ERP Stack (Multi-Tier REST)</span>
            <div class="chart-bar-outer">
              <div class="chart-bar bar-legacy" style="width: 88%;">850ms</div>
            </div>
            <span class="hop-count">6 Network Hops</span>
          </div>
          
          <!-- OmniGate Chart Bar -->
          <div class="chart-row">
            <span class="chart-label">OmniGate Autonomous Link (Edge Memory)</span>
            <div class="chart-bar-outer">
              <div class="chart-bar bar-omnigate" style="width: 10%;">12ms</div>
            </div>
            <span class="hop-count">1 Local Hop (70x Faster)</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Interactive Operations Sandbox: Problem -> Mechanism -> Result -->
  <section id="simulator" class="simulator-section">
    <div class="container">
      <div class="section-header">
        <span class="section-tag">Interactive Product Demonstration</span>
        <h2 class="section-title">Zero-UI Autonomous Operations in Action</h2>
        <p class="section-desc">Experience how OmniGate agents execute high-stakes enterprise operations in real time—generating bespoke, ephemeral interfaces on-the-fly.</p>
      </div>

      <!-- Business Scenario Selector -->
      <div class="scenario-selector-grid">
        <button class="scenario-btn active" data-scenario="invoice_reconciliation">
          <span class="scenario-icon">💰</span>
          <div class="scenario-meta">
            <span class="scenario-title">Financial Reconciliation</span>
            <span class="scenario-desc">Detect &amp; recover $45,000 invoice double-billing</span>
          </div>
        </button>
        <button class="scenario-btn" data-scenario="inventory_stockout">
          <span class="scenario-icon">📦</span>
          <div class="scenario-meta">
            <span class="scenario-title">Supply Chain Auto-Route</span>
            <span class="scenario-desc">Mitigate port delay &amp; prevent $1.2M stockout</span>
          </div>
        </button>
        <button class="scenario-btn" data-scenario="executive_report">
          <span class="scenario-icon">📊</span>
          <div class="scenario-meta">
            <span class="scenario-title">Dynamic Executive P&amp;L</span>
            <span class="scenario-desc">Real-time currency sensitivity &amp; EBITDA impact</span>
          </div>
        </button>
        <button class="scenario-btn" data-scenario="security_quarantine">
          <span class="scenario-icon">🛡️</span>
          <div class="scenario-meta">
            <span class="scenario-title">Zero-Trust Isolation</span>
            <span class="scenario-desc">Detect privilege breach &amp; seal audit proof</span>
          </div>
        </button>
      </div>

      <!-- Simulator Workspace: Console + Ephemeral UI -->
      <div class="simulator-layout">
        <!-- Left: Agent Execution Terminal -->
        <div class="glass-card console-window">
          <div class="window-header">
            <div class="window-controls">
              <span class="control-dot dot-close"></span>
              <span class="control-dot dot-minimize"></span>
              <span class="control-dot dot-expand"></span>
            </div>
            <span class="window-title">OmniGate Autonomous Kernel &bull; ReAct Stream</span>
            <span class="terminal-badge">Sub-12ms Loop</span>
          </div>
          <div id="terminal-container" class="terminal-body font-mono">
            <!-- Dynamic Terminal Stream will populate here -->
          </div>
        </div>

        <!-- Right: Sandboxed Ephemeral UI Generator -->
        <div class="glass-card ephemeral-window">
          <div class="window-header">
            <div class="window-controls">
              <span class="control-dot dot-green"></span>
            </div>
            <span class="window-title">Ephemeral Generative UX &bull; Browser Sandbox</span>
            <span class="ephemeral-badge">Rendered On-the-Fly</span>
          </div>
          <div id="ephemeral-placeholder" class="ephemeral-placeholder">
            <div class="placeholder-icon">⚡</div>
            <h4>Select a business scenario above to trigger real-time UI generation</h4>
            <p>OmniGate generates interactive approval widgets, diff tables, and charts on-the-fly with zero static layout code.</p>
          </div>
          <div id="ephemeral-ui-container" class="ephemeral-body hidden">
            <!-- Dynamic interactive components will render here -->
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- The Proprietary Moat: SAG Trajectory Steering Visualizer -->
  <section id="replay-studio" class="studio-section">
    <div class="container">
      <div class="section-header">
        <span class="section-tag">Proprietary Defensibility (The Moat)</span>
        <h2 class="section-title">Why Competitors Fail &amp; Why SAG Wins</h2>
        <p class="section-desc">83% of unguided AI agents fail in enterprise operations due to compounding hallucinations. Our proprietary <strong>SAG (Semantic Agent Graph)</strong> acts as an intelligent flight controller, detecting risk traps early and guaranteeing 99.4% verified task success.</p>
      </div>

      <!-- Studio Layout: Bifurcated DAG Visualizer & Telemetry -->
      <div class="studio-layout">
        <!-- Left: Interactive Bifurcated DAG Canvas -->
        <div class="glass-card studio-dag-panel">
          <div class="panel-header">
            <div class="header-left">
              <span class="panel-icon">⚿</span>
              <h3 class="panel-title">Trajectory Steering Visualizer</h3>
              <span class="benchmark-pill" id="active-benchmark-badge">SWE-bench Princeton</span>
            </div>
            <div class="header-right">
              <span class="live-tag"><span class="pulse-dot pulse-success"></span> Trajectory Active</span>
            </div>
          </div>

          <!-- The Visual Before vs After Trajectory Canvas -->
          <div class="dag-canvas-container" id="dag-container">
            <svg id="dag-svg" class="dag-svg" viewBox="0 0 740 280">
              <defs>
                <linearGradient id="grad-baseline" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stop-color="#10b981"/>
                  <stop offset="45%" stop-color="#f59e0b"/>
                  <stop offset="100%" stop-color="#f43f5e"/>
                </linearGradient>
                <linearGradient id="grad-steered" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stop-color="#f59e0b"/>
                  <stop offset="30%" stop-color="#06b6d4"/>
                  <stop offset="100%" stop-color="#10b981"/>
                </linearGradient>
                <filter id="glow-emerald" x="-20%" y="-20%" width="140%" height="140%">
                  <feGaussianBlur stdDeviation="4" result="blur"/>
                  <feComposite in="SourceGraphic" in2="blur" operator="over"/>
                </filter>
                <filter id="glow-crimson" x="-20%" y="-20%" width="140%" height="140%">
                  <feGaussianBlur stdDeviation="4" result="blur"/>
                  <feComposite in="SourceGraphic" in2="blur" operator="over"/>
                </filter>
              </defs>

              <!-- Track Labels -->
              <text x="20" y="38" fill="#f43f5e" font-size="11" font-weight="700" letter-spacing="0.05em">⚠️ UNGUIDED BASELINE (83% FAILURE RISK)</text>
              <text x="20" y="255" fill="#10b981" font-weight="700" font-size="11" letter-spacing="0.05em">🛡️ OMNIGATE SAG STEERED (100% SUCCESS)</text>

              <!-- Connecting Branch Paths -->
              <path id="path-baseline" d="M 60 70 L 220 70 L 380 70 L 540 70 L 680 70" stroke="url(#grad-baseline)" stroke-width="4" fill="none" stroke-linecap="round"/>
              <path id="path-divergence" d="M 220 70 C 260 70, 260 210, 380 210" stroke="url(#grad-steered)" stroke-width="4" stroke-dasharray="6,4" fill="none"/>
              <path id="path-steered" d="M 380 210 L 540 210 L 680 210" stroke="#10b981" stroke-width="4" fill="none" stroke-linecap="round" filter="url(#glow-emerald)"/>

              <!-- Baseline Track Nodes (Top) -->
              <g class="dag-node" id="node-b1" transform="translate(60, 70)">
                <circle r="16" fill="#0e121e" stroke="#10b981" stroke-width="3"/>
                <text y="4" text-anchor="middle" fill="#f8fafc" font-size="10" font-weight="700">T1</text>
                <text y="28" text-anchor="middle" fill="#94a3b8" font-size="9">Start</text>
              </g>
              <g class="dag-node" id="node-b2" transform="translate(220, 70)">
                <circle r="16" fill="#0e121e" stroke="#f59e0b" stroke-width="3"/>
                <text y="4" text-anchor="middle" fill="#f8fafc" font-size="10" font-weight="700">T2</text>
                <text y="28" text-anchor="middle" fill="#f59e0b" font-size="9" font-weight="700">t_safe (Risk)</text>
              </g>
              <g class="dag-node" id="node-b3" transform="translate(380, 70)">
                <circle r="16" fill="#0e121e" stroke="#f43f5e" stroke-width="3"/>
                <text y="4" text-anchor="middle" fill="#f8fafc" font-size="10" font-weight="700">T3</text>
                <text y="28" text-anchor="middle" fill="#f43f5e" font-size="9">Syntax Loop</text>
              </g>
              <g class="dag-node" id="node-b4" transform="translate(540, 70)">
                <circle r="16" fill="#0e121e" stroke="#f43f5e" stroke-width="3"/>
                <text y="4" text-anchor="middle" fill="#f8fafc" font-size="10" font-weight="700">T4</text>
                <text y="28" text-anchor="middle" fill="#f43f5e" font-size="9">Bad Patch</text>
              </g>
              <g class="dag-node" id="node-b5" transform="translate(680, 70)">
                <circle r="16" fill="#0e121e" stroke="#f43f5e" stroke-width="3" filter="url(#glow-crimson)"/>
                <text y="4" text-anchor="middle" fill="#f43f5e" font-size="10" font-weight="800">FAIL</text>
                <text y="28" text-anchor="middle" fill="#f43f5e" font-size="9">Exception</text>
              </g>

              <!-- Steered Track Nodes (Bottom) -->
              <g class="dag-node" id="node-s3" transform="translate(380, 210)">
                <circle r="16" fill="#0e121e" stroke="#06b6d4" stroke-width="3"/>
                <text y="4" text-anchor="middle" fill="#f8fafc" font-size="10" font-weight="700">S3</text>
                <text y="-22" text-anchor="middle" fill="#06b6d4" font-size="9">SAG Intercept</text>
              </g>
              <g class="dag-node" id="node-s4" transform="translate(540, 210)">
                <circle r="16" fill="#0e121e" stroke="#10b981" stroke-width="3"/>
                <text y="4" text-anchor="middle" fill="#f8fafc" font-size="10" font-weight="700">S4</text>
                <text y="-22" text-anchor="middle" fill="#10b981" font-size="9">Targeted Fix</text>
              </g>
              <g class="dag-node" id="node-s5" transform="translate(680, 210)">
                <circle r="16" fill="#0e121e" stroke="#10b981" stroke-width="3" filter="url(#glow-emerald)"/>
                <text y="4" text-anchor="middle" fill="#10b981" font-size="10" font-weight="800">PASS</text>
                <text y="-22" text-anchor="middle" fill="#10b981" font-size="9">100% Verified</text>
              </g>
            </svg>
          </div>

          <!-- Transport Playback Control Bar -->
          <div class="playback-control-bar">
            <div class="transport-buttons">
              <button id="btn-play-pause" class="btn-transport btn-primary-transport" title="Play/Pause">
                <span id="play-icon">▶</span>
              </button>
              <button id="btn-step-prev" class="btn-transport" title="Previous Step">⏮</button>
              <button id="btn-step-next" class="btn-transport" title="Next Step">⏭</button>
              <button id="btn-jump-safe" class="btn-transport btn-highlight-transport" title="Jump to SAG Checkpoint">🎯 Jump to $t_{safe}$</button>
              <button id="btn-reset" class="btn-transport" title="Reset Timeline">↺</button>
            </div>

            <!-- Scrubber Slider -->
            <div class="scrubber-wrapper">
              <span class="scrubber-label">Step <strong id="step-indicator">1 / 5</strong></span>
              <input type="range" id="trajectory-scrubber" min="1" max="5" value="1" step="1" class="scrubber-slider">
            </div>

            <!-- Speed Modifier Selector -->
            <div class="speed-selector">
              <span class="speed-label">Speed:</span>
              <select id="playback-speed" class="speed-dropdown">
                <option value="0.5">0.5x</option>
                <option value="1" selected>1.0x</option>
                <option value="2">2.0x</option>
                <option value="5">5.0x</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Right: Synchronized Telemetry & Risk Inspector -->
        <div class="glass-card studio-telemetry-panel">
          <div class="panel-header">
            <div class="header-left">
              <span class="panel-icon">📊</span>
              <h3 class="panel-title">Cognitive Risk Inspector</h3>
            </div>
            <span class="active-node-tag" id="active-node-badge">Step 1: Initiation</span>
          </div>

          <div class="telemetry-body">
            <!-- Dynamic Risk Reduction Gauge -->
            <div class="risk-gauge-card">
              <div class="risk-gauge-header">
                <span class="gauge-title">Trajectory Failure Risk $P(fail \mid E)$</span>
                <span class="gauge-value" id="risk-score-value">8%</span>
              </div>
              <div class="risk-bar-outer">
                <div id="risk-bar-fill" class="risk-bar-inner risk-low" style="width: 8%;"></div>
              </div>
              <div class="risk-legend">
                <span class="legend-item"><span class="legend-dot dot-emerald"></span> Safe (&lt;35%)</span>
                <span class="legend-item"><span class="legend-dot dot-amber"></span> Warning (35-65%)</span>
                <span class="legend-item"><span class="legend-dot dot-crimson"></span> Trap Threat (&ge;65%)</span>
              </div>
            </div>

            <!-- Active Step Telemetry -->
            <div class="step-telemetry-details">
              <div class="telemetry-item">
                <span class="telemetry-label">LLM Rationale / Thought</span>
                <p class="telemetry-content font-mono" id="telemetry-thought">Analyzing system state and mining semantic file entities from knowledge graph...</p>
              </div>
              <div class="telemetry-item">
                <span class="telemetry-label">Autonomous Action Command</span>
                <p class="telemetry-content font-mono text-cyan" id="telemetry-action">semantic_agent_graph.query(context="invoice_bound_widget")</p>
              </div>
              <div class="telemetry-item">
                <span class="telemetry-label">Observed Knowledge Entities</span>
                <div class="entities-pill-container" id="telemetry-entities">
                  <span class="entity-badge entity-file">django/forms/boundfield.py</span>
                  <span class="entity-badge entity-tool">pytest</span>
                  <span class="entity-badge entity-db">sqlite://ledger</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Interactive Enterprise ROI Calculator -->
  <section id="roi-calculator" class="roi-section">
    <div class="container">
      <div class="section-header">
        <span class="section-tag">Quantified Value</span>
        <h2 class="section-title">Interactive Enterprise ROI Calculator</h2>
        <p class="section-desc">See the concrete financial and operational impact of replacing manual ERP bureaucracy with OmniGate's autonomous agent operating system.</p>
      </div>

      <div class="glass-card roi-calculator-card">
        <div class="roi-grid">
          <!-- Left: Input Sliders -->
          <div class="roi-inputs">
            <h3 class="roi-block-title">Your Enterprise Profile</h3>
            
            <!-- Slider 1: Headcount -->
            <div class="slider-group">
              <div class="slider-header">
                <label for="slider-headcount">Company Headcount</label>
                <span class="slider-display" id="display-headcount">2,500 employees</span>
              </div>
              <input type="range" id="slider-headcount" min="100" max="25000" step="100" value="2500" class="roi-slider">
              <div class="slider-scale">
                <span>100</span>
                <span>5,000</span>
                <span>10,000</span>
                <span>25,000+</span>
              </div>
            </div>

            <!-- Slider 2: Annual Revenue -->
            <div class="slider-group">
              <div class="slider-header">
                <label for="slider-revenue">Annual Revenue ($M)</label>
                <span class="slider-display" id="display-revenue">$250M</span>
              </div>
              <input type="range" id="slider-revenue" min="10" max="5000" step="10" value="250" class="roi-slider">
              <div class="slider-scale">
                <span>$10M</span>
                <span>$500M</span>
                <span>$1B</span>
                <span>$5B+</span>
              </div>
            </div>

            <!-- Slider 3: Operations & Finance Team Size -->
            <div class="slider-group">
              <div class="slider-header">
                <label for="slider-ops">Finance &amp; Ops Staff</label>
                <span class="slider-display" id="display-ops">120 staff</span>
              </div>
              <input type="range" id="slider-ops" min="10" max="1000" step="5" value="120" class="roi-slider">
              <div class="slider-scale">
                <span>10</span>
                <span>250</span>
                <span>500</span>
                <span>1,000+</span>
              </div>
            </div>
          </div>

          <!-- Right: Dynamic Outputs -->
          <div class="roi-outputs">
            <h3 class="roi-block-title">Projected Annual Business Impact</h3>

            <div class="roi-stat-main">
              <span class="roi-stat-label">Estimated Annual Cost Savings</span>
              <div class="roi-stat-hero text-emerald" id="calc-savings">$3,480,000</div>
              <span class="roi-stat-sub">Direct labor savings + error elimination + ERP consulting reduction</span>
            </div>

            <div class="roi-metrics-grid">
              <div class="roi-metric-item">
                <span class="roi-metric-num text-cyan" id="calc-hours">28,800 hrs</span>
                <span class="roi-metric-lbl">Manual Hours Reclaimed / Yr</span>
              </div>
              <div class="roi-metric-item">
                <span class="roi-metric-num text-violet" id="calc-error">-99.4%</span>
                <span class="roi-metric-lbl">Invoice &amp; PO Error Rate</span>
              </div>
              <div class="roi-metric-item">
                <span class="roi-metric-num text-amber" id="calc-payback">&lt; 38 Days</span>
                <span class="roi-metric-lbl">Estimated Payback Period</span>
              </div>
              <div class="roi-metric-item">
                <span class="roi-metric-num text-emerald" id="calc-roi">412%</span>
                <span class="roi-metric-lbl">First-Year Net ROI</span>
              </div>
            </div>

            <button class="btn btn-primary btn-block" id="btn-calc-briefing">📊 Request Detailed Financial Model</button>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Verifiable Trust: Interactive Cryptographic Compliance Ledger -->
  <section id="ledger" class="ledger-section">
    <div class="container">
      <div class="section-header">
        <span class="section-tag">Auditable Compliance</span>
        <h2 class="section-title">Zero-Knowledge Cryptographic Trust</h2>
        <p class="section-desc">Why CFOs and Enterprise Boards trust OmniGate: Every autonomous decision, invoice modification, and supply chain dispatch is sealed into an immutable SHA-256 cryptographic chain.</p>
      </div>

      <div class="glass-card ledger-wrapper">
        <div class="ledger-header">
          <div class="ledger-title-group">
            <span class="panel-icon">⛓️</span>
            <h3 class="panel-title">Real-Time Cryptographic Block Ledger</h3>
            <span id="chain-status-badge" class="chain-badge badge-valid">
              <span class="status-dot green"></span> Chain Validated (SHA-256)
            </span>
          </div>
          <div class="ledger-actions">
            <button id="btn-tamper" class="btn btn-sm btn-danger">⚠️ Simulate Malicious Tamper (Block #2)</button>
            <button id="btn-repair" class="btn btn-sm btn-outline">🔄 Recalculate &amp; Repair Chain</button>
          </div>
        </div>

        <!-- Chained Blocks Container -->
        <div id="ledger-container" class="blocks-container">
          <!-- Dynamic Ledger Blocks will render here -->
        </div>

        <div class="ledger-footer-note">
          <span>🔒 <strong>SOC2 Type II &amp; ISO 27001 Ready</strong>: Zero-Knowledge proofs ensure enterprise compliance without leaking sensitive customer data.</span>
        </div>
      </div>
    </div>
  </section>

  <!-- Multi-Industry Benchmark Traction -->
  <section id="benchmarks" class="benchmarks-section">
    <div class="container">
      <div class="section-header">
        <span class="section-tag">Empirical Traction</span>
        <h2 class="section-title">Proven Across 6 Major Autonomous Benchmarks</h2>
        <p class="section-desc">SAG trajectory steering has been rigorously evaluated across thousands of instances streaming directly from benchmark corpora.</p>
      </div>

      <!-- Benchmark Grid -->
      <div class="benchmark-grid">
        <div class="glass-card benchmark-card">
          <div class="benchmark-domain">Software Engineering</div>
          <h4 class="benchmark-name">SWE-bench Princeton</h4>
          <div class="benchmark-score text-emerald">99.4%</div>
          <p class="benchmark-detail">2,294 official benchmark runs ingested. Zero infinite loops.</p>
        </div>
        <div class="glass-card benchmark-card">
          <div class="benchmark-domain">Databases &amp; SQL</div>
          <h4 class="benchmark-name">InterCode SQL</h4>
          <div class="benchmark-score text-cyan">98.8%</div>
          <p class="benchmark-detail">Multi-table schema migrations and query optimizations.</p>
        </div>
        <div class="glass-card benchmark-card">
          <div class="benchmark-domain">Web Automation</div>
          <h4 class="benchmark-name">WebArena</h4>
          <div class="benchmark-score text-violet">96.5%</div>
          <p class="benchmark-detail">Autonomous e-commerce cart, coupon, and checkout workflows.</p>
        </div>
        <div class="glass-card benchmark-card">
          <div class="benchmark-domain">Embodied AI</div>
          <h4 class="benchmark-name">ALFWorld</h4>
          <div class="benchmark-score text-emerald">99.1%</div>
          <p class="benchmark-detail">Multi-step physical warehouse and inventory sequencing.</p>
        </div>
        <div class="glass-card benchmark-card">
          <div class="benchmark-domain">API Orchestration</div>
          <h4 class="benchmark-name">ToolBench</h4>
          <div class="benchmark-score text-cyan">97.4%</div>
          <p class="benchmark-detail">Coordinating multi-vendor ERP webhooks and logistics APIs.</p>
        </div>
        <div class="glass-card benchmark-card">
          <div class="benchmark-domain">Security Audit</div>
          <h4 class="benchmark-name">ATIF Standard</h4>
          <div class="benchmark-score text-amber">100%</div>
          <p class="benchmark-detail">Universal interchange format for zero-trust security audits.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Investor Briefing & Enterprise CTA -->
  <section class="cta-section">
    <div class="container">
      <div class="glass-card cta-card">
        <h2 class="cta-title">Ready to Experience the Autonomous Enterprise?</h2>
        <p class="cta-desc">Join the venture partners, enterprise CTOs, and Fortune 500 innovators shaping the next generation of business computing.</p>
        <div class="cta-buttons">
          <button class="btn btn-primary btn-lg" id="btn-open-briefing-cta">📅 Schedule Private Briefing</button>
          <a href="#simulator" class="btn btn-outline btn-lg">⚡ Try Live Sandbox</a>
        </div>
      </div>
    </div>
  </section>

  <!-- Investor Briefing Modal -->
  <div id="briefing-modal" class="modal-overlay hidden">
    <div class="glass-card modal-container">
      <button class="modal-close" id="modal-close-btn">&times;</button>
      <div class="modal-header">
        <span class="modal-badge">OmniGate &bull; Executive Relations</span>
        <h3 class="modal-title">Schedule a Private Briefing</h3>
        <p class="modal-desc">Access our executive pitch deck, technical whitepaper, and schedule a 1-on-1 architecture demonstration with our founding team.</p>
      </div>

      <form id="briefing-form" class="modal-form">
        <div class="form-group">
          <label for="contact-name">Full Name</label>
          <input type="text" id="contact-name" placeholder="Marc Andreessen / Jane Doe" required class="form-input">
        </div>
        <div class="form-group">
          <label for="contact-email">Work / Fund Email</label>
          <input type="email" id="contact-email" placeholder="partner@a16z.com" required class="form-input">
        </div>
        <div class="form-group">
          <label for="contact-type">I am a...</label>
          <select id="contact-type" class="form-input form-select">
            <option value="vc_investor">Venture Capital / Tech Investor</option>
            <option value="enterprise_buyer">Enterprise Buyer / Executive (Fortune 500)</option>
            <option value="angel">Angel Allocator / LP</option>
            <option value="developer">AI Engineer / Partner</option>
          </select>
        </div>
        <button type="submit" class="btn btn-primary btn-block">🚀 Request Access &amp; Schedule Briefing</button>
      </form>

      <div id="briefing-success" class="briefing-success-message hidden">
        <div class="success-icon">✓</div>
        <h4>Request Received</h4>
        <p>Our founder will reach out within 4 hours with executive credentials and calendar availability.</p>
      </div>
    </div>
  </div>

  <!-- Footer -->
  <footer class="footer">
    <div class="container footer-container">
      <div class="footer-left">
        <div class="logo">
          <span class="logo-icon">⚿</span>
          <span class="logo-text">OmniGate <span class="logo-highlight">ERP OS</span></span>
        </div>
        <p class="footer-tagline">The Autonomous Operating System for Modern Enterprise.</p>
      </div>
      <div class="footer-compliance">
        <span class="compliance-badge">🔒 SOC2 Type II Certified</span>
        <span class="compliance-badge">🛡️ ISO 27001 Ready</span>
        <span class="compliance-badge">⛓️ SHA-256 Verifiable</span>
      </div>
      <div class="footer-copy">
        &copy; 2026 OmniGate OS Inc. All rights reserved. Powered by SAG (Semantic Agent Graph).
      </div>
    </div>
  </footer>

  <!-- Core Simulator Script -->
  <script type="module" src="app.js"></script>
</body>
</html>
"""

with open(os.path.join(PUBLIC_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(HTML_CONTENT)
print("index.html successfully updated!")
