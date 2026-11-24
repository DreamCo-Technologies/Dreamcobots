"""Catalog freeCodeCamp.org public YouTube uploads as attributed learning references.

Uses the official YouTube Data API v3. It fetches metadata only: no video,
audio, captions, transcript, comments, or viewer data are downloaded.
Cataloging does not grant training or redistribution rights.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_ROOT = "https://www.googleapis.com/youtube/v3"
CHANNEL_ID = "UC8butISFwT-Wl7EV0hUK0BQ"
CHANNEL_URL = "https://www.youtube.com/@freecodecamp"
CATEGORIES = {
    "programming_foundations": ["programming", "coding", "learn to code", "computer science", "cs50"],
    "python": ["python", "pandas", "django", "flask", "fastapi"],
    "javascript_typescript": ["javascript", "typescript", "node.js", "nodejs", "ecmascript"],
    "web_html_css": ["html", "css", "sass", "tailwind", "bootstrap"],
    "frontend": ["react", "vue", "angular", "svelte", "frontend", "front-end"],
    "backend_apis": ["backend", "back-end", "api", "express", "rest api", "graphql"],
    "databases_sql": ["sql", "postgres", "postgresql", "mysql", "mongodb", "database", "redis"],
    "data_engineering": ["data engineering", "etl", "airflow", "spark", "dbt", "warehouse"],
    "data_science": ["data science", "statistics", "data analysis", "visualization", "numpy"],
    "machine_learning": ["machine learning", "scikit-learn", "sklearn", "classification", "regression"],
    "deep_learning": ["deep learning", "pytorch", "tensorflow", "neural network", "transformer"],
    "generative_ai": ["generative ai", "llm", "large language model", "prompt engineering", "rag"],
    "agents_automation": ["agentic", "ai agent", "agents", "automation", "mcp", "workflow"],
    "devops_cloud": ["docker", "kubernetes", "aws", "azure", "gcp", "cloud", "ci/cd", "devops"],
    "cybersecurity": ["cybersecurity", "security", "penetration testing", "owasp", "cryptography"],
    "computer_science": ["computer science", "operating systems", "compiler", "architecture"],
    "algorithms_data_structures": ["algorithm", "data structures", "leetcode", "sorting", "graph theory"],
    "math_statistics": ["mathematics", "math", "linear algebra", "calculus", "probability", "statistics"],
    "mobile_development": ["android", "ios", "swift", "kotlin", "react native", "flutter"],
    "game_development": ["game development", "unity", "unreal engine", "godot"],
    "design_ux": ["ux", "ui design", "figma", "user experience", "accessibility"],
    "career_interview": ["interview", "resume", "career", "job search", "portfolio"],
    "business_product": ["product management", "startup", "business", "entrepreneurship"],
    "linux_networking": ["linux", "bash", "shell", "networking", "tcp/ip"]
}
LEVELS = {
    "beginner": ["beginner", "for beginners", "from scratch", "intro to", "introduction to"],
    "intermediate": ["intermediate", "build a", "project-based", "hands-on"],
    "advanced": ["advanced", "deep dive", "production", "internals", "masterclass"]
}


class YouTubeAPIError(RuntimeError):
    pass


def _api_get(resource: str, params: dict, api_key: str, sleep_seconds: float = 0.0) -> dict:
    query = dict(params)
    query["key"] = api_key
    request = Request(
        f"{API_ROOT}/{resource}?{urlencode(query)}",
        headers={"Accept": "application/json", "User-Agent": "DreamCo-Educational-Catalog/1.0"}
    )
    if sleep_seconds:
        time.sleep(sleep_seconds)
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise YouTubeAPIError(f"YouTube API request failed for {resource}: {exc}") from exc


def classify_video(title: str, description: str = "", tags: list[str] | None = None) -> dict:
    text = " ".join([title or "", description or "", " ".join(tags or [])]).casefold()
    categories = []
    for category, terms in CATEGORIES.items():
        if any(re.search(r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])", text) for term in terms):
            categories.append(category)
    if not categories:
        categories = ["other_needs_review"]
    level_hits = [level for level, terms in LEVELS.items() if any(term in text for term in terms)]
    level = level_hits[0] if len(level_hits) == 1 else ("mixed" if level_hits else "unknown")
    return {
        "categories": categories,
        "skill_level": level,
        "classification_method": "keyword_tag_heuristic",
        "human_review_required": True
    }


def catalog_all(api_key: str, channel_id: str = CHANNEL_ID, sleep_seconds: float = 0.0) -> dict:
    channel = _api_get("channels", {"part": "contentDetails,snippet", "id": channel_id}, api_key, sleep_seconds)
    items = channel.get("items", [])
    if len(items) != 1:
        raise YouTubeAPIError(f"Expected one channel record for {channel_id}; received {len(items)}")
    channel_item = items[0]
    uploads_id = channel_item["contentDetails"]["relatedPlaylists"]["uploads"]
    video_ids = []
    page_token = None
    pages = 0
    while True:
        params = {"part": "snippet,contentDetails", "playlistId": uploads_id, "maxResults": 50}
        if page_token:
            params["pageToken"] = page_token
        page = _api_get("playlistItems", params, api_key, sleep_seconds)
        pages += 1
        for item in page.get("items", []):
            video_id = item.get("contentDetails", {}).get("videoId")
            if video_id:
                video_ids.append(video_id)
        page_token = page.get("nextPageToken")
        if not page_token:
            break
    video_ids = list(dict.fromkeys(video_ids))
    videos = []
    for start in range(0, len(video_ids), 50):
        batch = video_ids[start:start + 50]
        response = _api_get("videos", {
            "part": "snippet,contentDetails", "id": ",".join(batch), "maxResults": 50
        }, api_key, sleep_seconds)
        for item in response.get("items", []):
            snippet = item.get("snippet", {})
            tags = snippet.get("tags", [])
            classification = classify_video(snippet.get("title", ""), snippet.get("description", ""), tags)
            videos.append({
                "video_id": item["id"],
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "published_at": snippet.get("publishedAt"),
                "duration": item.get("contentDetails", {}).get("duration"),
                "tags": tags,
                "youtube_category_id": snippet.get("categoryId"),
                "video_url": f"https://www.youtube.com/watch?v={item['id']}",
                **classification,
                "division_candidates": [],
                "division_owner_approval": "REQUIRED",
                "content_rights": "THIRD_PARTY_REFERENCE_ONLY",
                "training_permission": "NOT_GRANTED",
                "transcript_status": "NOT_FETCHED",
                "video_downloaded": False
            })
    videos.sort(key=lambda row: (row.get("published_at") or "", row["video_id"]))
    return {
        "schema": "dreamco.educational_video_catalog.v1",
        "publisher": "freeCodeCamp.org",
        "channel_id": channel_id,
        "channel_url": CHANNEL_URL if channel_id == CHANNEL_ID else f"https://www.youtube.com/channel/{channel_id}",
        "uploads_playlist_id": uploads_id,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "discovery_method": "YouTube Data API v3",
        "pagination_pages": pages,
        "video_id_count": len(video_ids),
        "metadata_returned_count": len(videos),
        "pagination_exhausted": True,
        "videos": videos,
        "rights_notice": "Metadata catalog only. This does not grant transcript, training, redistribution, or commercial rights."
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, help="Output JSON catalog path")
    parser.add_argument("--channel-id", default=CHANNEL_ID)
    parser.add_argument("--sleep-seconds", type=float, default=0.0)
    args = parser.parse_args()
    api_key = os.environ.get("YOUTUBE_DATA_API_KEY")
    if not api_key:
        parser.error("Set YOUTUBE_DATA_API_KEY in the environment; never commit API keys.")
    result = catalog_all(api_key, args.channel_id, args.sleep_seconds)
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "video_id_count": result["video_id_count"],
        "metadata_returned_count": result["metadata_returned_count"],
        "pagination_exhausted": result["pagination_exhausted"],
        "training_permission": "NOT_GRANTED",
        "transcripts_fetched": False
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
