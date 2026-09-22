#!/usr/bin/env python3
"""Choose where Buddy stores learning and teaching memory. 20 places."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PLACES_PATH = HERE / "places.json"
CHOICE_PATH = HERE / "chosen_place.json"
SECRET_HINT = re.compile(r"(api[_-]?key|secret|token|password|bearer)\s*[:=]", re.I)


def load_places() -> dict[str, Any]:
    return json.loads(PLACES_PATH.read_text(encoding="utf-8"))


def list_places() -> list[dict[str, Any]]:
    return list(load_places().get("places") or [])


def get_choice() -> dict[str, Any]:
    if CHOICE_PATH.exists():
        return json.loads(CHOICE_PATH.read_text(encoding="utf-8"))
    catalog = load_places()
    default = catalog.get("default_place", "this_computer")
    place = next((p for p in list_places() if p["id"] == default), list_places()[0])
    return {"place_id": place["id"], "custom_path": None, "place": place}


def resolve_dir(choice: dict[str, Any] | None = None) -> Path:
    choice = choice or get_choice()
    place = choice.get("place") or next(p for p in list_places() if p["id"] == choice["place_id"])
    kind = place.get("kind")
    if kind in {"custom_folder"}:
        raw = choice.get("custom_path") or ""
        if raw:
            return Path(raw).expanduser()
        return HERE / "export" / place["id"]
    if kind == "browser":
        return HERE / "browser_mirror"
    rel = place.get("path") or f"buddy/memory/export/{place['id']}"
    path = Path(rel)
    return path if path.is_absolute() else ROOT / path


def choose(place_id: str, custom_path: str | None = None) -> dict[str, Any]:
    place = next((p for p in list_places() if p["id"] == place_id), None)
    if not place:
        known = ", ".join(p["id"] for p in list_places())
        raise ValueError(f"Unknown place: {place_id}. Try: {known}")
    payload = {
        "place_id": place_id,
        "custom_path": custom_path,
        "place": place,
        "chosen_at": datetime.now(timezone.utc).isoformat(),
    }
    CHOICE_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    resolve_dir(payload).mkdir(parents=True, exist_ok=True)
    return payload


def _sanitize(text: str) -> str:
    if SECRET_HINT.search(text):
        raise ValueError("That looks like a secret key. Do not store it in memory.")
    return text.strip()


def remember(kind: str, text: str, bot: str = "buddy") -> dict[str, Any]:
    if kind not in {"learn", "teach"}:
        raise ValueError("kind must be learn or teach")
    body = _sanitize(text)
    if not body:
        raise ValueError("Empty note")
    choice = get_choice()
    folder = resolve_dir(choice)
    folder.mkdir(parents=True, exist_ok=True)
    event = {
        "at": datetime.now(timezone.utc).isoformat(),
        "kind": kind,
        "bot": bot,
        "text": body,
        "place_id": choice["place_id"],
        "how": (choice.get("place") or {}).get("how"),
    }
    target = folder / "memory.jsonl" if folder.suffix != ".jsonl" else folder
    if target.suffix == ".jsonl":
        target.parent.mkdir(parents=True, exist_ok=True)
    else:
        target = folder / "memory.jsonl"
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")
    return {
        "saved": True,
        "file": str(target),
        "event": event,
        "place": choice["place"]["easy_name"],
        "next": choice["place"].get("how"),
    }


def read_memory(limit: int = 50) -> list[dict[str, Any]]:
    folder = resolve_dir()
    target = folder / "memory.jsonl" if folder.suffix != ".jsonl" else folder
    if folder.suffix == ".jsonl":
        target = folder
    elif not target.exists() and folder.exists() and folder.is_file():
        target = folder
    if not target.exists():
        return []
    return [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines() if line.strip()][-limit:]


HELP = """Buddy memory places (20)

  python3 buddy/memory/memory_places.py places
  python3 buddy/memory/memory_places.py choose google_drive
  python3 buddy/memory/memory_places.py choose icloud_drive
  python3 buddy/memory/memory_places.py choose google_cloud_storage
  python3 buddy/memory/memory_places.py choose custom_folder --path ~/Documents/buddy-memory
  python3 buddy/memory/memory_places.py teach "Give short answers" --bot buddy
  python3 buddy/memory/memory_places.py learn "Ask for downside first" --bot deal
  python3 buddy/memory/memory_places.py show
  python3 buddy/memory/memory_places.py where
"""


def main(argv: list[str]) -> int:
    if not argv or argv[0] in {"help", "-h", "--help"}:
        print(HELP)
        return 0
    cmd = argv[0]
    if cmd == "places":
        print(json.dumps([{"id": p["id"], "easy_name": p["easy_name"], "kind": p["kind"], "how": p.get("how")} for p in list_places()], indent=2))
        return 0
    if cmd == "where":
        choice = get_choice()
        print(json.dumps({"choice": choice, "folder": str(resolve_dir(choice))}, indent=2, default=str))
        return 0
    if cmd == "choose":
        place_id = argv[1] if len(argv) > 1 else "this_computer"
        custom = argv[argv.index("--path") + 1] if "--path" in argv else None
        print(json.dumps(choose(place_id, custom), indent=2))
        return 0
    if cmd in {"learn", "teach"}:
        bot = "buddy"
        args = argv[1:]
        if "--bot" in args:
            i = args.index("--bot")
            bot = args[i + 1]
            args = args[:i] + args[i + 2 :]
        print(json.dumps(remember(cmd, " ".join(args), bot=bot), indent=2))
        return 0
    if cmd == "show":
        print(json.dumps(read_memory(), indent=2))
        return 0
    print(HELP)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
