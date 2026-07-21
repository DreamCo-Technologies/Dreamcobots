"""
Influencer Engine — Content Strategy and Meme Generation

Classes
-------
ContentStrategyEngine — AI-powered content calendars, viral posts, and engagement analysis.
MemeGenerator         — Meme generation, trend analysis, and virality prediction.

All classes integrate with the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401

PLATFORMS = ["instagram", "tiktok", "youtube", "twitter", "linkedin", "facebook"]


# ---------------------------------------------------------------------------
# Content Strategy Engine
# ---------------------------------------------------------------------------

class ContentStrategyEngine:
    """AI-powered content calendar creation, viral post generation, and engagement analytics."""

    def __init__(self) -> None:
        self.flow = GlobalAISourcesFlow(bot_name="ContentStrategyEngine")

    # ------------------------------------------------------------------
    def create_content_calendar(self, platform: str, niche: str, weeks: int = 4) -> dict:
        """Generate a weekly content posting schedule.

        Parameters
        ----------
        platform : str
            Target social media platform (see PLATFORMS).
        niche : str
            Content niche, e.g. "fitness", "travel", "tech reviews".
        weeks : int
            Number of weeks to plan (1–12).

        Returns
        -------
        dict
            Weekly content schedule with post types, topics, and optimal timing.
        """
        if platform not in PLATFORMS:
            platform = PLATFORMS[0]
        weeks = max(1, min(12, weeks))

        post_types_by_platform: dict[str, list[str]] = {
            "instagram": ["photo", "reel", "story", "carousel"],
            "tiktok": ["short_video", "duet", "stitch", "live"],
            "youtube": ["long_video", "short", "community_post", "live"],
            "twitter": ["tweet", "thread", "poll", "spaces"],
            "linkedin": ["article", "post", "video", "document"],
            "facebook": ["post", "reel", "story", "live", "event"],
        }

        best_times_by_platform: dict[str, list[str]] = {
            "instagram": ["9:00 AM", "12:00 PM", "7:00 PM"],
            "tiktok": ["7:00 AM", "3:00 PM", "9:00 PM"],
            "youtube": ["2:00 PM", "4:00 PM", "9:00 PM"],
            "twitter": ["8:00 AM", "12:00 PM", "5:00 PM"],
            "linkedin": ["8:00 AM", "12:00 PM", "5:30 PM"],
            "facebook": ["9:00 AM", "1:00 PM", "7:00 PM"],
        }

        post_types = post_types_by_platform.get(platform, ["post"])
        best_times = best_times_by_platform.get(platform, ["12:00 PM"])

        calendar = []
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        for week in range(1, weeks + 1):
            week_schedule = {
                "week": week,
                "posts": [],
            }
            posts_per_week = 5 if platform in ("instagram", "facebook") else 4
            for i in range(posts_per_week):
                week_schedule["posts"].append({
                    "day": days_of_week[i % 7],
                    "post_type": random.choice(post_types),
                    "topic": f"Week {week} {niche} content idea #{i + 1}",
                    "caption_hook": f"Did you know this about {niche}? 🔥",
                    "hashtags": [f"#{niche}", f"#{platform}creator", "#trending", "#viral"],
                    "optimal_time": random.choice(best_times),
                })
            calendar.append(week_schedule)

        result = self.flow.run_pipeline(
            raw_data={"task": "create_content_calendar", "platform": platform, "niche": niche, "weeks": weeks},
            learning_method="supervised",
        )

        return {
            "platform": platform,
            "niche": niche,
            "weeks": weeks,
            "total_posts": sum(len(w["posts"]) for w in calendar),
            "calendar": calendar,
            "framework_pipeline": result.get("bot_name"),
        }

    # ------------------------------------------------------------------
    def generate_viral_post(self, platform: str, topic: str, style: str = "educational") -> dict:
        """Generate high-engagement social media post content.

        Parameters
        ----------
        platform : str
            Target social media platform.
        topic : str
            Subject of the post.
        style : str
            Content style: "educational", "entertaining", "inspirational", "promotional".

        Returns
        -------
        dict
            Post content with caption, hashtags, call-to-action, and engagement tips.
        """
        if platform not in PLATFORMS:
            platform = PLATFORMS[0]

        hooks_by_style: dict[str, str] = {
            "educational": f"🧠 Most people don't know this about {topic}...",
            "entertaining": f"😂 POV: You just discovered {topic} for the first time",
            "inspirational": f"✨ {topic.capitalize()} changed my life — here's how",
            "promotional": f"🚀 Introducing the ultimate guide to {topic}",
        }

        hook = hooks_by_style.get(style, hooks_by_style["educational"])

        result = self.flow.run_pipeline(
            raw_data={"task": "generate_viral_post", "platform": platform, "topic": topic, "style": style},
            learning_method="supervised",
        )

        return {
            "platform": platform,
            "topic": topic,
            "style": style,
            "hook": hook,
            "caption": (
                f"{hook}\n\n"
                f"Here are 5 things about {topic} that will blow your mind:\n"
                f"1️⃣ First insight about {topic}\n"
                f"2️⃣ Second insight about {topic}\n"
                f"3️⃣ Third insight about {topic}\n"
                f"4️⃣ Fourth insight about {topic}\n"
                f"5️⃣ Fifth insight about {topic}\n\n"
                f"Save this post and share it with someone who needs to see it! 👇"
            ),
            "hashtags": [f"#{topic.replace(' ', '')}", "#viral", f"#{platform}", "#trending", "#fyp"],
            "call_to_action": "Drop a 🔥 if this helped you!",
            "predicted_reach": random.randint(1_000, 100_000),
            "engagement_tips": [
                "Post between 9–11 AM or 7–9 PM",
                "Reply to every comment in the first hour",
                "Use trending audio if posting video",
            ],
            "framework_pipeline": result.get("bot_name"),
        }

    # ------------------------------------------------------------------
    def analyze_engagement(self, post_data: dict) -> dict:
        """Analyze social media post engagement metrics.

        Parameters
        ----------
        post_data : dict
            Post descriptor including likes, comments, shares, reach, etc.

        Returns
        -------
        dict
            Engagement metrics analysis with recommendations.
        """
        likes = post_data.get("likes", 0)
        comments = post_data.get("comments", 0)
        shares = post_data.get("shares", 0)
        reach = post_data.get("reach", 1)

        engagement_rate = round(((likes + comments + shares) / max(reach, 1)) * 100, 2)
        virality_score = min(100, int(shares / max(reach, 1) * 1_000))

        result = self.flow.run_pipeline(
            raw_data={"task": "analyze_engagement", "post_data": post_data},
            learning_method="unsupervised",
        )

        return {
            "engagement_rate_pct": engagement_rate,
            "virality_score": virality_score,
            "performance_grade": "A" if engagement_rate > 5 else "B" if engagement_rate > 2 else "C",
            "top_metric": "shares" if shares > comments and shares > likes else "likes" if likes >= comments else "comments",
            "recommendations": [
                "Increase posting frequency to 5x/week",
                "Engage with comments within 30 minutes",
                "A/B test different hooks",
            ],
            "best_performing_hour": f"{random.randint(7, 21)}:00",
            "audience_retention_pct": round(random.uniform(40.0, 85.0), 1),
            "framework_pipeline": result.get("bot_name"),
        }


# ---------------------------------------------------------------------------
# Meme Generator
# ---------------------------------------------------------------------------

class MemeGenerator:
    """AI-powered meme creation, viral trend analysis, and content virality prediction."""

    def __init__(self) -> None:
        self.flow = GlobalAISourcesFlow(bot_name="MemeGenerator")

    # ------------------------------------------------------------------
    def generate_meme(self, topic: str, style: str = "relatable", target_audience: str = "gen_z") -> dict:
        """Generate meme content and description.

        Parameters
        ----------
        topic : str
            Subject of the meme.
        style : str
            Meme style: "relatable", "absurd", "wholesome", "dark_humor", "informational".
        target_audience : str
            Target demographic, e.g. "gen_z", "millennials", "gamers".

        Returns
        -------
        dict
            Meme content with template, text, and cultural references.
        """
        templates_by_style: dict[str, str] = {
            "relatable": "Two Buttons",
            "absurd": "Drake Pointing",
            "wholesome": "Surprised Pikachu",
            "dark_humor": "This Is Fine",
            "informational": "Expanding Brain",
        }

        top_text_by_style: dict[str, str] = {
            "relatable": f"When you finally understand {topic}",
            "absurd": f"Me ignoring {topic}",
            "wholesome": f"When {topic} actually works out",
            "dark_humor": f"{topic} at 3 AM",
            "informational": f"Level 1: knowing about {topic}",
        }

        result = self.flow.run_pipeline(
            raw_data={"task": "generate_meme", "topic": topic, "style": style, "target_audience": target_audience},
            learning_method="self_supervised",
        )

        return {
            "topic": topic,
            "style": style,
            "target_audience": target_audience,
            "template": templates_by_style.get(style, "Drake Pointing"),
            "top_text": top_text_by_style.get(style, f"When {topic} happens"),
            "bottom_text": f"Everyone who understands {topic}: 😂",
            "visual_description": f"Classic {templates_by_style.get(style, 'meme')} format featuring {topic}",
            "predicted_engagement": random.choice(["low", "medium", "high", "viral"]),
            "cultural_references": [topic, style, target_audience],
            "framework_pipeline": result.get("bot_name"),
        }

    # ------------------------------------------------------------------
    def analyze_viral_trends(self, platform: str) -> dict:
        """Analyze current viral content trends on a platform.

        Parameters
        ----------
        platform : str
            Social media platform to analyse (see PLATFORMS).

        Returns
        -------
        dict
            Trending content analysis with topics, formats, and recommendations.
        """
        if platform not in PLATFORMS:
            platform = PLATFORMS[0]

        trending_topics_by_platform: dict[str, list[str]] = {
            "instagram": ["aesthetic photos", "before/after", "day in my life", "GRWM", "recipe reels"],
            "tiktok": ["POV videos", "dance challenges", "life hacks", "skits", "educational shorts"],
            "youtube": ["long-form commentary", "tutorials", "vlogs", "gaming", "true crime"],
            "twitter": ["hot takes", "threads", "breaking news", "memes", "reply guys"],
            "linkedin": ["career advice", "industry insights", "personal branding", "company culture"],
            "facebook": ["community events", "nostalgia content", "giveaways", "family content"],
        }

        result = self.flow.run_pipeline(
            raw_data={"task": "analyze_viral_trends", "platform": platform},
            learning_method="unsupervised",
        )

        trending = trending_topics_by_platform.get(platform, trending_topics_by_platform["instagram"])

        return {
            "platform": platform,
            "trending_topics": trending,
            "trending_formats": random.sample(["video", "image", "carousel", "text", "poll", "live"], k=3),
            "peak_posting_hours": [f"{h}:00" for h in random.sample(range(6, 23), 3)],
            "top_hashtags": [f"#trending_{platform}", "#viral", "#fyp", "#explore", "#reels"],
            "audience_sentiment": random.choice(["positive", "humorous", "educational", "inspirational"]),
            "content_longevity_days": random.randint(1, 14),
            "framework_pipeline": result.get("bot_name"),
        }

    # ------------------------------------------------------------------
    def predict_viral_score(self, content_data: dict) -> dict:
        """Predict the virality potential of content on a 0–100 scale.

        Parameters
        ----------
        content_data : dict
            Content descriptor including platform, type, topic, and metadata.

        Returns
        -------
        dict
            Virality prediction with score, breakdown, and improvement tips.
        """
        base_score = random.randint(30, 70)

        platform = content_data.get("platform", "instagram")
        has_hook = bool(content_data.get("hook"))
        has_visual = bool(content_data.get("visual"))
        has_hashtags = bool(content_data.get("hashtags"))
        is_trending_topic = bool(content_data.get("trending_topic"))

        bonus = sum([
            10 if has_hook else 0,
            8 if has_visual else 0,
            5 if has_hashtags else 0,
            15 if is_trending_topic else 0,
        ])

        score = min(100, base_score + bonus)

        result = self.flow.run_pipeline(
            raw_data={"task": "predict_viral_score", "content_data": content_data},
            learning_method="supervised",
        )

        return {
            "viral_score": score,
            "score_breakdown": {
                "base_engagement_potential": base_score,
                "hook_bonus": 10 if has_hook else 0,
                "visual_bonus": 8 if has_visual else 0,
                "hashtag_bonus": 5 if has_hashtags else 0,
                "trending_topic_bonus": 15 if is_trending_topic else 0,
            },
            "prediction_label": "viral" if score >= 75 else "likely_popular" if score >= 50 else "average",
            "estimated_reach_multiplier": round(score / 20, 1),
            "improvement_tips": [
                "Add a strong hook in the first 3 seconds",
                "Use trending audio or sounds",
                "Post at peak engagement hours",
                "Include a clear call-to-action",
            ],
            "platform": platform,
            "framework_pipeline": result.get("bot_name"),
        }
