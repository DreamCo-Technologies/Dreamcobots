import { z } from "zod";

export const ADAPTER_STATES = ["missing","planned","configured","verified","sandbox_tested","live_tested","production_certified","blocked","deprecated"] as const;
export const BENCHMARK_COVERAGE_STATES = ["unmapped","mapped","fixtures_ready","tested","retested","saturated"] as const;

export const botPlatformBindingSchema = z.object({
  botSlug: z.string().trim().min(2).max(160),
  division: z.string().trim().min(2).max(160),
  userJob: z.string().trim().min(5).max(500),
  platformId: z.string().trim().min(2).max(160),
  platformName: z.string().trim().min(2).max(200),
  platformType: z.enum(["api","app","device","website","model_provider","cloud","database","crm","payment","social","marketplace","repository","local_tool","other"]),
  adapterId: z.string().trim().min(2).max(160),
  adapterState: z.enum(ADAPTER_STATES),
  requiredScopes: z.array(z.string().trim().min(1).max(160)).max(100).default([]),
  supportedActions: z.array(z.string().trim().min(2).max(200)).max(200).default([]),
  lastVerifiedAt: z.string().datetime().nullable().default(null),
  evidenceReferences: z.array(z.string().trim().min(2).max(1024)).max(100).default([]),
}).strict();

export const competitorTargetSchema = z.object({
  id: z.string().trim().min(2).max(160),
  name: z.string().trim().min(2).max(200),
  entityType: z.string().trim().min(2).max(120),
  relevantUserJobs: z.array(z.string().trim().min(3).max(500)).min(1).max(100),
  benchmarkDimensions: z.array(z.string().trim().min(2).max(160)).min(1).max(200),
  officialSourceReferences: z.array(z.string().trim().min(2).max(1024)).max(100).default([]),
  lastDiscoveredAt: z.string().datetime().nullable().default(null),
  retired: z.boolean().default(false),
}).strict();

export const botBenchmarkCoverageSchema = z.object({
  schema: z.literal("dreamco.bot_benchmark_coverage.v1"),
  botSlug: z.string().trim().min(2).max(160),
  category: z.string().trim().min(2).max(160),
  profession: z.string().trim().min(2).max(160),
  universalSuiteIds: z.array(z.string().trim().min(2).max(160)).min(1).max(100),
  categorySuiteIds: z.array(z.string().trim().min(2).max(160)).min(1).max(200),
  botSpecificSuiteIds: z.array(z.string().trim().min(2).max(160)).min(1).max(200),
  platformBindings: z.array(botPlatformBindingSchema).max(500).default([]),
  competitors: z.array(competitorTargetSchema).max(2000).default([]),
  coverageState: z.enum(BENCHMARK_COVERAGE_STATES).default("unmapped"),
  discoveryQueries: z.array(z.string().trim().min(2).max(500)).max(200).default([]),
  nextDiscoveryAt: z.string().datetime().nullable().default(null),
  saturationRules: z.object({
    requireAllKnownRelevantCompetitorsMapped: z.boolean().default(true),
    requireAllDeclaredCapabilitiesBenchmarked: z.boolean().default(true),
    requireAllProductionAdaptersBenchmarked: z.boolean().default(true),
    requireFreshOfficialSourceCheck: z.boolean().default(true),
    maxSourceAgeDays: z.number().int().min(1).max(365).default(30),
    stopWhenNoNewRelevantTargetsAcrossRuns: z.number().int().min(1).max(20).default(3),
  }).strict(),
}).strict();

export function benchmarkCoverageGaps(input: z.infer<typeof botBenchmarkCoverageSchema>) {
  const missingAdapters = input.platformBindings.filter((binding) => ["missing","planned","blocked"].includes(binding.adapterState));
  const unverifiedAdapters = input.platformBindings.filter((binding) => !["verified","sandbox_tested","live_tested","production_certified"].includes(binding.adapterState));
  const activeCompetitors = input.competitors.filter((target) => !target.retired);
  return {
    botSlug: input.botSlug,
    missingAdapterCount: missingAdapters.length,
    unverifiedAdapterCount: unverifiedAdapters.length,
    activeCompetitorCount: activeCompetitors.length,
    declaredCoverageState: input.coverageState,
    canCallCoverageSaturated:
      input.coverageState === "saturated"
      && missingAdapters.length === 0
      && unverifiedAdapters.length === 0
      && activeCompetitors.length > 0,
  } as const;
}
