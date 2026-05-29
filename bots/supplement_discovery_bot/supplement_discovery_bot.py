# GLOBAL AI SOURCES FLOW
"""Supplement Discovery Bot — researches compounds, natural remedies, and supplements with evidence grading."""
import sys
import os
import sqlite3
import json
from datetime import datetime, timezone
_REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
from framework import GlobalAISourcesFlow  # noqa: F401

from bots.dreamco_science.evidence_grading import SAFETY_DISCLAIMER, grade_evidence


VALID_CATEGORIES = {
    'supplement',
    'herb',
    'food_compound',
    'biotech',
    'traditional_remedy',
}


class SupplementDiscoveryBot:
    """Track supplement and compound research with safety-oriented evidence grading."""

    def __init__(self, db_path: str = ':memory:'):
        self._db = sqlite3.connect(db_path, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS compounds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                evidence_level TEXT NOT NULL,
                sources TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )
        self._db.commit()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def add_compound(self, name, type, description, evidence_level, sources=None) -> dict:
        sources = sources or []
        if type not in VALID_CATEGORIES:
            raise ValueError(f'Unsupported compound category: {type}')
        normalized = grade_evidence(evidence_level).value
        ts = self._now()
        cur = self._db.execute(
            'INSERT INTO compounds (name, category, description, evidence_level, sources, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (name, type, description, normalized, json.dumps(list(sources)), ts, ts),
        )
        self._db.commit()
        return {
            'id': cur.lastrowid,
            'name': name,
            'type': type,
            'evidence_level': normalized,
            'sources': list(sources),
            'disclaimer': SAFETY_DISCLAIMER,
        }

    def classify_compound(self, compound_id, new_evidence_level) -> dict:
        normalized = grade_evidence(new_evidence_level).value
        self._db.execute(
            'UPDATE compounds SET evidence_level = ?, updated_at = ? WHERE id = ?',
            (normalized, self._now(), compound_id),
        )
        self._db.commit()
        row = self._db.execute('SELECT * FROM compounds WHERE id = ?', (compound_id,)).fetchone()
        if not row:
            raise KeyError(f'Compound {compound_id} not found')
        result = dict(row)
        result['sources'] = json.loads(result['sources'])
        result['type'] = result.pop('category')
        result['disclaimer'] = SAFETY_DISCLAIMER
        return result

    def search_compounds(self, query, evidence_level=None) -> list:
        term = f"%{query.lower()}%"
        params = [term, term]
        sql = 'SELECT * FROM compounds WHERE lower(name) LIKE ? OR lower(description) LIKE ?'
        if evidence_level:
            sql += ' AND evidence_level = ?'
            params.append(grade_evidence(evidence_level).value)
        sql += ' ORDER BY id DESC'
        rows = self._db.execute(sql, params).fetchall()
        return [self._row_to_dict(row) for row in rows]

    def get_compounds_by_category(self, category) -> list:
        if category not in VALID_CATEGORIES:
            raise ValueError(f'Unsupported compound category: {category}')
        rows = self._db.execute('SELECT * FROM compounds WHERE category = ? ORDER BY id DESC', (category,)).fetchall()
        return [self._row_to_dict(row) for row in rows]

    def safety_check(self, compound_name) -> dict:
        row = self._db.execute('SELECT * FROM compounds WHERE lower(name) = lower(?) ORDER BY id DESC LIMIT 1', (compound_name,)).fetchone()
        if not row:
            return {
                'compound_name': compound_name,
                'safety_status': 'unknown',
                'evidence_level': 'unverified',
                'disclaimer': SAFETY_DISCLAIMER,
            }
        item = self._row_to_dict(row)
        level = item['evidence_level']
        if level == 'unsafe':
            status = 'avoid'
        elif level in {'experimental', 'unverified'}:
            status = 'use_caution'
        else:
            status = 'research_supported'
        return {
            'compound_name': item['name'],
            'category': item['type'],
            'safety_status': status,
            'evidence_level': level,
            'disclaimer': SAFETY_DISCLAIMER,
        }

    def _row_to_dict(self, row) -> dict:
        result = dict(row)
        result['sources'] = json.loads(result['sources'])
        result['type'] = result.pop('category')
        result['disclaimer'] = SAFETY_DISCLAIMER
        return result
