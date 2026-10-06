"""Validate and apply `/buddy customize` patches from GitHub Pages.

Pages is static and public, so it never holds a token. Its Customize form
builds a fenced YAML patch and opens a prefilled issue. The Buddy command
router (control plane) checks the actor's allowlist + write permission, then
calls this module, which:

* parses a deliberately tiny YAML subset (flat ``key: value`` lines plus one
  nested ``capabilities:`` map; no anchors, tags, lists or multi-docs);
* accepts only the editable fields below, each with its own validator;
* rejects anything that touches secrets, money, deletes, permissions,
  workflows, engines, readiness or evidence;
* writes the accepted values to ``config/bots/customizations.json`` (or
  ``config/files/prospectus-overrides.json`` for ``file:`` targets) so the
  router can commit them on a branch and open a PR. Nothing is applied to
  ``main`` directly and nothing here talks to the network.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .contract import ROOT, load_manifests

BOT_STORE = ROOT / "config" / "bots" / "customizations.json"
FILE_STORE = ROOT / "config" / "files" / "prospectus-overrides.json"

# The model choices are the gateway's server-side aliases
# (buddy.openrouter.gateway.BuddyGateway.resolve_model). Raw provider model
# ids are not selectable from Pages.
MODEL_ALLOWLIST = ("dreamco/auto", "dreamco/budget", "dreamco/coding", "dreamco/fast", "dreamco/reasoning", "dreamco/vision")

BOT_FIELDS = {
    "enabled": "boolean: false hides the bot's Run button and makes the runtime refuse runs",
    "display_name": "string, 3-80 chars",
    "prompt": "string, up to 2000 chars: extra instructions prepended to the bot's objective",
    "model": "one of " + ", ".join(MODEL_ALLOWLIST),
    "schedule": "5-field cron (UTC) with a fixed minute and hour, or 'off'",
    "division": "an existing division name",
    "capabilities": "map of existing capability -> true/false (at least one stays enabled)",
}
FILE_FIELDS = {
    "purpose": "string, 10-300 chars: replaces the auto-summary",
    "owner": "an existing bot slug or division name",
}
# Named so the error message is explicit even when the key would also fail
# the allowlist check.
FORBIDDEN_KEY_RE = re.compile(
    r"secret|token|api[_-]?key|password|credential|env|permission|workflow|approval|ceiling|run_policy|"
    r"money|payment|payout|price|billing|stripe|delete|remove|purge|engine|readiness|state|evidence|"
    r"production|claimable|mastered|frontier|live|tools?$|sources|flags", re.I)
SECRET_VALUE_RE = re.compile(r"(?<![A-Za-z0-9])(sk-[A-Za-z0-9_-]{8,}|gh[pousr]_[A-Za-z0-9]{20,}|xox[abp]-|AKIA[0-9A-Z]{12,}|-----BEGIN)")
CRON_FIELD = r"(\*|\d{1,2}(-\d{1,2})?(,\d{1,2}(-\d{1,2})?)*)(/\d{1,2})?"
CRON_RE = re.compile(rf"^(\d{{1,2}}) (\d{{1,2}}|\d{{1,2}}(,\d{{1,2}})+) {CRON_FIELD} {CRON_FIELD} {CRON_FIELD}$")
KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_ .:/()&+-]{0,119}$")
FENCE_RE = re.compile(r"```ya?ml\s*\n(.*?)\n```", re.S)
TARGET_RE = re.compile(r"/buddy\s+customize\s+(\S+)")


class PatchError(ValueError):
    """A patch was rejected. ``errors`` lists every reason."""

    def __init__(self, errors: list[str]):
        super().__init__("; ".join(errors))
        self.errors = errors


def _scalar(raw: str) -> Any:
    raw = raw.strip()
    if raw in {"true", "false"}:
        return raw == "true"
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
        if raw[0] == '"':
            return json.loads(raw)
        return raw[1:-1].replace("''", "'")
    if raw[:1] in {"&", "*", "!", "[", "{", "|", ">"}:
        raise PatchError([f"unsupported YAML construct: {raw[:20]!r} (use plain or quoted scalars)"])
    return raw


def parse_patch_yaml(text: str) -> dict[str, Any]:
    """Parse the restricted YAML subset the Pages form emits."""
    result: dict[str, Any] = {}
    nested: dict[str, Any] | None = None
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.strip() in {"---", "..."}:
            raise PatchError([f"line {number}: multi-document YAML is not accepted"])
        indented = line.startswith((" ", "\t"))
        key, sep, value = line.strip().partition(":")
        key = key.strip().strip("\"'")
        if not sep or not KEY_RE.match(key):
            raise PatchError([f"line {number}: expected 'key: value'"])
        if indented:
            if nested is None:
                raise PatchError([f"line {number}: unexpected indentation"])
            if key in nested:
                raise PatchError([f"line {number}: duplicate key {key!r}"])
            nested[key] = _scalar(value)
            continue
        if key in result:
            raise PatchError([f"line {number}: duplicate key {key!r}"])
        if value.strip() == "":
            nested = result[key] = {}
        else:
            nested = None
            result[key] = _scalar(value)
    return result


def extract_from_issue(body: str) -> tuple[str, dict[str, Any]]:
    """Return (target, patch) from a `/buddy customize <target>` issue body."""
    target = TARGET_RE.search(body or "")
    fence = FENCE_RE.search(body or "")
    if not target or not fence:
        raise PatchError(["issue must contain '/buddy customize <bot-id>' and one ```yaml fenced patch"])
    return target.group(1), parse_patch_yaml(fence.group(1))


def _check_text(value: Any, field: str, low: int, high: int) -> list[str]:
    if not isinstance(value, str):
        return [f"{field}: must be a string"]
    errors = []
    if not low <= len(value.strip()) <= high:
        errors.append(f"{field}: length must be {low}-{high} characters")
    if SECRET_VALUE_RE.search(value):
        errors.append(f"{field}: looks like it contains a credential; secrets are never accepted")
    if re.search(r"<\s*script|javascript:", value, re.I):
        errors.append(f"{field}: markup/script is not accepted")
    return errors


def validate_bot_patch(slug: str, patch: dict[str, Any], collection: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return the normalised patch or raise PatchError with every problem."""
    from .contract import expand

    collection = collection or load_manifests()
    bots = {b["slug"]: b for b in collection["bots"]}
    errors: list[str] = []
    if slug not in bots:
        raise PatchError([f"unknown bot {slug!r}"])
    compact = bots[slug]
    if compact.get("run") in {"blocked_money", "blocked_destructive"}:
        raise PatchError([f"{slug} is a {compact['run'].split('_')[1]} bot; it cannot be customized from Pages"])
    if not isinstance(patch, dict) or not patch:
        raise PatchError(["patch must be a non-empty mapping"])
    manifest = expand(compact, collection)
    divisions = {b["division"] for b in collection["bots"] if b.get("division")}
    clean: dict[str, Any] = {}
    for key, value in patch.items():
        if key not in BOT_FIELDS:
            reason = "is protected (secrets, money, deletes, permissions, workflows and readiness are never editable)" if FORBIDDEN_KEY_RE.search(key) else "is not an editable field"
            errors.append(f"{key}: {reason}")
            continue
        if key == "enabled":
            if not isinstance(value, bool):
                errors.append("enabled: must be true or false")
        elif key == "display_name":
            errors += _check_text(value, key, 3, 80)
        elif key == "prompt":
            errors += _check_text(value, key, 1, 2000)
        elif key == "model":
            if value not in MODEL_ALLOWLIST:
                errors.append(f"model: {value!r} is not on the allowlist ({', '.join(MODEL_ALLOWLIST)})")
        elif key == "schedule":
            match = CRON_RE.match(value) if isinstance(value, str) else None
            in_range = bool(match) and int(match.group(1)) <= 59 and all(int(h) <= 23 for h in match.group(2).split(","))
            if value != "off" and not in_range:
                errors.append("schedule: must be 'off' or a 5-field cron with a fixed minute and hour (e.g. '17 9 * * 1')")
        elif key == "division":
            if value not in divisions:
                errors.append(f"division: {value!r} is not an existing division")
        elif key == "capabilities":
            caps = manifest["capabilities"]
            if not isinstance(value, dict) or not value:
                errors.append("capabilities: must be a map of capability -> true/false")
            else:
                unknown = [c for c in value if c not in caps]
                if unknown:
                    errors.append(f"capabilities: unknown capability {unknown[0]!r} (only existing capabilities can be toggled)")
                if any(not isinstance(v, bool) for v in value.values()):
                    errors.append("capabilities: values must be true or false")
                if not unknown and all(value.get(c, True) is False for c in caps):
                    errors.append("capabilities: at least one capability must stay enabled")
        clean[key] = value
    if errors:
        raise PatchError(errors)
    return clean


def validate_file_patch(path: str, patch: dict[str, Any], known_paths: set[str], owners: set[str]) -> dict[str, Any]:
    errors: list[str] = []
    if path not in known_paths:
        raise PatchError([f"unknown file {path!r}"])
    if not isinstance(patch, dict) or not patch:
        raise PatchError(["patch must be a non-empty mapping"])
    for key, value in patch.items():
        if key not in FILE_FIELDS:
            errors.append(f"{key}: is not an editable file-prospectus field (file contents are never edited from Pages)")
        elif key == "purpose":
            errors += _check_text(value, key, 10, 300)
        elif key == "owner" and value not in owners:
            errors.append(f"owner: {value!r} is not an existing bot slug or division")
    if errors:
        raise PatchError(errors)
    return dict(patch)


def _merge_store(store: Path, key: str, clean: dict[str, Any]) -> dict[str, Any]:
    data = json.loads(store.read_text(encoding="utf-8")) if store.exists() else {"schema": "dreamco.customizations.v1", "entries": {}}
    entry = {**data["entries"].get(key, {}), **clean}
    data["entries"][key] = dict(sorted(entry.items()))
    data["entries"] = dict(sorted(data["entries"].items()))
    store.parent.mkdir(parents=True, exist_ok=True)
    store.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    return data["entries"][key]


def apply_bot_patch(slug: str, patch: dict[str, Any], store: Path = BOT_STORE) -> dict[str, Any]:
    return _merge_store(store, slug, validate_bot_patch(slug, patch))


def load_customizations(store: Path = BOT_STORE) -> dict[str, dict[str, Any]]:
    if not store.exists():
        return {}
    return json.loads(store.read_text(encoding="utf-8")).get("entries", {})


def apply_customization(manifest: dict[str, Any], custom: dict[str, Any]) -> dict[str, Any]:
    """Overlay an accepted customization on an expanded manifest."""
    if not custom:
        return manifest
    out = dict(manifest)
    out["customized_fields"] = sorted(custom)
    if "display_name" in custom:
        out["name"] = custom["display_name"]
    if "division" in custom:
        out["division"] = custom["division"]
    if "enabled" in custom:
        out["enabled"] = custom["enabled"]
    if "prompt" in custom:
        out["prompt"] = custom["prompt"]
    if "schedule" in custom:
        out["schedule"] = custom["schedule"]
    if "model" in custom:
        out["model_alias"] = custom["model"]
    if "capabilities" in custom:
        out["capabilities"] = [c for c in out["capabilities"] if custom["capabilities"].get(c, True)]
    return out
