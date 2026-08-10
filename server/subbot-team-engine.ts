import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { z } from "zod";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const REGISTRY_PATH = resolve(ROOT, "config", "dreamco-must-have-subbot-team.json");

const subBotBlueprintSchema = z.object({
  slug: z.string().min(2),
  name: z.string().min(2),
  purpose: z.string().min(10),
  features: z.array(z.string().min(2)).min(3),
});

const registrySchema = z.object({
  schema: z.string(),
  architecture: z.string(),
  global_master_preference: z.array(z.string()),
  default_lifecycle: z.string(),
  merge_rule: z.string(),
  spawn_rule: z.string(),
  data_rule: z.string(),
  bots: z.array(subBotBlueprintSchema).min(30),
});

export const subBotTeamRequestSchema = z.object({
  ownerBotSlug: z.string().trim().min(2).max(160),
  objective: z.string().trim().min(10).max(4_000),
  requestedRoles: z.array(z.string().trim().min(2).max(160)).max(12).default([]),
  maximumTeamSize: z.number().int().min(1).max(12).default(5),
  dataClasses: z.array(z.enum([
    "preferences", "projects", "notes", "documents", "images", "audio", "video",
    "app_exports", "business_records", "calendar", "contacts", "messages", "structured_data"
  ])).max(13).default([]),
  liveActionRequested: z.boolean().default(false),
}).strict();

export type SubBotTeamRequest = z.infer<typeof subBotTeamRequestSchema>;

type Blueprint = z.infer<typeof subBotBlueprintSchema>;

function normalize(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
}

function tokens(value: string) {
  return new Set(normalize(value).split(/\s+/).filter((token) => token.length >= 3));
}

function score(blueprint: Blueprint, objective: string, requestedRoles: string[]) {
  if (requestedRoles.includes(blueprint.slug) || requestedRoles.includes(blueprint.name)) return 10_000;
  const target = tokens(objective);
  const searchable = tokens(`${blueprint.slug} ${blueprint.name} ${blueprint.purpose} ${blueprint.features.join(" ")}`);
  let value = 0;
  for (const token of searchable) if (target.has(token)) value += 10;
  if (normalize(objective).includes(normalize(blueprint.name))) value += 500;
  return value;
}

export function loadSubBotRegistry() {
  return registrySchema.parse(JSON.parse(readFileSync(REGISTRY_PATH, "utf8")));
}

export function buildSubBotTeam(requestInput: SubBotTeamRequest) {
  const request = subBotTeamRequestSchema.parse(requestInput);
  const registry = loadSubBotRegistry();
  const ranked = registry.bots
    .map((blueprint) => ({ blueprint, score: score(blueprint, request.objective, request.requestedRoles) }))
    .sort((a, b) => b.score - a.score || a.blueprint.slug.localeCompare(b.blueprint.slug));

  const selected = ranked
    .filter((row, index) => row.score > 0 || index < Math.min(3, request.maximumTeamSize))
    .slice(0, request.maximumTeamSize)
    .map((row, index) => ({
      order: index + 1,
      slug: row.blueprint.slug,
      name: row.blueprint.name,
      purpose: row.blueprint.purpose,
      features: row.blueprint.features,
      activation: "task_scoped_subbot" as const,
      persistence: "ephemeral_unless_promoted_by_evidence" as const,
      score: row.score,
    }));

  const idMaterial = `${request.ownerBotSlug}:${request.objective}:${selected.map((row) => row.slug).join(",")}`;
  const teamId = `subbot-team-${createHash("sha256").update(idMaterial).digest("hex").slice(0, 18)}`;
  const dataRequested = request.dataClasses.length > 0;

  return {
    schema: "dreamco.subbot_team_plan.v1",
    teamId,
    ownerBotSlug: request.ownerBotSlug,
    objective: request.objective,
    lifecycle: registry.default_lifecycle,
    architecture: registry.architecture,
    members: selected,
    requestedDataClasses: request.dataClasses,
    dataPolicy: {
      rule: registry.data_rule,
      sourceRequirement: "user_owned_or_user_authorized_or_otherwise_permitted",
      readOnlyFirst: true,
      provenanceRequired: dataRequested,
      exportAndDeleteControlsRequired: dataRequested,
      sensitiveDataRequiresSpecificPurposeAndConsent: true,
    },
    mergePolicy: registry.merge_rule,
    promotionPolicy: registry.spawn_rule,
    liveActionStatus: request.liveActionRequested ? "approval_required" : "not_requested",
    externalActionTaken: false,
    evidenceRequired: [
      "owner_bot_resolved",
      "role_blueprints_resolved",
      "input_provenance_recorded_when_data_is_used",
      "sandbox_or_read_only_first",
      "results_linked_to_team_id",
      "temporary_team_destroy_or_archive_decision_recorded"
    ],
  } as const;
}
