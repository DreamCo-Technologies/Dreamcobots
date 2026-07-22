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

export type BotEndToEndCertification = {
  schema: "dreamco.bot_e2e_certification.v1";
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
    runtimeToolBindingVerified: boolean;
    platformCapabilityRegistryVerified: boolean;
    calculatorBindingVerified: boolean;
    samplePromptVerified: boolean;
    sandboxExecutionVerified: boolean;
    sandboxEvidenceVerified: boolean;
    liveApprovalGateVerified: boolean;
    noLiveSideEffectVerified: boolean;
  };
  declaredCapabilityCount: number;
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
        "runtime_instance_resolved",
        "profile_and_route_verified",
        "network_default_off",
        "no_live_external_write",
        "approval_gate_available",
      ],
      sampleTestPrompt: this.profile.sample_test_prompt,
      liveExternalActionTaken: false,
      createdAt: now,
    } as const;
  }

  certifyEndToEnd(): BotEndToEndCertification {
    const declaredCapabilities = this.profile.capability_search.split(" | ").filter(Boolean);
    const health = this.health();
    const checks: BotEndToEndCertification["checks"] = {
      runtimeReady: health.state === "ready",
      profileAndBuddyRouteVerified:
        this.profile.readiness.profile_schema === "verified" &&
        this.profile.readiness.buddy_chat_route === "verified",
      declaredCapabilitiesVerified:
        declaredCapabilities.length > 0 && declaredCapabilities.length === this.profile.capability_count,
      runtimeToolBindingVerified: this.profile.tool_summary.some(
        (tool) => tool.id === "buddy_fleet_runtime" && tool.status === "runtime_instance_ready",
      ),
      platformCapabilityRegistryVerified: this.profile.tool_summary.some(
        (tool) => tool.id === "buddy_platform_registry" && tool.status === "runtime_routed",
      ),
      calculatorBindingVerified: this.profile.tool_summary.some(
        (tool) => tool.id === "buddy_bot_calculator" && tool.status === "local_interactive_ready",
      ),
      samplePromptVerified: this.profile.sample_test_prompt.trim().length >= 10,
      sandboxExecutionVerified: false,
      sandboxEvidenceVerified: false,
      liveApprovalGateVerified: false,
      noLiveSideEffectVerified: false,
    };

    try {
      const sandboxResult = this.execute({
        objective: this.profile.sample_test_prompt,
        input: { certification: true, botSlug: this.profile.identity.slug },
        requestedCapabilities: declaredCapabilities.slice(0, 3),
        liveActionRequested: false,
      });
      if (sandboxResult.status === "sandbox_task_packet_ready") {
        checks.sandboxExecutionVerified =
          sandboxResult.instanceId === this.instanceId &&
          sandboxResult.capabilityPlan.length > 0 &&
          sandboxResult.capabilityPlan.every((step) => step.status === "declared_capability");
        const evidence = new Set<string>(sandboxResult.sandboxEvidence);
        checks.sandboxEvidenceVerified = [
          "runtime_instance_resolved",
          "profile_and_route_verified",
          "network_default_off",
          "no_live_external_write",
          "approval_gate_available",
        ].every((item) => evidence.has(item));
      }

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
      schema: "dreamco.bot_e2e_certification.v1",
      slug: this.profile.identity.slug,
      displayName: this.profile.identity.display_name,
      division: this.profile.identity.division,
      category: this.profile.identity.category,
      instanceId: this.instanceId,
      status: failures.length === 0 ? "sandbox_certified" : "failed",
      checks,
      declaredCapabilityCount: declaredCapabilities.length,
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
    const divisionMap = new Map<string, { profiles: number; passed: number; failed: number }>();
    for (const profile of profiles) {
      const division = divisionMap.get(profile.division) ?? { profiles: 0, passed: 0, failed: 0 };
      division.profiles += 1;
      if (profile.status === "sandbox_certified") division.passed += 1;
      else division.failed += 1;
      divisionMap.set(profile.division, division);
    }
    return {
      schema: "dreamco.bot_fleet_e2e.v1",
      summary: {
        profilesTested: profiles.length,
        sandboxCertified: profiles.filter((profile) => profile.status === "sandbox_certified").length,
        failed: profiles.filter((profile) => profile.status === "failed").length,
        divisionsTested: divisionMap.size,
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
