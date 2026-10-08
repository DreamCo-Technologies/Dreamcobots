#!/usr/bin/env python3
"""Canonical numbered proposals. No model calls, installs, or bot execution."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config/proposals/master-registry.json"
BASE_COUNT = 2200
MAX_BATCH = 100
DISCOVERY_CHANNELS = {'owner_request', 'industry_research', 'scientific_research',
                      'job_role', 'invention_opportunity', 'customer_request', 'capability_gap'}


def fingerprint(data):
    return hashlib.sha256(data).hexdigest()


def name_key(name):
    return " ".join(re.findall(r"\w+", unicodedata.normalize("NFKC", name).casefold()))


def entry(number, name=None, capabilities=None, source=None, source_status="missing"):
    return {
        "id": number, "key": f"proposal-{number:04d}",
        "division_id": (number - 1) // 10 + 1,
        "name": name, "purpose": (capabilities or [None])[0],
        "capabilities": capabilities or [], "source_status": source_status,
        "source": source, "status": "proposed", "implementation_refs": [],
        "tools": [], "system_dependencies": [], "required_packages": [],
        "apis": [], "workflows": [], "model_requirements": None,
        "revenue_model": None, "risk_review": "pending", "verification_evidence": [],
    }


def bootstrap(sources):
    """Recover only complete source rows; reserve every unavailable number."""
    systems = {i: entry(i) for i in range(1, BASE_COUNT + 1)}
    divisions = {i: {"id": i, "name": None} for i in range(1, 221)}
    for excerpt in sources["excerpts"]:
        lines = excerpt["text"].splitlines()
        active = None
        for index, line in enumerate(lines):
            division = re.match(r"^(?:#{1,4}\s+)?DIVISION\s+(\d+)\s*[—–-]\s*(.+)$", line)
            if division:
                did = int(division[1])
                if did in divisions:
                    divisions[did]["name"] = division[2].strip()
                active = None
            heading = re.match(r"^(?:#{2,4}\s+|\*\*)(\d+)\.\s+(.+?)(?:\*\*)?$", line)
            row = re.match(r"^\|\s*(\d+)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*$", line)
            if excerpt.get('format') == 'tsv':
                row = re.match(r'^(\d+)\t([^\t]+)\t(.+)$', line)
            match = row or heading
            if match:
                number = int(match[1])
                if not excerpt.get('min_id', 1) <= number <= excerpt.get('max_id', BASE_COUNT):
                    active = None
                    continue
                # An unfinished last heading is not an authenticated name.
                if heading and excerpt.get("truncated") and index == len(lines) - 1:
                    active = None
                    continue
                source = {"conversation_id": sources["conversation_id"],
                          "message_id": excerpt["message_id"], "line": index + 1,
                          "excerpt_sha256": fingerprint(excerpt["text"].encode())}
                if excerpt.get('attachment_sha256'):
                    source['attachment_sha256'] = excerpt['attachment_sha256']
                caps = [row[3].strip()] if row else []
                candidate = entry(number, match[2].strip(), caps, source, "recovered")
                if systems[number]["name"]:
                    if systems[number]['name'] != candidate['name'] or systems[number]['capabilities'] != candidate['capabilities']:
                        raise ValueError(f"Conflicting source for {number}")
                systems[number] = candidate
                active = number if heading else None
            elif active and line.startswith("- "):
                if index == len(lines) - 1 and excerpt.get("truncated"):
                    systems[active]["source_status"] = "partial"
                else:
                    systems[active]["capabilities"].append(line[2:])
            elif line.startswith(("#", "---", "**", "|")):
                active = None
        if active and excerpt.get("truncated"):
            systems[active]["source_status"] = "partial"
    for system in systems.values():
        system["purpose"] = next(iter(system["capabilities"]), None)
    result = {"schema_version": 1, "namespace": "dreamco.proposals",
              "baseline_count": BASE_COUNT, "next_id": BASE_COUNT + 1,
              "truth_boundary": "Proposals only; empty requirements are unknown, not unnecessary. Fleet IDs are a separate namespace.",
              "divisions": list(divisions.values()), "systems": list(systems.values()),
              "generation_requests": {}}
    validate(result)
    return result


def validate(data):
    if data.get("schema_version") != 1 or data.get("namespace") != "dreamco.proposals":
        raise ValueError("Unsupported registry schema/namespace")
    systems = data["systems"]
    if data.get("baseline_count") != BASE_COUNT:
        raise ValueError("Baseline count must remain 2200")
    if len(systems) < BASE_COUNT or [s["id"] for s in systems] != list(range(1, len(systems) + 1)):
        raise ValueError("IDs must be contiguous, unique, ordered, and preserve 1–2200")
    if data["next_id"] != len(systems) + 1:
        raise ValueError("Invalid next_id")
    divisions = {d["id"]: d for d in data["divisions"]}
    if len(divisions) != len(data["divisions"]):
        raise ValueError("Duplicate division")
    for s in systems:
        if s["key"] != f'proposal-{s["id"]:04d}' or s["division_id"] != (s["id"] - 1) // 10 + 1:
            raise ValueError("ID/key/division mismatch")
        if s["division_id"] not in divisions:
            raise ValueError("Missing division")
        if s["status"] != "proposed" or s["implementation_refs"] or s["verification_evidence"]:
            raise ValueError("Proposal registry cannot assert implementation or verification")
        if s["source_status"] not in {"missing", "partial", "recovered", "generated"}:
            raise ValueError("Invalid source status")
        if s["source_status"] == "missing":
            if s["name"] is not None or s["source"] is not None or s["capabilities"]:
                raise ValueError("Missing source cannot contain invented details")
        elif not isinstance(s["name"], str) or not name_key(s["name"]) or not s["source"]:
            raise ValueError("Named proposals require source provenance")
        for field in ("capabilities", "tools", "system_dependencies", "required_packages", "apis", "workflows"):
            if not isinstance(s[field], list):
                raise ValueError(f"{field} must be a list")
        if s["risk_review"] != "pending":
            raise ValueError("Proposal generation cannot approve risk")
    return data


def propose(data, seeds, request_id):
    validate(data)
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", request_id):
        raise ValueError("Use a 1–80 character request ID: letters, digits, _ or -")
    if not isinstance(seeds, list) or not 1 <= len(seeds) <= MAX_BATCH:
        raise ValueError(f"Provide 1–{MAX_BATCH} explicit proposals per batch")
    digest = fingerprint(json.dumps(seeds, sort_keys=True, ensure_ascii=False).encode())
    previous = data["generation_requests"].get(request_id)
    if previous:
        if previous["sha256"] != digest:
            raise ValueError("Request ID already used with different content")
        return copy.deepcopy(data), previous["ids"]
    updated = copy.deepcopy(data)
    known = {name_key(s["name"]) for s in data["systems"] if s["name"]}
    # Reuse existing fleet identities before considering a new numbered proposal.
    fleet = json.loads((REGISTRY.parents[1] / 'bots/bot-manifests.generated.json').read_text())
    existing_fleet = {name_key(label): bot['slug'] for bot in fleet['bots']
                      for label in (bot['name'], bot['slug'].replace('-', ' '))}
    known.update(existing_fleet)
    divisions = {d["id"]: d for d in updated["divisions"]}
    ids = []
    for seed in seeds:
        if not isinstance(seed, dict) or not {"name", "purpose", "division"} <= set(seed) or set(seed) - {"name", "purpose", "division", "discovery_channel"}:
            raise ValueError("Each seed needs name, purpose, division; only discovery_channel is optional")
        channel = seed.get('discovery_channel', 'owner_request')
        if channel not in DISCOVERY_CHANNELS:
            raise ValueError('Unknown discovery channel')
        for field, limit in (("name", 160), ("purpose", 2000), ("division", 160)):
            if not isinstance(seed[field], str) or not seed[field].strip() or len(seed[field]) > limit:
                raise ValueError(f"Invalid {field}")
            if any(ord(c) < 32 for c in seed[field]):
                raise ValueError("Control characters are not allowed")
        key = name_key(seed["name"])
        if key in existing_fleet:
            raise ValueError(f"Existing bot {existing_fleet[key]} already owns this name; reuse its identity")
        if not key or key in known:
            raise ValueError("Duplicate or empty normalized proposal name")
        meaningful = set(key.split()) - {'ai','bot','assistant','engine','system','intelligence'}
        for existing, slug in existing_fleet.items():
            other = set(existing.split()) - {'ai','bot','assistant','engine','system','intelligence'}
            if meaningful and meaningful == other:
                raise ValueError(f"Existing bot {slug} has the same meaningful name; reuse its identity")
        if len(meaningful) >= 3:
            for existing in known:
                other = set(existing.split()) - {'ai','bot','assistant','engine','system','intelligence'}
                if len(other) >= 3 and len(meaningful & other) / len(meaningful | other) >= 0.8:
                    raise ValueError('Near-duplicate name; review/reuse the existing proposal instead')
        known.add(key)
        number = updated["next_id"]
        did = (number - 1) // 10 + 1
        if did in divisions and divisions[did]["name"] != seed["division"].strip():
            raise ValueError(f"Division {did} already has a different name")
        if did not in divisions:
            divisions[did] = {"id": did, "name": seed["division"].strip()}
            updated["divisions"].append(divisions[did])
        updated["systems"].append(entry(number, seed["name"].strip(), [seed["purpose"].strip()],
                                      {"request_id": request_id, "seed_sha256": digest, "discovery_channel": channel}, "generated"))
        updated["next_id"] += 1
        ids.append(number)
    updated["generation_requests"][request_id] = {"sha256": digest, "ids": ids}
    return validate(updated), ids


def append(registry, seeds, request_id, expected_sha256):
    """Exclusive writer plus optimistic revision check and atomic replacement."""
    registry = Path(registry)
    lock = registry.with_suffix(".write-lock")
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    temp = None
    try:
        os.close(fd)
        raw = registry.read_bytes()
        if fingerprint(raw) != expected_sha256:
            raise ValueError("Stale registry revision; rescan and review again")
        updated, ids = propose(json.loads(raw), seeds, request_id)
        encoded = (json.dumps(updated, ensure_ascii=False, indent=2) + "\n").encode()
        with tempfile.NamedTemporaryFile(dir=registry.parent, delete=False) as stream:
            temp = Path(stream.name)
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temp, 0o644)
        os.replace(temp, registry)
        return ids
    finally:
        if temp and temp.exists():
            temp.unlink()
        lock.unlink()


def render_markdown(data):
    def cell(value):
        return str(value or 'Source needed').replace('|', '\\|').replace('\n', ' ')
    lines = ['# DreamCo canonical proposal master list', '',
             'Proposals only. Missing source is explicit; none of these records proves implementation.', '',
             '| ID | Division | Name | Purpose | Source status |',
             '| --- | --- | --- | --- | --- |']
    for s in data['systems']:
        lines.append(f"| {s['id']} | {s['division_id']} | {cell(s['name'])} | {cell(s['purpose'])} | {s['source_status']} |")
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--seed", type=Path)
    parser.add_argument("--request-id")
    parser.add_argument("--append", action="store_true")
    parser.add_argument("--expected-sha256")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    args = parser.parse_args()
    raw = args.registry.read_bytes()
    data = validate(json.loads(raw))
    if args.append and (not args.seed or not args.expected_sha256):
        parser.error("--append requires --seed and --expected-sha256")
    if args.seed:
        if not args.request_id:
            parser.error("--seed requires --request-id")
        if args.seed.stat().st_size > 1_000_000:
            parser.error("Seed exceeds 1 MB")
        seeds = json.loads(args.seed.read_text())
        updated, ids = propose(data, seeds, args.request_id)
        if args.append:
            append(args.registry, seeds, args.request_id, args.expected_sha256)
        print(json.dumps({"written": args.append, "base_sha256": fingerprint(raw),
                          "proposals": [updated["systems"][i-1] for i in ids]}, indent=2))
    elif args.format == 'markdown':
        print(render_markdown(data))
    else:
        print(json.dumps({"valid": True, "count": len(data["systems"]),
                          "missing_source": sum(s["source_status"] == "missing" for s in data["systems"]),
                          "sha256": fingerprint(raw)}))


if __name__ == "__main__":
    main()
