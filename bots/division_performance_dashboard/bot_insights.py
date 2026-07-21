# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class BotRecord:
    bot_id: str
    bot_name: str
    division_id: str
    tasks_completed: int = 0
    success_rate: float = 0.0
    revenue_generated: float = 0.0
    uptime_pct: float = 100.0

class BotInsights:
    def __init__(self):
        self._bots: dict = {}

    def register_bot(self, bot_id, bot_name, division_id) -> BotRecord:
        rec = BotRecord(bot_id=bot_id, bot_name=bot_name, division_id=division_id)
        self._bots[bot_id] = rec
        return rec

    def update_metrics(self, bot_id, tasks_completed, success_rate, revenue_generated, uptime_pct):
        if bot_id not in self._bots:
            raise KeyError(f"Bot '{bot_id}' not found")
        rec = self._bots[bot_id]
        rec.tasks_completed = tasks_completed
        rec.success_rate = success_rate
        rec.revenue_generated = revenue_generated
        rec.uptime_pct = uptime_pct

    def get_bot(self, bot_id: str) -> BotRecord:
        if bot_id not in self._bots:
            raise KeyError(f"Bot '{bot_id}' not found")
        return self._bots[bot_id]

    def get_top_bots(self, n: int = 5, metric: str = "revenue_generated") -> list:
        bots = list(self._bots.values())
        return sorted(bots, key=lambda b: getattr(b, metric, 0), reverse=True)[:n]

    def get_division_bots(self, division_id: str) -> list:
        return [b for b in self._bots.values() if b.division_id == division_id]

    def get_performance_report(self) -> dict:
        bots = list(self._bots.values())
        if not bots:
            return {"total_bots": 0, "avg_success_rate": 0.0, "total_revenue": 0.0, "avg_uptime": 0.0}
        return {
            "total_bots": len(bots),
            "avg_success_rate": sum(b.success_rate for b in bots) / len(bots),
            "total_revenue": sum(b.revenue_generated for b in bots),
            "avg_uptime": sum(b.uptime_pct for b in bots) / len(bots),
            "top_bots": [(b.bot_id, b.revenue_generated) for b in self.get_top_bots()],
        }

    def get_underperforming_bots(self, success_threshold: float = 0.7) -> list:
        return [b for b in self._bots.values() if b.success_rate < success_threshold]
