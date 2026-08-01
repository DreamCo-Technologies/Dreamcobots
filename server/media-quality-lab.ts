import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { z } from "zod";

import { getLocalMediaCatalog } from "./media-engine";

type Modality = "voice" | "image" | "video";

type QualityLabCatalog = {
  schema: string;
  reviewed_on: string;
  truth_boundary: string;
  strategy: string[];
  quality_modes: Record<string, {
    candidate_count_per_engine: number;
    repetitions_per_fixture: number;
    release_eligible: boolean;
  }>;
  candidate_pipeline: string[];
  hard_release_gates: string[];
  scorecards: Record<Modality, {
    release_threshold: number;
    regression_tolerance: number;
    dimensions: Record<string, number>;
  }>;
  fixture_sets: Array<{
    id: string;
    modality: Modality;
    minimum_release_fixtures: number;
    cases: string[];
  }>;
  comparison_gate: {
    minimum_fixtures: number;
    minimum_ratings_per_fixture: number;
    confidence_level: number;
    minimum_score_margin: number;
    minimum_wilson_lower_bound: number;
    requires_blind_review: boolean;
    requires_randomized_order: boolean;
    requires_identical_fixtures: boolean;
    superiority_language_before_gate: boolean;
  };
  evidence_required_per_candidate: string[];
  retention: Record<string, string | boolean>;
};

const catalog = JSON.parse(
  readFileSync(resolve(process.cwd(), "config", "buddy-media-quality-lab.json"), "utf8"),
) as QualityLabCatalog;

const sha256Schema = z.string().regex(/^[a-f0-9]{64}$/i, "Use a SHA-256 artifact reference.");
const qualityModeSchema = z.enum(["fast_preview", "balanced", "highest_quality"]);

export const mediaCandidatePlanRequestSchema = z.object({
  projectId: z.string().trim().regex(/^[A-Za-z0-9_-]{3,80}$/),
  modality: z.enum(["voice", "image", "video"]),
  fixtureSetId: z.string().trim().min(3).max(80),
  engineIds: z.array(z.string().trim().min(2).max(80)).min(1).max(6),
  qualityMode: qualityModeSchema.default("highest_quality"),
  seedStart: z.number().int().min(0).max(2_147_483_000).default(1701),
  commercialUse: z.boolean().default(false),
  fixtureClass: z.enum(["synthetic", "owner_consented_media"]).default("synthetic"),
  ownerMediaConsentReceipt: z.string().trim().min(3).max(180).optional(),
  comparisonTargetIds: z.array(z.string().trim().min(2).max(80)).max(4).default([]),
  externalComparisonApproved: z.boolean().default(false),
  paidComparisonApproved: z.boolean().default(false),
  ownerMediaExternalUploadApproved: z.boolean().default(false),
}).strict();

const evidenceSchema = z.object({
  artifactSha256: sha256Schema,
  fixtureSetSha256: sha256Schema,
  fixtureCount: z.number().int().min(1).max(10_000),
  repetitionsPerFixture: z.number().int().min(1).max(20),
  evaluatorVersion: z.string().trim().min(3).max(120),
  evidenceReference: z.string().trim().min(3).max(240),
  engineVersion: z.string().trim().min(1).max(120),
}).strict();

const candidateSchema = z.object({
  id: z.string().trim().regex(/^[A-Za-z0-9_-]{3,120}$/),
  engineId: z.string().trim().min(2).max(80),
  dimensions: z.record(z.number().min(0).max(1)),
  hardGates: z.record(z.boolean()),
  medianLatencyMs: z.number().min(0).max(86_400_000),
  evidence: evidenceSchema,
}).strict();

const baselineComparisonSchema = z.object({
  targetId: z.string().trim().min(2).max(80),
  blinded: z.boolean(),
  randomizedOrder: z.boolean(),
  identicalFixtures: z.boolean(),
  fixtureCount: z.number().int().min(1).max(10_000),
  ratingsPerFixture: z.number().int().min(1).max(100),
  buddyWins: z.number().int().min(0),
  baselineWins: z.number().int().min(0),
  ties: z.number().int().min(0),
  baselineScore: z.number().min(0).max(1),
  fixtureSetSha256: sha256Schema,
  evidenceSha256: sha256Schema,
  evaluatorVersion: z.string().trim().min(3).max(120),
  evidenceReference: z.string().trim().min(3).max(240),
}).strict();

export const mediaQualityEvaluationRequestSchema = z.object({
  projectId: z.string().trim().regex(/^[A-Za-z0-9_-]{3,80}$/),
  modality: z.enum(["voice", "image", "video"]),
  fixtureSetId: z.string().trim().min(3).max(80),
  stableBaselineScore: z.number().min(0).max(1).optional(),
  candidates: z.array(candidateSchema).min(1).max(48),
  baselineComparison: baselineComparisonSchema.optional(),
}).strict();

type Candidate = z.infer<typeof candidateSchema>;
type BaselineComparison = z.infer<typeof baselineComparisonSchema>;

function fixtureSet(modality: Modality, fixtureSetId: string) {
  const fixture = catalog.fixture_sets.find((item) => item.id === fixtureSetId && item.modality === modality);
  if (!fixture) throw new Error(`Fixture set ${fixtureSetId} is not registered for ${modality}.`);
  return fixture;
}

function validateCatalog(): void {
  for (const [modality, scorecard] of Object.entries(catalog.scorecards)) {
    const total = Object.values(scorecard.dimensions).reduce((sum, value) => sum + value, 0);
    if (Math.abs(total - 1) > 0.000001) throw new Error(`${modality} quality weights must total 1.`);
  }
}

validateCatalog();

function engineSupportsModality(engine: ReturnType<typeof getLocalMediaCatalog>["engines"][number], modality: Modality) {
  if (modality === "voice") return engine.modalities.some((item) => ["voice_replication", "speech_synthesis", "cross_lingual_speech", "multilingual_speech", "expressive_speech", "voice_style"].includes(item));
  if (modality === "image") return engine.modalities.some((item) => ["identity_preserving_image", "character_variation", "original_avatar", "brand_mascot", "character_card"].includes(item));
  return engine.modalities.some((item) => ["portrait_animation", "lip_sync", "video_dubbing", "expression_control"].includes(item));
}

export function buildMediaCandidatePlan(input: z.infer<typeof mediaCandidatePlanRequestSchema>) {
  const request = mediaCandidatePlanRequestSchema.parse(input);
  const mediaCatalog = getLocalMediaCatalog();
  const fixture = fixtureSet(request.modality, request.fixtureSetId);
  const engines = [...new Set(request.engineIds)].map((id) => {
    const engine = mediaCatalog.engines.find((item) => item.id === id);
    if (!engine) throw new Error(`Unknown media engine: ${id}`);
    if (!engineSupportsModality(engine, request.modality)) throw new Error(`${id} does not support ${request.modality} quality evaluation.`);
    if (request.commercialUse && !engine.commercial_status.startsWith("eligible")) {
      throw new Error(`${id} is not cleared for commercial candidate generation.`);
    }
    return engine;
  });
  const targets = [...new Set(request.comparisonTargetIds)].map((id) => {
    const target = mediaCatalog.benchmark_targets.find((item) => item.id === id);
    if (!target) throw new Error(`Unknown comparison target: ${id}`);
    return target;
  });
  const external = targets.filter((target) => target.kind === "optional_external_reference");
  if (external.length && !request.externalComparisonApproved) throw new Error("External comparisons require exact approval for this run.");
  if (external.some((target) => target.paid) && !request.paidComparisonApproved) throw new Error("Paid comparisons require a run-specific budget approval.");
  if (request.fixtureClass === "owner_consented_media" && !request.ownerMediaConsentReceipt) {
    throw new Error("Owner media comparisons require an active scoped consent receipt.");
  }
  if (external.length && request.fixtureClass === "owner_consented_media" && !request.ownerMediaExternalUploadApproved) {
    throw new Error("An external owner-media comparison requires a separate upload approval for this run.");
  }
  const mode = catalog.quality_modes[request.qualityMode];
  const candidates = engines.flatMap((engine, engineIndex) => Array.from(
    { length: mode.candidate_count_per_engine },
    (_, candidateIndex) => ({
      id: `${engine.id}-${candidateIndex + 1}`,
      engineId: engine.id,
      seed: request.seedStart + (engineIndex * mode.candidate_count_per_engine) + candidateIndex,
      state: "not_rendered",
    }),
  ));
  return {
    schema: "dreamco.buddy_media_candidate_plan.v1",
    projectId: request.projectId,
    status: "local_candidate_plan_ready",
    modality: request.modality,
    qualityMode: request.qualityMode,
    releaseEligibleMode: mode.release_eligible,
    fixtureSet: fixture,
    fixtureSource: request.fixtureClass,
    ownerMediaConsentReceipt: request.ownerMediaConsentReceipt ?? null,
    engines,
    comparisonTargets: targets,
    candidates,
    repetitionsPerFixture: mode.repetitions_per_fixture,
    pipeline: catalog.candidate_pipeline,
    hardReleaseGates: catalog.hard_release_gates,
    evidenceRequired: catalog.evidence_required_per_candidate,
    execution: {
      renderExecuted: false,
      networkDefault: "off",
      externalCallExecuted: false,
      ownerMediaUploaded: false,
      nextGate: external.length
        ? "install_local_weights_and_configure_a_separately_authenticated_comparison_adapter"
        : "install_exact_local_weights_then_render_and_measure",
    },
  } as const;
}

function scoreCandidate(candidate: Candidate, modality: Modality, minimumFixtureCount: number) {
  const scorecard = catalog.scorecards[modality];
  const missingDimensions = Object.keys(scorecard.dimensions).filter((dimension) => candidate.dimensions[dimension] === undefined);
  const unknownDimensions = Object.keys(candidate.dimensions).filter((dimension) => scorecard.dimensions[dimension] === undefined);
  const missingGates = catalog.hard_release_gates.filter((gate) => candidate.hardGates[gate] !== true);
  const weightedScore = missingDimensions.length || unknownDimensions.length
    ? 0
    : Object.entries(scorecard.dimensions).reduce(
      (sum, [dimension, weight]) => sum + candidate.dimensions[dimension] * weight,
      0,
    );
  const evidenceComplete = candidate.evidence.fixtureCount >= minimumFixtureCount
    && candidate.evidence.repetitionsPerFixture >= 1;
  const releaseEligible = !missingDimensions.length
    && !unknownDimensions.length
    && !missingGates.length
    && evidenceComplete
    && weightedScore >= scorecard.release_threshold;
  return {
    id: candidate.id,
    engineId: candidate.engineId,
    score: Number(weightedScore.toFixed(6)),
    releaseEligible,
    missingDimensions,
    unknownDimensions,
    failedOrMissingGates: missingGates,
    evidenceComplete,
    medianLatencyMs: candidate.medianLatencyMs,
    artifactSha256: candidate.evidence.artifactSha256,
    evidenceReference: candidate.evidence.evidenceReference,
  };
}

function wilsonLowerBound(successes: number, trials: number): number {
  if (trials <= 0) return 0;
  const zValue = 1.959963984540054;
  const proportion = successes / trials;
  const denominator = 1 + ((zValue ** 2) / trials);
  const center = proportion + ((zValue ** 2) / (2 * trials));
  const margin = zValue * Math.sqrt(((proportion * (1 - proportion)) + ((zValue ** 2) / (4 * trials))) / trials);
  return (center - margin) / denominator;
}

function evaluateComparison(comparison: BaselineComparison | undefined, winningScore: number | null) {
  if (!comparison) return null;
  const mediaCatalog = getLocalMediaCatalog();
  const target = mediaCatalog.benchmark_targets.find((item) => item.id === comparison.targetId);
  if (!target) throw new Error(`Unknown comparison target: ${comparison.targetId}`);
  const decisions = comparison.buddyWins + comparison.baselineWins + comparison.ties;
  const expectedMinimum = comparison.fixtureCount * comparison.ratingsPerFixture;
  if (decisions < expectedMinimum) throw new Error("Pairwise comparison outcomes do not cover every required fixture rating.");
  const effectiveWins = comparison.buddyWins + (comparison.ties * 0.5);
  const winRate = decisions ? effectiveWins / decisions : 0;
  const lowerBound = wilsonLowerBound(effectiveWins, decisions);
  const gate = catalog.comparison_gate;
  const failures = [
    comparison.fixtureCount < gate.minimum_fixtures ? "insufficient_fixtures" : null,
    comparison.ratingsPerFixture < gate.minimum_ratings_per_fixture ? "insufficient_raters" : null,
    gate.requires_blind_review && !comparison.blinded ? "review_not_blinded" : null,
    gate.requires_randomized_order && !comparison.randomizedOrder ? "order_not_randomized" : null,
    gate.requires_identical_fixtures && !comparison.identicalFixtures ? "fixtures_not_identical" : null,
    lowerBound <= gate.minimum_wilson_lower_bound ? "win_rate_not_statistically_clear" : null,
    winningScore === null || winningScore - comparison.baselineScore < gate.minimum_score_margin ? "score_margin_too_small" : null,
  ].filter((value): value is string => Boolean(value));
  const claimAllowed = failures.length === 0;
  return {
    target,
    claimAllowed,
    claimStatus: claimAllowed ? "evidence_backed_advantage" : "comparison_not_proven",
    claim: claimAllowed
      ? `Buddy outperformed ${target.label} on the signed ${comparison.fixtureCount}-fixture comparison recorded at ${comparison.evidenceReference}.`
      : null,
    failures,
    statistics: {
      decisions,
      winRate: Number(winRate.toFixed(6)),
      wilsonLowerBound95: Number(lowerBound.toFixed(6)),
      winningScore,
      baselineScore: comparison.baselineScore,
    },
  };
}

export function evaluateMediaCandidates(input: z.infer<typeof mediaQualityEvaluationRequestSchema>) {
  const request = mediaQualityEvaluationRequestSchema.parse(input);
  const fixture = fixtureSet(request.modality, request.fixtureSetId);
  const scorecard = catalog.scorecards[request.modality];
  const knownEngines = new Set(getLocalMediaCatalog().engines.map((engine) => engine.id));
  for (const candidate of request.candidates) {
    if (!knownEngines.has(candidate.engineId)) throw new Error(`Unknown media engine: ${candidate.engineId}`);
    const engine = getLocalMediaCatalog().engines.find((item) => item.id === candidate.engineId)!;
    if (!engineSupportsModality(engine, request.modality)) {
      throw new Error(`${candidate.engineId} does not support ${request.modality} quality evaluation.`);
    }
  }
  const results = request.candidates
    .map((candidate) => scoreCandidate(candidate, request.modality, fixture.minimum_release_fixtures))
    .sort((left, right) => right.score - left.score || left.medianLatencyMs - right.medianLatencyMs || left.id.localeCompare(right.id));
  const candidateWinner = results.find((result) => result.releaseEligible) ?? null;
  const regressionFloor = request.stableBaselineScore === undefined
    ? null
    : Math.max(0, request.stableBaselineScore - scorecard.regression_tolerance);
  const regressionPassed = candidateWinner !== null
    && (regressionFloor === null || candidateWinner.score >= regressionFloor);
  const winner = regressionPassed ? candidateWinner : null;
  const comparison = evaluateComparison(request.baselineComparison, winner?.score ?? null);
  return {
    schema: "dreamco.buddy_media_quality_evaluation.v1",
    projectId: request.projectId,
    status: winner ? "release_candidate_selected" : "no_release_candidate",
    modality: request.modality,
    fixtureSet: fixture,
    releaseThreshold: scorecard.release_threshold,
    stableBaselineScore: request.stableBaselineScore ?? null,
    regressionFloor,
    regressionPassed,
    winner,
    candidates: results,
    comparison,
    comparisonClaimAllowed: comparison?.claimAllowed ?? false,
    truthBoundary: catalog.truth_boundary,
    rawBiometricsInReport: false,
  } as const;
}

export function getMediaQualityLabCatalog() {
  return catalog;
}
