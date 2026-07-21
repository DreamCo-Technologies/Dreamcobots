"""
Bot Generator Bot — Template Engine Module

Dynamically builds a complete Python bot module (as source code) from a
fully-resolved Bot DNA dictionary.  The generated bot follows the standard
Dreamcobots GLOBAL AI SOURCES FLOW framework conventions.
"""

from __future__ import annotations

import re
import textwrap
from datetime import datetime, timezone
from typing import Optional


# ---------------------------------------------------------------------------
# Template Engine
# ---------------------------------------------------------------------------

class TemplateEngine:
    """
    Builds bot source code from a resolved Bot DNA dict.

    Usage::

        engine = TemplateEngine()
        dna = {
            "industry": "real_estate",
            "goal": "generate_leads",
            "bot_name": "real_estate_generate_leads_bot",
            "tools": ["google_maps", "zillow_scraper"],
            "monetization": ["subscriptions"],
            "resolved_tools": [...],
        }
        source = engine.build(dna)
        print(source)
    """

    def build(self, dna: dict) -> dict:
        """
        Generate a complete bot Python module from *dna*.

        Parameters
        ----------
        dna : dict
            Fully-resolved Bot DNA (output of :class:`ToolInjector.inject`).

        Returns
        -------
        dict
            ``{"bot_name": str, "filename": str, "source": str, "dna": dict}``
        """
        bot_name = dna.get("bot_name", "generated_bot")
        class_name = _to_class_name(bot_name)
        filename = f"{bot_name}.py"

        source = self._render_module(dna, class_name)
        return {
            "bot_name": bot_name,
            "class_name": class_name,
            "filename": filename,
            "source": source,
            "dna": dna,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Internal rendering
    # ------------------------------------------------------------------

    def _render_module(self, dna: dict, class_name: str) -> str:
        bot_name = dna.get("bot_name", "generated_bot")
        industry = dna.get("industry", "general")
        goal = dna.get("goal", "generate_leads")
        monetization = dna.get("monetization", [])
        resolved_tools = dna.get("resolved_tools", [])

        tool_stubs = "\n\n".join(
            textwrap.indent(t["stub"], "")
            for t in resolved_tools
        )

        tool_names = [t["name"] for t in resolved_tools]
        tool_list_repr = repr(tool_names)

        mono_list_repr = repr(monetization)

        lines = [
            '"""',
            f'{class_name} — Auto-generated bot.',
            "",
            f"Industry : {industry}",
            f"Goal     : {goal}",
            f"Tools    : {', '.join(tool_names) or 'none'}",
            f"Mono     : {', '.join(monetization) or 'none'}",
            "",
            "Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.",
            '"""',
            "",
            "from __future__ import annotations",
            "",
            "import sys",
            "import os",
            "",
            "sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))",
            "",
            "from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)",
            "",
        ]

        if tool_stubs:
            lines += [
                "# ---------------------------------------------------------------------------",
                "# Injected tool stubs",
                "# ---------------------------------------------------------------------------",
                "",
                tool_stubs,
                "",
            ]

        lines += [
            "# ---------------------------------------------------------------------------",
            "# Main bot class",
            "# ---------------------------------------------------------------------------",
            "",
            f"class {class_name}:",
            f'    """Auto-generated {industry} bot targeting goal: {goal}."""',
            "",
            f"    INDUSTRY = {industry!r}",
            f"    GOAL = {goal!r}",
            f"    TOOLS = {tool_list_repr}",
            f"    MONETIZATION = {mono_list_repr}",
            "",
            "    def __init__(self) -> None:",
            f"        self.name = {bot_name!r}",
            "        self.leads: list = []",
            "        self.revenue: float = 0.0",
            "        self._analytics: list = []",
            "",
            "    # ------------------------------------------------------------------",
            "    # Core actions",
            "    # ------------------------------------------------------------------",
            "",
            "    def run(self, **kwargs) -> dict:",
            '        """Execute the primary bot workflow."""',
            "        leads = self.collect_leads(**kwargs)",
            "        summary = self.get_summary()",
            "        return {'leads': leads, 'summary': summary}",
            "",
            "    def collect_leads(self, count: int = 10, **_kwargs) -> list:",
            '        """Collect leads using injected scraping tools."""',
        ]

        # Pick the primary scraping tool name for the stub call
        scraping_tools = [t["name"] for t in resolved_tools if t.get("category") == "scraping"]
        if scraping_tools:
            first_scraper = scraping_tools[0]
            lines.append(f"        # Primary tool: {first_scraper}")
            call_line = _scraper_call(first_scraper)
            lines += [
                call_line,
                "        self.leads.extend(raw)",
                "        return raw",
            ]
        else:
            lines += [
                "        # No scraping tools injected — override this method.",
                "        return []",
            ]

        lines += [
            "",
            "    def get_summary(self) -> dict:",
            '        """Return performance summary."""',
            "        return {",
            "            'bot_name': self.name,",
            "            'industry': self.INDUSTRY,",
            "            'goal': self.GOAL,",
            "            'total_leads': len(self.leads),",
            "            'revenue': self.revenue,",
            "        }",
            "",
            "    def chat(self, message: str) -> dict:",
            '        """Natural-language interface for BuddyAI routing."""',
            "        msg = message.lower()",
            "        if 'run' in msg or 'start' in msg:",
            "            return self.run()",
            "        if 'summary' in msg or 'stats' in msg:",
            "            return self.get_summary()",
            "        return {'message': f'{self.name} online. Say \"run\" to start.'}",
            "",
            "    def process(self, payload: dict) -> dict:",
            '        """GLOBAL AI SOURCES FLOW framework entry point."""',
            "        return self.chat(payload.get('command', ''))",
            "",
        ]

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_class_name(slug: str) -> str:
    """Convert a snake_case slug to a PascalCase class name."""
    return "".join(word.title() for word in re.split(r"[_\-\s]+", slug))


# Mapping of tool name → the generated collect_leads call line.
_SCRAPER_CALL_MAP: dict = {
    "google_maps":    "        raw = scrape_google_maps(query=self.INDUSTRY, location='United States', count=count)",
    "zillow_scraper": "        raw = scrape_zillow(location='United States', listing_type='for_sale', count=count)",
    "yelp_scraper":   "        raw = scrape_yelp(term=self.INDUSTRY, location='United States', limit=count)",
    "linkedin_scraper": "        raw = scrape_linkedin(search_query=self.INDUSTRY, count=count)",
    "mls_api":        "        raw = query_mls(zip_code='00000', status='Active')  # replace zip_code with target area",
    "twitter_scraper": "        raw = search_twitter(query=self.INDUSTRY, count=count)",
    "google_places":  "        raw = [get_place_details('ChIJN1t_tDeuEmsRUsoyG83frY4')]  # replace place_id with your target",
}


def _scraper_call(tool_name: str) -> str:
    """Return a collect_leads call line for *tool_name*."""
    return _SCRAPER_CALL_MAP.get(
        tool_name,
        f"        raw = []  # {tool_name}: override collect_leads() with your implementation",
    )
