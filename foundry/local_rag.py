#!/usr/bin/env python3
"""Dependency-free local RAG store for sandbox tests and laptops."""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

TOKEN = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return TOKEN.findall(text.lower())


@dataclass
class Chunk:
    chunk_id: str
    text: str
    source: str
    license: str


class LocalRagStore:
    def __init__(self) -> None:
        self.chunks: list[Chunk] = []
        self._df: Counter[str] = Counter()

    def add(self, chunk: Chunk) -> None:
        self.chunks.append(chunk)
        self._df.update(set(tokenize(chunk.text)))

    def _tfidf(self, text: str) -> dict[str, float]:
        tokens = tokenize(text)
        tf = Counter(tokens)
        n = max(len(self.chunks), 1)
        return {
            token: (count / max(len(tokens), 1)) * math.log((n + 1) / (1 + self._df[token]))
            for token, count in tf.items()
        }

    @staticmethod
    def _dot(a: dict[str, float], b: dict[str, float]) -> float:
        return sum(a[k] * b[k] for k in a.keys() & b.keys())

    def query(self, text: str, k: int = 4) -> list[tuple[float, Chunk]]:
        q = self._tfidf(text)
        scored = [(self._dot(q, self._tfidf(chunk.text)), chunk) for chunk in self.chunks]
        scored.sort(key=lambda row: row[0], reverse=True)
        return [row for row in scored[:k] if row[0] > 0]
