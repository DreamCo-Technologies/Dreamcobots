"""
Simple keyword-based NLP engine for FAQ responses.
Falls back to OpenAI API when OPENAI_API_KEY is set (optional, free-tier upgrade).
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import os
import re

# ---------------------------------------------------------------------------
# FAQ knowledge base – no external API required
# ---------------------------------------------------------------------------
FAQ_KB = [
    {
        "keywords": ["price", "cost", "pricing", "how much", "fee", "charge"],
        "answer": (
            "Our pricing starts at $99/month for the Starter plan. "
            "The Professional plan is $299/month and the Enterprise plan is custom-quoted. "
            "All plans include a 14-day free trial. Would you like to see a full pricing breakdown?"
        ),
    },
    {
        "keywords": ["custom bot", "custom automation", "custom workflow", "bespoke"],
        "answer": (
            "Custom Bot Development is one of our flagship services. "
            "We build tailored automation workflows that plug directly into your existing tools. "
            "Typical turnaround is 2-4 weeks. Want to book a free discovery call?"
        ),
    },
    {
        "keywords": ["nlp", "chatbot", "natural language", "conversational", "ai bot"],
        "answer": (
            "Our NLP Bots are powered by cutting-edge language models and can handle "
            "customer support, lead qualification, and FAQ automation. "
            "They integrate with your website, Slack, or any messaging platform."
        ),
    },
    {
        "keywords": ["income", "residual", "passive", "tracking", "financial", "revenue", "earnings"],
        "answer": (
            "Our Residual Income Tracking Bots monitor multiple revenue streams in real time, "
            "generate daily reports, and alert you to anomalies. "
            "Perfect for affiliate marketers, SaaS founders, and investors."
        ),
    },
    {
        "keywords": ["government", "contract", "grant", "federal", "sam.gov", "rfp", "proposal"],
        "answer": (
            "Our Government Contract/Grant Bots scan SAM.gov, Grants.gov, and other portals daily "
            "for opportunities matching your keywords and NAICS codes. "
            "They can even draft initial response outlines."
        ),
    },
    {
        "keywords": ["api", "integration", "connect", "webhook", "zapier", "third party"],
        "answer": (
            "API Integration Demos show how we connect disparate systems — CRMs, ERPs, payment "
            "gateways, social platforms — into seamless automated pipelines. "
            "We support REST, GraphQL, and webhooks."
        ),
    },
    {
        "keywords": ["ui", "ux", "frontend", "design", "template", "dashboard", "interface"],
        "answer": (
            "Our UI/UX automation service produces responsive, TailwindCSS-powered dashboards and "
            "client portals. We start from battle-tested templates and customise them for your brand."
        ),
    },
    {
        "keywords": ["trial", "free", "demo", "test", "try"],
        "answer": (
            "Every service on this page has an interactive mini-demo you can try right now — "
            "completely free and no sign-up required. "
            "Just pick a service from the menu and follow the prompts!"
        ),
    },
    {
        "keywords": ["contact", "reach", "talk", "speak", "human", "support", "email", "phone"],
        "answer": (
            "You can reach our team at support@dreamcobots.com or use the Lead Generation form "
            "to request a callback. We typically respond within one business day."
        ),
    },
    {
        "keywords": ["deploy", "hosting", "cloud", "server", "heroku", "dreamco"],
        "answer": (
            "All bots are deployed on cloud infrastructure. "
            "We offer managed hosting on free-tier-compatible platforms "
            "(Heroku, Railway, DreamCo) and can also deploy to your own servers."
        ),
    },
    {
        "keywords": ["secure", "security", "safe", "privacy", "data", "gdpr"],
        "answer": (
            "Security is paramount. All data is encrypted at rest and in transit. "
            "We are GDPR-compliant and never share your data with third parties."
        ),
    },
]

FALLBACK_RESPONSE = (
    "That's a great question! Our team would love to give you a personalised answer. "
    "Please use the Lead Generation form to request a callback, or ask something else — "
    "I'm happy to help with pricing, demos, or service details."
)


def _keyword_score(text: str, keywords: list) -> int:
    """Return the number of keyword matches in text (case-insensitive)."""
    text_lower = text.lower()
    return sum(1 for kw in keywords if re.search(r"\b" + re.escape(kw) + r"\b", text_lower))


def _keyword_faq_response(user_message: str) -> str:
    """Keyword-based FAQ lookup — zero external API calls required."""
    best_entry = None
    best_score = 0
    for entry in FAQ_KB:
        score = _keyword_score(user_message, entry["keywords"])
        if score > best_score:
            best_score = score
            best_entry = entry

    if best_entry and best_score > 0:
        return best_entry["answer"]
    return FALLBACK_RESPONSE


def get_faq_response(user_message: str) -> str:
    """
    Return the best FAQ answer for user_message.
    Optionally delegates to OpenAI when OPENAI_API_KEY is set.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        return _openai_response(user_message, api_key)
    return _keyword_faq_response(user_message)


def _openai_response(user_message: str, api_key: str) -> str:
    """Optional: use OpenAI chat completions for richer responses."""
    try:
        import urllib.request
        import json

        system_prompt = (
            "You are a helpful sales assistant for DreamCobots, a company that provides "
            "custom automation bots, NLP chatbots, income tracking bots, government contract "
            "bots, API integrations, and UI/UX automation services. "
            "Keep responses concise (2-3 sentences) and friendly. "
            "Always end by inviting the user to try a demo or contact sales."
        )
        payload = json.dumps({
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "max_tokens": 150,
        }).encode()

        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"].strip()
    except Exception:
        # Fall back to keyword-based engine when the OpenAI call fails
        return _keyword_faq_response(user_message)
