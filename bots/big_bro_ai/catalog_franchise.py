"""
Big Bro AI — Catalog & Franchise Engine

Manages the product/service catalog and franchise network.  Customers
browse the catalog and order through a franchisee or directly through
the platform.  Each franchise pays recurring territory fees and earns
commissions on catalog orders.

GLOBAL AI SOURCES FLOW: participates via big_bro_ai.py pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Catalog item categories
# ---------------------------------------------------------------------------

class CatalogCategory(Enum):
    BOTS = "bots"
    AUTOMATION_SERVICES = "automation_services"
    AI_TOOLS = "ai_tools"
    DIGITAL_PRODUCTS = "digital_products"
    COURSES = "courses"
    TEMPLATES = "templates"
    CONSULTING = "consulting"
    SAAS = "saas"
    FRANCHISE_KIT = "franchise_kit"
    MERCHANDISE = "merchandise"


# ---------------------------------------------------------------------------
# Franchise status
# ---------------------------------------------------------------------------

class FranchiseStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


# ---------------------------------------------------------------------------
# Catalog item
# ---------------------------------------------------------------------------

@dataclass
class CatalogItem:
    """
    A product or service listed in the DreamCo catalog.

    Attributes
    ----------
    item_id : str
        Unique identifier.
    name : str
        Display name.
    category : CatalogCategory
        Product/service type.
    description : str
        What the item provides.
    price_usd : float
        Retail price.
    commission_pct : float
        Franchisee commission percentage (0.0 – 1.0).
    is_recurring : bool
        Whether this generates recurring revenue.
    tags : list[str]
        Searchable tags.
    active : bool
        Whether this item is available.
    """

    item_id: str
    name: str
    category: CatalogCategory
    description: str
    price_usd: float
    commission_pct: float = 0.20
    is_recurring: bool = False
    tags: list[str] = field(default_factory=list)
    active: bool = True
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def commission_amount(self) -> float:
        """Return the dollar commission per sale."""
        return round(self.price_usd * self.commission_pct, 2)

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "price_usd": self.price_usd,
            "commission_pct": self.commission_pct,
            "commission_amount": self.commission_amount(),
            "is_recurring": self.is_recurring,
            "tags": self.tags,
            "active": self.active,
        }


# ---------------------------------------------------------------------------
# Franchise
# ---------------------------------------------------------------------------

@dataclass
class Franchise:
    """
    A franchise territory in the DreamCo network.

    Attributes
    ----------
    franchise_id : str
        Unique identifier.
    owner_name : str
        Franchisee's name.
    territory : str
        Geographic or niche territory covered.
    monthly_fee_usd : float
        Recurring territory fee paid to DreamCo.
    status : FranchiseStatus
        Current franchise status.
    total_orders : int
        Total orders processed through this franchise.
    total_commission_earned_usd : float
        Cumulative commission earnings.
    """

    franchise_id: str
    owner_name: str
    territory: str
    monthly_fee_usd: float = 99.0
    status: FranchiseStatus = FranchiseStatus.PENDING
    total_orders: int = 0
    total_commission_earned_usd: float = 0.0
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def activate(self) -> None:
        """Activate this franchise."""
        self.status = FranchiseStatus.ACTIVE

    def record_order(self, commission: float) -> None:
        """Record an order and the commission earned."""
        self.total_orders += 1
        self.total_commission_earned_usd += commission

    def to_dict(self) -> dict:
        return {
            "franchise_id": self.franchise_id,
            "owner_name": self.owner_name,
            "territory": self.territory,
            "monthly_fee_usd": self.monthly_fee_usd,
            "status": self.status.value,
            "total_orders": self.total_orders,
            "total_commission_earned_usd": round(self.total_commission_earned_usd, 2),
            "created_at": self.created_at,
        }


# ---------------------------------------------------------------------------
# Catalog order
# ---------------------------------------------------------------------------

@dataclass
class CatalogOrder:
    """A customer order placed through the catalog."""
    order_id: str
    customer_id: str
    item_id: str
    franchise_id: Optional[str]
    amount_usd: float
    commission_usd: float
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "item_id": self.item_id,
            "franchise_id": self.franchise_id,
            "amount_usd": self.amount_usd,
            "commission_usd": self.commission_usd,
            "timestamp": self.timestamp,
        }


# ---------------------------------------------------------------------------
# Catalog & Franchise Engine
# ---------------------------------------------------------------------------

class CatalogFranchiseError(Exception):
    """Raised when a catalog or franchise operation fails."""


class CatalogFranchiseEngine:
    """
    Manages the DreamCo product catalog and franchise network.
    """

    def __init__(self) -> None:
        self._items: dict[str, CatalogItem] = {}
        self._franchises: dict[str, Franchise] = {}
        self._orders: list[CatalogOrder] = []
        self._item_counter: int = 0
        self._franchise_counter: int = 0
        self._order_counter: int = 0
        self._seed_catalog()

    # ------------------------------------------------------------------
    # Seed catalog
    # ------------------------------------------------------------------

    def _seed_catalog(self) -> None:
        seeds = [
            {
                "name": "Big Bro AI Pro Access",
                "category": CatalogCategory.AI_TOOLS,
                "description": "Full Pro-tier access to Big Bro AI mentor platform.",
                "price_usd": 49.0,
                "commission_pct": 0.30,
                "is_recurring": True,
                "tags": ["ai", "mentor", "subscription"],
            },
            {
                "name": "DreamCo Bot Starter Kit",
                "category": CatalogCategory.BOTS,
                "description": "Bundle of 5 income-generating bots ready to deploy.",
                "price_usd": 197.0,
                "commission_pct": 0.25,
                "tags": ["bots", "automation", "income"],
            },
            {
                "name": "Automation Agency Template Pack",
                "category": CatalogCategory.TEMPLATES,
                "description": "Ready-to-use proposal, pricing, and delivery templates.",
                "price_usd": 97.0,
                "commission_pct": 0.40,
                "tags": ["templates", "agency", "freelance"],
            },
            {
                "name": "Franchise Owner Kit",
                "category": CatalogCategory.FRANCHISE_KIT,
                "description": "Everything needed to open a DreamCo franchise territory.",
                "price_usd": 999.0,
                "commission_pct": 0.15,
                "tags": ["franchise", "business", "territory"],
            },
            {
                "name": "Money Systems Course Bundle",
                "category": CatalogCategory.COURSES,
                "description": "Five-course bundle covering DreamCo money systems.",
                "price_usd": 249.0,
                "commission_pct": 0.35,
                "is_recurring": False,
                "tags": ["courses", "money", "education"],
            },
        ]
        for s in seeds:
            self._item_counter += 1
            item_id = f"itm_{self._item_counter:04d}"
            item = CatalogItem(
                item_id=item_id,
                name=s["name"],
                category=s["category"],
                description=s["description"],
                price_usd=s["price_usd"],
                commission_pct=s.get("commission_pct", 0.20),
                is_recurring=s.get("is_recurring", False),
                tags=s.get("tags", []),
            )
            self._items[item_id] = item

    # ------------------------------------------------------------------
    # Catalog management
    # ------------------------------------------------------------------

    def add_item(
        self,
        name: str,
        category: CatalogCategory,
        description: str,
        price_usd: float,
        commission_pct: float = 0.20,
        is_recurring: bool = False,
        tags: Optional[list[str]] = None,
    ) -> CatalogItem:
        """Add a new item to the catalog."""
        self._item_counter += 1
        item_id = f"itm_{self._item_counter:04d}"
        item = CatalogItem(
            item_id=item_id,
            name=name,
            category=category,
            description=description,
            price_usd=price_usd,
            commission_pct=commission_pct,
            is_recurring=is_recurring,
            tags=tags or [],
        )
        self._items[item_id] = item
        return item

    def get_item(self, item_id: str) -> Optional[CatalogItem]:
        return self._items.get(item_id)

    def search_catalog(
        self,
        category: Optional[CatalogCategory] = None,
        tag: Optional[str] = None,
        max_price: Optional[float] = None,
        active_only: bool = True,
    ) -> list[CatalogItem]:
        """Search catalog items by category, tag, or price."""
        items = list(self._items.values())
        if active_only:
            items = [i for i in items if i.active]
        if category is not None:
            items = [i for i in items if i.category == category]
        if tag is not None:
            items = [i for i in items if tag in i.tags]
        if max_price is not None:
            items = [i for i in items if i.price_usd <= max_price]
        return sorted(items, key=lambda i: i.price_usd)

    def item_count(self) -> int:
        return len(self._items)

    # ------------------------------------------------------------------
    # Franchise management
    # ------------------------------------------------------------------

    def open_franchise(
        self,
        owner_name: str,
        territory: str,
        monthly_fee_usd: float = 99.0,
    ) -> Franchise:
        """Register a new franchise."""
        self._franchise_counter += 1
        franchise_id = f"frn_{self._franchise_counter:04d}"
        franchise = Franchise(
            franchise_id=franchise_id,
            owner_name=owner_name,
            territory=territory,
            monthly_fee_usd=monthly_fee_usd,
        )
        self._franchises[franchise_id] = franchise
        return franchise

    def get_franchise(self, franchise_id: str) -> Optional[Franchise]:
        return self._franchises.get(franchise_id)

    def activate_franchise(self, franchise_id: str) -> Franchise:
        """Activate a pending franchise."""
        franchise = self._require_franchise(franchise_id)
        franchise.activate()
        return franchise

    def list_franchises(
        self, status: Optional[FranchiseStatus] = None
    ) -> list[Franchise]:
        franchises = list(self._franchises.values())
        if status is not None:
            franchises = [f for f in franchises if f.status == status]
        return franchises

    def franchise_count(self) -> int:
        return len(self._franchises)

    # ------------------------------------------------------------------
    # Order processing
    # ------------------------------------------------------------------

    def place_order(
        self,
        customer_id: str,
        item_id: str,
        franchise_id: Optional[str] = None,
    ) -> CatalogOrder:
        """Place a catalog order, optionally through a franchise."""
        item = self._items.get(item_id)
        if item is None:
            raise CatalogFranchiseError(f"Item '{item_id}' not found in catalog.")
        if franchise_id is not None:
            franchise = self._require_franchise(franchise_id)
            commission = item.commission_amount()
            franchise.record_order(commission)
        else:
            commission = 0.0
        self._order_counter += 1
        order_id = f"ord_{self._order_counter:04d}"
        order = CatalogOrder(
            order_id=order_id,
            customer_id=customer_id,
            item_id=item_id,
            franchise_id=franchise_id,
            amount_usd=item.price_usd,
            commission_usd=commission,
        )
        self._orders.append(order)
        return order

    # ------------------------------------------------------------------
    # Revenue summary
    # ------------------------------------------------------------------

    def catalog_report(self) -> dict:
        """Return a full catalog and franchise revenue summary."""
        total_order_revenue = sum(o.amount_usd for o in self._orders)
        total_commission_paid = sum(o.commission_usd for o in self._orders)
        active_franchises = [
            f for f in self._franchises.values() if f.status == FranchiseStatus.ACTIVE
        ]
        monthly_franchise_fees = sum(f.monthly_fee_usd for f in active_franchises)
        return {
            "total_catalog_items": self.item_count(),
            "total_orders": len(self._orders),
            "total_order_revenue_usd": round(total_order_revenue, 2),
            "total_commission_paid_usd": round(total_commission_paid, 2),
            "total_franchises": self.franchise_count(),
            "active_franchises": len(active_franchises),
            "monthly_franchise_fee_revenue_usd": round(monthly_franchise_fees, 2),
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _require_franchise(self, franchise_id: str) -> Franchise:
        franchise = self._franchises.get(franchise_id)
        if franchise is None:
            raise CatalogFranchiseError(f"Franchise '{franchise_id}' not found.")
        return franchise
