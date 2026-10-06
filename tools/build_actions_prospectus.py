#!/usr/bin/env python3
"""Build the public-safe prospectus for every Actions workflow AND every fleet bot.

One generator, one card format (``dreamco.run_prospectus.v1``) for every
"Run with Buddy" button on Pages:

* ``config/generated/actions-prospectus.json`` / ``website/data/actions-prospectus.json``
  -- the existing Actions prospectus (schema v2, unchanged consumers);
* ``config/buddy/run-with-buddy.generated.json`` -- one Buddy control-plane
  job per workflow plus ``fleet_bot_run`` (same job shape as
  ``config/buddy/control-plane.json`` from #13197; curated jobs win on merge);
* ``website/data/run-prospectus.json`` -- the cards. Workflow cards are full
  records; bot cards are compact and reference shared per-engine templates
  (``resolve()`` expands them; Pages does the same in JS).

Every field is derived from the workflow file, the Actions health report, the
bot manifest + shared profiles, and the fleet auditor's status file. Unknown
values are written as ``"unknown"``; nothing is hand-authored per card.

``--check`` fails when outputs are stale or the workflow count drifted from
``.github/workflows``; ``--check-buttons`` fails when any Run button (every
registry job and every bot) lacks a complete prospectus.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

REPO = "DreamCo-Technologies/Dreamcobots"
GH = f"https://github.com/{REPO}"
WORKFLOWS = ROOT / ".github" / "workflows"
HEALTH = ROOT / "website" / "data" / "actions-health-report.json"
CONTRACT = ROOT / "config" / "actions-control-prospectus.json"
CONTROL_PLANE = ROOT / "config" / "buddy" / "control-plane.json"
FLEET_STATUS = ROOT / "website" / "data" / "fleet-runtime-status.json"
OUT_ACTIONS_REPO = ROOT / "config" / "generated" / "actions-prospectus.json"
OUT_ACTIONS_PUBLIC = ROOT / "website" / "data" / "actions-prospectus.json"
OUT_REGISTRY = ROOT / "config" / "buddy" / "run-with-buddy.generated.json"
OUT_CARDS = ROOT / "website" / "data" / "run-prospectus.json"
OUT_BOT_CARDS = ROOT / "website" / "data" / "run-prospectus-bots.json"
BOT_COLUMNS = ["id", "title", "division", "engine", "does", "files", "risk_tier", "triggerable", "blocked", "readiness", "fixture",
               "evidence", "capabilities", "custom"]
# Bot "files" are stored as a short code when they follow the standard layout (keeps Pages small):
# A = App_bots/<division>.json, M = bots/<slug>.md, L = config/bots/teammate-lanes.json.
FILE_CODES = {"A": "App_bots/{division}.json", "M": "bots/{slug}.md", "L": "config/bots/teammate-lanes.json"}
CAPABILITIES_SHOWN = 8


def encode_files(files: list[str], slug: str, division: str) -> str | list[str]:
    code = ""
    for f in files:
        letter = next((k for k, v in FILE_CODES.items() if v.format(division=division, slug=slug) == f), None)
        if letter is None:
            return files
        code += letter
    return code


def decode_files(value: str | list[str], slug: str, division: str) -> list[str]:
    if isinstance(value, list):
        return value
    return [FILE_CODES[c].format(division=division, slug=slug) for c in value]


BLOCKED_REASONS = {"blocked_money": "money bot: never triggerable from Buddy or Pages",
                   "blocked_destructive": "delete/destructive bot: never triggerable from Buddy or Pages",
                   "spec_only": "no shared engine fits this bot yet",
                   "disabled": "disabled by an accepted customization"}

# Used only while #13197 (control plane) is not on main. Same values as its
# config/buddy/control-plane.json "operators".
FALLBACK_OPERATORS = ["ireanjordan24"]
ROUTER_WORKFLOW = "buddy-command-router.yml"
BOT_JOB_ID = "fleet_bot_run"
DIVISION_JOB_ID = "fleet_division_run"
DIVISIONS = ROOT / "config" / "bots" / "division-manifests.generated.json"
BOT_WORKFLOW = "fleet-bot-run.yml"
REQUIRED_CARD_FIELDS = ("id", "kind", "title", "does", "inputs", "outputs", "touches", "risk_tier", "trigger",
                        "secrets", "cost", "runtime", "readiness", "links")

SECRET_RE = re.compile(r"secrets\.([A-Z][A-Z0-9_]*)")
MONEY_RE = re.compile(r"\b(stripe|payouts?|payments?|billing|revenue|pricing|invoice|checkout|money[-_ ]os|trade)\b", re.I)
DESTRUCTIVE_RE = re.compile(r"git push [^\n]*--delete|git push \S+ :\S|git branch -D|-X DELETE|--method DELETE|"
                            r"gh (?:release|repo|issue) delete|delete-branch: *true|delete_branch|deleteRef", re.I)
PUSH_MAIN_RE = re.compile(r"git push(?![^\n]*--dry-run)[^\n]*(?:\bmain\b|HEAD:main|origin HEAD\b)|git push\s*$", re.M)
OPENS_PR_RE = re.compile(r"gh pr create|peter-evans/create-pull-request|pulls\.create", re.I)
ARTIFACT_RE = re.compile(r"uses:\s*actions/upload-artifact@v\d+[\s\S]*?name:\s*['\"]?([^\n'\"]+)", re.M)
SERVICE_PATTERNS = [
    ("GitHub API", r"api\.github\.com|gh api|github\.rest|actions/github-script"),
    ("GitHub Pages", r"actions/deploy-pages|actions/upload-pages-artifact"),
    ("OpenRouter", r"openrouter"), ("Hugging Face", r"huggingface|hf_hub|HF_TOKEN"),
    ("OpenAI", r"OPENAI_"), ("Anthropic", r"ANTHROPIC_"), ("xAI / Grok API", r"XAI_|api\.x\.ai"),
    ("Stripe", r"stripe"), ("Slack", r"slack"), ("Vercel", r"vercel"), ("Netlify", r"netlify"),
    ("Docker registry", r"docker/login-action|ghcr\.io"), ("npm registry", r"npm (?:ci|install)"),
    ("PyPI", r"pip install"),
]
WRITE_SCOPES = {"contents", "pull-requests", "issues", "pages", "actions", "packages", "deployments", "statuses",
                "checks", "security-events", "id-token", "discussions"}


def read_json(path: Path, default: Any = None) -> Any:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def job_id_for(filename: str) -> str:
    stem = re.sub(r"[^a-z0-9]+", "_", Path(filename).stem.lower()).strip("_")
    return ("wf_" + stem)[:64]


# --------------------------------------------------------------- workflows

def _load_yaml(text: str) -> dict[str, Any]:
    import yaml

    doc = yaml.safe_load(text) or {}
    if True in doc and "on" not in doc:  # YAML 1.1 parses bare `on:` as True
        doc["on"] = doc.pop(True)
    return doc


def _permissions(doc: dict[str, Any]) -> tuple[dict[str, str], bool]:
    """Merged permissions across top level + jobs, and whether any were declared."""
    merged: dict[str, str] = {}
    declared = False
    blocks = [doc.get("permissions")] + [(job or {}).get("permissions") for job in (doc.get("jobs") or {}).values()]
    for block in blocks:
        if block is None:
            continue
        declared = True
        if isinstance(block, str):
            if block in {"write-all"}:
                merged.update({scope: "write" for scope in WRITE_SCOPES})
            continue
        for scope, level in (block or {}).items():
            if level == "write" or merged.get(scope) != "write":
                merged[str(scope)] = str(level)
    return merged, declared


def _dispatch_inputs(doc: dict[str, Any]) -> tuple[bool, dict[str, Any], list[str]]:
    on = doc.get("on")
    if isinstance(on, str):
        on = {on: None}
    elif isinstance(on, list):
        on = {k: None for k in on}
    on = on or {}
    if "workflow_dispatch" not in on:
        return False, {}, []
    inputs = ((on.get("workflow_dispatch") or {}).get("inputs")) or {}
    accepted: dict[str, Any] = {}
    unsupported: list[str] = []
    for name, spec in inputs.items():
        spec = spec or {}
        kind = spec.get("type", "string")
        if kind == "choice" and spec.get("options"):
            accepted[name] = {"type": "choice", "options": [str(o) for o in spec["options"]],
                              "default": str(spec.get("default", spec["options"][0]))}
        elif kind == "boolean":
            accepted[name] = {"type": "boolean", "default": bool(spec.get("default", False))}
        elif spec.get("required") and spec.get("default") in (None, ""):
            unsupported.append(name)
    return True, accepted, unsupported


def classify_workflow(filename: str, text: str, doc: dict[str, Any]) -> dict[str, Any]:
    perms, declared = _permissions(doc)
    writes = sorted(scope for scope, level in perms.items() if level == "write")
    dispatchable, inputs, unsupported = _dispatch_inputs(doc)
    if MONEY_RE.search(filename) or MONEY_RE.search(str(doc.get("name", ""))):
        tier = "money"
    elif DESTRUCTIVE_RE.search(text):
        tier = "destructive"
    elif not declared or "contents" in writes and (PUSH_MAIN_RE.search(text) or OPENS_PR_RE.search(text)):
        tier = "writes_code" if declared else "unknown_permissions"
    elif writes:
        tier = "writes_reports"
    else:
        tier = "read_only"
    reason = None
    if filename == ROUTER_WORKFLOW:
        reason = "this is the Buddy command router itself"
    elif tier == "money":
        reason = "money workflows are never triggerable from Buddy or Pages"
    elif tier == "destructive":
        reason = "workflow deletes branches/releases/resources; never triggerable from Buddy"
    elif tier == "unknown_permissions":
        reason = "no permissions block (defaults may grant write); declare permissions before it can be triggered"
    elif tier == "writes_code" and PUSH_MAIN_RE.search(text):
        reason = "pushes to main; writes_code jobs must be PR-only"
    elif not dispatchable:
        reason = "no workflow_dispatch trigger; add one to run it from Buddy"
    elif unsupported:
        reason = f"required free-text input(s) {', '.join(unsupported)} need an anchored pattern in the registry"
    timeouts = [job.get("timeout-minutes") for job in (doc.get("jobs") or {}).values() if isinstance(job, dict)]
    timeouts = [t for t in timeouts if isinstance(t, (int, float))]
    return {
        "risk_tier": tier, "writes": writes, "permissions_declared": declared, "inputs": inputs,
        "triggerable": reason is None, "blocked_reason": reason,
        "requires_owner_approval": tier in {"writes_code", "writes_reports"},
        "secrets": sorted(set(SECRET_RE.findall(text)) - {"GITHUB_TOKEN"}),
        "uses_github_token": "GITHUB_TOKEN" in text or "github.token" in text,
        "artifacts": sorted({m.strip() for m in ARTIFACT_RE.findall(text)})[:8],
        "services": [name for name, pat in SERVICE_PATTERNS if re.search(pat, text, re.I)],
        "timeout_minutes": max(timeouts) if timeouts else None,
        "jobs": len(doc.get("jobs") or {}),
    }


def workflow_records(health: dict[str, Any], operators: list[str], curated: dict[str, str]) -> tuple[list, list]:
    by_file = {f["filename"]: f for f in health.get("findings", [])}
    jobs, cards = [], []
    for path in sorted(WORKFLOWS.glob("*.y*ml")):
        text = path.read_text(encoding="utf-8")
        try:
            doc = _load_yaml(text)
        except Exception as exc:  # malformed workflow: still gets a card, never a button
            doc = {}
            parse_error = type(exc).__name__
        else:
            parse_error = None
        finding = by_file.get(path.name, {})
        info = classify_workflow(path.name, text, doc)
        if path.name == BOT_WORKFLOW:
            info.update(triggerable=True, blocked_reason=None,
                        inputs={"bot": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]{0,79}$", "max_length": 80}})
        if parse_error:
            info.update(triggerable=False, blocked_reason=f"workflow YAML did not parse ({parse_error})")
        job_id = BOT_JOB_ID if path.name == BOT_WORKFLOW else (curated.get(path.name) or job_id_for(path.name))
        job = {
            "id": job_id, "family": "workflow", "title": finding.get("display_name") or doc.get("name") or path.stem,
            "workflow": path.name, "risk_tier": info["risk_tier"] if info["risk_tier"] in {"read_only", "writes_reports", "writes_code", "money"} else "writes_code",
            "requires_owner_approval": info["requires_owner_approval"], "triggerable": info["triggerable"],
            "inputs": info["inputs"], "generated": True,
            "notes": info["blocked_reason"] or f"Generated from .github/workflows/{path.name}.",
        }
        if not job["triggerable"]:
            job["blocked_reason"] = info["blocked_reason"] or "blocked by policy"
        if info["risk_tier"] == "destructive":
            job["destructive"] = True
        if job["risk_tier"] in {"writes_code", "money"}:
            job["requires_owner_approval"] = True
        if path.name in curated:
            job["covered_by_curated_job"] = curated[path.name]
        jobs.append(job)
        static = finding.get("static_status", "unknown")
        runtime = finding.get("runtime_status", "unknown_until_run_evidence_loaded")
        cost = "$0 GitHub Actions minutes (public repository, standard GitHub-hosted runner)"
        if info["secrets"]:
            cost += "; external API usage behind the listed secrets: unknown"
        cards.append({
            "id": job_id, "kind": "workflow", "title": job["title"],
            "does": finding.get("purpose") or f"Runs .github/workflows/{path.name}",
            "steps": finding.get("what_happens", [])[:8],
            "inputs": [f"{k} ({v['type']}{': ' + '|'.join(v['options']) if v.get('options') else ''}{' ' + v['pattern'] if v.get('pattern') else ''})" for k, v in info["inputs"].items()] or ["none (workflow_dispatch without inputs)" if info["triggerable"] or "dispatch" not in (info["blocked_reason"] or "") else "not dispatchable"],
            "outputs": sorted(set(finding.get("outputs", []) + [f"artifact: {a}" for a in info["artifacts"]])) or ["GitHub Actions run log"],
            "touches": {
                "files": sorted(set(finding.get("referenced_files", [])))[:12] + [f"npm run {s}" for s in finding.get("npm_scripts", [])[:6]],
                "systems": ["GitHub Actions runner"] + [f"token write: {w}" for w in info["writes"]]
                           + [f"action: {a}" for a in sorted(set(finding.get("actions", [])))[:6]],
                "services": info["services"] or ["none detected"],
            },
            "risk_tier": info["risk_tier"],
            "trigger": {"allowlist": operators, "requires_write_permission": True,
                        "requires_owner_approval": info["requires_owner_approval"], "triggerable": info["triggerable"],
                        "blocked_reason": info["blocked_reason"],
                        "command": (f"/buddy run {job_id}" + (" bot=<slug>" if path.name == BOT_WORKFLOW else "")) if info["triggerable"] else None,
                        "events": finding.get("triggers", [])},
            "secrets": (info["secrets"] + (["GITHUB_TOKEN (automatic, scoped by permissions)"] if info["uses_github_token"] else [])) or ["none"],
            "cost": cost,
            "runtime": f"unknown (timeout cap {info['timeout_minutes']} min)" if info["timeout_minutes"] else "unknown (no timeout declared)",
            "readiness": {"state": "CONFIGURED" if static == "static_checks_passed" else "BLOCKED",
                          "detail": f"static: {static}; runtime: {runtime}", "source": "website/data/actions-health-report.json"},
            "links": {"source": f"{GH}/blob/main/.github/workflows/{path.name}",
                      "workflow": f"{GH}/actions/workflows/{path.name}",
                      "latest_run": f"{GH}/actions/workflows/{path.name}?query=branch%3Amain",
                      "evidence": "actions.html#" + path.stem},
        })
    return jobs, cards


# -------------------------------------------------------------------- bots

def _schema_fields(schema: dict[str, Any], prefix: str = "") -> list[str]:
    out = []
    for key, spec in (schema.get("properties") or {}).items():
        if spec.get("type") == "object" and spec.get("properties"):
            out += _schema_fields(spec, f"{prefix}{key}.")
        else:
            out.append(f"{prefix}{key} ({spec.get('type') or 'enum'})")
    return out


def bot_templates(collection: dict[str, Any], operators: list[str]) -> dict[str, Any]:
    profiles = collection["profiles"]
    templates = {}
    for engine in ("analysis", "classification", "workflow", "drafting"):
        io = profiles["io_schema"].get(f"engine:{engine}", {})
        live = engine == "drafting"
        templates[f"engine:{engine}"] = {
            "inputs": _schema_fields(io.get("input", {})),
            "outputs": _schema_fields(io.get("output", {})) + ["evidence record (dreamco.fleet_runtime.job_evidence.v1) as a workflow artifact"],
            "systems": ["buddy/fleet_runtime (executor, engines, permissions, guardrails)", "GitHub Actions runner (read-only token)"],
            "services": ["none (offline deterministic)"] + (["OpenRouter via buddy.openrouter.gateway, only if DREAMCO_FLEET_LIVE_MODEL=1 server-side"] if live else []),
            "secrets": ["none for Run with Buddy (offline)"] + (["OPENROUTER_API_KEY (optional, server-side only, never on Pages)"] if live else []),
            "cost": "$0 model cost (offline deterministic engine); $0 GitHub Actions minutes (public repository)" + ("; live model cost unknown" if live else ""),
            "runtime": "engine < 1 s offline (full-fleet smoke runs in about 1 s); end-to-end workflow time unknown until first run",
            "allowlist": operators,
        }
    return templates


def bot_cards(collection: dict[str, Any], status: dict[str, Any], operators: list[str]) -> list[dict[str, Any]]:
    from buddy.fleet_runtime.contract import expand
    from buddy.fleet_runtime.customize import load_customizations, apply_customization

    columns = (status or {}).get("bot_columns", [])
    states = {row[0]: dict(zip(columns, row)) for row in (status or {}).get("bots", [])}
    custom = load_customizations()
    cards = []
    for compact in collection["bots"]:
        m = apply_customization(expand(compact, collection), custom.get(compact["slug"], {}))
        slug = m["slug"]
        policy = m.get("run_policy", "spec_only")
        if m.get("enabled") is False:
            policy = "disabled"
        row = states.get(slug, {})
        evidence_path = ROOT / "evidence" / "fleet-runtime" / f"{slug}.json"
        cards.append([
            slug, m["name"], m["division"], m["engine"],
            (m.get("description") or "").strip()[:160] or "unknown (spec has no description)",
            encode_files([x.split("#")[0] for x in m["sources"]][:2], slug, m["division"]),
            {"allowed": "read_only", "blocked_money": "money", "blocked_destructive": "destructive"}.get(policy, "none"),
            policy == "allowed", None if policy == "allowed" else policy,
            row.get("state", "unknown"), row.get("fixture"),
            f"evidence/fleet-runtime/{slug}.json" if evidence_path.exists() else None,
            expand(compact, collection)["capabilities"][:CAPABILITIES_SHOWN] if policy not in {"blocked_money", "blocked_destructive"} else [],
            custom.get(slug) or None,
        ])
    return cards


def division_cards(status: dict[str, Any], operators: list[str]) -> list[dict[str, Any]]:
    from buddy.fleet_runtime.customize import load_customizations

    custom = load_customizations()
    audited = {d["name"]: d for d in (status or {}).get("divisions", [])}
    cards = []
    for d in read_json(DIVISIONS, {"divisions": []})["divisions"]:
        a = audited.get(d["name"], {})
        c = custom.get("division:" + d["name"]) or None
        triggerable = d["triggerable"] and not (c or {}).get("enabled") is False
        reason = d["blocked_reason"] or (None if triggerable else "disabled by an accepted customization")
        money_only = d["run_policy"].get("allowed", 0) == 0 and d["name"] != "UNASSIGNED"
        src = next((x for x in d["sources"] if x.startswith(("App_bots/", "config/"))), "")
        cards.append({
            "id": "division:" + d["name"], "kind": "division", "title": d["name"] + " division",
            "does": d["description"] + f" Division smoke runs {', '.join(d['smoke_bots']) or 'no bots'} end to end offline.",
            "inputs": [f"division ({d['name']})"],
            "outputs": ["division smoke result per bot (generic + fixture)", "evidence record (dreamco.fleet_runtime.division_job_evidence.v1) as a workflow artifact"],
            "touches": {"files": d["sources"], "systems": ["buddy/fleet_runtime (executor, engines, divisions)", "GitHub Actions runner (read-only token)"],
                        "services": ["none (offline deterministic)"]},
            "risk_tier": "money" if money_only else ("none" if d["name"] == "UNASSIGNED" else "read_only"),
            "trigger": {"allowlist": operators, "requires_write_permission": True, "requires_owner_approval": False,
                        "triggerable": triggerable, "blocked_reason": reason,
                        "command": f"/buddy run {DIVISION_JOB_ID} division={d['name']}" if triggerable else None},
            "secrets": ["none (offline)"],
            "cost": "$0 model cost (offline deterministic engines); $0 GitHub Actions minutes (public repository)",
            "runtime": f"engine < 1 s for {len(d['smoke_bots'])} smoke bot(s) offline; end-to-end workflow time unknown until first run",
            "readiness": {"state": a.get("state", "unknown"),
                          "detail": f"division smoke {'passed' if a.get('smoke_passed') else 'not passed'}; bots: " +
                                    ", ".join(f"{k} {v}" for k, v in (a.get("bot_states") or {}).items()),
                          "source": "website/data/fleet-runtime-status.json"},
            "links": {"source": f"{GH}/blob/main/{src}" if src else f"{GH}/tree/main/bots",
                      "workflow": f"{GH}/actions/workflows/{BOT_WORKFLOW}",
                      "latest_run": f"{GH}/actions/workflows/{BOT_WORKFLOW}",
                      "evidence": "fleet-runtime.html#division-" + d["name"]},
            "bots": d["bots"], "smoke_bots": d["smoke_bots"], "runnable_bots": d["run_policy"].get("allowed", 0),
            "custom": c, "customizable": d["name"] != "UNASSIGNED" and not money_only,
        })
    return cards


def customize_spec(collection: dict[str, Any], operators: list[str]) -> dict[str, Any]:
    from buddy.fleet_runtime.customize import BOT_FIELDS, DIVISION_FIELDS, FILE_FIELDS, MODEL_ALLOWLIST

    return {
        "command": "/buddy customize <target>",
        "fence": "yaml",
        "bot_fields": BOT_FIELDS, "file_fields": FILE_FIELDS, "division_fields": DIVISION_FIELDS,
        "model_allowlist": list(MODEL_ALLOWLIST),
        "divisions": sorted({b["division"] for b in collection["bots"] if b.get("division")}),
        "toggle_key_pattern": "^[A-Za-z_][A-Za-z0-9_ ./()&+-]{0,119}$",
        "allowlist": operators,
        "policy": "Pages holds no token. Submitting opens a prefilled issue; the router checks the actor is an operator with write permission, validates the patch with buddy/fleet_runtime/customize.py, commits it on a branch and opens a PR. Money and destructive bots cannot be customized; secrets, permissions, workflows and readiness are never editable.",
    }


def resolve(row: list[Any] | dict[str, Any], templates: dict[str, Any], operators: list[str]) -> dict[str, Any]:
    """Expand a compact bot row to the shared dreamco.run_prospectus.v1 card shape."""
    if isinstance(row, dict):
        return row
    card = dict(zip(BOT_COLUMNS, row))
    card["files"] = decode_files(card["files"], card["id"], card["division"])
    card["blocked_reason"] = BLOCKED_REASONS.get(card["blocked"]) if card["blocked"] else None
    card["source"] = card["files"][0] if card["files"] else ""
    t = templates.get(f"engine:{card['engine']}", {})
    slug = card["id"]
    return {
        "id": slug, "kind": "bot", "title": card["title"], "does": card["does"],
        "inputs": t.get("inputs") or ["none: spec-only bot"], "outputs": t.get("outputs") or ["none: spec-only bot"],
        "touches": {"files": card["files"], "systems": t.get("systems") or ["none (not runnable)"],
                    "services": t.get("services") or ["none"]},
        "risk_tier": card["risk_tier"],
        "trigger": {"allowlist": operators, "requires_write_permission": True, "requires_owner_approval": False,
                    "triggerable": card["triggerable"], "blocked_reason": card["blocked_reason"],
                    "command": f"/buddy run {BOT_JOB_ID} bot={slug}" if card["triggerable"] else None},
        "secrets": t.get("secrets") or ["none"],
        "cost": t.get("cost") or "unknown",
        "runtime": t.get("runtime") or "unknown",
        "readiness": {"state": card["readiness"], "detail": f"fixture: {card['fixture'] or 'none'}",
                      "source": "website/data/fleet-runtime-status.json"},
        "links": {"source": f"{GH}/blob/main/{card['source']}" if card["source"] else "unknown",
                  "workflow": f"{GH}/actions/workflows/{BOT_WORKFLOW}",
                  "latest_run": f"{GH}/actions/workflows/{BOT_WORKFLOW}",
                  "evidence": f"{GH}/blob/main/{card['evidence']}" if card["evidence"] else "none yet (see fleet-runtime.html#bot-" + slug + ")"},
    }


# ------------------------------------------------------------------- build

def actions_prospectus(health: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    contract = read_json(CONTRACT)
    rows = []
    for workflow in health.get("findings", []):
        controls = workflow.get("controls", {})
        evidence = "static_checks_passed" if workflow.get("static_status") == "static_checks_passed" else "blocked"
        rows.append({
            "workflow": workflow["workflow"], "name": workflow["display_name"],
            "goal": workflow.get("goal", "repository operations"), "purpose": workflow["purpose"],
            "what_happens": workflow.get("what_happens", []), "outputs": workflow.get("outputs", []),
            "benchmark_commands": workflow.get("benchmark_commands", []), "triggers": workflow.get("triggers", []),
            "github_url": workflow.get("github_url"), "static_status": evidence,
            "runtime_status": workflow.get("runtime_status", "unknown_until_run_evidence_loaded"),
            "errors": workflow.get("errors", []), "warnings": workflow.get("warnings", []),
            "runner_jobs": controls.get("runner_jobs", 0), "controls": controls, "upgrades": workflow.get("upgrades", []),
            "possible_duplicate": workflow.get("possible_duplicate", False),
            "duplicate_candidate_group": workflow.get("duplicate_candidate_group"),
            "possible_duplicates": workflow.get("possible_duplicates", []),
            "progress": "configured" if evidence == "static_checks_passed" else "blocked",
            "prospectus_card": "data/run-prospectus.json#" + job_id_for(workflow["filename"]),
            "investor_note": "Static configuration is inspectable. Operational evidence is required before claiming workflow health, product readiness, or model mastery.",
        })
    controls = [{**item, "progress": "configured", "workflow_count": len(rows)} for item in contract["controls"]]
    summary = {**health.get("summary", {}), "control_areas": len(controls),
               "declared_goals": sorted({row["goal"] for row in rows}),
               "benchmarked_workflows": sum(bool(row["benchmark_commands"]) for row in rows)}
    out = {
        "schema": "dreamco.actions_prospectus.v2",
        "generated_from": ["config/actions-control-prospectus.json", "website/data/actions-health-report.json"],
        "summary": summary, "controls": controls,
        "duplicate_candidate_groups": health.get("duplicate_candidate_groups", []),
        "workflows": rows, "progress_model": contract["progress_model"],
        "truth_boundary": "This prospectus explains intent and static evidence. GitHub run results, retained artifacts, benchmarks, and production observations are required to prove operation. Duplicate candidates are never deleted automatically.",
    }
    public = {key: value for key, value in out.items() if key != "workflows"}
    public["workflow_catalog_url"] = "data/actions-health-report.json"
    public["run_prospectus_url"] = "data/run-prospectus.json"
    public["workflow_count"] = len(rows)
    return out, public


def control_plane() -> tuple[list[str], dict[str, str], bool]:
    plane = read_json(CONTROL_PLANE)
    if not plane:
        return FALLBACK_OPERATORS, {}, False
    curated = {}
    for job in plane.get("jobs", []):
        curated.setdefault(job["workflow"], job["id"])
    return list(plane.get("operators") or FALLBACK_OPERATORS), curated, True


def build() -> dict[Path, str]:
    from buddy.fleet_runtime.contract import load_manifests

    health = read_json(HEALTH)
    operators, curated, plane_present = control_plane()
    actions_repo, actions_public = actions_prospectus(health)
    wf_jobs, wf_cards = workflow_records(health, operators, curated)
    collection = load_manifests()
    status = read_json(FLEET_STATUS, {})
    templates = bot_templates(collection, operators)
    bots = bot_cards(collection, status, operators)
    bot_job = {
        "id": BOT_JOB_ID, "family": "fleet bots", "title": "Run one fleet bot offline (Run with Buddy)",
        "workflow": BOT_WORKFLOW, "risk_tier": "read_only", "requires_owner_approval": False, "triggerable": True,
        "inputs": {"bot": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]{0,79}$", "max_length": 80}},
        "generated": True,
        "notes": "Sandbox-only, offline, read-only token. The workflow refuses money, destructive, disabled and spec-only bots.",
    }
    division_job = {
        "id": DIVISION_JOB_ID, "family": "fleet divisions", "title": "Run one division's smoke test offline (Run with Buddy)",
        "workflow": BOT_WORKFLOW, "risk_tier": "read_only", "requires_owner_approval": False, "triggerable": True,
        "inputs": {"division": {"type": "string", "pattern": "^[A-Za-z][A-Za-z0-9]{1,40}$", "max_length": 41}},
        "generated": True,
        "notes": "Runs the division's runnable smoke bots offline; refuses UNASSIGNED, money-only and disabled divisions.",
    }
    divisions = division_cards(status, operators)
    registry = {
        "schema": "dreamco.buddy.run_with_buddy.v1",
        "generator": "tools/build_actions_prospectus.py",
        "merge_into": "config/buddy/control-plane.json",
        "control_plane_on_main": plane_present,
        "merge_rule": "Curated control-plane jobs win; generated jobs for the same workflow are marked covered_by_curated_job. The router must still enforce operators, never_dispatch_tiers and writes_code_must_be_pr_only.",
        "operators": operators,
        "jobs": [bot_job, division_job] + [j for j in wf_jobs if j["workflow"] not in {ROUTER_WORKFLOW, BOT_WORKFLOW}],
    }
    cards = {
        "schema": "dreamco.run_prospectus.v1",
        "generator": "tools/build_actions_prospectus.py",
        "required_fields": list(REQUIRED_CARD_FIELDS),
        "truth_boundary": "Cards are generated from workflow files, the Actions health report, bot manifests and the fleet auditor. 'unknown' means no evidence yet. Pages holds no tokens: Run opens a prefilled /buddy issue for the router to check.",
        "operators": operators,
        "counts": {"workflows": len(wf_cards), "workflow_buttons": sum(c["trigger"]["triggerable"] for c in wf_cards),
                   "bots": len(bots), "bot_buttons": sum(r[7] for r in bots),
                   "divisions": len(divisions), "division_buttons": sum(c["trigger"]["triggerable"] for c in divisions)},
        "templates": templates,
        "customize": customize_spec(collection, operators),
        "bot_cards_url": "data/run-prospectus-bots.json",
        "workflows": wf_cards,
        "divisions": divisions,
    }
    bot_payload = {"schema": "dreamco.run_prospectus.bots.v1", "generator": "tools/build_actions_prospectus.py",
                   "resolve": "Expand each row with templates['engine:<engine>'] from data/run-prospectus.json (see resolve() in the generator and fleet-runtime.js)",
                   "blocked_reasons": BLOCKED_REASONS, "columns": BOT_COLUMNS, "rows": bots}
    return {
        OUT_ACTIONS_REPO: json.dumps(actions_repo, indent=2) + "\n",
        OUT_ACTIONS_PUBLIC: json.dumps(actions_public, separators=(",", ":")) + "\n",
        OUT_REGISTRY: json.dumps(registry, indent=1, ensure_ascii=False) + "\n",
        OUT_CARDS: json.dumps(cards, separators=(",", ":"), ensure_ascii=False) + "\n",
        OUT_BOT_CARDS: "{" + json.dumps(bot_payload, ensure_ascii=False)[1:-1].split(', "rows": ')[0] + ', "rows": [\n'
                       + ",\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in bots) + "\n]}\n",
    }


def card_problems(card: dict[str, Any]) -> list[str]:
    problems = []
    for field in REQUIRED_CARD_FIELDS:
        value = card.get(field)
        if value in (None, "", [], {}):
            problems.append(f"{card.get('id')}: missing {field}")
    trigger = card.get("trigger") or {}
    if not trigger.get("allowlist"):
        problems.append(f"{card.get('id')}: empty trigger allowlist")
    if trigger.get("triggerable") and not trigger.get("command"):
        problems.append(f"{card.get('id')}: triggerable without a /buddy command")
    if not trigger.get("triggerable") and not trigger.get("blocked_reason"):
        problems.append(f"{card.get('id')}: not triggerable but no reason given")
    if card.get("risk_tier") in {"money", "destructive"} and trigger.get("triggerable"):
        problems.append(f"{card.get('id')}: money/destructive card is triggerable")
    links = card.get("links") or {}
    for key in ("source", "workflow", "latest_run", "evidence"):
        if not links.get(key):
            problems.append(f"{card.get('id')}: missing links.{key}")
    return problems


def check_buttons(cards_payload: dict[str, Any], registry: dict[str, Any], bot_payload: dict[str, Any]) -> list[str]:
    """Every Run button (registry job or bot) must have a complete prospectus card."""
    problems: list[str] = []
    operators = cards_payload.get("operators") or []
    templates = cards_payload.get("templates") or {}
    wf = {c["id"]: c for c in cards_payload.get("workflows", [])}
    bots = {r[0]: r for r in bot_payload.get("rows", [])}
    for card in cards_payload.get("divisions", []):
        problems += card_problems(card)
    div_names = {d["name"] for d in read_json(DIVISIONS, {"divisions": []})["divisions"]}
    missing_div = div_names - {c["id"].split(":", 1)[1] for c in cards_payload.get("divisions", [])}
    problems += [f"division {n}: no prospectus card" for n in sorted(missing_div)]
    for job in registry.get("jobs", []):
        if job["id"] == DIVISION_JOB_ID:
            continue
        card = wf.get(job["id"])
        if card is None:
            problems.append(f"registry job {job['id']}: no prospectus card")
            continue
        problems += card_problems(card)
        if bool(job["triggerable"]) != bool(card["trigger"]["triggerable"]):
            problems.append(f"registry job {job['id']}: triggerable disagrees with its card")
    plane = read_json(CONTROL_PLANE)
    if plane:
        for job in plane.get("jobs", []):
            if job["id"] not in wf and not any(c["links"]["workflow"].endswith("/" + job["workflow"]) for c in wf.values()):
                problems.append(f"control-plane job {job['id']}: no prospectus card for {job['workflow']}")
    for card in bots.values():
        problems += card_problems(resolve(card, templates, operators))
    status = read_json(FLEET_STATUS, {})
    for row in status.get("bots", []):
        if row[0] not in bots:
            problems.append(f"bot {row[0]}: no prospectus card")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--check", action="store_true", help="fail if outputs are stale or the workflow count drifted")
    parser.add_argument("--check-buttons", action="store_true", help="fail if any Run button lacks a complete prospectus")
    args = parser.parse_args(argv)
    live_count = len(list(WORKFLOWS.glob("*.y*ml")))
    health = read_json(HEALTH)
    if health.get("workflow_count") != live_count:
        msg = (f"Actions health report covers {health.get('workflow_count')} workflows but .github/workflows has {live_count}. "
               "Run: python3 tools/audit_actions_health.py && python3 tools/build_actions_prospectus.py")
        if args.check or args.check_buttons:
            print(msg, file=sys.stderr)
            return 1
        print("warning: " + msg, file=sys.stderr)
    outputs = build()
    if args.check or args.check_buttons:
        rc = 0
        if args.check:
            stale = [p.relative_to(ROOT).as_posix() for p, text in outputs.items()
                     if not p.exists() or p.read_text(encoding="utf-8") != text]
            if stale:
                print("stale: " + ", ".join(stale) + ". Run: python3 tools/build_actions_prospectus.py", file=sys.stderr)
                rc = 1
        if args.check_buttons:
            problems = check_buttons(json.loads(outputs[OUT_CARDS]), json.loads(outputs[OUT_REGISTRY]),
                                     json.loads(outputs[OUT_BOT_CARDS]))
            if problems:
                print(f"{len(problems)} Run button(s) without a complete prospectus:\n  " + "\n  ".join(problems[:50]), file=sys.stderr)
                rc = 1
        if rc == 0:
            cards = json.loads(outputs[OUT_CARDS])
            print(json.dumps({"ok": True, "live_workflows": live_count, **cards["counts"]}))
        return rc
    for path, text in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    cards = json.loads(outputs[OUT_CARDS])
    print(f"Generated Actions prospectus: {cards['counts']['workflows']} workflows; run prospectus: "
          f"{cards['counts']['workflow_buttons']} workflow buttons, {cards['counts']['bot_buttons']}/{cards['counts']['bots']} bot buttons")
    return 0


if __name__ == "__main__":
    sys.exit(main())
