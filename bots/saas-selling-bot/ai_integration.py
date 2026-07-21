"""
AI Integration module for the SaaS Selling Bot.
Provides personalised recommendations and chatbot capabilities
using OpenAI's GPT models (with a graceful fallback when no API key is configured).
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import os
import json

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from database import get_all_tools, search_tools, get_categories


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

SYSTEM_PROMPT = """You are SaaSBot, an expert SaaS consultant and selling assistant.
Your job is to help users discover the best free SaaS tools for their needs.
You have access to a catalogue of 200+ free SaaS tools spanning Analytics,
Marketing, Development, Collaboration, Finance, and AI.

When recommending tools:
- Always mention the free tier details.
- Explain why each tool fits the user's use-case.
- Keep recommendations concise (3-5 tools per response).
- Include the affiliate link when suggesting a tool.

Respond in a friendly, professional tone."""


def _fallback_recommend(query: str, tools: list) -> str:
    """Rule-based fallback recommendation when OpenAI is unavailable."""
    query_lower = query.lower()
    keywords = {
        "analytics": ["Analytics"],
        "marketing": ["Marketing"],
        "email": ["Marketing"],
        "dev": ["Development"],
        "code": ["Development"],
        "collab": ["Collaboration"],
        "team": ["Collaboration"],
        "finance": ["Finance"],
        "payment": ["Finance"],
        "ai": ["AI"],
        "machine learning": ["AI"],
        "chatbot": ["AI"],
    }

    matched_categories = set()
    for kw, cats in keywords.items():
        if kw in query_lower:
            matched_categories.update(cats)

    if not matched_categories:
        matched_categories = {"Analytics", "AI", "Development"}

    filtered = [t for t in tools if t["category"] in matched_categories][:5]
    if not filtered:
        filtered = tools[:5]

    lines = [f"Based on your query **\"{query}\"**, here are my top recommendations:\n"]
    for i, t in enumerate(filtered, 1):
        lines.append(
            f"{i}. **{t['name']}** ({t['category']})\n"
            f"   {t['description']}\n"
            f"   💰 Pricing: {t['pricing']}\n"
            f"   🔗 [Get started]({t['affiliate_link']})\n"
        )
    lines.append(
        "\n*(AI-powered recommendations are available when OPENAI_API_KEY is configured.)*"
    )
    return "\n".join(lines)


def get_recommendations(user_query: str, user_context: dict = None) -> str:
    """
    Return personalised tool recommendations for the given query.
    Uses OpenAI GPT when configured, otherwise falls back to rule-based logic.
    """
    all_tools = get_all_tools()
    categories = get_categories()

    if OPENAI_AVAILABLE and OPENAI_API_KEY:
        tool_summary = json.dumps(
            [
                {
                    "name": t["name"],
                    "category": t["category"],
                    "description": t["description"],
                    "pricing": t["pricing"],
                    "affiliate_link": t["affiliate_link"],
                }
                for t in all_tools
            ],
            indent=2,
        )

        context_note = ""
        if user_context:
            context_note = f"\nUser context: {json.dumps(user_context)}"

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Available tools catalogue:\n{tool_summary}\n\n"
                    f"{context_note}\n\n"
                    f"User query: {user_query}"
                ),
            },
        ]

        try:
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=800,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as exc:
            return _fallback_recommend(user_query, all_tools) + f"\n\n*(Error: {exc})*"
    else:
        return _fallback_recommend(user_query, all_tools)


def chatbot_response(conversation_history: list, user_message: str) -> str:
    """
    Generate a chatbot response given a conversation history and a new user message.
    conversation_history: list of {"role": "user"|"assistant", "content": "..."}
    """
    if OPENAI_AVAILABLE and OPENAI_API_KEY:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})

        try:
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=600,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as exc:
            return (
                "I'm SaaSBot! I'm here to help you find the perfect SaaS tools. "
                f"(AI temporarily unavailable: {exc})"
            )
    else:
        all_tools = get_all_tools()
        return _fallback_recommend(user_message, all_tools)


if __name__ == "__main__":
    print("Testing AI integration (fallback mode)...")
    result = get_recommendations("I need tools for email marketing and analytics")
    print(result)
