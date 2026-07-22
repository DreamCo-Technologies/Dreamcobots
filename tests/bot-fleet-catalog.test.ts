import assert from "node:assert/strict";
import test from "node:test";

import { buildFleetCatalog } from "../tools/generate_bot_fleet_catalog";

test("maps every division profile to a verified Buddy route and sandbox blueprint", () => {
  const catalog = buildFleetCatalog();
  assert.equal(catalog.summary.profiles, 1051);
  assert.equal(catalog.summary.divisions, 45);
  assert.equal(catalog.summary.runtime_routed_profiles, 1051);
  assert.equal(catalog.summary.executable_runtime_instances_evidenced, 1051);
  assert.equal(catalog.summary.per_bot_sandbox_blueprints, 1051);
  assert.equal(catalog.summary.per_bot_business_blueprints, 1051);
  assert.equal(catalog.summary.per_bot_governed_lead_systems, 1051);
  assert.ok(catalog.bots.every((bot) => bot.readiness.buddy_chat_route === "verified"));
  assert.ok(catalog.bots.every((bot) => bot.readiness.executable_runtime_instance === "verified"));
  assert.ok(catalog.bots.every((bot) => bot.sandbox.sandbox_id === `sandbox-${bot.identity.slug}`));
  assert.ok(catalog.bots.every((bot) => bot.tools.some((tool) => (
    tool.id === "buddy_platform_registry" && tool.status === "runtime_routed"
  ))));
  assert.ok(catalog.bots.every((bot) => bot.tools.some((tool) => (
    tool.id === "buddy_bot_calculator" && tool.status === "local_interactive_ready"
  ))));
  assert.ok(catalog.bots.every((bot) => bot.tools.some((tool) => (
    tool.id === "buddy_distribution_service" && tool.status === "web_ready_native_review_required"
  ))));
  assert.ok(catalog.bots.every((bot) => bot.tools.some((tool) => (
    tool.id === "buddy_governed_lead_system" && tool.status === "sandbox_ready_external_adapters_required"
  ))));
});

test("gives every bot a detailed permission-gated business and lead blueprint", () => {
  const catalog = buildFleetCatalog();
  assert.ok(catalog.bots.every((bot) => bot.business_system.operating_workflow.length >= 10));
  assert.ok(catalog.bots.every((bot) => bot.business_system.lead_system.discovery.query_templates.length >= 4));
  assert.ok(catalog.bots.every((bot) => bot.business_system.lead_system.qualification.minimum_score_for_owner_review === 65));
  assert.ok(catalog.bots.every((bot) => bot.business_system.lead_system.outreach.recipient_channel_permission_required));
  assert.ok(catalog.bots.every((bot) => bot.business_system.lead_system.outreach.exact_owner_approval_per_message));
  assert.ok(catalog.bots.every((bot) => bot.business_system.lead_system.follow_up.approval_required_for_each_follow_up));
  assert.ok(catalog.bots.every((bot) => bot.business_system.lead_system.follow_up.stop_conditions.includes("opt out")));
  assert.ok(catalog.bots.every((bot) => bot.business_system.readiness.independent_production_business === false));

  const realEstate = catalog.bots.find((bot) => bot.identity.slug === "commercial-scanner");
  const freelance = catalog.bots.find((bot) => bot.identity.slug === "hustle-finder-bot");
  assert.ok(realEstate?.business_system.specialization.promised_outputs.includes("Off-market deal sourcing"));
  assert.ok(freelance?.business_system.specialization.promised_outputs.includes("Skill-to-hustle matching"));
});

test("gives every bot a deterministic unique logo identity", () => {
  const catalog = buildFleetCatalog();
  const logoIds = new Set(catalog.bots.map((bot) => bot.logo.logo_id));
  const callSigns = new Set(catalog.bots.map((bot) => bot.logo.call_sign));
  const slugs = new Set(catalog.bots.map((bot) => bot.identity.slug));
  assert.equal(logoIds.size, catalog.bots.length);
  assert.equal(callSigns.size, catalog.bots.length);
  assert.equal(slugs.size, catalog.bots.length);
  assert.ok(catalog.bots.every((bot) => bot.logo.emoji && bot.logo.monogram && bot.logo.call_sign));
});

test("never calls catalog API candidates connected or profiles production ready", () => {
  const catalog = buildFleetCatalog();
  assert.equal(catalog.summary.configured_external_apis_evidenced, 0);
  assert.equal(catalog.summary.production_ready_profiles, 0);
  assert.ok(catalog.bots.every((bot) => bot.readiness.production_ready === false));
  assert.ok(catalog.bots.every((bot) => bot.approvals.approval_required === true));
  assert.ok(catalog.bots.flatMap((bot) => bot.api_candidates).every((api) => (
    api.status === "configuration_required" && api.sandbox_required
  )));
});
