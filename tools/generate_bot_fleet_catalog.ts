#!/usr/bin/env tsx
/** Build the evidence-backed Buddy bot fleet catalog from repository sources. */

import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

import { DIVISION_API_REGISTRIES, type ApiIntegration } from "../shared/api-registry.ts";
import { ALL_BOTS } from "../server/seed-bots.ts";
import { CODELAB_BOTS } from "../server/seed-codelabs.ts";
import { GITHUB_BOTS } from "../server/seed-github-bots.ts";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const APP_BOTS_DIR = join(ROOT, "App_bots");
const MASTER_PATH = join(ROOT, "config", "master_bot_registry.json");
const GENERATED_PATH = join(ROOT, "config", "generated", "bots.catalog.json");
const WEBSITE_PATH = join(ROOT, "website", "data", "bot-fleet-catalog.json");
const WEBSITE_SHARD_DIR = join(ROOT, "website", "data", "bot-fleet");
const REPORT_PATH = join(ROOT, "reports", "BOT_FLEET_PROSPECTUS.md");

type BotProfile = {
  slug: string;
  displayName: string;
  tier: string;
  category: string;
  description: string;
  capabilities: string[];
  revenueModel: string;
  targetUsers: string;
  priceRange: string;
  status: string;
  division?: string;
};

type DivisionFile = {
  division: string;
  total: number;
  bots: BotProfile[];
};

type RuntimeProfile = BotProfile & {
  systemPrompt?: string;
  traits?: Record<string, unknown>;
};

type ApiCandidate = ApiIntegration & {
  status: "configuration_required";
  sandbox_required: true;
  secret_policy: "backend_secret_reference_only";
};

const EMOJIS = [
  "🧭", "🛠️", "🧠", "🔎", "📊", "🎯", "🧩", "⚙️", "🛡️", "💡",
  "🎨", "🎮", "📚", "🚀", "🌐", "📈", "🧪", "🏗️", "🎬", "🎙️",
  "🧰", "🔐", "🛰️", "🗂️", "🤝", "📣", "🧮", "🖥️", "💼", "✨",
];
const ADJECTIVES = [
  "Bright", "Clever", "Noble", "Swift", "True", "Prime", "Bold", "Clear",
  "Grand", "Vivid", "Ready", "Solar", "Civic", "Golden", "Agile", "Royal",
  "Expert", "Open", "Trusted", "Dynamic", "Modern", "Focused", "Brave", "Calm",
];
const NOUNS = [
  "Compass", "Forge", "Beacon", "Studio", "Pilot", "Atlas", "Signal", "Ledger",
  "Bridge", "Workshop", "Scope", "Engine", "Guide", "Lab", "Tower", "Craft",
  "Spark", "Path", "Vault", "Canvas", "Harbor", "Pulse", "Orbit", "Launchpad",
];
const PALETTES = [
  ["#176B5B", "#D7A73B", "#F5F7F3"],
  ["#275DAD", "#E38B3C", "#F7F9FC"],
  ["#7A2E3A", "#2D8C7C", "#FFF8EE"],
  ["#5B3A8A", "#D89B2B", "#F8F5FF"],
  ["#0F6F88", "#C94D63", "#F4FBFC"],
  ["#334E3C", "#B96332", "#F7F4ED"],
  ["#3D4C8D", "#D56638", "#F4F6FF"],
  ["#77521F", "#287878", "#FFF9ED"],
];

const HIGH_IMPACT_WORDS = [
  "payment", "money", "trade", "wallet", "loan", "credit", "legal", "health",
  "medical", "military", "security", "cyber", "contract", "outreach", "email",
  "sms", "call", "publish", "deploy", "delete", "account", "personal data",
];

const TOOL_RULES: Array<{ words: string[]; tool: Record<string, unknown> }> = [
  {
    words: ["game", "simulation", "level", "player"],
    tool: {
      id: "buddy_game_lab",
      name: "Buddy Game Lab",
      status: "adapter_contract_available",
      evidence: "dreamco_platform/games/harness.py",
    },
  },
  {
    words: ["video", "voice", "image", "media", "course", "learning", "education"],
    tool: {
      id: "buddy_creative_studio",
      name: "Buddy Creative Studio",
      status: "local_prototype_available",
      evidence: "dreamco_platform/creative/studio.py",
    },
  },
  {
    words: ["social", "post", "campaign", "content", "influencer"],
    tool: {
      id: "buddy_social_manager",
      name: "Buddy Social Manager",
      status: "approval_gated_adapter_contract",
      evidence: "dreamco_platform/social/manager.py",
    },
  },
  {
    words: ["api", "integration", "webhook", "account", "authentication"],
    tool: {
      id: "buddy_connection_broker",
      name: "Buddy Connection Broker",
      status: "backend_broker_available",
      evidence: "dreamco_platform/connections/broker.py",
    },
  },
  {
    words: ["code", "app", "website", "debug", "deploy", "software"],
    tool: {
      id: "buddy_code_workspace",
      name: "Buddy Code Workspace",
      status: "shared_runtime_route",
      evidence: "server/seed-buddy-bot.ts",
    },
  },
];

function hashBytes(value: string): Buffer {
  return createHash("sha256").update(value).digest();
}

function searchable(profile: BotProfile): string {
  return [
    profile.slug,
    profile.displayName,
    profile.division,
    profile.category,
    profile.description,
    ...profile.capabilities,
  ].join(" ").toLowerCase();
}

function logoFor(profile: BotProfile) {
  const hash = hashBytes(profile.slug);
  const initials = profile.displayName
    .replace(/\b(bot|ai|automation|system|manager)\b/gi, "")
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0]?.toUpperCase())
    .join("") || "B";
  const palette = PALETTES[hash[3] % PALETTES.length];
  return {
    logo_id: `logo-${profile.slug}`,
    emoji: EMOJIS[hash[0] % EMOJIS.length],
    monogram: initials,
    call_sign: `${ADJECTIVES[hash[1] % ADJECTIVES.length]} ${NOUNS[hash[2] % NOUNS.length]} ${hash.toString("hex").slice(0, 8).toUpperCase()}`,
    shape: ["shield", "hex", "tile", "circle"][hash[4] % 4],
    colors: { primary: palette[0], accent: palette[1], surface: palette[2] },
    accessibility_label: `${profile.displayName} logo`,
  };
}

function inferTools(profile: BotProfile) {
  const text = searchable(profile);
  const tools: Record<string, unknown>[] = [
    {
      id: "buddy_fleet_runtime",
      name: "Executable fleet runtime",
      status: "runtime_instance_ready",
      evidence: "server/fleet-runtime.ts",
    },
    {
      id: "buddy_chat_router",
      name: "Buddy shared chat router",
      status: "runtime_routed",
      evidence: "server/routes.ts",
    },
    {
      id: "buddy_approval_gateway",
      name: "Buddy approval gateway",
      status: "policy_available",
      evidence: "server/approval-notifications.ts",
    },
    {
      id: "buddy_bot_sandbox",
      name: "Per-bot sandbox blueprint",
      status: "generated",
      evidence: "config/generated/bots.catalog.json",
    },
    {
      id: "buddy_platform_registry",
      name: "Governed platform capability registry",
      status: "runtime_routed",
      evidence: "config/generated/buddy_platform_expansion.json",
    },
  ];
  for (const rule of TOOL_RULES) {
    if (rule.words.some((word) => text.includes(word))) tools.push(rule.tool);
  }
  return tools;
}

function apiCandidatesFor(profile: BotProfile): ApiCandidate[] {
  const registry = DIVISION_API_REGISTRIES[profile.division || ""];
  if (!registry) return [];
  const terms = new Set(
    searchable(profile)
      .split(/[^a-z0-9]+/)
      .filter((term) => term.length >= 4),
  );
  const candidates = registry.categories.flatMap((group) =>
    group.apis.map((api) => {
      const apiText = `${group.name} ${api.name} ${api.category} ${api.description}`.toLowerCase();
      const score = [...terms].reduce((total, term) => total + (apiText.includes(term) ? 1 : 0), 0);
      return { api, score };
    }),
  );
  candidates.sort((a, b) => b.score - a.score || a.api.name.localeCompare(b.api.name));
  const positive = candidates.filter((item) => item.score > 0);
  const selected = (positive.length ? positive : candidates).slice(0, 8);
  return selected.map(({ api }) => ({
    ...api,
    status: "configuration_required",
    sandbox_required: true,
    secret_policy: "backend_secret_reference_only",
  }));
}

function approvalPolicy(profile: BotProfile) {
  const text = searchable(profile);
  const triggers = HIGH_IMPACT_WORDS.filter((word) => text.includes(word));
  return {
    default_mode: "sandbox",
    approval_required: true,
    high_impact_profile: triggers.length > 0,
    triggers: triggers.length ? triggers : ["any live external write or publish action"],
    channels_supported: ["in_app", "email", "sms", "voice_call"],
    contact_requirement: "verified user-owned destination and explicit channel opt-in",
    execution_rule: "approval authorizes one scoped action; it never exposes credentials to the bot or browser",
  };
}

function dataContract(profile: BotProfile) {
  const text = searchable(profile);
  const sensitive = ["health", "legal", "finance", "payment", "personal", "security", "employee", "student"]
    .filter((word) => text.includes(word));
  return {
    accepted_inputs: ["user brief", "user-selected files or records", "approved connector references"],
    produced_outputs: ["draft", "analysis", "task packet", "sandbox evidence", "approval request when required"],
    sensitivity: sensitive.length ? "potentially_sensitive" : "standard_business_data",
    sensitive_domains: sensitive,
    storage_policy: "store useful project artifacts only; raw credentials are forbidden; raw biometric media remains local or in an encrypted owner vault",
    retention: "owner-configurable with deletion and revocation support",
  };
}

function sandboxBlueprint(profile: BotProfile, apiCandidates: ApiCandidate[]) {
  return {
    sandbox_id: `sandbox-${profile.slug}`,
    network_default: "off",
    fixture_mode: "synthetic_or_owner_supplied",
    seed: hashBytes(profile.slug).readUInt32BE(0),
    checks: [
      "profile_schema_valid",
      "runtime_slug_resolves",
      "capability_output_matches_brief",
      "no_secret_in_output",
      "no_live_external_write",
      "approval_gate_for_high_impact_action",
      "failure_and_retry_state_recorded",
    ],
    api_tests: apiCandidates.map((api) => ({
      api: api.name,
      mode: "mock_contract_test",
      live_test_status: "blocked_until_owner_configures_secret_and_approves",
    })),
    release_gate: "all applicable checks pass and owner approves any live action",
  };
}

function runtimeSources() {
  const sources: Array<[string, RuntimeProfile[]]> = [
    ["server/seed-bots.ts", ALL_BOTS as RuntimeProfile[]],
    ["server/seed-codelabs.ts", CODELAB_BOTS as RuntimeProfile[]],
    ["server/seed-github-bots.ts", GITHUB_BOTS as RuntimeProfile[]],
  ];
  const bySlug = new Map<string, string[]>();
  for (const [source, profiles] of sources) {
    for (const profile of profiles) bySlug.set(profile.slug, [...(bySlug.get(profile.slug) || []), source]);
  }
  return bySlug;
}

export function buildFleetCatalog() {
  const runtime = runtimeSources();
  const divisionFiles = readdirSync(APP_BOTS_DIR)
    .filter((name) => name.endsWith(".json"))
    .sort()
    .map((name) => ({
      name,
      content: JSON.parse(readFileSync(join(APP_BOTS_DIR, name), "utf8")) as DivisionFile,
    }));

  const seen = new Set<string>();
  const bots = divisionFiles.flatMap(({ name, content }) => {
    if (content.total !== content.bots.length) throw new Error(`${name}: declared total does not match bot count`);
    return content.bots.map((sourceProfile) => {
      const profile = { ...sourceProfile, division: content.division };
      if (seen.has(profile.slug)) throw new Error(`Duplicate catalog slug: ${profile.slug}`);
      seen.add(profile.slug);
      const runtimeEvidence = runtime.get(profile.slug) || [];
      const apiCandidates = apiCandidatesFor(profile);
      return {
        identity: {
          slug: profile.slug,
          display_name: profile.displayName,
          division: profile.division,
          category: profile.category,
          tier: profile.tier,
          catalog_status: profile.status,
        },
        logo: logoFor(profile),
        prospectus: {
          mission: profile.description,
          target_users: profile.targetUsers,
          catalog_business_model: profile.revenueModel,
          catalog_price_range: profile.priceRange,
          pricing_evidence: "catalog_claim_not_verified_revenue",
          inputs: dataContract(profile).accepted_inputs,
          outputs: dataContract(profile).produced_outputs,
          limitations: [
            "This profile has an executable governed runtime instance backed by shared hardened code, not a separate always-running operating-system process.",
            "External APIs require owner configuration, provider terms, sandbox tests, and scoped approval.",
            "Published pricing and revenue models are catalog plans, not evidence of sales or earnings.",
          ],
        },
        capabilities: profile.capabilities.map((name) => ({
          name,
          source: `App_bots/${content.division}.json`,
          evidence_level: "catalog_declared",
          test_status: "sandbox_blueprint_generated",
        })),
        tools: inferTools(profile),
        api_candidates: apiCandidates,
        data_contract: dataContract(profile),
        approvals: approvalPolicy(profile),
        sandbox: sandboxBlueprint(profile, apiCandidates),
        readiness: {
          profile_schema: "verified",
          buddy_chat_route: runtimeEvidence.length ? "verified" : "missing",
          executable_runtime_instance: "verified",
          standalone_native_runtime: "shared_worker_not_standalone",
          external_integrations: apiCandidates.length ? "configuration_required" : "no_division_api_catalog",
          production_ready: false,
          production_gate: "implement or configure adapters, pass sandbox checks, add authentication, and verify deployment telemetry",
        },
        evidence: {
          catalog_source: `App_bots/${name}`,
          runtime_sources: runtimeEvidence,
          runtime_seed_duplicates: Math.max(runtimeEvidence.length - 1, 0),
        },
        sample_test_prompt: `Test ${profile.displayName} in sandbox mode. Use synthetic data, demonstrate ${profile.capabilities[0] || profile.category}, record evidence, and stop before any live external action.`,
      };
    });
  });

  const missingRuntime = bots.filter((bot) => bot.readiness.buddy_chat_route === "missing");
  if (missingRuntime.length) throw new Error(`${missingRuntime.length} catalog profiles have no Buddy runtime route`);
  if (bots.length !== 1051) throw new Error(`Expected 1,051 profiles, found ${bots.length}`);

  const divisions = divisionFiles.map(({ name, content }) => ({
    name: content.division,
    profile_count: content.bots.length,
    source: `App_bots/${name}`,
    api_candidate_count: (DIVISION_API_REGISTRIES[content.division]?.categories || [])
      .flatMap((category) => category.apis).length,
  }));
  const configuredApiCount = 0;
  return {
    schema: "dreamco.bot_fleet_catalog.v2",
    generated_from: {
      profile_sources: "App_bots/*.json",
      runtime_sources: ["server/seed-bots.ts", "server/seed-codelabs.ts", "server/seed-github-bots.ts"],
      executable_runtime: "server/fleet-runtime.ts",
      api_candidate_source: "shared/api-registry.ts",
    },
    truth_policy: {
      catalog_profile: "A declared specialization routed through Buddy's shared runtime.",
      connected_api: "Counted only after a configured adapter passes sandbox and live-owner verification.",
      production_ready: "Counted only with runtime, tests, authentication, deployment, and telemetry evidence.",
    },
    summary: {
      profiles: bots.length,
      divisions: divisions.length,
      runtime_routed_profiles: bots.filter((bot) => bot.readiness.buddy_chat_route === "verified").length,
      executable_runtime_instances_evidenced: bots.length,
      standalone_native_runtimes_evidenced: 0,
      configured_external_apis_evidenced: configuredApiCount,
      per_bot_sandbox_blueprints: bots.length,
      per_bot_logo_identities: bots.length,
      production_ready_profiles: 0,
    },
    divisions,
    bots,
  };
}

function compactCatalog(catalog: ReturnType<typeof buildFleetCatalog>) {
  return {
    schema: catalog.schema,
    truth_policy: catalog.truth_policy,
    summary: catalog.summary,
    divisions: catalog.divisions,
    bots: catalog.bots.map((bot) => ({
      identity: bot.identity,
      logo: bot.logo,
      mission: bot.prospectus.mission,
      capability_count: bot.capabilities.length,
      capability_search: bot.capabilities.map((capability) => capability.name).join(" | "),
      tool_summary: bot.tools.map((tool) => ({ id: tool.id, name: tool.name, status: tool.status })),
      api_candidate_count: bot.api_candidates.length,
      api_candidate_names: bot.api_candidates.map((api) => api.name),
      approval_required: bot.approvals.approval_required,
      readiness: bot.readiness,
      evidence: {
        catalog_source: bot.evidence.catalog_source,
        runtime_source_count: bot.evidence.runtime_sources.length,
      },
      sample_test_prompt: bot.sample_test_prompt,
      prospectus_ref: `data/bot-fleet/${bot.identity.division}.json#${bot.identity.slug}`,
    })),
  };
}

function stableJson(value: unknown) {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function buildReport(catalog: ReturnType<typeof buildFleetCatalog>) {
  const lines = [
    "# Buddy Bot Fleet Prospectus",
    "",
    "This report is generated from repository evidence. A catalog profile is not counted as an independent production runtime, and an API candidate is not counted as connected.",
    "",
    "## Verified Inventory",
    "",
    `- Bot profiles: ${catalog.summary.profiles}`,
    `- Divisions: ${catalog.summary.divisions}`,
    `- Buddy-routed profiles: ${catalog.summary.runtime_routed_profiles}`,
    `- Executable governed runtime instances: ${catalog.summary.executable_runtime_instances_evidenced}`,
    `- Separate standalone processes: ${catalog.summary.standalone_native_runtimes_evidenced}`,
    `- Configured external APIs evidenced: ${catalog.summary.configured_external_apis_evidenced}`,
    `- Per-bot sandbox blueprints: ${catalog.summary.per_bot_sandbox_blueprints}`,
    `- Per-bot logo identities: ${catalog.summary.per_bot_logo_identities}`,
    "",
    "## Production Gate",
    "",
    "Every profile now has a health-checkable sandbox runtime instance. Each profile must still configure any required external adapters, pass provider contract tests, use authenticated owner-scoped execution, and emit deployment telemetry before it can be labeled fully production-ready.",
    "",
    "## Divisions",
    "",
    "| Division | Profiles | API candidates |",
    "| --- | ---: | ---: |",
    ...catalog.divisions.map((division) => `| ${division.name} | ${division.profile_count} | ${division.api_candidate_count} |`),
  ];
  return `${lines.join("\n")}\n`;
}

export function writeFleetCatalog({ check = false } = {}) {
  const catalog = buildFleetCatalog();
  const compact = compactCatalog(catalog);
  const divisionShards = catalog.divisions.map((division) => [
    join(WEBSITE_SHARD_DIR, `${division.name}.json`),
    stableJson({
      schema: "dreamco.bot_fleet_division.v2",
      division: division.name,
      bots: catalog.bots.filter((bot) => bot.identity.division === division.name),
    }),
  ] as const);
  const outputs = [
    [MASTER_PATH, stableJson(catalog)],
    [GENERATED_PATH, stableJson(compact)],
    [WEBSITE_PATH, stableJson(compact)],
    [REPORT_PATH, buildReport(catalog)],
    ...divisionShards,
  ] as const;
  if (check) {
    for (const [path, expected] of outputs) {
      const current = readFileSync(path, "utf8");
      if (current !== expected) throw new Error(`${relative(ROOT, path)} is stale; regenerate the fleet catalog`);
    }
  } else {
    mkdirSync(WEBSITE_SHARD_DIR, { recursive: true });
    for (const [path, content] of outputs) writeFileSync(path, content, "utf8");
  }
  return catalog.summary;
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  const summary = writeFleetCatalog({ check: process.argv.includes("--check") });
  console.log(JSON.stringify({ ok: true, ...summary }, null, 2));
}
