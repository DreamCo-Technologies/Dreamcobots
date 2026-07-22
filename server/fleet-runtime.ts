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
}

let fleetRuntimeRegistry: FleetRuntimeRegistry | undefined;

export function getFleetRuntimeRegistry() {
  fleetRuntimeRegistry ??= FleetRuntimeRegistry.fromFile();
  return fleetRuntimeRegistry;
}
