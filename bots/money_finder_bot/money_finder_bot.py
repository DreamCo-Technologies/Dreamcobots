"""Money Finder Bot — tier-aware unclaimed funds and benefits finder."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.money_finder_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401


class MoneyFinderBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class MoneyFinderBot:
    """Tier-aware unclaimed funds, government benefits, and cashback finder."""

    US_STATES = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    ]
    INTERNATIONAL_SOURCES = ["Canada", "UK", "Australia", "Germany", "France"]

    MOCK_UNCLAIMED = [
        {"source": "Dormant Bank Account", "amount_usd": 324.50, "holder": "State Treasury", "years_dormant": 3, "claim_difficulty": "Easy"},
        {"source": "Insurance Policy Refund", "amount_usd": 812.00, "holder": "State Insurance Fund", "years_dormant": 5, "claim_difficulty": "Medium"},
        {"source": "Utility Deposit", "amount_usd": 145.00, "holder": "Utility Company", "years_dormant": 2, "claim_difficulty": "Easy"},
        {"source": "Payroll Uncashed Check", "amount_usd": 220.75, "holder": "Former Employer", "years_dormant": 4, "claim_difficulty": "Easy"},
        {"source": "Refund Check", "amount_usd": 67.20, "holder": "Retailer", "years_dormant": 1, "claim_difficulty": "Easy"},
        {"source": "Stock Dividend", "amount_usd": 1205.00, "holder": "DTCC", "years_dormant": 7, "claim_difficulty": "Hard"},
        {"source": "Tax Refund Unclaimed", "amount_usd": 450.00, "holder": "IRS / State", "years_dormant": 3, "claim_difficulty": "Medium"},
        {"source": "Pension Benefit", "amount_usd": 3400.00, "holder": "PBGC", "years_dormant": 10, "claim_difficulty": "Hard"},
        {"source": "Court Settlement", "amount_usd": 180.00, "holder": "Court Registry", "years_dormant": 2, "claim_difficulty": "Medium"},
        {"source": "Security Deposit", "amount_usd": 950.00, "holder": "Former Landlord", "years_dormant": 6, "claim_difficulty": "Hard"},
    ]

    GOVERNMENT_PROGRAMS = [
        {"program": "SNAP (Food Stamps)", "agency": "USDA", "typical_monthly_usd": 281, "eligibility_criteria": ["income_below_130pct_poverty", "household_size"]},
        {"program": "Medicaid", "agency": "CMS", "typical_monthly_usd": 600, "eligibility_criteria": ["income_below_138pct_poverty", "US_resident"]},
        {"program": "EITC (Earned Income Tax Credit)", "agency": "IRS", "typical_monthly_usd": 250, "eligibility_criteria": ["earned_income", "income_limit", "filing_taxes"]},
        {"program": "LIHEAP (Energy Assistance)", "agency": "HHS", "typical_monthly_usd": 150, "eligibility_criteria": ["income_below_150pct_poverty", "utility_bills"]},
        {"program": "WIC", "agency": "USDA", "typical_monthly_usd": 200, "eligibility_criteria": ["pregnant_or_infant", "income_below_185pct_poverty"]},
        {"program": "Section 8 Housing", "agency": "HUD", "typical_monthly_usd": 900, "eligibility_criteria": ["income_below_50pct_median", "US_resident"]},
        {"program": "SSI (Supplemental Security Income)", "agency": "SSA", "typical_monthly_usd": 914, "eligibility_criteria": ["age_65_plus_or_disabled", "limited_income"]},
        {"program": "Child Care Subsidy", "agency": "HHS", "typical_monthly_usd": 500, "eligibility_criteria": ["working_parent", "child_under_13", "income_limit"]},
        {"program": "Unemployment Insurance", "agency": "DOL", "typical_monthly_usd": 450, "eligibility_criteria": ["recently_unemployed", "meet_work_history"]},
        {"program": "Medicare Extra Help", "agency": "SSA", "typical_monthly_usd": 120, "eligibility_criteria": ["age_65_plus", "income_below_150pct_poverty"]},
    ]

    CASHBACK_OFFERS = [
        {"source": "Rakuten", "category": "Online Shopping", "avg_cashback_pct": 6.0, "max_cashback_usd": 500, "platform": "Browser Extension"},
        {"source": "Ibotta", "category": "Groceries", "avg_cashback_pct": 3.5, "max_cashback_usd": 200, "platform": "Mobile App"},
        {"source": "Honey", "category": "Coupon Codes", "avg_cashback_pct": 5.0, "max_cashback_usd": 300, "platform": "Browser Extension"},
        {"source": "Fetch Rewards", "category": "Receipts", "avg_cashback_pct": 2.0, "max_cashback_usd": 150, "platform": "Mobile App"},
        {"source": "Credit Card Sign-up Bonuses", "category": "Credit Cards", "avg_cashback_pct": 0, "bonus_usd": 200, "platform": "Multiple Banks"},
        {"source": "Upside", "category": "Gas", "avg_cashback_pct": 8.0, "max_cashback_usd": 100, "platform": "Mobile App"},
        {"source": "Dosh", "category": "Dining / Hotels", "avg_cashback_pct": 4.0, "max_cashback_usd": 250, "platform": "Mobile App"},
        {"source": "TopCashback", "category": "Insurance", "avg_cashback_pct": 7.5, "max_cashback_usd": 400, "platform": "Web"},
    ]

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._searched_states: list = []

    def scan_unclaimed_funds(self, name: str, state: str) -> list:
        """Return list of potentially unclaimed funds for a name in a state."""
        state_upper = state.upper()
        if self.tier == Tier.FREE:
            if len(self._searched_states) >= 1 and state_upper not in self._searched_states:
                raise MoneyFinderBotTierError(
                    f"FREE tier limited to 1 state. Already searched '{self._searched_states[0]}'. "
                    "Upgrade to PRO to search all US states."
                )
        elif self.tier not in (Tier.PRO, Tier.ENTERPRISE):
            raise MoneyFinderBotTierError(f"Unsupported tier: {self.tier}")

        if state_upper in self.INTERNATIONAL_SOURCES and self.tier != Tier.ENTERPRISE:
            raise MoneyFinderBotTierError("International search requires ENTERPRISE tier.")

        if state_upper not in self._searched_states:
            self._searched_states.append(state_upper)

        count = 2 if self.tier == Tier.FREE else (5 if self.tier == Tier.PRO else len(self.MOCK_UNCLAIMED))
        return [
            {**record, "name": name, "state": state_upper, "tier": self.tier.value}
            for record in self.MOCK_UNCLAIMED[:count]
        ]

    def check_government_benefits(self, profile: dict) -> list:
        """Return eligible government benefits based on profile."""
        if self.tier == Tier.FREE:
            raise MoneyFinderBotTierError("Government benefits checker requires PRO or ENTERPRISE tier.")
        income = profile.get("annual_income_usd", 50000)
        household_size = profile.get("household_size", 1)
        poverty_line = 14580 + (household_size - 1) * 5140
        eligible = []
        for prog in self.GOVERNMENT_PROGRAMS:
            if income < poverty_line * 1.85:
                eligible.append({
                    **prog,
                    "likely_eligible": income < poverty_line * 1.5,
                    "estimated_annual_benefit_usd": prog["typical_monthly_usd"] * 12,
                    "tier": self.tier.value,
                })
        return eligible

    def find_cashback_opportunities(self) -> list:
        """Return cashback and rebate opportunities."""
        count = 3 if self.tier == Tier.FREE else len(self.CASHBACK_OFFERS)
        return [
            {**offer, "tier": self.tier.value}
            for offer in self.CASHBACK_OFFERS[:count]
        ]

    def generate_recovery_report(self, name: str) -> dict:
        """Generate a comprehensive money recovery report."""
        unclaimed = self.MOCK_UNCLAIMED[:3] if self.tier == Tier.FREE else self.MOCK_UNCLAIMED
        total_unclaimed = sum(r["amount_usd"] for r in unclaimed)
        cashback = self.find_cashback_opportunities()
        annual_cashback = sum(o.get("max_cashback_usd", 0) for o in cashback)

        report = {
            "name": name,
            "unclaimed_funds_count": len(unclaimed),
            "total_unclaimed_usd": round(total_unclaimed, 2),
            "unclaimed_records": unclaimed,
            "cashback_opportunities": cashback,
            "estimated_annual_cashback_usd": annual_cashback,
            "total_recovery_potential_usd": round(total_unclaimed + annual_cashback, 2),
            "tier": self.tier.value,
            "features": BOT_FEATURES[self.tier.value],
        }
        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            report["government_benefits_note"] = "Run check_government_benefits() with your profile for benefit eligibility."
        if self.tier == Tier.ENTERPRISE:
            report["international_search"] = {"sources": self.INTERNATIONAL_SOURCES, "available": True}
            report["automated_recovery"] = True
        return report

    def describe_tier(self) -> str:
        info = get_bot_tier_info(self.tier)
        lines = [
            f"=== {info['name']} Money Finder Bot Tier ===",
            f"Price: ${info['price_usd_monthly']:.2f}/month",
            f"Support: {info['support_level']}",
            "Features:",
        ]
        for f in info["features"]:
            lines.append(f"  \u2713 {f}")
        output = "\n".join(lines)
        print(output)
        return output
