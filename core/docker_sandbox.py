"""Docker SDK-backed sandbox isolation for DreamCo bots."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import docker
except ImportError:  # pragma: no cover
    docker = None

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class SandboxResult:
    bot_slug: str
    exit_code: int
    stdout: str
    stderr: str


class DockerSandbox:
    """Run a bot inside a tightly constrained Docker container."""

    def __init__(self) -> None:
        self.client = docker.from_env() if docker else None

    def run(self, bot_slug: str, input_data: dict[str, Any], timeout: int = 30) -> SandboxResult:
        if self.client is None:
            return SandboxResult(bot_slug=bot_slug, exit_code=127, stdout="", stderr="docker SDK unavailable")
        bot_dir = ROOT / "bots" / bot_slug
        command = ["python", "-c", "import json,sys; print(json.dumps(json.load(sys.stdin)))"]
        container = self.client.containers.run(
            "python:3.11-slim",
            command=command,
            stdin_open=True,
            detach=True,
            mem_limit="256m",
            nano_cpus=500_000_000,
            environment={"SIMULATION_MODE": "true"},
            volumes={str(bot_dir): {"bind": "/app", "mode": "ro"}},
            working_dir="/app",
        )
        try:
            container.exec_run(cmd=["/bin/sh", "-lc", f"echo '{json.dumps(input_data)}' | python -c 'import sys; print(sys.stdin.read())'"], demux=True)
            result = container.wait(timeout=timeout)
            stdout = container.logs(stdout=True, stderr=False).decode("utf-8", errors="ignore")
            stderr = container.logs(stdout=False, stderr=True).decode("utf-8", errors="ignore")
            return SandboxResult(bot_slug=bot_slug, exit_code=int(result.get("StatusCode", 1)), stdout=stdout, stderr=stderr)
        finally:
            container.remove(force=True)
