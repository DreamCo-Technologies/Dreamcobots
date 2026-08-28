"""Adaptive questionnaire for selecting capabilities for a user's custom DreamCo page."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Question:
    id: str
    text: str
    choices: tuple[str, ...]
    capability_hints: dict[str, tuple[str, ...]] = field(default_factory=dict)


QUESTIONS = (
    Question("goal", "What are you primarily trying to accomplish?", ("learn", "build", "work", "business", "research", "create", "automate"), {
        "learn": ("tutoring", "study_planning", "knowledge_retrieval"),
        "build": ("coding", "debugging", "architecture", "testing"),
        "work": ("productivity", "documents", "communication", "planning"),
        "business": ("market_research", "sales", "finance", "operations"),
        "research": ("research", "evidence_analysis", "scientific_reasoning"),
        "create": ("writing", "design", "multimodal_generation"),
        "automate": ("workflow_automation", "integration", "scheduling"),
    }),
    Question("reasoning", "Which kinds of reasoning do you expect Buddy to use?", ("general", "math", "code", "geometry", "planning", "causal", "uncertain", "all"), {
        "general": ("logical_reasoning",), "math": ("mathematical_reasoning",), "code": ("program_reasoning",),
        "geometry": ("geometric_reasoning",), "planning": ("planning_reasoning",), "causal": ("causal_reasoning",),
        "uncertain": ("probabilistic_reasoning",), "all": ("reasoning_suite",),
    }),
    Question("data", "What information should the page work with?", ("documents", "web", "databases", "images", "audio", "video", "code", "mixed"), {
        "documents": ("document_analysis",), "web": ("web_research",), "databases": ("data_querying",),
        "images": ("vision",), "audio": ("audio_understanding",), "video": ("video_understanding",),
        "code": ("code_analysis",), "mixed": ("multimodal_reasoning",),
    }),
    Question("automation", "How much should the page automate?", ("assist", "recommend", "execute_with_approval", "automate_safe_tasks"), {
        "assist": ("assistant",), "recommend": ("recommendation",),
        "execute_with_approval": ("approval_workflows", "action_execution"),
        "automate_safe_tasks": ("workflow_automation", "scheduled_tasks", "monitoring"),
    }),
    Question("integrations", "What should it connect to?", ("github", "cloud", "business", "files", "calendar", "none", "custom"), {
        "github": ("github_integration",), "cloud": ("cloud_integration",), "business": ("business_integrations",),
        "files": ("file_management",), "calendar": ("calendar_integration",), "custom": ("integration_discovery",),
    }),
    Question("trust", "How should higher-impact actions be handled?", ("read_only", "ask_first", "policy_gated", "team_approval"), {
        "read_only": ("read_only_mode",), "ask_first": ("approval_gate",),
        "policy_gated": ("governance", "authorization"), "team_approval": ("multi_party_approval",),
    }),
)


def recommend_capabilities(answers: dict[str, str | list[str]]) -> dict[str, Any]:
    """Return ranked capability hints; unknown answers are ignored rather than failing."""
    scores: dict[str, int] = {}
    reasons: dict[str, list[str]] = {}
    for question in QUESTIONS:
        answer = answers.get(question.id)
        values = answer if isinstance(answer, list) else [answer] if answer else []
        for value in values:
            for capability in question.capability_hints.get(value, ()):
                scores[capability] = scores.get(capability, 0) + 1
                reasons.setdefault(capability, []).append(question.id)

    ranked = sorted(scores, key=lambda name: (-scores[name], name))
    return {
        "capabilities": [
            {"capability": name, "score": scores[name], "evidence": reasons[name]}
            for name in ranked
        ],
        "questions": len(QUESTIONS),
        "answered": sum(1 for q in QUESTIONS if answers.get(q.id)),
    }
