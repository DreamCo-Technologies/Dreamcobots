"""
Stripe Payment Links for Dreamcobots.

Generate shareable Stripe Payment Links so bots can direct customers to a
hosted payment page without requiring a custom checkout integration.

Usage
-----
    from bots.stripe_integration import PaymentLinks

    pl = PaymentLinks()
    link = pl.create_link(
        amount_cents=4999,
        currency="usd",
        product_name="Lead Gen Bot — Starter",
        quantity=1,
    )
    print(link["url"])  # e.g. https://buy.stripe.com/...
"""

import os
import uuid
import datetime
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401


class PaymentLinksError(Exception):
    """Raised when a payment link operation fails."""


class PaymentLinks:
    """
    Create and manage Stripe Payment Links for Dreamcobots bots.

    Parameters
    ----------
    secret_key : str, optional
        Stripe secret key.  Defaults to ``STRIPE_SECRET_KEY`` env var.
    """

    def __init__(self, secret_key: Optional[str] = None) -> None:
        self.secret_key = secret_key or os.environ.get("STRIPE_SECRET_KEY", "")
        self.simulation_mode = not self.secret_key
        self._stripe = None
        if not self.simulation_mode:
            self._stripe = self._load_stripe()
        self._links: dict[str, dict] = {}

    @staticmethod
    def _load_stripe():
        try:
            import stripe  # noqa: PLC0415
            return stripe
        except ImportError:
            return None

    @staticmethod
    def _new_id() -> str:
        return f"plink_{uuid.uuid4().hex[:16]}"

    @staticmethod
    def _now_iso() -> str:
        return datetime.datetime.now(datetime.timezone.utc).isoformat()

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create_link(
        self,
        amount_cents: int,
        currency: str,
        product_name: str,
        quantity: int = 1,
        allow_quantity_adjust: bool = False,
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        Create a Stripe Payment Link.

        Parameters
        ----------
        amount_cents : int
            Price in the smallest currency unit.
        currency : str
            ISO 4217 currency code, e.g. ``"usd"``.
        product_name : str
            Name shown on the hosted payment page.
        quantity : int
            Default quantity.
        allow_quantity_adjust : bool
            Whether customers can adjust the quantity.
        metadata : dict, optional
            Key-value metadata attached to the link.

        Returns
        -------
        dict
            Payment link record with ``id`` and ``url``.
        """
        if not self.simulation_mode and self._stripe:
            self._stripe.api_key = self.secret_key
            # Create an inline price to avoid needing a pre-existing Price ID
            price = self._stripe.Price.create(
                unit_amount=amount_cents,
                currency=currency.lower(),
                product_data={"name": product_name},
            )
            link = self._stripe.PaymentLink.create(
                line_items=[
                    {
                        "price": price.id,
                        "quantity": quantity,
                        "adjustable_quantity": {"enabled": allow_quantity_adjust},
                    }
                ],
                metadata=metadata or {},
            )
            result = {
                "id": link.id,
                "url": link.url,
                "product_name": product_name,
                "amount_cents": amount_cents,
                "currency": currency.lower(),
                "quantity": quantity,
                "active": link.active,
                "created": self._now_iso(),
                "live": True,
            }
        else:
            lid = self._new_id()
            result = {
                "id": lid,
                "url": f"https://buy.stripe.com/simulated/{lid}",
                "product_name": product_name,
                "amount_cents": amount_cents,
                "currency": currency.lower(),
                "quantity": quantity,
                "active": True,
                "created": self._now_iso(),
                "live": False,
            }
        self._links[result["id"]] = result
        return result

    # ------------------------------------------------------------------
    # Deactivate / list
    # ------------------------------------------------------------------

    def deactivate_link(self, link_id: str) -> dict:
        """
        Deactivate an existing Payment Link.

        Parameters
        ----------
        link_id : str
            Stripe Payment Link ID.

        Returns
        -------
        dict
            Updated link with ``active`` set to ``False``.
        """
        if not self.simulation_mode and self._stripe:
            self._stripe.api_key = self.secret_key
            link = self._stripe.PaymentLink.modify(link_id, active=False)
            return {"id": link.id, "active": link.active, "live": True}
        if link_id not in self._links:
            raise PaymentLinksError(f"Payment link not found: {link_id}")
        self._links[link_id]["active"] = False
        return {"id": link_id, "active": False, "live": False}

    def list_links(self) -> list:
        """Return all locally tracked payment links."""
        return list(self._links.values())
