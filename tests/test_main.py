"""Tests for main.py — DreamCo system entry point."""
import sys
import os
import importlib

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
AI_MODELS_DIR = os.path.join(REPO_ROOT, "bots", "ai-models-integration")
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest


class TestMainModule:
    def test_main_module_importable(self):
        import main  # noqa: F401 — just ensure import doesn't crash
        assert hasattr(main, "start")

    def test_start_returns_dict(self):
        import main
        result = main.start()
        assert isinstance(result, dict)

    def test_start_returns_controller_status(self):
        import main
        result = main.start()
        assert "controller_status" in result

    def test_start_returns_loop_results(self):
        import main
        result = main.start()
        assert "loop_results" in result

    def test_start_returns_learning_cycle(self):
        import main
        result = main.start()
        assert "learning_cycle" in result

    def test_controller_status_has_control_center_key(self):
        import main
        result = main.start()
        assert "control_center" in result["controller_status"]

    def test_loop_results_is_list(self):
        import main
        result = main.start()
        assert isinstance(result["loop_results"], list)

    def test_learning_cycle_is_dict(self):
        import main
        result = main.start()
        assert isinstance(result["learning_cycle"], dict)

    def test_learning_cycle_has_suggestions(self):
        import main
        result = main.start()
        assert "suggestions" in result["learning_cycle"]
