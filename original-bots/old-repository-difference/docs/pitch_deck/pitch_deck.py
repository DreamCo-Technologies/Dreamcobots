"""
DreamCo Global Wealth System — Investor Pitch Deck Structure

Provides a structured, programmatic representation of the 12-slide
DreamCo investor pitch deck. Each slide is a self-contained
``PitchSlide`` object with a title, type, bullet-point content,
and optional speaker notes.

Usage
-----
    from docs.pitch_deck import build_dreamco_pitch_deck

    deck = build_dreamco_pitch_deck()
    for slide in deck.slides:
        print(slide.render())

    # Export to Markdown
    print(deck.to_markdown())
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SlideType(Enum):
    """Semantic type for each slide in the deck."""
    VISION = "vision"
    PROBLEM = "problem"
    SOLUTION = "solution"
    MARKET = "market"
    HOW_IT_WORKS = "how_it_works"
    PRODUCT = "product"
    TECHNOLOGY = "technology"
    REVENUE = "revenue"
    GROWTH = "growth"
    COMPLIANCE = "compliance"
    ASK = "ask"
    CLOSING = "closing"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class PitchSlide:
    """A single investor pitch deck slide."""
    slide_number: int
    title: str
    slide_type: SlideType
    headline: str
    bullets: list[str]
    speaker_notes: str = ""
    visual_hint: str = ""         # Suggested diagram or image description
    call_to_action: Optional[str] = None

    def render(self) -> str:
        """Return a plain-text rendering of the slide."""
        lines = [
            f"{'='*60}",
            f"Slide {self.slide_number}: {self.title}",
            f"{'='*60}",
            f"  {self.headline}",
            "",
        ]
        for bullet in self.bullets:
            lines.append(f"  • {bullet}")
        if self.call_to_action:
            lines.append("")
            lines.append(f"  ➤ {self.call_to_action}")
        if self.visual_hint:
            lines.append("")
            lines.append(f"  [Visual: {self.visual_hint}]")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "slide_number": self.slide_number,
            "title": self.title,
            "slide_type": self.slide_type.value,
            "headline": self.headline,
            "bullets": self.bullets,
            "speaker_notes": self.speaker_notes,
            "visual_hint": self.visual_hint,
            "call_to_action": self.call_to_action,
        }


@dataclass
class PitchDeck:
    """The complete DreamCo investor pitch deck."""
    title: str
    subtitle: str
    company: str
    tagline: str
    slides: list[PitchSlide] = field(default_factory=list)

    def add_slide(self, slide: PitchSlide) -> None:
        self.slides.append(slide)

    def get_slide(self, slide_number: int) -> Optional[PitchSlide]:
        return next(
            (s for s in self.slides if s.slide_number == slide_number), None
        )

    def slide_count(self) -> int:
        return len(self.slides)

    def render(self) -> str:
        """Render the full deck as plain text."""
        header = [
            f"\n{'#'*60}",
            f"  {self.title}",
            f"  {self.subtitle}",
            f"  {self.company}",
            f"  '{self.tagline}'",
            f"{'#'*60}\n",
        ]
        body = [slide.render() for slide in self.slides]
        return "\n".join(header) + "\n\n".join(body)

    def to_markdown(self) -> str:
        """Export the deck as a Markdown document."""
        lines = [
            f"# {self.title}",
            f"## {self.subtitle}",
            f"**{self.company}** | *{self.tagline}*",
            "",
            "---",
            "",
        ]
        for slide in self.slides:
            lines.append(f"## Slide {slide.slide_number}: {slide.title}")
            lines.append(f"**{slide.headline}**")
            lines.append("")
            for bullet in slide.bullets:
                lines.append(f"- {bullet}")
            if slide.call_to_action:
                lines.append("")
                lines.append(f"> **Call to Action:** {slide.call_to_action}")
            if slide.visual_hint:
                lines.append("")
                lines.append(f"*Visual suggestion: {slide.visual_hint}*")
            if slide.speaker_notes:
                lines.append("")
                lines.append(f"<!-- Speaker notes: {slide.speaker_notes} -->")
            lines.append("")
            lines.append("---")
            lines.append("")
        return "\n".join(lines)

    def summary(self) -> dict:
        return {
            "title": self.title,
            "company": self.company,
            "tagline": self.tagline,
            "total_slides": self.slide_count(),
            "slide_types": [s.slide_type.value for s in self.slides],
        }


# ---------------------------------------------------------------------------
# Factory function
# ---------------------------------------------------------------------------

def build_dreamco_pitch_deck() -> PitchDeck:
    """
    Build and return the full 12-slide DreamCo Global Wealth System pitch deck.

    Returns
    -------
    PitchDeck
        Complete, investor-ready pitch deck structure.
    """
    deck = PitchDeck(
        title="DreamCo Global Wealth System",
        subtitle="Investor Pitch Deck",
        company="DreamCo Technologies",
        tagline="We're not replacing banks… we're replacing dependence.",
    )

    # ------------------------------------------------------------------
    # Slide 1 — Vision
    # ------------------------------------------------------------------
    deck.add_slide(PitchSlide(
        slide_number=1,
        title="Vision",
        slide_type=SlideType.VISION,
        headline="DreamCo = The People's Financial System",
        bullets=[
            "A global, AI-powered platform where communities pool money and invest together",
            "Every member earns automated income and shares in collective profits",
            "Communities control their own mini-economies through Wealth Hubs",
            "Think: Digital Credit Union + Hedge Fund + AI Business Engine — for everyone",
        ],
        speaker_notes=(
            "Open strong. Emphasize the democratization angle — this is about "
            "giving ordinary people the tools that were previously reserved for "
            "the wealthy. DreamCo levels the playing field."
        ),
        visual_hint="Globe icon with interconnected community nodes; DreamCo logo centered",
        call_to_action="Join the movement. Build generational wealth together.",
    ))

    # ------------------------------------------------------------------
    # Slide 2 — Problem
    # ------------------------------------------------------------------
    deck.add_slide(PitchSlide(
        slide_number=2,
        title="The Problem",
        slide_type=SlideType.PROBLEM,
        headline="The wealth gap is widening — and it's by design.",
        bullets=[
            "Traditional banks control capital and limit access to wealth-building tools",
            "Over 60% of Americans live paycheck to paycheck (CNBC, 2024)",
            "Communities lack collective ownership and shared investment vehicles",
            "Passive income streams are inaccessible to most without significant capital",
            "Existing fintech apps serve individuals — nobody serves communities",
        ],
        speaker_notes=(
            "Paint the pain clearly. Use real statistics. The audience should feel "
            "the urgency before you reveal the solution on the next slide."
        ),
        visual_hint="Split-screen: wealthy investor on left vs. struggling family on right",
    ))

    # ------------------------------------------------------------------
    # Slide 3 — Solution
    # ------------------------------------------------------------------
    deck.add_slide(PitchSlide(
        slide_number=3,
        title="The Solution",
        slide_type=SlideType.SOLUTION,
        headline="DreamCo creates a community-owned investment ecosystem.",
        bullets=[
            "Community Wealth Hubs — shared treasury pools anyone can create or join",
            "AI-powered income bots running automatically in the background",
            "Transparent shared investment portfolios with real-time tracking",
            "Automated dividend payouts distributed directly to members",
            "Governance voting so every member has a voice in decisions",
            "DreamCoin — an internal economy that rewards participation",
        ],
        speaker_notes=(
            "This is the 'aha' moment. Show how each problem from slide 2 is "
            "directly solved. The bots are the secret weapon — emphasize automation."
        ),
        visual_hint="DreamCo platform mockup showing Wealth Hub dashboard with member cards",
        call_to_action="One platform. Every tool you need to build wealth together.",
    ))

    # ------------------------------------------------------------------
    # Slide 4 — Market Opportunity
    # ------------------------------------------------------------------
    deck.add_slide(PitchSlide(
        slide_number=4,
        title="Market Opportunity",
        slide_type=SlideType.MARKET,
        headline="A multi-trillion dollar convergence of markets.",
        bullets=[
            "Global fintech market: $332B (2024) → $1.15T by 2032 (CAGR 16.8%)",
            "Creator economy & side hustle market: $127B and growing",
            "Community investing & cooperative finance: underserved $50B+ opportunity",
            "Decentralized finance (DeFi) total value: $100B+",
            "Target: 150M underbanked Americans + 1.7B globally",
            "Our beachhead: community groups, churches, families, online communities",
        ],
        speaker_notes=(
            "Show the TAM, SAM, SOM clearly. Investors need to see that the "
            "market is large enough to justify a billion-dollar outcome."
        ),
        visual_hint="Market size pyramid chart (TAM → SAM → SOM) with dollar figures",
    ))

    # ------------------------------------------------------------------
    # Slide 5 — How It Works
    # ------------------------------------------------------------------
    deck.add_slide(PitchSlide(
        slide_number=5,
        title="How It Works",
        slide_type=SlideType.HOW_IT_WORKS,
        headline="Five steps from deposit to dividend.",
        bullets=[
            "Step 1: User creates or joins a Wealth Hub (community treasury)",
            "Step 2: Members pool funds — each contribution tracked on ownership ledger",
            "Step 3: AI bots automatically allocate across three asset tiers",
            "  → 40% Wealth Protection: Gold, Silver, Treasury assets",
            "  → 40% Growth: Stocks, ETFs, Real Estate deals",
            "  → 20% High-Growth: Crypto, Startups, AI ventures",
            "Step 4: Profits generated and tracked in real time",
            "Step 5: Dividends distributed to members; portion auto-reinvested",
        ],
        speaker_notes=(
            "Walk through the flow visually. Make it feel simple. "
            "The technology handles the complexity — the user just deposits and earns."
        ),
        visual_hint="Circular flow diagram: Deposit → Pool → AI Invest → Profit → Dividend → Reinvest",
    ))

    # ------------------------------------------------------------------
    # Slide 6 — Secret Weapon: Bot Ecosystem
    # ------------------------------------------------------------------
    deck.add_slide(PitchSlide(
        slide_number=6,
        title="Secret Weapon: AI Bot Ecosystem",
        slide_type=SlideType.PRODUCT,
        headline="Every Wealth Hub gets a fleet of money-making AI bots.",
        bullets=[
            "💰 Money Finder Bot — scrapes grants, unclaimed funds, hidden opportunities",
            "📢 Referral Bot — auto-promotes apps and affiliate programs for passive income",
            "🏠 Real Estate Bot — finds foreclosures, deals, and no-money-down opportunities",
            "📊 Trading Bot — executes stock and crypto trades based on AI signals",
            "🛒 Arbitrage Bot — automatically flips products across platforms",
            "🎯 Lead Gen Bot — generates high-quality leads for member businesses",
            "🔍 Grant Finder Bot — discovers government and private grants",
            "Bots run 24/7, automatically, generating income while members sleep",
        ],
        speaker_notes=(
            "This is the differentiation. No competitor offers community-level "
            "AI automation. These bots compound the returns beyond passive investment."
        ),
        visual_hint="Bot control panel UI mockup with toggle switches and earnings per bot",
        call_to_action="Your Wealth Hub never sleeps.",
    ))

    # ------------------------------------------------------------------
    # Slide 7 — DreamCoin: Internal Economy
    # ------------------------------------------------------------------
    deck.add_slide(PitchSlide(
        slide_number=7,
        title="DreamCoin: Internal Economy",
        slide_type=SlideType.TECHNOLOGY,
        headline="DreamCoin powers the DreamCo ecosystem.",
        bullets=[
            "Internal utility token — not a speculative asset",
            "Earned through: contributions, bot activity, referrals, governance participation",
            "Used for: platform services, governance voting weight, staking rewards",
            "Burn + reward mechanism keeps value stable and incentives aligned",
            "1,000,000 total supply — distributed through activity, not ICO",
            "Cross-hub marketplace: members pay each other in DreamCoin for services",
        ],
        speaker_notes=(
            "Emphasize this is a utility token, not a speculative cryptocurrency. "
            "It's a loyalty/rewards program that powers the internal economy."
        ),
        visual_hint="DreamCoin token design with flow diagram showing earn/spend/stake cycle",
    ))

    # ------------------------------------------------------------------
    # Slide 8 — Revenue Model
    # ------------------------------------------------------------------
    deck.add_slide(PitchSlide(
        slide_number=8,
        title="Revenue Model",
        slide_type=SlideType.REVENUE,
        headline="Seven diversified streams targeting $1M+ ARR in Year 1.",
        bullets=[
            "1. Platform Fees — 1–3% on all transactions through Wealth Hubs",
            "2. Subscription Plans — FREE / PRO ($49/mo) / ENTERPRISE ($149/mo)",
            "3. Investment Performance Fee — 10% of profits generated by AI bots",
            "4. Referral System — DreamCo earns commission on all bot-generated referrals",
            "5. Marketplace Fees — 5% on cross-hub deals and member services",
            "6. DreamCoin Economy — token appreciation and staking fee revenue",
            "7. Business Funding Returns — equity in member businesses DreamCo funds",
        ],
        speaker_notes=(
            "Show unit economics. With 1,000 PRO subscribers at $49/mo = $588K ARR. "
            "Add transaction fees from $10M in hub treasury and you hit $1M easily."
        ),
        visual_hint="Revenue breakdown pie chart + 3-year projection bar chart",
        call_to_action="Path to $1M ARR: 1,000 PRO subscribers + $10M in hub treasury.",
    ))

    # ------------------------------------------------------------------
    # Slide 9 — Scale Strategy
    # ------------------------------------------------------------------
    deck.add_slide(PitchSlide(
        slide_number=9,
        title="Scale Strategy",
        slide_type=SlideType.GROWTH,
        headline="Local launch → Global financial ecosystem in 4 phases.",
        bullets=[
            "Phase 1 (Month 1–3): MVP — 1–3 Wealth Hubs, friends/family/community",
            "Phase 2 (Month 3–6): App Launch — public onboarding, automated bots live",
            "Phase 3 (Month 6–12): Viral Growth — referral explosion, influencer partnerships",
            "Phase 4 (Year 2+): Global Network — thousands of hubs, cross-border investing",
            "Viral loop: each member invites community → new Wealth Hub → more bots → more profit",
            "Network effects compound: larger hubs get access to bigger deal flow",
        ],
        speaker_notes=(
            "Growth strategy should feel inevitable, not theoretical. "
            "The referral bot creates a built-in viral loop that doesn't require paid ads."
        ),
        visual_hint="4-phase roadmap timeline with milestone markers and projected hub count",
    ))

    # ------------------------------------------------------------------
    # Slide 10 — Compliance
    # ------------------------------------------------------------------
    deck.add_slide(PitchSlide(
        slide_number=10,
        title="Compliance & Legal",
        slide_type=SlideType.COMPLIANCE,
        headline="Built to survive — compliance is a competitive advantage.",
        bullets=[
            "SEC-aligned: Wealth Hubs structured as investment cooperatives, not securities",
            "FinCEN / AML compliant: KYC verification at onboarding for all members",
            "No guaranteed returns: all risk disclosures legally embedded in platform",
            "Entity structure: LLC or Cooperative per hub for liability protection",
            "Data privacy: GDPR / CCPA compliant data handling",
            "Regulatory monitoring: real-time compliance dashboard for hub admins",
            "Legal counsel retained: securities, fintech, and data privacy specialists",
        ],
        speaker_notes=(
            "Proactively address the elephant in the room. Investors need to know "
            "you've thought about regulation. DreamCo operates legally AND "
            "disruptively — that's the power of the model."
        ),
        visual_hint="Compliance shield graphic with SEC, FinCEN, GDPR logos",
    ))

    # ------------------------------------------------------------------
    # Slide 11 — The Ask
    # ------------------------------------------------------------------
    deck.add_slide(PitchSlide(
        slide_number=11,
        title="The Ask",
        slide_type=SlideType.ASK,
        headline="We're raising to build the world's first community AI wealth platform.",
        bullets=[
            "Seeking: $500K seed round (adjust based on investor conversations)",
            "Use of funds:",
            "  → 40% Product development (mobile app, bot infrastructure)",
            "  → 25% Compliance & legal (entity setup, regulatory filings)",
            "  → 20% Marketing & community growth (influencer, referral launch)",
            "  → 15% Operations & team (key hires: CTO, Head of Compliance)",
            "Milestones this funding achieves:",
            "  → 10 live Wealth Hubs within 90 days",
            "  → 1,000 active members within 6 months",
            "  → $10M in hub treasury AUM within 12 months",
            "Also open to: strategic partnerships, early adopter deals, advisory roles",
        ],
        speaker_notes=(
            "Be specific about the ask. Investors respect founders who know "
            "exactly what they need and why. Show how this capital creates a "
            "clear path to the next funding milestone."
        ),
        visual_hint="Use-of-funds donut chart with milestone timeline",
        call_to_action="Invest in the people's financial system.",
    ))

    # ------------------------------------------------------------------
    # Slide 12 — Closing
    # ------------------------------------------------------------------
    deck.add_slide(PitchSlide(
        slide_number=12,
        title="The Vision",
        slide_type=SlideType.CLOSING,
        headline='"We\'re not replacing banks… we\'re replacing dependence."',
        bullets=[
            "✅ A community-owned investment platform — governed by the people",
            "✅ A passive income machine — powered by 7 AI bot categories",
            "✅ Multiple diversified revenue streams — resilient business model",
            "✅ Real and digital asset backing — Gold, Silver, Crypto, Real Estate",
            "✅ Scalable worldwide — every community can build a Wealth Hub",
            "",
            "DreamCo is not just a product — it's a movement.",
            "Join us in building the financial system the world deserves.",
        ],
        speaker_notes=(
            "End with emotion and conviction. Investors invest in people as much "
            "as products. Show your passion, your clarity, and your inevitability."
        ),
        visual_hint="Full-bleed hero image: diverse community celebrating financial freedom",
        call_to_action="Contact: invest@dreamco.com | dreamco.tech",
    ))

    return deck
