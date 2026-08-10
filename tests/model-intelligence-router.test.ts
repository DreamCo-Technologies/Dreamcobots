import assert from "node:assert/strict";
import test from "node:test";

import { getModelCapabilityManifest, selectBestModelForTask } from "../server/model-intelligence-router";
import { MODEL_BENCHMARK_TARGET_COUNT, MODEL_BENCHMARK_TARGETS } from "../shared/model-benchmark-targets";

test("500-target benchmark program remains intact", () => {
  assert.equal(MODEL_BENCHMARK_TARGET_COUNT, 500);
  assert.equal(MODEL_BENCHMARK_TARGETS.length, 500);
});

test("frontier and open-weight manifest includes requested providers", () => {
  const manifest = getModelCapabilityManifest();
  const providers = new Set(manifest.providers.map((provider) => provider.id));
  for (const provider of ["openai", "anthropic", "google", "xai", "deepseek", "alibaba", "mistral", "moonshot", "meta"]) {
    assert.ok(providers.has(provider), `missing provider ${provider}`);
  }
});

test("quality-first routing strongly prefers exact tool and modality fit", () => {
  const result = selectBestModelForTask({
    objective: "Research current information on the web, inspect images, and reason carefully about the evidence.",
    requiredTools: ["web_search"],
    requiredModalities: ["image"],
    allowPaid: true,
  }, {
    OPENAI_API_KEY: "test",
    ANTHROPIC_API_KEY: "test",
    GEMINI_API_KEY: "test",
    XAI_API_KEY: "test",
  });
  assert.ok(result.selected);
  assert.equal(result.truthContract.qualityDominatesCostAndLatencyByDefault, true);
  assert.equal(result.selected?.missingTools.length, 0);
  assert.equal(result.selected?.missingModalities.length, 0);
});

test("open-weight-only routing never returns a closed-weight winner", () => {
  const result = selectBestModelForTask({
    objective: "Run a private local coding and reasoning model on owner hardware.",
    requireOpenWeight: true,
    preferLocal: true,
  });
  assert.ok(result.selected);
  assert.ok(["open_weight", "open_weight_base", "weights_available"].includes(result.selected!.weightAccess));
});

test("paid frontier winner requires approval when paid use is not allowed", () => {
  const result = selectBestModelForTask({
    objective: "Use web search and computer use for a complex professional agent task.",
    requiredTools: ["web_search", "computer_use"],
    allowPaid: false,
  }, { OPENAI_API_KEY: "test", GEMINI_API_KEY: "test" });
  assert.ok(result.selected);
  if (result.selected!.license === "provider_terms") {
    assert.equal(result.selected!.paidApprovalRequired, true);
  }
});
