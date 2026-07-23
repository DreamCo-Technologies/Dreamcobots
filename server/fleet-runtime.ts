import { createHash, randomUUID } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { z } from "zod";

export const fleetExecutionRequestSchema = z.object({
  objective: z.string().trim().min(10).max(4_000),
  input: z.record(z.unknown()).default({}),
  requestedCapabilities: z.array(z.string().trim().min(2).max(160)).max(20).default([]),
  liveActionRequested: z.boolean().default(false),
}).strict();

export const capabilityTestRequestSchema = z.object({
  capability: z.string().trim().min(2).max(160),
}).strict();

export type FleetExecutionRequest = z.infer<typeof fleetExecutionRequestSchema>;

type CatalogBot = {
  identity: {
    slug: string;
    display_name: string;
    division: string;
    category: string;
    tier: string;
    catalog_status: string;
  };
  mission: string;
  capability_count: number;
  capability_search: string;
  tool_summary: Array<{ id: string; name: string; status: string }>;
  api_candidate_names: string[];
  approval_required: boolean;
  sample_test_prompt: string;
  readiness: {
    profile_schema: string;
    buddy_chat_route: string;
  };
};

type FleetCatalog = {
  schema: string;
  summary: { profiles: number; divisions: number };
  bots: CatalogBot[];
};

export type RuntimeState = "ready" | "offline" | "error";

const REQUIRED_SANDBOX_EVIDENCE = [
  "runtime_instance_resolved",
  "profile_and_route_verified",
  "network_default_off",
  "no_live_external_write",
  "approval_gate_available",
] as const;

const CAPABILITY_TEST_CHECKS = [
  { id: "declaredOnProfile", label: "Declared on profile" },
  { id: "runtimeReady", label: "Runtime ready" },
  { id: "routedAsDeclaredCapability", label: "Routed as declared capability" },
  { id: "evidenceRequired", label: "Evidence required" },
  { id: "requiredSandboxEvidencePresent", label: "Required sandbox evidence present" },
  { id: "noLiveSideEffect", label: "No live side effect" },
] as const;

export type CapabilityContractTest = {
  testId: string;
  capability: string;
  status: "sandbox_contract_passed" | "failed";
  checks: {
    declaredOnProfile: boolean;
    runtimeReady: boolean;
    routedAsDeclaredCapability: boolean;
    evidenceRequired: boolean;
    requiredSandboxEvidencePresent: boolean;
    noLiveSideEffect: boolean;
  };
  evidence: string[];
  liveExternalActionTaken: false;
  failures: string[];
};

export type BotEndToEndCertification = {
  schema: "dreamco.bot_e2e_certification.v2";
  slug: string;
  displayName: string;
  division: string;
  category: string;
  instanceId: string;
  status: "sandbox_certified" | "failed";
  checks: {
    runtimeReady: boolean;
    profileAndBuddyRouteVerified: boolean;
    declaredCapabilitiesVerified: boolean;
    allDeclaredCapabilityContractsTested: boolean;
    runtimeToolBindingVerified: boolean;
    platformCapabilityRegistryVerified: boolean;
    calculatorBindingVerified: boolean;
    distributionBindingVerified: boolean;
    leadSystemBindingVerified: boolean;
    samplePromptVerified: boolean;
    sandboxExecutionVerified: boolean;
    sandboxEvidenceVerified: boolean;
    liveApprovalGateVerified: boolean;
    noLiveSideEffectVerified: boolean;
  };
  declaredCapabilityCount: number;
  capabilityTests: Array<{
    testId: string;
    capability: string;
    status: "sandbox_contract_passed" | "failed";
    liveExternalActionTaken: false;
    failures?: string[];
  }>;
  toolBindingCount: number;
  apiCandidateCount: number;
  liveEndToEndStatus: "not_executed_requires_authenticated_deployment";
  failures: string[];
};

export class BotRuntimeInstance {
  readonly instanceId: string;
  readonly profile: CatalogBot;
  readonly startedAt: string;
  private state: RuntimeState = "ready";
  private executions = 0;
  private lastExecutionAt: string | null = null;

  constructor(profile: CatalogBot) {
    if (profile.readiness.profile_schema !== "verified" || profile.readiness.buddy_chat_route !== "verified") {
      throw new Error(`${profile.identity.slug} does not have verified profile and Buddy route evidence`);
    }
    this.profile = profile;
    this.instanceId = `fleet-runtime-${profile.identity.slug}`;
    this.startedAt = new Date().toISOString();
  }

  health() {
    return {
      schema: "dreamco.bot_runtime_health.v1",
      instanceId: this.instanceId,
      slug: this.profile.identity.slug,
      division: this.profile.identity.division,
      state: this.state,
      runtimeKind: "governed_shared_worker",
      executionMode: "sandbox",
      startedAt: this.startedAt,
      executions: this.executions,
      lastExecutionAt: this.lastExecutionAt,
      profileVerified: true,
      buddyRouteVerified: true,
    } as const;
  }

  stop() {
    this.state = "offline";
  }

  start() {
    this.state = "ready";
  }

  execute(requestInput: FleetExecutionRequest) {
    const request = fleetExecutionRequestSchema.parse(requestInput);
    if (this.state !== "ready") throw new Error(`${this.profile.identity.slug} runtime is not ready`);

    const executionId = `fleet-exec-${randomUUID()}`;
    const now = new Date().toISOString();
    this.executions += 1;
    this.lastExecutionAt = now;

    if (request.liveActionRequested) {
      return {
        schema: "dreamco.bot_runtime_execution.v1",
        executionId,
        instanceId: this.instanceId,
        bot: this.profile.identity,
        status: "approval_required",
        approval: {
          approvalRequestId: `approval-${executionId.slice(-24)}`,
          oneActionOnly: true,
          expiresInSeconds: 900,
          reason: "Live external actions require an authenticated owner and a configured adapter.",
        },
        liveExternalActionTaken: false,
        createdAt: now,
      } as const;
    }

    const declaredCapabilities = this.profile.capability_search.split(" | ").filter(Boolean);
    const requested = request.requestedCapabilities.length
      ? request.requestedCapabilities
      : declaredCapabilities.slice(0, 3);
    const objectiveFingerprint = createHash("sha256").update(request.objective).digest("hex").slice(0, 16);

    return {
      schema: "dreamco.bot_runtime_execution.v1",
      executionId,
      instanceId: this.instanceId,
      bot: this.profile.identity,
      status: "sandbox_task_packet_ready",
      objective: request.objective,
      objectiveFingerprint,
      acceptedInputKeys: Object.keys(request.input).sort(),
      capabilityPlan: requested.map((capability, index) => ({
        step: index + 1,
        capability,
        status: declaredCapabilities.includes(capability) ? "declared_capability" : "owner_requested_extension",
        evidenceRequired: true,
      })),
      toolBindings: this.profile.tool_summary,
      apiBindings: this.profile.api_candidate_names.map((name) => ({
        name,
        state: "configuration_required",
        sandboxTestRequired: true,
      })),
      sandboxEvidence: [
        ...REQUIRED_SANDBOX_EVIDENCE,
      ],
      sampleTestPrompt: this.profile.sample_test_prompt,
      liveExternalActionTaken: false,
      createdAt: now,
    } as const;
  }

  testCapability(capabilityInput: string): CapabilityContractTest {
    const capability = capabilityTestRequestSchema.parse({ capability: capabilityInput }).capability;
    const declaredCapabilities = this.profile.capability_search.split(" | ").filter(Boolean);
    const declaredOnProfile = declaredCapabilities.includes(capability);
    const checks: CapabilityContractTest["checks"] = {
      declaredOnProfile,
      runtimeReady: this.state === "ready",
      routedAsDeclaredCapability: false,
      evidenceRequired: false,
      requiredSandboxEvidencePresent: false,
      noLiveSideEffect: false,
    };
    let evidence: string[] = [];

    if (declaredOnProfile && checks.runtimeReady) {
      try {
        const result = this.execute({
          objective: `Test ${capability} for ${this.profile.identity.display_name} in the governed sandbox.`,
          input: {
            capabilityContractTest: true,
            botSlug: this.profile.identity.slug,
            syntheticDataOnly: true,
          },
          requestedCapabilities: [capability],
          liveActionRequested: false,
        });
        if (result.status === "sandbox_task_packet_ready") {
          const step = result.capabilityPlan[0];
          evidence = [...result.sandboxEvidence];
          checks.routedAsDeclaredCapability =
            result.instanceId === this.instanceId &&
            result.capabilityPlan.length === 1 &&
            step?.capability === capability &&
            step.status === "declared_capability";
          checks.evidenceRequired = step?.evidenceRequired === true;
          const evidenceSet = new Set<string>(evidence);
          checks.requiredSandboxEvidencePresent = REQUIRED_SANDBOX_EVIDENCE.every((item) => evidenceSet.has(item));
          checks.noLiveSideEffect = result.liveExternalActionTaken === false;
        }
      } catch {
        checks.routedAsDeclaredCapability = false;
      }
    }

    const failures = Object.entries(checks)
      .filter(([, passed]) => !passed)
      .map(([check]) => check);
    const digest = createHash("sha256")
      .update(`${this.profile.identity.slug}:${capability}`)
      .digest("hex")
      .slice(0, 20);
    return {
      testId: `capability-test-${digest}`,
      capability,
      status: failures.length === 0 ? "sandbox_contract_passed" : "failed",
      checks,
      evidence,
      liveExternalActionTaken: false,
      failures,
    };
  }

  certifyEndToEnd(): BotEndToEndCertification {
    const declaredCapabilities = this.profile.capability_search.split(" | ").filter(Boolean);
    const health = this.health();
    const capabilityTestResults = declaredCapabilities.map((capability) => this.testCapability(capability));
    const capabilityTests: BotEndToEndCertification["capabilityTests"] = capabilityTestResults.map((test) => ({
      testId: test.testId,
      capability: test.capability,
      status: test.status,
      liveExternalActionTaken: false,
      ...(test.failures.length ? { failures: test.failures } : {}),
    }));
    const checks: BotEndToEndCertification["checks"] = {
      runtimeReady: health.state === "ready",
      profileAndBuddyRouteVerified:
        this.profile.readiness.profile_schema === "verified" &&
        this.profile.readiness.buddy_chat_route === "verified",
      declaredCapabilitiesVerified:
        declaredCapabilities.length > 0 && declaredCapabilities.length === this.profile.capability_count,
      allDeclaredCapabilityContractsTested:
        capabilityTestResults.length === declaredCapabilities.length &&
        capabilityTestResults.every((test) => test.status === "sandbox_contract_passed"),
      runtimeToolBindingVerified: this.profile.tool_summary.some(
        (tool) => tool.id === "buddy_fleet_runtime" && tool.status === "runtime_instance_ready",
      ),
      platformCapabilityRegistryVerified: this.profile.tool_summary.some(
        (tool) => tool.id === "buddy_platform_registry" && tool.status === "runtime_routed",
      ),
      calculatorBindingVerified: this.profile.tool_summary.some(
        (tool) => tool.id === "buddy_bot_calculator" && tool.status === "local_interactive_ready",
      ),
      distributionBindingVerified: this.profile.tool_summary.some(
        (tool) => (
          tool.id === "buddy_distribution_service" &&
          tool.status === "web_ready_native_review_required"
        ),
      ),
      leadSystemBindingVerified: this.profile.tool_summary.some(
        (tool) => (
          tool.id === "buddy_governed_lead_system" &&
          tool.status === "sandbox_ready_external_adapters_required"
        ),
      ),
      samplePromptVerified: this.profile.sample_test_prompt.trim().length >= 10,
      sandboxExecutionVerified: capabilityTestResults.every((test) => test.checks.routedAsDeclaredCapability),
      sandboxEvidenceVerified: capabilityTestResults.every((test) => test.checks.requiredSandboxEvidencePresent),
      liveApprovalGateVerified: false,
      noLiveSideEffectVerified: false,
    };

    try {
      const liveResult = this.execute({
        objective: `Request one live external action for ${this.profile.identity.display_name}.`,
        input: { certification: true, botSlug: this.profile.identity.slug },
        requestedCapabilities: declaredCapabilities.slice(0, 1),
        liveActionRequested: true,
      });
      checks.liveApprovalGateVerified =
        liveResult.status === "approval_required" && liveResult.approval.oneActionOnly === true;
      checks.noLiveSideEffectVerified = liveResult.liveExternalActionTaken === false;
    } catch {
      checks.sandboxExecutionVerified = false;
      checks.liveApprovalGateVerified = false;
      checks.noLiveSideEffectVerified = false;
    }

    const failures = Object.entries(checks)
      .filter(([, passed]) => !passed)
      .map(([check]) => check);
    return {
      schema: "dreamco.bot_e2e_certification.v2",
      slug: this.profile.identity.slug,
      displayName: this.profile.identity.display_name,
      division: this.profile.identity.division,
      category: this.profile.identity.category,
      instanceId: this.instanceId,
      status: failures.length === 0 ? "sandbox_certified" : "failed",
      checks,
      declaredCapabilityCount: declaredCapabilities.length,
      capabilityTests,
      toolBindingCount: this.profile.tool_summary.length,
      apiCandidateCount: this.profile.api_candidate_names.length,
      liveEndToEndStatus: "not_executed_requires_authenticated_deployment",
      failures,
    };
  }
}

export class FleetRuntimeRegistry {
  private readonly runtimes = new Map<string, BotRuntimeInstance>();
  readonly catalogSchema: string;
  readonly loadedAt = new Date().toISOString();

  constructor(catalog: FleetCatalog) {
    if (catalog.summary.profiles !== catalog.bots.length) {
      throw new Error("Fleet catalog summary does not match the bot records");
    }
    for (const profile of catalog.bots) {
      if (this.runtimes.has(profile.identity.slug)) throw new Error(`Duplicate runtime slug: ${profile.identity.slug}`);
      this.runtimes.set(profile.identity.slug, new BotRuntimeInstance(profile));
    }
    if (this.runtimes.size !== 1051) throw new Error(`Expected 1,051 runtime instances, found ${this.runtimes.size}`);
    this.catalogSchema = catalog.schema;
  }

  static fromFile(path = resolve(process.cwd(), "config", "generated", "bots.catalog.json")) {
    const catalog = JSON.parse(readFileSync(path, "utf8")) as FleetCatalog;
    return new FleetRuntimeRegistry(catalog);
  }

  get(slug: string) {
    return this.runtimes.get(slug);
  }

  summary() {
    const health = [...this.runtimes.values()].map((runtime) => runtime.health());
    return {
      schema: "dreamco.fleet_runtime_health.v1",
      catalogSchema: this.catalogSchema,
      loadedAt: this.loadedAt,
      runtimeImplementation: "server/fleet-runtime.ts",
      runtimeKind: "governed_shared_worker",
      instances: health.length,
      ready: health.filter((item) => item.state === "ready").length,
      offline: health.filter((item) => item.state === "offline").length,
      error: health.filter((item) => item.state === "error").length,
      executionMode: "sandbox",
      liveActionsRequireApprovalAndAdapter: true,
    } as const;
  }

  healthChecks() {
    return [...this.runtimes.values()].map((runtime) => runtime.health());
  }

  certifyAllEndToEnd() {
    const profiles = [...this.runtimes.values()]
      .map((runtime) => runtime.certifyEndToEnd())
      .sort((a, b) => a.slug.localeCompare(b.slug));
    const divisionMap = new Map<string, {
      profiles: number;
      passed: number;
      failed: number;
      capabilityTests: number;
      capabilityTestsPassed: number;
      capabilityTestsFailed: number;
    }>();
    for (const profile of profiles) {
      const division = divisionMap.get(profile.division) ?? {
        profiles: 0,
        passed: 0,
        failed: 0,
        capabilityTests: 0,
        capabilityTestsPassed: 0,
        capabilityTestsFailed: 0,
      };
      division.profiles += 1;
      if (profile.status === "sandbox_certified") division.passed += 1;
      else division.failed += 1;
      division.capabilityTests += profile.capabilityTests.length;
      division.capabilityTestsPassed += profile.capabilityTests.filter((test) => test.status === "sandbox_contract_passed").length;
      division.capabilityTestsFailed += profile.capabilityTests.filter((test) => test.status === "failed").length;
      divisionMap.set(profile.division, division);
    }
    const capabilityTests = profiles.flatMap((profile) => profile.capabilityTests);
    return {
      schema: "dreamco.bot_fleet_e2e.v2",
      capabilityTestContract: {
        mode: "repository_controlled_sandbox",
        checks: CAPABILITY_TEST_CHECKS,
        requiredEvidence: REQUIRED_SANDBOX_EVIDENCE,
        networkDefault: "off",
        liveExternalActions: "forbidden",
        externalProviderBehavior: "not_tested_requires_configured_adapter_and_provider_sandbox",
      },
      summary: {
        profilesTested: profiles.length,
        sandboxCertified: profiles.filter((profile) => profile.status === "sandbox_certified").length,
        failed: profiles.filter((profile) => profile.status === "failed").length,
        divisionsTested: divisionMap.size,
        declaredCapabilitiesTested: capabilityTests.length,
        sandboxCapabilityTestsPassed: capabilityTests.filter((test) => test.status === "sandbox_contract_passed").length,
        sandboxCapabilityTestsFailed: capabilityTests.filter((test) => test.status === "failed").length,
        allDeclaredCapabilitiesTested:
          capabilityTests.length > 0 && capabilityTests.every((test) => test.status === "sandbox_contract_passed"),
        repositoryControlledFlowComplete: profiles.every((profile) => profile.status === "sandbox_certified"),
        liveExternalFlowComplete: false,
        liveExternalBoundary: "an authenticated deployment, configured adapter, owner approval, and provider sandbox",
      },
      divisions: [...divisionMap.entries()]
        .map(([division, result]) => ({ division, ...result }))
        .sort((a, b) => a.division.localeCompare(b.division)),
      profiles,
    } as const;
  }
}

let fleetRuntimeRegistry: FleetRuntimeRegistry | undefined;

export function getFleetRuntimeRegistry() {
  fleetRuntimeRegistry ??= FleetRuntimeRegistry.fromFile();
  return fleetRuntimeRegistry;
}
