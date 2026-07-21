"""Marketing Bot - SEO, content creation, social media, and campaign management."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core.base_bot import BaseBot


class MarketingBot(BaseBot):
    """AI bot for marketing automation: SEO, content, social media, and campaigns."""

    def __init__(self):
        """Initialize the MarketingBot."""
        super().__init__(
            name="marketing-bot",
            description="Automates marketing tasks: SEO research, content calendars, social posts, email campaigns, and ad copy.",
            version="2.0.0",
        )
        self.priority = "medium"

    def run(self):
        """Run the marketing bot main workflow."""
        self.start()
        return self.get_status()

    def research_keywords(self, niche: str, num_keywords: int = 10) -> list:
        """Generate SEO keyword research for a given niche."""
        base_keywords = [
            f"best {niche} software", f"{niche} for beginners", f"{niche} tutorial",
            f"how to {niche}", f"{niche} tools", f"top {niche} strategies",
            f"{niche} tips and tricks", f"affordable {niche} solutions",
            f"{niche} examples", f"{niche} case study", f"{niche} ROI",
            f"learn {niche} online", f"{niche} certification", f"{niche} vs",
        ]
        return [
            {
                "keyword": kw,
                "monthly_searches": 1000 + (i * 237 % 9000),
                "difficulty": ["Low", "Medium", "High"][i % 3],
                "cpc_usd": round(0.50 + i * 0.31, 2),
                "intent": ["informational", "transactional", "navigational"][i % 3],
            }
            for i, kw in enumerate(base_keywords[:num_keywords])
        ]

    def create_content_calendar(self, business_type: str, month: str) -> dict:
        """Create a monthly content calendar for a business type."""
        weeks = []
        themes = ["Educational", "Case Study", "Product Feature", "Customer Story"]
        platforms = ["Blog", "LinkedIn", "Instagram", "YouTube", "Twitter/X", "TikTok"]
        for week in range(1, 5):
            theme = themes[(week - 1) % len(themes)]
            weeks.append({
                "week": week,
                "theme": theme,
                "content_pieces": [
                    {"day": "Monday", "platform": "Blog", "type": f"1500-word article on {business_type} {theme}"},
                    {"day": "Tuesday", "platform": "LinkedIn", "type": f"Professional insight post (300 words)"},
                    {"day": "Wednesday", "platform": "Instagram", "type": f"Infographic: {theme} tips"},
                    {"day": "Thursday", "platform": "YouTube", "type": f"10-min explainer video"},
                    {"day": "Friday", "platform": "Email", "type": f"Weekly newsletter digest"},
                ],
            })
        return {
            "business_type": business_type,
            "month": month,
            "total_content_pieces": 20,
            "weekly_plan": weeks,
            "content_pillars": [
                "Educational/How-to (40%)",
                "Product/Service showcase (25%)",
                "Customer stories/testimonials (20%)",
                "Industry news/trends (15%)",
            ],
            "recommended_posting_frequency": "5x/week across platforms",
        }

    def generate_social_posts(self, topic: str, platforms: list, num_posts: int = 3) -> dict:
        """Generate social media posts for multiple platforms."""
        posts = {}
        for platform in platforms:
            platform_posts = []
            for i in range(num_posts):
                if platform.lower() in ["twitter", "x"]:
                    content = f"🔥 Did you know? {topic} can transform your business in 30 days. Here's how: [THREAD 1/{num_posts}] #business #growth"
                elif platform.lower() == "linkedin":
                    content = f"I've been thinking about {topic} lately.\n\nHere's what most people get wrong...\n\n[3 key insights about {topic}]\n\nWhat's your experience? Drop a comment 👇"
                elif platform.lower() == "instagram":
                    content = f"✨ {topic.upper()} ✨\n\n[Eye-catching visual hook]\n\nSwipe to see how we use {topic} to drive results ➡️\n\n#businesstips #{topic.replace(' ', '')} #entrepreneur"
                else:
                    content = f"[{platform.title()} Post {i+1}] {topic}: Key insight #{i+1} that drives real results for businesses like yours."
                platform_posts.append({
                    "post_number": i + 1,
                    "content": content,
                    "recommended_hashtags": [f"#{topic.replace(' ', '')}", "#business", "#growth", "#entrepreneur"],
                    "best_time_to_post": ["9:00 AM", "12:00 PM", "5:00 PM"][i % 3],
                })
            posts[platform] = platform_posts
        return {"topic": topic, "platforms": platforms, "posts": posts}

    def build_email_campaign(self, product: str, audience: str, campaign_type: str) -> dict:
        """Build a complete email marketing campaign."""
        sequences = {
            "welcome": [
                {"email": 1, "subject": f"Welcome! Here's how to get started with {product}", "delay": "Immediate"},
                {"email": 2, "subject": f"Your {product} quick-start guide (3 easy steps)", "delay": "Day 2"},
                {"email": 3, "subject": f"How [Customer Name] got results with {product} in 7 days", "delay": "Day 5"},
                {"email": 4, "subject": f"Special offer just for you - 20% off {product} upgrade", "delay": "Day 7"},
            ],
            "promotional": [
                {"email": 1, "subject": f"🔥 Limited time: {product} sale ends Sunday", "delay": "Day 0"},
                {"email": 2, "subject": f"Last 48 hours: {product} deal expires soon", "delay": "Day 3"},
                {"email": 3, "subject": f"Final hours - don't miss your {product} discount", "delay": "Day 5"},
            ],
            "nurture": [
                {"email": 1, "subject": f"The #1 mistake people make with {product}", "delay": "Week 1"},
                {"email": 2, "subject": f"3 ways {product} can save you 10+ hours/week", "delay": "Week 2"},
                {"email": 3, "subject": f"Case study: How [Company] 10x'd results with {product}", "delay": "Week 3"},
                {"email": 4, "subject": f"Ready to level up? {product} pro plan is here", "delay": "Week 4"},
            ],
        }
        sequence = sequences.get(campaign_type.lower(), sequences["nurture"])
        return {
            "product": product,
            "target_audience": audience,
            "campaign_type": campaign_type,
            "email_sequence": sequence,
            "best_practices": [
                "A/B test subject lines - send 20% each variant, send winner to remaining 60%",
                "Personalize with [First Name] and behavior-based triggers",
                "Mobile-optimize: 60%+ opens are on mobile",
                "Include one clear CTA per email",
                "Unsubscribe rate >0.5% = review your targeting",
            ],
            "expected_open_rate": "25-40%",
            "expected_click_rate": "3-8%",
        }

    def write_ad_copy(self, product: str, platform: str, tone: str) -> dict:
        """Write advertising copy for a product on a given platform."""
        tones = {
            "professional": f"Trusted by 10,000+ businesses. {product} delivers measurable results.",
            "casual": f"Tired of the same old tools? Try {product} - your team will thank you.",
            "urgent": f"⚠️ Only 47 spots left! {product} is almost sold out. Claim yours now.",
            "emotional": f"Imagine never worrying about [pain point] again. {product} makes it real.",
        }
        headline = tones.get(tone.lower(), tones["professional"])
        return {
            "product": product,
            "platform": platform,
            "tone": tone,
            "headline": headline,
            "body_copy": f"{headline} {product} helps you [benefit 1], [benefit 2], and [benefit 3] - all in one place.",
            "cta_options": ["Start Free Trial", "Get Started Today", "Claim Your Spot", "Learn More"],
            "recommended_cta": "Start Free Trial",
            "character_counts": {
                "headline": len(headline),
                "body": len(headline) + 80,
            },
            "platform_specs": {
                "Google Ads": "30 char headline / 90 char description",
                "Facebook/Instagram": "125 char primary text / 40 char headline",
                "LinkedIn": "150 char headline / 600 char description",
            }.get(platform, "Check platform documentation for character limits"),
        }

    def develop_brand_voice(self, business_type: str, values: list) -> dict:
        """Develop a brand voice guide based on business type and values."""
        return {
            "business_type": business_type,
            "core_values": values,
            "brand_voice": {
                "personality": ["Trustworthy", "Expert", "Approachable", "Innovative"],
                "tone_adjectives": ["Professional yet friendly", "Clear and direct", "Empowering", "Results-focused"],
                "do": [
                    "Use active voice",
                    "Lead with benefits, not features",
                    "Use data and social proof",
                    "Speak directly to the reader (you/your)",
                    "Keep sentences under 20 words",
                ],
                "dont": [
                    "Use jargon without explanation",
                    "Be overly formal or robotic",
                    "Make unsubstantiated claims",
                    "Use passive voice excessively",
                ],
            },
            "brand_story_template": f"{business_type} was founded because [founder insight]. We believe [core belief]. Our mission is to [mission statement].",
        }

    def analyze_competitor(self, competitor_name: str, industry: str) -> dict:
        """Analyze a competitor's marketing strategy."""
        return {
            "competitor": competitor_name,
            "industry": industry,
            "estimated_monthly_traffic": "125,000 visits",
            "top_traffic_channels": ["Organic Search (45%)", "Direct (25%)", "Social (20%)", "Paid (10%)"],
            "top_keywords": [f"{industry} software", f"best {industry} tools", f"{industry} solutions"],
            "content_strategy": "Publishes 3-4 blog posts/week, heavy LinkedIn presence",
            "social_following": {"LinkedIn": "45K", "Twitter": "12K", "YouTube": "8K"},
            "ad_spend_estimate": "$15,000-$25,000/month",
            "weaknesses": [
                "No YouTube video content (opportunity)",
                "Blog posts lack depth (rank for informational but no conversions)",
                "No podcast presence",
            ],
            "opportunities": [
                f"Target their low-ranking keywords for {industry}",
                "Create comparison pages: 'vs [competitor]'",
                "Reach out to their dissatisfied customers on review sites",
            ],
        }

    def track_campaign_roi(self, spend: float, revenue: float, clicks: int, conversions: int) -> dict:
        """Calculate and analyze marketing campaign ROI metrics."""
        roi = (revenue - spend) / spend * 100 if spend > 0 else 0
        roas = revenue / spend if spend > 0 else 0
        cpc = spend / clicks if clicks > 0 else 0
        cpa = spend / conversions if conversions > 0 else 0
        cvr = conversions / clicks * 100 if clicks > 0 else 0
        return {
            "spend": spend,
            "revenue": revenue,
            "clicks": clicks,
            "conversions": conversions,
            "roi_percent": round(roi, 1),
            "roas": round(roas, 2),
            "cost_per_click": round(cpc, 2),
            "cost_per_acquisition": round(cpa, 2),
            "conversion_rate_percent": round(cvr, 2),
            "campaign_rating": "Excellent" if roi >= 200 else "Good" if roi >= 100 else "Break-even" if roi >= 0 else "Loss",
            "recommendations": [
                f"ROAS of {roas:.1f}x {'is healthy (>3x target)' if roas >= 3 else 'needs improvement (target 3x+)'}",
                f"CVR of {cvr:.1f}% {'is above average' if cvr >= 3 else 'is below 3% average - optimize landing page'}",
            ],
        }
