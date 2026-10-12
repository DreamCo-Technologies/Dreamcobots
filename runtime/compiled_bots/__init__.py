"""Compiled sandbox bots generated from bots/*.md."""
from __future__ import annotations
from importlib import import_module
from pathlib import Path

REGISTRY_PATH = Path(__file__).with_name("registry.json")


def load_registry() -> dict:
    import json
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def create_bot(slug: str):
    mod = import_module(f"runtime.compiled_bots.{slug.replace('-', '_')}")
    return mod.create()


def run_bot(slug: str, task: dict | None = None) -> dict:
    return create_bot(slug).run(task)
