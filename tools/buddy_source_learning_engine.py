#!/usr/bin/env python3
"""Buddy Source Learning Engine.

Fast path: discover -> verify -> fingerprint -> extract -> chunk -> rank -> retrieve -> practice -> benchmark -> learn.
This module intentionally separates knowledge acquisition from model training and never treats ingestion as mastery.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse


@dataclass(frozen=True)
class Source:
    uri: str
    kind: str  # book, movie, video, website, database, paper, course, repo, dataset
    title: str = ""
    license: str = "unknown"
    authority: float = 0.5
    freshness: float = 0.5
    relevance: float = 0.5
    accessibility: float = 0.5


@dataclass(frozen=True)
class LearningChunk:
    source_id: str
    chunk_id: str
    text: str
    topic: str
    modality: str
    license: str


@dataclass(frozen=True)
class StudyPlan:
    capability: str
    objective: str
    source_ids: tuple[str, ...]
    practice_tasks: tuple[str, ...]
    benchmark_ids: tuple[str, ...]
    mastery_requirements: tuple[str, ...]


def source_id(source: Source) -> str:
    raw = f"{source.kind}|{source.uri}|{source.title}".encode()
    return sha256(raw).hexdigest()[:16]


def score_source(source: Source, capability: str) -> float:
    """Rank sources without pretending a heuristic is ground truth."""
    kind_bonus = {
        "course": 0.10,
        "book": 0.10,
        "paper": 0.08,
        "database": 0.06,
        "website": 0.04,
        "repo": 0.06,
        "video": 0.05,
        "movie": 0.02,
        "dataset": 0.07,
    }.get(source.kind, 0.0)
    return round(
        min(1.0, 0.30 * source.authority + 0.25 * source.relevance +
                0.20 * source.freshness + 0.15 * source.accessibility + kind_bonus),
        4,
    )


def dedupe_sources(sources: Iterable[Source]) -> list[Source]:
    seen: set[str] = set()
    result: list[Source] = []
    for source in sources:
        key = source.uri.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(source)
    return result


def classify_uri(uri: str) -> str:
    path = urlparse(uri).path.lower()
    suffix = Path(path).suffix
    if suffix in {".pdf", ".epub", ".mobi"}:
        return "book"
    if suffix in {".mp4", ".mkv", ".mov", ".webm"}:
        return "movie"
    if suffix in {".csv", ".parquet", ".json", ".jsonl", ".db", ".sqlite"}:
        return "database"
    if "github.com" in uri.lower():
        return "repo"
    return "website"


def make_chunks(source: Source, text: str, *, chunk_size: int = 1800, overlap: int = 180) -> list[LearningChunk]:
    """Create deterministic chunks suitable for retrieval and later evaluation."""
    if chunk_size <= overlap or overlap < 0:
        raise ValueError("chunk_size must be greater than overlap")
    clean = " ".join(text.split())
    if not clean:
        return []
    sid = source_id(source)
    chunks: list[LearningChunk] = []
    start = 0
    index = 0
    while start < len(clean):
        end = min(len(clean), start + chunk_size)
        body = clean[start:end]
        cid = sha256(f"{sid}|{index}|{body}".encode()).hexdigest()[:16]
        chunks.append(LearningChunk(sid, cid, body, "unclassified", "text", source.license))
        if end == len(clean):
            break
        start = end - overlap
        index += 1
    return chunks


def build_study_plan(capability: str, sources: Iterable[Source], benchmark_ids: Iterable[str]) -> StudyPlan:
    ranked = sorted(dedupe_sources(sources), key=lambda item: score_source(item, capability), reverse=True)
    selected = ranked[:8]
    source_ids = tuple(source_id(item) for item in selected)
    tasks = (
        f"Explain {capability} from first principles.",
        f"Solve a novel {capability} task without copying source solutions.",
        f"Debug a deliberately flawed {capability} implementation.",
        f"Compare two approaches to {capability} and justify the choice.",
        f"Apply {capability} to an unseen scenario and state limitations.",
    )
    requirements = (
        "repeatable correctness threshold",
        "quality threshold",
        "speed threshold",
        "safety/policy checks",
        "independent explanation",
        "regression protection",
    )
    return StudyPlan(capability, f"Acquire and demonstrate {capability}", source_ids, tasks, tuple(benchmark_ids), requirements)


def learning_manifest(sources: Iterable[Source], capability: str, benchmark_ids: Iterable[str]) -> dict:
    unique = dedupe_sources(sources)
    plan = build_study_plan(capability, unique, benchmark_ids)
    return {
        "engine": "buddy-source-learning-engine-v1",
        "sources": [dict(asdict(item), id=source_id(item), score=score_source(item, capability)) for item in unique],
        "study_plan": asdict(plan),
        "principles": [
            "source ingestion is not training",
            "retrieval is not mastery",
            "book/movie/course completion is not mastery",
            "copyright and license metadata must travel with every chunk",
            "benchmark evidence determines capability state",
            "failed attempts generate targeted remediation",
        ],
    }


if __name__ == "__main__":
    demo = [
        Source("https://ocw.mit.edu/", "course", "MIT OpenCourseWare", "CC BY-NC-SA", .98, .9, .95, .95),
        Source("https://developers.google.com/books/docs/v1/reference/", "database", "Google Books API", "API terms", .95, .9, .75, .9),
    ]
    import json
    print(json.dumps(learning_manifest(demo, "retrieval-augmented generation", ["rag-quality", "rag-speed"]), indent=2))
