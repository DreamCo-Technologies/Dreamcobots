"""
AliDropship Money Bot — DreamCo Level autonomous dropshipping empire system.

Engines:
  1. Product Hunter Engine   — finds viral, high-profit AliExpress products
  2. Store Builder Engine    — auto-creates WordPress + AliDropship stores
  3. Pricing & Profit Engine — calculates optimal sell prices
  4. Auto Fulfillment Engine — processes orders and sends tracking updates
  5. Traffic Generator       — TikTok viral bot, Facebook ads, influencer outreach
  6. Scaling Engine          — scales winners, kills losers, duplicates stores

Tiers:
  FREE       — product discovery (5/day), pricing calculator, 1 niche
  PRO ($49)  — full store builder, 50 products/day, ads bot, 5 niches
  ENTERPRISE ($199) — multi-store, unlimited discovery, AI automation, white-label
"""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.alidropship_money_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401


class AliDropshipBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class AliDropshipMoneyBot:
    """
    Autonomous AliDropship dropshipping empire bot (DreamCo Level).

    Orchestrates all six engines to find products, build stores, price
    items, fulfill orders, drive traffic, and scale winning products.
    """

    # ------------------------------------------------------------------ #
    # Static data — winning-product catalogue and niche registry           #
    # ------------------------------------------------------------------ #

    WINNING_PRODUCTS = [
        {
            "id": "p001",
            "title": "Posture Corrector Belt",
            "niche": "health",
            "aliexpress_cost_usd": 6.50,
            "orders": 12800,
            "rating": 4.7,
            "tiktok_trending": True,
            "wow_factor": True,
            "solves_problem": True,
            "easy_to_ship": True,
            "video_engagement": "high",
        },
        {
            "id": "p002",
            "title": "LED Nail Lamp 48W",
            "niche": "beauty",
            "aliexpress_cost_usd": 8.20,
            "orders": 9400,
            "rating": 4.8,
            "tiktok_trending": True,
            "wow_factor": True,
            "solves_problem": False,
            "easy_to_ship": True,
            "video_engagement": "high",
        },
        {
            "id": "p003",
            "title": "Smart Plant Watering Device",
            "niche": "home_gadgets",
            "aliexpress_cost_usd": 7.00,
            "orders": 6700,
            "rating": 4.6,
            "tiktok_trending": False,
            "wow_factor": True,
            "solves_problem": True,
            "easy_to_ship": True,
            "video_engagement": "medium",
        },
        {
            "id": "p004",
            "title": "Pet Hair Remover Roller",
            "niche": "pets",
            "aliexpress_cost_usd": 5.00,
            "orders": 18200,
            "rating": 4.9,
            "tiktok_trending": True,
            "wow_factor": False,
            "solves_problem": True,
            "easy_to_ship": True,
            "video_engagement": "high",
        },
        {
            "id": "p005",
            "title": "Resistance Band Set (11 pcs)",
            "niche": "fitness",
            "aliexpress_cost_usd": 9.00,
            "orders": 22000,
            "rating": 4.8,
            "tiktok_trending": True,
            "wow_factor": False,
            "solves_problem": True,
            "easy_to_ship": True,
            "video_engagement": "high",
        },
        {
            "id": "p006",
            "title": "Magnetic Phone Car Mount",
            "niche": "home_gadgets",
            "aliexpress_cost_usd": 5.50,
            "orders": 31000,
            "rating": 4.7,
            "tiktok_trending": False,
            "wow_factor": False,
            "solves_problem": True,
            "easy_to_ship": True,
            "video_engagement": "medium",
        },
        {
            "id": "p007",
            "title": "Eyebrow Stamp Stencil Kit",
            "niche": "beauty",
            "aliexpress_cost_usd": 6.00,
            "orders": 15600,
            "rating": 4.6,
            "tiktok_trending": True,
            "wow_factor": True,
            "solves_problem": True,
            "easy_to_ship": True,
            "video_engagement": "high",
        },
        {
            "id": "p008",
            "title": "Automatic Dog Ball Launcher",
            "niche": "pets",
            "aliexpress_cost_usd": 18.00,
            "orders": 5100,
            "rating": 4.7,
            "tiktok_trending": True,
            "wow_factor": True,
            "solves_problem": False,
            "easy_to_ship": False,
            "video_engagement": "high",
        },
        {
            "id": "p009",
            "title": "Portable Mini Projector",
            "niche": "home_gadgets",
            "aliexpress_cost_usd": 15.00,
            "orders": 8900,
            "rating": 4.5,
            "tiktok_trending": True,
            "wow_factor": True,
            "solves_problem": False,
            "easy_to_ship": True,
            "video_engagement": "high",
        },
        {
            "id": "p010",
            "title": "Ab Roller Wheel Kit",
            "niche": "fitness",
            "aliexpress_cost_usd": 7.80,
            "orders": 19500,
            "rating": 4.8,
            "tiktok_trending": True,
            "wow_factor": False,
            "solves_problem": True,
            "easy_to_ship": True,
            "video_engagement": "high",
        },
        {
            "id": "p011",
            "title": "Ultrasonic Pest Repeller",
            "niche": "home_gadgets",
            "aliexpress_cost_usd": 5.20,
            "orders": 24000,
            "rating": 4.4,
            "tiktok_trending": False,
            "wow_factor": False,
            "solves_problem": True,
            "easy_to_ship": True,
            "video_engagement": "low",
        },
        {
            "id": "p012",
            "title": "Teeth Whitening LED Kit",
            "niche": "beauty",
            "aliexpress_cost_usd": 10.00,
            "orders": 7300,
            "rating": 4.6,
            "tiktok_trending": True,
            "wow_factor": True,
            "solves_problem": True,
            "easy_to_ship": True,
            "video_engagement": "high",
        },
    ]

    NICHES = ["health", "beauty", "fitness", "pets", "home_gadgets", "fashion", "tech_accessories", "baby", "outdoor", "kitchen"]

    STORE_PAGES = ["Home", "Shop", "Track Order", "Contact", "FAQ", "About Us"]

    MOCK_ORDERS = [
        {"order_id": "ORD-001", "product_id": "p001", "customer": "Alice Johnson", "amount_usd": 29.99, "status": "pending"},
        {"order_id": "ORD-002", "product_id": "p004", "customer": "Bob Smith",   "amount_usd": 19.99, "status": "pending"},
        {"order_id": "ORD-003", "product_id": "p005", "customer": "Carol Davis", "amount_usd": 34.99, "status": "pending"},
    ]

    DAILY_PRODUCT_LIMIT = {Tier.FREE: 5, Tier.PRO: 50, Tier.ENTERPRISE: None}
    NICHE_LIMIT         = {Tier.FREE: 1, Tier.PRO: 5,  Tier.ENTERPRISE: None}
    STORE_LIMIT         = {Tier.FREE: 0, Tier.PRO: 1,  Tier.ENTERPRISE: 10}
    AD_LIMIT_PER_DAY    = {Tier.FREE: 0, Tier.PRO: 5,  Tier.ENTERPRISE: None}
    VIDEO_LIMIT_PER_DAY = {Tier.FREE: 0, Tier.PRO: 3,  Tier.ENTERPRISE: 10}

    # ------------------------------------------------------------------ #
    # Lifecycle                                                            #
    # ------------------------------------------------------------------ #

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier   = tier
        self.config = get_tier_config(tier)
        self._built_stores:    list[dict] = []
        self._active_products: list[dict] = []
        self._fulfilled_orders: list[dict] = []
        self._launched_ads:    list[dict] = []

    # ================================================================== #
    # 1. Product Hunter Engine                                             #
    # ================================================================== #

    def find_winning_products(self, niche: str | None = None, limit: int | None = None) -> list[dict]:
        """
        Discover viral, high-profit AliExpress products.

        Filters by orders > 500, rating > 4.5, and trending signals.
        FREE tier: up to 5 products, 1 niche.
        PRO tier:  up to 50 products, 5 niches.
        ENTERPRISE: unlimited.
        """
        daily_cap = self.DAILY_PRODUCT_LIMIT[self.tier]

        products = [
            p for p in self.WINNING_PRODUCTS
            if p["orders"] > 500 and p["rating"] > 4.5
        ]

        if niche:
            products = [p for p in products if p["niche"] == niche]

        # On FREE tier only tiktok-trending items are surfaced
        if self.tier == Tier.FREE:
            products = [p for p in products if p["tiktok_trending"]]

        if limit is not None:
            products = products[:limit]
        elif daily_cap is not None:
            products = products[:daily_cap]

        self._active_products = products
        return [self._annotate_product(p) for p in products]

    def _annotate_product(self, product: dict) -> dict:
        sell_price = self.calculate_sell_price(product["aliexpress_cost_usd"])
        profit     = round(sell_price - product["aliexpress_cost_usd"], 2)
        return {
            **product,
            "suggested_sell_price_usd": sell_price,
            "estimated_profit_usd":     profit,
            "profit_margin_pct":        round(profit / sell_price * 100, 1),
            "tier": self.tier.value,
        }

    # ================================================================== #
    # 2. Store Builder Engine                                              #
    # ================================================================== #

    def build_store(self, niche: str, products: list[dict] | None = None) -> dict:
        """
        Auto-create a WordPress + AliDropship store for a niche.

        FREE tier: not available.
        PRO tier:  build 1 store.
        ENTERPRISE: build up to 10 stores.
        """
        store_cap = self.STORE_LIMIT[self.tier]
        if store_cap == 0:
            raise AliDropshipBotTierError(
                "Store builder requires PRO or ENTERPRISE tier. "
                "Upgrade to automatically create WordPress + AliDropship stores."
            )
        if store_cap is not None and len(self._built_stores) >= store_cap:
            raise AliDropshipBotTierError(
                f"{self.config.name} tier allows up to {store_cap} store(s). "
                "Upgrade to ENTERPRISE for up to 10 stores."
            )

        if products is None:
            products = self.find_winning_products(niche=niche)

        domain   = self._generate_domain(niche)
        brand    = self.create_brand(niche)
        store_id = f"store_{len(self._built_stores) + 1:03d}"

        store = {
            "store_id":    store_id,
            "domain":      domain,
            "niche":       niche,
            "brand":       brand,
            "platform":    "WordPress + AliDropship",
            "pages":       self.STORE_PAGES,
            "products":    products,
            "features": {
                "reviews":       True,
                "scarcity_alert": True,
                "upsells":       self.tier in (Tier.PRO, Tier.ENTERPRISE),
                "ai_descriptions": self.tier == Tier.ENTERPRISE,
                "live_chat":     self.tier == Tier.ENTERPRISE,
            },
            "status": "live",
            "tier":   self.tier.value,
        }
        self._built_stores.append(store)
        return store

    def create_brand(self, niche: str) -> dict:
        """Generate a brand identity (name, logo placeholder, slogan) for a niche."""
        brand_map = {
            "health":          ("VitalCore Shop",   "Your health, delivered."),
            "beauty":          ("GlowHaven",        "Reveal your glow."),
            "fitness":         ("IronEdge Gear",    "Train harder. Live stronger."),
            "pets":            ("PawPerfect Store", "Because they deserve the best."),
            "home_gadgets":    ("SmartNest Hub",    "Smart home, smart life."),
            "fashion":         ("TrendVault",       "Style without limits."),
            "tech_accessories": ("TechFlow Store",  "Power your world."),
            "baby":            ("TinyWonders",      "Gentle care, big smiles."),
            "outdoor":         ("TrailBlaze Gear",  "Gear up, go further."),
            "kitchen":         ("ChefMate Store",   "Cook smarter, eat better."),
        }
        name, slogan = brand_map.get(niche, (f"{niche.title()} Store", "Quality you can trust."))
        return {
            "name":   name,
            "logo":   f"https://assets.dreamco.ai/logos/{niche}_logo.png",
            "slogan": slogan,
            "niche":  niche,
        }

    def _generate_domain(self, niche: str) -> str:
        brand = self.create_brand(niche)
        slug  = brand["name"].lower().replace(" ", "")
        return f"https://www.{slug}.com"

    # ================================================================== #
    # 3. Pricing & Profit Engine                                           #
    # ================================================================== #

    def calculate_sell_price(self, cost_usd: float, multiplier: float = 3.0) -> float:
        """
        Apply the 3x markup formula and round to the nearest .99.

        Example: $10 cost → $29.99
        """
        raw   = cost_usd * multiplier
        floor = int(raw)
        return float(floor) + 0.99 if floor < raw else float(floor) - 0.01

    def generate_pricing_report(self, products: list[dict] | None = None) -> list[dict]:
        """Return a pricing report for the supplied (or active) products."""
        if products is None:
            products = self._active_products if self._active_products else self.find_winning_products()
        report = []
        for p in products:
            sell_price = self.calculate_sell_price(p["aliexpress_cost_usd"])
            profit     = round(sell_price - p["aliexpress_cost_usd"], 2)
            report.append({
                "id":             p["id"],
                "title":          p["title"],
                "cost_usd":       p["aliexpress_cost_usd"],
                "sell_price_usd": sell_price,
                "profit_usd":     profit,
                "roi_multiplier": 3.0,
                "tier":           self.tier.value,
            })
        return report

    # ================================================================== #
    # 4. Auto Fulfillment Engine                                           #
    # ================================================================== #

    def fulfill_order(self, order: dict) -> dict:
        """
        Process a customer order: place AliExpress order, add tracking,
        and queue a customer update notification.

        PRO and ENTERPRISE only.
        """
        if self.tier == Tier.FREE:
            raise AliDropshipBotTierError(
                "Auto fulfillment requires PRO or ENTERPRISE tier."
            )
        tracking = f"AE{abs(hash(order['order_id'])) % 10 ** 12:012d}"
        fulfilled = {
            **order,
            "status":        "fulfilled",
            "aliexpress_order_placed": True,
            "tracking_number": tracking,
            "customer_notified": True,
            "tier": self.tier.value,
        }
        self._fulfilled_orders.append(fulfilled)
        return fulfilled

    def bulk_fulfill_orders(self, orders: list[dict] | None = None) -> list[dict]:
        """Fulfill all pending orders in bulk."""
        if self.tier == Tier.FREE:
            raise AliDropshipBotTierError(
                "Bulk fulfillment requires PRO or ENTERPRISE tier."
            )
        pending = orders if orders is not None else [o for o in self.MOCK_ORDERS if o["status"] == "pending"]
        return [self.fulfill_order(o) for o in pending]

    # ================================================================== #
    # 5. Traffic Generator                                                 #
    # ================================================================== #

    def create_tiktok_content(self, product: dict) -> list[dict]:
        """
        Generate TikTok viral video scripts and auto-post metadata.

        FREE: not available.
        PRO:  up to 3 videos/day.
        ENTERPRISE: up to 10 videos/day.
        """
        cap = self.VIDEO_LIMIT_PER_DAY[self.tier]
        if cap == 0:
            raise AliDropshipBotTierError(
                "TikTok content generator requires PRO or ENTERPRISE tier."
            )
        hooks = [
            f"This {product['title']} changed everything…",
            f"POV: You finally found {product['title']} 😱",
            f"I can't believe this {product['title']} is only ${self.calculate_sell_price(product['aliexpress_cost_usd']):.2f}",
            f"The {product['niche']} hack nobody is talking about 👀",
            f"Watch this before you shop for {product['title']}",
        ]
        videos = []
        for i, hook in enumerate(hooks[:cap]):
            videos.append({
                "video_id":  f"vid_{product['id']}_{i + 1:02d}",
                "product":   product["title"],
                "hook":      hook,
                "format":    "demo + hook + CTA",
                "duration_s": 15 + i * 5,
                "posted":    True,
                "platform":  "TikTok",
                "tier":      self.tier.value,
            })
        return videos

    def run_facebook_ads(self, product: dict, daily_budget_usd: float = 10.0) -> list[dict]:
        """
        Launch and monitor Facebook ad campaigns for a product.

        FREE: not available.
        PRO:  up to 5 ads/day.
        ENTERPRISE: unlimited.
        """
        cap = self.AD_LIMIT_PER_DAY[self.tier]
        if cap == 0:
            raise AliDropshipBotTierError(
                "Facebook ads bot requires PRO or ENTERPRISE tier."
            )
        sell_price = self.calculate_sell_price(product["aliexpress_cost_usd"])
        ad_copy_templates = [
            f"🔥 {product['title']} — Limited Stock! Only ${sell_price:.2f}",
            f"✅ Best {product['niche'].replace('_', ' ').title()} Deal: {product['title']}",
            f"😍 Customers LOVE this {product['title']} — Get yours now!",
            f"⚡ Flash Sale: {product['title']} at ${sell_price:.2f} — Free Shipping!",
            f"💯 Top-Rated {product['title']} — Shop Now Before It Sells Out!",
        ]
        ads = []
        limit = cap if cap is not None else len(ad_copy_templates)
        for i, copy in enumerate(ad_copy_templates[:limit]):
            roas = round(1.5 + i * 0.4, 1)
            ads.append({
                "ad_id":         f"ad_{product['id']}_{i + 1:02d}",
                "product":       product["title"],
                "copy":          copy,
                "daily_budget":  daily_budget_usd,
                "status":        "active" if roas >= 2.0 else "paused",
                "roas":          roas,
                "platform":      "Facebook",
                "tier":          self.tier.value,
            })
        return ads

    def run_influencer_outreach(self, niche: str) -> list[dict]:
        """
        Find micro-influencers and send DM outreach scripts.

        ENTERPRISE only.
        """
        if self.tier != Tier.ENTERPRISE:
            raise AliDropshipBotTierError(
                "Influencer outreach requires ENTERPRISE tier."
            )
        influencers = [
            {"handle": f"@{niche}fan_{i}", "followers": 15000 + i * 5000, "niche": niche}
            for i in range(1, 6)
        ]
        outreach = []
        for inf in influencers:
            outreach.append({
                **inf,
                "dm_script": (
                    f"Hey {inf['handle']}! Love your {niche} content. "
                    "We'd love to partner — free product + commission per sale. "
                    "Interested? Reply here!"
                ),
                "sent":  True,
                "tier":  self.tier.value,
            })
        return outreach

    # ================================================================== #
    # 6. Scaling Engine                                                    #
    # ================================================================== #

    def scale_or_kill_product(self, product: dict, roi: float) -> dict:
        """
        Decide to scale (increase budget, duplicate ads) or kill
        a product based on ROI.

        PRO and ENTERPRISE only.
        """
        if self.tier == Tier.FREE:
            raise AliDropshipBotTierError(
                "Scaling engine requires PRO or ENTERPRISE tier."
            )
        if roi >= 2.0:
            action = "scale"
            result = {
                "action":           "scale",
                "budget_increase":  "2x current spend",
                "duplicate_ads":    True,
                "new_creatives":    self.tier == Tier.ENTERPRISE,
                "build_brand":      self.tier == Tier.ENTERPRISE,
            }
        else:
            action = "kill"
            result = {
                "action":  "kill",
                "reason":  f"ROI {roi:.2f} below 2.0 threshold",
            }
        return {
            "product_id": product.get("id", "unknown"),
            "product":    product.get("title", ""),
            "roi":        roi,
            **result,
            "tier":       self.tier.value,
        }

    def get_scaling_report(self, product_roi_map: dict[str, float] | None = None) -> list[dict]:
        """
        Generate scaling decisions for all active products.

        Parameters
        ----------
        product_roi_map : dict mapping product_id -> roi float, optional
            Provide custom ROI values; defaults to mock data.
        """
        if self.tier == Tier.FREE:
            raise AliDropshipBotTierError(
                "Scaling report requires PRO or ENTERPRISE tier."
            )
        mock_rois = {"p001": 2.5, "p004": 3.1, "p005": 1.8, "p007": 2.2, "p010": 0.9}
        rois      = product_roi_map if product_roi_map is not None else mock_rois
        products  = self._active_products if self._active_products else self.find_winning_products()
        return [
            self.scale_or_kill_product(p, rois.get(p["id"], 1.5))
            for p in products
        ]

    # ================================================================== #
    # Master Orchestrator                                                  #
    # ================================================================== #

    def run_dreamco_master(self, niches: list[str] | None = None) -> dict:
        """
        Master control: runs the full DreamCo AliDropship system end-to-end.

        For each niche: discovers products, builds a store, creates TikTok
        content, launches ads, and evaluates scaling decisions.

        ENTERPRISE only (full automation across all engines).
        """
        if self.tier != Tier.ENTERPRISE:
            raise AliDropshipBotTierError(
                "Full master orchestration requires ENTERPRISE tier."
            )
        if niches is None:
            niches = self.NICHES[:3]

        results: dict = {"stores": [], "content": [], "ads": [], "scaling": []}

        for niche in niches:
            products = self.find_winning_products(niche=niche)
            if not products:
                continue
            store = self.build_store(niche, products)
            results["stores"].append(store)

            for product in products[:2]:
                videos = self.create_tiktok_content(product)
                results["content"].extend(videos)
                ads = self.run_facebook_ads(product)
                results["ads"].extend(ads)

            scaling = self.get_scaling_report()
            results["scaling"].extend(scaling)

        return results

    # ================================================================== #
    # Support-site network (ENTERPRISE)                                    #
    # ================================================================== #

    def build_support_sites(self, niche: str, store_domain: str) -> dict:
        """
        Build the self-marketing support-site network for a niche store.

        Creates authority blog, deal/discount site, review site, and viral
        content hub — all linking back to *store_domain*.

        ENTERPRISE only.
        """
        if self.tier != Tier.ENTERPRISE:
            raise AliDropshipBotTierError(
                "Support-site network requires ENTERPRISE tier."
            )
        slug = niche.replace("_", "")
        return {
            "niche":        niche,
            "store_domain": store_domain,
            "sites": [
                {
                    "type":    "authority_blog",
                    "domain":  f"https://www.{slug}review.com",
                    "content": f"Top 10 trending {niche} products",
                    "traffic": "SEO",
                    "links_to": store_domain,
                },
                {
                    "type":    "deal_site",
                    "domain":  f"https://www.{slug}deals.com",
                    "content": "Discount alerts for all stores",
                    "traffic": "email + push",
                    "links_to": store_domain,
                },
                {
                    "type":    "review_site",
                    "domain":  f"https://www.best{slug}stores.com",
                    "content": f"Top rated {niche} stores",
                    "traffic": "organic",
                    "links_to": store_domain,
                },
                {
                    "type":    "viral_hub",
                    "domain":  f"https://www.{slug}viral.com",
                    "content": "Embedded TikTok videos",
                    "traffic": "TikTok embed",
                    "links_to": store_domain,
                },
            ],
            "tier": self.tier.value,
        }

    # ================================================================== #
    # Revenue projections                                                  #
    # ================================================================== #

    def get_revenue_projections(self) -> dict:
        """Return realistic revenue projections based on tier."""
        projections = {
            Tier.FREE: {
                "day_1":     "$0 – $100",
                "week_1":    "$0 – $200",
                "month_1":   "$0 – $500",
                "note":      "Manual setup required. Upgrade to PRO to automate.",
            },
            Tier.PRO: {
                "day_1":     "$0 – $100",
                "week_1":    "$200 – $1,000",
                "month_1":   "$1K – $5K",
                "months_3_6": "$5K – $20K+",
                "note":      "Depends on niche selection and ad execution.",
            },
            Tier.ENTERPRISE: {
                "day_1":     "$0 – $100",
                "week_1":    "$200 – $1,000",
                "month_1":   "$1K – $10K",
                "months_3_6": "$10K – $50K+",
                "note":      "Multi-store + AI automation + influencer network.",
            },
        }
        return {"tier": self.tier.value, **projections[self.tier]}

    # ================================================================== #
    # Tier info                                                            #
    # ================================================================== #

    def describe_tier(self) -> str:
        info  = get_bot_tier_info(self.tier)
        lines = [
            f"=== {info['name']} AliDropship Money Bot Tier ===",
            f"Price: ${info['price_usd_monthly']:.2f}/month",
            f"Support: {info['support_level']}",
            "Features:",
        ]
        for f in info["features"]:
            lines.append(f"  \u2713 {f}")
        output = "\n".join(lines)
        print(output)
        return output
