"""
SQL Bot — DreamCo AI-Powered Database Interaction Bot

Provides a safe, validated SQL execution engine for dynamic database
operations in the DreamCo pipeline.  The bot can run SELECT queries,
INSERT/UPDATE data, generate analytical reports, and inspect schema
structure — all with built-in safety guardrails that block destructive
or unsafe SQL operations.

Key features
------------
  • Query execution     — run parametrised SQL against an SQLite backend
  • Safety guardrails   — block DROP TABLE, DELETE without WHERE, TRUNCATE, etc.
  • Query validation    — parse and lint SQL before execution
  • Analytical reports  — built-in report generators (row counts, top-N, summary)
  • Schema inspection   — list tables, columns, and row counts
  • Integrity checks    — verify primary-key constraints and detect nulls

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.

Usage
-----
    from bots.sql_bot import SQLBot

    bot = SQLBot()                          # in-memory SQLite (default)
    bot.create_table("users", [("id", "INTEGER PRIMARY KEY"), ("name", "TEXT")])
    bot.insert("users", {"id": 1, "name": "Alice"})
    result = bot.query("SELECT * FROM users")
    print(result.rows)
"""

from __future__ import annotations

import re
import sqlite3
import sys
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class SQLBotError(Exception):
    """Base exception for SQL Bot errors."""


class SafetyViolation(SQLBotError):
    """Raised when a query is blocked by the safety guardrails."""


class QueryError(SQLBotError):
    """Raised when a SQL query fails to execute."""


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class QueryResult:
    """Encapsulates the result of a SQL query execution.

    Attributes
    ----------
    sql : str
        The SQL statement that was executed.
    rows : list[dict]
        Rows returned as a list of dicts (column name → value).
    rowcount : int
        Number of rows affected (for INSERT/UPDATE/DELETE).
    columns : list[str]
        Column names returned by the query.
    duration_ms : float
        Wall-clock time taken to execute the query in milliseconds.
    executed_at : str
        ISO-8601 UTC timestamp of execution.
    """

    sql: str
    rows: list[dict] = field(default_factory=list)
    rowcount: int = 0
    columns: list[str] = field(default_factory=list)
    duration_ms: float = 0.0
    executed_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "sql": self.sql,
            "rows": self.rows,
            "rowcount": self.rowcount,
            "columns": self.columns,
            "duration_ms": self.duration_ms,
            "executed_at": self.executed_at,
        }


# ---------------------------------------------------------------------------
# Identifier validation
# ---------------------------------------------------------------------------

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _validate_identifier(name: str, label: str = "identifier") -> None:
    """Raise :class:`SQLBotError` if *name* is not a safe SQL identifier.

    Only alphanumeric characters and underscores are allowed, and the name
    must start with a letter or underscore.  This prevents SQL injection
    through table/column name interpolation.
    """
    if not _IDENTIFIER_RE.match(name):
        raise SQLBotError(
            f"Unsafe {label} '{name}': only letters, digits, and underscores are "
            "allowed and the name must start with a letter or underscore."
        )


# Allowlist for ORDER BY direction keywords.
_ORDER_BY_RE = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_]*(\s+(ASC|DESC))?(\s*,\s*[A-Za-z_][A-Za-z0-9_]*(\s+(ASC|DESC))?)*$",
    re.IGNORECASE,
)


def _validate_order_by(order_by: str) -> None:
    """Raise :class:`SQLBotError` if *order_by* contains unsafe SQL."""
    if not _ORDER_BY_RE.match(order_by.strip()):
        raise SQLBotError(
            f"Unsafe ORDER BY expression '{order_by}': only column identifiers "
            "and ASC/DESC keywords are allowed."
        )


def _validate_non_negative_int(value: Any, label: str = "value") -> None:
    """Raise :class:`SQLBotError` if *value* is not a non-negative integer."""
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise SQLBotError(
            f"Unsafe {label} '{value}': must be a non-negative integer."
        )


# ---------------------------------------------------------------------------
# Safety guardrails
# ---------------------------------------------------------------------------

# Patterns that are always blocked regardless of context.
_BLOCKED_PATTERNS: list[re.Pattern] = [
    re.compile(r"\bDROP\s+(TABLE|DATABASE|INDEX|VIEW|SCHEMA)\b", re.IGNORECASE),
    re.compile(r"\bTRUNCATE\b", re.IGNORECASE),
    re.compile(r"\bALTER\s+TABLE\b", re.IGNORECASE),
    re.compile(r"\bCREATE\s+(DATABASE|SCHEMA)\b", re.IGNORECASE),
    re.compile(r"\bATTACH\b", re.IGNORECASE),
    re.compile(r"\bDETACH\b", re.IGNORECASE),
    # Allow only read-only PRAGMAs (table_info, foreign_keys); block any
    # PRAGMA that includes an assignment (= ...) to prevent runtime config changes.
    re.compile(r"\bPRAGMA\s+(?!table_info|foreign_keys)\w+\s*=", re.IGNORECASE),
]

# DELETE without a WHERE clause is flagged as unsafe.
_DELETE_WITHOUT_WHERE = re.compile(
    r"\bDELETE\s+FROM\s+\w+\s*(?:;|$)", re.IGNORECASE
)


def validate_query(sql: str) -> None:
    """Validate a SQL string against the DreamCo safety policy.

    Raises
    ------
    SafetyViolation
        If the query contains any blocked pattern.
    """
    cleaned = sql.strip()
    for pattern in _BLOCKED_PATTERNS:
        if pattern.search(cleaned):
            raise SafetyViolation(
                f"Query blocked by safety guardrails: matches pattern "
                f"'{pattern.pattern}'. Destructive DDL statements are not allowed."
            )
    if _DELETE_WITHOUT_WHERE.search(cleaned):
        raise SafetyViolation(
            "DELETE without a WHERE clause is blocked. "
            "Add a WHERE condition to limit the affected rows."
        )


# ---------------------------------------------------------------------------
# SQL Bot
# ---------------------------------------------------------------------------

class SQLBot:
    """AI-powered SQL bot for safe, validated database operations.

    Parameters
    ----------
    db_path : str
        Path to the SQLite database file.  Use ``":memory:"`` (default) for
        a non-persistent in-memory store ideal for testing.
    enforce_safety : bool
        When *True* (default), all queries pass through :func:`validate_query`
        before execution.  Set to *False* only in sandboxed environments.
    """

    def __init__(
        self,
        db_path: str = ":memory:",
        enforce_safety: bool = True,
    ) -> None:
        self.db_path = db_path
        self.enforce_safety = enforce_safety
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._query_log: list[QueryResult] = []

    # ------------------------------------------------------------------
    # Core execution
    # ------------------------------------------------------------------

    def query(
        self,
        sql: str,
        params: Optional[tuple | list] = None,
    ) -> QueryResult:
        """Execute a SQL statement and return a :class:`QueryResult`.

        Parameters
        ----------
        sql : str
            The SQL statement to execute.
        params : tuple or list, optional
            Positional parameters for parameterised queries.

        Returns
        -------
        QueryResult

        Raises
        ------
        SafetyViolation
            If the query is blocked by safety guardrails.
        QueryError
            If the SQL statement fails to execute.
        """
        if self.enforce_safety:
            validate_query(sql)

        params = params or ()
        start = time.monotonic()
        try:
            cursor = self._conn.execute(sql, params)
            self._conn.commit()
            elapsed_ms = (time.monotonic() - start) * 1000

            columns = [desc[0] for desc in (cursor.description or [])]
            raw_rows = cursor.fetchall() if columns else []
            rows = [dict(zip(columns, row)) for row in raw_rows]

            result = QueryResult(
                sql=sql,
                rows=rows,
                rowcount=cursor.rowcount if cursor.rowcount >= 0 else len(rows),
                columns=columns,
                duration_ms=round(elapsed_ms, 3),
            )
        except sqlite3.Error as exc:
            raise QueryError(f"Query failed: {exc}\nSQL: {sql}") from exc

        self._query_log.append(result)
        return result

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def create_table(
        self,
        table_name: str,
        columns: list[tuple[str, str]],
        if_not_exists: bool = True,
    ) -> QueryResult:
        """Create a table with the given column definitions.

        Parameters
        ----------
        table_name : str
            Name of the table to create.
        columns : list of (name, type_def) tuples
            Column definitions, e.g. ``[("id", "INTEGER PRIMARY KEY"), ("name", "TEXT")]``.
        if_not_exists : bool
            Append ``IF NOT EXISTS`` to avoid an error if the table already exists.

        Returns
        -------
        QueryResult
        """
        _validate_identifier(table_name, "table name")
        for col_name, _ in columns:
            _validate_identifier(col_name, "column name")
        col_defs = ", ".join(f"{name} {typedef}" for name, typedef in columns)
        qualifier = "IF NOT EXISTS " if if_not_exists else ""
        sql = f"CREATE TABLE {qualifier}{table_name} ({col_defs})"
        return self.query(sql)

    def insert(self, table_name: str, data: dict) -> QueryResult:
        """Insert a single row into *table_name*.

        Parameters
        ----------
        table_name : str
        data : dict
            Column → value mapping.

        Returns
        -------
        QueryResult
        """
        _validate_identifier(table_name, "table name")
        for col_name in data.keys():
            _validate_identifier(col_name, "column name")
        cols = ", ".join(data.keys())
        placeholders = ", ".join("?" for _ in data)
        sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
        return self.query(sql, tuple(data.values()))

    def insert_many(self, table_name: str, rows: list[dict]) -> list[QueryResult]:
        """Insert multiple rows into *table_name*.

        Parameters
        ----------
        table_name : str
        rows : list of dict

        Returns
        -------
        list of QueryResult
        """
        return [self.insert(table_name, row) for row in rows]

    def update(
        self,
        table_name: str,
        data: dict,
        where: str,
        where_params: Optional[tuple | list] = None,
    ) -> QueryResult:
        """Update rows in *table_name* matching *where*.

        Parameters
        ----------
        table_name : str
        data : dict
            Column → value pairs to SET.
        where : str
            SQL WHERE clause (without the ``WHERE`` keyword).
        where_params : tuple or list, optional
            Positional parameters for the WHERE clause.

        Returns
        -------
        QueryResult
        """
        _validate_identifier(table_name, "table name")
        for col_name in data.keys():
            _validate_identifier(col_name, "column name")
        set_clause = ", ".join(f"{col} = ?" for col in data.keys())
        sql = f"UPDATE {table_name} SET {set_clause} WHERE {where}"
        params = tuple(data.values()) + tuple(where_params or ())
        return self.query(sql, params)

    def select(
        self,
        table_name: str,
        columns: str = "*",
        where: Optional[str] = None,
        where_params: Optional[tuple | list] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> QueryResult:
        """Run a SELECT query with optional filtering.

        Parameters
        ----------
        table_name : str
        columns : str
            Comma-separated column list or ``"*"``.  Each column name must
            be a safe SQL identifier (or ``"*"``).
        where : str, optional
            WHERE clause (without the keyword).
        where_params : tuple or list, optional
        order_by : str, optional
            ORDER BY expression.
        limit : int, optional
            LIMIT value.

        Returns
        -------
        QueryResult
        """
        _validate_identifier(table_name, "table name")
        if columns != "*":
            for col in [c.strip() for c in columns.split(",")]:
                _validate_identifier(col, "column name")
        if order_by is not None:
            _validate_order_by(order_by)
        if limit is not None:
            _validate_non_negative_int(limit, "limit")
        sql = f"SELECT {columns} FROM {table_name}"
        params: list[Any] = list(where_params or [])
        if where:
            sql += f" WHERE {where}"
        if order_by:
            sql += f" ORDER BY {order_by}"
        if limit is not None:
            sql += f" LIMIT {limit}"
        return self.query(sql, params)

    def delete(
        self,
        table_name: str,
        where: str,
        where_params: Optional[tuple | list] = None,
    ) -> QueryResult:
        """Delete rows from *table_name* matching *where*.

        A WHERE clause is required; DELETE without WHERE is always blocked
        by the safety guardrails.

        Parameters
        ----------
        table_name : str
        where : str
            WHERE clause (without the keyword).
        where_params : tuple or list, optional

        Returns
        -------
        QueryResult
        """
        _validate_identifier(table_name, "table name")
        sql = f"DELETE FROM {table_name} WHERE {where}"
        return self.query(sql, where_params)

    # ------------------------------------------------------------------
    # Schema inspection
    # ------------------------------------------------------------------

    def list_tables(self) -> list[str]:
        """Return a list of all user-created table names in the database."""
        result = self.query(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        return [row["name"] for row in result.rows]

    def get_schema(self, table_name: str) -> list[dict]:
        """Return column metadata for *table_name*.

        Returns
        -------
        list of dict with keys: cid, name, type, notnull, dflt_value, pk
        """
        _validate_identifier(table_name, "table name")
        result = self._conn.execute(f"PRAGMA table_info({table_name})")
        return [dict(row) for row in result.fetchall()]

    def get_row_count(self, table_name: str) -> int:
        """Return the number of rows in *table_name*."""
        _validate_identifier(table_name, "table name")
        result = self.query(f"SELECT COUNT(*) AS cnt FROM {table_name}")
        return result.rows[0]["cnt"] if result.rows else 0

    # ------------------------------------------------------------------
    # Analytical reports
    # ------------------------------------------------------------------

    def generate_summary_report(self) -> dict:
        """Generate a summary report of all tables in the database.

        Returns
        -------
        dict
            Keys: ``tables`` (list of table stats), ``total_tables``,
            ``total_rows``, ``generated_at``.
        """
        tables = self.list_tables()
        table_stats = []
        total_rows = 0
        for table in tables:
            schema = self.get_schema(table)
            count = self.get_row_count(table)
            total_rows += count
            table_stats.append({
                "table": table,
                "row_count": count,
                "column_count": len(schema),
                "columns": [col["name"] for col in schema],
            })
        return {
            "tables": table_stats,
            "total_tables": len(tables),
            "total_rows": total_rows,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def generate_top_n_report(
        self,
        table_name: str,
        value_column: str,
        label_column: str,
        n: int = 10,
        aggregation: str = "SUM",
    ) -> dict:
        """Generate a top-N analytical report from a table.

        Parameters
        ----------
        table_name : str
        value_column : str
            Numeric column to aggregate.
        label_column : str
            Column used as the grouping label.
        n : int
            Number of top results to return.
        aggregation : str
            Aggregation function: ``SUM``, ``COUNT``, ``AVG``, ``MAX``, ``MIN``.

        Returns
        -------
        dict with keys ``title``, ``rows``, ``generated_at``.
        """
        agg = aggregation.upper()
        allowed = {"SUM", "COUNT", "AVG", "MAX", "MIN"}
        if agg not in allowed:
            raise SQLBotError(f"Unsupported aggregation '{agg}'. Use one of: {allowed}")
        _validate_identifier(table_name, "table name")
        _validate_identifier(value_column, "value column")
        _validate_identifier(label_column, "label column")
        _validate_non_negative_int(n, "n (top-N count)")
        sql = (
            f"SELECT {label_column}, {agg}({value_column}) AS metric "
            f"FROM {table_name} "
            f"GROUP BY {label_column} "
            f"ORDER BY metric DESC "
            f"LIMIT {n}"
        )
        result = self.query(sql)
        return {
            "title": f"Top {n} by {agg}({value_column})",
            "rows": result.rows,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Integrity checks
    # ------------------------------------------------------------------

    def check_integrity(self) -> dict:
        """Run SQLite's built-in integrity check.

        Returns
        -------
        dict with keys ``passed`` (bool), ``issues`` (list of str), ``checked_at``.
        """
        result = self._conn.execute("PRAGMA integrity_check").fetchall()
        issues = [row[0] for row in result if row[0] != "ok"]
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }

    def find_null_columns(self, table_name: str) -> dict:
        """Identify columns that contain NULL values in *table_name*.

        Returns
        -------
        dict mapping column name → null row count.
        """
        # get_schema already validates table_name
        schema = self.get_schema(table_name)
        null_report: dict[str, int] = {}
        for col in schema:
            col_name = col["name"]
            # Validate col_name even though it comes from PRAGMA table_info,
            # as a defence-in-depth measure.
            _validate_identifier(col_name, "column name")
            result = self.query(
                f"SELECT COUNT(*) AS cnt FROM {table_name} WHERE {col_name} IS NULL"
            )
            cnt = result.rows[0]["cnt"]
            if cnt > 0:
                null_report[col_name] = cnt
        return null_report

    # ------------------------------------------------------------------
    # Query log
    # ------------------------------------------------------------------

    def get_query_log(self, last_n: int = 50) -> list[dict]:
        """Return the last *last_n* executed queries.

        Returns
        -------
        list of dict (QueryResult.to_dict())
        """
        return [r.to_dict() for r in self._query_log[-last_n:]]

    def get_stats(self) -> dict:
        """Return execution statistics for this session.

        Returns
        -------
        dict with keys ``total_queries``, ``total_duration_ms``, ``avg_duration_ms``.
        """
        total = len(self._query_log)
        total_ms = sum(r.duration_ms for r in self._query_log)
        return {
            "total_queries": total,
            "total_duration_ms": round(total_ms, 3),
            "avg_duration_ms": round(total_ms / total, 3) if total else 0.0,
        }

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Close the database connection."""
        self._conn.close()
