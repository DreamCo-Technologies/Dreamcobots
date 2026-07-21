#!/usr/bin/env python3
"""Generate Buddy's professional free-first API model router."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ROUTER_JSON = ROOT / "config" / "generated" / "buddy_professional_api_router.json"
FREE_JSON = ROOT / "config" / "generated" / "buddy_free_model_task_library.json"
ROUTER_MD = ROOT / "reports" / "BUDDY_PROFESSIONAL_API_ROUTER.md"
FREE_MD = ROOT / "reports" / "BUDDY_FREE_MODEL_TASK_LIBRARY.md"


FREE_MODEL_POOL = [
    ("llama-3.1-8b-instruct", "Meta", "open_weight_local", ["general_chat", "summarization", "customer_support"]),
    ("llama-3.1-70b-instruct", "Meta", "open_weight_local", ["reasoning", "planning", "business_strategy"]),
    ("llama-3.2-vision-11b", "Meta", "open_weight_local", ["vision", "image_understanding", "document_review"]),
    ("llama-3.3-70b-instruct", "Meta", "open_weight_local", ["reasoning", "coding_review", "long_form_writing"]),
    ("mistral-7b-instruct", "Mistral", "open_weight_local", ["fast_chat", "summarization", "classification"]),
    ("mixtral-8x7b-instruct", "Mistral", "open_weight_local", ["reasoning", "multilingual", "workflow_planning"]),
    ("mixtral-8x22b-instruct", "Mistral", "open_weight_local", ["complex_writing", "analysis", "planning"]),
    ("mistral-nemo-instruct", "Mistral", "open_weight_local", ["multilingual", "customer_support", "summarization"]),
    ("qwen2.5-7b-instruct", "Qwen", "open_weight_local", ["general_chat", "coding_help", "translation"]),
    ("qwen2.5-14b-instruct", "Qwen", "open_weight_local", ["reasoning", "analysis", "structured_outputs"]),
    ("qwen2.5-32b-instruct", "Qwen", "open_weight_local", ["coding", "math", "planning"]),
    ("qwen2.5-72b-instruct", "Qwen", "open_weight_local", ["advanced_reasoning", "multilingual", "business_analysis"]),
    ("qwen2.5-coder-7b", "Qwen", "open_weight_local", ["coding", "debugging", "test_generation"]),
    ("qwen2.5-coder-14b", "Qwen", "open_weight_local", ["coding", "repo_review", "tool_building"]),
    ("qwen2.5-coder-32b", "Qwen", "open_weight_local", ["advanced_coding", "debugging", "refactoring"]),
    ("deepseek-coder-6.7b-instruct", "DeepSeek", "open_weight_local", ["coding", "debugging", "code_explanation"]),
    ("deepseek-coder-v2-lite", "DeepSeek", "open_weight_local", ["coding", "agent_tools", "repo_tasks"]),
    ("deepseek-r1-distill-qwen-7b", "DeepSeek", "open_weight_local", ["reasoning", "math", "verification"]),
    ("deepseek-r1-distill-qwen-14b", "DeepSeek", "open_weight_local", ["reasoning", "planning", "rubric_eval"]),
    ("deepseek-r1-distill-llama-70b", "DeepSeek", "open_weight_local", ["hard_reasoning", "debate", "decision_support"]),
    ("gemma-2-2b-it", "Google", "open_weight_local", ["small_device_chat", "classification", "drafting"]),
    ("gemma-2-9b-it", "Google", "open_weight_local", ["chat", "summarization", "content"]),
    ("gemma-2-27b-it", "Google", "open_weight_local", ["analysis", "long_form", "planning"]),
    ("codegemma-7b-it", "Google", "open_weight_local", ["coding", "code_review", "tool_scripts"]),
    ("phi-3.5-mini-instruct", "Microsoft", "open_weight_local", ["small_device_chat", "fast_drafts", "classification"]),
    ("phi-3.5-moe-instruct", "Microsoft", "open_weight_local", ["reasoning", "summarization", "planning"]),
    ("phi-3.5-vision-instruct", "Microsoft", "open_weight_local", ["vision", "image_qa", "screenshots"]),
    ("phi-4-mini-instruct", "Microsoft", "open_weight_local", ["fast_reasoning", "coding_help", "education"]),
    ("yi-1.5-9b-chat", "01.AI", "open_weight_local", ["chat", "writing", "summarization"]),
    ("yi-1.5-34b-chat", "01.AI", "open_weight_local", ["analysis", "multilingual", "long_form"]),
    ("command-r", "Cohere", "free_tier_or_local_adapter", ["rag", "retrieval", "enterprise_search"]),
    ("command-r-plus", "Cohere", "free_tier_or_local_adapter", ["rag", "research", "summarization"]),
    ("jina-embeddings-v2", "Jina AI", "open_weight_local", ["embeddings", "semantic_search", "memory"]),
    ("bge-large-en-v1.5", "BAAI", "open_weight_local", ["embeddings", "retrieval", "ranking"]),
    ("bge-m3", "BAAI", "open_weight_local", ["multilingual_embeddings", "hybrid_search", "memory"]),
    ("e5-large-v2", "Microsoft", "open_weight_local", ["embeddings", "semantic_search", "classification"]),
    ("nomic-embed-text", "Nomic", "open_weight_local", ["embeddings", "local_memory", "search"]),
    ("gte-large", "Alibaba", "open_weight_local", ["embeddings", "retrieval", "clustering"]),
    ("colbertv2", "Stanford", "open_weight_local", ["reranking", "search", "evidence"]),
    ("bge-reranker-large", "BAAI", "open_weight_local", ["reranking", "rag_quality", "source_selection"]),
    ("whisper-large-v3", "OpenAI", "open_weight_local", ["speech_transcription", "audio_notes", "captions"]),
    ("whisper-small", "OpenAI", "open_weight_local", ["fast_transcription", "captions", "voice_notes"]),
    ("faster-whisper", "SYSTRAN", "open_source_runtime", ["speech_transcription", "batch_audio", "local_cpu_gpu"]),
    ("wav2vec2-base-960h", "Meta", "open_weight_local", ["speech_recognition", "audio_classification", "voice_features"]),
    ("coqui-tts", "Coqui", "open_source_runtime", ["text_to_speech", "voice_lab", "local_audio"]),
    ("piper-tts", "Rhasspy", "open_source_runtime", ["fast_tts", "local_voice", "offline_voice"]),
    ("bark-small", "Suno", "open_weight_local", ["creative_tts", "audio_experiment", "voice_style"]),
    ("musicgen-small", "Meta", "open_weight_local", ["music_generation", "jingles", "song_sketch"]),
    ("musicgen-medium", "Meta", "open_weight_local", ["music_generation", "soundtrack", "loop_creation"]),
    ("audiocraft", "Meta", "open_source_runtime", ["audio_generation", "sound_effects", "music"]),
    ("stable-diffusion-xl", "Stability AI", "open_weight_local", ["image_generation", "marketing_images", "concept_art"]),
    ("stable-diffusion-3-medium", "Stability AI", "open_weight_local", ["image_generation", "design", "assets"]),
    ("flux.1-schnell", "Black Forest Labs", "open_weight_local", ["fast_image_generation", "concepts", "mockups"]),
    ("flux.1-dev", "Black Forest Labs", "research_weight_local", ["high_quality_images", "brand_mockups", "visual_exploration"]),
    ("kandinsky-3", "Kandinsky", "open_weight_local", ["image_generation", "style_transfer", "creative_assets"]),
    ("pixart-alpha", "PixArt", "open_weight_local", ["image_generation", "posters", "visual_drafts"]),
    ("deepfloyd-if", "DeepFloyd", "open_weight_local", ["image_generation", "prompt_testing", "creative"]),
    ("controlnet", "Open Source", "open_weight_local", ["image_control", "pose_guidance", "layout_guidance"]),
    ("segment-anything", "Meta", "open_weight_local", ["image_segmentation", "photo_editing", "vision_tools"]),
    ("sam-2", "Meta", "open_weight_local", ["video_segmentation", "object_tracking", "editing"]),
    ("clip-vit-large", "OpenAI", "open_weight_local", ["image_search", "classification", "moderation_assist"]),
    ("blip-2", "Salesforce", "open_weight_local", ["image_captioning", "visual_qa", "accessibility"]),
    ("llava-1.6", "LLaVA", "open_weight_local", ["vision_chat", "screenshot_analysis", "image_reasoning"]),
    ("moondream2", "Moondream", "open_weight_local", ["lightweight_vision", "image_qa", "device_tasks"]),
    ("kosmos-2", "Microsoft", "open_weight_local", ["vision_language", "grounding", "image_explanation"]),
    ("owl-vit", "Google", "open_weight_local", ["object_detection", "visual_search", "inventory"]),
    ("yolo-v8", "Ultralytics", "open_source_runtime", ["object_detection", "video_detection", "inspection"]),
    ("opencv", "OpenCV", "open_source_runtime", ["computer_vision", "face_detection_local", "image_processing"]),
    ("tesseract-ocr", "Tesseract", "open_source_runtime", ["ocr", "document_text", "receipts"]),
    ("easyocr", "JaidedAI", "open_source_runtime", ["ocr", "multilingual_text", "forms"]),
    ("layoutlmv3", "Microsoft", "open_weight_local", ["document_ai", "forms", "layout_understanding"]),
    ("donut-base", "NAVER", "open_weight_local", ["document_parsing", "receipts", "invoices"]),
    ("nougat", "Meta", "open_weight_local", ["scientific_pdf", "math_documents", "paper_extraction"]),
    ("spacy", "Explosion", "open_source_runtime", ["ner", "text_pipeline", "classification"]),
    ("presidio", "Microsoft", "open_source_runtime", ["pii_detection", "privacy", "redaction"]),
    ("rasa", "Rasa", "open_source_runtime", ["chatbot_flows", "intent_detection", "dialog_manager"]),
    ("haystack", "deepset", "open_source_runtime", ["rag_pipeline", "search", "qa"]),
    ("langchain", "LangChain", "open_source_runtime", ["agent_orchestration", "tools", "workflows"]),
    ("llamaindex", "LlamaIndex", "open_source_runtime", ["rag", "document_agents", "knowledge_graph"]),
    ("autogen", "Microsoft", "open_source_runtime", ["multi_agent", "debate", "workflow_agents"]),
    ("crewai", "CrewAI", "open_source_runtime", ["multi_agent", "role_agents", "business_workflows"]),
    ("semantic-kernel", "Microsoft", "open_source_runtime", ["agent_framework", "plugins", "enterprise"]),
    ("ollama", "Ollama", "open_source_runtime", ["local_model_runner", "free_local_inference", "model_switching"]),
    ("llama.cpp", "GGML", "open_source_runtime", ["local_inference", "quantized_models", "offline"]),
    ("vllm", "vLLM", "open_source_runtime", ["fast_inference", "server", "batching"]),
    ("text-generation-inference", "Hugging Face", "open_source_runtime", ["model_server", "inference", "deployment"]),
    ("open-webui", "Open WebUI", "open_source_runtime", ["chat_ui", "local_models", "admin"]),
    ("anythingllm", "Mintplex", "open_source_runtime", ["local_rag_ui", "documents", "workspace_chat"]),
    ("supabase-free", "Supabase", "free_tier_service", ["auth", "database", "storage"]),
    ("firebase-free", "Google", "free_tier_service", ["auth", "realtime_db", "hosting"]),
    ("cloudflare-workers-free", "Cloudflare", "free_tier_service", ["edge_api", "workers", "static_hosting"]),
    ("github-pages-free", "GitHub", "free_tier_service", ["static_hosting", "docs", "demo_site"]),
    ("vercel-free", "Vercel", "free_tier_service", ["frontend_hosting", "previews", "serverless_light"]),
    ("netlify-free", "Netlify", "free_tier_service", ["static_hosting", "forms_light", "previews"]),
    ("render-free", "Render", "free_tier_service", ["prototype_backend", "web_service", "cron_light"]),
    ("railway-trial", "Railway", "free_trial_or_credit", ["prototype_backend", "database", "workers"]),
    ("neon-free", "Neon", "free_tier_service", ["postgres", "branching", "serverless_db"]),
    ("turso-free", "Turso", "free_tier_service", ["sqlite_edge", "local_first_db", "replication"]),
    ("duckdb", "DuckDB", "open_source_runtime", ["local_analytics", "data_extraction", "spreadsheet_analysis"]),
    ("sqlite-vec", "SQLite", "open_source_runtime", ["local_vectors", "memory_curation", "semantic_search"]),
]


TASKS = [
    "general_chat", "coding", "debugging", "repo_review", "tool_building", "api_router_design",
    "workflow_automation", "customer_support", "sales_copy", "business_strategy", "market_research",
    "competitor_analysis", "lead_research_packet", "grant_contract_research", "document_summary",
    "legal_safety_review", "financial_analysis_draft", "data_extraction", "dashboard_building",
    "spreadsheet_analysis", "rag_search", "memory_curation", "embeddings", "reranking",
    "semantic_search", "speech_transcription", "voice_notes", "text_to_speech", "voice_clone_readiness",
    "music_generation", "song_sketch", "sound_effects", "image_generation", "image_editing",
    "image_captioning", "vision_chat", "screenshot_analysis", "object_detection", "image_segmentation",
    "ocr", "document_ai", "pdf_extraction", "privacy_redaction", "chatbot_flow_builder",
    "agent_orchestration", "multi_agent_debate", "local_model_runner", "local_inference_server",
    "frontend_hosting", "backend_prototype", "database_free_tier", "auth_free_tier",
]

PREFERRED_BY_TASK = {
    "database_free_tier": ["supabase-free", "neon-free", "turso-free", "duckdb", "sqlite-vec"],
    "auth_free_tier": ["supabase-free", "firebase-free", "cloudflare-workers-free"],
    "frontend_hosting": ["github-pages-free", "cloudflare-workers-free", "vercel-free", "netlify-free"],
    "backend_prototype": ["cloudflare-workers-free", "render-free", "firebase-free", "supabase-free"],
    "local_model_runner": ["ollama", "llama.cpp", "vllm", "open-webui", "anythingllm"],
    "local_inference_server": ["vllm", "text-generation-inference", "llama.cpp", "ollama"],
    "semantic_search": ["sqlite-vec", "nomic-embed-text", "bge-m3", "jina-embeddings-v2"],
    "voice_clone_readiness": ["coqui-tts", "piper-tts", "whisper-small", "wav2vec2-base-960h"],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def score_model(task: str, model: dict[str, Any]) -> int:
    preferred = PREFERRED_BY_TASK.get(task, [])
    if model["id"] in preferred:
        return 100 - preferred.index(model["id"])
    tags = " ".join(model["best_for"]).lower()
    task_words = [word for word in task.replace("_", " ").split() if word not in {"free", "tier"}]
    score = sum(3 for word in task_words if word in tags)
    if task in model["best_for"]:
        score += 10
    if "coding" in task and any(term in tags for term in ["coding", "code", "repo"]):
        score += 5
    if "image" in task and any(term in tags for term in ["image", "vision", "photo"]):
        score += 5
    if "voice" in task and any(term in tags for term in ["voice", "tts", "speech"]):
        score += 5
    if "music" in task or "song" in task:
        if any(term in tags for term in ["music", "audio", "song"]):
            score += 5
    if "free" in model["access"]:
        score += 2
    if "open" in model["access"] or "local" in model["access"]:
        score += 3
    return score


def model_records() -> list[dict[str, Any]]:
    return [
        {
            "rank": index + 1,
            "id": model_id,
            "provider": provider,
            "access": access,
            "best_for": best_for,
            "cost_mode": "free_or_local_first",
            "caveat": "Free means local/open-weight/free-tier where available; license, hardware, and rate limits must be checked before production.",
        }
        for index, (model_id, provider, access, best_for) in enumerate(FREE_MODEL_POOL[:100])
    ]


def task_routes(models: list[dict[str, Any]]) -> list[dict[str, Any]]:
    routes = []
    for task in TASKS:
        ranked = sorted(models, key=lambda item: (-score_model(task, item), item["rank"]))
        picks = ranked[:5]
        routes.append(
            {
                "task_type": task,
                "user_choice_mode": "free_first",
                "primary_free_model": picks[0]["id"],
                "fallback_free_models": [item["id"] for item in picks[1:]],
                "selection_rule": "Prefer local/open/free-tier models; escalate only when the user chooses premium or an approved provider key exists.",
            }
        )
    return routes


def build_router() -> tuple[dict[str, Any], dict[str, Any]]:
    models = model_records()
    routes = task_routes(models)
    model_count = len(models)
    free_library = {
        "schema": "dreamco.buddy_free_model_task_library.v1",
        "generated_at": utc_now(),
        "mission": "Give Buddy and users 100 free-first model/resource candidates organized by task.",
        "policy": {
            "default": "free_first",
            "user_can_choose": ["free_first", "local_only", "premium_optional", "quality_first"],
            "paid_calls": "blocked_until_user_approval_and_budget",
            "secrets": "environment_or_keychain_only_never_repo",
            "production": "verify_license_rate_limits_model_ids_and_privacy_before_live_use",
        },
        "models": models,
        "task_routes": routes,
    }
    router = {
        "schema": "dreamco.buddy_professional_api_router.v1",
        "generated_at": utc_now(),
        "mission": "Route every Buddy task to the best available model/resource with free-first defaults, user choice, fallbacks, safety gates, and cost controls.",
        "default_mode": "free_first",
        "user_selectable_modes": {
            "free_first": "Use local, open, and free-tier resources before any paid provider.",
            "local_only": "Use only local/offline/open runtime resources.",
            "premium_optional": "Use free routes first, then allow approved paid providers for hard tasks.",
            "quality_first": "Use highest-quality approved provider route after user budget approval.",
        },
        "routing_pipeline": [
            "classify_task",
            "classify_risk",
            "read_user_model_preference",
            "pick_free_primary_and_fallbacks",
            "check_local_runtime_or_free_tier_availability",
            "block_paid_call_unless_approved",
            "run_sandbox_eval",
            "record_cost_quality_latency",
            "return_answer_with_route_evidence",
        ],
        "approval_required_for": [
            "paid model calls",
            "provider key creation or rotation",
            "uploading private user media",
            "customer data processing by third-party providers",
            "voice or likeness cloning",
            "production route changes",
            "public claims that one model is best without current eval evidence",
        ],
        "cost_controls": {
            "monthly_budget_without_owner_approval_usd": 0,
            "per_user_default_mode": "free_first",
            "cache_reuse": True,
            "batch_when_possible": True,
            "smallest_capable_model_first": True,
            "log_estimated_cost_before_paid_escalation": True,
        },
        "free_model_candidate_count": model_count,
        "task_routes_source": str(FREE_JSON.relative_to(ROOT)),
        "routes": routes,
    }
    return router, free_library


def write_markdown(router: dict[str, Any], free_library: dict[str, Any]) -> None:
    lines = [
        "# Buddy Professional API Router",
        "",
        router["mission"],
        "",
        "## Modes",
        "",
    ]
    for mode, description in router["user_selectable_modes"].items():
        lines.append(f"- {mode}: {description}")
    lines.extend(["", "## Approval Required", ""])
    lines.extend(f"- {item}" for item in router["approval_required_for"])
    lines.extend(["", "## Sample Routes", ""])
    for route in router["routes"][:20]:
        lines.append(f"- {route['task_type']}: {route['primary_free_model']} -> {', '.join(route['fallback_free_models'])}")
    ROUTER_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    free_lines = [
        "# Buddy Free Model Task Library",
        "",
        free_library["mission"],
        "",
        f"- Model/resource candidates: {len(free_library['models'])}",
        f"- Task route groups: {len(free_library['task_routes'])}",
        "",
        "## Top 100 Free-First Candidates",
        "",
    ]
    for model in free_library["models"]:
        free_lines.append(f"- {model['rank']}. {model['id']} ({model['provider']}): {', '.join(model['best_for'])}")
    FREE_MD.write_text("\n".join(free_lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Buddy professional API router and free model library.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    router, free_library = build_router()
    if args.check:
        existing_router = json.loads(ROUTER_JSON.read_text(encoding="utf-8")) if ROUTER_JSON.exists() else {}
        existing_free = json.loads(FREE_JSON.read_text(encoding="utf-8")) if FREE_JSON.exists() else {}
        ok = (
            existing_router.get("schema") == router["schema"]
            and existing_free.get("schema") == free_library["schema"]
            and len(existing_free.get("models", [])) == len(FREE_MODEL_POOL[:100])
            and len(existing_router.get("routes", [])) == len(TASKS)
            and ROUTER_MD.exists()
            and FREE_MD.exists()
        )
        print(json.dumps({"ok": ok, "free_models": len(FREE_MODEL_POOL[:100]), "task_routes": len(TASKS)}, indent=2))
        return 0 if ok else 1

    ROUTER_JSON.parent.mkdir(parents=True, exist_ok=True)
    ROUTER_JSON.write_text(json.dumps(router, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    FREE_JSON.write_text(json.dumps(free_library, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(router, free_library)
    print(json.dumps({"ok": True, "router": str(ROUTER_JSON.relative_to(ROOT)), "free_models": len(FREE_MODEL_POOL[:100]), "task_routes": len(TASKS)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
