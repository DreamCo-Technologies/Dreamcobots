import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { validateIntelligentStorage } from "../shared/intelligent-data-policy.ts";

const root = process.cwd();
const readJson = (rel: string) => JSON.parse(fs.readFileSync(path.join(root, rel), "utf8"));

test("intelligent storage blocks raw card data and protects credentials", () => {
  assert.throws(() => validateIntelligentStorage({
    ownerId: "u1", purpose: "payment", source: "checkout", dataClass: "financial", retentionClass: "business_record", containsRawPaymentCard: true,
  }), /raw payment card/i);
  assert.throws(() => validateIntelligentStorage({
    ownerId: "u1", purpose: "api", source: "user", dataClass: "internal", retentionClass: "project", containsCredential: true,
  }), /credential_secret/i);
  const result = validateIntelligentStorage({
    ownerId: "u1", purpose: "memory", source: "user", dataClass: "generated_derived", retentionClass: "user_memory", inheritedClasses: ["sensitive_personal"],
  });
  assert.equal(result.effectiveClass, "sensitive_personal");
  assert.equal(result.storageTier, "user_owned_encrypted_vault");
});

test("live revenue defaults to sandbox and requires explicit owner enable", () => {
  const gate = readJson("config/live-revenue-gate.json");
  assert.equal(gate.default_mode, "sandbox_only");
  assert.ok(gate.required_gates.length >= 10);
  assert.match(gate.truth_rule, /owner/i);
  assert.match(gate.truth_rule, /verified Stripe events/i);
});

test("gap gauges cannot reach 100 without runtime evidence", () => {
  const gauges = readJson("config/system-progress-gauges.json");
  const total = gauges.gap_stages.reduce((sum: number, row: {weight:number}) => sum + row.weight, 0);
  assert.equal(total, 100);
  assert.equal(gauges.gap_stages.at(-1).id, "runtime_evidence_pass");
  assert.match(gauges.truth_rule, /100%.*runtime evidence/i);
});

test("mastery packs inherit database book API and evaluation knowledge", () => {
  const layers = readJson("config/mastery-data-pack-knowledge-layers.json");
  for (const key of ["database_knowledge", "book_reference_knowledge", "api_sdk_knowledge", "library_framework_knowledge", "evaluation_knowledge", "provenance_rights_knowledge"]) {
    assert.ok(Array.isArray(layers.required_layers[key]));
    assert.ok(layers.required_layers[key].length >= 5);
  }
});

test("China-US scout is evidence based and supports ecommerce/manufacturing", () => {
  const scout = readJson("config/china-us-tech-manufacturing-scout-program.json");
  assert.ok(scout.source_classes.some((x: string) => x.includes("Alibaba")));
  assert.ok(scout.opportunity_types.includes("Shopify DTC"));
  assert.ok(scout.opportunity_types.includes("Amazon marketplace"));
  assert.ok(scout.opportunity_types.includes("bring manufacturing to U.S."));
  assert.match(scout.truth_rule, /does not prove/i);
});

test("manufacturer marketplace supports RFQ-to-contract workflow safely", () => {
  const market = readJson("config/us-manufacturer-rfq-marketplace-program.json");
  assert.ok(market.marketplace_features.includes("post RFQ"));
  assert.ok(market.marketplace_features.includes("quote comparison"));
  assert.ok(market.contract_flow.includes("sample/prototype"));
  assert.equal(market.payments.test_mode_default, true);
  assert.equal(market.payments.live_payment_requires_live_revenue_gate, true);
  assert.equal(market.payments.escrow_claim, false);
});
