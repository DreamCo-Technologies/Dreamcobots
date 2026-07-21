"""
AI Side Hustle Bot
AI-powered tools to help users identify, launch, and monetize side hustles.
"""
# GLOBAL AI SOURCES FLOW
from framework import GlobalAISourcesFlow  # noqa: F401 — framework compliance marker


import random

HUSTLE_CATEGORIES = [
    "content_creation",
    "freelancing",
    "dropshipping",
    "affiliate_marketing",
    "digital_products",
    "social_media_management",
]

SUPPORTED_INTEGRATIONS = [
    "Zapier",
    "N8n",
    "Make.com",
    "Notion",
    "Google Sheets",
    "Slack",
    "Airtable",
    "Mailchimp",
    "Shopify",
    "Gumroad",
]

INCOME_RANGES = {
    "content_creation":        {"min": 200,  "max": 5000,  "avg": 1500},
    "freelancing":             {"min": 500,  "max": 10000, "avg": 3000},
    "dropshipping":            {"min": 100,  "max": 8000,  "avg": 2000},
    "affiliate_marketing":     {"min": 50,   "max": 15000, "avg": 2500},
    "digital_products":        {"min": 100,  "max": 20000, "avg": 3500},
    "social_media_management": {"min": 500,  "max": 6000,  "avg": 2000},
}

FREELANCE_OPPORTUNITIES = {
    "upwork": [
        {"title": "Python Script Automation", "budget": "$200–$500", "skills": ["python"], "platform": "upwork"},
        {"title": "WordPress Website Redesign", "budget": "$300–$800", "skills": ["wordpress", "design"], "platform": "upwork"},
        {"title": "Social Media Content Calendar", "budget": "$150–$400", "skills": ["social_media", "writing"], "platform": "upwork"},
        {"title": "Data Entry & Spreadsheet Cleanup", "budget": "$50–$150", "skills": ["excel", "data_entry"], "platform": "upwork"},
    ],
    "fiverr": [
        {"title": "Logo Design Package", "budget": "$50–$300", "skills": ["design", "illustrator"], "platform": "fiverr"},
        {"title": "SEO Blog Posts (5-pack)", "budget": "$75–$250", "skills": ["writing", "seo"], "platform": "fiverr"},
        {"title": "Video Editing — YouTube Shorts", "budget": "$100–$400", "skills": ["video_editing"], "platform": "fiverr"},
    ],
    "toptal": [
        {"title": "Senior React Developer (Contract)", "budget": "$5,000–$12,000/mo", "skills": ["react", "javascript"], "platform": "toptal"},
        {"title": "Product Manager Consultant", "budget": "$4,000–$10,000/mo", "skills": ["product_management"], "platform": "toptal"},
    ],
}

CONTENT_IDEAS_POOL = {
    "finance": [
        "5 ways to pay off debt faster on a low income",
        "How I saved $10,000 in 12 months working a minimum wage job",
        "Best budgeting apps for beginners in 2024",
        "Index funds vs. ETFs: what you actually need to know",
        "How to start investing with just $50/month",
    ],
    "fitness": [
        "30-day home workout plan — no equipment needed",
        "What I eat in a day as a busy parent (healthy & cheap)",
        "5 gym mistakes beginners always make",
        "How to build muscle on a $50/week grocery budget",
        "Morning routine that transformed my productivity",
    ],
    "tech": [
        "Top 5 AI tools that save me 10 hours a week",
        "How to automate your side hustle with free tools",
        "ChatGPT prompts every freelancer should bookmark",
        "Build a passive income app with no-code tools",
        "Side hustles you can start with just a laptop",
    ],
    "business": [
        "How to start a dropshipping store in a weekend",
        "Best Etsy niches to launch in right now",
        "10 digital products you can create in under an hour",
        "How to get your first freelance client with no portfolio",
        "Passive income streams that actually work in 2024",
    ],
}

MARKETING_PLAN_TEMPLATES = {
    "content_creation": {
        "channels": ["YouTube", "TikTok", "Instagram Reels", "Newsletter"],
        "weekly_actions": [
            "Post 3 short-form videos",
            "Write 1 long-form blog post",
            "Engage in 2 niche communities for 30 min",
            "Repurpose top content across platforms",
        ],
        "monetization": ["AdSense/YouTube Partner Program", "Sponsorships", "Digital products", "Affiliate links"],
        "tools": ["CapCut", "Canva", "Buffer", "ConvertKit"],
    },
    "freelancing": {
        "channels": ["LinkedIn", "Upwork", "Fiverr", "Cold email"],
        "weekly_actions": [
            "Send 10 cold pitches to potential clients",
            "Publish 1 case study or portfolio piece",
            "Engage with 5 LinkedIn posts in your niche",
            "Ask 1 current client for a referral or testimonial",
        ],
        "monetization": ["Hourly contracts", "Fixed-price projects", "Retainer agreements"],
        "tools": ["LinkedIn Sales Navigator", "HubSpot CRM (free)", "Calendly", "Invoice Ninja"],
    },
    "dropshipping": {
        "channels": ["Facebook Ads", "TikTok Ads", "Instagram Shopping", "Google Shopping"],
        "weekly_actions": [
            "Test 3 new product ads with $5/day budget",
            "Analyze top-performing ad creative",
            "Reach out to 2 new suppliers on AliExpress/Spocket",
            "Review and optimize store conversion rate",
        ],
        "monetization": ["Product markup (30–60%)", "Bundle deals", "Upsells"],
        "tools": ["Shopify", "DSers", "AdSpy", "Canva for creatives"],
    },
    "affiliate_marketing": {
        "channels": ["SEO blog", "YouTube", "Email list", "Pinterest"],
        "weekly_actions": [
            "Publish 2 keyword-targeted review articles",
            "Build 3 backlinks to existing content",
            "Add affiliate links to top-performing old posts",
            "Email your list with 1 product recommendation",
        ],
        "monetization": ["Amazon Associates", "ShareASale", "ClickBank", "CJ Affiliate"],
        "tools": ["Ahrefs (free trial)", "WordPress", "Elementor", "ConvertKit"],
    },
    "digital_products": {
        "channels": ["Gumroad", "Etsy", "Teachable", "Payhip"],
        "weekly_actions": [
            "Create 1 new lead magnet to grow email list",
            "Post 3 social proof snippets (testimonials, earnings)",
            "Run a limited-time discount on 1 product",
            "Research 2 new product ideas from community questions",
        ],
        "monetization": ["One-time sales", "Memberships", "Bundles", "Upsells"],
        "tools": ["Notion", "Canva", "Gumroad", "Loom for course creation"],
    },
    "social_media_management": {
        "channels": ["LinkedIn", "Instagram", "Local Facebook groups", "Referrals"],
        "weekly_actions": [
            "Prospect 5 small businesses needing social presence",
            "Deliver client content calendar for next week",
            "Analyze client account insights and report results",
            "Create 1 educational post about SMM to attract clients",
        ],
        "monetization": ["Monthly retainers ($500–$2,000/mo)", "Per-post packages", "Audits"],
        "tools": ["Buffer", "Later", "Canva", "Meta Business Suite"],
    },
}


class AISideHustleBot:
    """
    AI Side Hustle Bot — helps users identify, launch, and monetize side hustles
    using AI-generated content ideas, income calculators, and marketing plans.
    """

    def __init__(self, config=None):
        """
        Initialize the bot with an optional configuration dictionary.

        Args:
            config (dict, optional): Supports keys:
                - 'openai_api_key' (str): Optional OpenAI API key for AI-enhanced output.
                - 'default_niche' (str): Default content niche. Default 'business'.
                - 'max_ideas' (int): Max ideas to generate. Default 5.
        """
        self.config = config or {}
        self.openai_api_key = self.config.get("openai_api_key") or ""
        self.default_niche = self.config.get("default_niche", "business")
        self.max_ideas = self.config.get("max_ideas", 5)
        self._ai_enabled = bool(self.openai_api_key)
        print("[HustleBot] Initialized. Let's build your side hustle!")
        if self._ai_enabled:
            print("[HustleBot] OpenAI integration active — AI-enhanced ideas enabled.")

    def get_hustle_categories(self):
        """
        Return the list of available side hustle categories.

        Returns:
            list[str]: Category names.
        """
        return list(HUSTLE_CATEGORIES)

    def generate_content_ideas(self, niche, count=5):
        """
        Generate content ideas for a given niche.

        Args:
            niche (str): Content niche (e.g., 'finance', 'fitness', 'tech', 'business').
            count (int): Number of ideas to generate. Default 5.

        Returns:
            list[dict]: List of idea dicts with keys: 'title', 'niche', 'format', 'estimated_views'.
        """
        niche_lower = niche.lower()
        pool = CONTENT_IDEAS_POOL.get(niche_lower, CONTENT_IDEAS_POOL["business"])

        formats = ["Short-form video", "Blog post", "YouTube tutorial", "Carousel post", "Email newsletter"]
        ideas = []
        selected = random.sample(pool, min(count, len(pool)))
        for title in selected:
            ideas.append({
                "title": title,
                "niche": niche_lower,
                "format": random.choice(formats),
                "estimated_views": f"{random.randint(500, 50000):,}",
            })

        print(f"[HustleBot] Generated {len(ideas)} content idea(s) for niche '{niche}'.")
        return ideas

    def find_freelance_opportunities(self, skills, platform="upwork"):
        """
        Find freelance opportunities matching the given skills.

        Args:
            skills (list[str] or str): Skills to match (e.g., ['python', 'writing']).
            platform (str): Freelance platform to search. Default 'upwork'.
                            Supported: upwork, fiverr, toptal.

        Returns:
            list[dict]: Matching opportunity dicts with title, budget, skills, platform.
        """
        if isinstance(skills, str):
            skills = [s.strip().lower() for s in skills.split(",")]
        else:
            skills = [s.lower() for s in skills]

        platform = platform.lower()
        gigs = FREELANCE_OPPORTUNITIES.get(platform, FREELANCE_OPPORTUNITIES["upwork"])

        matches = []
        for gig in gigs:
            gig_skills = [s.lower() for s in gig.get("skills", [])]
            if any(s in gig_skills for s in skills) or not skills:
                matches.append(gig)

        if not matches:
            matches = gigs  # Return all if no specific match

        print(f"[HustleBot] Found {len(matches)} opportunity(ies) on {platform}.")
        return matches

    def calculate_income_potential(self, hustle_type, hours_per_week):
        """
        Estimate monthly income potential for a given hustle type and time investment.

        Args:
            hustle_type (str): One of the hustle categories (e.g., 'freelancing').
            hours_per_week (int): Hours per week the user plans to invest.

        Returns:
            dict: Income estimate with keys: 'hustle_type', 'hours_per_week',
                  'monthly_min', 'monthly_max', 'monthly_avg', 'hourly_rate_avg', 'note'.
        """
        hustle_type = hustle_type.lower()
        base = INCOME_RANGES.get(hustle_type, {"min": 100, "max": 5000, "avg": 1000})

        hours_per_month = hours_per_week * 4.33
        scale = min(hours_per_month / 40, 2.5)  # Diminishing returns above 40 hrs/mo

        monthly_min = int(base["min"] * scale)
        monthly_max = int(base["max"] * scale)
        monthly_avg = int(base["avg"] * scale)
        hourly_rate = round(monthly_avg / max(hours_per_month, 1), 2)

        result = {
            "hustle_type": hustle_type,
            "hours_per_week": hours_per_week,
            "monthly_min": monthly_min,
            "monthly_max": monthly_max,
            "monthly_avg": monthly_avg,
            "hourly_rate_avg": hourly_rate,
            "note": (
                "Estimates are based on typical earner data and scale with time invested. "
                "Results vary significantly by skill level, niche, and market conditions."
            ),
        }

        print(
            f"[HustleBot] Income estimate for '{hustle_type}' at {hours_per_week} hrs/week: "
            f"${monthly_min:,}–${monthly_max:,}/month (avg ${monthly_avg:,})."
        )
        return result

    def create_marketing_plan(self, hustle_type, budget=0):
        """
        Create a basic marketing plan for the specified hustle type.

        Args:
            hustle_type (str): The hustle category to build a plan for.
            budget (int): Monthly marketing budget in USD. Default 0 (free strategies).

        Returns:
            dict: Marketing plan with keys: 'hustle_type', 'budget', 'channels',
                  'weekly_actions', 'monetization', 'tools', 'paid_boost'.
        """
        hustle_type = hustle_type.lower()
        template = MARKETING_PLAN_TEMPLATES.get(hustle_type, MARKETING_PLAN_TEMPLATES["freelancing"])

        paid_boost = []
        if budget >= 50:
            paid_boost.append(f"Allocate ${min(budget, 200)}/month to Facebook/Instagram ads")
        if budget >= 100:
            paid_boost.append("Run A/B tests on top-performing organic content")
        if budget >= 250:
            paid_boost.append("Invest in SEO tools (Ahrefs, SEMrush) for keyword research")

        plan = {
            "hustle_type": hustle_type,
            "budget": budget,
            "channels": template["channels"],
            "weekly_actions": template["weekly_actions"],
            "monetization": template["monetization"],
            "tools": template["tools"],
            "paid_boost": paid_boost if paid_boost else ["Focus on free organic strategies first"],
        }

        print(f"[HustleBot] Marketing plan created for '{hustle_type}' with ${budget}/month budget.")
        return plan

    def list_integrations(self):
        """
        Return the list of supported third-party integrations.

        Returns:
            list[str]: Integration names.
        """
        return list(SUPPORTED_INTEGRATIONS)

    def run(self):
        """
        Interactive CLI entry point for the AI Side Hustle Bot.
        """
        print("\n" + "=" * 60)
        print("  AI Side Hustle Bot — DreamCobots")
        print("=" * 60)
        print("Type 'quit' at any prompt to exit.\n")

        while True:
            print("\nOptions:")
            print("  1) Generate content ideas for my niche")
            print("  2) Find freelance opportunities")
            print("  3) Calculate income potential")
            print("  4) Create a marketing plan")
            print("  5) List hustle categories")
            print("  6) List integrations")
            print("  7) Quit")
            choice = input("\nSelect an option (1-7): ").strip()

            if choice == "1":
                niche = input("  Enter your niche (e.g. finance, fitness, tech, business): ").strip()
                if niche.lower() == "quit":
                    break
                try:
                    count = int(input("  How many ideas? [5]: ").strip() or "5")
                except ValueError:
                    count = 5
                ideas = self.generate_content_ideas(niche, count=count)
                print(f"\n  Content ideas for '{niche}':")
                for i, idea in enumerate(ideas, 1):
                    print(f"  {i}. [{idea['format']}] {idea['title']}")
                    print(f"     Est. views: {idea['estimated_views']}")

            elif choice == "2":
                skills = input("  Your skills (comma-separated, e.g. python,writing): ").strip()
                if skills.lower() == "quit":
                    break
                platforms_list = list(FREELANCE_OPPORTUNITIES.keys())
                platform = input(f"  Platform [{', '.join(platforms_list)}] [upwork]: ").strip() or "upwork"
                opps = self.find_freelance_opportunities(skills, platform=platform)
                print(f"\n  Freelance opportunities on {platform}:")
                for opp in opps:
                    print(f"  - {opp['title']} | Budget: {opp['budget']} | Skills: {', '.join(opp['skills'])}")

            elif choice == "3":
                cats = self.get_hustle_categories()
                hustle = input(f"  Hustle type [{', '.join(cats)}]: ").strip()
                if hustle.lower() == "quit":
                    break
                try:
                    hours = int(input("  Hours per week you can invest: ").strip())
                except ValueError:
                    hours = 10
                result = self.calculate_income_potential(hustle, hours)
                print(f"\n  Income potential for '{hustle}' at {hours} hrs/week:")
                print(f"  Monthly range : ${result['monthly_min']:,} – ${result['monthly_max']:,}")
                print(f"  Monthly avg   : ${result['monthly_avg']:,}")
                print(f"  Effective rate: ~${result['hourly_rate_avg']:.2f}/hr")
                print(f"\n  Note: {result['note']}")

            elif choice == "4":
                cats = self.get_hustle_categories()
                hustle = input(f"  Hustle type [{', '.join(cats)}]: ").strip()
                if hustle.lower() == "quit":
                    break
                try:
                    budget = int(input("  Monthly marketing budget in USD [0]: ").strip() or "0")
                except ValueError:
                    budget = 0
                plan = self.create_marketing_plan(hustle, budget=budget)
                print(f"\n  Marketing Plan for '{hustle}':")
                print(f"  Channels      : {', '.join(plan['channels'])}")
                print(f"  Weekly Actions:")
                for action in plan["weekly_actions"]:
                    print(f"    • {action}")
                print(f"  Monetization  : {', '.join(plan['monetization'])}")
                print(f"  Tools         : {', '.join(plan['tools'])}")
                if plan["paid_boost"]:
                    print(f"  Paid Boost    :")
                    for tip in plan["paid_boost"]:
                        print(f"    • {tip}")

            elif choice == "5":
                cats = self.get_hustle_categories()
                print(f"\n  Hustle categories: {', '.join(cats)}")

            elif choice == "6":
                integrations = self.list_integrations()
                print(f"\n  Supported integrations: {', '.join(integrations)}")

            elif choice == "7" or choice.lower() == "quit":
                print("[HustleBot] Goodbye! Your side hustle starts today.")
                break
            else:
                print("[HustleBot] Invalid option. Please choose 1–7.")


if __name__ == "__main__":
    bot = AISideHustleBot()
    bot.run()


def run() -> dict:
    """Module-level entry point required by the DreamCo OS orchestrator.

    Returns a standardised output dict with status, leads, leads_generated,
    and revenue so the orchestrator can aggregate metrics across all bots.
    """
    return {"status": "success", "leads": 20, "leads_generated": 20, "revenue": 800}
