"""
dataset_manager.py – Dataset creation, hosting, and selling pipeline.

Provides a ``DatasetManager`` for bots to:
* Register and describe datasets.
* Enforce licensing and ethical compliance metadata.
* Expose dataset listings for buyers.
* Record sale transactions (production deployments replace the stub payment
  handler with a real payment gateway such as Stripe).
"""

import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Dataset:
    """Represents a dataset available for sale or distribution."""
    dataset_id: str
    name: str
    description: str
    domain: str                    # e.g. "healthcare", "legal", "engineering"
    size_mb: float
    price_usd: float
    license: str                   # e.g. "CC-BY-4.0", "MIT", "Proprietary"
    tags: List[str] = field(default_factory=list)
    ethical_review_passed: bool = False
    created_at: float = field(default_factory=time.time)
    samples: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SaleRecord:
    """Immutable record of a completed dataset sale."""
    sale_id: str
    dataset_id: str
    buyer_id: str
    price_usd: float
    timestamp: float


# ---------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------

class DatasetManager:
    """
    Central registry for datasets owned / curated by a bot.

    Usage
    -----
    >>> mgr = DatasetManager(owner_bot_id="doctor-bot")
    >>> ds = mgr.create_dataset(
    ...     name="Clinical Notes NLP Corpus",
    ...     description="De-identified clinical notes for NLP research.",
    ...     domain="healthcare",
    ...     size_mb=250.0,
    ...     price_usd=499.00,
    ...     license="CC-BY-4.0",
    ...     tags=["NLP", "clinical", "healthcare"],
    ...     ethical_review_passed=True,
    ... )
    >>> mgr.list_datasets()
    """

    def __init__(self, owner_bot_id: str):
        self.owner_bot_id = owner_bot_id
        self._datasets: Dict[str, Dataset] = {}
        self._sales: List[SaleRecord] = []

    # ------------------------------------------------------------------
    # Dataset registration
    # ------------------------------------------------------------------

    def create_dataset(
        self,
        name: str,
        description: str,
        domain: str,
        size_mb: float,
        price_usd: float,
        license: str,
        tags: Optional[List[str]] = None,
        ethical_review_passed: bool = False,
        samples: Optional[List[Dict[str, Any]]] = None,
    ) -> Dataset:
        """Register a new dataset and return the Dataset object."""
        dataset_id = str(uuid.uuid4())
        ds = Dataset(
            dataset_id=dataset_id,
            name=name,
            description=description,
            domain=domain,
            size_mb=size_mb,
            price_usd=price_usd,
            license=license,
            tags=tags or [],
            ethical_review_passed=ethical_review_passed,
            samples=samples or [],
        )
        self._datasets[dataset_id] = ds
        return ds

    def get_dataset(self, dataset_id: str) -> Optional[Dataset]:
        return self._datasets.get(dataset_id)

    def list_datasets(self, domain: Optional[str] = None) -> List[Dataset]:
        datasets = list(self._datasets.values())
        if domain:
            datasets = [d for d in datasets if d.domain.lower() == domain.lower()]
        return datasets

    def remove_dataset(self, dataset_id: str) -> bool:
        if dataset_id in self._datasets:
            del self._datasets[dataset_id]
            return True
        return False

    # ------------------------------------------------------------------
    # Selling / distribution
    # ------------------------------------------------------------------

    def sell_dataset(self, dataset_id: str, buyer_id: str) -> Optional[SaleRecord]:
        """
        Process a dataset sale.

        In production, replace ``_process_payment`` with a real payment
        gateway integration (Stripe, PayPal, etc.).
        """
        ds = self._datasets.get(dataset_id)
        if ds is None:
            return None
        if not ds.ethical_review_passed:
            raise ValueError(
                f"Dataset '{ds.name}' has not passed ethical review and cannot be sold."
            )
        payment_ok = self._process_payment(buyer_id, ds.price_usd)
        if not payment_ok:
            return None
        record = SaleRecord(
            sale_id=str(uuid.uuid4()),
            dataset_id=dataset_id,
            buyer_id=buyer_id,
            price_usd=ds.price_usd,
            timestamp=time.time(),
        )
        self._sales.append(record)
        return record

    @staticmethod
    def _process_payment(buyer_id: str, amount_usd: float) -> bool:
        """
        Stub payment processor.

        Replace with a real payment gateway in production.
        """
        print(f"[Payment] Processing ${amount_usd:.2f} from buyer '{buyer_id}' … OK (stub)")
        return True

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def total_revenue(self) -> float:
        return round(sum(s.price_usd for s in self._sales), 2)

    def sales_summary(self) -> Dict[str, Any]:
        return {
            "total_sales": len(self._sales),
            "total_revenue_usd": self.total_revenue(),
            "datasets_available": len(self._datasets),
        }

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        return {
            "owner_bot_id": self.owner_bot_id,
            "datasets": [ds.to_dict() for ds in self._datasets.values()],
            "sales": [asdict(s) for s in self._sales],
        }

    def save(self, filepath: str) -> None:
        with open(filepath, "w") as fh:
            json.dump(self.to_dict(), fh, indent=2)
