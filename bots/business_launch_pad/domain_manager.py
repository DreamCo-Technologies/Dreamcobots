# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""
Domain Manager — manage, sell, and flip domains for DreamCo apps and websites.

Extends the existing WebsiteSetup domain-availability checker with a full
domain portfolio lifecycle:

    register  → acquire a domain (recorded in the portfolio)
    list      → view owned domains with valuation and status
    sell      → list a domain on the marketplace at an ask price
    flip      → record a buy→sell flip and compute profit
    portfolio → aggregate portfolio summary

Domain status lifecycle
-----------------------
    available  →  owned     (register)
    owned      →  listed    (sell / mark for sale)
    listed     →  sold      (close a sale)
    owned      →  flipped   (direct flip without listing)
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class PortfolioDomainStatus(Enum):
    """Lifecycle state of a domain in the portfolio."""

    OWNED = "owned"
    LISTED = "listed"
    SOLD = "sold"
    FLIPPED = "flipped"


@dataclass
class PortfolioDomain:
    """A single domain asset in the owner's portfolio.

    Attributes
    ----------
    domain_id : str
        Unique internal identifier (``dom_<uuid4_short>``).
    name : str
        Fully-qualified domain name (e.g. ``dreamco.io``).
    registrar : str
        Where the domain is registered (e.g. ``GoDaddy``, ``Namecheap``).
    registration_cost_usd : float
        Original acquisition cost.
    ask_price_usd : float | None
        Asking price when listed for sale (``None`` while not listed).
    status : PortfolioDomainStatus
    registered_at : float
        Unix timestamp of registration.
    expiry_date : str | None
        ISO date string of domain expiry (``YYYY-MM-DD``).
    estimated_value_usd : float
        AI-estimated market value (set via :meth:`valuate`).
    user_id : str
        Owning user.
    sold_price_usd : float | None
        Actual sale price (set when status becomes ``SOLD`` or ``FLIPPED``).
    profit_usd : float | None
        Net profit after costs (``sold_price_usd - registration_cost_usd``).
    notes : str
        Optional notes.
    """

    domain_id: str
    name: str
    registrar: str
    registration_cost_usd: float
    user_id: str
    status: PortfolioDomainStatus = PortfolioDomainStatus.OWNED
    ask_price_usd: Optional[float] = None
    registered_at: float = field(default_factory=time.time)
    expiry_date: Optional[str] = None
    estimated_value_usd: float = 0.0
    sold_price_usd: Optional[float] = None
    profit_usd: Optional[float] = None
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "domain_id": self.domain_id,
            "name": self.name,
            "registrar": self.registrar,
            "registration_cost_usd": self.registration_cost_usd,
            "ask_price_usd": self.ask_price_usd,
            "status": self.status.value,
            "registered_at": self.registered_at,
            "expiry_date": self.expiry_date,
            "estimated_value_usd": self.estimated_value_usd,
            "sold_price_usd": self.sold_price_usd,
            "profit_usd": self.profit_usd,
            "user_id": self.user_id,
            "notes": self.notes,
        }


# ---------------------------------------------------------------------------
# Valuation heuristic
# ---------------------------------------------------------------------------

# Premium TLDs attract a multiplier on the estimated value
_TLD_MULTIPLIERS: Dict[str, float] = {
    ".com": 1.8,
    ".io": 1.4,
    ".ai": 2.0,
    ".co": 1.2,
    ".app": 1.1,
    ".net": 0.9,
    ".org": 0.8,
}

# Short names are worth more
def _length_factor(name: str) -> float:
    label = name.split(".")[0]
    n = len(label)
    if n <= 3:
        return 4.0
    if n <= 5:
        return 2.5
    if n <= 8:
        return 1.5
    if n <= 12:
        return 1.0
    return 0.7


def _estimate_value(name: str, registration_cost: float) -> float:
    """Return a simple heuristic valuation for *name*."""
    tld = "." + name.rsplit(".", 1)[-1] if "." in name else ".com"
    tld_mult = _TLD_MULTIPLIERS.get(tld, 0.75)
    base = max(registration_cost * 3.0, 15.0)
    return round(base * tld_mult * _length_factor(name), 2)


# ---------------------------------------------------------------------------
# DomainManager
# ---------------------------------------------------------------------------


class DomainManagerError(Exception):
    """Raised when a domain operation cannot be completed."""


class DomainManager:
    """Manage, sell, and flip domains for DreamCo apps and websites.

    All operations are in-memory and keyed by ``user_id``.  Replace the
    internal ``_domains`` dict with a database-backed store in production.

    Usage
    -----
    >>> mgr = DomainManager()
    >>> dom = mgr.register("dreamco.io", user_id="usr_abc", registrar="Namecheap",
    ...                    registration_cost_usd=12.99)
    >>> mgr.mark_for_sale(dom.domain_id, user_id="usr_abc", ask_price_usd=4999.0)
    >>> result = mgr.close_sale(dom.domain_id, user_id="usr_abc", sold_price_usd=4200.0)
    >>> result.profit_usd
    4187.01
    """

    def __init__(self) -> None:
        # domain_id → PortfolioDomain
        self._domains: Dict[str, PortfolioDomain] = {}

    # ------------------------------------------------------------------
    # Acquire
    # ------------------------------------------------------------------

    def register(
        self,
        name: str,
        user_id: str,
        registrar: str = "Namecheap",
        registration_cost_usd: float = 12.99,
        expiry_date: Optional[str] = None,
        notes: str = "",
    ) -> PortfolioDomain:
        """Record a newly registered domain in the portfolio.

        Parameters
        ----------
        name:
            Fully-qualified domain name (e.g. ``example.com``).
        user_id:
            Owning user identifier.
        registrar:
            Registrar name string.
        registration_cost_usd:
            Cost paid to register the domain.
        expiry_date:
            Optional ISO date string (``YYYY-MM-DD``) of when the domain expires.
        notes:
            Optional free-text notes.

        Returns
        -------
        PortfolioDomain
            The newly created domain record.

        Raises
        ------
        DomainManagerError
            If the domain name is blank or already registered by this user.
        """
        name = name.strip().lower()
        if not name:
            raise DomainManagerError("Domain name must not be empty")
        if registration_cost_usd < 0:
            raise DomainManagerError("Registration cost must be non-negative")

        # Prevent duplicate active registrations for the same user+name
        for dom in self._domains.values():
            if (
                dom.user_id == user_id
                and dom.name == name
                and dom.status not in (PortfolioDomainStatus.SOLD, PortfolioDomainStatus.FLIPPED)
            ):
                raise DomainManagerError(
                    f"Domain '{name}' is already in the portfolio for user '{user_id}'"
                )

        domain_id = f"dom_{uuid.uuid4().hex[:8]}"
        estimated = _estimate_value(name, registration_cost_usd)
        domain = PortfolioDomain(
            domain_id=domain_id,
            name=name,
            registrar=registrar,
            registration_cost_usd=registration_cost_usd,
            user_id=user_id,
            expiry_date=expiry_date,
            estimated_value_usd=estimated,
            notes=notes,
        )
        self._domains[domain_id] = domain
        return domain

    # ------------------------------------------------------------------
    # List / filter
    # ------------------------------------------------------------------

    def list_portfolio(
        self,
        user_id: str,
        *,
        status: Optional[str] = None,
    ) -> List[PortfolioDomain]:
        """Return all domain records owned by *user_id*.

        Parameters
        ----------
        user_id:
            Owner to filter by.
        status:
            Optional status string to filter (``owned``, ``listed``,
            ``sold``, ``flipped``).

        Returns
        -------
        list[PortfolioDomain]
            Sorted by registration date, newest first.
        """
        results = [d for d in self._domains.values() if d.user_id == user_id]
        if status:
            try:
                status_enum = PortfolioDomainStatus(status.lower())
            except ValueError:
                raise DomainManagerError(
                    f"Invalid status '{status}'. "
                    f"Valid values: {[s.value for s in PortfolioDomainStatus]}"
                )
            results = [d for d in results if d.status == status_enum]
        results.sort(key=lambda d: d.registered_at, reverse=True)
        return results

    def get_domain(self, domain_id: str, user_id: str) -> PortfolioDomain:
        """Retrieve a single domain record by ID.

        Raises
        ------
        KeyError
            If not found or not owned by *user_id*.
        """
        dom = self._domains.get(domain_id)
        if dom is None or dom.user_id != user_id:
            raise KeyError(f"Domain '{domain_id}' not found for user '{user_id}'")
        return dom

    # ------------------------------------------------------------------
    # Valuation
    # ------------------------------------------------------------------

    def valuate(self, domain_id: str, user_id: str) -> PortfolioDomain:
        """Refresh the estimated market value for a domain.

        Returns
        -------
        PortfolioDomain
            The updated record.
        """
        dom = self.get_domain(domain_id, user_id)
        dom.estimated_value_usd = _estimate_value(dom.name, dom.registration_cost_usd)
        return dom

    # ------------------------------------------------------------------
    # Sell workflow
    # ------------------------------------------------------------------

    def mark_for_sale(
        self,
        domain_id: str,
        user_id: str,
        ask_price_usd: float,
    ) -> PortfolioDomain:
        """List a domain on the marketplace with an asking price.

        Parameters
        ----------
        domain_id:
            Target domain.
        user_id:
            Must be the owner.
        ask_price_usd:
            Desired sale price (must be > 0).

        Returns
        -------
        PortfolioDomain
            Updated record with status ``LISTED``.

        Raises
        ------
        DomainManagerError
            If the domain is not in ``OWNED`` status or price is invalid.
        """
        dom = self.get_domain(domain_id, user_id)
        if dom.status != PortfolioDomainStatus.OWNED:
            raise DomainManagerError(
                f"Domain '{dom.name}' must be OWNED to list for sale "
                f"(current status: {dom.status.value})"
            )
        if ask_price_usd <= 0:
            raise DomainManagerError("Ask price must be greater than zero")
        dom.status = PortfolioDomainStatus.LISTED
        dom.ask_price_usd = ask_price_usd
        return dom

    def close_sale(
        self,
        domain_id: str,
        user_id: str,
        sold_price_usd: float,
    ) -> PortfolioDomain:
        """Record the completion of a domain sale.

        Parameters
        ----------
        domain_id:
            Target domain (must be in ``LISTED`` status).
        user_id:
            Must be the owner.
        sold_price_usd:
            Actual amount received from the buyer.

        Returns
        -------
        PortfolioDomain
            Updated record with status ``SOLD`` and ``profit_usd`` set.
        """
        dom = self.get_domain(domain_id, user_id)
        if dom.status != PortfolioDomainStatus.LISTED:
            raise DomainManagerError(
                f"Domain '{dom.name}' must be LISTED to close a sale "
                f"(current status: {dom.status.value})"
            )
        if sold_price_usd <= 0:
            raise DomainManagerError("Sold price must be greater than zero")
        dom.status = PortfolioDomainStatus.SOLD
        dom.sold_price_usd = sold_price_usd
        dom.profit_usd = round(sold_price_usd - dom.registration_cost_usd, 2)
        return dom

    # ------------------------------------------------------------------
    # Flip workflow (buy + sell in one step)
    # ------------------------------------------------------------------

    def flip_domain(
        self,
        name: str,
        user_id: str,
        buy_price_usd: float,
        sell_price_usd: float,
        registrar: str = "Namecheap",
        notes: str = "",
    ) -> PortfolioDomain:
        """Record a complete domain flip (buy and sell in one transaction).

        This convenience method registers the domain and immediately closes
        the sale, useful for recording already-completed flips.

        Parameters
        ----------
        name:
            Fully-qualified domain name.
        user_id:
            Owning user.
        buy_price_usd:
            Cost to acquire the domain.
        sell_price_usd:
            Amount received from the sale (must be > 0).
        registrar:
            Registrar used.
        notes:
            Optional notes.

        Returns
        -------
        PortfolioDomain
            Record with status ``FLIPPED`` and ``profit_usd`` set.

        Raises
        ------
        DomainManagerError
            If *sell_price_usd* ≤ 0 or *buy_price_usd* < 0.
        """
        if sell_price_usd <= 0:
            raise DomainManagerError("Sell price must be greater than zero")

        dom = self.register(
            name=name,
            user_id=user_id,
            registrar=registrar,
            registration_cost_usd=buy_price_usd,
            notes=notes,
        )
        dom.status = PortfolioDomainStatus.FLIPPED
        dom.sold_price_usd = sell_price_usd
        dom.profit_usd = round(sell_price_usd - buy_price_usd, 2)
        return dom

    # ------------------------------------------------------------------
    # Portfolio summary
    # ------------------------------------------------------------------

    def portfolio_summary(self, user_id: str) -> dict:
        """Return aggregate portfolio statistics for *user_id*.

        Returns
        -------
        dict
            Keys: ``total_domains``, ``owned``, ``listed``, ``sold``,
            ``flipped``, ``total_invested_usd``, ``total_revenue_usd``,
            ``total_profit_usd``, ``portfolio_estimated_value_usd``.
        """
        domains = [d for d in self._domains.values() if d.user_id == user_id]
        counts: Dict[str, int] = {s.value: 0 for s in PortfolioDomainStatus}
        total_invested = 0.0
        total_revenue = 0.0
        portfolio_value = 0.0

        for dom in domains:
            counts[dom.status.value] += 1
            total_invested += dom.registration_cost_usd
            if dom.sold_price_usd is not None:
                total_revenue += dom.sold_price_usd
            if dom.status in (PortfolioDomainStatus.OWNED, PortfolioDomainStatus.LISTED):
                portfolio_value += dom.estimated_value_usd

        return {
            "user_id": user_id,
            "total_domains": len(domains),
            "owned": counts["owned"],
            "listed": counts["listed"],
            "sold": counts["sold"],
            "flipped": counts["flipped"],
            "total_invested_usd": round(total_invested, 2),
            "total_revenue_usd": round(total_revenue, 2),
            "total_profit_usd": round(total_revenue - total_invested, 2),
            "portfolio_estimated_value_usd": round(portfolio_value, 2),
        }
