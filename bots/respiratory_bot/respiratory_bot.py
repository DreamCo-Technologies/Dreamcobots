# GLOBAL AI SOURCES FLOW
"""Respiratory Bot — researches lung health, breathing therapies, and oxygen optimization."""
import sys
import os
_REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
from framework import GlobalAISourcesFlow  # noqa: F401
import importlib.util
import sqlite3
from datetime import datetime, timezone

from bots.dreamco_science.evidence_grading import SAFETY_DISCLAIMER, grade_evidence

_spec = importlib.util.spec_from_file_location('_local_tiers', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tiers.py'))
_tiers = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_tiers)

SYSTEM_NAME = 'Respiratory System'
RESEARCH_DOMAINS = ['lung health', 'breathing therapies', 'oxygen optimization', 'respiratory recovery', 'airway science', 'sleep breathing']


class RespiratoryBotError(Exception):
    pass


class RespiratoryBotTierError(RespiratoryBotError):
    pass


class RespiratoryBot:
    """Researches respiratory resilience, lung therapies, and oxygen optimization."""

    def __init__(self, tier: str = 'free', db_path: str = ':memory:'):
        self.tier = tier
        self._db = self._init_db(db_path)

    def _init_db(self, db_path):
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS research_findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL,
                title TEXT NOT NULL,
                summary TEXT,
                evidence_level TEXT DEFAULT 'experimental',
                source TEXT,
                recorded_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS discovery_updates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                headline TEXT NOT NULL,
                details TEXT,
                posted_at TEXT NOT NULL
            );
            """
        )
        conn.commit()
        return conn

    def record_finding(self, domain: str, title: str, summary: str = '',
                       evidence_level: str = 'experimental', source: str = '') -> dict:
        if domain not in RESEARCH_DOMAINS:
            raise RespiratoryBotError(f"Domain '{domain}' not in scope. Valid: {RESEARCH_DOMAINS}")
        normalized_level = grade_evidence(evidence_level).value
        ts = datetime.now(timezone.utc).isoformat()
        cur = self._db.execute(
            "INSERT INTO research_findings (domain, title, summary, evidence_level, source, recorded_at) VALUES (?,?,?,?,?,?)",
            (domain, title, summary, normalized_level, source, ts),
        )
        self._db.commit()
        return {
            'id': cur.lastrowid,
            'domain': domain,
            'title': title,
            'evidence_level': normalized_level,
            'recorded_at': ts,
            'disclaimer': SAFETY_DISCLAIMER,
        }

    def get_findings(self, domain: str = None, evidence_level: str = None) -> list:
        query = 'SELECT * FROM research_findings WHERE 1=1'
        params = []
        if domain:
            query += ' AND domain=?'
            params.append(domain)
        if evidence_level:
            query += ' AND evidence_level=?'
            params.append(grade_evidence(evidence_level).value)
        query += ' ORDER BY id DESC'
        return [dict(r) for r in self._db.execute(query, params).fetchall()]

    def post_discovery_update(self, headline: str, details: str = '') -> dict:
        ts = datetime.now(timezone.utc).isoformat()
        cur = self._db.execute(
            'INSERT INTO discovery_updates (headline, details, posted_at) VALUES (?,?,?)',
            (headline, details, ts),
        )
        self._db.commit()
        return {
            'id': cur.lastrowid,
            'headline': headline,
            'posted_at': ts,
            'disclaimer': SAFETY_DISCLAIMER,
        }

    def get_discovery_feed(self, limit: int = 10) -> list:
        return [dict(r) for r in self._db.execute(
            'SELECT * FROM discovery_updates ORDER BY id DESC LIMIT ?',
            (limit,),
        ).fetchall()]

    def describe_tier(self) -> dict:
        return _tiers.get_tier_info(self.tier)

    def research_summary(self) -> dict:
        total = self._db.execute('SELECT COUNT(*) FROM research_findings').fetchone()[0]
        proven = self._db.execute(
            "SELECT COUNT(*) FROM research_findings WHERE evidence_level='proven'"
        ).fetchone()[0]
        return {
            'system': SYSTEM_NAME,
            'total_findings': total,
            'proven_findings': proven,
            'research_domains': RESEARCH_DOMAINS,
            'tier': self.tier,
            'disclaimer': SAFETY_DISCLAIMER,
        }
