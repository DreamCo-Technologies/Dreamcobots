import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { z } from "zod";

type LocalMediaCatalog = {
  schema: string;
  reviewed_on: string;
  policy: Record<string, unknown>;
  owned_stack: {
    identity: string;
    required_external_provider: null;
    components: string[];
  };
  benchmark_targets: Array<{
    id: string;
    label: string;
    kind: "owned_system" | "optional_local_reference" | "optional_external_reference";
    execution: string;
    required: boolean;
    paid: boolean;
    raw_media_upload_default: boolean;
    purpose: string;
  }>;
  engines: Array<{
    id: string;
    label: string;
    modalities: string[];
    runtime: string;
    source: string;
    license_status: string;
    commercial_status: string;
    identity_replication: boolean;
    watermark: string;
    readiness: string;
    best_for: string[];
    limitations: string[];
  }>;
  benchmark_suites: Array<{
    id: string;
    modality: string;
    metrics: string[];
    release_gate: string;
  }>;
  performance_modes?: Array<{ id: string; label: string; targets: string[] }>;
  performance_fixtures?: Array<{ id: string; mode: string; label: string; prompt: string; recommended_seconds: number }>;
};

const catalog = JSON.parse(
  readFileSync(resolve(process.cwd(), "config", "buddy-local-media-engines.json"), "utf8"),
) as LocalMediaCatalog;

const sha256Schema = z.string().regex(/^[a-f0-9]{64}$/i, "Use a SHA-256 reference, not raw media.");

export const mediaRightsSchema = z.object({
  sourceType: z.enum(["original_synthetic", "adult_owner", "licensed_adult_performer", "company_brand_asset"]),
  subjectReference: z.string().trim().min(3).max(120),
  sourceReferenceSha256: sha256Schema.optional(),
  consentReceiptReference: z.string().trim().min(3).max(180).optional(),
  rightsReceiptReference: z.string().trim().min(3).max(180).optional(),
  ownerIsSubject: z.boolean().default(false),
  adultConfirmed: z.boolean().default(false),
  voiceUseApproved: z.boolean().default(false),
  likenessUseApproved: z.boolean().default(false),
  commercialUseApproved: z.boolean().default(false),
  commercialScope: z.string().trim().min(3).max(500).optional(),
  syntheticMediaLabelApproved: z.literal(true),
  revoked: z.boolean().default(false),
}).strict();

export const mediaRenderPlanRequestSchema = z.object({
  projectId: z.string().trim().regex(/^[A-Za-z0-9_-]{3,80}$/),
  mediaType: z.enum(["speech_synthesis", "voice_replication", "rap_performance", "melodic_rap", "singing_voice_synthesis", "original_avatar", "identity_preserving_image", "portrait_animation", "lip_sync"]),
  objective: z.string().trim().min(10).max(4000),
  script: z.string().trim().max(12000).default(""),
  characterRole: z.string().trim().min(2).max(160).default("Buddy guide"),
  personalityTraits: z.record(z.string(), z.number().min(0).max(1)).default({ warmth: 0.8, clarity: 0.9 }),
  preferredEngineId: z.string().trim().max(80).optional(),
  performanceMode: z.enum(["spoken_conversation", "narration", "rap", "melodic_rap", "singing", "character_acting", "commercial_delivery", "multilingual_delivery"]).optional(),
  tempoBpm: z.number().int().min(40).max(240).optional(),
  musicalMaterialRightsConfirmed: z.boolean().default(false),
  commercialUse: z.boolean().default(false),
  rights: mediaRightsSchema,
}).strict();

export const mediaBenchmarkPlanRequestSchema = z.object({
  engineIds: z.array(z.string().trim().max(80)).max(8).default([]),
  targetIds: z.array(z.string().trim().max(80)).min(1).max(8).default(["buddy-media-core"]),
  modalities: z.array(z.enum(["voice", "image", "video", "all"])).min(1).max(4),
  commercialUse: z.boolean().default(false),
  ownerApprovedSyntheticFixturesOnly: z.literal(true),
  fixtureClass: z.enum(["synthetic", "owner_consented_media"]).default("synthetic"),
  ownerMediaComparisonConsentReceipt: z.string().trim().min(3).max(180).optional(),
  externalComparisonApproved: z.boolean().default(false),
  externalFixtureUploadApproved: z.boolean().default(false),
  paidComparisonApproved: z.boolean().default(false),
  maxRuntimeMinutes: z.number().int().min(1).max(240).default(30),
}).strict();

export type MediaRenderPlanRequest = z.infer<typeof mediaRenderPlanRequestSchema>;

function validateRights(request: MediaRenderPlanRequest): void {
  const { rights, mediaType } = request;
  const musicalVoice = ["rap_performance", "melodic_rap", "singing_voice_synthesis"].includes(mediaType);
  if (musicalVoice && !request.musicalMaterialRightsConfirmed) {
    throw new Error("Rap and singing plans require original or licensed lyrics, melody, and backing-track confirmation.");
  }
  if (rights.revoked) throw new Error("Consent or media rights have been revoked.");
  if (request.commercialUse && (!rights.commercialUseApproved || !rights.commercialScope)) {
    throw new Error("Commercial media requires explicit approval and a written usage scope.");
  }
  if (rights.sourceType === "original_synthetic") {
    if (["voice_replication", "identity_preserving_image", "portrait_animation", "lip_sync"].includes(mediaType)) {
      throw new Error("Real-person replication needs an adult owner or licensed adult performer source.");
    }
    return;
  }
  if (rights.sourceType === "company_brand_asset") {
    if (!["original_avatar"].includes(mediaType)) {
      throw new Error("A company brand asset cannot authorize biometric voice or likeness replication.");
    }
    if (!rights.rightsReceiptReference) throw new Error("A company asset rights receipt is required.");
    return;
  }
  if (!rights.adultConfirmed) throw new Error("Voice and likeness replication is not available for minors.");
  if (!rights.sourceReferenceSha256) throw new Error("A hashed local source reference is required.");
  if (!rights.consentReceiptReference) throw new Error("Active scoped consent evidence is required.");
  if (rights.sourceType === "adult_owner" && !rights.ownerIsSubject) {
    throw new Error("Adult owner media must belong to the signed-in owner.");
  }
  if (rights.sourceType === "licensed_adult_performer" && !rights.rightsReceiptReference) {
    throw new Error("Licensed performer media requires a written rights receipt.");
  }
  if (["voice_replication", "speech_synthesis", "rap_performance", "melodic_rap", "singing_voice_synthesis"].includes(mediaType) && !rights.voiceUseApproved) {
    throw new Error("Explicit voice-use consent is required.");
  }
  if (["identity_preserving_image", "portrait_animation", "lip_sync"].includes(mediaType) && !rights.likenessUseApproved) {
    throw new Error("Explicit likeness-use consent is required.");
  }
}

function compatibleEngines(request: MediaRenderPlanRequest) {
  return catalog.engines.filter((engine) => engine.modalities.includes(request.mediaType));
}

export function buildMediaRenderPlan(request: MediaRenderPlanRequest) {
  validateRights(request);
  const compatible = compatibleEngines(request);
  const selected = request.preferredEngineId
    ? compatible.find((engine) => engine.id === request.preferredEngineId)
    : compatible.find((engine) => !request.commercialUse || engine.commercial_status.startsWith("eligible"));
  if (!selected) throw new Error("No compatible local media engine is registered for this request.");
  if (request.commercialUse && !selected.commercial_status.startsWith("eligible")) {
    throw new Error(`${selected.label} is not cleared for commercial output.`);
  }
  const productionReady = selected.readiness === "local_prototype_ready"
    || selected.readiness === "available_when_browser_supports_speech_synthesis";
  return {
    schema: "dreamco.buddy_media_render_plan.v1",
    projectId: request.projectId,
    status: productionReady ? "local_preview_ready" : "local_model_install_and_benchmark_required",
    selectedEngine: selected,
    alternatives: compatible.filter((engine) => engine.id !== selected.id),
    character: {
      role: request.characterRole,
      personalityTraits: request.personalityTraits,
      identityMode: request.rights.sourceType,
      performanceMode: request.performanceMode ?? null,
      tempoBpm: request.tempoBpm ?? null,
      musicalMaterialRightsConfirmed: request.musicalMaterialRightsConfirmed,
    },
    rights: {
      sourceType: request.rights.sourceType,
      consentReceiptReference: request.rights.consentReceiptReference ?? null,
      rightsReceiptReference: request.rights.rightsReceiptReference ?? null,
      sourceReferenceSha256: request.rights.sourceReferenceSha256 ?? null,
      rawMediaAcceptedByThisRoute: false,
      syntheticMediaLabelRequired: true,
      revocationCheckRequiredAtRenderAndExport: true,
      commercialUseApproved: request.rights.commercialUseApproved,
      commercialScope: request.rights.commercialScope ?? null,
    },
    execution: {
      renderExecuted: false,
      networkDefault: "off",
      paidProviderRequired: false,
      nextGate: productionReady ? "local_preview_and_owner_review" : "install_local_model_then_run_benchmarks",
    },
    requiredEvidence: [
      "installed code, model, and dependency versions",
      "license manifest for the exact installed artifacts",
      "consent active at render and export",
      "synthetic-media label and provenance manifest",
      "quality benchmark results for the target device",
      "owner review of the generated identity and performance",
    ],
  };
}

export function buildMediaBenchmarkPlan(request: z.infer<typeof mediaBenchmarkPlanRequestSchema>) {
  const engines = request.engineIds.map((id) => catalog.engines.find((engine) => engine.id === id));
  if (engines.some((engine) => !engine)) throw new Error("Every benchmark engine must exist in the local media catalog.");
  const targets = request.targetIds.map((id) => catalog.benchmark_targets.find((target) => target.id === id));
  if (targets.some((target) => !target)) throw new Error("Every benchmark target must exist in the media comparison catalog.");
  const externalTargets = targets.filter((target) => target!.kind === "optional_external_reference");
  if (externalTargets.length && !request.externalComparisonApproved) {
    throw new Error("External benchmark targets require exact approval for this comparison.");
  }
  if (externalTargets.some((target) => target!.paid) && !request.paidComparisonApproved) {
    throw new Error("Paid benchmark targets require exact paid-use approval for this comparison.");
  }
  if (request.fixtureClass === "owner_consented_media") {
    if (!request.ownerMediaComparisonConsentReceipt) throw new Error("Owner media comparisons require an active consent receipt.");
    if (externalTargets.length && !request.externalFixtureUploadApproved) {
      throw new Error("Uploading owner media to an external benchmark requires separate exact approval.");
    }
  }
  if (request.commercialUse) {
    const blocked = engines.filter((engine) => !engine!.commercial_status.startsWith("eligible"));
    if (blocked.length) throw new Error(`Commercial benchmark includes uncleared engines: ${blocked.map((engine) => engine!.id).join(", ")}`);
  }
  const suites = catalog.benchmark_suites.filter((suite) => (
    suite.modality === "all"
    || request.modalities.includes("all")
    || request.modalities.includes(suite.modality as "voice" | "image" | "video")
  ));
  return {
    schema: "dreamco.buddy_media_benchmark_plan.v1",
    status: "sandbox_plan_ready",
    ownedStack: catalog.owned_stack,
    engines,
    targets,
    suites,
    fixtures: {
      source: request.fixtureClass,
      ownerMediaComparisonConsentReceipt: request.ownerMediaComparisonConsentReceipt ?? null,
      rawBiometricsInReport: false,
      signedTranscripts: true,
      deterministicSeedsWhereSupported: true,
      repeatedRunsPerFixture: 3,
    },
    limits: {
      maxRuntimeMinutes: request.maxRuntimeMinutes,
      networkDefault: "off",
      externalUploads: externalTargets.length ? "requires_fresh_execution_approval" : false,
      paidCalls: externalTargets.some((target) => target!.paid) ? "requires_fresh_execution_approval" : false,
    },
    resultState: "not_run",
    comparisonClaimAllowed: false,
    externalCallExecuted: false,
  };
}

export function getLocalMediaCatalog() {
  return catalog;
}
