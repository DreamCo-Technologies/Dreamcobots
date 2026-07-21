"""Software Bot — tier-aware software idea generation and revenue estimation."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.software_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401


class SoftwareBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class SoftwareBot:
    """Tier-aware software idea generation and revenue estimation bot."""

    FREE_CATEGORIES = ["productivity", "utility", "games"]
    PRO_CATEGORIES = ["productivity", "utility", "games", "health", "finance", "education", "social", "ecommerce", "travel", "fitness"]
    ALL_CATEGORIES = PRO_CATEGORIES + ["iot", "ai_tools", "security", "entertainment", "real_estate"]

    CATEGORY_LIMITS = {
        Tier.FREE: FREE_CATEGORIES,
        Tier.PRO: PRO_CATEGORIES,
        Tier.ENTERPRISE: ALL_CATEGORIES,
    }

    REVENUE_RANGES = {
        Tier.FREE: {"daily_min": 100, "daily_max": 500},
        Tier.PRO: {"daily_min": 500, "daily_max": 2000},
        Tier.ENTERPRISE: {"daily_min": 1000, "daily_max": 3000},
    }

    APP_IDEAS = {
        "productivity": [
            {"name": "FocusFlow", "description": "Pomodoro-based task manager with AI prioritization", "target_market": "Remote workers", "monetization": "Subscription $9.99/mo"},
            {"name": "MeetingMind", "description": "AI meeting notes and action item extractor", "target_market": "Corporate teams", "monetization": "Freemium + $15/mo Pro"},
            {"name": "DailyPlanner AI", "description": "Smart daily schedule optimizer using ML", "target_market": "Busy professionals", "monetization": "Subscription $7.99/mo"},
            {"name": "QuickCapture", "description": "Voice-to-task inbox for instant capture", "target_market": "GTD enthusiasts", "monetization": "One-time $4.99"},
            {"name": "TeamFlow", "description": "Cross-timezone team coordination dashboard", "target_market": "Distributed teams", "monetization": "Per-seat $12/mo"},
        ],
        "utility": [
            {"name": "FileOrganizer Pro", "description": "AI-powered file sorting and deduplication", "target_market": "Power users", "monetization": "One-time $19.99"},
            {"name": "ClipboardManager", "description": "Smart clipboard history with search", "target_market": "Developers", "monetization": "Freemium + $4.99/mo"},
            {"name": "BatteryGuard", "description": "Battery health optimizer and monitor", "target_market": "Laptop users", "monetization": "One-time $2.99"},
            {"name": "NetworkScanner", "description": "Home network device discovery and security", "target_market": "Home users", "monetization": "Freemium + $8/mo"},
            {"name": "AutoBackup", "description": "Incremental cloud backup with versioning", "target_market": "Small businesses", "monetization": "Subscription $6.99/mo"},
        ],
        "games": [
            {"name": "WordRush", "description": "Multiplayer real-time word game", "target_market": "Casual gamers", "monetization": "In-app purchases"},
            {"name": "PuzzleForge", "description": "Daily logic puzzle generator with AI", "target_market": "Puzzle lovers", "monetization": "Ads + Premium $1.99/mo"},
            {"name": "TriviaNight", "description": "Live trivia battles with friends", "target_market": "Social gamers", "monetization": "In-app + ads"},
            {"name": "PixelQuest", "description": "Retro-style RPG with procedural dungeons", "target_market": "Retro gamers", "monetization": "One-time $4.99"},
            {"name": "ChessCoach", "description": "AI chess tutor with position analysis", "target_market": "Chess players", "monetization": "Freemium + $9.99/mo"},
        ],
        "health": [
            {"name": "SymptomTracker", "description": "Daily symptom logging with trend analysis", "target_market": "Chronic illness patients", "monetization": "Subscription $5.99/mo"},
            {"name": "MindfulMoments", "description": "Guided breathing and stress reduction", "target_market": "Stressed professionals", "monetization": "Freemium + $7.99/mo"},
            {"name": "SleepOptimizer", "description": "Sleep cycle tracker with smart alarm", "target_market": "Sleep-deprived adults", "monetization": "One-time $2.99"},
            {"name": "MedicineReminder", "description": "Medication tracking with family sharing", "target_market": "Seniors and caregivers", "monetization": "Free + $3.99/mo Premium"},
            {"name": "NutritionScan", "description": "Food photo calorie and nutrition scanner", "target_market": "Diet-conscious users", "monetization": "Subscription $8.99/mo"},
        ],
        "finance": [
            {"name": "BudgetBuddy", "description": "AI personal budget coach and tracker", "target_market": "Millennials", "monetization": "Freemium + $9.99/mo"},
            {"name": "InvoiceZap", "description": "Freelancer invoice generator and tracker", "target_market": "Freelancers", "monetization": "Free + $6.99/mo Pro"},
            {"name": "CryptoWatch", "description": "Multi-exchange crypto portfolio tracker", "target_market": "Crypto investors", "monetization": "Freemium + $14.99/mo"},
            {"name": "TaxEasy", "description": "Self-employed tax estimation and filing helper", "target_market": "Self-employed", "monetization": "Per-filing $29.99"},
            {"name": "SplitEase", "description": "Bill splitting and expense tracking app", "target_market": "Roommates, groups", "monetization": "Free + ads"},
        ],
        "education": [
            {"name": "FlashGenius", "description": "AI-powered spaced repetition flashcards", "target_market": "Students", "monetization": "Freemium + $4.99/mo"},
            {"name": "CodeTutor", "description": "Interactive programming tutor for beginners", "target_market": "Coding beginners", "monetization": "Subscription $12.99/mo"},
            {"name": "LanguageSprint", "description": "Microlearning language app with AI speaking coach", "target_market": "Language learners", "monetization": "Freemium + $9.99/mo"},
            {"name": "ReadingRocket", "description": "Speed reading trainer with comprehension tests", "target_market": "Students, professionals", "monetization": "One-time $4.99"},
            {"name": "MathMaster", "description": "Adaptive math problem generator with hints", "target_market": "K-12 students", "monetization": "School licenses + $3.99/mo"},
        ],
        "social": [
            {"name": "EventCircle", "description": "Neighborhood event discovery and RSVP", "target_market": "Local communities", "monetization": "Freemium + promoted listings"},
            {"name": "SkillSwap", "description": "Peer-to-peer skill trading community", "target_market": "Lifelong learners", "monetization": "Premium connections $6.99/mo"},
            {"name": "PhotoMemory", "description": "Collaborative family album with stories", "target_market": "Families", "monetization": "Print orders + $2.99/mo"},
            {"name": "LocalMentor", "description": "Connect mentors and mentees in your city", "target_market": "Young professionals", "monetization": "Premium features $9.99/mo"},
            {"name": "BookClubApp", "description": "Virtual book club with reading schedules", "target_market": "Book lovers", "monetization": "Free + affiliate books"},
        ],
        "ecommerce": [
            {"name": "DropshipPilot", "description": "Automated dropshipping product research", "target_market": "Dropshippers", "monetization": "Subscription $29.99/mo"},
            {"name": "PriceSniper", "description": "Real-time price comparison and alert tool", "target_market": "Online shoppers", "monetization": "Affiliate commissions"},
            {"name": "ReviewRadar", "description": "Product review aggregator with sentiment", "target_market": "Smart shoppers", "monetization": "Premium alerts $4.99/mo"},
            {"name": "CartAbandon", "description": "Ecommerce cart recovery email automation", "target_market": "Shopify stores", "monetization": "SaaS $19.99/mo"},
            {"name": "InventorySync", "description": "Multi-channel inventory management", "target_market": "SMB retailers", "monetization": "Subscription $39.99/mo"},
        ],
        "travel": [
            {"name": "TripCraft", "description": "AI itinerary planner from preferences", "target_market": "Leisure travelers", "monetization": "Booking commissions"},
            {"name": "PackSmarter", "description": "Destination-aware packing list generator", "target_market": "Frequent travelers", "monetization": "Premium features $2.99/mo"},
            {"name": "FlightDeal", "description": "Fare alert and mistake fare finder", "target_market": "Budget travelers", "monetization": "Affiliate + premium $7.99/mo"},
            {"name": "LocalEats", "description": "Hyper-local food recommendation engine", "target_market": "Tourists", "monetization": "Restaurant partnerships"},
            {"name": "VaultPass", "description": "Travel document organizer and reminder", "target_market": "International travelers", "monetization": "One-time $1.99"},
        ],
        "fitness": [
            {"name": "GymBuddy", "description": "Workout partner matching and tracking", "target_market": "Gym goers", "monetization": "Freemium + $9.99/mo"},
            {"name": "RunCoach AI", "description": "Adaptive running training plan generator", "target_market": "Runners", "monetization": "Subscription $7.99/mo"},
            {"name": "FormCheck", "description": "Exercise form analysis via phone camera", "target_market": "Home workout fans", "monetization": "Premium $12.99/mo"},
            {"name": "MealPrep Pro", "description": "Weekly meal prep planner with macros", "target_market": "Fitness enthusiasts", "monetization": "Freemium + $4.99/mo"},
            {"name": "StretchBot", "description": "Personalized stretching routine generator", "target_market": "Desk workers", "monetization": "One-time $1.99"},
        ],
        "iot": [
            {"name": "SmartHomeHub", "description": "Unified IoT device dashboard and automation", "target_market": "Smart home owners", "monetization": "Premium $14.99/mo"},
            {"name": "EnergyTracker", "description": "Home energy usage monitor and optimizer", "target_market": "Eco-conscious homeowners", "monetization": "Subscription $8.99/mo"},
            {"name": "PlantSensor", "description": "Soil sensor companion app for plant care", "target_market": "Plant enthusiasts", "monetization": "Hardware + app $2.99/mo"},
            {"name": "SecurityCamera", "description": "Multi-camera home security dashboard", "target_market": "Homeowners", "monetization": "Cloud storage $4.99/mo"},
            {"name": "AirQualityAlert", "description": "Indoor air quality monitor and alerts", "target_market": "Health-conscious families", "monetization": "Device + app $3.99/mo"},
        ],
        "ai_tools": [
            {"name": "ContentForge", "description": "AI long-form content generator for blogs", "target_market": "Content marketers", "monetization": "Credits + $29.99/mo"},
            {"name": "ImageAlter", "description": "AI image editing via text prompts", "target_market": "Designers, marketers", "monetization": "Pay-per-use + subscription"},
            {"name": "ChatPersona", "description": "Custom AI chatbot builder for websites", "target_market": "SMBs", "monetization": "SaaS $19.99/mo"},
            {"name": "TranscribeAI", "description": "Real-time multi-speaker transcription", "target_market": "Journalists, researchers", "monetization": "Per-minute + $12/mo"},
            {"name": "SummarizeIt", "description": "Document and video summarization engine", "target_market": "Knowledge workers", "monetization": "Freemium + $9.99/mo"},
        ],
        "security": [
            {"name": "VaultKey", "description": "Zero-knowledge password manager", "target_market": "Privacy-conscious users", "monetization": "Freemium + $3.99/mo"},
            {"name": "PhishGuard", "description": "Email phishing link detector browser ext", "target_market": "Non-technical users", "monetization": "Premium $2.99/mo"},
            {"name": "DataBreachAlert", "description": "Personal data breach monitoring service", "target_market": "Everyone", "monetization": "Premium $4.99/mo"},
            {"name": "VPNOptimizer", "description": "VPN server performance optimizer", "target_market": "VPN users", "monetization": "Affiliate + premium $6.99/mo"},
            {"name": "SecureNote", "description": "End-to-end encrypted note sharing", "target_market": "Professionals", "monetization": "Freemium + $7.99/mo"},
        ],
        "entertainment": [
            {"name": "PodcastClip", "description": "Auto-generate short clips from podcast episodes", "target_market": "Podcasters", "monetization": "Subscription $14.99/mo"},
            {"name": "StreamTracker", "description": "Track what to watch across all streaming services", "target_market": "Binge watchers", "monetization": "Free + ads + affiliate"},
            {"name": "MusicMood", "description": "Mood-based playlist generator", "target_market": "Music lovers", "monetization": "Premium $2.99/mo"},
            {"name": "ComedyBot", "description": "AI joke and meme generator", "target_market": "Social media users", "monetization": "Ads + premium $1.99/mo"},
            {"name": "FanForum", "description": "Community platform for niche fandoms", "target_market": "Fandom communities", "monetization": "Premium memberships"},
        ],
        "real_estate": [
            {"name": "HouseFlipper", "description": "Property flip ROI calculator and deal scorer", "target_market": "Real estate investors", "monetization": "Subscription $29.99/mo"},
            {"name": "RentAnalyzer", "description": "Rental income estimator by address", "target_market": "Landlords", "monetization": "Per-report + $14.99/mo"},
            {"name": "TenantScreen", "description": "Automated tenant background check tool", "target_market": "Property managers", "monetization": "Per-report $9.99"},
            {"name": "ListingBoost", "description": "AI property listing description writer", "target_market": "Real estate agents", "monetization": "Pay-per-use + $19.99/mo"},
            {"name": "MarketPulse", "description": "Local real estate market analytics dashboard", "target_market": "Agents and investors", "monetization": "Subscription $24.99/mo"},
        ],
    }

    TECH_STACKS = {
        "mobile": {"frontend": "React Native", "backend": "Node.js + Express", "database": "Firebase", "hosting": "AWS Amplify"},
        "web": {"frontend": "React + TypeScript", "backend": "FastAPI (Python)", "database": "PostgreSQL", "hosting": "Vercel + AWS RDS"},
        "desktop": {"frontend": "Electron + React", "backend": "Python", "database": "SQLite", "hosting": "Self-hosted"},
        "api": {"framework": "FastAPI / Django REST", "database": "PostgreSQL", "hosting": "AWS Lambda", "auth": "JWT + OAuth2"},
        "fullstack": {"frontend": "Next.js", "backend": "Node.js + NestJS", "database": "PostgreSQL + Redis", "hosting": "Railway / Render"},
    }

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)

    def list_app_categories(self) -> list:
        """Return available app categories for the current tier."""
        return list(self.CATEGORY_LIMITS[self.tier])

    def generate_app_idea(self, category: str) -> dict:
        """Return an app idea for the given category."""
        allowed = self.CATEGORY_LIMITS[self.tier]
        if category.lower() not in allowed:
            raise SoftwareBotTierError(
                f"Category '{category}' not available on {self.config.name} tier. "
                f"Available: {allowed}. Upgrade to access more categories."
            )
        ideas = self.APP_IDEAS.get(category.lower(), self.APP_IDEAS["productivity"])
        idea = ideas[0].copy()
        idea["category"] = category
        idea["tier"] = self.tier.value
        if self.tier == Tier.ENTERPRISE:
            idea["market_analysis"] = {
                "tam_usd_billion": round(5.0 + hash(idea["name"]) % 50, 1),
                "competition_level": "Medium",
                "recommended_approach": "Mobile-first SaaS with freemium model",
            }
        return idea

    def create_app_template(self, idea: dict) -> dict:
        """Return a template with tech stack, features, and architecture."""
        category = idea.get("category", "productivity")
        app_type = "mobile" if category in ("fitness", "health", "travel", "games") else "web"
        stack = self.TECH_STACKS.get(app_type, self.TECH_STACKS["web"])

        template = {
            "app_name": idea.get("name", "MyApp"),
            "app_type": app_type,
            "tech_stack": stack,
            "core_features": [
                "User authentication (OAuth2)",
                "Dashboard / home screen",
                f"{idea.get('name', 'App')} core functionality",
                "Settings and preferences",
                "Push notifications",
            ],
            "architecture": "MVC with service layer",
            "estimated_mvp_weeks": 8 if self.tier == Tier.FREE else 6,
            "tier": self.tier.value,
        }
        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            template["premium_features"] = ["Analytics dashboard", "A/B testing", "In-app payments", "Admin panel"]
            template["monetization_strategy"] = idea.get("monetization", "Subscription")
        if self.tier == Tier.ENTERPRISE:
            template["ci_cd_pipeline"] = {"ci": "GitHub Actions", "cd": "AWS CodeDeploy", "testing": "pytest + Jest"}
            template["ai_generated_scaffold"] = True
        return template

    def estimate_revenue(self, app: dict) -> dict:
        """Return revenue projections (daily, monthly, annual)."""
        rng = self.REVENUE_RANGES[self.tier]
        daily_low = rng["daily_min"]
        daily_high = rng["daily_max"]
        daily_mid = (daily_low + daily_high) // 2

        return {
            "app_name": app.get("name", "App"),
            "daily_revenue_usd": {"low": daily_low, "mid": daily_mid, "high": daily_high},
            "monthly_revenue_usd": {"low": daily_low * 30, "mid": daily_mid * 30, "high": daily_high * 30},
            "annual_revenue_usd": {"low": daily_low * 365, "mid": daily_mid * 365, "high": daily_high * 365},
            "monetization": app.get("monetization", "Unknown"),
            "tier": self.tier.value,
        }

    def describe_tier(self) -> str:
        info = get_bot_tier_info(self.tier)
        lines = [
            f"=== {info['name']} Software Bot Tier ===",
            f"Price: ${info['price_usd_monthly']:.2f}/month",
            f"Support: {info['support_level']}",
            "Features:",
        ]
        for f in info["features"]:
            lines.append(f"  \u2713 {f}")
        output = "\n".join(lines)
        print(output)
        return output
