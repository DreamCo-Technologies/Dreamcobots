"""
models.py — Database schema (SQLAlchemy-style models).

Defines the ORM models for the DreamCo Global Learning System. Uses
standard Python dataclasses as a lightweight stand-in that mirrors the
structure of SQLAlchemy declarative models (swap for real SQLAlchemy in
production environments).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Base helper
# ---------------------------------------------------------------------------

class Base:
    """Lightweight metaclass placeholder mirroring SQLAlchemy's Base."""

    _registry: List[type] = []

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        Base._registry.append(cls)

    @classmethod
    def get_all_models(cls) -> List[type]:
        """Return all models that inherit from Base."""
        return list(cls._registry)


# ---------------------------------------------------------------------------
# ORM models
# ---------------------------------------------------------------------------

@dataclass
class ResearchPaper(Base):
    """Persisted record for an ingested research paper."""

    id: Optional[int] = None
    title: str = ""
    authors: str = ""          # comma-separated
    abstract: str = ""
    source: str = ""
    url: str = ""
    published_date: Optional[str] = None
    tags: str = ""             # comma-separated
    created_at: str = field(default_factory=_now)

    # -- column definitions (informational for documentation purposes) --
    __tablename__ = "research_papers"
    __columns__ = {
        # Note: AUTOINCREMENT is SQLite syntax; use SERIAL/BIGSERIAL for PostgreSQL.
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "title": "TEXT NOT NULL",
        "authors": "TEXT",
        "abstract": "TEXT",
        "source": "VARCHAR(64)",
        "url": "TEXT UNIQUE",
        "published_date": "DATE",
        "tags": "TEXT",
        "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    }


@dataclass
class ExperimentResult(Base):
    """Persisted record for a sandbox experiment result."""

    id: Optional[int] = None
    run_id: str = ""
    experiment_name: str = ""
    status: str = "pending"
    metrics: str = ""          # JSON string
    duration_ms: float = 0.0
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    created_at: str = field(default_factory=_now)

    __tablename__ = "experiment_results"
    __columns__ = {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "run_id": "VARCHAR(64) UNIQUE NOT NULL",
        "experiment_name": "TEXT NOT NULL",
        "status": "VARCHAR(16) DEFAULT 'pending'",
        "metrics": "TEXT",
        "duration_ms": "FLOAT",
        "started_at": "TIMESTAMP",
        "completed_at": "TIMESTAMP",
        "error": "TEXT",
        "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    }


@dataclass
class BotDeployment(Base):
    """Persisted record for a bot strategy deployment."""

    id: Optional[int] = None
    deployment_id: str = ""
    strategy_id: str = ""
    bot_name: str = ""
    version: str = ""
    status: str = "pending"
    deployed_at: Optional[str] = None
    rolled_back_at: Optional[str] = None
    created_at: str = field(default_factory=_now)

    __tablename__ = "bot_deployments"
    __columns__ = {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "deployment_id": "VARCHAR(64) UNIQUE NOT NULL",
        "strategy_id": "VARCHAR(128) NOT NULL",
        "bot_name": "VARCHAR(128) NOT NULL",
        "version": "VARCHAR(32)",
        "status": "VARCHAR(16) DEFAULT 'pending'",
        "deployed_at": "TIMESTAMP",
        "rolled_back_at": "TIMESTAMP",
        "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    }
