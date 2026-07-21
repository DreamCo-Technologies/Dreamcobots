"""Lead Generator Bot — tier-aware business lead discovery and scoring."""
import sys, os
import math
import random
import csv
import io

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tiers import Tier, get_tier_config
from bots.lead_generator_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401

DATABASE = [
    {"id": "L001", "name": "Alice Johnson", "company": "TechNova Solutions", "title": "CEO", "industry": "tech", "location": "San Francisco, CA", "company_size": "mid", "email": "alice@technova.com", "phone": "415-555-0101", "website": "technova.com", "revenue_estimate": 5_000_000, "employees": 80, "score": random.randint(70, 100), "verified": True},
    {"id": "L002", "name": "Brian Kim", "company": "Apex Fintech", "title": "Founder", "industry": "finance", "location": "New York, NY", "company_size": "small", "email": "bkim@apexfintech.io", "phone": "212-555-0202", "website": "apexfintech.io", "revenue_estimate": 1_200_000, "employees": 15, "score": random.randint(60, 95), "verified": True},
    {"id": "L003", "name": "Carla Mendez", "company": "HealthBridge Inc", "title": "VP Operations", "industry": "healthcare", "location": "Austin, TX", "company_size": "large", "email": "cmendez@healthbridge.com", "phone": "512-555-0303", "website": "healthbridge.com", "revenue_estimate": 20_000_000, "employees": 350, "score": random.randint(65, 100), "verified": True},
    {"id": "L004", "name": "David Park", "company": "RetailEdge", "title": "Director of Procurement", "industry": "retail", "location": "Chicago, IL", "company_size": "mid", "email": "dpark@retailedge.com", "phone": "312-555-0404", "website": "retailedge.com", "revenue_estimate": 8_500_000, "employees": 120, "score": random.randint(50, 85), "verified": False},
    {"id": "L005", "name": "Eva Torres", "company": "ManufactPro", "title": "COO", "industry": "manufacturing", "location": "Detroit, MI", "company_size": "large", "email": "etorres@manufactpro.com", "phone": "313-555-0505", "website": "manufactpro.com", "revenue_estimate": 45_000_000, "employees": 600, "score": random.randint(70, 100), "verified": True},
    {"id": "L006", "name": "Frank Lee", "company": "Prime Realty Group", "title": "Managing Director", "industry": "real_estate", "location": "Miami, FL", "company_size": "mid", "email": "flee@primerealygroup.com", "phone": "305-555-0606", "website": "primerealty.com", "revenue_estimate": 12_000_000, "employees": 95, "score": random.randint(55, 90), "verified": True},
    {"id": "L007", "name": "Grace Nguyen", "company": "EduFuture Academy", "title": "Director", "industry": "education", "location": "Boston, MA", "company_size": "small", "email": "gnguyen@edufuture.org", "phone": "617-555-0707", "website": "edufuture.org", "revenue_estimate": 900_000, "employees": 22, "score": random.randint(40, 75), "verified": False},
    {"id": "L008", "name": "Henry Walsh", "company": "Walsh & Partners Law", "title": "Partner", "industry": "legal", "location": "Washington, DC", "company_size": "small", "email": "hwalsh@walshlaw.com", "phone": "202-555-0808", "website": "walshlaw.com", "revenue_estimate": 3_200_000, "employees": 30, "score": random.randint(60, 90), "verified": True},
    {"id": "L009", "name": "Isla Brown", "company": "StratEdge Consulting", "title": "VP Strategy", "industry": "consulting", "location": "Seattle, WA", "company_size": "mid", "email": "ibrown@stratedge.com", "phone": "206-555-0909", "website": "stratedge.com", "revenue_estimate": 7_000_000, "employees": 75, "score": random.randint(65, 95), "verified": True},
    {"id": "L010", "name": "James Carter", "company": "SwiftLogix", "title": "CEO", "industry": "logistics", "location": "Dallas, TX", "company_size": "large", "email": "jcarter@swiftlogix.com", "phone": "214-555-1010", "website": "swiftlogix.com", "revenue_estimate": 30_000_000, "employees": 450, "score": random.randint(70, 100), "verified": True},
    {"id": "L011", "name": "Karen Smith", "company": "CloudWave Tech", "title": "Founder", "industry": "tech", "location": "Austin, TX", "company_size": "small", "email": "ksmith@cloudwave.io", "phone": "512-555-1111", "website": "cloudwave.io", "revenue_estimate": 2_000_000, "employees": 25, "score": random.randint(55, 85), "verified": True},
    {"id": "L012", "name": "Liam Patel", "company": "CapitalFlow Finance", "title": "CFO", "industry": "finance", "location": "Charlotte, NC", "company_size": "mid", "email": "lpatel@capitalflow.com", "phone": "704-555-1212", "website": "capitalflow.com", "revenue_estimate": 6_500_000, "employees": 90, "score": random.randint(60, 95), "verified": True},
    {"id": "L013", "name": "Mia Roberts", "company": "CareFirst Medical", "title": "CEO", "industry": "healthcare", "location": "Philadelphia, PA", "company_size": "large", "email": "mroberts@carefirst.com", "phone": "215-555-1313", "website": "carefirst.com", "revenue_estimate": 55_000_000, "employees": 800, "score": random.randint(75, 100), "verified": True},
    {"id": "L014", "name": "Nathan Cruz", "company": "ShopSmart Retail", "title": "Head of Buying", "industry": "retail", "location": "Los Angeles, CA", "company_size": "large", "email": "ncruz@shopsmart.com", "phone": "323-555-1414", "website": "shopsmart.com", "revenue_estimate": 40_000_000, "employees": 500, "score": random.randint(60, 90), "verified": False},
    {"id": "L015", "name": "Olivia Grant", "company": "BuildCraft Manufacturing", "title": "VP Manufacturing", "industry": "manufacturing", "location": "Columbus, OH", "company_size": "mid", "email": "ogrant@buildcraft.com", "phone": "614-555-1515", "website": "buildcraft.com", "revenue_estimate": 15_000_000, "employees": 200, "score": random.randint(65, 95), "verified": True},
    {"id": "L016", "name": "Peter Stone", "company": "UrbanNest Real Estate", "title": "Founder", "industry": "real_estate", "location": "Denver, CO", "company_size": "small", "email": "pstone@urbannest.com", "phone": "720-555-1616", "website": "urbannest.com", "revenue_estimate": 1_800_000, "employees": 18, "score": random.randint(45, 80), "verified": False},
    {"id": "L017", "name": "Quinn Foster", "company": "BrightPath Learning", "title": "Director of Growth", "industry": "education", "location": "Minneapolis, MN", "company_size": "mid", "email": "qfoster@brightpath.com", "phone": "612-555-1717", "website": "brightpath.com", "revenue_estimate": 4_000_000, "employees": 55, "score": random.randint(50, 80), "verified": True},
    {"id": "L018", "name": "Rachel Moore", "company": "LexGroup Legal", "title": "Managing Partner", "industry": "legal", "location": "Atlanta, GA", "company_size": "mid", "email": "rmoore@lexgroup.com", "phone": "404-555-1818", "website": "lexgroup.com", "revenue_estimate": 9_000_000, "employees": 110, "score": random.randint(65, 95), "verified": True},
    {"id": "L019", "name": "Samuel Young", "company": "GrowthAxis Consulting", "title": "CEO", "industry": "consulting", "location": "Phoenix, AZ", "company_size": "small", "email": "syoung@growthaxis.com", "phone": "602-555-1919", "website": "growthaxis.com", "revenue_estimate": 2_500_000, "employees": 28, "score": random.randint(55, 88), "verified": True},
    {"id": "L020", "name": "Tanya Bell", "company": "FreightMaster Logistics", "title": "VP Logistics", "industry": "logistics", "location": "Memphis, TN", "company_size": "large", "email": "tbell@freightmaster.com", "phone": "901-555-2020", "website": "freightmaster.com", "revenue_estimate": 60_000_000, "employees": 950, "score": random.randint(70, 100), "verified": True},
    {"id": "L021", "name": "Umar Hassan", "company": "DataSync Tech", "title": "CTO", "industry": "tech", "location": "San Jose, CA", "company_size": "large", "email": "uhassan@datasync.com", "phone": "408-555-2121", "website": "datasync.com", "revenue_estimate": 25_000_000, "employees": 310, "score": random.randint(70, 100), "verified": True},
    {"id": "L022", "name": "Victoria Lane", "company": "InvestSmart Finance", "title": "Director", "industry": "finance", "location": "Boston, MA", "company_size": "mid", "email": "vlane@investsmart.com", "phone": "617-555-2222", "website": "investsmart.com", "revenue_estimate": 11_000_000, "employees": 130, "score": random.randint(60, 95), "verified": True},
    {"id": "L023", "name": "Will Torres", "company": "MedCore Health", "title": "Founder", "industry": "healthcare", "location": "Houston, TX", "company_size": "small", "email": "wtorres@medcore.io", "phone": "713-555-2323", "website": "medcore.io", "revenue_estimate": 1_500_000, "employees": 20, "score": random.randint(50, 80), "verified": False},
    {"id": "L024", "name": "Xena Powell", "company": "TrendShop", "title": "CEO", "industry": "retail", "location": "Nashville, TN", "company_size": "mid", "email": "xpowell@trendshop.com", "phone": "615-555-2424", "website": "trendshop.com", "revenue_estimate": 7_200_000, "employees": 100, "score": random.randint(55, 85), "verified": True},
    {"id": "L025", "name": "Yusuf Okafor", "company": "PrecisionParts Mfg", "title": "VP Sales", "industry": "manufacturing", "location": "Indianapolis, IN", "company_size": "large", "email": "yokafor@precisionparts.com", "phone": "317-555-2525", "website": "precisionparts.com", "revenue_estimate": 35_000_000, "employees": 520, "score": random.randint(65, 95), "verified": True},
    {"id": "L026", "name": "Zoe Harper", "company": "Skyline Properties", "title": "CEO", "industry": "real_estate", "location": "Portland, OR", "company_size": "mid", "email": "zharper@skylineprop.com", "phone": "503-555-2626", "website": "skylineprop.com", "revenue_estimate": 10_000_000, "employees": 85, "score": random.randint(60, 90), "verified": True},
    {"id": "L027", "name": "Aaron Reed", "company": "NextGen Ed", "title": "Co-Founder", "industry": "education", "location": "Salt Lake City, UT", "company_size": "small", "email": "areed@nextgened.com", "phone": "801-555-2727", "website": "nextgened.com", "revenue_estimate": 750_000, "employees": 12, "score": random.randint(35, 70), "verified": False},
    {"id": "L028", "name": "Bella Cruz", "company": "Apex Legal Group", "title": "Partner", "industry": "legal", "location": "San Diego, CA", "company_size": "mid", "email": "bcruz@apexlegal.com", "phone": "619-555-2828", "website": "apexlegal.com", "revenue_estimate": 5_500_000, "employees": 65, "score": random.randint(55, 88), "verified": True},
    {"id": "L029", "name": "Colin Ward", "company": "PeakAdvisors", "title": "Managing Director", "industry": "consulting", "location": "Kansas City, MO", "company_size": "large", "email": "cward@peakadvisors.com", "phone": "816-555-2929", "website": "peakadvisors.com", "revenue_estimate": 22_000_000, "employees": 280, "score": random.randint(65, 95), "verified": True},
    {"id": "L030", "name": "Dana Fox", "company": "QuickShip Logistics", "title": "COO", "industry": "logistics", "location": "Louisville, KY", "company_size": "mid", "email": "dfox@quickship.com", "phone": "502-555-3030", "website": "quickship.com", "revenue_estimate": 13_000_000, "employees": 175, "score": random.randint(60, 90), "verified": True},
    {"id": "L031", "name": "Ethan Moss", "company": "NovaSpark AI", "title": "CEO", "industry": "tech", "location": "Raleigh, NC", "company_size": "small", "email": "emoss@novaspark.ai", "phone": "919-555-3131", "website": "novaspark.ai", "revenue_estimate": 3_000_000, "employees": 35, "score": random.randint(65, 95), "verified": True},
    {"id": "L032", "name": "Faith Owens", "company": "WealthPath Capital", "title": "Founder", "industry": "finance", "location": "Tampa, FL", "company_size": "small", "email": "fowens@wealthpath.com", "phone": "813-555-3232", "website": "wealthpath.com", "revenue_estimate": 2_200_000, "employees": 20, "score": random.randint(50, 80), "verified": False},
]

TIER_LEAD_LIMITS = {
    Tier.FREE: 10,
    Tier.PRO: 100,
    Tier.ENTERPRISE: None,  # unlimited
}


class LeadGeneratorBot:
    """Tier-aware lead generator bot."""

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self.flow = GlobalAISourcesFlow(bot_name="LeadGeneratorBot")

    def search_leads(self, industry: str, location: str = None, company_size: str = None, limit: int = 10) -> list:
        results = [
            lead for lead in DATABASE
            if industry.lower() in lead["industry"].lower()
            and (location is None or location.lower() in lead["location"].lower())
            and (company_size is None or lead["company_size"] == company_size)
        ]

        tier_limit = TIER_LEAD_LIMITS[self.tier]
        if tier_limit is not None:
            effective_limit = min(limit, tier_limit)
        else:
            effective_limit = limit

        results = results[:effective_limit]

        if self.tier == Tier.FREE:
            masked = []
            for lead in results:
                masked_lead = {k: v for k, v in lead.items() if k not in ("phone", "verified")}
                masked_lead["email"] = "[UPGRADE TO PRO]"
                masked.append(masked_lead)
            results = masked

        return results

    def score_lead(self, lead_dict: dict) -> dict:
        score = 50
        reasoning = []

        size = lead_dict.get("company_size", "")
        if size == "large":
            score += 20
            reasoning.append("Large company — high budget potential")
        elif size == "mid":
            score += 10
            reasoning.append("Mid-size company — moderate budget potential")
        else:
            reasoning.append("Small company — limited budget")

        revenue = lead_dict.get("revenue_estimate", 0)
        if revenue >= 10_000_000:
            score += 15
            reasoning.append("Revenue ≥ $10M — strong financial capacity")
        elif revenue >= 1_000_000:
            score += 8
            reasoning.append("Revenue $1M–$10M — moderate financial capacity")

        employees = lead_dict.get("employees", 0)
        if employees >= 200:
            score += 10
            reasoning.append("200+ employees — established organisation")
        elif employees >= 50:
            score += 5
            reasoning.append("50–200 employees — growing organisation")

        title = lead_dict.get("title", "").lower()
        senior_keywords = ["ceo", "founder", "coo", "cto", "cfo", "vp", "director", "partner", "managing"]
        if any(kw in title for kw in senior_keywords):
            score += 15
            reasoning.append("Senior decision-maker title — high influence")
        else:
            reasoning.append("Non-executive title — may need escalation")

        score = max(0, min(100, score))

        if score >= 80:
            grade = "A"
            recommendation = "High-priority — contact immediately"
        elif score >= 65:
            grade = "B"
            recommendation = "Warm lead — schedule follow-up this week"
        elif score >= 45:
            grade = "C"
            recommendation = "Medium potential — nurture with content"
        else:
            grade = "D"
            recommendation = "Low priority — add to long-term nurture sequence"

        return {
            "score": score,
            "grade": grade,
            "reasoning": reasoning,
            "recommendation": recommendation,
        }

    def get_lead_details(self, lead_id: str) -> dict:
        if self.tier == Tier.FREE:
            raise PermissionError("Full lead details require PRO or ENTERPRISE tier")
        for lead in DATABASE:
            if lead["id"] == lead_id:
                return {**lead, "enrichment": {"linkedin_url": f"linkedin.com/in/{lead['name'].replace(' ', '-').lower()}", "last_updated": "2024-01-15"}}
        raise ValueError(f"Lead with id '{lead_id}' not found")

    def export_to_csv(self, leads_list: list) -> str:
        if self.tier == Tier.FREE:
            raise PermissionError("CSV export requires PRO or ENTERPRISE tier")
        if not leads_list:
            return ""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=leads_list[0].keys())
        writer.writeheader()
        writer.writerows(leads_list)
        return output.getvalue()

    def run(self):
        return self.flow.run_pipeline(
            raw_data={"domain": "lead_generation"},
            learning_method="supervised",
        )
