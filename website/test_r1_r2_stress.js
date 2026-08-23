/**
 * Empirical Stress Test Suite for R1 & R2:
 * Proprietary SAG Backtrack & Replay Studio and Multi-Benchmark Ingestion Hub
 */

// 1. Setup mock browser globals before dynamic import of app.js
const elements = {};
const mockDoc = {
  getElementById(id) {
    if (!elements[id]) {
      elements[id] = {
        id,
        innerHTML: "",
        textContent: "",
        value: "0",
        className: "",
        classList: {
          classes: new Set(),
          add(c) { this.classes.add(c); },
          remove(c) { this.classes.delete(c); },
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
        },
        style: {},
        attributes: {},
        setAttribute(k, v) { this.attributes[k] = v; },
        getAttribute(k) { return this.attributes[k]; },
        addEventListener() {}
      };
    }
    return elements[id];
  },
  querySelectorAll(selector) {
    return [];
  },
  querySelector(selector) {
    return null;
  },
  addEventListener(event, callback) {
    // Save DOMContentLoaded listener
    if (event === "DOMContentLoaded") {
      this._domContentLoadedCb = callback;
    }
  }
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

let testsPassed = 0;
let testsTotal = 0;

function test(name, fn) {
  testsTotal++;
  try {
    fn();
    console.log(`  [PASS] ${name}`);
    testsPassed++;
  } catch (err) {
    console.error(`  [FAIL] ${name}: ${err.message}`);
    throw err;
  }
}

async function runAsyncTest(name, fn) {
  testsTotal++;
  try {
    await fn();
    console.log(`  [PASS] ${name}`);
    testsPassed++;
  } catch (err) {
    console.error(`  [FAIL] ${name}: ${err.message}`);
    throw err;
  }
}

async function runSuite() {
  console.log("===============================================================");
  console.log("STARTING EMPIRICAL ADVERSARIAL STRESS TESTS: R1 & R2 ENGINE");
  console.log("===============================================================\n");

  const app = await import("./public/app.js");
  const { BENCHMARK_DATASETS, SAGStudioEngine, BenchmarkHubController } = app;

  // -----------------------------------------------------------------------------
  // SECTION 1: BENCHMARK DATASET INGESTION INTEGRITY (6 BENCHMARKS)
  // -----------------------------------------------------------------------------
  console.log("--- Section 1: Benchmark Dataset Integrity (6 Benchmarks) ---");

  const expectedBenchmarks = ["swe-bench", "intercode", "webarena", "alfworld", "toolbench", "atif"];

  test("All 6 benchmark keys exist in BENCHMARK_DATASETS", () => {
    expectedBenchmarks.forEach(bId => {
      assert(BENCHMARK_DATASETS[bId] !== undefined, `Benchmark ${bId} missing from BENCHMARK_DATASETS`);
    });
  });

  expectedBenchmarks.forEach(bId => {
    test(`Benchmark [${bId}] schema and episodic step integrity`, () => {
      const ds = BENCHMARK_DATASETS[bId];
      assert(ds.id === bId, `Benchmark id mismatch: expected ${bId}, got ${ds.id}`);
      assert(typeof ds.name === "string" && ds.name.length > 0, `Benchmark name invalid`);
      assert(typeof ds.category === "string" && ds.category.length > 0, `Benchmark category invalid`);
      assert(typeof ds.instances === "string" && ds.instances.length > 0, `Benchmark instances invalid`);
      assert(typeof ds.description === "string" && ds.description.length > 0, `Benchmark description invalid`);
      assert(ds.stats && typeof ds.stats.baseline === "string" && typeof ds.stats.sag === "string", `Benchmark stats invalid`);
      assert(ds.tSafeIndex === 2, `Expected tSafeIndex to be 2 for divergence analysis, got ${ds.tSafeIndex}`);
      assert(Array.isArray(ds.steps) && ds.steps.length === 5, `Expected exactly 5 steps (t0..t4), got ${ds.steps.length}`);

      // Verify each step in trajectory
      ds.steps.forEach((step, idx) => {
        assert(step.stepIndex === idx, `Step index mismatch at step ${idx}`);
        assert(typeof step.title === "string" && step.title.length > 0, `Step ${idx} missing title`);
        assert(step.subagent && typeof step.subagent.role === "string" && typeof step.subagent.icon === "string", `Step ${idx} invalid subagent`);
        
        // Upper Lane (Unguided Baseline)
        const u = step.upperLane;
        assert(u && u.nodeId === `u${idx}`, `Step ${idx} invalid upper nodeId ${u ? u.nodeId : 'none'}`);
        assert(typeof u.label === "string" && u.label.length > 0, `Step ${idx} upper label missing`);
        assert(typeof u.riskScore === "number" && u.riskScore >= 0 && u.riskScore <= 100, `Step ${idx} invalid upper riskScore ${u.riskScore}`);
        assert(typeof u.thought === "string" && u.thought.length > 0, `Step ${idx} upper thought missing`);
        assert(typeof u.action === "string" && u.action.length > 0, `Step ${idx} upper action missing`);
        assert(typeof u.observation === "string" && u.observation.length > 0, `Step ${idx} upper observation missing`);
        assert(u.entities && Array.isArray(u.entities.files) && Array.isArray(u.entities.tables) && Array.isArray(u.entities.errors), `Step ${idx} upper entities missing`);

        // Lower Lane (SAG Steered)
        const l = step.lowerLane;
        assert(l && l.nodeId === `l${idx}`, `Step ${idx} invalid lower nodeId ${l ? l.nodeId : 'none'}`);
        assert(typeof l.label === "string" && l.label.length > 0, `Step ${idx} lower label missing`);
        assert(typeof l.riskScore === "number" && l.riskScore >= 0 && l.riskScore <= 100, `Step ${idx} invalid lower riskScore ${l.riskScore}`);
        assert(typeof l.thought === "string" && l.thought.length > 0, `Step ${idx} lower thought missing`);
        assert(typeof l.action === "string" && l.action.length > 0, `Step ${idx} lower action missing`);
        assert(typeof l.observation === "string" && l.observation.length > 0, `Step ${idx} lower observation missing`);
        assert(l.entities && Array.isArray(l.entities.files) && Array.isArray(l.entities.tables) && Array.isArray(l.entities.errors), `Step ${idx} lower entities missing`);

        // Risk gradient properties
        if (idx === 0) {
          assert(u.riskScore < 35, `Step 0 upper risk score should be nominal (<35%), got ${u.riskScore}`);
          assert(l.riskScore < 35, `Step 0 lower risk score should be nominal (<35%), got ${l.riskScore}`);
        } else if (idx === 2) {
          assert(step.isDivergence === true, `Step 2 must be divergence point (t_safe)`);
          assert(typeof step.divergenceReason === "string" && step.divergenceReason.length > 0, `Step 2 must specify divergenceReason`);
          assert(u.riskScore >= 35, `Step 2 upper risk score must be elevated (>=35%), got ${u.riskScore}`);
          assert(l.riskScore <= 20, `Step 2 lower risk score must remain safe (<=20%), got ${l.riskScore}`);
        } else if (idx === 4) {
          assert(u.riskScore >= 65, `Step 4 upper risk score must be critical failure (>=65%), got ${u.riskScore}`);
          assert(u.status === "failure", `Step 4 upper status must be 'failure'`);
          assert(l.riskScore === 0, `Step 4 lower risk score must be 0% for 100% verified completion, got ${l.riskScore}`);
          assert(l.status === "success", `Step 4 lower status must be 'success'`);
        }
      });
    });
  });

  // -----------------------------------------------------------------------------
  // SECTION 2: TRANSPORT CONTROLS ADVERSARIAL STRESS TESTING
  // -----------------------------------------------------------------------------
  console.log("\n--- Section 2: Transport Controls Adversarial Stress Testing ---");

  test("SAGStudioEngine.goToStep boundary clamping (negative, overflow, exact)", () => {
    SAGStudioEngine.loadBenchmark("swe-bench");
    
    // Test negative index -> clamps to 0
    SAGStudioEngine.goToStep(-999);
    assert(SAGStudioEngine.currentStepIndex === 0, `Expected step 0, got ${SAGStudioEngine.currentStepIndex}`);

    // Test overflow index -> clamps to 4
    SAGStudioEngine.goToStep(999);
    assert(SAGStudioEngine.currentStepIndex === 4, `Expected step 4, got ${SAGStudioEngine.currentStepIndex}`);

    // Test middle steps
    [0, 1, 2, 3, 4].forEach(s => {
      SAGStudioEngine.goToStep(s);
      assert(SAGStudioEngine.currentStepIndex === s, `Expected step ${s}, got ${SAGStudioEngine.currentStepIndex}`);
    });
  });

  test("Transport: stepPrev() boundary at step 0 and stepNext() boundary at step 4", () => {
    SAGStudioEngine.goToStep(0);
    SAGStudioEngine.stepPrev();
    assert(SAGStudioEngine.currentStepIndex === 0, `stepPrev at 0 should stay at 0, got ${SAGStudioEngine.currentStepIndex}`);
    assert(!SAGStudioEngine.isPlaying, "stepPrev should pause playback");

    SAGStudioEngine.goToStep(4);
    SAGStudioEngine.stepNext();
    assert(SAGStudioEngine.currentStepIndex === 4, `stepNext at 4 should stay at 4, got ${SAGStudioEngine.currentStepIndex}`);
    assert(!SAGStudioEngine.isPlaying, "stepNext should pause playback");
  });

  test("Transport: jumpToTSafe() from every step (0..4) anchors at tSafeIndex (step 2)", () => {
    [0, 1, 2, 3, 4].forEach(fromStep => {
      SAGStudioEngine.goToStep(fromStep);
      SAGStudioEngine.jumpToTSafe();
      assert(SAGStudioEngine.currentStepIndex === 2, `jumpToTSafe from step ${fromStep} failed: got ${SAGStudioEngine.currentStepIndex}`);
      assert(!SAGStudioEngine.isPlaying, "jumpToTSafe should pause playback");
    });
  });

  test("Transport: reset() from every step (0..4) resets to step 0", () => {
    [0, 1, 2, 3, 4].forEach(fromStep => {
      SAGStudioEngine.goToStep(fromStep);
      SAGStudioEngine.reset();
      assert(SAGStudioEngine.currentStepIndex === 0, `reset from step ${fromStep} failed: got ${SAGStudioEngine.currentStepIndex}`);
      assert(!SAGStudioEngine.isPlaying, "reset should pause playback");
    });
  });

  await runAsyncTest("Transport: Rapid Play/Pause toggling stress test (100 iterations)", async () => {
    SAGStudioEngine.pause();
    assert(!SAGStudioEngine.isPlaying && SAGStudioEngine.playbackTimer === null, "Initial pause state invalid");

    for (let i = 0; i < 100; i++) {
      SAGStudioEngine.togglePlay();
      if (i % 2 === 0) {
        assert(SAGStudioEngine.isPlaying === true, `Iteration ${i}: Expected playing=true`);
        assert(SAGStudioEngine.playbackTimer !== null, `Iteration ${i}: Expected timer to exist`);
      } else {
        assert(SAGStudioEngine.isPlaying === false, `Iteration ${i}: Expected playing=false`);
        assert(SAGStudioEngine.playbackTimer === null, `Iteration ${i}: Expected timer to be null`);
      }
    }

    // Final cleanup
    SAGStudioEngine.pause();
    assert(!SAGStudioEngine.isPlaying && SAGStudioEngine.playbackTimer === null, "Final cleanup pause failed");
  });

  // -----------------------------------------------------------------------------
  // SECTION 3: SPEED MODIFIERS & PLAYBACK MODES
  // -----------------------------------------------------------------------------
  console.log("\n--- Section 3: Speed Modifiers & Playback Modes ---");

  const testSpeeds = [0.25, 0.5, 1.0, 2.0, 5.0, 10.0];

  testSpeeds.forEach(spd => {
    test(`Speed modifier preset ${spd}x calculation & active state`, () => {
      SAGStudioEngine.setSpeed(spd);
      assert(SAGStudioEngine.playbackSpeed === spd, `Speed mismatch: expected ${spd}, got ${SAGStudioEngine.playbackSpeed}`);
      const expectedInterval = Math.max(100, Math.floor(1200 / spd));
      assert(expectedInterval >= 100, `Interval should be at least 100ms, got ${expectedInterval}`);
    });
  });

  test("Speed change during active playback restarts timer cleanly without leaks", () => {
    SAGStudioEngine.play();
    const timer1 = SAGStudioEngine.playbackTimer;
    assert(timer1 !== null, "Timer 1 should exist");

    SAGStudioEngine.setSpeed(5.0);
    assert(SAGStudioEngine.isPlaying === true, "Should still be playing after speed change");
    const timer2 = SAGStudioEngine.playbackTimer;
    assert(timer2 !== null, "Timer 2 should exist");
    assert(timer2 !== timer1, "Old timer should be replaced with new timer");

    SAGStudioEngine.pause();
    assert(SAGStudioEngine.playbackTimer === null, "Timer should be null after pause");
  });

  test("Playback mode switching between 'bloom' and 'pulse'", () => {
    SAGStudioEngine.setPlaybackMode("bloom");
    assert(SAGStudioEngine.playbackMode === "bloom", "Expected mode 'bloom'");

    SAGStudioEngine.setPlaybackMode("pulse");
    assert(SAGStudioEngine.playbackMode === "pulse", "Expected mode 'pulse'");

    SAGStudioEngine.setPlaybackMode("bloom");
    assert(SAGStudioEngine.playbackMode === "bloom", "Expected mode 'bloom'");
  });

  // -----------------------------------------------------------------------------
  // SECTION 4: TELEMETRY INSPECTOR SYNCHRONIZATION
  // -----------------------------------------------------------------------------
  console.log("\n--- Section 4: Telemetry Inspector Synchronization ---");

  expectedBenchmarks.forEach(bId => {
    test(`Telemetry Inspector updates correctly across all steps for [${bId}]`, () => {
      SAGStudioEngine.loadBenchmark(bId);
      const ds = BENCHMARK_DATASETS[bId];

      for (let s = 0; s < 5; s++) {
        SAGStudioEngine.goToStep(s);
        const currentStep = SAGStudioEngine.getCurrentStep();
        assert(currentStep.stepIndex === s, `Step mismatch at step ${s}`);

        const isBeyond = s >= 2;
        const expectedLane = isBeyond ? currentStep.lowerLane : currentStep.upperLane;
        const expectedRisk = expectedLane.riskScore;

        // Verify DOM element sync
        const riskBar = document.getElementById("telemetry-risk-bar");
        const riskBadge = document.getElementById("telemetry-risk-badge");
        const subagentRole = document.getElementById("telemetry-subagent-role");
        const thoughtEl = document.getElementById("telemetry-thought");
        const actionEl = document.getElementById("telemetry-action");
        const obsEl = document.getElementById("telemetry-observation");

        assert(riskBar.style.width === `${expectedRisk}%`, `Risk bar width mismatch: expected ${expectedRisk}%, got ${riskBar.style.width}`);
        assert(subagentRole.textContent === currentStep.subagent.role, `Subagent role mismatch`);
        assert(thoughtEl.textContent === expectedLane.thought, `Thought mismatch at step ${s}`);
        assert(actionEl.textContent === expectedLane.action, `Action mismatch at step ${s}`);
        assert(obsEl.textContent === expectedLane.observation, `Observation mismatch at step ${s}`);
      }
    });
  });

  console.log("\n===============================================================");
  console.log(`ALL EMPIRICAL ADVERSARIAL TESTS PASSED: ${testsPassed} / ${testsTotal}`);
  console.log("===============================================================\n");
}

runSuite().catch(err => {
  console.error("FATAL SUITE ERROR:", err);
  process.exit(1);
});
