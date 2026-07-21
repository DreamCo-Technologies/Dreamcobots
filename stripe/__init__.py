"""
DreamCobots stripe package.

Provides DreamCobots-specific Stripe utilities:
  - ``subscription_handler`` — tier-based subscription management

For the Stripe SDK (``stripe.Customer``, ``stripe.Webhook``, etc.),
import it directly via ``import stripe as _stripe_sdk`` using a path that
doesn't include this directory, or guard with a try/except in simulation mode.
"""
