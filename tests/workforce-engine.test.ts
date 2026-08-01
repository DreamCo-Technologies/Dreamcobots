import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import test from "node:test";

import {
  analyzeJobOpportunity,
  buildSyntheticJobFixtures,
  buildWorkforceRegistry,
  createPaymentRoutingPlan,
  createProfessionalReviewPacket,
  createServiceOpportunity,
  createVoiceSandboxPlan,
  jobOpportunityRequestSchema,
} from "../server/workforce-engine";

const fleetSlugs = new Set(
  readdirSync("App_bots").filter((name) => name.endsWith(".json")).flatMap((name) => (
    JSON.parse(readFileSync(`App_bots/${name}`, "utf8")).bots.map((bot: { slug: string }) => bot.slug)
  )),
);

function job(description: string, responsibilities: string[] = []) {
  return jobOpportunityRequestSchema.parse({
    ownerUserId: "owner-1",
    title: "Bounded work opportunity",
    description,
    responsibilities,
    sourceType: "owner_supplied",
    currency: "USD",
  });
}

test("workforce registry contains attached worker systems and defaults to Shadow Mode", () => {
  const registry = buildWorkforceRegistry();
  assert.equal(registry.defaultMode, "shadow");
  assert.equal(registry.summary.systems, 4);
  assert.equal(registry.summary.syntheticJobFixtures, 100);
  assert.equal(registry.summary.liveExternalActionsEnabled, false);
  assert.ok(registry.summary.workerBots >= 100);
  assert.deepEqual(new Set(registry.workers.map((worker) => worker.system)), new Set(["payments", "sales", "competition", "opportunity"]));
});

test("all 100 synthetic job fixtures parse, classify, and route only to real fleet bots", () => {
  const fixtures = buildSyntheticJobFixtures();
  assert.equal(fixtures.length, 100);
  for (const fixture of fixtures) {
    const analysis = analyzeJobOpportunity(jobOpportunityRequestSchema.parse(fixture));
    assert.ok(analysis.tasks.length > 0, fixture.title);
    assert.equal(analysis.externalActionsTaken, false);
    for (const slug of analysis.summary.matchedBots) assert.ok(fleetSlugs.has(slug), `${fixture.title}: ${slug}`);
  }
});

test("A-F classification preserves approval, professional, physical, and prohibited boundaries", () => {
  const analysis = analyzeJobOpportunity(job(
    "Classify six bounded responsibilities for a synthetic policy test.",
    [
      "Organize a local source-backed document.",
      "Send email to the approved customer.",
      "Negotiate a supplier agreement.",
      "Provide legal advice as an attorney.",
      "Repair vehicle brakes in the customer's garage.",
      "Hack into a private account to retrieve records.",
    ],
  ));
  assert.deepEqual(analysis.tasks.map((task) => task.level), ["A", "B", "C", "D", "E", "F"]);
  assert.equal(analysis.status, "rejected");
});

test("service, payment, professional, and voice plans stop before external action", () => {
  const service = createServiceOpportunity(job("Prepare a local website prototype and test report for owner review."));
  assert.equal(service.publication.published, false);
  assert.equal(service.delivery.invoiceSent, false);
  const payment = createPaymentRoutingPlan({
    ownerUserId: "owner-1",
    amount: 125,
    currency: "USD",
    paymentType: "invoice",
    customerRegion: "Illinois, US",
    sellerRegion: "Illinois, US",
    preferredProviders: ["stripe", "bank_transfer"],
    prioritize: "lowest_cost",
  });
  assert.equal(payment.paymentProcessed, false);
  assert.equal(payment.fundsMoved, false);
  const review = createProfessionalReviewPacket({
    ownerUserId: "owner-1",
    workTitle: "Contract information packet",
    domain: "legal",
    jurisdiction: "Illinois, US",
    draftReference: "vault:draft-1",
  });
  assert.equal(review.status, "verified_professional_required");
  assert.equal(review.finalDeliverableReleased, false);
  const voice = createVoiceSandboxPlan({
    ownerUserId: "owner-1",
    useCase: "internal",
    script: "Identify Buddy as an AI and practice the approved internal support flow.",
    outbound: false,
  });
  assert.equal(voice.simulatedCallOnly, true);
  assert.equal(voice.liveProviderConfigured, false);
});

test("outbound and recorded voice simulations require consent references", () => {
  assert.throws(() => createVoiceSandboxPlan({
    ownerUserId: "owner-1",
    useCase: "requested_callback",
    script: "Identify Buddy as an AI and practice the requested callback flow.",
    outbound: true,
  }), /recipient consent/);
  assert.throws(() => createVoiceSandboxPlan({
    ownerUserId: "owner-1",
    useCase: "internal",
    script: "Identify Buddy as an AI and practice an internal recorded call flow.",
    recordingEnabled: true,
  }), /recording consent/);
});
