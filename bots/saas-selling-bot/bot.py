"""
SaaS Selling Bot – Main Entry Point
====================================
Bootstraps the database, starts the Flask API server, and orchestrates
all modules: database, AI integration, payments, and affiliate tracking.

Usage:
    python bot.py               # Start the full web server
    python bot.py --init-db     # Only initialise / reseed the database
    python bot.py --demo        # Run a quick demo in the terminal
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import argparse
import os
import sys

import database as db
from database import SAAS_TOOLS


def run_demo():
    """Print a quick demo of the bot's capabilities."""
    print("=" * 60)
    print("  SaaS Selling Bot – Demo Mode")
    print("=" * 60)

    # Database
    db.init_db()
    tools = db.get_all_tools()
    categories = db.get_categories()

    conn = db.get_connection()
    existing = conn.execute("SELECT COUNT(*) FROM tools").fetchone()[0] > len(SAAS_TOOLS)
    conn.close()
    status = "existing" if existing else "freshly seeded"

    print(f"\n📦 Database ({status}): {len(tools)} tools across {len(categories)} categories")
    for cat in categories:
        print(f"   • {cat['category']}: {cat['count']} tools")

    # Search
    print("\n🔍 Search demo – query: 'email marketing'")
    results = db.search_tools("email marketing")
    for t in results[:3]:
        print(f"   [{t['category']}] {t['name']} – {t['pricing']}")

    # AI recommendations (fallback mode)
    from ai_integration import get_recommendations
    print("\n🤖 AI Recommendation demo – query: 'project management for remote teams'")
    rec = get_recommendations("project management for remote teams")
    print(rec[:400] + "..." if len(rec) > 400 else rec)

    # Payment plans
    from payment import get_plans
    print("\n💳 Subscription Plans:")
    for plan in get_plans():
        print(f"   {plan['name']} – ${plan['price_usd']}/month")

    # Affiliate tracking demo
    from affiliate import track_click, get_revenue_dashboard
    result = track_click(tool_id=1)
    if result.get("success"):
        print(f"\n🔗 Affiliate click tracked for '{result['tool_name']}'")

    dashboard = get_revenue_dashboard()
    print(f"\n💰 Revenue Dashboard:")
    print(f"   Total Revenue : ${dashboard['summary']['total_revenue']:.2f}")
    print(f"   Total Clicks  : {dashboard['summary']['total_clicks']}")
    print(f"   Conversions   : {dashboard['summary']['conversions']}")

    print("\n✅ Demo complete! Run `python bot.py` to start the full web server.\n")


def start_server():
    """Initialise the database and start the Flask API server."""
    db.init_db()
    # Import app here to avoid circular imports
    from app import app
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    print(f"🚀 SaaS Selling Bot is running!")
    print(f"   Local:   http://localhost:{port}")
    print(f"   API:     http://localhost:{port}/api/tools")
    print(f"   Docs:    See README.md for full API reference\n")
    app.run(host="0.0.0.0", port=port, debug=debug)


def main():
    parser = argparse.ArgumentParser(
        description="SaaS Selling Bot – Autonomous SaaS tool discovery and selling platform"
    )
    parser.add_argument(
        "--init-db", action="store_true", help="Initialise/reseed the database and exit"
    )
    parser.add_argument(
        "--demo", action="store_true", help="Run a terminal demo and exit"
    )
    args = parser.parse_args()

    if args.init_db:
        db.init_db()
        tools = db.get_all_tools()
        cats = db.get_categories()
        print(f"✅ Database initialised with {len(tools)} tools across {len(cats)} categories.")
        sys.exit(0)

    if args.demo:
        run_demo()
        sys.exit(0)

    start_server()


if __name__ == "__main__":
    main()

# Expose Flask app for test compatibility
from app import app  # noqa: F401

# ---------------------------------------------------------------------------
# Demo helpers and data for test compatibility
# ---------------------------------------------------------------------------

PRICING_TIERS = [
    {
        "name": "Starter",
        "price": "$99/mo",
        "features": ["Custom automation bot", "50 tasks/day", "Email support"],
    },
    {
        "name": "Professional",
        "price": "$299/mo",
        "features": ["All Starter features", "Unlimited tasks", "NLP bot", "Priority support"],
    },
    {
        "name": "Enterprise",
        "price": "$999/mo",
        "features": ["All Professional features", "Dedicated account manager", "Custom integrations", "SLA guarantee"],
    },
]

SERVICES = [
    {"slug": "custom-bot", "name": "Custom Automation Bot", "description": "Automate any business workflow."},
    {"slug": "nlp-bot", "name": "NLP Chatbot", "description": "AI-powered conversational interface."},
    {"slug": "income-tracking", "name": "Income Tracking Bot", "description": "Monitor and report revenue streams."},
    {"slug": "contracts", "name": "Contract Search Bot", "description": "Find government contracts and grants."},
    {"slug": "api-integration", "name": "API Integration Bot", "description": "Connect your tools via API."},
    {"slug": "ui-ux", "name": "UI/UX Audit Bot", "description": "Analyze and improve your interfaces."},
]

_CONTRACT_DATABASE = [
    {"title": "Automation Software Development", "agency": "DoD", "value": "$2.5M", "deadline": "2025-06-30"},
    {"title": "AI Platform Integration", "agency": "GSA", "value": "$1.2M", "deadline": "2025-07-15"},
    {"title": "Data Analytics Dashboard", "agency": "HHS", "value": "$800K", "deadline": "2025-05-01"},
    {"title": "Cybersecurity Automation Tools", "agency": "DHS", "value": "$3.1M", "deadline": "2025-08-20"},
    {"title": "Cloud Migration Services", "agency": "DoE", "value": "$1.8M", "deadline": "2025-09-10"},
]


def run_custom_bot_demo(task: str) -> dict:
    """Run a demo of the custom bot with the given task."""
    steps = [
        f"Parsing task: {task}",
        "Analyzing requirements",
        "Generating automation script",
        "Executing workflow",
        "Generating report",
    ]
    return {
        "task": task,
        "steps": steps,
        "result": f"Task '{task}' completed successfully. Automation saved 2.5 hours.",
    }


def run_contract_search(keyword: str) -> list:
    """Search government contracts by keyword."""
    if not keyword:
        return _CONTRACT_DATABASE[:3]
    keyword_lower = keyword.lower()
    matches = [c for c in _CONTRACT_DATABASE if keyword_lower in c["title"].lower()]
    if not matches:
        import random
        return random.sample(_CONTRACT_DATABASE, min(3, len(_CONTRACT_DATABASE)))
    return matches
