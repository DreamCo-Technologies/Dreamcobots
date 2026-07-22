"""Safely inspect local repository trees before any code is executed."""

from __future__ import annotations

import hashlib
import os
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


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


@dataclass(frozen=True)
class UpgradeRequest:
    owner_user_id: str
    buddy_instance_id: str
    capability: str
    repository_path: str
    license_id: str
    allow_sandbox_execution: bool = False


class BuddyOpenSourceLab:
    """Create repository evidence and a sandboxed upgrade plan."""

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
        return {
            "schema": "dreamco.buddy_open_source_upgrade.v1",
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
                "network_default": "off",
                "filesystem": "temporary_copy",
                "secrets": "none",
                "resource_limits": True,
                "source_execution_approved": request.allow_sandbox_execution,
            },
            "stages": [
                "lock dependencies and verify checksums",
                "scan licenses, secrets, vulnerabilities, and generated files",
                "build in an isolated disposable sandbox",
                "run upstream tests",
                "run Buddy compatibility and adversarial tests",
                "show visual or behavioral diff",
                "generate attribution and source-obligation report",
                "owner approves a reversible upgrade checkpoint",
            ],
            "automatic_merge": False,
        }
