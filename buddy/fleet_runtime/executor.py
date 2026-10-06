"""Generic bot executor: manifest -> capability engine -> router -> policy -> evidence."""
from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from . import engines, evidence, permissions
from .customize import apply_customization, effective_customization, load_customizations
from .contract import expand, load_manifests, validate, validate_bot_manifest, load_schema

try:  # Reuse Buddy's shared guardrails; tolerate absence in stripped builds.
    from buddy.safety.guardrails import review as _guardrail_review
except Exception:  # pragma: no cover
    _guardrail_review = None

TASK_SCHEMA = {
    "type": "object",
    "required": ["objective"],
    "properties": {
        "objective": {"type": "string", "minLength": 1},
        "input": {"type": "object"},
        "action_level": {"type": "string"},
    },
}


def guardrail(text: str) -> dict[str, Any]:
    if _guardrail_review is None:
        return {"allowed": True, "reasons": ["guardrails module unavailable"], "source": None}
    verdict = _guardrail_review(text)
    return {"allowed": bool(verdict.get("allowed")), "reasons": verdict.get("reasons", []),
            "source": "buddy.safety.guardrails"}


class FleetExecutor:
    """Run any bot manifest through the shared engines."""

    def __init__(self, manifests_path: Path | None = None, env: dict[str, str] | None = None,
                 collection: dict[str, Any] | None = None, customizations: dict[str, Any] | None = None):
        self.collection = collection or load_manifests(manifests_path)
        self.bots = {bot["slug"]: bot for bot in self.collection["bots"]}
        self.profiles = self.collection["profiles"]
        self.env = env
        self._schema = load_schema()

        self._expanded: dict[str, dict[str, Any]] = {}
        self.customizations = load_customizations() if customizations is None else customizations

    def manifest(self, slug: str) -> dict[str, Any]:
        """Return the expanded 16-piece manifest for ``slug``."""
        if slug not in self.bots:
            raise KeyError(f"unknown bot: {slug}")
        if slug not in self._expanded:
            base = expand(self.bots[slug], self.collection)
            self._expanded[slug] = apply_customization(
                base, effective_customization(self.customizations, slug, base["division"]))
        return self._expanded[slug]

    def _finish(self, manifest, task, status, mode, permission, guards, result, error=None, stamp=False):
        record = evidence.run_record(manifest=manifest, task=task, status=status, mode=mode,
                                     permission=permission, guardrails=guards, result=result,
                                     error=error, stamp=stamp)
        out = {
            "status": status,
            "bot": manifest.get("slug"),
            "engine": manifest.get("engine"),
            "mode": mode,
            "result": result,
            "live_external_action_taken": False,
            "evidence": record,
        }
        if error:
            out["error"] = error
        return out

    def run(self, slug: str, task: dict[str, Any], *, stamp: bool = False) -> dict[str, Any]:
        task = copy.deepcopy(task or {})
        try:
            manifest = self.manifest(slug)
        except KeyError as exc:
            stub = {"slug": slug, "engine": None, "division": None}
            return self._finish(stub, task, "error", "none", {}, {}, None,
                                {"type": "unknown_bot", "message": str(exc)}, stamp)
        none_perm: dict[str, Any] = {}
        try:
            problems = validate_bot_manifest(manifest, self._schema)
            if problems:
                return self._finish(manifest, task, "error", "none", none_perm, {}, None,
                                    {"type": "invalid_manifest", "message": "; ".join(problems[:5])}, stamp)
            engine_name = manifest["engine"]
            if engine_name not in engines.ENGINE_FUNCS:
                return self._finish(manifest, task, "unmapped", "none", none_perm, {}, None,
                                    {"type": "engine_unmapped",
                                     "message": "No shared engine is mapped for this bot; it is spec-only."}, stamp)
            if manifest.get("enabled") is False:
                return self._finish(manifest, task, "disabled", "none", none_perm, {}, None,
                                    {"type": "bot_disabled", "message": "Disabled by an accepted customization."}, stamp)
            task_errors = validate(task, TASK_SCHEMA)
            if task_errors:
                return self._finish(manifest, task, "invalid_input", "none", none_perm, {}, None,
                                    {"type": "invalid_input", "message": "; ".join(task_errors)}, stamp)
            if manifest.get("prompt"):
                task["objective"] = f"{manifest['prompt']}\n\n{task.get('objective', '')}"
            permission = permissions.decide(manifest["permissions"]["ceiling"], task.get("action_level", "sandbox"))
            if not permission["allowed"]:
                return self._finish(manifest, task, "approval_required", "none", permission, {}, None, None, stamp)
            in_guard = guardrail(f"{task.get('objective', '')} {task.get('input', '')}")
            if not in_guard["allowed"]:
                return self._finish(manifest, task, "guardrail_blocked", "none", permission,
                                    {"input": in_guard}, None, None, stamp)
            profile = dict(self.profiles["model_router"][manifest["model_router"]])
            if manifest.get("model_alias") and profile.get("mode") != "offline_only":
                profile["live_alias"] = manifest["model_alias"]
            func = engines.ENGINE_FUNCS[engine_name]
            if engine_name == "drafting":
                result = func(manifest, task, profile, env=self.env)
                mode = result.get("generated_by", "offline_deterministic")
            else:
                result = func(manifest, task, profile)
                mode = "offline_deterministic"
            out_guard = guardrail(str(result))
            guards = {"input": in_guard, "output": out_guard}
            if not out_guard["allowed"]:
                return self._finish(manifest, task, "guardrail_blocked", mode, permission, guards,
                                    {"withheld": True}, None, stamp)
            io_profile = self.profiles["io_schema"][manifest["io_schema"]]
            output_errors = validate(result, io_profile["output"])
            if output_errors:
                return self._finish(manifest, task, "error", mode, permission, guards, result,
                                    {"type": "invalid_output", "message": "; ".join(output_errors[:5])}, stamp)
            status = "ok" if result.get("status") == "ok" else result.get("status", "ok")
            return self._finish(manifest, task, status, mode, permission, guards, result, None, stamp)
        except Exception as exc:  # error_handling profile: structured, never raises
            return self._finish(manifest, task, "error", "none", none_perm, {}, None,
                                {"type": "exception", "class": type(exc).__name__, "message": str(exc)[:300]}, stamp)


def run_bot(slug: str, task: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    return FleetExecutor(**kwargs).run(slug, task)
