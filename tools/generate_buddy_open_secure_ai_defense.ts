import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

type CatalogRow = {
  id: string;
  label: string;
  official_source: string;
};

type DefenseCatalog = {
  schema: string;
  catalog_reviewed_on: string;
  stale_after_days: number;
  truth_contract: Record<string, boolean>;
  official_sources: Array<{ id: string; label: string; url: string; purpose: string }>;
  alliance_reference_tools: CatalogRow[];
  openssf_projects: CatalogRow[];
  threat_domains: Array<{ id: string; label: string; required_control: string }>;
  defense_pipeline: Array<{ id: string; label: string; evidence: string[] }>;
  model_discovery_sources: Array<CatalogRow & { connection_status: string }>;
  priority_open_model_watchlist_2026: CatalogRow[];
  github_profile_contract: Record<string, unknown>;
  open_source_upgrade_contract: Record<string, unknown>;
  product_profiles: Array<{ id: string; label: string; scope: string }>;
};

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const sourcePath = resolve(root, "config", "buddy-open-secure-ai-defense.json");
const generatedPath = resolve(root, "config", "generated", "buddy_open_secure_ai_defense.json");
const publicPath = resolve(root, "website", "data", "buddy-open-secure-ai-defense.js");
const allowedStatuses = new Set([
  "reference_available",
  "configuration_required",
  "format_supported",
  "provider_access_required",
  "membership_or_intake_required",
  "public_metadata_available",
  "local_runtime_required",
]);

function assertUnique(rows: CatalogRow[], label: string) {
  const ids = rows.map((row) => row.id);
  if (ids.some((id) => !/^[a-z][a-z0-9-]{1,79}$/.test(id))) {
    throw new Error(`${label} ids must use lowercase slugs.`);
  }
  if (ids.length !== new Set(ids).size) throw new Error(`${label} ids must be unique.`);
}

function assertOfficialHttps(rows: CatalogRow[], label: string) {
  for (const row of rows) {
    const url = new URL(row.official_source);
    if (url.protocol !== "https:" || url.username || url.password) {
      throw new Error(`${label} ${row.id} must use an official HTTPS source without credentials.`);
    }
  }
}

function validate(catalog: DefenseCatalog) {
  if (catalog.schema !== "dreamco.buddy_open_secure_ai_defense.v1") {
    throw new Error("Unsupported Buddy defense catalog schema.");
  }
  if (catalog.stale_after_days < 1 || catalog.stale_after_days > 30) {
    throw new Error("The defense catalog review window must stay between 1 and 30 days.");
  }
  const requiredTruth = [
    "alliance_membership_claimed",
    "catalog_entry_means_connected",
    "configured_adapter_required_for_live_access",
    "benchmark_evidence_required_for_quality_claims",
    "defensive_use_only",
    "automatic_install_or_execution",
    "automatic_merge_or_publish",
  ];
  for (const key of requiredTruth) {
    if (!(key in catalog.truth_contract)) throw new Error(`Missing truth contract control: ${key}`);
  }
  if (catalog.truth_contract.catalog_entry_means_connected !== false) {
    throw new Error("Catalog entries must never be reported as live connections.");
  }
  if (catalog.truth_contract.alliance_membership_claimed !== false) {
    throw new Error("The catalog must not claim alliance membership.");
  }
  if (catalog.truth_contract.defensive_use_only !== true) {
    throw new Error("The security catalog must remain defensive-only.");
  }
  if (catalog.truth_contract.configured_adapter_required_for_live_access !== true
    || catalog.truth_contract.benchmark_evidence_required_for_quality_claims !== true) {
    throw new Error("Live access and quality claims must remain evidence-gated.");
  }
  if (catalog.truth_contract.automatic_install_or_execution !== false
    || catalog.truth_contract.automatic_merge_or_publish !== false) {
    throw new Error("Unreviewed installation, execution, merge, and publishing must remain disabled.");
  }

  const rowGroups: Array<[CatalogRow[], string]> = [
    [catalog.alliance_reference_tools, "Alliance tool"],
    [catalog.openssf_projects, "OpenSSF project"],
    [catalog.model_discovery_sources, "Model source"],
    [catalog.priority_open_model_watchlist_2026, "Open-model watchlist"],
  ];
  for (const [rows, label] of rowGroups) {
    assertUnique(rows, label);
    assertOfficialHttps(rows, label);
  }
  assertUnique(
    catalog.official_sources.map((row) => ({ id: row.id, label: row.label, official_source: row.url })),
    "Official source",
  );
  assertOfficialHttps(
    catalog.official_sources.map((row) => ({ id: row.id, label: row.label, official_source: row.url })),
    "Official source",
  );
  assertUnique(
    catalog.threat_domains.map((row) => ({ id: row.id, label: row.label, official_source: "https://openssf.org/groups/ai-ml-security/" })),
    "Threat domain",
  );
  assertUnique(
    catalog.defense_pipeline.map((row) => ({ id: row.id, label: row.label, official_source: "https://openssf.org/" })),
    "Defense pipeline stage",
  );
  if (catalog.alliance_reference_tools.length < 6) throw new Error("Alliance reference coverage is incomplete.");
  if (catalog.openssf_projects.length < 23) throw new Error("The official OpenSSF project catalog is incomplete.");
  if (catalog.threat_domains.length < 10 || catalog.defense_pipeline.length < 7) {
    throw new Error("Defense threats and lifecycle stages need full-stack coverage.");
  }
  if (catalog.model_discovery_sources.length < 8 || catalog.priority_open_model_watchlist_2026.length < 8) {
    throw new Error("Current hosted, open, and local model discovery coverage is incomplete.");
  }
  for (const source of catalog.model_discovery_sources) {
    if (!allowedStatuses.has(source.connection_status) || source.connection_status === "connected") {
      throw new Error(`Model source ${source.id} has an unsupported connection status.`);
    }
  }
  if (catalog.github_profile_contract.raw_token_in_browser !== false
    || catalog.github_profile_contract.per_user_isolation !== true
    || catalog.github_profile_contract.repository_allowlist_required !== true) {
    throw new Error("GitHub profile isolation and raw-token controls must remain enabled.");
  }
  if (catalog.open_source_upgrade_contract.automatic_merge !== false
    || catalog.open_source_upgrade_contract.owner_approval_required !== true
    || catalog.open_source_upgrade_contract.sandbox_required !== true) {
    throw new Error("Open-source upgrades must stay sandboxed, reviewed, and owner-approved.");
  }
  return {
    ...catalog,
    summary: {
      alliance_reference_tools: catalog.alliance_reference_tools.length,
      openssf_projects: catalog.openssf_projects.length,
      threat_domains: catalog.threat_domains.length,
      defense_pipeline_stages: catalog.defense_pipeline.length,
      model_discovery_sources: catalog.model_discovery_sources.length,
      priority_open_model_families: catalog.priority_open_model_watchlist_2026.length,
      product_profiles: catalog.product_profiles.length,
      live_company_connections: 0,
      alliance_membership_claimed: false,
    },
  };
}

function serialize(value: unknown) {
  return `${JSON.stringify(value, null, 2)}\n`;
}

const catalog = validate(JSON.parse(readFileSync(sourcePath, "utf8")) as DefenseCatalog);
const generated = serialize(catalog);
const publicScript = `window.BUDDY_OPEN_SECURE_AI_DEFENSE = ${JSON.stringify(catalog)};\n`;
const check = process.argv.includes("--check");

if (check) {
  for (const [path, expected] of [[generatedPath, generated], [publicPath, publicScript]] as const) {
    if (!existsSync(path) || readFileSync(path, "utf8") !== expected) {
      throw new Error(`Generated file is stale: ${path.replace(`${root}/`, "")}`);
    }
  }
} else {
  writeFileSync(generatedPath, generated);
  writeFileSync(publicPath, publicScript);
}

console.log(JSON.stringify(catalog.summary));
