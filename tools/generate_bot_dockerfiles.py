"""Generate Dockerfiles and compose fragments for DreamCo bots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BOTS_DIR = ROOT / "bots"
COMPOSE_OUTPUT = ROOT / "bots" / "docker-compose.generated.yml"

DOCKERFILE_TEMPLATE = """FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY . /app
RUN pip install --no-cache-dir -r /app/requirements.txt || true
EXPOSE 8000
CMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]
"""


def load_profiles() -> list[tuple[str, Path, dict[str, Any]]]:
    profiles = []
    for profile_path in sorted(BOTS_DIR.glob("*/replit_profile.json")):
        data = json.loads(profile_path.read_text())
        slug = data.get("slug") or profile_path.parent.name
        profiles.append((slug, profile_path.parent, data))
    return profiles


def render_service(slug: str, profile: dict[str, Any]) -> str:
    port = int(profile.get("port", 8000))
    return f"""  {slug}:
    build:
      context: ./bots/{slug}
      dockerfile: Dockerfile
    container_name: dreamco-{slug}
    environment:
      BOT_SLUG: {slug}
      PORT: {port}
    ports:
      - \"{port}:{port}\"
    restart: unless-stopped
"""


def ensure_dockerfile(bot_dir: Path) -> bool:
    dockerfile = bot_dir / "Dockerfile"
    if dockerfile.exists():
        return False
    dockerfile.write_text(DOCKERFILE_TEMPLATE)
    return True


def generate() -> dict[str, int]:
    profiles = load_profiles()
    created = 0
    services = ['version: "3.9"', "services:"]
    for slug, bot_dir, profile in profiles:
        created += int(ensure_dockerfile(bot_dir))
        services.append(render_service(slug, profile))
    COMPOSE_OUTPUT.write_text("\n".join(services).rstrip() + "\n")
    return {"profiles": len(profiles), "dockerfiles_created": created}


def main() -> None:
    result = generate()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
