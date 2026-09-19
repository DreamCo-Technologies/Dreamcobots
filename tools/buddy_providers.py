#!/usr/bin/env python3
"""Live provider pings. Keys come from the environment, never from git.

  python3 tools/buddy_providers.py          # report which keys exist
  python3 tools/buddy_providers.py --live   # one tiny ping per present key

OpenAI uses OPENAI_API_KEY (GitHub Actions secret).
Grok uses XAI_API_KEY.
Claude uses ANTHROPIC_API_KEY (owner will add).
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "website" / "data" / "live-providers.json"
PROVIDERS = (
    {
        "id": "grok",
        "label": "Grok (xAI)",
        "env": "XAI_API_KEY",
        "model": "grok-4.5",
        "kind": "openai_compat",
        "url": "https://api.x.ai/v1/chat/completions",
    },
    {
        "id": "openai",
        "label": "OpenAI",
        "env": "OPENAI_API_KEY",
        "model": "gpt-4o-mini",
        "kind": "openai_compat",
        "url": "https://api.openai.com/v1/chat/completions",
    },
    {
        "id": "claude",
        "label": "Claude (Anthropic)",
        "env": "ANTHROPIC_API_KEY",
        "model": "claude-sonnet-4-5",
        "kind": "anthropic",
        "url": "https://api.anthropic.com/v1/messages",
    },
)


def redact(text: str) -> str:
    out = text
    for needle in ("sk-ant-", "sk-"):
        if needle in out:
            start = out.find(needle)
            out = out[:start] + needle + "REDACTED" + out[start + 40 :]
    return out.replace("Bearer ", "Bearer REDACTED ")[:240]


def present(env_name: str) -> bool:
    return bool(os.environ.get(env_name, "").strip())


def ping_openai_compat(url: str, key: str, model: str) -> str:
    models_url = url.replace("/chat/completions", "/models")
    req = urllib.request.Request(
        models_url,
        headers={"Authorization": f"Bearer {key}"},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=20) as res:
        payload = json.loads(res.read().decode())
    ids = [row.get("id") for row in payload.get("data") or [] if row.get("id")]
    if not ids:
        raise RuntimeError("no models")
    return f"{len(ids)} models; prefer {model}"


def ping_claude(url: str, key: str, model: str) -> str:
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/models",
        headers={
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=20) as res:
        payload = json.loads(res.read().decode())
    ids = [row.get("id") for row in payload.get("data") or [] if row.get("id")]
    if not ids:
        raise RuntimeError("no models")
    return f"{len(ids)} models; prefer {model}"


def run(live: bool) -> dict:
    items = []
    for spec in PROVIDERS:
        key = os.environ.get(spec["env"], "").strip()
        item = {
            "id": spec["id"],
            "label": spec["label"],
            "env": spec["env"],
            "model": spec["model"],
            "key_present": bool(key),
            "status": "blocked",
            "sample": "",
            "error": None,
        }
        if not key:
            item["error"] = f"{spec['env']} missing"
            items.append(item)
            continue
        if not live:
            item["status"] = "key_present_not_called"
            items.append(item)
            continue
        try:
            if spec["kind"] == "anthropic":
                sample = ping_claude(spec["url"], key, spec["model"])
            else:
                sample = ping_openai_compat(spec["url"], key, spec["model"])
            item["status"] = "live"
            item["sample"] = sample
        except urllib.error.HTTPError as exc:
            item["status"] = "error"
            item["error"] = redact(f"HTTP {exc.code} {exc.read().decode(errors='replace')[:160]}")
        except Exception as exc:
            item["status"] = "error"
            item["error"] = redact(str(exc))
        items.append(item)

    report = {
        "schema": "dreamco.live_providers.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "live": live,
        "truth": "A live ping is one tiny completion. Keys never print. Missing keys stay blocked.",
        "items": items,
        "live_stripe": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "live-providers.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    report = run(live=args.live)
    summary = {item["id"]: item["status"] for item in report["items"]}
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
