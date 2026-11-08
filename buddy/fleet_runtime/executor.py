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
            learning_packet = None
            learning_request = (task.get("input") or {}).get("learning_request")
            if learning_request is not None:
                if not isinstance(learning_request, dict):
                    return self._finish(manifest, task, "learning_blocked", "none", permission,
                                        {"input": in_guard}, None,
                                        {"type": "invalid_learning_request", "message": "input.learning_request must be an object."}, stamp)
                try:
                    from buddy.bootcamp.live_learning_bridge import prepare_learning_execution
                    from buddy.bootcamp.task_learning_router import LearningResource, TaskRequest

                    raw_resources = learning_request.get("resources") or []
                    resources = []
                    for raw in raw_resources:
                        item = dict(raw)
                        item["skills"] = tuple(item.get("skills") or ())
                        item["modes"] = tuple(item.get("modes") or ("read", "practice"))
                        resources.append(LearningResource(**item))
                    learning_task = TaskRequest(
                        request=str(learning_request.get("request") or task.get("objective") or ""),
                        skills=tuple(learning_request.get("skills") or ()),
                        preferred_mode=str(learning_request.get("preferred_mode") or "practice"),
                        max_cost_per_hour_usd=float(learning_request.get("max_cost_per_hour_usd") or 0.0),
                        allow_paid=bool(learning_request.get("allow_paid", False)),
                        allow_external_access=bool(learning_request.get("allow_external_access", False)),
                    )
                    learning_packet = prepare_learning_execution(
                        learning_task, resources,
                        request_id=str(learning_request.get("request_id") or task.get("task_id") or "learning-request"),
                        task_id=str(learning_request.get("task_id") or task.get("task_id") or "learning-task"),
                        sandbox_profile=str(learning_request.get("sandbox_profile") or "fleet-runtime-sandbox"),
                        allowed_tools=learning_request.get("allowed_tools") or (),
                        source_rights_refs=learning_request.get("source_rights_refs") or (),
                        original_lesson_id=learning_request.get("original_lesson_id"),
                        practice_task_ids=learning_request.get("practice_task_ids") or (),
                        benchmark_ids=learning_request.get("benchmark_ids") or (),
                        compute_budget_usd=float(learning_request.get("compute_budget_usd") or 0.0),
                        time_budget_seconds=int(learning_request.get("time_budget_seconds") or 300),
                        approval_requirements=learning_request.get("approval_requirements") or (),
                    )
                except (TypeError, ValueError, KeyError) as exc:
                    return self._finish(manifest, task, "learning_blocked", "none", permission,
                                        {"input": in_guard}, None,
                                        {"type": "invalid_learning_request", "class": type(exc).__name__}, stamp)
                if learning_packet.get("status") == "blocked":
                    return self._finish(manifest, task, "learning_blocked", "none", permission,
                                        {"input": in_guard}, learning_packet, None, stamp)
                if learning_packet.get("status") == "awaiting_user_approval":
                    return self._finish(manifest, task, "approval_required", "none", permission,
                                        {"input": in_guard}, learning_packet, None, stamp)
                task.setdefault("input", {})["learning_execution"] = learning_packet
                if engine_name == "workflow":
                    route_steps = learning_packet.get("route", {}).get("course_plan", [])
                    existing_steps = task["input"].get("steps") or []
                    task["input"]["steps"] = route_steps + existing_steps

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
            if learning_packet is not None:
                result = dict(result)
                result["learning_execution"] = learning_packet
                        status = "ok" if result.get("status") == "ok" else result.get("status", "ok")
            return self._finish(manifest, task, status, mode, permission, guards, result, None, stamp)
        except Exception as exc:  # error_handling profile: structured, never raises
            return self._finish(manifest, task, "error", "none", none_perm, {}, None,
                                {"type": "exception", "class": type(exc).__name__, "message": str(exc)[:300]}, stamp)


def run_bot(slug: str, task: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    return FleetExecutor(**kwargs).run(slug, task)
