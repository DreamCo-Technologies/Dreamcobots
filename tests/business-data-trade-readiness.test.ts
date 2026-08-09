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
  assert.match(gate.live_actions.charge, /never direct raw-card charge/i);
});

test("live revenue readiness registry does not invent enabled bots", () => {
  const readiness = readJson("config/generated/live-revenue-readiness.json");
  assert.ok(readiness.bot_count >= 1000);
  assert.equal(readiness.live_enabled_count, 0);
  for (const bot of readiness.bots) {
    assert.equal(bot.live_checkout_allowed, false);
    assert.equal(bot.verified_live_revenue_usd, 0);
    assert.equal(bot.checks.owner_live_enable, false);
  }
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
  assert.ok(scout.source_classes.length >= 12);
  assert.ok(scout.comparison_dimensions.length >= 25);
  assert.ok(scout.opportunity_types.includes("Shopify DTC"));
  assert.ok(scout.opportunity_types.includes("Amazon marketplace"));
  assert.ok(scout.opportunity_types.includes("bring manufacturing to U.S."));
  assert.match(scout.truth_rule, /does not prove/i);
  assert.match(scout.guardrails.join(" "), /do not bypass anti-bot controls/i);
});

test("manufacturer marketplace supports RFQ-to-contract workflow safely", () => {
  const market = readJson("config/us-manufacturer-rfq-marketplace-program.json");
  assert.ok(market.marketplace_features.includes("post RFQ"));
  assert.ok(market.marketplace_features.includes("quote comparison"));
  assert.ok(market.marketplace_features.length >= 20);
  assert.ok(market.contract_flow.includes("sample/prototype"));
  assert.equal(market.payments.test_mode_default, true);
  assert.equal(market.payments.live_payment_requires_live_revenue_gate, true);
  assert.equal(market.payments.escrow_claim, false);
});

test("canonical manufacturer catalog starts with verified-data truth instead of fake suppliers", () => {
  const catalog = readJson("website/data/manufacturer-marketplace.json");
  assert.equal(catalog.manufacturer_count, 0);
  assert.equal(catalog.rfq_count, 0);
  assert.equal(catalog.quote_count, 0);
  assert.ok(catalog.source_adapters.length >= 12);
  assert.ok(catalog.sandbox_requirements.length >= 15);
  for (const source of catalog.source_adapters) {
    assert.equal(source.authorized_only, true);
    assert.equal(source.runtime_evidence, "missing_until_connected");
  }
  assert.match(catalog.truth_boundary, /No supplier, RFQ, quote or opportunity is invented/i);
});

test("DreamTrade owns dedicated manufacturing marketplace and China-US scout agents without breaking fixed fleet count", () => {
  const trade = readJson("App_bots/DreamTrade.json");
  assert.equal(trade.division, "DreamTrade");
  assert.equal(trade.total, 12);
  const marketplaceAgent = fs.readFileSync(path.join(root, ".github/agents/manufacturer-marketplace-bot.agent.md"), "utf8");
  const scoutAgent = fs.readFileSync(path.join(root, ".github/agents/china-us-tech-manufacturing-scout.agent.md"), "utf8");
  assert.match(marketplaceAgent, /owned by DreamTrade/i);
  assert.match(scoutAgent, /owned by DreamTrade/i);
});

test("manufacturer marketplace prototype exists and preserves local-draft boundary", () => {
  const html = fs.readFileSync(path.join(root, "website/manufacturer-marketplace.html"), "utf8");
  assert.match(html, /Local RFQ drafts/i);
  assert.match(html, /No manufacturer was contacted/i);
  assert.match(html, /No real RFQ, contract, payment, or outreach/i);
});
