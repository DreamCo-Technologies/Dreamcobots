from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Dict, List


@dataclass
class VersionedAPI:
    version: str
    schema_hash: str
    breaking_changes: List[str]
    migration_guide: List[str]


class VersioningManager:
    def detect_breaking_changes(self, old_schema: Dict[str, str], new_schema: Dict[str, str]) -> List[str]:
        changes = []
        for field, old_type in old_schema.items():
            if field not in new_schema:
                changes.append(f'Removed field: {field}')
            elif new_schema[field] != old_type:
                changes.append(f'Type changed for {field}: {old_type} -> {new_schema[field]}')
        return changes

    def version_api(self, version: str, old_schema: Dict[str, str], new_schema: Dict[str, str]) -> VersionedAPI:
        breaking = self.detect_breaking_changes(old_schema, new_schema)
        schema_hash = hashlib.sha256(json.dumps(new_schema, sort_keys=True).encode('utf-8')).hexdigest()
        migration = self.generate_migration_scripts(old_schema, new_schema)
        return VersionedAPI(version, schema_hash, breaking, migration)

    def generate_migration_scripts(self, old_schema: Dict[str, str], new_schema: Dict[str, str]) -> List[str]:
        scripts = []
        for field, field_type in new_schema.items():
            if field not in old_schema:
                scripts.append(f'client.setdefault("{field}", None)  # add {field_type}')
        for field in old_schema:
            if field not in new_schema:
                scripts.append(f'client.pop("{field}", None)')
        return scripts

def _generate_changelog(self, old_schema: Dict[str, str], new_schema: Dict[str, str]) -> List[str]:
    notes = []
    notes.extend(self.detect_breaking_changes(old_schema, new_schema))
    for field in new_schema:
        if field not in old_schema:
            notes.append(f'Added field: {field}')
    return notes or ['No schema changes detected']


def _migration_preview(self, versioned: VersionedAPI) -> str:
    return '
'.join(versioned.migration_guide)


VersioningManager.generate_changelog = _generate_changelog
VersioningManager.migration_preview = _migration_preview

def _version_summary(self, versioned: VersionedAPI) -> dict:
    return {'version': versioned.version, 'breaking_change_count': len(versioned.breaking_changes)}


VersioningManager.version_summary = _version_summary
