# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class SkillPack:
    pack_id: str
    name: str
    description: str
    plugins: list
    price_usd: float
    industry: str

class SkillPackRegistry:
    def __init__(self):
        self._packs: dict = {}
        self._init_packs()

    def _init_packs(self):
        defaults = [
            SkillPack("ecommerce_pack", "E-Commerce Pack",
                      "Complete e-commerce toolkit for online sellers",
                      ["inventory_manager", "deal_alert_pro", "receipt_scanner_pro", "coupon_stacker"],
                      19.0, "e-commerce"),
            SkillPack("marketing_pack", "Marketing Pack",
                      "Boost your marketing with AI-powered tools",
                      ["seo_optimizer", "deal_alert_pro"],
                      15.0, "marketing"),
            SkillPack("finance_pack", "Finance Pack",
                      "Track crypto and calculate flip profits",
                      ["crypto_price_tracker", "flip_profit_calculator"],
                      19.0, "finance"),
            SkillPack("logistics_pack", "Logistics Pack",
                      "Optimize routes and manage inventory",
                      ["route_optimizer", "inventory_manager"],
                      15.0, "logistics"),
            SkillPack("integration_pack", "Integration Pack",
                      "Connect to Slack, Telegram, and Discord",
                      ["slack_workspace_plugin", "telegram_bot_connector", "discord_server_bot"],
                      25.0, "integration"),
            SkillPack("ai_performance_pack", "AI Performance Pack",
                      "Route AI models and track performance analytics",
                      ["ai_model_router"],
                      29.0, "ai"),
        ]
        for p in defaults:
            self._packs[p.pack_id] = p

    def get_pack(self, pack_id: str) -> SkillPack:
        if pack_id not in self._packs:
            raise KeyError(f"Skill pack '{pack_id}' not found")
        return self._packs[pack_id]

    def list_packs(self, industry: str = None) -> list:
        packs = list(self._packs.values())
        if industry is not None:
            packs = [p for p in packs if p.industry == industry]
        return packs

    def get_pack_value(self, pack_id: str, individual_prices: dict) -> float:
        pack = self.get_pack(pack_id)
        total_individual = sum(individual_prices.get(pid, 0) for pid in pack.plugins)
        return total_individual - pack.price_usd
