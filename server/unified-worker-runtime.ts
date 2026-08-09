import { buddyCapabilityRouteRequestSchema, getFleetRuntimeRegistry } from "./fleet-runtime";
import { getRecoveredFleetRuntimeRegistry } from "./recovered-fleet-runtime";
import type { z } from "zod";

function normalized(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
}

function explicitlyNamesRecovered(objective: string, slug: string, displayName: string) {
  const target = normalized(objective);
  const normalizedSlug = normalized(slug);
  const normalizedName = normalized(displayName);
  return Boolean(
    (normalizedSlug && target.includes(normalizedSlug)) ||
    (normalizedName && target.includes(normalizedName))
  );
}

export class UnifiedWorkerRuntime {
  readonly canonical = getFleetRuntimeRegistry();
  readonly recovered = getRecoveredFleetRuntimeRegistry();

  summary() {
    const canonical = this.canonical.summary();
    const recovered = this.recovered.summary();
    return {
      schema: "dreamco.unified_worker_runtime_summary.v1",
      canonical,
      recovered,
      totalRoutableWorkers: canonical.instances + recovered.supplementalProfiles,
      canonicalBaselinePreserved: canonical.instances === 1051,
      executionMode: "sandbox",
      liveExternalActionsRequireApproval: true,
      sourceOfTruth: {
        canonical: "config/generated/bots.catalog.json",
        recovered: "config/generated/recovered-original-bot-overlay.json",
        legacyUnification: "config/generated/unified-legacy-system.json",
      },
    } as const;
  }

  get(slug: string) {
    const canonical = this.canonical.get(slug);
    if (canonical) return { source: "canonical" as const, runtime: canonical };
    const recovered = this.recovered.get(slug);
    if (recovered) return { source: "recovered" as const, profile: recovered };
    return undefined;
  }

  routeCapability(requestInput: z.input<typeof buddyCapabilityRouteRequestSchema>) {
    const request = buddyCapabilityRouteRequestSchema.parse(requestInput);
    const recoveredPreferred = request.preferredBotSlug
      ? this.recovered.get(request.preferredBotSlug)
      : undefined;

    if (recoveredPreferred) {
      const execution = this.recovered.execute(recoveredPreferred.identity.slug, request.objective);
      return {
        schema: "dreamco.unified_worker_route.v1",
        source: "recovered" as const,
        objective: request.objective,
        selected: recoveredPreferred.identity,
        matchedCapabilities: recoveredPreferred.capability_search.split(" | ").filter(Boolean).slice(0, 5),
        selectionReason: "owner_selected_recovered_specialist",
        confidence: "high" as const,
        alternatives: [],
        coverage: this.summary(),
        execution,
      } as const;
    }

    const canonicalRoute = this.canonical.routeCapability(request);
    const recoveredRanked = this.recovered.route(request.objective, 5);
    const topRecovered = recoveredRanked[0];
    const explicitRecovered = recoveredRanked.find(({ profile }) =>
      explicitlyNamesRecovered(request.objective, profile.identity.slug, profile.identity.display_name),
    );
    const shouldUseRecovered = Boolean(
      explicitRecovered ||
      (canonicalRoute.confidence === "low" && topRecovered && topRecovered.score >= 3)
    );

    if (shouldUseRecovered) {
      const chosen = explicitRecovered || topRecovered!;
      const execution = this.recovered.execute(chosen.profile.identity.slug, request.objective);
      return {
        schema: "dreamco.unified_worker_route.v1",
        source: "recovered" as const,
        objective: request.objective,
        selected: chosen.profile.identity,
        matchedCapabilities: chosen.profile.capability_search.split(" | ").filter(Boolean).slice(0, 5),
        selectionReason: explicitRecovered
          ? "explicit_recovered_specialist_match"
          : "recovered_specialist_fills_low_confidence_canonical_gap",
        confidence: explicitRecovered ? "high" as const : "medium" as const,
        alternatives: [
          {
            source: "canonical" as const,
            identity: canonicalRoute.selected,
            matchedCapabilities: canonicalRoute.matchedCapabilities,
          },
          ...recoveredRanked
            .filter((row) => row.profile.identity.slug !== chosen.profile.identity.slug)
            .slice(0, 2)
            .map((row) => ({
              source: "recovered" as const,
              identity: row.profile.identity,
              matchedCapabilities: row.profile.capability_search.split(" | ").filter(Boolean).slice(0, 3),
            })),
        ],
        coverage: this.summary(),
        execution,
      } as const;
    }

    return {
      ...canonicalRoute,
      schema: "dreamco.unified_worker_route.v1",
      source: "canonical" as const,
      alternatives: [
        ...canonicalRoute.alternatives.map((row) => ({ source: "canonical" as const, identity: row, matchedCapabilities: row.matchedCapabilities })),
        ...recoveredRanked.slice(0, 3).map((row) => ({
          source: "recovered" as const,
          identity: row.profile.identity,
          matchedCapabilities: row.profile.capability_search.split(" | ").filter(Boolean).slice(0, 3),
        })),
      ],
      coverage: this.summary(),
    } as const;
  }
}

let unifiedWorkerRuntime: UnifiedWorkerRuntime | undefined;

export function getUnifiedWorkerRuntime() {
  unifiedWorkerRuntime ??= new UnifiedWorkerRuntime();
  return unifiedWorkerRuntime;
}
