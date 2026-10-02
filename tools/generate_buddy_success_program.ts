import { createHash } from "node:crypto";
import { existsSync, readFileSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { dirname, extname, relative, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

import {
  ONTOLOGY_DIMENSIONS,
  ONTOLOGY_PRESETS,
  SUCCESS_QUESTIONNAIRE,
} from "../shared/buddy-success-contract";
import {
  DAILY_BENCHMARK_WORKER_ROLES,
  DIVISION_CAPABILITY_OPERATIONS,
  DIVISION_DOMAIN_PROFILES,
  OFFICIAL_AI_ALLIANCE_WATCH,
  PRODUCTION_READINESS_GATES,
  SAFE_AI_TRAINING_CONTRACT,
  UNIVERSAL_CONNECTOR_LIFECYCLE,
} from "../shared/division-production-contract";
import { MODEL_BENCHMARK_TARGETS, OFFICIAL_MODEL_DISCOVERY_SOURCES } from "../shared/model-benchmark-targets";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const FLEET_PATH = resolve(ROOT, "config", "generated", "bots.catalog.json");
const CONNECTOR_PATH = resolve(ROOT, "config", "buddy-connector-registry.json");
const GENERATED_PATH = resolve(ROOT, "config", "generated", "buddy_success_program.json");
const ORGANIZATION_INTELLIGENCE_PATH = resolve(ROOT, "config", "generated", "ai_organization_intelligence.json");
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
const SKIP_DIRS = new Set([
  ".git",
  ".cache",
  ".venv",
  "attached_assets",
  "dist",
  "logs",
  "node_modules",
  "playwright-report",
  "reports",
  "test-results",
  "tmp",
]);
const SKIP_FILES = new Set(["package-lock.json"]);
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
    if (SKIP_DIRS.has(entry) || SKIP_FILES.has(entry) || entry.startsWith(".")) continue;
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

function capabilityTemplates() {
  return Array.from({ length: 10 }, (_, focusIndex) => DIVISION_CAPABILITY_OPERATIONS.map((operation, operationIndex) => ({
    id: `capability-${focusIndex + 1}-${operation.id}`,
    number: focusIndex * DIVISION_CAPABILITY_OPERATIONS.length + operationIndex + 1,
    focus_index: focusIndex,
    operation: operation.id,
    title: `{focus}: ${operation.title}`,
    description: operation.description,
    evidence_required: ["signed fixture", "expected output", "failure case", "quality score", "owner-visible result"],
    production_claimed: false,
  }))).flat();
}

function divisionFocuses(fleet: Fleet, divisionName: string) {
  const profile = DIVISION_DOMAIN_PROFILES[divisionName];
  if (!profile) throw new Error(`Missing professional domain profile for ${divisionName}`);
  const categoryNames = categoryProfile(fleet, divisionName).map((category) => category.name.replaceAll("-", " "));
  const fallbacks = ["user experience", "evidence management", "workflow reliability", "cost control", "continuous learning"];
  return [...new Set([...profile.focusAreas, ...categoryNames, ...fallbacks])].slice(0, 10);
}

function divisionPrograms(fleet: Fleet) {
  return fleet.divisions.map((division, index) => {
    const domain = DIVISION_DOMAIN_PROFILES[division.name];
    if (!domain) throw new Error(`Missing professional domain profile for ${division.name}`);
    const focuses = divisionFocuses(fleet, division.name);
    if (focuses.length !== 10) throw new Error(`${division.name} must resolve to exactly 10 capability focuses`);
    return {
      id: division.name.toLowerCase(),
      name: division.name,
      profile_count: division.profile_count,
      api_candidate_count: division.api_candidate_count,
      top_categories: categoryProfile(fleet, division.name),
      charter: {
      purpose: domain.purpose,
      serves: domain.serves,
      intended_outcome: domain.outcome,
      professional_boundary: domain.boundary,
      what_it_does: [
        "discovers and defines authorized work",
        "plans and builds reviewable artifacts",
        "tests work in a bounded sandbox",
        "routes specialized bot profiles",
        "measures quality, cost, safety, and user value",
      ],
      what_it_does_not_do: [
        "guarantee income or outcomes",
        "claim professional authority it does not have",
        "use credentials or personal data without authorization",
        "take consequential external action without the required approval",
      ],
      },
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
      capabilities: {
      count: 100,
      template_set: "division_capabilities",
      id_prefix: `capability-${digest(division.name)}`,
      focuses,
      },
      production_readiness: {
      production_ready: false,
      repository_contract_status: "implemented_and_tested",
      external_runtime_status: "deployment_and_evidence_required",
      gates: PRODUCTION_READINESS_GATES.map((name, gateIndex) => ({
        id: `gate-${gateIndex + 1}`,
        name,
        status: "evidence_required",
      })),
      release_rule: "Every gate must have current evidence before this division may be labeled production ready.",
      false_readiness_claims_blocked: true,
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
      daily_operations: {
        logical_parallel_worker_slots: DAILY_BENCHMARK_WORKER_ROLES.length,
        worker_roles: DAILY_BENCHMARK_WORKER_ROLES,
        division_profile_pool: division.profile_count,
        daily_signed_fixture_target: 10,
        scheduler_status: "local_or_deployed_scheduler_required",
        live_runtime_processes_claimed: 0,
        external_network_default: "off",
        paid_runs_default: "off",
        release_authority: "owner_review_required",
      },
      },
    };
  });
}

export function buildBuddySuccessProgram() {
  const fleet = JSON.parse(readFileSync(FLEET_PATH, "utf8")) as Fleet;
  const connectorRegistry = JSON.parse(readFileSync(CONNECTOR_PATH, "utf8"));
  const organizationIntelligence = JSON.parse(readFileSync(ORGANIZATION_INTELLIGENCE_PATH, "utf8"));
  const inventory = resourceInventory(connectorRegistry);
  const mustHaveTemplates = improvementTemplates("must_have");
  const upgradeTemplates = improvementTemplates("upgrade");
  const divisionCapabilityTemplates = capabilityTemplates();
  const divisions = divisionPrograms(fleet);
  if (divisions.length !== 45) throw new Error(`Expected 45 divisions, found ${divisions.length}`);
  if (mustHaveTemplates.length !== 100 || upgradeTemplates.length !== 100 || divisionCapabilityTemplates.length !== 100
    || divisions.some((division) => division.must_have_updates.count !== 100 || division.upgrades.count !== 100 || division.capabilities.count !== 100)) {
    throw new Error("Every division must have exactly 100 must-have updates, 100 upgrades, and 100 capabilities.");
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
      division_capabilities: divisions.reduce((sum, division) => sum + division.capabilities.count, 0),
      daily_logical_benchmark_slots: divisions.reduce((sum, division) => sum + division.benchmark_system.daily_operations.logical_parallel_worker_slots, 0),
      production_ready_divisions: divisions.filter((division) => division.production_readiness.production_ready).length,
      model_benchmark_targets: MODEL_BENCHMARK_TARGETS.length,
      ai_organization_records: organizationIntelligence.summary.organizationRecords,
      alliance_directory_members: organizationIntelligence.summary.allianceMembers,
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
      division_capabilities: divisionCapabilityTemplates,
    },
    daily_benchmark_operations: {
      divisions: divisions.length,
      logical_parallel_worker_slots: divisions.reduce((sum, division) => sum + division.benchmark_system.daily_operations.logical_parallel_worker_slots, 0),
      daily_signed_fixture_target: divisions.reduce((sum, division) => sum + division.benchmark_system.daily_operations.daily_signed_fixture_target, 0),
      runtime_status: "scheduler_required",
      worker_processes_online_claimed: 0,
      local_first: true,
      network_default: "off",
      paid_runs_default: "off",
      never_self_release: true,
    },
    open_ai_alliance_watch: {
      ...OFFICIAL_AI_ALLIANCE_WATCH,
      directorySnapshot: {
        date: organizationIntelligence.snapshotDate,
        records: organizationIntelligence.summary.allianceMembers,
        matchedExistingProviders: organizationIntelligence.summary.allianceMembersMatchedToExistingProviders,
        generatedRegistry: "config/generated/ai_organization_intelligence.json",
      },
    },
    safe_ai_training: SAFE_AI_TRAINING_CONTRACT,
    trust_and_access: {
      zero_breach_or_fraud_guaranteed: false,
      raw_credentials_accepted: false,
      credential_handling: "vault_reference_only",
      preferred_identity: ["passkey", "OAuth PKCE", "short-lived service identity"],
      universal_connector_lifecycle: UNIVERSAL_CONNECTOR_LIFECYCLE,
      universal_control_claimed: false,
      connector_health_and_scope_evidence_required: true,
    },
    model_program: {
      target_count: MODEL_BENCHMARK_TARGETS.length,
      curated_catalog_targets: MODEL_BENCHMARK_TARGETS.filter((target) => !target.discoveryTarget).length,
      dynamic_discovery_targets: MODEL_BENCHMARK_TARGETS.filter((target) => target.discoveryTarget).length,
      sources: OFFICIAL_MODEL_DISCOVERY_SOURCES,
      permanent_best_model_ranking_claimed: false,
      exact_model_ids_discovered_at_run_time: true,
    },
    organization_intelligence: {
      existing_benchmark_targets: organizationIntelligence.summary.existingBenchmarkTargets,
      existing_providers: organizationIntelligence.summary.existingProviders,
      alliance_members: organizationIntelligence.summary.allianceMembers,
      organization_records: organizationIntelligence.summary.organizationRecords,
      user_need_categories: organizationIntelligence.summary.userNeedCategories,
      benchmark_dimensions: organizationIntelligence.summary.benchmarkDimensions,
      live_benchmarks_completed: 0,
      static_site_accepts_raw_keys: false,
      secure_key_intake: "authenticated_loopback_to_macos_keychain",
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
    `- Division capability records: ${program.summary.division_capabilities}`,
    `- Logical daily benchmark worker slots: ${program.summary.daily_logical_benchmark_slots}`,
    `- Divisions with complete production evidence: ${program.summary.production_ready_divisions}`,
    `- Model benchmark targets: ${program.summary.model_benchmark_targets}`,
    `- Referenced resource hosts cataloged: ${program.summary.referenced_resource_hosts}`,
    `- Resource hosts verified live: ${program.summary.verified_live_resource_hosts}`,
    "",
    "A resource mention is not a connection. A connector becomes verified live only after authentication, a least-privilege scope review, a health check, and recorded evidence.",
    "Logical benchmark workers are governed work slots, not claims that background processes are online. A scheduler and compute runtime must be deployed before daily runs occur.",
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
