"""Discover and categorize freeCodeCamp channel metadata without downloading media."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "buddy/bootcamp/sources/freecodecamp/catalog.json"
CHANNEL_URL = "https://www.youtube.com/@freecodecamp/videos"
CHANNEL_ID = "UC8butISFwT-Wl7EV0hUK0BQ"

CATEGORIES = [
    ("computer_science_and_fundamentals", "Computer science and programming fundamentals", ["computer science", "cs50", "algorithm", "data structure", "programming fundamentals", "big o", "operating system"]),
    ("html_css_and_accessibility", "HTML, CSS and accessibility", ["html", "css", "responsive web", "accessibility", "web design", "sass", "tailwind"]),
    ("javascript_and_typescript", "JavaScript and TypeScript", ["javascript", "typescript", "ecmascript", "node.js", "nodejs", "deno", "bun"]),
    ("frontend_and_ui_frameworks", "Frontend frameworks and UI engineering", ["react", "next.js", "vue", "angular", "svelte", "frontend", "front-end", "web component"]),
    ("backend_and_apis", "Backend engineering and APIs", ["backend", "back-end", "api", "rest", "graphql", "express", "django", "flask", "fastapi", "server"]),
    ("python_and_automation", "Python and automation", ["python", "automation", "scripting", "pandas", "numpy", "pytest"]),
    ("java_and_jvm", "Java and JVM languages", ["java", "spring boot", "kotlin", "scala", "jvm"]),
    ("c_cpp_and_systems", "C, C++ and systems programming", [" c ", "c programming", "c++", "cpp", "rust", "assembly", "embedded", "systems programming"]),
    ("databases_and_sql", "Databases and SQL", ["sql", "postgres", "postgresql", "mysql", "mongodb", "database", "redis", "sqlite", "vector database"]),
    ("data_science_and_visualization", "Data science and visualization", ["data science", "data analysis", "visualization", "matplotlib", "tableau", "statistics", "power bi", "excel"]),
    ("machine_learning_and_deep_learning", "Machine learning and deep learning", ["machine learning", "deep learning", "pytorch", "tensorflow", "keras", "neural network", "computer vision"]),
    ("generative_ai_and_llms", "Generative AI and large language models", ["generative ai", "llm", "large language model", "rag", "fine-tuning", "embeddings", "prompt engineering", "transformer"]),
    ("ai_agents_and_mcp", "AI agents, tool use and MCP", ["agentic", "ai agent", "agents", "mcp", "model context protocol", "tool calling", "ai coding", "coding agent"]),
    ("cybersecurity_and_privacy", "Cybersecurity and privacy", ["cybersecurity", "security", "ethical hack", "penetration test", "owasp", "cryptography", "privacy", "threat"]),
    ("linux_networking_and_it", "Linux, networking and IT", ["linux", "bash", "command line", "networking", "tcp/ip", "system administration", "it support"]),
    ("cloud_devops_and_ci_cd", "Cloud, DevOps and CI/CD", ["aws", "azure", "google cloud", "cloud", "docker", "kubernetes", "devops", "ci/cd", "github actions", "terraform"]),
    ("mobile_and_cross_platform", "Mobile and cross-platform development", ["android", "ios", "swift", "flutter", "react native", "mobile app"]),
    ("game_development", "Game development", ["game development", "godot", "unity", "unreal", "game engine"]),
    ("mathematics_and_statistics", "Mathematics and statistics", ["mathematics", "math for", "linear algebra", "calculus", "probability", "statistics"]),
    ("career_and_interview_skills", "Career development and technical interviews", ["career", "resume", "interview", "portfolio", "job search", "technical interview"]),
    ("software_architecture_and_testing", "Software architecture, testing and quality", ["software architecture", "design pattern", "system design", "testing", "test-driven", "debugging", "clean code", "refactoring"]),
]

def categorize(title: str, description: str = "") -> list[str]:
    text = f" {title} {description} ".casefold()
    matches = []
    for category_id, _label, keywords in CATEGORIES:
        if any(keyword in text for keyword in keywords):
            matches.append(category_id)
    return matches or ["other_or_unclassified"]

def parse_discovery_payload(payload: dict[str, Any], enumerator_version: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Accept a catalog as complete only when yt-dlp's channel count matches every unique entry."""
    expected = payload.get("playlist_count")
    entries = payload.get("entries")
    if not isinstance(expected, int) or expected < 1:
        raise RuntimeError("yt-dlp did not return a usable playlist_count; inventory completeness is unknown")
    if not isinstance(entries, list):
        raise RuntimeError("yt-dlp did not return a playlist entries list")
    if len(entries) != expected:
        raise RuntimeError(
            f"Incomplete channel inventory: expected {expected} entries, received {len(entries)}"
        )
    if any(entry is None or not isinstance(entry, dict) for entry in entries):
        raise RuntimeError("Incomplete channel inventory: one or more entries are missing or malformed")

    videos: list[dict[str, Any]] = []
    seen: set[str] = set()
    for entry in entries:
        video_id = entry.get("id")
        if not isinstance(video_id, str) or not video_id.strip():
            raise RuntimeError("Incomplete channel inventory: an entry has no stable video ID")
        if video_id in seen:
            raise RuntimeError(f"Incomplete channel inventory: duplicate video ID {video_id}")
        seen.add(video_id)
        title = str(entry.get("title") or "Untitled video").strip()
        url = entry.get("url") or f"https://www.youtube.com/watch?v={video_id}"
        if not str(url).startswith("https://"):
            url = f"https://www.youtube.com/watch?v={video_id}"
        upload_date = entry.get("upload_date")
        videos.append({
            "video_id": video_id,
            "title": title,
            "url": str(url),
            "description": "",
            "duration_seconds": entry.get("duration"),
            "upload_date": upload_date,
            "categories": categorize(title),
            "discovery_source": "public_channel_metadata",
            "rights_status": "review_required",
            "learning_status": "not_studied",
            "all_divisions_foundation": True,
        })

    if len(videos) != expected:
        raise RuntimeError("Incomplete channel inventory: parsed video count does not match expected count")
    inventory = {
        "enumerator": "yt-dlp",
        "enumerator_version": enumerator_version,
        "expected_entry_count": expected,
        "observed_entry_count": len(videos),
        "null_entry_count": 0,
        "duplicate_video_id_count": 0,
        "complete": True,
        "completeness_basis": "playlist_count equals every parsed, non-null, unique video entry; extraction aborts on errors",
    }
    return videos, inventory


def discover() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Enumerate public metadata only; fail closed when completeness cannot be proven."""
    version_result = subprocess.run(
        [sys.executable, "-m", "yt_dlp", "--version"],
        check=True, capture_output=True, text=True, timeout=30,
    )
    enumerator_version = version_result.stdout.strip()
    if not enumerator_version:
        raise RuntimeError("Unable to determine pinned yt-dlp version")
    command = [
        sys.executable, "-m", "yt_dlp",
        "--flat-playlist", "--dump-single-json", "--no-warnings",
        "--abort-on-error", CHANNEL_URL,
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=900)
    payload = json.loads(result.stdout)
    return parse_discovery_payload(payload, enumerator_version)


def build_catalog(videos: list[dict[str, Any]], inventory: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build a catalog; absent completeness evidence always means partial, never complete."""
    if inventory is None:
        inventory = {
            "enumerator": "unknown",
            "enumerator_version": "not-recorded",
            "expected_entry_count": None,
            "observed_entry_count": len(videos),
            "null_entry_count": None,
            "duplicate_video_id_count": None,
            "complete": False,
            "completeness_basis": "no upstream enumeration count was supplied",
        }
    complete = (
        inventory.get("complete") is True
        and inventory.get("expected_entry_count") == len(videos)
        and inventory.get("observed_entry_count") == len(videos)
        and inventory.get("null_entry_count") == 0
        and inventory.get("duplicate_video_id_count") == 0
    )
    if inventory.get("complete") is True and not complete:
        raise ValueError("inventory completeness evidence does not match the video records")
    categories = [
        {"id": cid, "label": label, "keywords": keywords,
         "division_routing": "all_65_divisions_as_shared_foundation; prioritize_divisions_by_capability_and_subject"}
        for cid, label, keywords in CATEGORIES
    ]
    categories.append({"id": "other_or_unclassified", "label": "Other or awaiting classification",
                       "keywords": [], "division_routing": "curriculum_owner_review"})
    return {
        "schema": "dreamco.freecodecamp_catalog.v1",
        "source": {"name": "freeCodeCamp.org", "channel_url": "https://www.youtube.com/@freecodecamp",
                   "channel_id": CHANNEL_ID, "learning_platform": "https://www.freecodecamp.org/"},
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "inventory_status": "complete" if complete else "partial",
        "inventory": inventory,
        "video_count": len(videos),
        "categories": categories,
        "videos": sorted(videos, key=lambda row: (row.get("upload_date") or "", row["video_id"]), reverse=True),
        "learning_pipeline": ["discover", "categorize", "map_to_divisions", "rights_review",
                              "select_by_capability_gap", "study_authorized_material", "create_original_lesson",
                              "sandbox_practice", "targeted_benchmark", "holdout", "regression", "record_evidence"],
        "rights_policy": {"media_download_enabled": False, "transcript_ingestion_enabled": False,
                          "model_training_requires_review": True,
                          "public_metadata_is_not_training_permission": True},
        "truth_boundary": "A catalog entry means discovered and categorized, not watched, understood, trained on, or mastered."
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate the current catalog without changing it")
    parser.add_argument("--out", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.check:
        if not args.out.exists():
            raise SystemExit(f"Missing catalog: {args.out}")
        data = json.loads(args.out.read_text(encoding="utf-8"))
        videos = data.get("videos")
        inventory = data.get("inventory") or {}
        if data.get("schema") != "dreamco.freecodecamp_catalog.v1":
            raise SystemExit("Unsupported freeCodeCamp catalog schema")
        if not isinstance(videos, list) or data.get("video_count") != len(videos) or not videos:
            raise SystemExit("Catalog video_count does not match a non-empty videos list")
        ids = [video.get("video_id") for video in videos]
        if any(not isinstance(video_id, str) or not video_id for video_id in ids):
            raise SystemExit("Catalog contains a missing video ID")
        if len(set(ids)) != len(ids):
            raise SystemExit("Catalog contains duplicate video IDs")
        if inventory.get("observed_entry_count") != len(videos):
            raise SystemExit("Inventory observed_entry_count does not match catalog")
        if data.get("inventory_status") == "complete":
            if not (
                inventory.get("complete") is True
                and inventory.get("expected_entry_count") == len(videos)
                and inventory.get("null_entry_count") == 0
                and inventory.get("duplicate_video_id_count") == 0
            ):
                raise SystemExit("Catalog claims complete without matching completeness evidence")
        elif data.get("inventory_status") == "partial":
            if inventory.get("complete") is not False:
                raise SystemExit("Partial catalog must explicitly record complete=false")
        else:
            raise SystemExit("Catalog inventory_status must be complete or partial")
        if not isinstance(data.get("categories"), list) or not data["categories"]:
            raise SystemExit("Catalog must include categories")
        if data["rights_policy"]["media_download_enabled"] is not False:
            raise SystemExit("Media downloads must remain disabled")
        if data["rights_policy"]["transcript_ingestion_enabled"] is not False:
            raise SystemExit("Transcript ingestion must remain disabled")
        print(json.dumps({
            "ok": True,
            "inventory_status": data["inventory_status"],
            "video_count": len(videos),
            "expected_entry_count": inventory.get("expected_entry_count"),
            "enumerator_version": inventory.get("enumerator_version"),
            "categories": len(data["categories"]),
        }, indent=2))
        return 0
    videos, inventory = discover()
    catalog = build_catalog(videos, inventory)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "written": str(args.out.relative_to(ROOT)),
        "inventory_status": catalog["inventory_status"],
        "video_count": len(videos),
        "expected_entry_count": inventory["expected_entry_count"],
        "enumerator_version": inventory["enumerator_version"],
        "categorized": sum(bool(v["categories"]) for v in videos),
    }, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
