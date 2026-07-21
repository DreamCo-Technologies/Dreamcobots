"""
Auto-Bot Factory — Code Generator Module

Builds production-ready Python bot modules from an optimized feature list.
Generates modular components: logic, APIs, monetization, and tracking.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

import re
import textwrap
from datetime import datetime, timezone
from typing import List, Optional

from bots.bot_generator.request_interface import BotRequest


# ---------------------------------------------------------------------------
# Code Generator
# ---------------------------------------------------------------------------

class CodeGeneratorError(Exception):
    """Raised when code generation fails."""


def _slugify(text: str) -> str:
    """Convert *text* to a snake_case Python identifier."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "bot"


class CodeGenerator:
    """
    DreamCo Auto-Bot Factory — Code Generator.

    Builds scalable, production-ready Python bot source code from an
    optimized feature list produced by :class:`FeatureOptimizer`.

    Generated bots follow the standard Dreamcobots GLOBAL AI SOURCES FLOW
    framework conventions and include:
    - Core bot logic module
    - Monetization / pricing module
    - Tracking / analytics module
    - README stub

    Usage::

        generator = CodeGenerator()
        result = generator.generate(request, optimized_features)
        print(result["modules"]["bot_main"])
    """

    TIER_PRICING = {
        "basic": 99,
        "pro": 299,
        "enterprise": None,  # usage-based
    }

    def __init__(self, output_dir: Optional[str] = None) -> None:
        if output_dir is None:
            output_dir = os.path.join(
                os.path.dirname(__file__), "..", "..", "bots"
            )
        self.output_dir = os.path.abspath(output_dir)
        self._generation_log: List[dict] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        request: BotRequest,
        optimized_features: Optional[List[str]] = None,
        write_files: bool = False,
    ) -> dict:
        """
        Generate bot source code from *request*.

        Parameters
        ----------
        request : BotRequest
            Validated bot creation request.
        optimized_features : list[str], optional
            Prioritized feature list from FeatureOptimizer.  When omitted
            the request's own feature list is used.
        write_files : bool
            When ``True``, write the generated modules to disk under
            ``output_dir/<bot_name>/``.

        Returns
        -------
        dict
            Keys: ``bot_name``, ``modules``, ``file_paths`` (if written),
            ``generated_at``.
        """
        features = optimized_features or request.features
        bot_name = _slugify(request.bot_name or request.category)
        class_name = "".join(w.title() for w in bot_name.split("_"))

        modules = {
            "bot_main": self._render_main(bot_name, class_name, request, features),
            "monetization": self._render_monetization(bot_name, class_name),
            "tracking": self._render_tracking(bot_name, class_name),
            "readme": self._render_readme(bot_name, request, features),
        }

        result: dict = {
            "bot_name": bot_name,
            "class_name": class_name,
            "category": request.category,
            "features": features,
            "modules": modules,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        if write_files:
            result["file_paths"] = self._write_to_disk(bot_name, modules)

        entry = {
            "bot_name": bot_name,
            "category": request.category,
            "feature_count": len(features),
            "generated_at": result["generated_at"],
            "written": write_files,
        }
        self._generation_log.append(entry)
        return result

    def get_generation_log(self) -> List[dict]:
        """Return the history of generated bots."""
        return list(self._generation_log)

    def run(self) -> str:
        """GLOBAL AI SOURCES FLOW framework entry point."""
        return (
            f"CodeGenerator active — "
            f"{len(self._generation_log)} bot(s) generated so far."
        )

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------

    def _render_main(
        self,
        bot_name: str,
        class_name: str,
        request: BotRequest,
        features: List[str],
    ) -> str:
        feature_list = "\n".join(f"    # - {f}" for f in features)
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return textwrap.dedent(f'''\
            """
            {class_name} — Auto-generated by DreamCo Auto-Bot Factory
            Category : {request.category}
            Purpose  : {request.purpose}
            Audience : {request.target_audience}
            Created  : {now}

            Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
            """

            from __future__ import annotations

            import sys
            import os

            sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

            from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

            from bots.{bot_name}.monetization import Monetization
            from bots.{bot_name}.tracking import Tracker


            class {class_name}:
                """
                {request.purpose}

                Optimized features:
            {feature_list}
                """

                MAX_BOTS = 200
                MAX_MESSAGES_PER_CYCLE = 10

                def __init__(self, tier: str = "basic") -> None:
                    self.tier = tier
                    self.monetization = Monetization(tier=tier)
                    self.tracker = Tracker(bot_name="{bot_name}")
                    self._active = True

                def run(self) -> str:
                    """GLOBAL AI SOURCES FLOW framework entry point."""
                    self.tracker.record_run()
                    revenue = self.monetization.get_revenue()
                    return (
                        f"{class_name} running on tier={{self.tier}}. "
                        f"Revenue tracked: ${{revenue:.2f}}"
                    )

                def execute_cycle(self) -> dict:
                    """Run one operational cycle."""
                    self.tracker.record_run()
                    return {{
                        "bot": "{bot_name}",
                        "tier": self.tier,
                        "status": "cycle_complete",
                        "revenue": self.monetization.get_revenue(),
                    }}

                def heal(self) -> str:
                    """Self-healing: reset internal state after a failure."""
                    self._active = True
                    return "healed"

                def get_status(self) -> dict:
                    """Return current bot health and performance metrics."""
                    return {{
                        "bot_name": "{bot_name}",
                        "tier": self.tier,
                        "active": self._active,
                        "runs": self.tracker.run_count,
                        "revenue_usd": self.monetization.get_revenue(),
                    }}
            ''')

    def _render_monetization(self, bot_name: str, class_name: str) -> str:
        return textwrap.dedent(f'''\
            """
            {class_name} — Monetization Module (GLOBAL AI SOURCES FLOW)

            Tiered pricing: basic $99/mo, pro $299/mo, enterprise usage-based.
            Tracks billed activities and provides revenue reporting.
            """

            from __future__ import annotations


            TIER_PRICES = {{
                "basic": 99.0,
                "pro": 299.0,
                "enterprise": 0.0,  # usage-based
            }}

            USAGE_RATE_USD = 0.05  # per billable action for enterprise tier


            class Monetization:
                """In-app billing and revenue tracking."""

                def __init__(self, tier: str = "basic") -> None:
                    self.tier = tier
                    self._billable_actions: int = 0
                    self._subscriptions: int = 0

                def add_subscription(self) -> float:
                    """Record a new subscription and return the charge amount."""
                    self._subscriptions += 1
                    return TIER_PRICES.get(self.tier, 0.0)

                def record_action(self) -> float:
                    """Record one billable action and return the charge amount."""
                    self._billable_actions += 1
                    if self.tier == "enterprise":
                        return USAGE_RATE_USD
                    return 0.0

                def get_revenue(self) -> float:
                    """Return total tracked revenue in USD."""
                    base = TIER_PRICES.get(self.tier, 0.0) * self._subscriptions
                    usage = self._billable_actions * USAGE_RATE_USD if self.tier == "enterprise" else 0.0
                    return round(base + usage, 2)

                def get_report(self) -> dict:
                    """Return a structured revenue report."""
                    return {{
                        "tier": self.tier,
                        "subscriptions": self._subscriptions,
                        "billable_actions": self._billable_actions,
                        "total_revenue_usd": self.get_revenue(),
                        "monthly_price_usd": TIER_PRICES.get(self.tier, 0.0),
                    }}
            ''')

    def _render_tracking(self, bot_name: str, class_name: str) -> str:
        return textwrap.dedent(f'''\
            """
            {class_name} — Tracking Module (GLOBAL AI SOURCES FLOW)

            Records bot run history, performance metrics, and errors.
            """

            from __future__ import annotations

            from datetime import datetime, timezone


            class Tracker:
                """Lightweight in-app performance and run tracker."""

                def __init__(self, bot_name: str = "{bot_name}") -> None:
                    self.bot_name = bot_name
                    self.run_count: int = 0
                    self._errors: list = []
                    self._log: list = []

                def record_run(self) -> None:
                    """Log one completed run."""
                    self.run_count += 1
                    self._log.append({{
                        "run": self.run_count,
                        "ts": datetime.now(timezone.utc).isoformat(),
                    }})

                def record_error(self, error: str) -> None:
                    """Log an error."""
                    self._errors.append({{
                        "error": error,
                        "ts": datetime.now(timezone.utc).isoformat(),
                    }})

                def get_summary(self) -> dict:
                    """Return a performance summary."""
                    return {{
                        "bot_name": self.bot_name,
                        "total_runs": self.run_count,
                        "total_errors": len(self._errors),
                        "last_run": self._log[-1]["ts"] if self._log else None,
                    }}
            ''')

    def _render_readme(
        self,
        bot_name: str,
        request: BotRequest,
        features: List[str],
    ) -> str:
        feature_md = "\n".join(f"- {f}" for f in features)
        return textwrap.dedent(f"""\
            # {bot_name}

            **Category:** {request.category}
            **Purpose:** {request.purpose}
            **Target Audience:** {request.target_audience}
            **Pricing:** {request.pricing_model}

            ## Features

            {feature_md}

            ## Usage

            ```python
            from bots.{bot_name}.{bot_name} import {"".join(w.title() for w in bot_name.split("_"))}
            bot = {"".join(w.title() for w in bot_name.split("_"))}(tier="pro")
            print(bot.run())
            ```

            ## Tiers

            | Tier       | Price       |
            |------------|-------------|
            | Basic      | $99/month   |
            | Pro        | $299/month  |
            | Enterprise | Usage-based |

            *Auto-generated by the DreamCo Auto-Bot Factory.*
            """)

    # ------------------------------------------------------------------
    # File I/O
    # ------------------------------------------------------------------

    def _write_to_disk(self, bot_name: str, modules: dict) -> dict:
        bot_dir = os.path.join(self.output_dir, bot_name)
        os.makedirs(bot_dir, exist_ok=True)
        paths: dict = {}

        file_map = {
            "bot_main": f"{bot_name}.py",
            "monetization": "monetization.py",
            "tracking": "tracking.py",
            "readme": "README.md",
        }

        for key, filename in file_map.items():
            path = os.path.join(bot_dir, filename)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(modules[key])
            paths[key] = path

        # Write __init__.py
        init_path = os.path.join(bot_dir, "__init__.py")
        with open(init_path, "w", encoding="utf-8") as fh:
            fh.write(f'"""Auto-generated {bot_name} package."""\n')
        paths["init"] = init_path

        return paths
