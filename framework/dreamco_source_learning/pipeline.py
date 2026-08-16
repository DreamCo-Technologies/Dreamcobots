"""Compliance-first source learning and capability packaging.

This module deliberately does NOT scrape around access controls, copy protected
source text, or claim ownership of third-party material. External sources are
reference inputs. The sellable artifact is DreamCo's original work product:
independent explanations, experiments, tasks, evaluations, and structured
capability notes, with provenance retained for every artifact.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


class LicenseStatus(str, Enum):
    APPROVED = "approved"
    REVIEW = "review_required"
    RESTRICTED = "restricted"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    url: str
    title: str
    accessed_at: str
    license_status: LicenseStatus
    license_name: str | None = None
    terms_checked: bool = False
    notes: str = ""


@dataclass(frozen=True)
class LearningArtifact:
    artifact_id: str
    capability_id: str
    kind: str
    content: str
    source_ids: tuple[str, ...] = ()
    original_author: str = "DreamCo"
    originality_statement: str = (
        "DreamCo-created synthesis/analysis; not a reproduction of source text."
    )


@dataclass
class CapabilityPackage:
    capability_id: str
    name: str
    version: str = "0.1.0"
    description: str = ""
    artifacts: list[LearningArtifact] = field(default_factory=list)
    source_records: list[SourceRecord] = field(default_factory=list)
    evaluation_tasks: list[dict[str, Any]] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)

    def manifest(self) -> dict[str, Any]:
        payload = {
            "schema": "dreamco.capability_package.v1",
            "capability_id": self.capability_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "artifacts": [asdict(a) for a in self.artifacts],
            "source_records": [asdict(s) for s in self.source_records],
            "evaluation_tasks": self.evaluation_tasks,
            "provenance": self.provenance,
        }
        return payload

    def content_hash(self) -> str:
        encoded = json.dumps(self.manifest(), sort_keys=True, default=str).encode()
        return hashlib.sha256(encoded).hexdigest()


class SourceLearningPipeline:
    """Build DreamCo-owned/original capability artifacts from authorized research.

    The pipeline is intentionally conservative: sources marked REVIEW, RESTRICTED,
    or UNKNOWN cannot be packaged for sale. A human/legal review can change a
    source to APPROVED after verifying the applicable license/terms.
    """

    def __init__(self, policy_path: str | Path | None = None) -> None:
        self.policy = self._load_policy(policy_path)

    @staticmethod
    def _load_policy(policy_path: str | Path | None) -> dict[str, Any]:
        if policy_path is None:
            return {"require_authorized_training_data": True}
        return json.loads(Path(policy_path).read_text(encoding="utf-8"))

    def validate_sources(self, sources: Iterable[SourceRecord]) -> list[str]:
        errors: list[str] = []
        for source in sources:
            if source.license_status is not LicenseStatus.APPROVED:
                errors.append(
                    f"{source.source_id}: source is {source.license_status.value}; "
                    "not eligible for commercial packaging"
                )
            if not source.terms_checked:
                errors.append(f"{source.source_id}: source terms/license not checked")
        return errors

    def can_publish(self, package: CapabilityPackage) -> tuple[bool, list[str]]:
        errors = self.validate_sources(package.source_records)
        if not package.artifacts:
            errors.append("package contains no DreamCo-created artifacts")
        if not package.evaluation_tasks:
            errors.append("package contains no independent evaluation tasks")
        if package.provenance.get("rights_reviewed") is not True:
            errors.append("package rights review is not recorded")
        return (not errors, errors)

    def build_manifest(self, package: CapabilityPackage) -> dict[str, Any]:
        allowed, errors = self.can_publish(package)
        manifest = package.manifest()
        manifest["commercial_status"] = "approved" if allowed else "blocked"
        manifest["blocking_reasons"] = errors
        manifest["content_hash"] = package.content_hash()
        return manifest

    def write_manifest(self, package: CapabilityPackage, output: str | Path) -> Path:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.build_manifest(package), indent=2, default=str) + "\n",
            encoding="utf-8",
        )
        return path
