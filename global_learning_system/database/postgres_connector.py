"""
postgres_connector.py — PostgreSQL database connection handler.

Manages connection lifecycle, query execution, and connection pooling
for PostgreSQL databases used by the DreamCo Global Learning System.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus


@dataclass
class ConnectionConfig:
    """PostgreSQL connection parameters."""

    host: str = "localhost"
    port: int = 5432
    database: str = "dreamco"
    user: str = "dreamco_user"
    password: str = ""
    pool_size: int = 5
    max_overflow: int = 10
    connect_timeout: int = 30

    @property
    def dsn(self) -> str:
        """Return a PostgreSQL DSN string."""
        pw = quote_plus(self.password)
        return (
            f"postgresql://{self.user}:{pw}@{self.host}:{self.port}/{self.database}"
            f"?connect_timeout={self.connect_timeout}"
        )


class PostgresConnector:
    """
    Manages a PostgreSQL connection (mock implementation).

    Replace the stubbed ``_execute`` method with a real driver call
    (e.g. *psycopg2*, *asyncpg*, or *SQLAlchemy engine*) in production.

    Parameters
    ----------
    config : ConnectionConfig
        Database connection parameters.
    """

    def __init__(self, config: Optional[ConnectionConfig] = None):
        self.config = config or ConnectionConfig()
        self._connected: bool = False
        self._query_log: List[str] = []

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def connect(self) -> None:
        """Open the database connection (stub)."""
        self._connected = True

    def disconnect(self) -> None:
        """Close the database connection (stub)."""
        self._connected = False

    @property
    def is_connected(self) -> bool:
        """Return ``True`` if the connection is open."""
        return self._connected

    def execute(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a SQL statement and return a list of row dicts.

        Parameters
        ----------
        sql : str
            Parameterised SQL statement.
        params : dict | None
            Query parameters.

        Returns
        -------
        list[dict]
            Result rows (empty for non-SELECT statements).

        Raises
        ------
        RuntimeError
            If called while disconnected.
        """
        if not self._connected:
            raise RuntimeError("Not connected. Call connect() first.")
        self._query_log.append(sql)
        return self._execute(sql, params or {})

    def get_query_log(self) -> List[str]:
        """Return the list of SQL statements executed in this session."""
        return list(self._query_log)

    def clear_query_log(self) -> None:
        """Clear the query log."""
        self._query_log = []

    def health_check(self) -> Dict[str, Any]:
        """Return connection health information."""
        return {
            "connected": self._connected,
            "host": self.config.host,
            "port": self.config.port,
            "database": self.config.database,
        }

    # ------------------------------------------------------------------
    # Internal helpers (override for production driver)
    # ------------------------------------------------------------------

    def _execute(self, sql: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Stub executor — override with a real database driver call."""
        return []
