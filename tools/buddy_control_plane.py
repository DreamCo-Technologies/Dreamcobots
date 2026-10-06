#!/usr/bin/env python3
"""Buddy control plane: registry check, `/buddy` command router, and status snapshot.

Subcommands
-----------
check               Validate config/buddy/control-plane.json (and cross-check workflows).
list                Print the registry as a table.
route               Handle one issues / issue_comment event (used by buddy-command-router.yml).
status --out PATH   Write the public status snapshot (last run per registered workflow).
publish-registry    Copy the registry to website/data/buddy-control-plane.json (--check to diff).

Security model (fail closed):
* Only jobs in the registry can be dispatched, always on the registry's default_ref.
* Every user-supplied token is matched against strict regexes; nothing is ever passed
  through a shell. Dispatch uses `gh workflow run` with an argument list.
* The actor must be in `operators` AND have write/maintain/admin on the repo (API check).
  Issue-based commands also require the issue author to be an operator.
* Owner-approval jobs require the actor to be in `owners`.
* Money tier, destructive jobs, and `triggerable: false` jobs are never dispatched.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "config" / "buddy" / "control-plane.json"
WORKFLOWS_DIR = ROOT / ".github" / "workflows"
PUBLIC_REGISTRY_PATH = ROOT / "website" / "data" / "buddy-control-plane.json"
# Generated Run with Buddy jobs (one per workflow + fleet bot/division jobs), produced by
# tools/build_actions_prospectus.py. Merged under the curated registry: curated jobs always win.
GENERATED_PATH = ROOT / "config" / "buddy" / "run-with-buddy.generated.json"
PUBLIC_STATUS_PATH = ROOT / "website" / "data" / "buddy-control-status.json"

SCHEMA = "dreamco.buddy.control-plane.v1"
STATUS_SCHEMA = "dreamco.buddy.control-status.v1"
TIERS = ("read_only", "writes_reports", "writes_code", "money")
VERBS = ("run", "status", "list", "help", "customize")

JOB_ID_RE = re.compile(r"^[a-z][a-z0-9_]{1,63}$")
INPUT_KEY_RE = re.compile(r"^[a-z][a-z0-9_]{0,39}$")
INPUT_VALUE_RE = re.compile(r"^[A-Za-z0-9._-]{1,100}$")
LOGIN_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
WORKFLOW_FILE_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,98}\.ya?ml$")
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]{1,100}/[A-Za-z0-9_.-]{1,100}$")
REF_RE = re.compile(r"^[A-Za-z0-9._/-]{1,100}$")
RUN_URL_RE = re.compile(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/actions/runs/\d+")
CUSTOMIZE_TARGET_RE = re.compile(r"^(?:[a-z0-9][a-z0-9-]{1,80}|division:[A-Za-z][A-Za-z0-9]{1,40}|file:[A-Za-z0-9_.][A-Za-z0-9_./-]{0,199})$")
YAML_FENCE_RE = re.compile(r"^```ya?ml[ \t]*$(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)
CUSTOMIZE_JOB_ID = "buddy_customize_apply"
CUSTOMIZE_BODY_MAX = 4000
GENERATED_FIELDS = ("id", "family", "title", "workflow", "risk_tier", "requires_owner_approval", "triggerable",
                    "blocked_reason", "destructive", "inputs", "fixed_inputs", "notes")
INPUTS_FENCE_RE = re.compile(r"^```buddy-inputs[ \t]*$(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)

COMMAND_LINE_MAX = 300
MAX_INPUTS = 10
WRITE_PERMISSIONS = {"admin", "maintain", "write"}
MARKER = "<!-- buddy-command-router -->"
ISSUE_MARKER = "<!-- buddy-command-router:issue-handled -->"
YAML_REQUIRED = "PyYAML is required for the workflow cross-check (pip install pyyaml)"
PUSH_TO_MAIN_RE = re.compile(r"^\s*git push(\s*$|\s+(origin\s+)?(main|HEAD|HEAD:main)\s*$)", re.MULTILINE)


class CommandError(ValueError):
    """A user command was rejected. The message is safe to show back to the user."""


# --------------------------------------------------------------------------- registry


def load_registry(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def merge_generated(registry: dict[str, Any], generated: dict[str, Any] | None,
                    workflows_dir: Path | None = None) -> tuple[dict[str, Any], list[str]]:
    """Return (registry + generated jobs, skipped notes). Curated jobs always win.

    A generated job is added only when its id and workflow are not already curated and it
    passes check_registry on its own (each job fails closed individually; a bad generated job
    never invalidates the curated registry).
    """
    merged = dict(registry)
    jobs = list(registry.get("jobs") or [])
    skipped: list[str] = []
    if not generated:
        return merged, skipped
    curated_ids = {j.get("id") for j in jobs if isinstance(j, dict)}
    curated_workflows = {j.get("workflow") for j in jobs if isinstance(j, dict)}
    for raw in generated.get("jobs") or []:
        if not isinstance(raw, dict):
            continue
        job_id = raw.get("id")
        if job_id in curated_ids:
            continue
        if raw.get("workflow") in curated_workflows and not str(job_id).startswith("fleet_"):
            continue
        job = {k: raw[k] for k in GENERATED_FIELDS if k in raw}
        job["generated"] = True
        errors = check_registry(dict(registry, jobs=[job]), workflows_dir)
        if errors:
            skipped.append(f"{job_id}: {errors[0]}")
            continue
        jobs.append(job)
        curated_ids.add(job_id)
    merged["jobs"] = jobs
    return merged, skipped


def load_merged(path: Path = REGISTRY_PATH, generated_path: Path | None = GENERATED_PATH,
                workflows_dir: Path | None = None) -> tuple[dict[str, Any], list[str]]:
    registry = load_registry(path)
    generated = None
    if generated_path is not None and generated_path.is_file():
        try:
            generated = json.loads(generated_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return registry, ["generated registry unreadable; using curated jobs only"]
    return merge_generated(registry, generated, workflows_dir)


def jobs_by_id(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {job["id"]: job for job in registry.get("jobs", []) if isinstance(job, dict) and "id" in job}


def _casefold_set(items: Any) -> set[str]:
    return {str(x).casefold() for x in items or []}


def _load_yaml(path: Path) -> Any:
    import yaml  # PyYAML; only needed for the workflow cross-check

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _workflow_on(doc: dict[str, Any]) -> Any:
    # PyYAML (YAML 1.1) parses the bare key `on` as boolean True.
    return doc.get("on", doc.get(True))


def _permission_writes(perms: Any) -> bool:
    """True when a permissions block may grant any write scope (or is missing)."""
    if perms is None:
        return True  # default token permissions may be write
    if isinstance(perms, str):
        return perms not in ("read-all", "{}")
    if isinstance(perms, dict):
        return any(str(v) == "write" for v in perms.values())
    return True


def check_input_spec(job_id: str, name: str, spec: Any) -> list[str]:
    errors: list[str] = []
    where = f"jobs.{job_id}.inputs.{name}"
    if not INPUT_KEY_RE.match(name):
        errors.append(f"{where}: invalid input name")
    if not isinstance(spec, dict):
        return errors + [f"{where}: spec must be an object"]
    kind = spec.get("type")
    if kind == "choice":
        options = spec.get("options")
        if not isinstance(options, list) or not options:
            errors.append(f"{where}: choice needs non-empty options")
        elif not all(isinstance(o, str) and INPUT_VALUE_RE.match(o) for o in options):
            errors.append(f"{where}: options must match {INPUT_VALUE_RE.pattern}")
        if "default" in spec and spec["default"] not in (options or []):
            errors.append(f"{where}: default not in options")
    elif kind == "boolean":
        if "default" in spec and not isinstance(spec["default"], bool):
            errors.append(f"{where}: boolean default must be true/false")
    elif kind == "string":
        pattern = spec.get("pattern")
        if not isinstance(pattern, str) or not pattern.startswith("^") or not pattern.endswith("$"):
            errors.append(f"{where}: string inputs need an anchored pattern")
        else:
            try:
                re.compile(pattern)
            except re.error:
                errors.append(f"{where}: pattern does not compile")
        if not isinstance(spec.get("max_length"), int) or not 1 <= spec["max_length"] <= 100:
            errors.append(f"{where}: string inputs need max_length 1..100")
    else:
        errors.append(f"{where}: type must be choice, boolean, or string")
    return errors


def check_registry(
    registry: dict[str, Any],
    workflows_dir: Path | None = WORKFLOWS_DIR,
) -> list[str]:
    """Return a list of schema/policy errors. Empty list means valid.

    When workflows_dir is given, each job is cross-checked against its workflow file
    (exists, has workflow_dispatch, declared inputs exist, read_only really is read-only).
    """
    errors: list[str] = []
    if registry.get("schema") != SCHEMA:
        errors.append(f"schema must be {SCHEMA}")
    if not REPO_RE.match(str(registry.get("repository", ""))):
        errors.append("repository must be owner/name")
    if not REF_RE.match(str(registry.get("default_ref", ""))):
        errors.append("default_ref is invalid")
    if not isinstance(registry.get("command_label"), str) or not registry["command_label"]:
        errors.append("command_label is required")
    router = registry.get("router_workflow")
    if not isinstance(router, str) or not WORKFLOW_FILE_RE.match(router):
        errors.append("router_workflow must be a workflow file name")

    operators = registry.get("operators")
    owners = registry.get("owners")
    if not isinstance(operators, list) or not operators:
        errors.append("operators must be a non-empty list")
        operators = []
    if not isinstance(owners, list) or not owners:
        errors.append("owners must be a non-empty list")
        owners = []
    for login in list(operators) + list(owners):
        if not isinstance(login, str) or not LOGIN_RE.match(login):
            errors.append(f"invalid GitHub login: {login!r}")
    if not _casefold_set(owners) <= _casefold_set(operators):
        errors.append("every owner must also be an operator")

    tiers = registry.get("risk_tiers")
    if not isinstance(tiers, dict) or set(tiers) != set(TIERS):
        errors.append(f"risk_tiers must define exactly {', '.join(TIERS)}")
        tiers = {}
    elif tiers["money"].get("dispatchable") is not False:
        errors.append("risk_tiers.money.dispatchable must be false")

    jobs = registry.get("jobs")
    if not isinstance(jobs, list) or not jobs:
        return errors + ["jobs must be a non-empty list"]

    seen: set[str] = set()
    for job in jobs:
        if not isinstance(job, dict):
            errors.append("each job must be an object")
            continue
        job_id = str(job.get("id", ""))
        if not JOB_ID_RE.match(job_id):
            errors.append(f"invalid job id: {job_id!r}")
            continue
        if job_id in seen:
            errors.append(f"duplicate job id: {job_id}")
        seen.add(job_id)
        for key in ("family", "title"):
            if not isinstance(job.get(key), str) or not job[key]:
                errors.append(f"jobs.{job_id}.{key} is required")
        tier = job.get("risk_tier")
        if tier not in TIERS:
            errors.append(f"jobs.{job_id}.risk_tier must be one of {TIERS}")
        for key in ("requires_owner_approval", "triggerable"):
            if not isinstance(job.get(key), bool):
                errors.append(f"jobs.{job_id}.{key} must be true/false")
        if "destructive" in job and not isinstance(job["destructive"], bool):
            errors.append(f"jobs.{job_id}.destructive must be true/false")
        workflow = job.get("workflow")
        if not isinstance(workflow, str) or not WORKFLOW_FILE_RE.match(workflow):
            errors.append(f"jobs.{job_id}.workflow must be a workflow file name")
            workflow = None
        if workflow and workflow == router:
            errors.append(f"jobs.{job_id}: the router cannot dispatch itself")

        triggerable = job.get("triggerable") is True
        if tier == "money" and triggerable:
            errors.append(f"jobs.{job_id}: money tier can never be triggerable")
        if job.get("destructive") and triggerable:
            errors.append(f"jobs.{job_id}: destructive jobs can never be triggerable")
        if tier == "writes_code" and job.get("requires_owner_approval") is not True:
            errors.append(f"jobs.{job_id}: writes_code requires owner approval")
        if tier == "money" and job.get("requires_owner_approval") is not True:
            errors.append(f"jobs.{job_id}: money tier requires owner approval")
        if not triggerable and not job.get("blocked_reason"):
            errors.append(f"jobs.{job_id}: non-triggerable jobs need a blocked_reason")

        inputs = job.get("inputs", {})
        if not isinstance(inputs, dict):
            errors.append(f"jobs.{job_id}.inputs must be an object")
            inputs = {}
        if len(inputs) > MAX_INPUTS:
            errors.append(f"jobs.{job_id}: at most {MAX_INPUTS} inputs")
        for name, spec in inputs.items():
            errors.extend(check_input_spec(job_id, name, spec))
        fixed = job.get("fixed_inputs", {})
        if not isinstance(fixed, dict):
            errors.append(f"jobs.{job_id}.fixed_inputs must be an object")
            fixed = {}
        for name, value in fixed.items():
            if not INPUT_KEY_RE.match(str(name)) or not isinstance(value, str) or not INPUT_VALUE_RE.match(value):
                errors.append(f"jobs.{job_id}.fixed_inputs.{name} is invalid")
            if name in inputs:
                errors.append(f"jobs.{job_id}: {name} cannot be both an input and a fixed input")

        if workflows_dir is None or not workflow:
            continue
        path = workflows_dir / workflow
        if not path.is_file():
            errors.append(f"jobs.{job_id}: workflow {workflow} does not exist")
            continue
        try:
            doc = _load_yaml(path)
        except ImportError:
            errors.append(YAML_REQUIRED)
            return errors
        except Exception as exc:  # noqa: BLE001 - report any parse failure
            errors.append(f"jobs.{job_id}: cannot parse {workflow}: {exc.__class__.__name__}")
            continue
        text = path.read_text(encoding="utf-8")
        on = _workflow_on(doc) or {}
        dispatch = None
        if isinstance(on, dict):
            dispatch = on.get("workflow_dispatch", "missing")
        elif isinstance(on, list):
            dispatch = {} if "workflow_dispatch" in on else "missing"
        elif on == "workflow_dispatch":
            dispatch = {}
        if triggerable:
            if dispatch == "missing":
                errors.append(f"jobs.{job_id}: {workflow} has no workflow_dispatch trigger")
            else:
                declared = ((dispatch or {}).get("inputs") or {}) if isinstance(dispatch, dict) else {}
                for name in list(inputs) + list(fixed):
                    if name not in declared:
                        errors.append(f"jobs.{job_id}: {workflow} does not declare input {name}")
                for name, spec in inputs.items():
                    wf_spec = declared.get(name) or {}
                    if spec.get("type") == "choice" and wf_spec.get("type") == "choice":
                        extra = set(spec.get("options", [])) - set(map(str, wf_spec.get("options", [])))
                        if extra:
                            errors.append(f"jobs.{job_id}.inputs.{name}: options not in workflow: {sorted(extra)}")
            if tier == "writes_code" and PUSH_TO_MAIN_RE.search(text):
                errors.append(f"jobs.{job_id}: writes_code jobs must be PR-only but {workflow} pushes to main")
        if tier == "read_only":
            perms = [doc.get("permissions")]
            perms += [j.get("permissions", doc.get("permissions")) for j in (doc.get("jobs") or {}).values() if isinstance(j, dict)]
            if any(_permission_writes(p) for p in perms):
                errors.append(f"jobs.{job_id}: tier read_only but {workflow} token can write")
    return errors


# --------------------------------------------------------------------------- parsing


@dataclass
class Command:
    verb: str
    job_id: str | None = None
    inputs: dict[str, str] = field(default_factory=dict)
    target: str | None = None


def _parse_pair(token: str, inputs: dict[str, str]) -> None:
    if token.count("=") != 1:
        raise CommandError("inputs must be written as key=value")
    key, value = token.split("=", 1)
    if not INPUT_KEY_RE.match(key):
        raise CommandError("input names must be lowercase letters, digits, or underscores")
    if not INPUT_VALUE_RE.match(value):
        raise CommandError("input values may only use letters, digits, dot, dash, or underscore")
    if key in inputs:
        raise CommandError("each input may only be given once")
    if len(inputs) >= MAX_INPUTS:
        raise CommandError(f"at most {MAX_INPUTS} inputs are allowed")
    inputs[key] = value


def parse_command_line(line: str) -> Command:
    """Parse one `/buddy ...` line. Raises CommandError on anything unexpected."""
    if not isinstance(line, str):
        raise CommandError("missing command")
    line = line.strip()
    if len(line) > COMMAND_LINE_MAX:
        raise CommandError("command is too long")
    if any(not (32 <= ord(ch) < 127) for ch in line):
        raise CommandError("command must be plain printable ASCII on one line")
    tokens = [t for t in line.split(" ") if t]
    if not tokens or tokens[0] != "/buddy":
        raise CommandError("commands start with /buddy")
    if len(tokens) == 1:
        return Command("help")
    verb = tokens[1]
    if verb not in VERBS:
        raise CommandError("unknown verb; use /buddy run, /buddy status, /buddy list, /buddy customize, or /buddy help")
    rest = tokens[2:]
    if verb == "customize":
        if len(rest) != 1 or not CUSTOMIZE_TARGET_RE.match(rest[0]) or ".." in rest[0]:
            raise CommandError("/buddy customize needs one target: <bot-id>, division:<Name>, or file:<path>")
        return Command("customize", target=rest[0])
    if verb in ("list", "help"):
        if rest:
            raise CommandError(f"/buddy {verb} takes no arguments")
        return Command(verb)
    if verb == "status":
        if len(rest) > 1:
            raise CommandError("/buddy status takes at most one job id")
        if rest and not JOB_ID_RE.match(rest[0]):
            raise CommandError("job ids are lowercase letters, digits, and underscores")
        return Command("status", rest[0] if rest else None)
    if not rest:
        raise CommandError("/buddy run needs a job id")
    job_id = rest[0]
    if not JOB_ID_RE.match(job_id):
        raise CommandError("job ids are lowercase letters, digits, and underscores")
    inputs: dict[str, str] = {}
    for token in rest[1:]:
        _parse_pair(token, inputs)
    return Command("run", job_id, inputs)


def parse_inputs_block(body: str | None, inputs: dict[str, str]) -> dict[str, str]:
    """Merge `key=value` lines from a ```buddy-inputs fenced block into inputs."""
    if not body:
        return inputs
    blocks = INPUTS_FENCE_RE.findall(body.replace("\r\n", "\n"))
    if len(blocks) > 1:
        raise CommandError("use at most one buddy-inputs block")
    for raw in blocks[0].split("\n") if blocks else []:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if any(not (32 <= ord(ch) < 127) for ch in line) or " " in line:
            raise CommandError("each buddy-inputs line must be a single key=value")
        _parse_pair(line, inputs)
    return inputs


def check_customize_body(text: str | None) -> None:
    """Structural check only; field-level validation runs in the apply workflow (allowlists)."""
    text = (text or "").replace("\r\n", "\n")
    if len(text) > CUSTOMIZE_BODY_MAX:
        raise CommandError(f"customize patches are limited to {CUSTOMIZE_BODY_MAX} characters")
    blocks = YAML_FENCE_RE.findall(text)
    if len(blocks) != 1:
        raise CommandError("/buddy customize needs exactly one ```yaml fenced patch")
    if not blocks[0].strip():
        raise CommandError("the yaml patch is empty")
    if any(ord(ch) < 32 and ch not in "\n\t" for ch in blocks[0]):
        raise CommandError("the yaml patch contains control characters")


def command_from_event(event: dict[str, str]) -> Command:
    """Build a Command from router env (issue title/body or comment body)."""
    if event.get("event_name") == "issue_comment":
        body = (event.get("comment_body") or "").replace("\r\n", "\n")
        first, _, remainder = body.lstrip("\n").partition("\n")
        cmd = parse_command_line(first)
        if cmd.verb == "run":
            parse_inputs_block(remainder, cmd.inputs)
        if cmd.verb == "customize":
            check_customize_body(remainder)
        return cmd
    if event.get("event_name") == "issues":
        cmd = parse_command_line(event.get("issue_title") or "")
        if cmd.verb == "run":
            parse_inputs_block(event.get("issue_body"), cmd.inputs)
        if cmd.verb == "customize":
            check_customize_body(event.get("issue_body"))
        return cmd
    raise CommandError("unsupported event")


# --------------------------------------------------------------------------- validation + auth


def validate_run(registry: dict[str, Any], cmd: Command) -> tuple[dict[str, Any], dict[str, str]]:
    """Return (job, final_inputs) or raise CommandError."""
    job = jobs_by_id(registry).get(cmd.job_id or "")
    if job is None:
        raise CommandError("unknown job id; use /buddy list")
    tier = job.get("risk_tier")
    tier_cfg = (registry.get("risk_tiers") or {}).get(tier) or {}
    if tier == "money" or tier_cfg.get("dispatchable") is not True:
        raise CommandError(f"{job['id']} is {tier} tier, which is never dispatchable from the router")
    if job.get("destructive"):
        raise CommandError(f"{job['id']} is destructive and is never dispatchable from the router")
    if job.get("triggerable") is not True:
        raise CommandError(f"{job['id']} is not triggerable: {job.get('blocked_reason', 'blocked by policy')}")
    specs: dict[str, Any] = job.get("inputs") or {}
    fixed: dict[str, str] = job.get("fixed_inputs") or {}
    final: dict[str, str] = {}
    for key, value in cmd.inputs.items():
        if key in fixed:
            raise CommandError(f"input {key} is fixed by policy and cannot be changed")
        spec = specs.get(key)
        if spec is None:
            raise CommandError(f"input {key} is not allowed for {job['id']}")
        kind = spec.get("type")
        if kind == "choice":
            if value not in spec.get("options", []):
                raise CommandError(f"input {key} must be one of: {', '.join(spec.get('options', []))}")
        elif kind == "boolean":
            value = value.lower()
            if value not in ("true", "false"):
                raise CommandError(f"input {key} must be true or false")
        elif kind == "string":
            if len(value) > int(spec.get("max_length", 0)) or not re.fullmatch(spec.get("pattern", "^$"), value):
                raise CommandError(f"input {key} does not match the allowed pattern")
        else:
            raise CommandError(f"input {key} has no valid spec")
        final[key] = value
    for key, spec in specs.items():
        if key not in final and "default" in spec:
            default = spec["default"]
            final[key] = ("true" if default else "false") if isinstance(default, bool) else str(default)
    final.update(fixed)
    return job, final


@dataclass
class AuthDecision:
    allowed: bool
    reason: str


def authorize(
    registry: dict[str, Any],
    actor: str,
    permission: str | None,
    job: dict[str, Any] | None = None,
    issue_author: str | None = None,
) -> AuthDecision:
    if not actor or not LOGIN_RE.match(actor) or actor.endswith("[bot]"):
        return AuthDecision(False, "actor is not a valid human GitHub login")
    operators = _casefold_set(registry.get("operators"))
    owners = _casefold_set(registry.get("owners"))
    if actor.casefold() not in operators:
        return AuthDecision(False, "actor is not a Buddy operator (config/buddy/control-plane.json operators)")
    if permission is None:
        return AuthDecision(False, "could not verify repository permission")
    if permission not in WRITE_PERMISSIONS:
        return AuthDecision(False, "actor does not have write permission on this repository")
    if issue_author is not None and issue_author.casefold() not in operators:
        return AuthDecision(False, "issue author is not a Buddy operator")
    if job is not None and job.get("requires_owner_approval") and actor.casefold() not in owners:
        return AuthDecision(False, f"{job['id']} requires owner approval; only owners can run it")
    return AuthDecision(True, "authorized")


# --------------------------------------------------------------------------- GitHub API


class GitHubAPI:
    """Tiny REST client (urllib). The token is only ever sent to api.github.com."""

    def __init__(
        self,
        repo: str,
        token: str | None,
        opener: Callable[..., Any] | None = None,
        runner: Callable[..., Any] | None = None,
        base: str = "https://api.github.com",
    ) -> None:
        if not REPO_RE.match(repo or ""):
            raise ValueError("invalid repository")
        self.repo = repo
        self.token = token or None
        self.base = base
        self.opener = opener or urllib.request.urlopen
        self.runner = runner or subprocess.run

    def request(self, method: str, path: str, body: Any = None, auth: bool = True) -> tuple[int, Any]:
        url = f"{self.base}/{path.lstrip('/')}"
        data = json.dumps(body).encode() if body is not None else None
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "buddy-control-plane"}
        if data is not None:
            headers["Content-Type"] = "application/json"
        if auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        try:
            with self.opener(req, timeout=20) as resp:
                raw = resp.read()
                return getattr(resp, "status", 200), (json.loads(raw) if raw else None)
        except urllib.error.HTTPError as exc:
            return exc.code, None

    def get(self, path: str) -> tuple[int, Any]:
        status, data = self.request("GET", path)
        if status in (401, 403) and self.token:
            # Public repo: retry anonymously when the job token lacks a scope.
            status, data = self.request("GET", path, auth=False)
        return status, data

    def permission(self, login: str) -> str | None:
        if not LOGIN_RE.match(login or ""):
            return None
        status, data = self.request("GET", f"repos/{self.repo}/collaborators/{login}/permission")
        if status == 404:
            return "none"
        if status != 200 or not isinstance(data, dict):
            return None
        role = str(data.get("role_name") or "").lower()
        perm = str(data.get("permission") or "").lower()
        if role in WRITE_PERMISSIONS:
            return role
        return perm or None

    def issue_comments(self, number: int) -> list[dict[str, Any]]:
        status, data = self.request("GET", f"repos/{self.repo}/issues/{int(number)}/comments?per_page=100")
        if status != 200 or not isinstance(data, list):
            raise RuntimeError(f"could not list issue comments (HTTP {status})")
        return data

    def post_comment(self, number: int, body: str) -> None:
        status, _ = self.request("POST", f"repos/{self.repo}/issues/{int(number)}/comments", {"body": body})
        if status not in (200, 201):
            raise RuntimeError(f"could not post issue comment (HTTP {status})")

    def latest_run(self, workflow: str, branch: str) -> tuple[int, dict[str, Any] | None]:
        if not WORKFLOW_FILE_RE.match(workflow) or not REF_RE.match(branch):
            return 400, None
        query = urllib.parse.urlencode({"per_page": 1, "branch": branch, "exclude_pull_requests": "true"})
        status, data = self.get(f"repos/{self.repo}/actions/workflows/{workflow}/runs?{query}")
        if status != 200 or not isinstance(data, dict):
            return status, None
        runs = data.get("workflow_runs") or []
        return status, (runs[0] if runs else None)

    def find_dispatched_run(self, workflow: str, since: float, attempts: int = 6, delay: float = 5.0) -> str | None:
        query = urllib.parse.urlencode({"per_page": 10, "event": "workflow_dispatch"})
        for attempt in range(attempts):
            status, data = self.get(f"repos/{self.repo}/actions/workflows/{workflow}/runs?{query}")
            if status == 200 and isinstance(data, dict):
                for run in data.get("workflow_runs") or []:
                    created = _parse_time(run.get("created_at"))
                    url = str(run.get("html_url") or "")
                    if created and created >= since - 5 and RUN_URL_RE.fullmatch(url):
                        return url
            if attempt + 1 < attempts:
                time.sleep(delay)
        return None

    def dispatch(self, workflow: str, ref: str, inputs: dict[str, str]) -> str:
        """Run `gh workflow run` with an argument list (never a shell). Returns stdout."""
        if not WORKFLOW_FILE_RE.match(workflow) or not REF_RE.match(ref):
            raise RuntimeError("refusing to dispatch: invalid workflow or ref")
        args = ["gh", "workflow", "run", workflow, "--repo", self.repo, "--ref", ref]
        for key, value in inputs.items():
            if not INPUT_KEY_RE.match(key) or not INPUT_VALUE_RE.match(value):
                raise RuntimeError("refusing to dispatch: invalid input")
            args += ["-f", f"{key}={value}"]
        env = {k: v for k, v in os.environ.items() if k in ("PATH", "HOME", "GH_TOKEN", "GITHUB_TOKEN", "GH_HOST")}
        proc = self.runner(args, capture_output=True, text=True, timeout=60, env=env, check=False)
        if proc.returncode != 0:
            raise RuntimeError(f"gh workflow run failed (exit {proc.returncode})")
        return proc.stdout or ""


def _parse_time(value: Any) -> float | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


# --------------------------------------------------------------------------- router


def event_from_env(env: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ if env is None else env)
    return {
        "event_name": env.get("BUDDY_EVENT_NAME", ""),
        "action": env.get("BUDDY_EVENT_ACTION", ""),
        "actor": env.get("BUDDY_ACTOR", ""),
        "issue_number": env.get("BUDDY_ISSUE_NUMBER", ""),
        "issue_author": env.get("BUDDY_ISSUE_AUTHOR", ""),
        "issue_title": env.get("BUDDY_ISSUE_TITLE", ""),
        "issue_body": env.get("BUDDY_ISSUE_BODY", ""),
        "comment_body": env.get("BUDDY_COMMENT_BODY", ""),
        "comment_id": env.get("BUDDY_COMMENT_ID", ""),
        "label_name": env.get("BUDDY_LABEL_NAME", ""),
        "router_run_url": env.get("BUDDY_ROUTER_RUN_URL", ""),
    }


def _actions_url(repo: str, workflow: str) -> str:
    return f"https://github.com/{repo}/actions/workflows/{workflow}"


def _reply(lines: list[str], issue_event: bool, router_run_url: str = "") -> str:
    footer = []
    if RUN_URL_RE.fullmatch(router_run_url or ""):
        footer.append(f"Router run: {router_run_url}")
    footer.append("Docs: docs/BUDDY_CONTROL_PLANE.md")
    marker = ISSUE_MARKER if issue_event else MARKER
    return "\n".join([marker, *lines, "", "<sub>" + " · ".join(footer) + "</sub>"])


def _job_table(registry: dict[str, Any]) -> list[str]:
    rows = ["| job | tier | owner approval | triggerable |", "|---|---|---|---|"]
    for job in registry.get("jobs", []):
        rows.append(
            f"| `{job['id']}` | {job['risk_tier']} | {'yes' if job.get('requires_owner_approval') else 'no'} | "
            f"{'yes' if job.get('triggerable') and job['risk_tier'] != 'money' and not job.get('destructive') else 'no'} |"
        )
    return rows


def route(event: dict[str, str], registry: dict[str, Any], api: GitHubAPI) -> tuple[int, str | None]:
    """Handle one event. Returns (exit_code, posted_comment_or_None)."""
    issue_event = event.get("event_name") == "issues"
    try:
        number = int(event.get("issue_number") or "")
    except ValueError:
        return 1, None
    if event.get("event_name") not in ("issues", "issue_comment"):
        return 0, None
    if issue_event:
        label = registry.get("command_label")
        title = (event.get("issue_title") or "").strip()
        if event.get("action") == "labeled" and event.get("label_name") != label:
            return 0, None
        if not title.startswith("/buddy"):
            body = _reply(["**Buddy command rejected:** the issue title must be the command, e.g. `/buddy run system_watch`."], True, event.get("router_run_url", ""))
            if any(ISSUE_MARKER in str(c.get("body", "")) for c in api.issue_comments(number)):
                return 0, None
            api.post_comment(number, body)
            return 0, body
        # opened + labeled can both fire for one new issue: handle it once.
        if any(ISSUE_MARKER in str(c.get("body", "")) for c in api.issue_comments(number)):
            return 0, None

    def reject(reason: str) -> tuple[int, str]:
        body = _reply([f"**Buddy command rejected:** {reason}."], issue_event, event.get("router_run_url", ""))
        api.post_comment(number, body)
        return 0, body

    errors = check_registry(registry, workflows_dir=None)
    if errors:
        return reject("the control-plane registry failed validation, so nothing was dispatched (fail closed)")

    try:
        cmd = command_from_event(event)
    except CommandError as exc:
        return reject(str(exc))

    job = None
    if cmd.verb == "run":
        job = jobs_by_id(registry).get(cmd.job_id or "")
    if cmd.verb == "customize":
        job = jobs_by_id(registry).get(CUSTOMIZE_JOB_ID)
        if job is None:
            return reject("customization is not enabled (no buddy_customize_apply job in the registry)")
    actor = event.get("actor") or ""
    permission = api.permission(actor) if LOGIN_RE.match(actor) else None
    decision = authorize(registry, actor, permission, job, event.get("issue_author") if issue_event else None)
    if not decision.allowed:
        return reject(decision.reason)

    repo = registry["repository"]
    ref = registry["default_ref"]
    if cmd.verb == "help":
        lines = [
            "**Buddy commands**",
            "- `/buddy list` - registered jobs",
            "- `/buddy status [job_id]` - last run on " + ref,
            "- `/buddy run <job_id> [key=value ...]` - dispatch a registered job",
            "- `/buddy customize <bot-id|division:Name|file:path>` + one ```yaml patch - validated against the editable-field allowlist, applied on a branch, opened as a PR",
            "",
            "Inputs can also go in a fenced block tagged `buddy-inputs`, one `key=value` per line.",
        ]
        body = _reply(lines, issue_event, event.get("router_run_url", ""))
        api.post_comment(number, body)
        return 0, body
    if cmd.verb == "list":
        body = _reply(["**Registered Buddy jobs**", "", *_job_table(registry)], issue_event, event.get("router_run_url", ""))
        api.post_comment(number, body)
        return 0, body
    if cmd.verb == "status":
        targets = [jobs_by_id(registry)[cmd.job_id]] if cmd.job_id in jobs_by_id(registry) else None
        if cmd.job_id and targets is None:
            return reject("unknown job id; use /buddy list")
        snapshot = build_status(registry, api, only=targets)
        rows = ["| job | state | last run |", "|---|---|---|"]
        for job_id, item in snapshot["jobs"].items():
            rows.append(f"| `{job_id}` | {item['state']} | {item.get('run_url') or '-'} |")
        body = _reply([f"**Buddy status** (`{ref}`, {snapshot['generated_at']})", "", *rows], issue_event, event.get("router_run_url", ""))
        api.post_comment(number, body)
        return 0, body

    if cmd.verb == "customize":
        tier_cfg = (registry.get("risk_tiers") or {}).get(job.get("risk_tier")) or {}
        if job.get("risk_tier") == "money" or tier_cfg.get("dispatchable") is not True or job.get("destructive"):
            return reject("the customize job is not dispatchable under the registry policy")
        comment_id = event.get("comment_id") or "0"
        if issue_event or not re.fullmatch(r"[0-9]{1,15}", comment_id):
            comment_id = "0"
        final_inputs = {"issue": str(number), "comment": comment_id}
    else:
        try:
            job, final_inputs = validate_run(registry, cmd)
        except CommandError as exc:
            return reject(str(exc))

    started = time.time()
    try:
        out = api.dispatch(job["workflow"], ref, final_inputs)
    except Exception as exc:  # noqa: BLE001
        body = _reply([f"**Buddy dispatch failed** for `{job['id']}`: {exc}. Nothing else was attempted."], issue_event, event.get("router_run_url", ""))
        api.post_comment(number, body)
        return 1, body
    match = RUN_URL_RE.search(out)
    run_url = match.group(0) if match else api.find_dispatched_run(job["workflow"], started)
    shown_inputs = ", ".join(f"`{k}={v}`" for k, v in final_inputs.items()) or "none"
    lines = [
        f"**Buddy dispatched `{job['id']}`** ({job['risk_tier']}) on `{ref}`." + (
            f" Customization of `{cmd.target}`: the apply job validates the patch and opens a PR; nothing is merged automatically."
            if cmd.verb == "customize" else ""),
        f"- Workflow: `{job['workflow']}`",
        f"- Inputs: {shown_inputs}",
        f"- Run: {run_url}" if run_url else f"- Run: not found yet; see {_actions_url(repo, job['workflow'])}",
    ]
    body = _reply(lines, issue_event, event.get("router_run_url", ""))
    api.post_comment(number, body)
    return 0, body


# --------------------------------------------------------------------------- status snapshot


def _state(run: dict[str, Any] | None) -> str:
    if run is None:
        return "never_run"
    if run.get("status") != "completed":
        return str(run.get("status") or "unknown")
    return str(run.get("conclusion") or "unknown")


def build_status(
    registry: dict[str, Any],
    api: GitHubAPI | None,
    only: list[dict[str, Any]] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    branch = registry.get("default_ref", "main")
    cache: dict[str, tuple[int, dict[str, Any] | None]] = {}
    jobs: dict[str, Any] = {}
    errors: list[str] = []
    for job in only or registry.get("jobs", []):
        workflow = job["workflow"]
        item: dict[str, Any] = {"workflow": workflow, "workflow_url": _actions_url(registry["repository"], workflow)}
        if api is None:
            item["state"] = "unavailable"
        else:
            if workflow not in cache:
                try:
                    cache[workflow] = api.latest_run(workflow, branch)
                except Exception as exc:  # noqa: BLE001
                    cache[workflow] = (0, None)
                    errors.append(f"{workflow}: {exc.__class__.__name__}")
            status, run = cache[workflow]
            if status == 404:
                item["state"] = "workflow_missing"
            elif status != 200:
                item["state"] = "unavailable"
                if f"{workflow}: HTTP {status}" not in errors:
                    errors.append(f"{workflow}: HTTP {status}")
            else:
                item["state"] = _state(run)
                if run:
                    url = str(run.get("html_url") or "")
                    item.update(
                        {
                            "run_url": url if RUN_URL_RE.fullmatch(url) else None,
                            "run_number": run.get("run_number") if isinstance(run.get("run_number"), int) else None,
                            "event": str(run.get("event") or "")[:40],
                            "updated_at": str(run.get("updated_at") or "")[:40],
                        }
                    )
        jobs[job["id"]] = item
    states = [j["state"] for j in jobs.values()]
    return {
        "schema": STATUS_SCHEMA,
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repository": registry["repository"],
        "branch": branch,
        "source": "github-actions-api" if api is not None and "unavailable" not in states else ("partial" if api else "unavailable"),
        "jobs": jobs,
        "errors": errors[:20],
    }


def public_registry_text(registry: dict[str, Any]) -> str:
    return json.dumps(registry, indent=2, ensure_ascii=False) + "\n"


# --------------------------------------------------------------------------- CLI


def _api_from_env(registry: dict[str, Any]) -> GitHubAPI:
    repo = os.environ.get("GITHUB_REPOSITORY") or registry["repository"]
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    return GitHubAPI(repo, token)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--registry", type=Path, default=REGISTRY_PATH)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_check = sub.add_parser("check")
    p_check.add_argument("--no-workflows", action="store_true", help="skip the workflow-file cross-check")
    sub.add_parser("list")
    sub.add_parser("route")
    p_status = sub.add_parser("status")
    p_status.add_argument("--out", type=Path, default=PUBLIC_STATUS_PATH)
    p_status.add_argument("--offline", action="store_true", help="write an 'unavailable' snapshot without calling the API")
    p_pub = sub.add_parser("publish-registry")
    p_pub.add_argument("--out", type=Path, default=PUBLIC_REGISTRY_PATH)
    p_pub.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    curated = load_registry(args.registry)
    generated_path = GENERATED_PATH if args.registry == REGISTRY_PATH else None
    if args.cmd == "check":
        errors = check_registry(curated, None if args.no_workflows else WORKFLOWS_DIR)
        merged, skipped = load_merged(args.registry, generated_path, None if args.no_workflows else WORKFLOWS_DIR)
        for err in errors:
            print(f"ERROR {err}")
        for note in skipped:
            print(f"SKIP generated job {note}")
        if not errors:
            print(f"OK {len(curated['jobs'])} curated jobs, {len(merged['jobs']) - len(curated['jobs'])} generated jobs merged")
        return 1 if errors else 0
    registry, _skipped = load_merged(args.registry, generated_path, None)
    if args.cmd == "list":
        print("\n".join(_job_table(registry)))
        return 0
    if args.cmd == "route":
        if os.environ.get("GITHUB_REPOSITORY") and os.environ["GITHUB_REPOSITORY"] != registry["repository"]:
            print("::error::registry repository does not match GITHUB_REPOSITORY; refusing to route")
            return 1
        code, body = route(event_from_env(), registry, _api_from_env(registry))
        summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary and body:
            with open(summary, "a", encoding="utf-8") as fh:
                fh.write(body.replace(MARKER, "").replace(ISSUE_MARKER, "") + "\n")
        return code
    if args.cmd == "status":
        if check_registry(registry, workflows_dir=None):
            print("::error::registry invalid; not writing status")
            return 1
        snapshot = build_status(registry, None if args.offline else _api_from_env(registry))
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {args.out} source={snapshot['source']} jobs={len(snapshot['jobs'])} errors={len(snapshot['errors'])}")
        return 0
    if args.cmd == "publish-registry":
        # Curated jobs only: generated jobs are published by tools/build_actions_prospectus.py
        # (website/data/run-prospectus.json) and rendered on buddy-control.html from there.
        text = public_registry_text(curated)
        if args.check:
            current = args.out.read_text(encoding="utf-8") if args.out.exists() else ""
            if current != text:
                print(f"{args.out} is stale; run python3 tools/buddy_control_plane.py publish-registry")
                return 1
            print("public registry up to date")
            return 0
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
