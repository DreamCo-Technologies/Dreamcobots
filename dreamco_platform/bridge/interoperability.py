"""Payload interoperability helpers between systems."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List


@dataclass
class FieldMapping:
    source: str
    target: str
    required: bool = False
    default: Any = None


class InteroperabilityBridge:
    def __init__(self) -> None:
        self._mappings: List[FieldMapping] = []

    def register_mapping(self, source: str, target: str, required: bool = False, default: Any = None) -> FieldMapping:
        mapping = FieldMapping(source=source, target=target, required=required, default=default)
        self._mappings.append(mapping)
        return mapping

    def transform(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for mapping in self._mappings:
            if mapping.source in payload:
                result[mapping.target] = payload[mapping.source]
            elif mapping.required:
                result[mapping.target] = mapping.default
        return result

    def compatibility_report(self, payload: Dict[str, Any]) -> Dict[str, object]:
        missing = [mapping.source for mapping in self._mappings if mapping.required and mapping.source not in payload]
        transformed = self.transform(payload)
        return {
            'missing_required': missing,
            'mapped_fields': sorted(transformed.keys()),
            'compatible': not missing,
        }


def bridge_payload(payload: Dict[str, Any], mappings: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    bridge = InteroperabilityBridge()
    for item in mappings:
        bridge.register_mapping(str(item['source']), str(item['target']), bool(item.get('required', False)), item.get('default'))
    return bridge.transform(payload)
