"""
Open Claw Bot — Client Manager

Manages client profiles and their customised strategy configurations.
Each client can have individual risk preferences, goals, and strategy rules
that are injected into the strategy engine at generation time.

GLOBAL AI SOURCES FLOW: participates via open_claw_bot.py pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401


class ClientStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PROSPECT = "prospect"
    SUSPENDED = "suspended"


class GoalType(Enum):
    PROFIT_MAXIMISATION = "profit_maximisation"
    RISK_REDUCTION = "risk_reduction"
    DIVERSIFICATION = "diversification"
    INCOME_GENERATION = "income_generation"
    GROWTH = "growth"
    PRESERVATION = "preservation"


@dataclass
class ClientPreferences:
    """Risk and goal preferences for a client."""

    max_risk_pct: float = 5.0
    preferred_strategy_types: list = field(default_factory=list)
    goals: list = field(default_factory=list)
    custom_rules: list = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "max_risk_pct": self.max_risk_pct,
            "preferred_strategy_types": self.preferred_strategy_types,
            "goals": [g if isinstance(g, str) else g.value for g in self.goals],
            "custom_rules": self.custom_rules,
            "notes": self.notes,
        }


@dataclass
class ClientProfile:
    """A client registered with the Open Claw Bot."""

    client_id: str
    name: str
    email: str
    status: ClientStatus = ClientStatus.ACTIVE
    preferences: ClientPreferences = field(default_factory=ClientPreferences)
    strategy_ids: list = field(default_factory=list)
    total_roi_pct: float = 0.0
    metadata: dict = field(default_factory=dict)

    def is_active(self) -> bool:
        return self.status == ClientStatus.ACTIVE

    def to_dict(self) -> dict:
        return {
            "client_id": self.client_id,
            "name": self.name,
            "email": self.email,
            "status": self.status.value,
            "preferences": self.preferences.to_dict(),
            "strategy_count": len(self.strategy_ids),
            "total_roi_pct": self.total_roi_pct,
        }


class ClientManager:
    """
    Manage client profiles and their strategy assignments.

    Supports client-specific customisation options to optimise results
    for various scenarios (per the problem statement).
    """

    def __init__(self, max_clients: Optional[int] = None) -> None:
        self._clients: dict[str, ClientProfile] = {}
        self._counter: int = 0
        self._max_clients = max_clients

    # ------------------------------------------------------------------
    # Client CRUD
    # ------------------------------------------------------------------

    def add_client(
        self,
        name: str,
        email: str,
        preferences: Optional[ClientPreferences] = None,
        metadata: Optional[dict] = None,
    ) -> ClientProfile:
        """Register a new client."""
        if self._max_clients is not None and len(self._clients) >= self._max_clients:
            raise RuntimeError(
                f"Client limit of {self._max_clients} reached. Upgrade your tier."
            )
        self._counter += 1
        client_id = f"client_{self._counter:04d}"
        client = ClientProfile(
            client_id=client_id,
            name=name,
            email=email,
            preferences=preferences or ClientPreferences(),
            metadata=dict(metadata or {}),
        )
        self._clients[client_id] = client
        return client

    def remove_client(self, client_id: str) -> None:
        self._clients.pop(client_id, None)

    def update_preferences(
        self, client_id: str, preferences: ClientPreferences
    ) -> ClientProfile:
        """Update a client's strategy preferences."""
        client = self._get(client_id)
        client.preferences = preferences
        return client

    def set_status(self, client_id: str, status: ClientStatus) -> ClientProfile:
        client = self._get(client_id)
        client.status = status
        return client

    # ------------------------------------------------------------------
    # Strategy assignment
    # ------------------------------------------------------------------

    def assign_strategy(self, client_id: str, strategy_id: str) -> ClientProfile:
        """Associate a strategy with a client."""
        client = self._get(client_id)
        if strategy_id not in client.strategy_ids:
            client.strategy_ids.append(strategy_id)
        return client

    def remove_strategy(self, client_id: str, strategy_id: str) -> ClientProfile:
        """Remove a strategy assignment from a client."""
        client = self._get(client_id)
        if strategy_id in client.strategy_ids:
            client.strategy_ids.remove(strategy_id)
        return client

    def record_roi(self, client_id: str, roi_pct: float) -> ClientProfile:
        """Accumulate realised ROI for a client."""
        client = self._get(client_id)
        client.total_roi_pct = round(client.total_roi_pct + roi_pct, 4)
        return client

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_client(self, client_id: str) -> ClientProfile:
        return self._get(client_id)

    def list_clients(
        self, status: Optional[ClientStatus] = None
    ) -> list[ClientProfile]:
        clients = list(self._clients.values())
        if status is not None:
            clients = [c for c in clients if c.status == status]
        return clients

    def find_clients_by_name(self, name: str) -> list[ClientProfile]:
        name_lower = name.lower()
        return [c for c in self._clients.values() if name_lower in c.name.lower()]

    def get_top_clients(self, n: int = 5) -> list[ClientProfile]:
        """Return the top-N clients by accumulated ROI."""
        return sorted(
            self._clients.values(),
            key=lambda c: c.total_roi_pct,
            reverse=True,
        )[:n]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get(self, client_id: str) -> ClientProfile:
        if client_id not in self._clients:
            raise KeyError(f"Client '{client_id}' not found.")
        return self._clients[client_id]
