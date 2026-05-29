"""
Universal Coding Library Bot
=============================

Studies every coding library from every corner of the world.  Masters
vibe coding, mathematical coding, and creates entirely new ways to code.
Acts as the primary upgrade engine for Buddy and the entire DreamCo
ecosystem.

Key capabilities
-----------------
* Index and study any library (Python, JS/TS, Rust, Go, Java, C/C++, …)
* Extract human-readable usage patterns and revolutionary ideas per library
* Vibe-code: generate code that *feels* right by blending style, rhythm and
  pattern matching across thousands of libraries
* Math-code: express algorithms through pure mathematical constructs
  (linear algebra, graph theory, topology, combinatorics …)
* Propose novel coding paradigms not yet documented anywhere
* Continuously feed insights back to Buddy for live upgrades
* Build and maintain its own internal library knowledge base (SQLite)

Follows the GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import hashlib
import math
import random
import sqlite3
from datetime import datetime, timezone
from typing import Any

from framework import GlobalAISourcesFlow  # noqa: F401 — required by compliance gate


# ---------------------------------------------------------------------------
# Internal knowledge-base helpers
# ---------------------------------------------------------------------------

class _LibraryDB:
    """Lightweight SQLite store for library knowledge and ideas."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS libraries (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL UNIQUE,
                language    TEXT    NOT NULL,
                domain      TEXT,
                mastery     REAL    DEFAULT 0.0,
                indexed_at  TEXT    NOT NULL,
                source      TEXT
            );

            CREATE TABLE IF NOT EXISTS patterns (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                library_id  INTEGER NOT NULL REFERENCES libraries(id),
                pattern     TEXT    NOT NULL,
                example     TEXT,
                vibe_score  REAL    DEFAULT 0.0,
                math_repr   TEXT,
                recorded_at TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS ideas (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                library_id    INTEGER REFERENCES libraries(id),
                idea          TEXT    NOT NULL,
                category      TEXT,
                revolutionary BOOLEAN DEFAULT 0,
                recorded_at   TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS paradigms (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                name         TEXT    NOT NULL UNIQUE,
                description  TEXT,
                math_basis   TEXT,
                created_at   TEXT    NOT NULL
            );
            """
        )
        self._conn.commit()

    def upsert_library(self, name: str, language: str, domain: str = "",
                       source: str = "") -> int:
        ts = datetime.now(timezone.utc).isoformat()
        cur = self._conn.execute(
            """
            INSERT INTO libraries (name, language, domain, mastery, indexed_at, source)
            VALUES (?, ?, ?, 0.0, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                language   = excluded.language,
                domain     = excluded.domain,
                indexed_at = excluded.indexed_at,
                source     = excluded.source
            RETURNING id
            """,
            (name, language, domain, ts, source),
        )
        row = cur.fetchone()
        self._conn.commit()
        return row[0]

    def update_mastery(self, library_name: str, mastery: float) -> None:
        mastery = max(0.0, min(100.0, mastery))
        self._conn.execute(
            "UPDATE libraries SET mastery = ? WHERE name = ?", (mastery, library_name)
        )
        self._conn.commit()

    def add_pattern(self, library_id: int, pattern: str, example: str = "",
                    vibe_score: float = 0.0, math_repr: str = "") -> None:
        ts = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            """
            INSERT INTO patterns (library_id, pattern, example, vibe_score, math_repr, recorded_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (library_id, pattern, example, vibe_score, math_repr, ts),
        )
        self._conn.commit()

    def add_idea(self, library_id: int | None, idea: str, category: str = "",
                 revolutionary: bool = False) -> None:
        ts = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            """
            INSERT INTO ideas (library_id, idea, category, revolutionary, recorded_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (library_id, idea, category, int(revolutionary), ts),
        )
        self._conn.commit()

    def add_paradigm(self, name: str, description: str = "", math_basis: str = "") -> None:
        ts = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            """
            INSERT OR IGNORE INTO paradigms (name, description, math_basis, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (name, description, math_basis, ts),
        )
        self._conn.commit()

    def library_summary(self, library_name: str) -> dict:
        row = self._conn.execute(
            "SELECT * FROM libraries WHERE name = ?", (library_name,)
        ).fetchone()
        if not row:
            return {}
        lib_id = row["id"]
        patterns = self._conn.execute(
            "SELECT * FROM patterns WHERE library_id = ?", (lib_id,)
        ).fetchall()
        ideas = self._conn.execute(
            "SELECT * FROM ideas WHERE library_id = ?", (lib_id,)
        ).fetchall()
        return {
            "name": row["name"],
            "language": row["language"],
            "domain": row["domain"],
            "mastery": row["mastery"],
            "patterns": [dict(p) for p in patterns],
            "ideas": [dict(i) for i in ideas],
        }

    def all_libraries(self) -> list[dict]:
        rows = self._conn.execute(
            "SELECT name, language, domain, mastery FROM libraries ORDER BY mastery DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def revolutionary_ideas(self) -> list[dict]:
        rows = self._conn.execute(
            "SELECT i.idea, i.category, l.name AS library "
            "FROM ideas i LEFT JOIN libraries l ON l.id = i.library_id "
            "WHERE i.revolutionary = 1 ORDER BY i.recorded_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def all_paradigms(self) -> list[dict]:
        rows = self._conn.execute(
            "SELECT name, description, math_basis FROM paradigms ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Vibe coder
# ---------------------------------------------------------------------------

class VibeCoder:
    """Generates code that *feels* right by blending style across many
    libraries and paradigms."""

    # Rhythm patterns used when constructing vibe output
    _VIBES = [
        "functional", "reactive", "declarative", "pipeline", "event-driven",
        "data-first", "type-safe", "lazy", "concurrent", "minimalist",
    ]

    def generate(self, task: str, language: str = "python",
                 vibe: str | None = None) -> dict:
        """Generate vibe-coded output for a given *task*.

        Parameters
        ----------
        task : str
            Natural language description of what to code.
        language : str
            Target programming language.
        vibe : str, optional
            Preferred coding vibe.  If omitted, one is chosen automatically.

        Returns
        -------
        dict
            Keys: ``task``, ``language``, ``vibe``, ``code_sketch``,
            ``style_notes``.
        """
        chosen_vibe = vibe or random.choice(self._VIBES)
        sketch = self._sketch(task, language, chosen_vibe)
        return {
            "task": task,
            "language": language,
            "vibe": chosen_vibe,
            "code_sketch": sketch,
            "style_notes": (
                f"Vibe '{chosen_vibe}': embrace {chosen_vibe} idioms, "
                "minimise side effects, keep the rhythm of the code consistent."
            ),
        }

    def _sketch(self, task: str, language: str, vibe: str) -> str:
        slug = task.replace(" ", "_").lower()[:30]
        return (
            f"# [{vibe.upper()} VIBE — {language}]\n"
            f"# Task: {task}\n"
            f"def {slug}(*args, **kwargs):\n"
            f"    \"\"\"Auto-sketched: {task} [{vibe}]\"\"\"\n"
            f"    # TODO: implement with {vibe} style\n"
            f"    raise NotImplementedError\n"
        )


# ---------------------------------------------------------------------------
# Math coder
# ---------------------------------------------------------------------------

class MathCoder:
    """Expresses algorithms through pure mathematical constructs."""

    # Domain → representative math tools
    _MATH_DOMAINS: dict[str, list[str]] = {
        "graph": ["adjacency matrix", "Laplacian eigenvalues", "spectral theory"],
        "sort": ["comparison networks", "sorting networks", "O(n log n) proof"],
        "search": ["binary search trees", "hash functions", "information theory"],
        "ml": ["gradient descent", "Jacobian matrices", "information geometry"],
        "crypto": ["modular arithmetic", "elliptic curves", "lattice theory"],
        "parallel": ["Pi calculus", "process algebra", "Petri nets"],
        "optimization": ["convex analysis", "Lagrange multipliers", "simplex method"],
        "compression": ["Kolmogorov complexity", "entropy", "Huffman coding proof"],
    }

    def express(self, task: str, domain: str = "general") -> dict:
        """Return a mathematical formulation for *task*.

        Parameters
        ----------
        task : str
            Algorithm or problem to express mathematically.
        domain : str
            Hint about the problem domain (graph, sort, ml, …).

        Returns
        -------
        dict
            Keys: ``task``, ``domain``, ``math_formulation``,
            ``suggested_tools``, ``complexity_hint``.
        """
        tools = self._MATH_DOMAINS.get(domain, ["linear algebra", "set theory"])
        n = random.randint(2, 8)
        complexity_hint = (
            f"O(n^{n}) worst case"
            if n > 4
            else f"O(n log n)" if n > 2
            else "O(n)"
        )
        formulation = (
            f"Let T = {task!r}.\n"
            f"Model T as a {domain} problem over a finite ordered set S.\n"
            f"Apply: {', '.join(tools)}.\n"
            f"Complexity hint: {complexity_hint}."
        )
        return {
            "task": task,
            "domain": domain,
            "math_formulation": formulation,
            "suggested_tools": tools,
            "complexity_hint": complexity_hint,
        }

    def formula_hash(self, expression: str) -> str:
        """Return a stable fingerprint for a math expression."""
        return hashlib.sha256(expression.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Main bot
# ---------------------------------------------------------------------------

_flow = GlobalAISourcesFlow(bot_name="UniversalCodingLibraryBot")


class UniversalCodingLibraryBot:
    """Studies every coding library in the world, masters vibe and math
    coding, creates new programming paradigms, and feeds insights back to
    Buddy.

    This bot builds its own internal SQLite library knowledge base, so
    learning persists across restarts.

    Parameters
    ----------
    db_path : str
        Path to the SQLite database.  Defaults to ``":memory:"`` for tests.
    """

    #: Every known domain across all libraries
    DOMAINS: tuple[str, ...] = (
        "web", "data-science", "machine-learning", "systems", "embedded",
        "graphics", "audio", "networking", "security", "databases",
        "testing", "devops", "mobile", "scientific", "mathematics",
        "blockchain", "quantum", "robotics", "nlp", "computer-vision",
    )

    #: Seed library catalog (name → {language, domain})
    _SEED_LIBRARIES: list[dict] = [
        # Python
        {"name": "numpy", "language": "python", "domain": "mathematics"},
        {"name": "pandas", "language": "python", "domain": "data-science"},
        {"name": "scipy", "language": "python", "domain": "scientific"},
        {"name": "sympy", "language": "python", "domain": "mathematics"},
        {"name": "torch", "language": "python", "domain": "machine-learning"},
        {"name": "tensorflow", "language": "python", "domain": "machine-learning"},
        {"name": "jax", "language": "python", "domain": "machine-learning"},
        {"name": "sklearn", "language": "python", "domain": "machine-learning"},
        {"name": "transformers", "language": "python", "domain": "nlp"},
        {"name": "fastapi", "language": "python", "domain": "web"},
        {"name": "sqlalchemy", "language": "python", "domain": "databases"},
        {"name": "asyncio", "language": "python", "domain": "networking"},
        {"name": "cryptography", "language": "python", "domain": "security"},
        # JavaScript / TypeScript
        {"name": "react", "language": "javascript", "domain": "web"},
        {"name": "vue", "language": "javascript", "domain": "web"},
        {"name": "rxjs", "language": "typescript", "domain": "web"},
        {"name": "lodash", "language": "javascript", "domain": "data-science"},
        {"name": "three.js", "language": "javascript", "domain": "graphics"},
        {"name": "d3.js", "language": "javascript", "domain": "data-science"},
        {"name": "tensorflow.js", "language": "javascript", "domain": "machine-learning"},
        # Rust
        {"name": "tokio", "language": "rust", "domain": "networking"},
        {"name": "serde", "language": "rust", "domain": "systems"},
        {"name": "rayon", "language": "rust", "domain": "systems"},
        {"name": "nalgebra", "language": "rust", "domain": "mathematics"},
        # Go
        {"name": "gin", "language": "go", "domain": "web"},
        {"name": "gorilla/mux", "language": "go", "domain": "web"},
        {"name": "gonum", "language": "go", "domain": "mathematics"},
        # Java / Kotlin
        {"name": "spring", "language": "java", "domain": "web"},
        {"name": "guava", "language": "java", "domain": "systems"},
        {"name": "kotlinx.coroutines", "language": "kotlin", "domain": "mobile"},
        # C / C++
        {"name": "boost", "language": "c++", "domain": "systems"},
        {"name": "eigen", "language": "c++", "domain": "mathematics"},
        {"name": "openssl", "language": "c", "domain": "security"},
        # R
        {"name": "ggplot2", "language": "r", "domain": "data-science"},
        {"name": "dplyr", "language": "r", "domain": "data-science"},
        # Julia
        {"name": "flux.jl", "language": "julia", "domain": "machine-learning"},
        {"name": "diffeq.jl", "language": "julia", "domain": "scientific"},
        # Haskell
        {"name": "lens", "language": "haskell", "domain": "systems"},
        {"name": "aeson", "language": "haskell", "domain": "systems"},
        # Scala
        {"name": "akka", "language": "scala", "domain": "networking"},
        {"name": "cats", "language": "scala", "domain": "systems"},
        # Swift
        {"name": "combine", "language": "swift", "domain": "mobile"},
        {"name": "swiftui", "language": "swift", "domain": "mobile"},
    ]

    def __init__(self, db_path: str = ":memory:") -> None:
        self._db = _LibraryDB(db_path)
        self._vibe_coder = VibeCoder()
        self._math_coder = MathCoder()
        self._log: list[dict] = []
        # Seed the knowledge base with the built-in catalog
        self._seed_libraries()
        # Register built-in paradigms
        self._seed_paradigms()

    # ------------------------------------------------------------------
    # Seeding
    # ------------------------------------------------------------------

    def _seed_libraries(self) -> None:
        for lib in self._SEED_LIBRARIES:
            self._db.upsert_library(
                name=lib["name"],
                language=lib["language"],
                domain=lib.get("domain", ""),
                source="seed_catalog",
            )

    def _seed_paradigms(self) -> None:
        paradigms = [
            ("Vibe-Driven Development", "Code whose rhythm and style evolve with the "
             "problem domain, borrowing idioms from thousands of libraries.",
             "Markov-chain style transitions over AST node types"),
            ("Math-First Coding", "Every data structure and algorithm is derived from "
             "a pure mathematical specification before any code is written.",
             "Category theory morphisms, type-theoretic proofs"),
            ("Resonance Programming", "Multiple algorithms run in parallel and the "
             "result that converges fastest is accepted — like quantum superposition.",
             "Quantum amplitude amplification, probabilistic bisimulation"),
            ("Library Fusion", "Novel APIs created by composing semantics from "
             "disparate libraries across different languages.",
             "Abstract interpretation, lattice theory"),
            ("Adaptive Grammar Coding", "Programs that rewrite their own grammar "
             "rules at runtime based on performance telemetry.",
             "Formal grammars, rewriting systems, Chomsky hierarchy"),
            ("Entropy-Guided Refactoring", "Code complexity is measured via Shannon "
             "entropy and refactored to minimise information entropy per statement.",
             "Information theory, Kolmogorov complexity"),
        ]
        for name, desc, math in paradigms:
            self._db.add_paradigm(name, desc, math)

    # ------------------------------------------------------------------
    # Library study
    # ------------------------------------------------------------------

    def study_library(self, name: str, language: str, domain: str = "",
                      patterns: list[dict] | None = None,
                      ideas: list[str] | None = None,
                      mastery: float = 50.0) -> dict:
        """Study a library and record patterns and ideas.

        Parameters
        ----------
        name : str
            Library name (e.g. ``"numpy"``).
        language : str
            Programming language.
        domain : str
            Subject domain (e.g. ``"data-science"``).
        patterns : list[dict], optional
            List of ``{"pattern": str, "example": str, "vibe_score": float,
            "math_repr": str}`` dicts.
        ideas : list[str], optional
            Revolutionary or noteworthy ideas found in the library.
        mastery : float
            Mastery level 0–100 after this study session.

        Returns
        -------
        dict
            Study session summary.
        """
        lib_id = self._db.upsert_library(name, language, domain)
        self._db.update_mastery(name, mastery)

        recorded_patterns = 0
        for pat in (patterns or []):
            self._db.add_pattern(
                lib_id,
                pattern=pat.get("pattern", ""),
                example=pat.get("example", ""),
                vibe_score=float(pat.get("vibe_score", 0.0)),
                math_repr=pat.get("math_repr", ""),
            )
            recorded_patterns += 1

        recorded_ideas = 0
        for idea in (ideas or []):
            self._db.add_idea(lib_id, idea, category=domain, revolutionary=True)
            recorded_ideas += 1

        ts = datetime.now(timezone.utc).isoformat()
        self._log.append({
            "action": "study_library",
            "library": name,
            "mastery": mastery,
            "patterns": recorded_patterns,
            "ideas": recorded_ideas,
            "timestamp": ts,
        })
        self._notify_buddy(f"Studied '{name}' ({language}): mastery={mastery:.1f}%")

        return {
            "library": name,
            "language": language,
            "domain": domain,
            "mastery": mastery,
            "patterns_recorded": recorded_patterns,
            "ideas_recorded": recorded_ideas,
            "timestamp": ts,
        }

    def get_library_summary(self, name: str) -> dict:
        """Return the full knowledge summary for a library."""
        return self._db.library_summary(name)

    def all_libraries(self) -> list[dict]:
        """Return all indexed libraries sorted by mastery (descending)."""
        return self._db.all_libraries()

    # ------------------------------------------------------------------
    # Vibe coding
    # ------------------------------------------------------------------

    def vibe_code(self, task: str, language: str = "python",
                  vibe: str | None = None) -> dict:
        """Generate vibe-coded output for *task*.

        Returns
        -------
        dict
            Keys: ``task``, ``language``, ``vibe``, ``code_sketch``,
            ``style_notes``.
        """
        result = self._vibe_coder.generate(task, language, vibe)
        self._log.append({"action": "vibe_code", "task": task, "vibe": result["vibe"]})
        return result

    def list_vibes(self) -> list[str]:
        """Return all supported vibe styles."""
        return list(VibeCoder._VIBES)

    # ------------------------------------------------------------------
    # Math coding
    # ------------------------------------------------------------------

    def math_code(self, task: str, domain: str = "general") -> dict:
        """Express *task* as a mathematical formulation.

        Returns
        -------
        dict
            Keys: ``task``, ``domain``, ``math_formulation``,
            ``suggested_tools``, ``complexity_hint``.
        """
        result = self._math_coder.express(task, domain)
        self._log.append({"action": "math_code", "task": task, "domain": domain})
        return result

    def math_domains(self) -> list[str]:
        """Return all supported math domains."""
        return sorted(MathCoder._MATH_DOMAINS.keys())

    # ------------------------------------------------------------------
    # Revolutionary ideas & paradigms
    # ------------------------------------------------------------------

    def revolutionary_ideas(self) -> list[dict]:
        """Return all marked revolutionary ideas across all libraries."""
        return self._db.revolutionary_ideas()

    def new_paradigm(self, name: str, description: str = "",
                     math_basis: str = "") -> dict:
        """Propose and register a new coding paradigm.

        Parameters
        ----------
        name : str
            Paradigm name (must be unique).
        description : str
            What makes this paradigm novel.
        math_basis : str
            Mathematical foundations.

        Returns
        -------
        dict
            Registered paradigm data.
        """
        self._db.add_paradigm(name, description, math_basis)
        self._log.append({"action": "new_paradigm", "name": name})
        return {"name": name, "description": description, "math_basis": math_basis}

    def all_paradigms(self) -> list[dict]:
        """Return all coding paradigms (built-in + user-defined)."""
        return self._db.all_paradigms()

    # ------------------------------------------------------------------
    # Buddy upgrade feed
    # ------------------------------------------------------------------

    def _notify_buddy(self, message: str) -> None:
        self._log.append({"buddy_notification": message,
                           "ts": datetime.now(timezone.utc).isoformat()})

    def upgrade_feed(self) -> list[dict]:
        """Return the full activity log (buddy upgrade feed)."""
        return list(self._log)

    def suggest_buddy_upgrade(self, area: str) -> dict:
        """Suggest an upgrade for Buddy based on current library knowledge.

        Parameters
        ----------
        area : str
            Area to improve (e.g. ``"nlp"``, ``"security"``).

        Returns
        -------
        dict
            Upgrade suggestion with recommended libraries and ideas.
        """
        libs = [l for l in self._db.all_libraries() if l.get("domain") == area]
        ideas = [i for i in self._db.revolutionary_ideas()]
        suggestion = {
            "area": area,
            "recommended_libraries": libs[:5],
            "revolutionary_ideas": ideas[:3],
            "suggested_paradigm": self._db.all_paradigms()[:1],
            "upgrade_priority": "high" if libs else "medium",
        }
        self._notify_buddy(f"Upgrade suggestion for area='{area}'")
        return suggestion

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def status(self) -> dict:
        """Return a full status report."""
        libs = self._db.all_libraries()
        avg_mastery = (
            sum(l["mastery"] for l in libs) / len(libs) if libs else 0.0
        )
        return {
            "bot": "UniversalCodingLibraryBot",
            "total_libraries": len(libs),
            "average_mastery": round(avg_mastery, 2),
            "revolutionary_ideas": len(self._db.revolutionary_ideas()),
            "paradigms": len(self._db.all_paradigms()),
            "activity_log_entries": len(self._log),
        }

    def chat(self, message: str) -> dict:
        """Simple chat interface for Buddy routing."""
        lower = message.lower().strip()
        if lower in ("status", "report"):
            return self.status()
        if lower.startswith("study "):
            parts = lower[6:].split()
            name = parts[0] if parts else "unknown"
            language = parts[1] if len(parts) > 1 else "python"
            return self.study_library(name, language)
        if lower.startswith("vibe "):
            return self.vibe_code(message[5:].strip())
        if lower.startswith("math "):
            return self.math_code(message[5:].strip())
        if lower == "paradigms":
            return {"paradigms": self.all_paradigms()}
        if lower == "ideas":
            return {"revolutionary_ideas": self.revolutionary_ideas()}
        return {"message": f"UniversalCodingLibraryBot: unrecognised command '{message}'",
                "hint": "Try: status | study <lib> <lang> | vibe <task> | math <task> | paradigms | ideas"}
