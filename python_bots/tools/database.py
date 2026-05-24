"""
DreamCo OS — Database Tool
============================

Unified SQLite/Postgres access layer for structured bot storage.

Usage::

    tool = DatabaseTool()
    await tool.execute(operation="query", sql="SELECT COUNT(*) FROM bot_runs")
"""

from __future__ import annotations

import os
import sqlite3
from typing import Any

from python_bots.tools.base import BaseTool


class DatabaseTool(BaseTool):

    def __init__(self, db_url: str | None = None) -> None:
        self._url = db_url or os.getenv("DATABASE_URL", ".dreamco_state.db")

    @property
    def name(self) -> str:
        return "database"

    @property
    def description(self) -> str:
        return "Execute SQL queries against the DreamCo structured database."

    def schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {"type": "string", "enum": ["query", "execute"]},
                "sql": {"type": "string"},
                "params": {"type": "array", "items": {"type": "string"}, "default": []},
            },
            "required": ["operation", "sql"],
        }

    async def execute(
        self,
        operation: str,
        sql: str,
        params: list[Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        conn = sqlite3.connect(self._url)
        conn.row_factory = sqlite3.Row
        try:
            cur = conn.cursor()
            cur.execute(sql, params or [])
            if operation == "query":
                rows = cur.fetchall()
                return [dict(row) for row in rows]
            else:
                conn.commit()
                return {"rowcount": cur.rowcount}
        finally:
            conn.close()
