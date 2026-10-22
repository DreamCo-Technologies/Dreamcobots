"""Minimal, offline GEDCOM importer with explicit provenance and privacy defaults.

No network access, genetic inference, or storage of personal records.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import re

LINE = re.compile(r"^(\d+)\s+(?:(@[^@\s]+@)\s+)?([A-Z0-9_]+)(?:\s+(.*))?$")
MAX_BYTES = 2_000_000
MAX_LINES = 50_000

@dataclass
class Person:
    id: str
    name: str = ""
    birth: str = ""
    death: str = ""
    sources: list[str] = field(default_factory=list)

def parse_gedcom(data: str, *, include_living: bool = False) -> dict:
    """Parse limited GEDCOM INDI records; exclude potentially living by default.

    Missing death evidence does not establish living status. By default those
    records are withheld pending explicit review, including historical cases.
    """
    if not isinstance(data, str) or len(data.encode("utf-8")) > MAX_BYTES:
        raise ValueError("Invalid or oversized GEDCOM input")
    people: dict[str, Person] = {}
    current = None
    event = None
    count = 0
    for raw in data.splitlines():
        count += 1
        if count > MAX_LINES:
            raise ValueError("Too many GEDCOM lines")
        match = LINE.fullmatch(raw.strip())
        if not match:
            if raw.strip():
                raise ValueError("Malformed GEDCOM line")
            continue
        level, pointer, tag, value = match.groups()
        level = int(level)
        value = value or ""
        if level == 0:
            current = None
            event = None
            if pointer and tag == "INDI":
                if pointer in people:
                    raise ValueError("Duplicate individual identifier")
                current = Person(id=pointer)
                people[pointer] = current
            continue
        if current is None:
            continue
        if level == 1:
            event = tag if tag in {"BIRT", "DEAT"} else None
            if tag == "NAME":
                current.name = value[:300]
            elif tag == "SOUR":
                current.sources.append(value[:300])
        elif level == 2 and tag == "DATE" and event:
            if event == "BIRT":
                current.birth = value[:100]
            elif event == "DEAT":
                current.death = value[:100]
        elif level == 2 and tag == "SOUR":
            current.sources.append(value[:300])
    exported = []
    withheld = 0
    for person in people.values():
        if not include_living and not person.death:
            withheld += 1
            continue
        exported.append({"id": person.id, "name": person.name,
                         "birth": person.birth, "death": person.death,
                         "sources": person.sources, "verified": False})
    return {"people": exported, "withheld_without_death_evidence": withheld,
            "count": len(exported), "requires_human_source_review": True}
