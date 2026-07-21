"""
200-Strategy Framework — integrates speed, automation, integrations, UX,
resilience, monetization, testing, and intelligence strategies into every
generated bot's design.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Strategy categories (8 pillars)
# ---------------------------------------------------------------------------

class StrategyCategory(Enum):
    SPEED = "speed"
    AUTOMATION = "automation"
    INTEGRATIONS = "integrations"
    UX = "ux"
    RESILIENCE = "resilience"
    MONETIZATION = "monetization"
    TESTING = "testing"
    INTELLIGENCE = "intelligence"


@dataclass
class Strategy:
    """A single strategy in the 200-strategy framework."""
    id: int
    name: str
    category: StrategyCategory
    description: str
    priority: int = 5  # 1 (low) to 10 (high)
    applicable_categories: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "priority": self.priority,
            "applicable_categories": self.applicable_categories,
        }


# ---------------------------------------------------------------------------
# 200-Strategy catalogue
# ---------------------------------------------------------------------------

def _build_strategy_catalogue() -> list[Strategy]:
    """Build the full 200-strategy catalogue."""
    strategies: list[Strategy] = []
    sid = 1

    # (A) SPEED — 25 strategies
    speed_strategies = [
        ("Async API Calls", "Use asyncio for non-blocking API requests", 9),
        ("Multithreading", "Leverage threading for parallel task execution", 8),
        ("Connection Pooling", "Reuse HTTP connections to reduce latency", 8),
        ("Response Caching", "Cache API responses to avoid redundant calls", 7),
        ("Load Balancing", "Distribute workload across multiple workers", 8),
        ("Database Indexing", "Index frequently queried fields for faster lookups", 9),
        ("Batch Processing", "Group operations into batches to reduce overhead", 8),
        ("Lazy Loading", "Load data only when needed to reduce startup time", 7),
        ("CDN Integration", "Serve static assets via CDN for faster delivery", 6),
        ("Memory Caching", "Use in-memory caches (e.g., Redis) for hot data", 8),
        ("Query Optimization", "Optimize database queries to reduce execution time", 9),
        ("Compression", "Compress API payloads to reduce transfer time", 7),
        ("Rate Limiting Bypass", "Smart retry logic to maximize throughput", 7),
        ("Prefetching", "Prefetch likely-needed data in background", 7),
        ("Pipeline Optimization", "Streamline processing pipelines to reduce steps", 8),
        ("Load Testing", "Run load tests to identify and fix bottlenecks", 8),
        ("Profiling", "Profile code execution to find slow spots", 8),
        ("Network Timeout Tuning", "Set optimal timeouts to prevent stalls", 7),
        ("Data Streaming", "Stream large datasets instead of bulk loading", 7),
        ("Parallel Execution", "Run independent tasks in parallel", 9),
        ("Circuit Breaker", "Fast-fail on repeated errors to maintain speed", 8),
        ("Request Deduplication", "Deduplicate identical in-flight requests", 6),
        ("Worker Queue", "Use task queues to manage load spikes", 8),
        ("Hot Path Optimization", "Identify and optimize the critical code path", 9),
        ("Async DB Queries", "Use async database drivers for non-blocking queries", 8),
    ]
    for name, desc, priority in speed_strategies:
        strategies.append(
            Strategy(
                id=sid, name=name, category=StrategyCategory.SPEED,
                description=desc, priority=priority,
                applicable_categories=["all"],
            )
        )
        sid += 1

    # (B) AUTOMATION — 25 strategies
    automation_strategies = [
        ("NLP Intent Detection", "Parse user intent from natural language", 9),
        ("Personalized Messaging", "Tailor outreach messages per lead profile", 9),
        ("Auto Feature Updates", "Automatically apply feature improvements", 8),
        ("Adaptive Workflows", "Adjust workflows based on real-time outcomes", 8),
        ("Scheduled Campaigns", "Schedule outreach campaigns automatically", 8),
        ("Lead Scoring", "Auto-score leads based on engagement signals", 9),
        ("CRM Sync", "Automatically sync lead data to CRM", 8),
        ("Email Automation", "Send automated follow-up emails", 8),
        ("SMS Automation", "Send automated SMS messages", 9),
        ("Voice Bot Automation", "Auto-dial and deliver voice messages", 7),
        ("Social Media Monitoring", "Monitor social signals for lead triggers", 7),
        ("Auto-Respond to Inquiries", "Reply to inbound inquiries automatically", 9),
        ("Pipeline Stage Automation", "Move leads through pipeline stages automatically", 8),
        ("Data Enrichment", "Auto-enrich lead data from public sources", 7),
        ("Document Generation", "Auto-generate proposals and contracts", 7),
        ("Calendar Scheduling", "Auto-book meetings based on availability", 8),
        ("Invoice Automation", "Auto-generate and send invoices", 7),
        ("Feedback Collection", "Automatically collect and analyze feedback", 7),
        ("A/B Test Automation", "Auto-run and measure A/B tests", 8),
        ("Report Generation", "Auto-generate performance reports", 7),
        ("Competitor Monitoring", "Automatically track competitor changes", 8),
        ("Content Scheduling", "Auto-schedule content across channels", 6),
        ("Trigger-Based Actions", "Execute actions based on event triggers", 9),
        ("Data Backup Automation", "Automatically back up critical data", 8),
        ("Workflow Versioning", "Track and version workflow changes automatically", 7),
    ]
    for name, desc, priority in automation_strategies:
        strategies.append(
            Strategy(
                id=sid, name=name, category=StrategyCategory.AUTOMATION,
                description=desc, priority=priority,
                applicable_categories=["all"],
            )
        )
        sid += 1

    # (C) INTEGRATIONS — 25 strategies
    integration_strategies = [
        ("Slack Integration", "Send bot alerts and reports to Slack", 8),
        ("Discord Integration", "Connect bots to Discord communities", 7),
        ("Stripe Integration", "Process payments via Stripe", 9),
        ("Twilio SMS", "Send SMS messages via Twilio", 9),
        ("Google Analytics", "Track bot performance in Google Analytics", 7),
        ("HubSpot CRM", "Sync leads and deals with HubSpot", 8),
        ("Salesforce CRM", "Integrate with Salesforce for enterprise clients", 7),
        ("Zapier Webhooks", "Trigger Zapier workflows from bot events", 7),
        ("GitHub Actions", "Deploy bots via GitHub Actions CI/CD", 9),
        ("AWS S3 Storage", "Store bot data and artifacts in S3", 7),
        ("OpenAI API", "Enhance bot intelligence via OpenAI models", 9),
        ("SendGrid Email", "Send transactional emails via SendGrid", 8),
        ("Google Calendar", "Book appointments via Google Calendar", 7),
        ("PayPal Integration", "Accept PayPal payments", 7),
        ("Shopify Integration", "Connect to Shopify for e-commerce bots", 6),
        ("LinkedIn API", "Scrape leads from LinkedIn", 8),
        ("Twitter/X API", "Monitor and engage on Twitter/X", 6),
        ("Airtable", "Use Airtable as a lightweight CRM/database", 7),
        ("Notion API", "Sync data with Notion workspaces", 6),
        ("Plaid Financial", "Integrate financial data via Plaid", 6),
        ("Twilio Voice", "Automated voice calls via Twilio", 8),
        ("Google Sheets", "Log data to Google Sheets", 7),
        ("Mailchimp", "Sync leads with Mailchimp campaigns", 6),
        ("Firebase", "Real-time database and auth via Firebase", 7),
        ("API Gateway", "Expose bot capabilities via REST API", 8),
    ]
    for name, desc, priority in integration_strategies:
        strategies.append(
            Strategy(
                id=sid, name=name, category=StrategyCategory.INTEGRATIONS,
                description=desc, priority=priority,
                applicable_categories=["all"],
            )
        )
        sid += 1

    # (D) UX — 25 strategies
    ux_strategies = [
        ("Simple Onboarding", "Streamlined onboarding with minimal steps", 9),
        ("Interactive Tutorials", "Step-by-step tutorials for new users", 8),
        ("Real-Time Status Indicators", "Show live progress and status", 8),
        ("Responsive UI", "Mobile-friendly, responsive interface design", 8),
        ("Dark Mode Support", "Offer dark mode for better usability", 6),
        ("Keyboard Shortcuts", "Power-user keyboard shortcuts", 6),
        ("Error Messages UX", "Clear, actionable error messages", 9),
        ("Progress Bars", "Visual progress indicators for long tasks", 8),
        ("Dashboard Overview", "Single-page overview of all key metrics", 9),
        ("Search Functionality", "Fast search across leads, deals, and bots", 7),
        ("Drag-and-Drop", "Drag-and-drop interface for workflow builder", 7),
        ("Notification System", "In-app and push notifications", 7),
        ("User Preferences", "Customizable user settings", 6),
        ("Help Documentation", "Accessible, searchable help docs", 7),
        ("Contextual Tooltips", "Tooltips that explain features in context", 7),
        ("One-Click Actions", "Reduce multi-step actions to one click", 9),
        ("Undo/Redo Support", "Allow users to undo/redo actions", 7),
        ("Data Export", "Export data to CSV/Excel/PDF", 7),
        ("Custom Branding", "White-label branding for enterprise", 7),
        ("Accessibility (A11y)", "WCAG-compliant accessibility features", 7),
        ("Multi-Language Support", "Localization for international users", 6),
        ("Smart Defaults", "Pre-fill forms with intelligent defaults", 8),
        ("Onboarding Checklists", "Interactive checklists to guide first use", 8),
        ("In-App Feedback", "Let users submit feedback without leaving app", 7),
        ("Contextual Help", "Show relevant help based on current screen", 7),
    ]
    for name, desc, priority in ux_strategies:
        strategies.append(
            Strategy(
                id=sid, name=name, category=StrategyCategory.UX,
                description=desc, priority=priority,
                applicable_categories=["all"],
            )
        )
        sid += 1

    # (E) RESILIENCE — 25 strategies
    resilience_strategies = [
        ("Auto-Restart", "Automatically restart crashed bots", 10),
        ("Crash Recovery", "Resume from last checkpoint after crash", 9),
        ("Health Checks", "Periodic health checks for all running bots", 9),
        ("Versioning", "Track and rollback bot versions", 8),
        ("SLA Monitoring", "Monitor and enforce SLA targets", 8),
        ("Graceful Degradation", "Reduce functionality gracefully under load", 8),
        ("Retry Logic", "Auto-retry failed operations with backoff", 9),
        ("Dead Letter Queue", "Route failed tasks to dead letter queue", 7),
        ("Failover", "Switch to backup system on primary failure", 8),
        ("Rate Limit Handling", "Handle API rate limits gracefully", 9),
        ("Data Validation", "Validate all input data before processing", 9),
        ("Error Logging", "Comprehensive error logging with context", 9),
        ("Alerting", "Instant alerts on critical failures", 9),
        ("Backup Systems", "Redundant backups for critical data", 8),
        ("Chaos Testing", "Intentional failure injection to test resilience", 7),
        ("Database Replication", "Replicate DB to prevent data loss", 7),
        ("Memory Leak Detection", "Detect and fix memory leaks automatically", 8),
        ("Resource Monitoring", "Monitor CPU, memory, and disk usage", 8),
        ("Timeout Handling", "Define and enforce operation timeouts", 9),
        ("Idempotency", "Ensure operations are safe to retry", 8),
        ("Blue-Green Deploy", "Zero-downtime deployments via blue-green strategy", 7),
        ("State Persistence", "Persist state across restarts", 9),
        ("Configuration Hot Reload", "Update config without restarts", 7),
        ("Dependency Health", "Monitor health of external dependencies", 8),
        ("Distributed Tracing", "Trace requests across distributed systems", 7),
    ]
    for name, desc, priority in resilience_strategies:
        strategies.append(
            Strategy(
                id=sid, name=name, category=StrategyCategory.RESILIENCE,
                description=desc, priority=priority,
                applicable_categories=["all"],
            )
        )
        sid += 1

    # (F) MONETIZATION — 25 strategies
    monetization_strategies = [
        ("Tiered Pricing", "Offer basic/advanced/enterprise pricing tiers", 10),
        ("Usage-Based Revenue", "Charge based on actual usage volume", 9),
        ("Affiliate Integration", "Earn commissions via affiliate programs", 7),
        ("Freemium Model", "Free tier to drive user acquisition", 8),
        ("Annual Discount", "Offer discounts for annual commitments", 7),
        ("Per-Lead Pricing", "Charge per lead delivered ($50/lead)", 9),
        ("Monthly Retainer", "Sell monthly retainer packages ($300-$2,000)", 10),
        ("Performance Bonuses", "Bonus pricing tied to conversion rates", 7),
        ("White-Label Licensing", "License bot technology to agencies", 7),
        ("API Access Fees", "Charge for API access above free tier", 7),
        ("Premium Features Upsell", "Upsell premium features within the app", 8),
        ("Training & Onboarding", "Charge for onboarding and training services", 6),
        ("Done-For-You Service", "Charge premium for fully managed service", 9),
        ("Referral Program", "Reward users for referring new clients", 7),
        ("Enterprise Contracts", "Long-term enterprise SLA contracts", 8),
        ("Marketplace Listings", "List on marketplaces (Fiverr, Upwork)", 7),
        ("Revenue Sharing", "Share revenue with integration partners", 6),
        ("Credits System", "Pre-paid credits for flexible usage", 7),
        ("SaaS Transition", "Migrate service model to SaaS product", 10),
        ("Niche Specialization", "Command premium pricing for niche expertise", 9),
        ("Outcome-Based Pricing", "Charge only on successful outcomes", 8),
        ("Add-On Modules", "Sell optional add-on modules", 7),
        ("Data Insights Product", "Monetize aggregated market insights", 6),
        ("Co-Marketing Deals", "Revenue from co-marketing partnerships", 6),
        ("Subscription Tiers", "$99/$299/usage for different client needs", 10),
    ]
    for name, desc, priority in monetization_strategies:
        strategies.append(
            Strategy(
                id=sid, name=name, category=StrategyCategory.MONETIZATION,
                description=desc, priority=priority,
                applicable_categories=["all"],
            )
        )
        sid += 1

    # (G) TESTING — 25 strategies
    testing_strategies = [
        ("Unit Tests", "Write unit tests for all bot functions", 10),
        ("Integration Tests", "Test integration with external APIs", 9),
        ("Benchmarking", "Benchmark bot speed and throughput", 8),
        ("A/B Testing", "Run A/B tests on messages and offers", 9),
        ("Regression Tests", "Detect regressions after code changes", 9),
        ("Load Testing", "Test under peak load conditions", 8),
        ("Chaos Testing", "Inject failures to test robustness", 7),
        ("Smoke Tests", "Quick sanity checks after deployment", 8),
        ("Contract Tests", "Test API contracts with external services", 7),
        ("Security Testing", "Scan for vulnerabilities and XSS/injection", 9),
        ("Performance Profiling", "Profile bot performance in production", 8),
        ("Code Coverage", "Maintain >80% code coverage", 8),
        ("End-to-End Tests", "Test complete user workflows end-to-end", 8),
        ("Data Quality Tests", "Validate lead and deal data quality", 8),
        ("Mutation Testing", "Verify test suite detects code mutations", 6),
        ("Snapshot Testing", "Capture and compare output snapshots", 6),
        ("Property-Based Testing", "Generate random inputs to find edge cases", 7),
        ("Canary Releases", "Deploy to small % of users first", 7),
        ("Feature Flags", "Test features with controlled rollouts", 7),
        ("Monitoring as Tests", "Use production monitoring as continuous tests", 8),
        ("Message Quality Tests", "A/B test outreach message effectiveness", 9),
        ("Conversion Rate Tests", "Measure and optimize conversion rates", 9),
        ("Bot Benchmark Suite", "Compare bot metrics against competitors", 8),
        ("Automated Test CI", "Run tests automatically in CI/CD pipeline", 9),
        ("Test Data Management", "Manage and refresh test datasets", 7),
    ]
    for name, desc, priority in testing_strategies:
        strategies.append(
            Strategy(
                id=sid, name=name, category=StrategyCategory.TESTING,
                description=desc, priority=priority,
                applicable_categories=["all"],
            )
        )
        sid += 1

    # (H) INTELLIGENCE — 25 strategies
    intelligence_strategies = [
        ("Continuous Learning Loop", "Improve bot performance from every run", 10),
        ("Competitive Analysis", "Analyze and outperform competitors automatically", 9),
        ("Performance-Based Decisions", "Make decisions based on real performance data", 10),
        ("Market Trend Detection", "Detect market trends from scraped data", 8),
        ("Sentiment Analysis", "Analyze reply sentiment to adjust strategy", 8),
        ("Predictive Lead Scoring", "Predict lead conversion probability via ML", 9),
        ("Revenue Forecasting", "Forecast future revenue from current pipeline", 8),
        ("Churn Prediction", "Predict and prevent client churn", 7),
        ("Dynamic Pricing Engine", "Adjust prices based on demand signals", 7),
        ("NLP-Powered Replies", "Generate intelligent replies using NLP", 9),
        ("Decision Tree Optimization", "Optimize decision trees from outcome data", 8),
        ("Anomaly Detection", "Detect unusual patterns in bot behavior", 8),
        ("Knowledge Graph", "Build a knowledge graph of leads and deals", 7),
        ("Reinforcement Learning", "Improve strategy through reward signals", 7),
        ("Clustering", "Segment leads into behavioral clusters", 7),
        ("Recommendation Engine", "Recommend best next actions to users", 8),
        ("Time Series Analysis", "Analyze performance trends over time", 7),
        ("Natural Language Generation", "Generate human-like outreach messages", 9),
        ("Competitor Gap Analysis", "Identify and exploit competitor weaknesses", 9),
        ("Self-Optimization", "Automatically adjust parameters for better results", 10),
        ("Market Intelligence Dashboard", "Centralized view of all market data", 8),
        ("Win/Loss Analysis", "Analyze why deals are won or lost", 8),
        ("Adaptive Messaging", "Adapt message tone based on lead responses", 9),
        ("Bot Evolution", "Generate improved bot versions from performance data", 8),
        ("Revenue Optimization", "Continuously optimize for maximum revenue", 10),
    ]
    for name, desc, priority in intelligence_strategies:
        strategies.append(
            Strategy(
                id=sid, name=name, category=StrategyCategory.INTELLIGENCE,
                description=desc, priority=priority,
                applicable_categories=["all"],
            )
        )
        sid += 1

    return strategies


# ---------------------------------------------------------------------------
# Strategy Framework
# ---------------------------------------------------------------------------

class StrategyFramework:
    """
    200-Strategy Framework that integrates speed, automation, integrations,
    UX, resilience, monetization, testing, and intelligence strategies into
    every bot's design.
    """

    def __init__(self) -> None:
        self._strategies: list[Strategy] = _build_strategy_catalogue()

    @property
    def total_strategies(self) -> int:
        return len(self._strategies)

    def get_all_strategies(self) -> list[dict]:
        """Return all 200 strategies as dicts."""
        return [s.to_dict() for s in self._strategies]

    def get_by_category(self, category: StrategyCategory) -> list[dict]:
        """Return all strategies for a given category."""
        return [
            s.to_dict()
            for s in self._strategies
            if s.category == category
        ]

    def get_top_strategies(self, n: int = 20, category: Optional[StrategyCategory] = None) -> list[dict]:
        """Return the top N strategies by priority, optionally filtered by category."""
        pool = self._strategies
        if category is not None:
            pool = [s for s in pool if s.category == category]
        return [
            s.to_dict()
            for s in sorted(pool, key=lambda x: x.priority, reverse=True)[:n]
        ]

    def get_strategy_by_id(self, strategy_id: int) -> Optional[dict]:
        """Return a specific strategy by ID."""
        for s in self._strategies:
            if s.id == strategy_id:
                return s.to_dict()
        return None

    def get_recommended_for_bot(self, bot_category: str, top_n: int = 10) -> list[dict]:
        """
        Return the top recommended strategies for a specific bot category.
        Prioritizes intelligence, resilience, and automation for all bots.
        """
        high_priority = [s for s in self._strategies if s.priority >= 9]
        sorted_high = sorted(high_priority, key=lambda x: x.priority, reverse=True)
        return [s.to_dict() for s in sorted_high[:top_n]]

    def get_category_summary(self) -> dict:
        """Return a summary of strategies per category."""
        summary: dict[str, dict] = {}
        for cat in StrategyCategory:
            cat_strategies = [s for s in self._strategies if s.category == cat]
            summary[cat.value] = {
                "count": len(cat_strategies),
                "avg_priority": (
                    round(
                        sum(s.priority for s in cat_strategies) / len(cat_strategies), 2
                    )
                    if cat_strategies
                    else 0.0
                ),
                "top_strategy": (
                    max(cat_strategies, key=lambda x: x.priority).name
                    if cat_strategies
                    else None
                ),
            }
        return summary
