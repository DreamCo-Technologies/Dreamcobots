"""Safely inspect local repository trees before any code is executed."""

from __future__ import annotations

import hashlib
import json
import os
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


class OpenSourceError(ValueError):
    """Raised when a repository or upgrade violates lab limits."""


PERMISSIVE_LICENSES = {"MIT", "APACHE-2.0", "BSD-2-CLAUSE", "BSD-3-CLAUSE", "ISC", "0BSD"}
REVIEW_LICENSES = {"MPL-2.0", "LGPL-2.1", "LGPL-3.0", "GPL-2.0", "GPL-3.0", "AGPL-3.0"}
EXTENSION_LANGUAGE = {
    ".py": "Python",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".rs": "Rust",
    ".go": "Go",
    ".java": "Java",
    ".kt": "Kotlin",
    ".swift": "Swift",
    ".cpp": "C++",
    ".c": "C",
    ".cs": "C#",
    ".html": "HTML",
    ".css": "CSS",
}
SKIP_DIRS = {".git", "node_modules", "dist", "build", ".venv", "venv", "__pycache__"}
SECRET_FILENAMES = {".env", "id_rsa", "id_ed25519", "credentials.json", "service-account.json"}
CUSTOMIZATION_AREAS = {
    "audience", "workflow", "interface", "accessibility", "privacy", "security",
    "integrations", "performance", "cost", "original_features",
}
TEXT_EXTENSIONS = set(EXTENSION_LANGUAGE) | {".md", ".mdx", ".json", ".yaml", ".yml", ".toml"}


@dataclass(frozen=True)
class UpgradeRequest:
    owner_user_id: str
    buddy_instance_id: str
    capability: str
    repository_path: str
    license_id: str
    allow_sandbox_execution: bool = False
    source_revision: str = ""
    allow_network_during_build: bool = False
    trust_remote_code: bool = False
    timeout_seconds: int = 900
    memory_mb: int = 4096


class BuddyOpenSourceLab:
    """Create repository evidence and a sandboxed upgrade plan."""

    def investigation_plan(
        self,
        target_kind: str,
        target_reference: str,
        *,
        owner_authorized: bool,
        written_scope: str,
        customizations: list[str],
        differentiator: str,
        revision: str = "",
        execution_requested: bool = False,
        allow_network: bool = False,
        max_cost_usd: float = 0,
    ) -> dict[str, Any]:
        """Prepare a bounded, modality-specific plan; never connects or executes a target."""
        profiles_path = Path(__file__).resolve().parents[2] / "config" / "dreamco-investigation-profiles.json"
        profiles = json.loads(profiles_path.read_text(encoding="utf-8"))["profiles"]
        if target_kind not in profiles:
            raise OpenSourceError("Choose a supported investigation profile.")
        if not owner_authorized:
            raise OpenSourceError("Owner authorization is required for this target.")
        if len(" ".join(written_scope.split())) < 20:
            raise OpenSourceError("Write a specific scope of at least 20 characters.")
        reference = target_reference.strip()
        if not reference or len(reference) > 2_048 or any(ord(char) < 32 for char in reference):
            raise OpenSourceError("Provide a valid local reference or public target URL.")
        parsed = urlsplit(reference)
        local_windows_path = bool(re.match(r"^[A-Za-z]:[\\/]", reference))
        if parsed.scheme and not local_windows_path and (parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password):
            raise OpenSourceError("Remote targets must use credential-free HTTPS URLs.")
        if target_kind in {"code_repository", "open_weights_model"}:
            pinned_revision = revision.strip()
            if len(pinned_revision) < 7 or pinned_revision.lower() in {"main", "master", "latest", "head", "stable", "dev", "develop"}:
                raise OpenSourceError("Pin repositories and model weights to an immutable revision or content hash.")
        if len(set(customizations)) < 2 or any(value not in CUSTOMIZATION_AREAS for value in customizations):
            raise OpenSourceError("Choose at least two supported DreamCo customization areas.")
        original = " ".join(differentiator.split())
        if len(original) < 30:
            raise OpenSourceError("Describe an original differentiator in at least 30 characters.")
        if not isinstance(max_cost_usd, (int, float)) or max_cost_usd < 0 or max_cost_usd > 10_000:
            raise OpenSourceError("Set a budget between zero and 10,000 USD.")
        profile = profiles[target_kind]
        return {
            "schema": "dreamco.authorized_investigation_plan.v1",
            "system": "DreamCo Code Workbench",
            "target": {"kind": target_kind, "label": profile["label"], "reference": reference, "revision": revision or None},
            "authorization": {"owner_confirmed": True, "written_scope": " ".join(written_scope.split())},
            "evidence_to_collect": profile["evidence"],
            "test_plan": profile["tests"],
            "execution_controls": {
                "execution_requested": execution_requested,
                "execution_started": False,
                "adapter_required": True,
                "network_default": "off" if not allow_network else "explicitly_requested_adapter_gate_required",
                "maximum_cost_usd": float(max_cost_usd),
                "profile_controls": profile["execution"],
                "host_secrets_available": False,
                "production_write_access": False,
            },
            "customization": {"areas": list(dict.fromkeys(customizations)), "original_differentiator": original},
            "universal_gates": ["maintain an evidence and uncertainty log", "use fixtures and test accounts", "review privacy, license, accessibility, and security", "owner reviews results before release"],
            "prohibited": ["access-control bypass", "DRM or anti-cheat circumvention", "credential or secret extraction", "production-destructive tests", "copying protected source or media"],
            "truth_boundary": "This is a plan, not a connection or test result. A configured isolated adapter must execute the plan and record evidence.",
        }

    def inspect(self, root: Path, *, max_files: int = 20_000, max_bytes: int = 250_000_000) -> dict[str, Any]:
        root = root.expanduser().resolve()
        if not root.is_dir():
            raise OpenSourceError("Repository path must be a readable local directory.")
        files = 0
        total_bytes = 0
        languages: Counter[str] = Counter()
        secret_risks: list[str] = []
        manifests: list[str] = []
        license_files: list[str] = []
        fingerprint = hashlib.sha256()

        for directory, dirnames, filenames in os.walk(root, followlinks=False):
            dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
            for filename in filenames:
                path = Path(directory) / filename
                if path.is_symlink() or not path.is_file():
                    continue
                relative = path.relative_to(root).as_posix()
                size = path.stat().st_size
                files += 1
                total_bytes += size
                if files > max_files or total_bytes > max_bytes:
                    raise OpenSourceError("Repository exceeds the configured inspection limit.")
                fingerprint.update(f"{relative}:{size}\n".encode("utf-8"))
                language = EXTENSION_LANGUAGE.get(path.suffix.lower())
                if language:
                    languages[language] += 1
                if filename.lower() in SECRET_FILENAMES or path.suffix.lower() in {".pem", ".key", ".p12"}:
                    secret_risks.append(relative)
                if filename in {"package.json", "pyproject.toml", "requirements.txt", "Cargo.toml", "go.mod", "pom.xml"}:
                    manifests.append(relative)
                if filename.lower().startswith(("license", "copying")):
                    license_files.append(relative)

        return {
            "schema": "dreamco.open_source_repository_inspection.v1",
            "repository_id": f"repo-{fingerprint.hexdigest()[:20]}",
            "root_name": root.name,
            "files": files,
            "bytes": total_bytes,
            "languages": dict(languages.most_common()),
            "manifests": sorted(manifests),
            "license_files": sorted(license_files),
            "potential_secret_files": sorted(secret_risks),
            "source_executed": False,
            "network_used": False,
        }

    def analyze_clean_room(
        self,
        root: Path,
        *,
        owner_authorized: bool,
        customizations: list[str],
        differentiator: str,
        max_source_files: int = 2_000,
        max_file_bytes: int = 1_000_000,
    ) -> dict[str, Any]:
        """Produce static evidence and an original implementation brief, without executing code."""
        if not owner_authorized:
            raise OpenSourceError("Owner authorization is required before source analysis.")
        chosen = list(dict.fromkeys(value.strip().lower() for value in customizations if value.strip()))
        if len(chosen) < 2 or any(value not in CUSTOMIZATION_AREAS for value in chosen):
            raise OpenSourceError("Choose at least two supported DreamCo customization areas.")
        original = " ".join(differentiator.split())
        if len(original) < 30:
            raise OpenSourceError("Describe an original differentiator in at least 30 characters.")

        inspection = self.inspect(root)
        if inspection["potential_secret_files"]:
            raise OpenSourceError("Remove potential secret files before clean-room analysis.")
        resolved_root = Path(root).expanduser().resolve()
        evidence: dict[str, list[dict[str, Any]]] = {
            "entry_points": [], "routes_and_apis": [], "tests": [], "documentation": [],
        }
        source_count = 0
        for directory, dirnames, filenames in os.walk(resolved_root, followlinks=False):
            dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
            for filename in filenames:
                path = Path(directory) / filename
                if path.is_symlink() or not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
                    continue
                if path.stat().st_size > max_file_bytes:
                    continue
                source_count += 1
                if source_count > max_source_files:
                    raise OpenSourceError("Repository exceeds the clean-room source-file limit.")
                relative = path.relative_to(resolved_root).as_posix()
                try:
                    lines = path.read_text(encoding="utf-8").splitlines()
                except (UnicodeError, OSError):
                    continue
                if len(evidence["entry_points"]) < 100 and (
                    filename.lower() in {"main.py", "app.py", "server.py", "index.ts", "index.js", "main.go"}
                    or relative.lower().startswith(("src/main/", "app/"))
                ):
                    evidence["entry_points"].append({"path": relative, "line": 1})
                if len(evidence["tests"]) < 100 and (
                    "test" in path.parts or filename.lower().startswith(("test_", "spec."))
                ):
                    evidence["tests"].append({"path": relative, "line": 1})
                if len(evidence["documentation"]) < 100 and path.suffix.lower() in {".md", ".mdx"}:
                    evidence["documentation"].append({"path": relative, "line": 1})
                if len(evidence["routes_and_apis"]) < 200:
                    for line_number, line in enumerate(lines, 1):
                        if any(token in line.lower() for token in ("@app.route", "@router.", "app.get(", "app.post(", "router.get(", "router.post(", "routes/", "/api/")):
                            evidence["routes_and_apis"].append({"path": relative, "line": line_number})
                            if len(evidence["routes_and_apis"]) >= 200:
                                break

        return {
            "schema": "dreamco.clean_room_code_analysis.v1",
            "system": "DreamCo Code Workbench",
            "analysis_mode": "static_local_source_review",
            "repository": inspection,
            "evidence": evidence,
            "customization": {"areas": chosen, "original_differentiator": original},
            "implementation_brief": [
                "Write an independent behavior specification from authorized evidence.",
                "Implement DreamCo-owned code around the selected user and product needs.",
                "Create original tests for observed behavior and each selected customization.",
                "Review licenses, security, accessibility, and regression results before release.",
            ],
            "limitations": [
                "Static source review only; runtime and visual behavior are not verified.",
                "Evidence lists file paths and line numbers, never copies source into the report.",
                "Third-party binaries, hosted services, and undocumented behavior need separate authorized evidence.",
            ],
            "source_executed": False,
            "network_used": False,
            "source_code_copied": False,
            "training_started": False,
        }

    def upgrade_plan(self, request: UpgradeRequest, inspection: dict[str, Any]) -> dict[str, Any]:
        license_id = request.license_id.strip().upper()
        if len(request.capability.strip()) < 5:
            raise OpenSourceError("Describe the capability to evaluate.")
        if inspection.get("schema") != "dreamco.open_source_repository_inspection.v1":
            raise OpenSourceError("A valid read-only repository inspection is required.")
        if not inspection.get("license_files"):
            raise OpenSourceError("A repository license must be identified before reuse.")
        if license_id not in PERMISSIVE_LICENSES | REVIEW_LICENSES:
            raise OpenSourceError("The license is unknown or not approved for this evaluation.")
        if inspection.get("potential_secret_files"):
            raise OpenSourceError("Potential secret files must be removed from the sandbox package.")
        if request.trust_remote_code:
            raise OpenSourceError("Remote model or repository code is disabled in Buddy sandboxes.")
        if request.timeout_seconds < 30 or request.timeout_seconds > 7_200:
            raise OpenSourceError("Sandbox timeout must be between 30 and 7,200 seconds.")
        if request.memory_mb < 512 or request.memory_mb > 131_072:
            raise OpenSourceError("Sandbox memory must be between 512 and 131,072 MB.")
        return {
            "schema": "dreamco.buddy_open_source_upgrade.v2",
            "status": "sandbox_plan_ready" if request.allow_sandbox_execution else "execution_permission_required",
            "buddy_instance_id": request.buddy_instance_id,
            "repository_id": inspection["repository_id"],
            "capability": request.capability,
            "license": {
                "spdx": license_id,
                "review": "standard" if license_id in PERMISSIVE_LICENSES else "copyleft_and_distribution_review_required",
                "attribution_required": True,
            },
            "sandbox": {
                "adapter_required": True,
                "live_execution_performed": False,
                "network_default": "one_run_approval_required" if request.allow_network_during_build else "off",
                "source_mount": "read_only",
                "filesystem": "ephemeral_work_directory",
                "run_as": "non_root",
                "host_sockets": "none",
                "secrets": "none",
                "resource_limits": {
                    "timeout_seconds": request.timeout_seconds,
                    "memory_mb": request.memory_mb,
                    "cpu": "capped_by_adapter",
                    "disk": "capped_by_adapter",
                    "processes": "capped_by_adapter",
                },
                "trust_remote_code": False,
                "source_execution_approved": request.allow_sandbox_execution,
                "outputs": "quarantined_until_tests_and_owner_review",
            },
            "stages": [
                "pin and verify the exact source revision",
                "lock dependencies and verify checksums",
                "scan licenses, secrets, unsafe serialization, vulnerabilities, and generated files",
                "generate an SBOM and open-source security scorecard evidence",
                "build in an isolated disposable sandbox",
                "run upstream tests",
                "run Buddy compatibility, mutation, security, and adversarial tests",
                "record failures, resource use, logs, and artifact hashes",
                "show visual or behavioral diff",
                "generate attribution and source-obligation report",
                "owner approves a reversible upgrade checkpoint",
            ],
            "automatic_merge": False,
            "automatic_publish": False,
        }
