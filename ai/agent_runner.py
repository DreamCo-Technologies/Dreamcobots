"""
DreamCo Agent Runner — Top-level agent execution example.

Demonstrates the full Task → Classify → Route → Execute → Action loop:

    Task
     → TaskClassifier (classify task type)
     → ModelRouter    (select best AI provider)
     → LLM stub       (produce response)
     → ResourceManager (take real-world action)

Usage
-----
    python ai/agent_runner.py
    # or:
    from ai.agent_runner import run
    result = run("build a lead generation system")

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import GlobalAISourcesFlow  # noqa: F401
from ai.router_agent import RouterAgent
from tools.resource_manager import ResourceManager


# ---------------------------------------------------------------------------
# Module-level agent / resource instances (re-used across calls)
# ---------------------------------------------------------------------------

_agent = RouterAgent()
_resources = ResourceManager()


# ---------------------------------------------------------------------------
# run()
# ---------------------------------------------------------------------------

def run(task: str, email: str = "client@example.com") -> dict:
    """Execute a full agent cycle for *task*.

    Steps
    -----
    1. Route the task to the best AI provider via :class:`RouterAgent`.
    2. Simulate a real-world action via :class:`ResourceManager`.

    Parameters
    ----------
    task : str
        Raw task or prompt text.
    email : str
        Email address used for the simulated outreach action.

    Returns
    -------
    dict
        ``{"agent_result": dict, "action_result": dict}``
    """
    agent_result = _agent.run(task)

    # Choose resource tool based on task type
    task_type = agent_result.get("task_type", "general")
    tool_map: dict[str, tuple[str, dict]] = {
        "coding":    ("data",    {"source": "github", "query": task}),
        "search":    ("data",    {"source": "web",    "query": task}),
        "real_time": ("data",    {"source": "feed",   "query": task}),
        "vision":    ("data",    {"source": "vision", "query": task}),
    }
    tool_name, tool_payload = tool_map.get(
        task_type,
        ("email", {"email": email, "subject": f"DreamCo Agent: {task[:60]}"}),
    )
    action_result = _resources.use(tool_name, tool_payload)

    return {
        "agent_result": agent_result,
        "action_result": action_result,
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    demo_tasks = [
        "build a lead generation system",
        "search for top real estate deals",
        "send a proposal email to the client",
        "generate a vision report from the uploaded photos",
        "get live trending topics on social media",
    ]

    for demo_task in demo_tasks:
        result = run(demo_task)
        ar = result["agent_result"]
        print(f"Task      : {ar['task']}")
        print(f"Type      : {ar['task_type']}")
        print(f"Provider  : {ar['model']}")
        print(f"Response  : {ar['response']}")
        print(f"Action    : {result['action_result']}")
        print("-" * 60)
