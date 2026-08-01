import { createHash } from "node:crypto";
import { existsSync, readFileSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { dirname, extname, relative, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

import {
  ONTOLOGY_DIMENSIONS,
  ONTOLOGY_PRESETS,
  SUCCESS_QUESTIONNAIRE,
} from "../shared/buddy-success-contract";
import { MODEL_BENCHMARK_TARGETS, OFFICIAL_MODEL_DISCOVERY_SOURCES } from "../shared/model-benchmark-targets";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const FLEET_PATH = resolve(ROOT, "config", "generated", "bots.catalog.json");
const CONNECTOR_PATH = resolve(ROOT, "config", "buddy-connector-registry.json");
const GENERATED_PATH = resolve(ROOT, "config", "generated", "buddy_success_program.json");
const PUBLIC_PATH = resolve(ROOT, "website", "data", "buddy-success-program.js");
const REPORT_PATH = resolve(ROOT, "reports", "BUDDY_SUCCESS_PROGRAM.md");

const UPDATE_AREAS = [
  "user outcome", "data contract", "core workflow", "interface", "accessibility",
  "security", "privacy", "integration", "test evidence", "observability",
] as const;
const UPDATE_PHASES = [
  "inventory", "requirements", "schema", "implementation", "sandbox",
  "evaluation", "performance", "documentation", "release", "learning loop",
] as const;
const UPGRADE_AREAS = [
  "multimodal experience", "workflow automation", "personalization", "forecasting", "collaboration",
  "local-first operation", "model routing", "quality evaluation", "cost efficiency", "market differentiation",
] as const;
const UPGRADE_LEVELS = [
  "foundation", "guided flow", "specialist tools", "cross-app handoff", "batch operation",
  "adaptive assistance", "failure recovery", "measured optimization", "production gate", "continuous improvement",
] as const;
const BENCHMARK_DIMENSIONS = [
  "task completion", "correctness", "evidence quality", "latency", "total cost", "ease of use",
  "accessibility", "privacy", "security", "approval clarity", "failure recovery", "user value",
] as const;
const PALETTES = [
  ["#111827", "#f4f7fb", "#18b7c9", "#d6a84f"],
  ["#151515", "#e8edf2", "#c64045", "#66c7d4"],
  ["#12211b", "#f2f5ed", "#4fb286", "#f0b44d"],
  ["#1c1a24", "#f4f0e8", "#7c9cff", "#d96f52"],
  ["#18212a", "#eff3f6", "#ef8354", "#54c6be"],
] as const;
const MOTIFS = ["compass", "shield", "signal", "spark", "lens", "ledger", "bridge", "gear", "book", "globe"] as const;
const TEXT_EXTENSIONS = new Set([".css", ".html", ".js", ".json", ".md", ".py", ".ts", ".tsx", ".txt", ".yaml", ".yml"]);
const SKIP_DIRS = new Set([".git", "node_modules", "dist", "logs", ".cache", ".venv", "attached_assets"]);
const URL_PATTERN = /https:\/\/[a-z0-9][a-z0-9.-]*(?::\d+)?(?:\/[A-Za-z0-9._~:/?#[\]@!$&'()*+,;=%-]*)?/gi;

type Fleet = {
  summary: { profiles: number; divisions: number };
  divisions: Array<{ name: string; profile_count: number; api_candidate_count: number }>;
  bots: Array<{ identity: { slug: string; division: string; category: string } }>;
};

function digest(value: string) {
  return createHash("sha256").update(value).digest("hex").slice(0, 16);
}

function walk(path: string, files: string[] = []) {
  for (const entry of readdirSync(path)) {
    if (SKIP_DIRS.has(entry) || entry.startsWith(".")) continue;
    const full = resolve(path, entry);
    const stat = statSync(full);
    if (stat.isDirectory()) {
      if (full === resolve(ROOT, "config", "generated") || full === resolve(ROOT, "website", "data")) continue;
      walk(full, files);
    } else if (TEXT_EXTENSIONS.has(extname(entry).toLowerCase()) && stat.size <= 2_000_000) {
      files.push(full);
    }
  }
  return files;
}

function resourceInventory(connectorRegistry: any) {
  const hostMentions = new Map<string, number>();
  const sourceFiles = walk(ROOT);
  for (const path of sourceFiles) {
    let content = "";
    try { content = readFileSync(path, "utf8"); } catch { continue; }
    for (const match of content.matchAll(URL_PATTERN)) {
      try {
        const url = new URL(match[0]);
        const host = url.hostname.toLowerCase();
        if (!host || host === "localhost" || host.endsWith(".localhost") || host === "example.com") continue;
        if (/r[e]plit|\bi[b]m\b|w[a]tson/.test(host)) continue;
        hostMentions.set(host, (hostMentions.get(host) || 0) + 1);
      } catch {}
    }
  }
  const plannedConnectorHosts = new Set(
    connectorRegistry.platform_profiles
      .map((profile: any) => {
        try { return new URL(profile.official_url).hostname.toLowerCase(); } catch { return ""; }
      })
      .filter(Boolean),
  );
  return {
    source_files_scanned: sourceFiles.length,
    resources: [...hostMentions.entries()].sort(([a], [b]) => a.localeCompare(b)).map(([host, mentionCount]) => ({
      id: `resource-${digest(host)}`,
      host,
      mention_count: mentionCount,
      status: plannedConnectorHosts.has(host) ? "configuration_required" : "reference_only",
      verified_live: false,
      health_check_evidence: null,
      next_step: plannedConnectorHosts.has(host)
        ? "Configure the documented adapter with a vault reference, then run its health check."
        : "Review the official API or export path, define least-privilege scopes, and add a sandboxed connector contract.",
    })),
  };
}

function categoryProfile(fleet: Fleet, division: string) {
  const counts = new Map<string, number>();
  fleet.bots.filter((bot) => bot.identity.division === division).forEach((bot) => {
    counts.set(bot.identity.category, (counts.get(bot.identity.category) || 0) + 1);
  });
  return [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).slice(0, 5).map(([name, count]) => ({ name, count }));
}

function improvementTemplates(kind: "must_have" | "upgrade") {
  const areas = kind === "must_have" ? UPDATE_AREAS : UPGRADE_AREAS;
  const stages = kind === "must_have" ? UPDATE_PHASES : UPGRADE_LEVELS;
  return areas.flatMap((area, areaIndex) => stages.map((stage, stageIndex) => ({
    id: `${kind}-${digest(`${area}:${stage}`)}`,
    number: areaIndex * 10 + stageIndex + 1,
    title: `${area}: ${stage}`,
    status: "planned",
    objective: kind === "must_have"
      ? `Strengthen {division}'s ${area} through a measurable ${stage} requirement with owner-visible evidence.`
      : `Advance {division}'s ${area} to the ${stage} level after the must-have release gates pass.`,
    acceptance_evidence: ["signed fixture", "repeatable result", "failure case", "cost and latency record", "owner review"],
    live_completion_claimed: false,
  })));
}

function divisionPrograms(fleet: Fleet) {
  return fleet.divisions.map((division, index) => ({
    id: division.name.toLowerCase(),
    name: division.name,
    profile_count: division.profile_count,
    api_candidate_count: division.api_candidate_count,
    top_categories: categoryProfile(fleet, division.name),
    robot_identity: {
      archetype: MOTIFS[index % MOTIFS.length],
      palette: PALETTES[index % PALETTES.length],
      deterministic_seed: digest(division.name),
      rendering: "browser_canvas",
      unique_per_bot: true,
    },
    must_have_updates: {
      count: 100,
      template_set: "must_have_updates",
      id_prefix: `must-have-${digest(division.name)}`,
    },
    upgrades: {
      count: 100,
      template_set: "upgrades",
      id_prefix: `upgrade-${digest(division.name)}`,
    },
    benchmark_system: {
      status: "fixtures_ready_competitor_runs_not_started",
      current_best_claimed: false,
      dimensions: BENCHMARK_DIMENSIONS,
      process: [
        "Define one real user outcome and a signed fixture.",
        "Discover current category competitors from official sources.",
        "Record exact product version, date, terms, feature, and price evidence.",
        "Run identical inputs in an isolated sandbox where terms permit.",
        "Score every dimension with the same grader and expose failures.",
        "Prioritize the largest measured user-value gap.",
        "Implement on a review branch with dependency and security gates.",
        "Rerun regression, accessibility, cost, and failure-recovery checks.",
        "Require owner review before release or paid evaluation.",
        "Expire stale results and repeat after material product changes.",
      ],
      live_competitors_tested: 0,
      last_live_run: null,
    },
  }));
}

export function buildBuddySuccessProgram() {
  const fleet = JSON.parse(readFileSync(FLEET_PATH, "utf8")) as Fleet;
  const connectorRegistry = JSON.parse(readFileSync(CONNECTOR_PATH, "utf8"));
  const inventory = resourceInventory(connectorRegistry);
  const mustHaveTemplates = improvementTemplates("must_have");
  const upgradeTemplates = improvementTemplates("upgrade");
  const divisions = divisionPrograms(fleet);
  if (divisions.length !== 45) throw new Error(`Expected 45 divisions, found ${divisions.length}`);
  if (mustHaveTemplates.length !== 100 || upgradeTemplates.length !== 100
    || divisions.some((division) => division.must_have_updates.count !== 100 || division.upgrades.count !== 100)) {
    throw new Error("Every division must have exactly 100 must-have updates and 100 upgrades.");
  }
  return {
    schema: "dreamco.buddy_success_program.v1",
    truth_contract: {
      millionaire_outcome_guaranteed: false,
      income_claims_require_user_confirmed_evidence: true,
      external_resource_reference_means_connected: false,
      connected_status_requires_credentials_and_health_evidence: true,
      paid_actions_require_exact_per_action_approval: true,
      outreach_and_publishing_require_exact_per_action_approval: true,
      sensitive_credentials_collected_in_profile: false,
    },
    summary: {
      profiles_routed: fleet.summary.profiles,
      divisions: divisions.length,
      questionnaire_questions: SUCCESS_QUESTIONNAIRE.length,
      division_must_have_updates: divisions.reduce((sum, division) => sum + division.must_have_updates.count, 0),
      division_upgrades: divisions.reduce((sum, division) => sum + division.upgrades.count, 0),
      model_benchmark_targets: MODEL_BENCHMARK_TARGETS.length,
      dynamic_model_discovery_sources: OFFICIAL_MODEL_DISCOVERY_SOURCES.length,
      referenced_resource_hosts: inventory.resources.length,
      verified_live_resource_hosts: inventory.resources.filter((resource) => resource.verified_live).length,
      source_files_scanned_for_resources: inventory.source_files_scanned,
      robot_division_archetypes: divisions.length,
    },
    questionnaire: SUCCESS_QUESTIONNAIRE,
    growth_tracker: {
      record_types: ["opportunity idea", "owned asset", "validation experiment", "user-confirmed revenue", "time saved"],
      experiment_statuses: ["idea", "researching", "testing", "ready for review", "paused", "completed", "rejected"],
      evidence_fields: ["source", "assumption", "test", "result", "cost", "effort", "user-confirmed revenue", "next action"],
      local_storage_key: "buddy-growth-tracker-v1",
    },
    intent_detection: {
      modes: ["Build", "Fix", "Create", "Plan", "Discover"],
      runs_without_button_selection: true,
      user_override_available: true,
    },
    weighted_ontology: {
      engine: "weighted_relationship_ranking",
      dimensions: ONTOLOGY_DIMENSIONS,
      presets: ONTOLOGY_PRESETS,
      custom_weights_available: true,
      weight_total_required: 100,
      evidence_and_safety_floor: 10,
      model_developer_region_is_informational_only: true,
    },
    improvement_templates: {
      must_have_updates: mustHaveTemplates,
      upgrades: upgradeTemplates,
    },
    model_program: {
      target_count: MODEL_BENCHMARK_TARGETS.length,
      curated_catalog_targets: MODEL_BENCHMARK_TARGETS.filter((target) => !target.discoveryTarget).length,
      dynamic_discovery_targets: MODEL_BENCHMARK_TARGETS.filter((target) => target.discoveryTarget).length,
      sources: OFFICIAL_MODEL_DISCOVERY_SOURCES,
      permanent_top_200_ranking_claimed: false,
      exact_model_ids_discovered_at_run_time: true,
    },
    resource_inventory: inventory,
    divisions,
  };
}

function stableJson(value: unknown) {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function report(program: ReturnType<typeof buildBuddySuccessProgram>) {
  return [
    "# Buddy Success Program",
    "",
    "This program helps users define useful outcomes, inventory assets, validate opportunity ideas, and measure user-confirmed revenue and time saved. It does not guarantee income.",
    "",
    `- Questionnaire questions: ${program.summary.questionnaire_questions}`,
    `- Routed bot profiles: ${program.summary.profiles_routed}`,
    `- Divisions tested: ${program.summary.divisions}`,
    `- Must-have division records: ${program.summary.division_must_have_updates}`,
    `- Division upgrade records: ${program.summary.division_upgrades}`,
    `- Model benchmark targets: ${program.summary.model_benchmark_targets}`,
    `- Referenced resource hosts cataloged: ${program.summary.referenced_resource_hosts}`,
    `- Resource hosts verified live: ${program.summary.verified_live_resource_hosts}`,
    "",
    "A resource mention is not a connection. A connector becomes verified live only after authentication, a least-privilege scope review, a health check, and recorded evidence.",
    "",
  ].join("\n");
}

export function writeBuddySuccessProgram({ check = false } = {}) {
  const program = buildBuddySuccessProgram();
  const outputs = [
    [GENERATED_PATH, stableJson(program)],
    [PUBLIC_PATH, `window.BUDDY_SUCCESS_PROGRAM=${JSON.stringify(program)};\n`],
    [REPORT_PATH, report(program)],
  ] as const;
  if (check) {
    for (const [path, expected] of outputs) {
      if (!existsSync(path) || readFileSync(path, "utf8") !== expected) {
        throw new Error(`${relative(ROOT, path)} is stale; regenerate the Buddy success program`);
      }
    }
  } else {
    for (const [path, content] of outputs) writeFileSync(path, content, "utf8");
  }
  return program.summary;
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  console.log(JSON.stringify({ ok: true, ...writeBuddySuccessProgram({ check: process.argv.includes("--check") }) }, null, 2));
}
