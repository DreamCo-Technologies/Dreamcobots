# Fiverr Automation Bot

A tier-aware Fiverr-like bot for the DreamCo ecosystem. Automates freelance
and gig-economy operations: gig listings, order management, freelancer/client
matching, job postings, proposal workflows, Stripe-powered payments,
milestone management, featured gig placement, and an admin analytics dashboard.

## Tiers & Service Fees

| Feature | Free | Pro ($49/mo) | Enterprise ($199/mo) |
|---|---|---|---|
| Service fee per transaction | 20% | 10% | 5% |
| Gig listings | 5 | 50 | Unlimited |
| Orders per month | 20 | 500 | Unlimited |
| Order tracking | ✅ | ✅ | ✅ |
| Inbox automation | ❌ | ✅ | ✅ |
| Review collection | ❌ | ✅ | ✅ |
| Analytics | ❌ | ✅ | ✅ |
| Pricing optimizer | ❌ | ✅ | ✅ |
| Bulk messaging | ❌ | ✅ | ✅ |
| Freelancer matching | ❌ | ✅ | ✅ |
| Job postings | ❌ | ✅ | ✅ |
| Proposals | ❌ | ✅ | ✅ |
| Stripe payments | ❌ | ✅ | ✅ |
| Milestones | ❌ | ✅ | ✅ |
| CRM export | ❌ | ❌ | ✅ |
| AI pricing | ❌ | ❌ | ✅ |
| White-label | ❌ | ❌ | ✅ |
| Admin dashboard | ❌ | ❌ | ✅ |
| Featured gigs | ❌ | ❌ | ✅ |
| Support | Community | Email 24 h SLA | Dedicated 24/7 |

---

## Quick Start

```python
from bots.fiverr_bot import FiverrBot, GigCategory, Tier

# Create a PRO bot
bot = FiverrBot(tier=Tier.PRO)

# Create a gig
gig = bot.create_gig(GigCategory.CONTENT_WRITING, price_usd=30.0)

# Receive and manage an order
order = bot.receive_order(gig["gig_id"], buyer_username="alice")
bot.start_order(order["order_id"])
bot.deliver_order(order["order_id"], "Here are your 10 articles!")
bot.complete_order(order["order_id"])
```

---

## Freelancer & Client Matching

```python
# Register profiles (PRO or ENTERPRISE)
bot.register_freelancer("jane", skills=["seo", "analytics"], hourly_rate_usd=45.0)
bot.register_client("acme_corp", company_name="ACME Corp")

# Post a job
job = bot.post_job(
    client_username="acme_corp",
    title="SEO audit needed",
    description="Audit our e-commerce site",
    category=GigCategory.SEO,
    budget_usd=500.0,
    skills_required=["seo", "analytics"],
)

# Get skill-matched freelancers
matches = bot.match_freelancers(job["job_id"])
# matches sorted by match_score descending
```

---

## Proposals

```python
# Freelancer submits a proposal
proposal = bot.submit_proposal(
    job_id=job["job_id"],
    freelancer_username="jane",
    cover_letter="I have 5 years of SEO experience.",
    rate_usd=40.0,
    delivery_days=7,
)

# Client accepts the best proposal (others auto-rejected)
bot.accept_proposal(proposal["proposal_id"])
```

---

## Stripe Payments

The bot reads the Stripe secret key from the `STRIPE_SECRET_KEY` environment
variable.  **Never hard-code your Stripe key in source code.**

```bash
export STRIPE_SECRET_KEY=sk_test_...   # or sk_live_... for production
```

When `STRIPE_SECRET_KEY` is not set the bot operates in **mock mode** — all
payment calls return realistic mock responses without making real API calls.
This is the default in tests and local development.

```python
# Create a payment intent for an order (uses env var automatically)
result = bot.create_payment_intent(order_id="ord_0001")
print(result["id"])        # pi_...
print(result.get("mock"))  # True in mock mode, absent in live mode
```

---

## Milestones

```python
# Add milestones to an order
ms1 = bot.add_milestone(order["order_id"], "Design phase", amount_usd=100.0)
ms2 = bot.add_milestone(order["order_id"], "Development phase", amount_usd=200.0)

# Fund a milestone (creates a Stripe PaymentIntent)
bot.fund_milestone(ms1["milestone_id"])

# Release funds to freelancer (Stripe Transfer, deducting service fee)
result = bot.release_milestone(ms1["milestone_id"])
print(result["transfer"])  # Transfer details
```

---

## Featured Gigs (ENTERPRISE)

```python
bot_ent = FiverrBot(tier=Tier.ENTERPRISE)
gig = bot_ent.create_gig(GigCategory.WEB_DEVELOPMENT)

# Feature for 14 days for priority placement
bot_ent.feature_gig(gig["gig_id"], days=14)

# List all featured gigs
featured = bot_ent.get_featured_gigs()
```

---

## Admin Dashboard (ENTERPRISE)

```python
dashboard = bot_ent.get_admin_dashboard()
print(dashboard["revenue"])
# {
#   "gross_usd": 1500.0,
#   "service_fees_usd": 75.0,   # 5% enterprise fee
#   "net_usd": 1425.0,
#   "service_fee_pct": 5.0
# }
print(dashboard["users"])
# {"freelancers": 12, "clients": 8}
```

---

## Revenue Features

- **Service fees**: charged automatically on every completed order/milestone
  release. Rate depends on tier (5%–20%).
- **Subscription tiers**: recurring monthly revenue at $49 (Pro) or $199
  (Enterprise).
- **Featured gig placements**: ENTERPRISE clients can pay to highlight gigs
  for priority placement (via `feature_gig()`).
- **Premium memberships**: access to AI pricing, white-label, and admin
  dashboard requires the ENTERPRISE subscription.

---

## Running Tests

```bash
python -m pytest tests/test_fiverr_bot.py -v
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `STRIPE_SECRET_KEY` | No (mock used if absent) | Stripe API secret key (`sk_test_...` or `sk_live_...`) |
| `STRIPE_PUBLISHABLE_KEY` | No | Stripe publishable key for client-side |
| `STRIPE_WEBHOOK_SECRET` | No | Stripe webhook signing secret |

Store secrets securely — use `.env` locally (never commit to source control)
and GitHub Secrets / environment variables in CI/CD pipelines.
