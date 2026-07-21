"""
Bot Generator Bot — Tool Injector Module

Adds appropriate scraping and processing tool stubs into a bot DNA
dictionary based on the detected industry and goal.  Each tool entry
contains a ``name``, ``description``, and ``stub`` — a minimal Python
code snippet that the template engine can inline into the generated bot.

GLOBAL AI SOURCES FLOW: participates via bot_generator_bot.py pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

@dataclass
class Tool:
    """Represents a single injectable tool."""
    name: str
    description: str
    category: str          # "scraping" | "processing" | "export" | "payment" | "analytics"
    stub: str              # Minimal Python implementation
    requires_api_key: bool = False
    api_key_env_var: Optional[str] = None
    dependencies: list = field(default_factory=list)


_TOOL_REGISTRY: dict[str, Tool] = {
    "google_maps": Tool(
        name="google_maps",
        description="Scrape business listings from Google Maps / Places API.",
        category="scraping",
        stub=(
            "def scrape_google_maps(query: str, location: str, count: int = 20) -> list:\n"
            "    \"\"\"Return simulated Google Maps business leads.\"\"\"\n"
            "    import random\n"
            "    results = []\n"
            "    for i in range(count):\n"
            "        results.append({\n"
            "            'name': f'Business {i} ({query})',\n"
            "            'address': f'{random.randint(100,999)} Main St, {location}',\n"
            "            'phone': f'+1-555-{random.randint(1000,9999)}',\n"
            "            'rating': round(random.uniform(3.0, 5.0), 1),\n"
            "        })\n"
            "    return results\n"
        ),
        requires_api_key=True,
        api_key_env_var="GOOGLE_MAPS_API_KEY",
        dependencies=["requests"],
    ),
    "email_finder": Tool(
        name="email_finder",
        description="Discover and validate professional email addresses.",
        category="processing",
        stub=(
            "def find_email(first: str, last: str, domain: str) -> str:\n"
            "    \"\"\"Return a probable professional email address.\"\"\"\n"
            "    patterns = [\n"
            "        f'{first.lower()}.{last.lower()}@{domain}',\n"
            "        f'{first[0].lower()}{last.lower()}@{domain}',\n"
            "        f'{first.lower()}@{domain}',\n"
            "    ]\n"
            "    return patterns[0]  # swap with Hunter.io / Snov.io API call\n"
        ),
        requires_api_key=False,
        dependencies=[],
    ),
    "zillow_scraper": Tool(
        name="zillow_scraper",
        description="Scrape real-estate listings from Zillow.",
        category="scraping",
        stub=(
            "def scrape_zillow(location: str, listing_type: str = 'for_sale', count: int = 10) -> list:\n"
            "    \"\"\"Return simulated Zillow property listings.\"\"\"\n"
            "    import random\n"
            "    return [\n"
            "        {\n"
            "            'address': f'{random.randint(100,999)} Oak Ave, {location}',\n"
            "            'price': random.randint(200_000, 2_000_000),\n"
            "            'beds': random.randint(2, 6),\n"
            "            'baths': random.randint(1, 4),\n"
            "            'sqft': random.randint(800, 4_000),\n"
            "            'listing_type': listing_type,\n"
            "        }\n"
            "        for _ in range(count)\n"
            "    ]\n"
        ),
        requires_api_key=False,
        dependencies=["requests", "beautifulsoup4"],
    ),
    "mls_api": Tool(
        name="mls_api",
        description="Query MLS (Multiple Listing Service) data via Spark API.",
        category="scraping",
        stub=(
            "def query_mls(zip_code: str, status: str = 'Active') -> list:\n"
            "    \"\"\"Return MLS listings for a zip code via the Spark API.\"\"\"\n"
            "    import os\n"
            "    import requests\n"
            "    api_key = os.environ.get('MLS_API_KEY', '')\n"
            "    if not api_key:\n"
            "        return []\n"
            "    try:\n"
            "        headers = {\n"
            "            'Authorization': f'Bearer {api_key}',\n"
            "            'Accept': 'application/json',\n"
            "        }\n"
            "        params = {\n"
            "            '_filter': f\"PostalCode Eq '{zip_code}' And StandardStatus Eq '{status}'\",\n"
            "            '_limit': 25,\n"
            "        }\n"
            "        resp = requests.get(\n"
            "            'https://sparkapi.com/v1/listings',\n"
            "            headers=headers,\n"
            "            params=params,\n"
            "            timeout=10,\n"
            "        )\n"
            "        if resp.status_code == 200:\n"
            "            return resp.json().get('D', {}).get('Results', [])\n"
            "    except Exception:\n"
            "        pass\n"
            "    return []\n"
        ),
        requires_api_key=True,
        api_key_env_var="MLS_API_KEY",
        dependencies=["requests"],
    ),
    "yelp_scraper": Tool(
        name="yelp_scraper",
        description="Retrieve business data from the Yelp Fusion API.",
        category="scraping",
        stub=(
            "def scrape_yelp(term: str, location: str, limit: int = 20) -> list:\n"
            "    \"\"\"Return business listings from Yelp.\"\"\"\n"
            "    import random\n"
            "    return [\n"
            "        {\n"
            "            'name': f'{term.title()} Pro #{i}',\n"
            "            'location': location,\n"
            "            'rating': round(random.uniform(3.0, 5.0), 1),\n"
            "            'review_count': random.randint(5, 500),\n"
            "            'phone': f'+1-555-{random.randint(1000,9999)}',\n"
            "        }\n"
            "        for i in range(limit)\n"
            "    ]\n"
        ),
        requires_api_key=True,
        api_key_env_var="YELP_API_KEY",
        dependencies=["requests"],
    ),
    "linkedin_scraper": Tool(
        name="linkedin_scraper",
        description="Scrape professional profiles and company data from LinkedIn.",
        category="scraping",
        stub=(
            "def scrape_linkedin(search_query: str, count: int = 10) -> list:\n"
            "    \"\"\"Return simulated LinkedIn profile data.\"\"\"\n"
            "    return [\n"
            "        {\n"
            "            'name': f'Professional {i}',\n"
            "            'title': 'Manager',\n"
            "            'company': f'Company {i}',\n"
            "            'url': f'https://linkedin.com/in/professional-{i}',\n"
            "        }\n"
            "        for i in range(count)\n"
            "    ]\n"
        ),
        requires_api_key=False,
        dependencies=["selenium", "playwright"],
    ),
    "stripe_api": Tool(
        name="stripe_api",
        description="Accept payments, manage subscriptions, and handle webhooks via Stripe.",
        category="payment",
        stub=(
            "def create_checkout_session(plan: str, customer_email: str, success_url: str, cancel_url: str) -> str:\n"
            "    \"\"\"Create a Stripe checkout session and return the URL.\"\"\"\n"
            "    import os\n"
            "    # import stripe  # pip install stripe\n"
            "    # stripe.api_key = os.environ['STRIPE_SECRET_KEY']\n"
            "    # session = stripe.checkout.Session.create(\n"
            "    #     payment_method_types=['card'],\n"
            "    #     line_items=[{'price': PLAN_PRICE_IDS[plan], 'quantity': 1}],\n"
            "    #     mode='subscription',\n"
            "    #     customer_email=customer_email,\n"
            "    #     success_url=success_url,\n"
            "    #     cancel_url=cancel_url,\n"
            "    # )\n"
            "    # return session.url\n"
            "    return f'https://checkout.stripe.com/pay/simulated_{plan}'\n"
        ),
        requires_api_key=True,
        api_key_env_var="STRIPE_SECRET_KEY",
        dependencies=["stripe"],
    ),
    "analytics_tracker": Tool(
        name="analytics_tracker",
        description="Track leads generated, revenue earned, and bot performance metrics.",
        category="analytics",
        stub=(
            "def track_event(event: str, properties: dict) -> None:\n"
            "    \"\"\"Log an analytics event.\"\"\"\n"
            "    import json\n"
            "    from datetime import datetime, timezone\n"
            "    entry = {'event': event, 'properties': properties, 'ts': datetime.now(timezone.utc).isoformat()}\n"
            "    print(f'[ANALYTICS] {json.dumps(entry)}')\n"
        ),
        requires_api_key=False,
        dependencies=[],
    ),
    "email_sender": Tool(
        name="email_sender",
        description="Send automated outreach emails via SendGrid or SMTP.",
        category="export",
        stub=(
            "def send_email(to: str, subject: str, body: str) -> bool:\n"
            "    \"\"\"Send an email; returns True on success.\"\"\"\n"
            "    # Configure via SENDGRID_API_KEY or SMTP env vars\n"
            "    print(f'[EMAIL] To: {to} | Subject: {subject}')\n"
            "    return True\n"
        ),
        requires_api_key=True,
        api_key_env_var="SENDGRID_API_KEY",
        dependencies=["sendgrid"],
    ),
    "invoice_generator": Tool(
        name="invoice_generator",
        description="Generate PDF invoices for lead purchases and subscriptions.",
        category="payment",
        stub=(
            "def generate_invoice(customer: str, amount: float, items: list) -> str:\n"
            "    \"\"\"Return a simulated invoice ID.\"\"\"\n"
            "    import uuid\n"
            "    invoice_id = str(uuid.uuid4())[:8].upper()\n"
            "    print(f'[INVOICE] #{invoice_id} | {customer} | ${amount:.2f}')\n"
            "    return invoice_id\n"
        ),
        requires_api_key=False,
        dependencies=[],
    ),
    "google_places": Tool(
        name="google_places",
        description="Fetch place details (address, phone, hours) from Google Places API.",
        category="scraping",
        stub=(
            "def get_place_details(place_id: str) -> dict:\n"
            "    \"\"\"Return place details from Google Places API.\"\"\"\n"
            "    return {'place_id': place_id, 'name': 'Sample Place', 'phone': '+1-555-0000'}\n"
        ),
        requires_api_key=True,
        api_key_env_var="GOOGLE_PLACES_API_KEY",
        dependencies=["requests"],
    ),
    "twitter_scraper": Tool(
        name="twitter_scraper",
        description="Search tweets and profiles via the Twitter/X API v2.",
        category="scraping",
        stub=(
            "def search_twitter(query: str, count: int = 10) -> list:\n"
            "    \"\"\"Return tweets/profiles from the Twitter API v2.\"\"\"\n"
            "    import os\n"
            "    import requests\n"
            "    bearer = os.environ.get('TWITTER_BEARER_TOKEN', '')\n"
            "    if not bearer:\n"
            "        return []\n"
            "    try:\n"
            "        headers = {'Authorization': f'Bearer {bearer}'}\n"
            "        params = {\n"
            "            'query': query,\n"
            "            'max_results': min(count, 100),\n"
            "            'tweet.fields': 'author_id,text,created_at',\n"
            "        }\n"
            "        resp = requests.get(\n"
            "            'https://api.twitter.com/2/tweets/search/recent',\n"
            "            headers=headers,\n"
            "            params=params,\n"
            "            timeout=10,\n"
            "        )\n"
            "        if resp.status_code == 200:\n"
            "            data = resp.json()\n"
            "            return [\n"
            "                {\n"
            "                    'id': t['id'],\n"
            "                    'text': t['text'],\n"
            "                    'author_id': t.get('author_id', ''),\n"
            "                    'created_at': t.get('created_at', ''),\n"
            "                }\n"
            "                for t in data.get('data', [])\n"
            "            ]\n"
            "    except Exception:\n"
            "        pass\n"
            "    return []\n"
        ),
        requires_api_key=True,
        api_key_env_var="TWITTER_BEARER_TOKEN",
        dependencies=["requests"],
    ),
    "dashboard_renderer": Tool(
        name="dashboard_renderer",
        description="Render analytics summaries as HTML dashboard snippets.",
        category="analytics",
        stub=(
            "def render_dashboard(data: dict) -> str:\n"
            "    \"\"\"Return a minimal HTML representation of analytics data.\"\"\"\n"
            "    rows = ''.join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in data.items())\n"
            "    return f'<table>{rows}</table>'\n"
        ),
        requires_api_key=False,
        dependencies=[],
    ),
}


# ---------------------------------------------------------------------------
# Tool Injector
# ---------------------------------------------------------------------------

class ToolInjector:
    """
    Injects tool stubs into a bot DNA dictionary.

    Usage::

        injector = ToolInjector()
        dna = {"industry": "real_estate", "tools": ["google_maps", "zillow_scraper"]}
        enriched_dna = injector.inject(dna)
    """

    def inject(self, dna: dict) -> dict:
        """
        Resolve each tool name in *dna["tools"]* to a full :class:`Tool`
        object and attach the resolved tools list back to the DNA.

        Parameters
        ----------
        dna : dict
            Bot DNA dict (from :meth:`BotIntent.to_dna`).  Must contain a
            ``"tools"`` key with a list of tool name strings.

        Returns
        -------
        dict
            Updated DNA with ``"resolved_tools"`` key added.
        """
        tool_names: list[str] = dna.get("tools", [])
        resolved = []
        missing = []

        for name in tool_names:
            if name in _TOOL_REGISTRY:
                tool = _TOOL_REGISTRY[name]
                resolved.append({
                    "name": tool.name,
                    "description": tool.description,
                    "category": tool.category,
                    "stub": tool.stub,
                    "requires_api_key": tool.requires_api_key,
                    "api_key_env_var": tool.api_key_env_var,
                    "dependencies": tool.dependencies,
                })
            else:
                missing.append(name)

        updated_dna = dict(dna)
        updated_dna["resolved_tools"] = resolved
        updated_dna["missing_tools"] = missing
        return updated_dna

    def list_available_tools(self) -> list:
        """Return metadata for all registered tools."""
        return [
            {"name": t.name, "description": t.description, "category": t.category}
            for t in _TOOL_REGISTRY.values()
        ]

    def get_tool(self, name: str) -> Optional[Tool]:
        """Return a :class:`Tool` by name, or ``None`` if not found."""
        return _TOOL_REGISTRY.get(name)

    def tools_for_category(self, category: str) -> list:
        """Return all tools matching a given category."""
        return [t for t in _TOOL_REGISTRY.values() if t.category == category]
