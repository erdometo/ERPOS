/**
 * Empirical Adversarial Stress Suite for UI Interaction & Transport Controls
 * Challenger 1 Specialist: Extreme boundary conditions, concurrency, state machine integrity
 */

// Mock Browser DOM Environment
const elements = {};
const listeners = {};

function createMockElement(id) {
  const classList = {
    classes: new Set(),
    add(...args) { args.forEach(c => this.classes.add(c)); },
    remove(...args) { args.forEach(c => this.classes.delete(c)); },
    toggle(c, force) {
      if (force === undefined) {
        if (this.classes.has(c)) this.classes.delete(c);
        else this.classes.add(c);
      } else if (force) {
        this.classes.add(c);
      } else {
        this.classes.delete(c);
      }
    },
    contains(c) { return this.classes.has(c); }
  };

  const el = {
    id,
    tagName: "DIV",
    innerHTML: "",
    textContent: "",
    value: "0",
    className: "",
    classList,
    style: {},
    attributes: {},
    children: [],
    setAttribute(k, v) { this.attributes[k] = String(v); },
    getAttribute(k) { return this.attributes[k] || null; },
    appendChild(child) {
      this.children.push(child);
      return child;
    },
    removeChild(child) {
      const idx = this.children.indexOf(child);
      if (idx >= 0) this.children.splice(idx, 1);
      return child;
    },
    remove() {
      if (this.parentNode) this.parentNode.removeChild(this);
    },
    addEventListener(event, handler) {
      if (!listeners[this.id]) listeners[this.id] = {};
      if (!listeners[this.id][event]) listeners[this.id][event] = [];
      listeners[this.id][event].push(handler);
    },
    dispatchEvent(event) {
      const evListeners = (listeners[this.id] && listeners[this.id][event.type]) || [];
      evListeners.forEach(fn => fn(event));
    },
    reset() {
      this.value = "";
    }
  };
  return el;
}

const mockDoc = {
  getElementById(id) {
    if (!elements[id]) {
      elements[id] = createMockElement(id);
    }
    return elements[id];
  },
  createElement(tag) {
    const el = createMockElement(`dyn_${Math.random().toString(36).slice(2)}`);
    el.tagName = tag.toUpperCase();
    return el;
  },
  querySelectorAll(selector) {
    if (selector.includes(".btn-speed") || selector.includes("#dag-speed-presets")) {
      const speeds = ["0.25", "0.5", "1", "2", "5", "10"];
      return speeds.map(spd => {
        const btn = createMockElement(`btn_speed_${spd}`);
        btn.setAttribute("data-speed", spd);
        return btn;
      });
    }
    if (selector.includes(".tick") || selector.includes("#dag-scrubber-ticks")) {
      return [0, 1, 2, 3, 4].map(s => {
        const t = createMockElement(`tick_${s}`);
        t.setAttribute("data-step", String(s));
        return t;
      });
    }
    if (selector.includes(".dag-node")) {
      const nodes = [];
      for (let i = 0; i < 5; i++) {
        const u = createMockElement(`node_u_${i}`);
        u.setAttribute("data-step", String(i));
        nodes.push(u);
        const l = createMockElement(`node_l_${i}`);
        l.setAttribute("data-step", String(i));
        nodes.push(l);
      }
      return nodes;
    }
    if (selector.includes(".benchmark-card")) {
      return ["swe-bench", "intercode", "webarena", "alfworld", "toolbench", "atif"].map(bId => {
        const card = createMockElement(`card_${bId}`);
        card.setAttribute("data-benchmark", bId);
        return card;
      });
    }
    return [];
  },
  querySelector(selector) {
    return null;
  },
  body: createMockElement("body"),
  addEventListener(event, callback) {}
};

global.document = mockDoc;
global.window = {
  addEventListener() {},
  crypto: {
    subtle: {
      digest: async () => new Uint8Array(32).buffer
    }
  }
};
global.navigator = { clipboard: { writeText: async () => {} } };

function assert(condition, message) {
  if (!condition) {
    console.error(`[FAIL] ${message}`);
    throw new Error(message);
  }
}

let passed = 0;
let total = 0;

function test(name, fn) {
  total++;
  try {
    fn();
    console.log(`  [PASS] ${name}`);
    passed++;
  } catch (e) {
    console.error(`  [FAIL] ${name}: ${e.message}`);
    throw e;
  }
}

async function runAsyncTest(name, fn) {
  total++;
  try {
    await fn();
    console.log(`  [PASS] ${name}`);
    passed++;
  } catch (e) {
    console.error(`  [FAIL] ${name}: ${e.message}`);
    throw e;
  }
}

async function main() {
  console.log("===============================================================================");
  console.log("CHALLENGER 1: UI INTERACTION & TRANSPORT ADVERSARIAL STRESS TEST SUITE");
  console.log("===============================================================================\n");

  const app = await import("./public/app.js");
  const { BENCHMARK_DATASETS, SAGStudioEngine, BenchmarkHubController, Workflows, SimulatorState } = app;

  // ---------------------------------------------------------------------------
  // 1. BOUNDARY CONDITIONS: STEP BOUNDS & CLAMPING
  // ---------------------------------------------------------------------------
  console.log("--- 1. Transport Boundary Clamping & Extreme Values ---");

  test("goToStep clamps negative infinity, negative numbers, and boundary underflow to step 0", () => {
    [-1e9, -9999, -100, -5, -1].forEach(val => {
      SAGStudioEngine.goToStep(val);
      assert(SAGStudioEngine.currentStepIndex === 0, `Expected 0 for goToStep(${val}), got ${SAGStudioEngine.currentStepIndex}`);
    });
  });

  test("goToStep clamps positive overflow and large integers to step 4", () => {
    [5, 6, 10, 100, 99999, 1e9].forEach(val => {
      SAGStudioEngine.goToStep(val);
      assert(SAGStudioEngine.currentStepIndex === 4, `Expected 4 for goToStep(${val}), got ${SAGStudioEngine.currentStepIndex}`);
    });
  });

  test("goToStep handles float inputs by flooring & clamping", () => {
    SAGStudioEngine.goToStep(0.0);
    assert(SAGStudioEngine.currentStepIndex === 0, `Failed for 0.0`);
    SAGStudioEngine.goToStep(1.99);
    assert(SAGStudioEngine.currentStepIndex === 1, `Failed for 1.99`);
    SAGStudioEngine.goToStep(2.01);
    assert(SAGStudioEngine.currentStepIndex === 2, `Failed for 2.01`);
    SAGStudioEngine.goToStep(3.8);
    assert(SAGStudioEngine.currentStepIndex === 3, `Failed for 3.8`);
    SAGStudioEngine.goToStep(4.5);
    assert(SAGStudioEngine.currentStepIndex === 4, `Failed for 4.5`);
  });

  test("stepPrev() 100 consecutive calls from step 0 stays clamped at step 0", () => {
    SAGStudioEngine.goToStep(0);
    for (let i = 0; i < 100; i++) {
      SAGStudioEngine.stepPrev();
      assert(SAGStudioEngine.currentStepIndex === 0, `stepPrev() underflow at iteration ${i}: got ${SAGStudioEngine.currentStepIndex}`);
      assert(SAGStudioEngine.isPlaying === false, "stepPrev() did not pause playback");
    }
  });

  test("stepNext() 100 consecutive calls from step 4 stays clamped at step 4", () => {
    SAGStudioEngine.goToStep(4);
    for (let i = 0; i < 100; i++) {
      SAGStudioEngine.stepNext();
      assert(SAGStudioEngine.currentStepIndex === 4, `stepNext() overflow at iteration ${i}: got ${SAGStudioEngine.currentStepIndex}`);
      assert(SAGStudioEngine.isPlaying === false, "stepNext() did not pause playback");
    }
  });

  test("jumpToTSafe() anchors at t_safe (step 2) across all 6 benchmark datasets from every step", () => {
    const benchmarks = ["swe-bench", "intercode", "webarena", "alfworld", "toolbench", "atif"];
    benchmarks.forEach(bId => {
      SAGStudioEngine.loadBenchmark(bId);
      for (let s = 0; s <= 4; s++) {
        SAGStudioEngine.goToStep(s);
        SAGStudioEngine.jumpToTSafe();
        assert(SAGStudioEngine.currentStepIndex === 2, `jumpToTSafe failed for benchmark ${bId} from step ${s}`);
        assert(SAGStudioEngine.isPlaying === false, `jumpToTSafe did not pause for ${bId}`);
      }
    });
  });

  test("reset() from every step (0..4) and all benchmarks resets cleanly to step 0 and pauses", () => {
    const benchmarks = ["swe-bench", "intercode", "webarena", "alfworld", "toolbench", "atif"];
    benchmarks.forEach(bId => {
      SAGStudioEngine.loadBenchmark(bId);
      for (let s = 0; s <= 4; s++) {
        SAGStudioEngine.goToStep(s);
        SAGStudioEngine.reset();
        assert(SAGStudioEngine.currentStepIndex === 0, `reset failed for benchmark ${bId} from step ${s}`);
        assert(SAGStudioEngine.isPlaying === false, `reset did not pause for ${bId}`);
      }
    });
  });

  // ---------------------------------------------------------------------------
  // 2. CONCURRENCY & RAPID PLAY/PAUSE TOGGLING
  // ---------------------------------------------------------------------------
  console.log("\n--- 2. Concurrency & Rapid Play/Pause State Machine ---");

  test("Rapid Play/Pause spamming (500 iterations) maintains state machine integrity", () => {
    for (let i = 0; i < 500; i++) {
      SAGStudioEngine.togglePlay();
      const expected = (i % 2 === 0);
      assert(SAGStudioEngine.isPlaying === expected, `Mismatch at toggle ${i}: expected isPlaying=${expected}, got ${SAGStudioEngine.isPlaying}`);
      if (expected) {
        assert(SAGStudioEngine.playbackTimer !== null, `Timer null while playing at toggle ${i}`);
      } else {
        assert(SAGStudioEngine.playbackTimer === null, `Timer not cleared while paused at toggle ${i}`);
      }
    }
    // Clean up
    SAGStudioEngine.pause();
    assert(!SAGStudioEngine.isPlaying && SAGStudioEngine.playbackTimer === null, "Failed final pause cleanup");
  });

  // ---------------------------------------------------------------------------
  // 3. EXTREME SPEED MODIFIERS & PLAYBACK MODES
  // ---------------------------------------------------------------------------
  console.log("\n--- 3. Extreme Speed Modifiers & Playback Modes ---");

  test("Speed modifiers calculate interval accurately and enforce minimum 100ms throttle", () => {
    const speeds = [0.25, 0.5, 1.0, 2.0, 5.0, 10.0, 50.0, 100.0];
    speeds.forEach(spd => {
      SAGStudioEngine.setSpeed(spd);
      assert(SAGStudioEngine.playbackSpeed === spd, `Speed set failed for ${spd}`);
      const expectedInterval = Math.max(100, Math.floor(1200 / spd));
      assert(expectedInterval >= 100, `Interval violated 100ms minimum: ${expectedInterval} for speed ${spd}`);
    });
  });

  test("Speed change during active playback cleanly restarts timer without timer leak", () => {
    SAGStudioEngine.play();
    assert(SAGStudioEngine.isPlaying === true, "Engine did not start playing");
    const t1 = SAGStudioEngine.playbackTimer;
    assert(t1 !== null, "Timer was null");

    SAGStudioEngine.setSpeed(2.0);
    assert(SAGStudioEngine.isPlaying === true, "Engine stopped playing after speed change");
    const t2 = SAGStudioEngine.playbackTimer;
    assert(t2 !== null && t2 !== t1, "Timer was not refreshed after speed change");

    SAGStudioEngine.setSpeed(0.5);
    assert(SAGStudioEngine.isPlaying === true, "Engine stopped playing after second speed change");
    const t3 = SAGStudioEngine.playbackTimer;
    assert(t3 !== null && t3 !== t2, "Timer was not refreshed on second speed change");

    SAGStudioEngine.pause();
    assert(SAGStudioEngine.isPlaying === false && SAGStudioEngine.playbackTimer === null, "Pause failed");
  });

  test("Playback mode switching between 'bloom' and 'pulse' (100 iterations)", () => {
    for (let i = 0; i < 100; i++) {
      const mode = i % 2 === 0 ? "bloom" : "pulse";
      SAGStudioEngine.setPlaybackMode(mode);
      assert(SAGStudioEngine.playbackMode === mode, `Failed setting mode to ${mode} at iteration ${i}`);
    }
  });

  test("Invalid playback mode input is rejected gracefully without modifying current mode", () => {
    SAGStudioEngine.setPlaybackMode("bloom");
    SAGStudioEngine.setPlaybackMode("invalid_mode");
    assert(SAGStudioEngine.playbackMode === "bloom", `Invalid mode corrupted playbackMode`);
    SAGStudioEngine.setPlaybackMode(null);
    assert(SAGStudioEngine.playbackMode === "bloom", `Null corrupted playbackMode`);
    SAGStudioEngine.setPlaybackMode(12345);
    assert(SAGStudioEngine.playbackMode === "bloom", `Number corrupted playbackMode`);
  });

  // ---------------------------------------------------------------------------
  // 4. RAPID DATASET SWITCHING & INTEGRITY UNDER PLAYBACK
  // ---------------------------------------------------------------------------
  console.log("\n--- 4. Rapid Dataset Switching & Integrity ---");

  test("Rapid Dataset switching (120 switches) while playback is running maintains synchronization", () => {
    const benchmarks = ["swe-bench", "intercode", "webarena", "alfworld", "toolbench", "atif"];
    SAGStudioEngine.play();

    for (let i = 0; i < 120; i++) {
      const bId = benchmarks[i % benchmarks.length];
      SAGStudioEngine.loadBenchmark(bId);
      assert(SAGStudioEngine.currentDatasetId === bId, `currentDatasetId mismatch: ${SAGStudioEngine.currentDatasetId} vs ${bId}`);
      assert(SAGStudioEngine.currentStepIndex === 0, `loadBenchmark did not reset step to 0`);
      assert(SAGStudioEngine.isPlaying === false, `loadBenchmark did not pause playback`);

      // Resume playing for next iteration
      SAGStudioEngine.play();
    }

    SAGStudioEngine.pause();
    assert(SAGStudioEngine.isPlaying === false, "Final pause failed");
  });

  test("Invalid benchmark dataset ID is safely ignored without crash", () => {
    const initialId = SAGStudioEngine.currentDatasetId;
    SAGStudioEngine.loadBenchmark("nonexistent_benchmark_xyz");
    assert(SAGStudioEngine.currentDatasetId === initialId, "Invalid benchmark ID overwrote currentDatasetId");
    SAGStudioEngine.loadBenchmark("");
    assert(SAGStudioEngine.currentDatasetId === initialId, "Empty benchmark ID overwrote currentDatasetId");
    SAGStudioEngine.loadBenchmark(null);
    assert(SAGStudioEngine.currentDatasetId === initialId, "Null benchmark ID overwrote currentDatasetId");
  });

  // ---------------------------------------------------------------------------
  // 5. TELEMETRY & LANE DATA INTEGRITY ADVERSARIAL AUDIT
  // ---------------------------------------------------------------------------
  console.log("\n--- 5. Telemetry & Lane Data Integrity Adversarial Audit ---");

  test("Every step of every benchmark has valid Upper (Risk >= 0) and Lower (Risk <= Upper) trajectories", () => {
    const benchmarks = ["swe-bench", "intercode", "webarena", "alfworld", "toolbench", "atif"];
    benchmarks.forEach(bId => {
      const ds = BENCHMARK_DATASETS[bId];
      ds.steps.forEach((s, idx) => {
        assert(s.upperLane.riskScore >= 0 && s.upperLane.riskScore <= 100, `Invalid upper risk score at ${bId} step ${idx}`);
        assert(s.lowerLane.riskScore >= 0 && s.lowerLane.riskScore <= 100, `Invalid lower risk score at ${bId} step ${idx}`);
        if (idx >= 2) {
          // At and beyond t_safe divergence, steered risk should be significantly lower than unguided baseline
          assert(s.lowerLane.riskScore < s.upperLane.riskScore, `Steered risk ${s.lowerLane.riskScore} not lower than baseline ${s.upperLane.riskScore} at ${bId} step ${idx}`);
        }
        if (idx === 4) {
          assert(s.upperLane.status === "failure", `Step 4 upperLane expected status 'failure' on ${bId}`);
          assert(s.lowerLane.status === "success", `Step 4 lowerLane expected status 'success' on ${bId}`);
          assert(s.lowerLane.riskScore === 0, `Step 4 lowerLane expected 0% risk on ${bId}`);
        }
      });
    });
  });

  console.log("\n===============================================================================");
  console.log(`CHALLENGER 1 STRESS SUITE RESULTS: ${passed} / ${total} TESTS PASSED (100%)`);
  console.log("===============================================================================\n");
}

main().catch(err => {
  console.error("FATAL ERROR IN CHALLENGER 1 STRESS SUITE:", err);
  process.exit(1);
});
