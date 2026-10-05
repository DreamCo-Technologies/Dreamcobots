#!/usr/bin/env python3
"""Minimal JSON Schema (draft 2020-12 subset) validator for DreamCo data-package schemas.

`jsonschema` is not listed in any requirements*.txt in this repo, so the data-package
gate tools validate with this small, dependency-free subset instead. Supported keywords:
$ref (local "#/$defs/..." only), type, enum, const, required, properties,
additionalProperties, items, minItems, maxItems, uniqueItems, minLength, maxLength,
pattern, minimum, maximum, minProperties, anyOf, oneOf, allOf, format (date-time, date, uri — checked
loosely). Unsupported keywords are ignored, so schemas should stay simple.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_TYPES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}
_FORMATS = {
    "date-time": re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:\d{2})$"),
    "date": re.compile(r"^\d{4}-\d{2}-\d{2}$"),
    "uri": re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:[^\s]+$"),
}


def load_schema(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _resolve(root: dict, ref: str) -> dict:
    if not ref.startswith("#/"):
        raise ValueError(f"only local $ref supported: {ref}")
    node: Any = root
    for part in ref[2:].split("/"):
        node = node[part.replace("~1", "/").replace("~0", "~")]
    return node


def _validate(value: Any, schema: Any, root: dict, path: str, errors: list[str]) -> None:
    if schema is True or schema == {}:
        return
    if schema is False:
        errors.append(f"{path}: not allowed")
        return
    if "$ref" in schema:
        _validate(value, _resolve(root, schema["$ref"]), root, path, errors)
    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_TYPES[t](value) for t in types):
            errors.append(f"{path}: expected type {types}, got {type(value).__name__}")
            return
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} not in enum {schema['enum']}")
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{path}: shorter than minLength {schema['minLength']}")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append(f"{path}: longer than maxLength {schema['maxLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{path}: {value!r} does not match pattern {schema['pattern']}")
        fmt = schema.get("format")
        if fmt in _FORMATS and not _FORMATS[fmt].match(value):
            errors.append(f"{path}: {value!r} is not a valid {fmt}")
    if _TYPES["number"](value):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: {value} < minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: {value} > maximum {schema['maximum']}")
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{path}: fewer than minItems {schema['minItems']}")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"{path}: more than maxItems {schema['maxItems']}")
        if schema.get("uniqueItems"):
            seen = [json.dumps(v, sort_keys=True) for v in value]
            if len(seen) != len(set(seen)):
                errors.append(f"{path}: items are not unique")
        if "items" in schema:
            for i, item in enumerate(value):
                _validate(item, schema["items"], root, f"{path}[{i}]", errors)
    if isinstance(value, dict):
        if "minProperties" in schema and len(value) < schema["minProperties"]:
            errors.append(f"{path}: fewer than minProperties {schema['minProperties']}")
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing required property {key!r}")
        props = schema.get("properties", {})
        for key, sub in props.items():
            if key in value:
                _validate(value[key], sub, root, f"{path}.{key}", errors)
        extra = schema.get("additionalProperties", True)
        for key in value:
            if key in props:
                continue
            if extra is False:
                errors.append(f"{path}: additional property {key!r} not allowed")
            elif isinstance(extra, dict):
                _validate(value[key], extra, root, f"{path}.{key}", errors)
    for sub in schema.get("allOf", []):
        _validate(value, sub, root, path, errors)
    for keyword, want in (("anyOf", None), ("oneOf", 1)):
        if keyword in schema:
            matches = 0
            for sub in schema[keyword]:
                sub_errors: list[str] = []
                _validate(value, sub, root, path, sub_errors)
                matches += not sub_errors
            if (want is None and matches == 0) or (want == 1 and matches != 1):
                errors.append(f"{path}: does not satisfy {keyword} ({matches} branches matched)")


def validate(instance: Any, schema: dict) -> list[str]:
    """Return a list of human-readable validation errors (empty list means valid)."""
    errors: list[str] = []
    _validate(instance, schema, schema, "$", errors)
    return errors
