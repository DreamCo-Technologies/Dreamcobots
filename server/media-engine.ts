import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { z } from "zod";

type LocalMediaCatalog = {
  schema: string;
  reviewed_on: string;
  policy: Record<string, unknown>;
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
  syntheticMediaLabelApproved: z.literal(true),
  revoked: z.boolean().default(false),
}).strict();

export const mediaRenderPlanRequestSchema = z.object({
  projectId: z.string().trim().regex(/^[A-Za-z0-9_-]{3,80}$/),
  mediaType: z.enum(["speech_synthesis", "voice_replication", "original_avatar", "identity_preserving_image", "portrait_animation", "lip_sync"]),
  objective: z.string().trim().min(10).max(4000),
  script: z.string().trim().max(12000).default(""),
  characterRole: z.string().trim().min(2).max(160).default("Buddy guide"),
  personalityTraits: z.record(z.number().min(0).max(1)).default({ warmth: 0.8, clarity: 0.9 }),
  preferredEngineId: z.string().trim().max(80).optional(),
  commercialUse: z.boolean().default(false),
  rights: mediaRightsSchema,
}).strict();

export const mediaBenchmarkPlanRequestSchema = z.object({
  engineIds: z.array(z.string().trim().max(80)).min(1).max(8),
  modalities: z.array(z.enum(["voice", "image", "video", "all"])).min(1).max(4),
  commercialUse: z.boolean().default(false),
  ownerApprovedSyntheticFixturesOnly: z.literal(true),
  maxRuntimeMinutes: z.number().int().min(1).max(240).default(30),
}).strict();

export type MediaRenderPlanRequest = z.infer<typeof mediaRenderPlanRequestSchema>;

function validateRights(request: MediaRenderPlanRequest): void {
  const { rights, mediaType } = request;
  if (rights.revoked) throw new Error("Consent or media rights have been revoked.");
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
  if (["voice_replication", "speech_synthesis"].includes(mediaType) && !rights.voiceUseApproved) {
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
    },
    rights: {
      sourceType: request.rights.sourceType,
      consentReceiptReference: request.rights.consentReceiptReference ?? null,
      rightsReceiptReference: request.rights.rightsReceiptReference ?? null,
      sourceReferenceSha256: request.rights.sourceReferenceSha256 ?? null,
      rawMediaAcceptedByThisRoute: false,
      syntheticMediaLabelRequired: true,
      revocationCheckRequiredAtRenderAndExport: true,
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
    engines,
    suites,
    fixtures: {
      source: "synthetic_or_owner_generated_with_active_consent",
      rawBiometricsInReport: false,
      signedTranscripts: true,
      deterministicSeedsWhereSupported: true,
      repeatedRunsPerFixture: 3,
    },
    limits: {
      maxRuntimeMinutes: request.maxRuntimeMinutes,
      networkDefault: "off",
      externalUploads: false,
      paidCalls: false,
    },
    resultState: "not_run",
    comparisonClaimAllowed: false,
  };
}

export function getLocalMediaCatalog() {
  return catalog;
}
