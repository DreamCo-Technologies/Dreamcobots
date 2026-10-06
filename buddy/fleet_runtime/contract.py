"""Universal Bot Runtime Contract constants, loading and light validation.

The JSON Schema lives at config/bots/bot-runtime-contract.schema.json. This
module carries a dependency-free validator for the subset of JSON Schema the
runtime needs (type/required/enum/const/pattern) so CI does not need the
``jsonschema`` package. Tests cross-check it against the schema file.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "config" / "bots" / "bot-runtime-contract.schema.json"
MANIFESTS_PATH = ROOT / "config" / "bots" / "bot-manifests.generated.json"
FIXTURES_PATH = ROOT / "config" / "bots" / "smoke-fixtures.json"
EVIDENCE_DIR = ROOT / "evidence" / "fleet-runtime"

# The 16 required pieces, in contract order. ``where`` says which artifact
# proves the piece; the auditor resolves each one per bot.
CONTRACT_PIECES: tuple[dict[str, str], ...] = (
    {"id": "manifest", "where": "config/bots/bot-manifests.generated.json entry validates against the contract schema"},
    {"id": "division", "where": "division resolves to an App_bots/<Division>.json manifest"},
    {"id": "capabilities", "where": "at least one bot-specific capability (tier boilerplate is not counted)"},
    {"id": "runtime_adapter", "where": "manifest maps to an implemented shared engine (not 'unmapped')"},
    {"id": "model_router", "where": "named model/router profile with deterministic offline fallback"},
    {"id": "tools_apis", "where": "every declared tool resolves to a runtime tool profile"},
    {"id": "io_schema", "where": "engine input/output schema assigned"},
    {"id": "permissions", "where": "permission ceiling derived from buddy_os/governance/approval_policy.yaml"},
    {"id": "error_handling", "where": "named error-handling profile; executor returns structured errors"},
    {"id": "unit_test", "where": "engine unit tests exist in tests/test_fleet_runtime_executor.py"},
    {"id": "smoke_test", "where": "bot-specific smoke fixture in config/bots/smoke-fixtures.json passes offline"},
    {"id": "benchmark", "where": "at least one declared benchmark has a measured result in committed evidence"},
    {"id": "health_status", "where": "auditor executed the generic smoke task and recorded health"},
    {"id": "pages_route", "where": "Pages card route exists on website/fleet-runtime.html"},
    {"id": "evidence_record", "where": "committed evidence/fleet-runtime/<slug>.json with release_readiness fields"},
    {"id": "readiness_state", "where": "state computed by tools/fleet_runtime_audit.py, never hand-set"},
)
PIECE_IDS = tuple(piece["id"] for piece in CONTRACT_PIECES)

ENGINES = ("drafting", "analysis", "classification", "workflow")

# Ordered ladder (BLOCKED is off-ladder). Mirrors release_readiness.yaml:
# discovered->implemented->tested->verified->canary->production, with
# CONNECTED inserted between tested and verified for dependency wiring.
READINESS_STATES = ("SPEC_ONLY", "IMPLEMENTED", "TESTED", "CONNECTED", "VERIFIED", "PRODUCTION")
STATE_RANK = {state: rank for rank, state in enumerate(READINESS_STATES)}
STATE_RANK["BLOCKED"] = -1

# Capabilities appended to every profile by tier (see server/seed-bots.ts
# TIER_FEATURES). They are product packaging, not bot capabilities.
TIER_BOILERPLATE = frozenset(
    {
        "advanced analytics dashboard",
        "priority email support",
        "api access",
        "basic analytics",
        "email support",
        "community access",
        "custom integrations",
        "webhook notifications",
        "data export (csv/json)",
        "scheduled automations",
        "multi-user access",
        "dedicated account manager",
    }
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=4)
def _load_manifest_file(path_str: str) -> dict[str, Any]:
    return read_json(Path(path_str))


def load_manifests(path: Path | None = None) -> dict[str, Any]:
    """Return the generated manifest collection (cached per path)."""
    return _load_manifest_file(str(path or MANIFESTS_PATH))


def load_schema() -> dict[str, Any]:
    return read_json(SCHEMA_PATH)


def load_fixtures(path: Path | None = None, include_generated: bool = True) -> dict[str, Any]:
    """Generated fixtures (buddy.fleet_runtime.fixtures) overlaid by hand-written config/bots/smoke-fixtures.json."""
    if path is not None:
        return read_json(path) if path.exists() else {"fixtures": {}}
    merged: dict[str, Any] = {}
    if include_generated and MANIFESTS_PATH.exists():
        from .fixtures import build_fixtures

        merged.update(build_fixtures(load_manifests())["fixtures"])
    if FIXTURES_PATH.exists():
        merged.update(read_json(FIXTURES_PATH).get("fixtures", {}))
    return {"fixtures": merged}


_TYPE_MAP = {
    "object": dict,
    "array": list,
    "string": str,
    "boolean": bool,
    "integer": int,
    "number": (int, float),
    "null": type(None),
}


def _type_ok(value: Any, expected: Any) -> bool:
    names = expected if isinstance(expected, list) else [expected]
    for name in names:
        py = _TYPE_MAP[name]
        if name in {"integer", "number"} and isinstance(value, bool):
            continue
        if isinstance(value, py):
            return True
    return False


def validate(value: Any, schema: dict[str, Any], root: dict[str, Any] | None = None, path: str = "$") -> list[str]:
    """Validate ``value`` against a JSON-Schema subset. Returns error strings."""
    root = root or schema
    errors: list[str] = []
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/"):
            return [f"{path}: unsupported $ref {ref}"]
        target: Any = root
        for part in ref[2:].split("/"):
            target = target[part]
        return validate(value, target, root, path)
    if "type" in schema and not _type_ok(value, schema["type"]):
        return [f"{path}: expected {schema['type']}, got {type(value).__name__}"]
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} not in {schema['enum']}")
    if isinstance(value, str):
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{path}: {value!r} does not match {schema['pattern']}")
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{path}: shorter than {schema['minLength']}")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: below minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: above maximum {schema['maximum']}")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing required '{key}'")
        props = schema.get("properties", {})
        for key, sub in props.items():
            if key in value:
                errors.extend(validate(value[key], sub, root, f"{path}.{key}"))
        extra = schema.get("additionalProperties")
        if isinstance(extra, dict):
            for key, item in value.items():
                if key not in props:
                    errors.extend(validate(item, extra, root, f"{path}.{key}"))
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{path}: fewer than {schema['minItems']} items")
        if isinstance(schema.get("items"), dict):
            for index, item in enumerate(value):
                errors.extend(validate(item, schema["items"], root, f"{path}[{index}]"))
    return errors


def validate_bot_manifest(manifest: dict[str, Any], schema: dict[str, Any] | None = None) -> list[str]:
    schema = schema or load_schema()
    return validate(manifest, schema["$defs"]["botManifest"], schema, f"$.bots[{manifest.get('slug', '?')}]")


def validate_collection(collection: dict[str, Any], schema: dict[str, Any] | None = None) -> list[str]:
    return validate(collection, schema or load_schema())


def expand(compact: dict[str, Any], collection: dict[str, Any], with_content: bool = True) -> dict[str, Any]:
    """Expand a compact generated entry into the full 16-piece manifest.

    ``with_content`` loads description/capabilities from the canonical profile
    sources (App_bots / bots/*.md) so text is never duplicated in the
    generated file.
    """
    defaults = collection["defaults"]
    slug = compact["slug"]
    engine = compact["engine"]
    mapped = engine != "unmapped"

    def sub(template: str) -> str:
        return template.replace("{slug}", slug).replace("{engine}", engine)

    manifest: dict[str, Any] = {
        "slug": slug,
        "name": compact["name"],
        "division": compact["division"],
        "category": compact.get("category", ""),
        "tier": compact.get("tier", ""),
        "description": "",
        "capabilities": [],
        "tier_features_dropped": compact.get("tier_features_dropped", 0),
        "engine": engine,
        "engine_confidence": compact.get("engine_confidence", 0.0),
        "runtime_adapter": f"shared_engine:{engine}" if mapped else None,
        "model_router": "offline_first" if engine == "drafting" else "offline_only",
        "tools": list(compact.get("tools", defaults["tools"])),
        "external_api_candidates": list(compact.get("api", [])),
        "io_schema": f"engine:{engine}" if mapped else None,
        "permissions": {"ceiling": compact["ceiling"], "live_actions_declared": bool(compact.get("live")),
                        "approval_policy": defaults["approval_policy"]},
        "error_handling": defaults["error_handling"],
        "tests": {"unit": defaults["unit_test"] if mapped else None, "smoke": sub(defaults["smoke"])},
        "benchmark": {"declared": compact.get("bench", 0), "measured": 0},
        "health": sub(defaults["health"]),
        "pages_route": sub(defaults["pages_route"]),
        "evidence": sub(defaults["evidence"]),
        "readiness": {"claimed_production_ready": bool(compact.get("claims_ready")),
                      "computed_by": "tools/fleet_runtime_audit.py"},
        "sources": list(compact["sources"]),
        "flags": list(compact.get("flags", [])),
        "run_policy": compact.get("run", "spec_only" if not mapped else "allowed"),
    }
    if compact.get("seed_division"):
        manifest["seed_division"] = compact["seed_division"]
    if with_content:
        from .sources import profile_content

        content = profile_content(slug)
        manifest["description"] = content["description"]
        manifest["capabilities"] = [c[:120] for c in content["capabilities_raw"]
                                    if c.strip().lower() not in TIER_BOILERPLATE][:12]
        if content.get("target_users"):
            manifest["target_users"] = content["target_users"]
    return manifest
