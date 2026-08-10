import { createHash, randomUUID } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { z } from "zod";

import {
  buddyModelRequestSchema,
  resolveBuddyModelPlan,
} from "./buddy-model-policy";

export const fleetExecutionRequestSchema = z.object({
  objective: z.string().trim().min(10).max(4_000),
  input: z.record(z.string(), z.unknown()).default({}),
  requestedCapabilities: z.array(z.string().trim().min(2).max(160)).max(20).default([]),
  liveActionRequested: z.boolean().default(false),
}).strict();

export const capabilityTestRequestSchema = z.object({
  capability: z.string().trim().min(2).max(160),
}).strict();

export const buddyCapabilityRouteRequestSchema = z.object({
  objective: z.string().trim().min(3).max(4_000),
  successContext: z.string().trim().max(1_500).optional(),
  preferredBotSlug: z.string().trim().min(2).max(160).optional(),
  requestedCapabilities: z.array(z.string().trim().min(2).max(160)).max(20).default([]),
  liveActionRequested: z.boolean().default(false),
  ...buddyModelRequestSchema.shape,
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
  summary: { profiles: number; divisions: number; declared_capability_slots?: number };
  bots: CatalogBot[];
};

export class FleetRuntimeInstance {
  constructor(readonly bot: CatalogBot) {}

  execute(requestInput: FleetExecutionRequest) {
    const request = fleetExecutionRequestSchema.parse(requestInput);
    const executionId = `fleet-run-${createHash("sha256").update(`${this.bot.identity.slug}:${request.objective}:${randomUUID()}`).digest("hex").slice(0, 20)}`;
    return {
      schema: "dreamco.fleet_execution.v1",
      executionId,
      bot: this.bot.identity,
      objective: request.objective,
      requestedCapabilities: request.requestedCapabilities,
      mode: request.liveActionRequested ? "approval_required" : "sandbox",
      externalActionTaken: false,
      approvalRequired: request.liveActionRequested || this.bot.approval_required,
      result: {
        status: "planned",
        message: `${this.bot.identity.display_name} accepted the task for governed planning and capability execution.`,
        inputKeys: Object.keys(request.input),
      },
      evidence: {
        profileSchema: this.bot.readiness.profile_schema,
        buddyRoute: this.bot.readiness.buddy_chat_route,
        sampleTestPrompt: this.bot.sample_test_prompt,
      },
    } as const;
  }
}

export class FleetRuntimeRegistry {
  private readonly catalog: FleetCatalog;
  private readonly instances: Map<string, FleetRuntimeInstance>;

  constructor(catalogPath = resolve(process.cwd(), "config/generated/bots.catalog.json")) {
    this.catalog = JSON.parse(readFileSync(catalogPath, "utf8")) as FleetCatalog;
    this.instances = new Map(this.catalog.bots.map((bot) => [bot.identity.slug, new FleetRuntimeInstance(bot)]));
  }

  get(slug: string) {
    return this.instances.get(slug);
  }

  summary() {
    return {
      schema: this.catalog.schema,
      instances: this.instances.size,
      divisions: this.catalog.summary.divisions,
      declaredCapabilities: this.catalog.summary.declared_capability_slots ?? 0,
    };
  }

  routeCapability(requestInput: z.input<typeof buddyCapabilityRouteRequestSchema>) {
    const request = buddyCapabilityRouteRequestSchema.parse(requestInput);
    const modelPlan = resolveBuddyModelPlan(request);
    const preferred = request.preferredBotSlug ? this.get(request.preferredBotSlug) : undefined;
    if (request.preferredBotSlug && !preferred) {
      throw new Error(`Preferred bot does not resolve: ${request.preferredBotSlug}`);
    }
    const terms = new Set(
      `${request.objective} ${request.successContext || ""} ${request.requestedCapabilities.join(" ")}`
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, " ")
        .split(/\s+/)
        .filter((term) => term.length >= 3),
    );
    const rank = (instance: FleetRuntimeInstance) => {
      const haystack = `${instance.bot.identity.slug} ${instance.bot.identity.display_name} ${instance.bot.identity.division} ${instance.bot.identity.category} ${instance.bot.mission} ${instance.bot.capability_search}`.toLowerCase();
      let score = 0;
      const matches: string[] = [];
      for (const term of terms) {
        if (haystack.includes(term)) {
          score += 1;
          matches.push(term);
        }
      }
      for (const requested of request.requestedCapabilities) {
        if (instance.bot.capability_search.toLowerCase().includes(requested.toLowerCase())) score += 4;
      }
      return { instance, score, matches };
    };
    const ranked = [...this.instances.values()].map(rank).sort((a, b) => b.score - a.score || a.instance.bot.identity.slug.localeCompare(b.instance.bot.identity.slug));
    const selected = preferred ? rank(preferred) : ranked[0];
    if (!selected) throw new Error("No fleet runtime instance is available.");
    const execution = selected.instance.execute({
      objective: request.objective.length >= 10 ? request.objective : `${request.objective} — governed Buddy capability route`,
      input: {},
      requestedCapabilities: request.requestedCapabilities,
      liveActionRequested: request.liveActionRequested,
    });
    return {
      schema: "dreamco.buddy_capability_route.v1",
      objective: request.objective,
      selected: selected.instance.bot.identity,
      matchedCapabilities: selected.matches.slice(0, 8),
      selectionReason: preferred ? "owner_selected_specialist" : "capability_match",
      confidence: selected.score >= 8 ? "high" : selected.score >= 3 ? "medium" : "low",
      alternatives: ranked.slice(0, 5).map(({ instance, score, matches }) => ({ ...instance.bot.identity, score, matchedCapabilities: matches.slice(0, 5) })),
      modelPlan,
      coverage: this.summary(),
      execution,
    } as const;
  }
}

let fleetRuntimeRegistry: FleetRuntimeRegistry | undefined;

export function getFleetRuntimeRegistry() {
  fleetRuntimeRegistry ??= new FleetRuntimeRegistry();
  return fleetRuntimeRegistry;
}
