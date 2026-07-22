"""Credential-free local media engine adapter for approved creator media."""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .studio import CreativeStudioError


@dataclass(frozen=True)
class LocalRendererCommand:
    argv: tuple[str, ...]
    output_suffix: str

    def validate(self) -> None:
        if not self.argv:
            raise CreativeStudioError("A local renderer command is required.")
        executable = self.argv[0]
        resolved = shutil.which(executable) if "/" not in executable else executable
        if not resolved or not Path(resolved).is_file() or not os.access(resolved, os.X_OK):
            raise CreativeStudioError(f"Local media executable is unavailable: {executable}")
        if not self.output_suffix.startswith(".") or "/" in self.output_suffix:
            raise CreativeStudioError("Local media output suffix is invalid.")


class LocalCommandMediaRenderer:
    """Run an installed local model with argv templates and no shell.

    Templates may use ``{text}``, ``{prompt}``, ``{sample}``, ``{project_id}``,
    and ``{output}``. The engine must create the requested output file.
    """

    name = "buddy-local-command-media"

    def __init__(
        self,
        work_dir: Path,
        *,
        voice: LocalRendererCommand | None = None,
        avatar: LocalRendererCommand | None = None,
        timeout_seconds: int = 300,
    ) -> None:
        if voice is None and avatar is None:
            raise CreativeStudioError("Configure at least one local media command.")
        if voice:
            voice.validate()
        if avatar:
            avatar.validate()
        self.work_dir = work_dir.resolve()
        self.work_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.voice = voice
        self.avatar = avatar
        self.timeout_seconds = min(max(timeout_seconds, 5), 3_600)

    def readiness(self) -> dict[str, object]:
        return {
            "schema": "dreamco.local_media_renderer_readiness.v1",
            "name": self.name,
            "voice_configured": self.voice is not None,
            "avatar_configured": self.avatar is not None,
            "credentials_required": False,
            "shell_execution": False,
            "work_dir": str(self.work_dir),
        }

    def render_voice(self, *, text: str, sample_ref: str, project_id: str) -> str:
        if self.voice is None:
            raise CreativeStudioError("A local voice engine is not configured.")
        return self._run(
            self.voice,
            project_id=project_id,
            output_name="voice",
            replacements={"text": text, "sample": sample_ref, "prompt": ""},
        )

    def render_avatar(self, *, prompt: str, sample_ref: str, project_id: str) -> str:
        if self.avatar is None:
            raise CreativeStudioError("A local image or avatar engine is not configured.")
        return self._run(
            self.avatar,
            project_id=project_id,
            output_name="avatar",
            replacements={"text": "", "sample": sample_ref, "prompt": prompt},
        )

    def _run(
        self,
        command: LocalRendererCommand,
        *,
        project_id: str,
        output_name: str,
        replacements: dict[str, str],
    ) -> str:
        safe_project_id = "".join(character for character in project_id if character.isalnum() or character in "-_")
        if not safe_project_id or safe_project_id != project_id:
            raise CreativeStudioError("Project id contains unsupported characters.")
        project_dir = (self.work_dir / safe_project_id).resolve()
        if self.work_dir not in project_dir.parents:
            raise CreativeStudioError("Local media output escaped the configured work directory.")
        project_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        output = project_dir / f"{output_name}{command.output_suffix}"
        values = {**replacements, "project_id": project_id, "output": str(output)}
        argv = [self._replace(argument, values) for argument in command.argv]
        environment = {"PATH": os.environ.get("PATH", ""), "HOME": str(self.work_dir)}
        result = subprocess.run(
            argv,
            cwd=project_dir,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=self.timeout_seconds,
            check=False,
            shell=False,
        )
        if result.returncode != 0:
            message = result.stderr.decode("utf-8", errors="replace")[-500:]
            raise CreativeStudioError(f"Local media engine failed: {message or result.returncode}")
        if not output.is_file() or output.stat().st_size == 0:
            raise CreativeStudioError("Local media engine did not create a usable output asset.")
        output.chmod(0o600)
        return f"local-asset:{project_id}/{output.name}"

    @staticmethod
    def _replace(template: str, values: dict[str, str]) -> str:
        rendered = template
        for key, value in values.items():
            rendered = rendered.replace("{" + key + "}", value)
        return rendered
