import { readFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";
import { createHash, randomUUID } from "node:crypto";

export type RecoveredBotProfile = {
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
  readiness: { profile_schema: string; buddy_chat_route: string };
  evidence?: Record<string, unknown>;
};

type Overlay = {
  schema: string;
  summary: {
    canonical_baseline: number;
    supplemental_profiles: number;
    combined_routable_profiles_when_loaded: number;
  };
  bots: RecoveredBotProfile[];
  truth_boundary?: string;
};

function normalize(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
}

function tokens(value: string) {
  return new Set(normalize(value).split(/\s+/).filter((x) => x.length >= 3));
}

function routeScore(profile: RecoveredBotProfile, objective: string) {
  const target = tokens(objective);
  const source = tokens([
    profile.identity.slug,
    profile.identity.display_name,
    profile.identity.division,
    profile.identity.category,
    profile.mission,
    profile.capability_search,
  ].join(" "));
  return [...source].filter((token) => target.has(token)).length;
}

export class RecoveredFleetRuntimeRegistry {
  readonly overlay: Overlay;

  constructor(overlay: Overlay) {
    if (overlay.summary.supplemental_profiles !== overlay.bots.length) {
      throw new Error("Recovered overlay summary does not match bot records");
    }
    const slugs = new Set<string>();
    for (const bot of overlay.bots) {
      if (!bot.identity.slug) throw new Error("Recovered bot missing slug");
      if (slugs.has(bot.identity.slug)) throw new Error(`Duplicate recovered bot slug: ${bot.identity.slug}`);
      if (bot.readiness.profile_schema !== "verified" || bot.readiness.buddy_chat_route !== "verified") {
        throw new Error(`${bot.identity.slug} recovered profile is not runtime-ready`);
      }
      slugs.add(bot.identity.slug);
    }
    this.overlay = overlay;
  }

  static fromFile(path = resolve(process.cwd(), "config/generated/recovered-original-bot-overlay.json")) {
    if (!existsSync(path)) {
      return new RecoveredFleetRuntimeRegistry({
        schema: "dreamco.recovered_original_bot_overlay.v2",
        summary: { canonical_baseline: 1051, supplemental_profiles: 0, combined_routable_profiles_when_loaded: 1051 },
        bots: [],
      });
    }
    return new RecoveredFleetRuntimeRegistry(JSON.parse(readFileSync(path, "utf8")) as Overlay);
  }

  summary() {
    return {
      schema: "dreamco.recovered_fleet_runtime_summary.v1",
      canonicalBaseline: this.overlay.summary.canonical_baseline,
      supplementalProfiles: this.overlay.bots.length,
      combinedRoutableProfiles: this.overlay.summary.canonical_baseline + this.overlay.bots.length,
      executionMode: "sandbox",
      liveActionsRequireApproval: true,
    } as const;
  }

  list() {
    return [...this.overlay.bots];
  }

  get(slug: string) {
    return this.overlay.bots.find((bot) => bot.identity.slug === slug);
  }

  route(objective: string, limit = 5) {
    return this.overlay.bots
      .map((profile) => ({ profile, score: routeScore(profile, objective) }))
      .filter((row) => row.score > 0)
      .sort((a, b) => b.score - a.score || a.profile.identity.slug.localeCompare(b.profile.identity.slug))
      .slice(0, Math.max(1, limit));
  }

  execute(slug: string, objective: string) {
    const profile = this.get(slug);
    if (!profile) throw new Error(`Unknown recovered bot: ${slug}`);
    const executionId = randomUUID();
    const evidenceId = createHash("sha256")
      .update(`${slug}:${objective}:${executionId}`)
      .digest("hex")
      .slice(0, 24);
    return {
      schema: "dreamco.recovered_bot_execution.v1",
      executionId,
      evidenceId,
      slug,
      division: profile.identity.division,
      objective,
      mode: "sandbox",
      approvalRequiredForLiveExternalActions: true,
      capabilityCount: profile.capability_count,
      plannedTools: profile.tool_summary.map((tool) => tool.id),
      sourceEvidence: profile.evidence ?? {},
      status: "sandbox_plan_ready",
      truthBoundary: "Recovered historical workers must earn runtime evidence before production claims.",
    } as const;
  }
}

let recoveredFleetRuntimeRegistry: RecoveredFleetRuntimeRegistry | undefined;

export function getRecoveredFleetRuntimeRegistry() {
  recoveredFleetRuntimeRegistry ??= RecoveredFleetRuntimeRegistry.fromFile();
  return recoveredFleetRuntimeRegistry;
}
