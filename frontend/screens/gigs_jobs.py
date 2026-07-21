"""GigsJobsScreen — Fiverr gigs and remote job opportunities."""


class GigsJobsScreen:
    SCREEN_ID = "gigs_jobs"

    def __init__(self, gigs=None, jobs=None):
        self.gigs = gigs or []
        self.jobs = jobs or []

    def render(self) -> str:
        total_gig_revenue = sum(g.get("revenue", 0) for g in self.gigs)
        lines = [
            "=== DreamCo — Gigs & Jobs ===",
            f"Active Gigs: {len(self.gigs)}",
            f"Job Opportunities: {len(self.jobs)}",
            f"Gig Revenue: ${total_gig_revenue:.2f}",
        ]
        for g in self.gigs[:2]:
            lines.append(f"  [Gig] {g.get('title', '?')} — ${g.get('price', 0):.2f}/order")
        for j in self.jobs[:2]:
            lines.append(f"  [Job] {j.get('title', '?')} — ${j.get('rate', 0):.2f}/hr")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "screen": self.SCREEN_ID,
            "gigs": self.gigs,
            "jobs": self.jobs,
        }

    @classmethod
    def demo(cls) -> "GigsJobsScreen":
        return cls(
            gigs=[
                {"title": "AI Content Writing", "price": 50.0, "revenue": 500.0},
                {"title": "Python Bot Development", "price": 150.0, "revenue": 1500.0},
            ],
            jobs=[
                {"title": "Remote Data Entry", "rate": 18.0},
                {"title": "Virtual Assistant", "rate": 22.0},
            ],
        )
