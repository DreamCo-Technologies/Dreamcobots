from __future__ import annotations

from framework import GlobalAISourcesFlow  # noqa: F401

import json
import os
import threading
from copy import deepcopy
from pathlib import Path
from typing import Any


class ExecutionStateStore:
    """File-backed execution state store for durable bot runtime state."""

    def __init__(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        if not self.file_path.exists():
            self._write(self._default_state())

    @staticmethod
    def _default_state() -> dict[str, Any]:
        return {
            "projects": {},
            "active_project_id": None,
            "render_jobs": {},
            "assets": {},
        }

    def _read(self) -> dict[str, Any]:
        if not self.file_path.exists():
            return self._default_state()
        with self.file_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, state: dict[str, Any]) -> None:
        with self.file_path.open("w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, sort_keys=True)

    def get_state(self) -> dict[str, Any]:
        with self._lock:
            return deepcopy(self._read())

    def update_state(self, mutator) -> dict[str, Any]:
        with self._lock:
            state = self._read()
            mutator(state)
            self._write(state)
            return deepcopy(state)


class ProjectRepository:
    def __init__(self, store: ExecutionStateStore) -> None:
        self.store = store

    def get(self, project_id: str) -> dict[str, Any] | None:
        state = self.store.get_state()
        return state["projects"].get(project_id)

    def save(self, project: dict[str, Any]) -> dict[str, Any]:
        project_id = project["project_id"]

        def _mutate(state: dict[str, Any]) -> None:
            state["projects"][project_id] = project

        state = self.store.update_state(_mutate)
        return state["projects"][project_id]

    def count(self) -> int:
        return len(self.store.get_state()["projects"])

    def set_active_project(self, project_id: str | None) -> None:
        self.store.update_state(lambda state: state.__setitem__("active_project_id", project_id))

    def get_active_project(self) -> str | None:
        return self.store.get_state().get("active_project_id")


class RenderJobRepository:
    def __init__(self, store: ExecutionStateStore) -> None:
        self.store = store

    def save(self, job: dict[str, Any]) -> dict[str, Any]:
        job_id = job["job_id"]

        def _mutate(state: dict[str, Any]) -> None:
            state["render_jobs"][job_id] = job

        state = self.store.update_state(_mutate)
        return state["render_jobs"][job_id]

    def get(self, job_id: str) -> dict[str, Any] | None:
        return self.store.get_state()["render_jobs"].get(job_id)


class AssetRegistry:
    def __init__(self, store: ExecutionStateStore) -> None:
        self.store = store

    def register(self, asset: dict[str, Any]) -> dict[str, Any]:
        asset_id = asset["asset_id"]

        def _mutate(state: dict[str, Any]) -> None:
            state["assets"][asset_id] = asset

        state = self.store.update_state(_mutate)
        return state["assets"][asset_id]

    def get(self, asset_id: str) -> dict[str, Any] | None:
        return self.store.get_state()["assets"].get(asset_id)


def default_state_path(bot_name: str) -> str:
    base = os.getenv("DREAMCO_EXECUTION_STATE_DIR", "/tmp/dreamcobots_execution_state")
    Path(base).mkdir(parents=True, exist_ok=True)
    return str(Path(base) / f"{bot_name}.json")
