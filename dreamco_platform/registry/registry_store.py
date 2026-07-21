"""PostgreSQL-backed bot registry store for DreamCo Empire OS."""

from __future__ import annotations

import asyncio
import json
import os
from typing import Iterable, Optional

try:
    import asyncpg
except ImportError:  # pragma: no cover - optional dependency for runtime
    asyncpg = None

from dreamco_platform.registry.bot_registry import BotRegistryEntry, HealthStatus


class PostgresBotRegistryStore:
    """Persist ``BotRegistryEntry`` rows in PostgreSQL using ``asyncpg``."""

    def __init__(
        self,
        dsn: str | None = None,
        *,
        min_size: int = 1,
        max_size: int = 10,
        pool: "asyncpg.Pool | None" = None,
    ) -> None:
        self._dsn = dsn or os.getenv("DATABASE_URL", "")
        self._min_size = min_size
        self._max_size = max_size
        self._pool = pool
        self._pool_lock = asyncio.Lock()

    async def connect(self) -> "asyncpg.Pool":
        """Create the connection pool lazily and ensure the schema exists."""
        if self._pool is not None:
            return self._pool
        if asyncpg is None:
            raise RuntimeError("asyncpg is required for PostgresBotRegistryStore")
        if not self._dsn:
            raise RuntimeError("DATABASE_URL is not configured")
        async with self._pool_lock:
            if self._pool is None:
                self._pool = await asyncpg.create_pool(
                    dsn=self._dsn,
                    min_size=self._min_size,
                    max_size=self._max_size,
                    command_timeout=30,
                )
                await self._ensure_schema()
        return self._pool

    async def close(self) -> None:
        """Close the asyncpg pool if it was created."""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    async def _ensure_schema(self) -> None:
        pool = await self.connect()
        ddl = """
        CREATE TABLE IF NOT EXISTS bot_registry_entries (
            bot_id TEXT PRIMARY KEY,
            payload JSONB NOT NULL,
            health TEXT NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_bot_registry_health
            ON bot_registry_entries (health);
        """
        async with pool.acquire() as conn:
            await conn.execute(ddl)

    async def save_entry(self, entry: BotRegistryEntry) -> BotRegistryEntry:
        """Insert or update a registry row using PostgreSQL upsert semantics."""
        pool = await self.connect()
        query = """
        INSERT INTO bot_registry_entries (bot_id, payload, health, updated_at)
        VALUES ($1, $2::jsonb, $3, NOW())
        ON CONFLICT (bot_id)
        DO UPDATE SET
            payload = EXCLUDED.payload,
            health = EXCLUDED.health,
            updated_at = NOW()
        """
        async with pool.acquire() as conn:
            await conn.execute(query, entry.bot_id, json.dumps(entry.to_dict()), entry.health.value)
        return entry

    async def get_entry(self, bot_id: str) -> Optional[BotRegistryEntry]:
        """Fetch one registry entry by bot id."""
        pool = await self.connect()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT payload FROM bot_registry_entries WHERE bot_id = $1",
                bot_id,
            )
        if row is None:
            return None
        payload = row["payload"] if isinstance(row["payload"], dict) else json.loads(row["payload"])
        return BotRegistryEntry.from_dict(payload)

    async def list_all(self) -> list[BotRegistryEntry]:
        """Return every saved registry entry ordered by bot id."""
        pool = await self.connect()
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT payload FROM bot_registry_entries ORDER BY bot_id ASC")
        entries: list[BotRegistryEntry] = []
        for row in rows:
            payload = row["payload"] if isinstance(row["payload"], dict) else json.loads(row["payload"])
            entries.append(BotRegistryEntry.from_dict(payload))
        return entries

    async def delete_entry(self, bot_id: str) -> bool:
        """Delete one bot registry record."""
        pool = await self.connect()
        async with pool.acquire() as conn:
            result = await conn.execute("DELETE FROM bot_registry_entries WHERE bot_id = $1", bot_id)
        return result.endswith("1")

    async def update_health(self, bot_id: str, status: HealthStatus | str) -> BotRegistryEntry:
        """Update the stored health field without mutating the rest of the payload."""
        entry = await self.get_entry(bot_id)
        if entry is None:
            raise KeyError(f"Unknown bot_id: {bot_id}")
        resolved = status if isinstance(status, HealthStatus) else HealthStatus(status)
        payload = entry.to_dict()
        payload["health"] = resolved.value
        pool = await self.connect()
        query = """
        UPDATE bot_registry_entries
        SET health = $2, payload = $3::jsonb, updated_at = NOW()
        WHERE bot_id = $1
        """
        async with pool.acquire() as conn:
            await conn.execute(query, bot_id, resolved.value, json.dumps(payload))
        return BotRegistryEntry.from_dict(payload)

    async def save_many(self, entries: Iterable[BotRegistryEntry]) -> list[BotRegistryEntry]:
        """Convenience helper for bulk saves using the same upsert primitive."""
        saved: list[BotRegistryEntry] = []
        for entry in entries:
            saved.append(await self.save_entry(entry))
        return saved

    async def __aenter__(self) -> "PostgresBotRegistryStore":
        await self.connect()
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        await self.close()
