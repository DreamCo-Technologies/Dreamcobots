"""FiverrBot: automates SEO content gig generation and delivery."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py

import io
import logging
from typing import Dict, List, Optional

from core.bot_base import AbstractBotBase as BotBase
from core.crash_guard import crash_guard, safe_run
from core.monetization_hooks import MonetizationHooks
from core.revenue_engine import RevenueEngine


class FiverrBot(BotBase):
    """
    Automates SEO content gig generation on Fiverr.

    Responsibilities:
    - Generate SEO-focused content gigs based on provided keywords/topics.
    - Produce deliverables in Word-like text and PDF-compatible formats.
    - Record revenue events via RevenueEngine.
    - Track funnel stages via MonetizationHooks.
    """

    GIG_PRICE_USD = 25.0

    def __init__(
        self,
        revenue_engine: Optional[RevenueEngine] = None,
        monetization_hooks: Optional[MonetizationHooks] = None,
    ):
        super().__init__(name="FiverrBot")
        self.revenue_engine = revenue_engine or RevenueEngine()
        self.monetization_hooks = monetization_hooks or MonetizationHooks()
        self._pending_gigs: List[Dict] = []
        self._completed_gigs: List[Dict] = []

    # ------------------------------------------------------------------
    # BotBase lifecycle hooks
    # ------------------------------------------------------------------

    def on_start(self) -> None:
        self.logger.info("FiverrBot ready. Pending gigs: %d", len(self._pending_gigs))
        self.monetization_hooks.track("bot_started", {"bot": self.name})

    def on_stop(self) -> None:
        self.logger.info(
            "FiverrBot stopped. Completed gigs: %d | Revenue: $%.2f",
            len(self._completed_gigs),
            self.revenue_engine.total(),
        )
        self.monetization_hooks.track(
            "bot_stopped",
            {"completed": len(self._completed_gigs), "revenue": self.revenue_engine.total()},
        )

    def execute(self) -> None:
        """Process all pending gigs."""
        for gig in list(self._pending_gigs):
            with safe_run(f"gig:{gig.get('title', 'unknown')}"):
                result = self._process_gig(gig)
                if result:
                    self._completed_gigs.append(result)
        self._pending_gigs.clear()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_gig(self, title: str, keywords: List[str], word_count: int = 500) -> None:
        """Queue a new SEO content gig for processing."""
        self._pending_gigs.append(
            {"title": title, "keywords": keywords, "word_count": word_count}
        )
        self.logger.info("Gig queued: '%s' | keywords=%s", title, keywords)

    def get_completed_gigs(self) -> List[Dict]:
        """Return all completed gig results."""
        return list(self._completed_gigs)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @crash_guard
    def _process_gig(self, gig: Dict) -> Optional[Dict]:
        """Generate SEO content for a single gig and record revenue."""
        title = gig["title"]
        keywords = gig["keywords"]
        word_count = gig.get("word_count", 500)

        self.logger.info("Processing gig: '%s'", title)
        self.monetization_hooks.track("gig_started", {"title": title})

        content = self._generate_seo_content(title, keywords, word_count)
        txt_output = self._export_text(title, content)
        pdf_output = self._export_pdf(title, content)

        self.revenue_engine.record(source="fiverr_gig", amount=self.GIG_PRICE_USD)
        self.monetization_hooks.track(
            "gig_completed",
            {"title": title, "revenue": self.GIG_PRICE_USD},
        )

        result = {
            "title": title,
            "keywords": keywords,
            "content": content,
            "txt_output": txt_output,
            "pdf_output": pdf_output,
            "revenue": self.GIG_PRICE_USD,
        }
        self.logger.info("Gig completed: '%s' | $%.2f recorded", title, self.GIG_PRICE_USD)
        return result

    def _generate_seo_content(
        self, title: str, keywords: List[str], word_count: int
    ) -> str:
        """Generate structured SEO article content."""
        kw_list = ", ".join(keywords)
        intro = (
            f"# {title}\n\n"
            f"In today's competitive digital landscape, understanding {kw_list} "
            f"is essential for success. This article explores key insights to help "
            f"you leverage these opportunities effectively.\n\n"
        )
        body_paragraphs = []
        for i, kw in enumerate(keywords, start=1):
            body_paragraphs.append(
                f"## Section {i}: {kw.title()}\n\n"
                f"{kw.title()} plays a critical role in modern SEO strategies. "
                f"By optimising for {kw}, businesses can achieve higher search rankings "
                f"and attract targeted organic traffic.\n"
            )
        conclusion = (
            "\n## Conclusion\n\n"
            f"Incorporating {kw_list} into your content strategy is a proven path to "
            f"long-term digital growth. Start implementing these strategies today.\n"
        )
        content = intro + "\n".join(body_paragraphs) + conclusion
        # Pad content to approximate word_count
        current_words = len(content.split())
        if current_words < word_count:
            filler = (
                f"\nAdditionally, focusing on {kw_list} helps establish authority "
                f"and trust with your audience."
            )
            while len(content.split()) < word_count:
                content += filler
        return content

    def _export_text(self, title: str, content: str) -> str:
        """Return content as a plain-text (Word-compatible) string."""
        header = f"Document Title: {title}\n{'=' * 60}\n\n"
        return header + content

    def _export_pdf(self, title: str, content: str) -> bytes:
        """Return content as minimal PDF-compatible bytes (plain text encoded)."""
        pdf_text = f"%PDF-1.4\n%DreamCo FiverrBot\n%Title: {title}\n\n{content}\n%%EOF"
        return pdf_text.encode("utf-8")
