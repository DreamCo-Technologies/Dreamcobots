#!/usr/bin/env python3
"""Generate source-backed, evidence-honest Division Superbot manifests."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "superbot-consolidation-v1.json"
INVENTORY = ROOT / "config" / "generated" / "superbot-repository-inventory.json"
BOT_MANIFEST = ROOT / "config" / "bots" / "bot-manifests.generated.json"
APP_BOTS = ROOT / "App_bots"
DOMAIN_CONTRACT = ROOT / "shared" / "division-production-contract.ts"
MODEL_MANIFEST = ROOT / "config" / "generated" / "division-model-manifest.json"
TRAINING_POLICY = ROOT / "config" / "division-model-training-policy.json"
OUT = ROOT / "config" / "divisions"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def unique_rows(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    found: dict[str, dict[str, Any]] = {}
    for row in rows:
        value = str(row.get(key, "")).strip()
        if value:
            source = str(row.get("source_bot_slug", "")).strip()
            found.setdefault(f"{value.casefold()}|{source.casefold()}", row)
    return [found[k] for k in sorted(found)]


def load_domain_profiles(path: Path) -> dict[str, dict[str, Any]]:
    """Read the simple typed domain-profile object without importing TypeScript at runtime."""
    source = path.read_text(encoding="utf-8")
    pattern = re.compile(r"^  (?P<name>[A-Za-z][A-Za-z0-9]+): \{\n(?P<body>.*?)^  \},", re.M | re.S)
    profiles: dict[str, dict[str, Any]] = {}
    for match in pattern.finditer(source):
        body = match.group("body")
        profile: dict[str, Any] = {}
        for key in ("purpose", "outcome", "boundary"):
            found = re.search(rf'^\s*{key}:\s*"((?:\\.|[^"\\])*)",?\s*$', body, re.M)
            if found:
                profile[key] = json.loads('"' + found.group(1) + '"')
        for key in ("serves", "focusAreas"):
            found = re.search(rf"^\s*{key}:\s*\[(.*?)\],?\s*$", body, re.M | re.S)
            if found:
                profile[key] = [json.loads('"' + value + '"') for value in re.findall(r'"((?:\\.|[^"\\])*)"', found.group(1))]
        if all(profile.get(key) for key in ("purpose", "outcome", "boundary", "serves", "focusAreas")):
            profiles[match.group("name")] = profile
    if not profiles:
        raise ValueError(f"no domain profiles parsed from {path}")
    return profiles


def profile_rows(app_bots_dir: Path, bot_registry: dict[str, Any]) -> list[dict[str, Any]]:
    routes = {row["slug"]: row for row in bot_registry.get("bots", []) if row.get("slug")}
    rows: list[dict[str, Any]] = []
    for path in sorted(app_bots_dir.glob("*.json")):
        if path.name == "masterbots-46-65.json":
            continue
        payload = load_json(path)
        for bot in payload.get("bots", []):
            bot_slug = str(bot.get("slug", "")).strip()
            if bot_slug:
                rows.append({**bot, "slug": bot_slug, "source_path": path.relative_to(ROOT).as_posix(),
                             "route": routes.get(bot_slug, {})})
    return rows


def _capabilities(profiles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for profile in profiles:
        for index, value in enumerate(profile.get("capabilities", []) or [], start=1):
            if isinstance(value, str) and value.strip():
                out.append({
                    "id": f"{profile['slug']}:capability:{index}",
                    "name": value.strip(),
                    "source_bot_slug": profile["slug"],
                    "source_path": profile["source_path"],
                    "evidence_status": "declared_in_source_profile_not_runtime_verified",
                })
    return out


def build_division_manifest(
    division: dict[str, Any],
    canonical_profiles: list[dict[str, Any]],
    proposed_profiles: list[dict[str, Any]],
    owned_files: list[str],
    domain_profile: dict[str, Any] | None = None,
    model_record: dict[str, Any] | None = None,
    training_policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    name = division["division"]
    domain_profile = domain_profile or {}
    training_policy = training_policy or {}
    tools, connectors, benchmarks, implementation_tasks = [], [], [], []
    user_segments = list(domain_profile.get("serves", []))
    revenue_models, explicit_jobs, explicit_workflows = [], [], []

    for profile in canonical_profiles:
        for tool in profile.get("toolsNeeded", []) or []:
            if isinstance(tool, str) and tool.strip():
                tools.append({"name": tool.strip(), "source_bot_slug": profile["slug"],
                              "source_path": profile["source_path"], "status": "required_not_configured_or_verified"})
        for api in profile.get("api", []) or []:
            if isinstance(api, str) and api.strip():
                connectors.append({"name": api.strip(), "source_bot_slug": profile["slug"],
                                   "source_path": profile["source_path"], "status": "candidate_not_connected"})
        for metric in profile.get("benchmarks", []) or []:
            if isinstance(metric, dict):
                benchmarks.append({**metric, "source_bot_slug": profile["slug"],
                                   "source_path": profile["source_path"], "status": "declared_target_not_measured"})
        for task in profile.get("tasks", []) or []:
            if isinstance(task, dict):
                implementation_tasks.append({**task, "source_bot_slug": profile["slug"],
                                              "source_path": profile["source_path"]})
        target_users = profile.get("targetUsers")
        if isinstance(target_users, str) and target_users.strip():
            user_segments.append(target_users.strip())
        revenue = profile.get("revenueModel")
        if isinstance(revenue, str) and revenue.strip():
            revenue_models.append(revenue.strip())
        explicit_jobs.extend({**job, "source_bot_slug": profile["slug"], "source_path": profile["source_path"]}
                             for job in profile.get("userJobs", []) or [] if isinstance(job, dict))
        explicit_workflows.extend({**workflow, "source_bot_slug": profile["slug"], "source_path": profile["source_path"]}
                                  for workflow in profile.get("workflows", []) or [] if isinstance(workflow, dict))

    gaps = []
    if not explicit_jobs:
        gaps.append({"area": "user_jobs", "reason": "No explicit user-job contract was found; focus areas below are hypotheses, not validated jobs."})
    if not explicit_workflows:
        gaps.append({"area": "workflows", "reason": "No executable workflow contract was found in source profiles."})
    if not tools:
        gaps.append({"area": "tools", "reason": "No tool requirements were declared in source profiles."})
    else:
        gaps.append({"area": "tools", "reason": "Required tools are profile declarations; adapter availability and health are not verified."})
    if not connectors:
        gaps.append({"area": "connectors", "reason": "No API or connector contract was found in source profiles."})
    else:
        gaps.append({"area": "connectors", "reason": "API names are candidates only; no credentials, scopes, connection tests, or health evidence are implied."})
    if not benchmarks:
        gaps.append({"area": "benchmarks", "reason": "No benchmark definitions were found in source profiles."})
    else:
        gaps.append({"area": "benchmarks", "reason": "Targets are declared; measured runs, baselines, and holdout evidence are absent."})
    if not implementation_tasks:
        gaps.append({"area": "implementation_tasks", "reason": "No implementation task backlog was found in source profiles."})
    if not domain_profile:
        gaps.append({"area": "domain_profile", "reason": "No canonical division production contract was found."})
    if not revenue_models:
        gaps.append({"area": "commercial", "reason": "No revenue model was declared in source profiles."})
    if not canonical_profiles:
        gaps.append({"area": "ownership", "reason": "No source bot profile has a canonical owner route to this division."})
    if proposed_profiles:
        gaps.append({"area": "proposed_ownership", "reason": "Proposed profiles remain excluded from canonical capabilities until an owner approves their route."})
    if not model_record:
        gaps.append({"area": "model_training", "reason": "No division model registry record was found."})
    elif model_record.get("lifecycle_state") != "trained":
        gaps.append({"area": "model_training", "reason": "The division model remains planned or experimental; no production checkpoint is certified."})

    capabilities = _capabilities(canonical_profiles)
    proposed_capabilities = _capabilities(proposed_profiles)
    outcome_metrics = unique_rows(
        [{"label": str(row.get("label", "")).strip(), "target": row.get("target"),
          "source_bot_slug": row.get("source_bot_slug"), "source_path": row.get("source_path"),
          "status": "declared_not_measured"} for row in benchmarks if row.get("label")], "label")
    if domain_profile.get("outcome"):
        outcome_metrics.append({
            "label": domain_profile["outcome"],
            "target": None,
            "source_bot_slug": None,
            "source_path": "shared/division-production-contract.ts",
            "status": "domain_outcome_not_measured",
        })

    model_training = {
        "status": model_record.get("lifecycle_state", "unregistered") if model_record else "unregistered",
        "modelId": model_record.get("model_id") if model_record else None,
        "modelVersion": model_record.get("model_version") if model_record else None,
        "parameterTarget": (training_policy.get("student_size") or {}).get("initial_parameter_target"),
        "tokenizerMode": (training_policy.get("tokenizer") or {}).get("default_mode"),
        "trainingStrategy": (training_policy.get("training") or {}).get("strategy"),
        "checkpoint": (model_record.get("training") or {}).get("checkpoint") if model_record else None,
        "checkpointSha256": (model_record.get("training") or {}).get("checkpoint_sha256") if model_record else None,
        "evaluation": model_record.get("evaluation") if model_record else None,
        "serving": model_record.get("serving") if model_record else None,
        "releaseEvidence": model_record.get("release_evidence") if model_record else None,
        "modelManifestSource": "config/generated/division-model-manifest.json",
        "policySource": "config/division-model-training-policy.json",
    }
    return {
        "schema": "dreamco.division_superbot.v3",
        "version": "3.0.0",
        "identity": {"id": division["id"], "displayName": f"{name} Superbot",
                     "division": name, "cluster": division["cluster"]},
        "mission": domain_profile.get("purpose") or f"Coordinate and improve source-backed capabilities canonically assigned to {name}.",
        "domainProfile": {
            "purpose": domain_profile.get("purpose"),
            "serves": domain_profile.get("serves", []),
            "outcome": domain_profile.get("outcome"),
            "boundary": domain_profile.get("boundary"),
            "focusAreas": domain_profile.get("focusAreas", []),
            "sourcePath": "shared/division-production-contract.ts" if domain_profile else None,
        },
        "candidateUserJobAreas": [
            {"area": area, "status": "hypothesis_not_validated",
             "sourcePath": "shared/division-production-contract.ts"}
            for area in domain_profile.get("focusAreas", [])
        ],
        "userJobs": explicit_jobs,
        "userSegments": sorted(set(user_segments)),
        "capabilities": capabilities,
        "proposedCapabilities": proposed_capabilities,
        "tools": unique_rows(tools, "name"),
        "connectors": unique_rows(connectors, "name"),
        "policies": {"externalWritesDefault": "disabled", "approvalRequiredForHighImpact": True,
                     "secretPolicy": "secrets-never-in-source", "canonicalOwnershipOnly": True},
        "dependencies": [
            {"name": row["name"], "kind": "required_tool", "status": row["status"], "source_bot_slug": row["source_bot_slug"]}
            for row in unique_rows(tools, "name")
        ] + [
            {"name": row["name"], "kind": "candidate_connector", "status": row["status"], "source_bot_slug": row["source_bot_slug"]}
            for row in unique_rows(connectors, "name")
        ],
        "workflows": explicit_workflows,
        "implementationTasks": implementation_tasks,
        "benchmarks": benchmarks,
        "modelTraining": model_training,
        "commercial": {"revenueModels": sorted(set(revenue_models)), "outcomeMetrics": outcome_metrics,
                       "status": "source_declared_not_financially_verified"},
        "migration": {
            "legacyProfiles": sorted({p["slug"] for p in canonical_profiles}),
            "proposedProfilesPendingOwnerReview": sorted({p["slug"] for p in proposed_profiles}),
            "legacyFiles": sorted(set(owned_files)), "aliases": [], "provenanceRequired": True,
        },
        "sourceSummary": {
            "canonicalProfileCount": len(canonical_profiles), "proposedProfileCount": len(proposed_profiles),
            "declaredCapabilityCount": len(capabilities), "requiredToolCount": len(tools),
            "candidateConnectorCount": len(connectors), "declaredBenchmarkCount": len(benchmarks),
            "implementationTaskCount": len(implementation_tasks),
        },
        "gaps": gaps,
        "status": "source_mapped_needs_validation" if canonical_profiles else "inventory_only_needs_owner_review",
        "notes": [
            "Capabilities are copied from source profiles and are not evidence of working runtime implementations.",
            "Proposed capabilities are kept separate from canonical ownership and do not grant execution rights.",
            "Tools and connectors are requirements/candidates, not verified connections.",
            "Benchmarks and commercial metrics are declarations, not measured results or verified revenue.",
            "Candidate user-job areas are hypotheses and require user validation.",
            "Model registry state is not a claim that weights have been trained or deployed.",
            "No source files are deleted or rewritten by this generator.",
        ],
    }


def build_all(config: dict[str, Any], inventory: dict[str, Any], bot_registry: dict[str, Any],
              app_profiles: list[dict[str, Any]], domain_profiles: dict[str, dict[str, Any]],
              model_manifest: dict[str, Any], training_policy: dict[str, Any]) -> dict[str, dict[str, Any]]:
    output = {}
    records = inventory.get("records", [])
    model_records = {row.get("division_name"): row for row in model_manifest.get("records", [])}
    for division in config.get("division_superbots", []):
        name = division["division"]
        canonical = [p for p in app_profiles if p["route"].get("primary_domain_owner") == name]
        proposed = [p for p in app_profiles if not p["route"].get("primary_domain_owner")
                    and p["route"].get("proposed_domain_owner") == name]
        owned_files = [row["path"] for row in records
                       if row.get("proposed_superbot") == division["cluster"] or row.get("division") == name]
        output[f"{slug(name)}.json"] = build_division_manifest(
            division, canonical, proposed, owned_files,
            domain_profiles.get(name), model_records.get(name), training_policy)
    return output


def render(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail when generated division manifests are stale")
    args = parser.parse_args(argv)
    required = (CONFIG, INVENTORY, BOT_MANIFEST, DOMAIN_CONTRACT, MODEL_MANIFEST, TRAINING_POLICY)
    for path in required:
        if not path.exists():
            raise SystemExit(f"required input missing: {path.relative_to(ROOT)}")
    bot_registry = load_json(BOT_MANIFEST)
    manifests = build_all(
        load_json(CONFIG), load_json(INVENTORY), bot_registry, profile_rows(APP_BOTS, bot_registry),
        load_domain_profiles(DOMAIN_CONTRACT), load_json(MODEL_MANIFEST), load_json(TRAINING_POLICY))
    expected = {name: render(payload) for name, payload in manifests.items()}
    existing = {path.name for path in OUT.glob("*.json")} if OUT.exists() else set()
    stale = sorted(name for name, content in expected.items()
                   if not (OUT / name).exists() or (OUT / name).read_text(encoding="utf-8") != content)
    extra = sorted(existing - set(expected))
    if args.check:
        if stale or extra:
            raise SystemExit(f"division manifests stale: {len(stale)} stale, {len(extra)} extra; run tools/build_division_superbot_manifests.py")
        print(f"division manifests current: {len(expected)} source-backed Division Superbots")
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    for name, content in expected.items():
        (OUT / name).write_text(content, encoding="utf-8")
    for name in extra:
        (OUT / name).unlink()
    print(json.dumps({"ok": True, "divisions": len(expected),
                      "canonical_profiles": sum(m["sourceSummary"]["canonicalProfileCount"] for m in manifests.values()),
                      "proposed_profiles": sum(m["sourceSummary"]["proposedProfileCount"] for m in manifests.values()),
                      "output": str(OUT.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
