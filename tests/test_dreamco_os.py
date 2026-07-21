"""
Tests for the DreamCo OS system update:

  - event_bus.base_bus.BaseEventBus
  - event_bus.redis_bus.RedisEventBus
  - python_bots.base_bot.BaseBot
  - python_bots.real_estate.bot.RealEstateBot
  - Real_Estate_bots.feature_1.Feature1Bot
  - core.bot_registry
  - core.bot_validator.validate_bot
  - core.sandbox_runner.run_in_sandbox
  - core.bot_lab.BotLab
  - core.orchestrator.Orchestrator
  - api.upload_api Flask endpoints
"""

from __future__ import annotations

import os
import sys
import tempfile

import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)

# ---------------------------------------------------------------------------
# event_bus.base_bus
# ---------------------------------------------------------------------------

from event_bus.base_bus import BaseEventBus


class TestBaseEventBus:
    def test_is_abstract(self):
        with pytest.raises(TypeError):
            BaseEventBus()  # type: ignore[abstract]

    def test_concrete_subclass_works(self):
        class SimpleEventBus(BaseEventBus):
            def __init__(self):
                self._log = {}

            def publish(self, event_type, data):
                self._log.setdefault(event_type, []).append(data)

            def subscribe(self, event_type, handler):
                pass

        bus = SimpleEventBus()
        bus.publish("ping", {"value": 1})
        assert bus._log["ping"] == [{"value": 1}]


# ---------------------------------------------------------------------------
# event_bus.redis_bus
# ---------------------------------------------------------------------------

from event_bus.redis_bus import RedisEventBus


class TestRedisEventBus:
    def setup_method(self):
        # Use a bus that will almost certainly not have Redis available
        self.bus = RedisEventBus(host="localhost", port=6379)

    def test_instantiates(self):
        assert self.bus is not None

    def test_redis_connected_attribute_is_bool(self):
        assert isinstance(self.bus.redis_connected, bool)

    def test_subscribe_and_publish_in_process(self):
        received = []
        self.bus.subscribe("test_event", received.append)
        self.bus.publish("test_event", {"val": 42})
        assert received == [{"val": 42}]

    def test_multiple_subscribers(self):
        a, b = [], []
        self.bus.subscribe("evt", a.append)
        self.bus.subscribe("evt", b.append)
        self.bus.publish("evt", "hello")
        assert a == ["hello"]
        assert b == ["hello"]

    def test_no_duplicate_subscriber(self):
        calls = []
        handler = calls.append
        self.bus.subscribe("dup", handler)
        self.bus.subscribe("dup", handler)
        self.bus.publish("dup", 1)
        assert calls == [1]

    def test_get_events_returns_history(self):
        self.bus.publish("history", "first")
        self.bus.publish("history", "second")
        events = self.bus.get_events("history")
        assert "first" in events
        assert "second" in events

    def test_get_events_empty_for_unknown_type(self):
        assert self.bus.get_events("nonexistent_xyz") == []


# ---------------------------------------------------------------------------
# python_bots.base_bot
# ---------------------------------------------------------------------------

from python_bots.base_bot import BaseBot


class TestBaseBotPythonBots:
    def test_is_abstract(self):
        with pytest.raises(TypeError):
            BaseBot("test")  # type: ignore[abstract]

    def test_concrete_subclass(self):
        class MyBot(BaseBot):
            def run(self, event_bus):
                event_bus.publish("ran", self.name)

        bot = MyBot("my_bot")
        assert bot.name == "my_bot"

        bus = RedisEventBus()
        bot.run(bus)
        assert bus.get_events("ran") == ["my_bot"]


# ---------------------------------------------------------------------------
# python_bots.real_estate.bot
# ---------------------------------------------------------------------------

from python_bots.real_estate.bot import RealEstateBot


class TestRealEstateBotOS:
    def test_run_publishes_deal_found(self):
        bot = RealEstateBot("re_test")
        bus = RedisEventBus()
        bot.run(bus)
        events = bus.get_events("deal_found")
        assert len(events) == 1
        deal = events[0]
        assert deal["address"] == "123 Main St"
        assert deal["profit"] == 25000
        assert deal["source"] == "re_test"

    def test_bot_name(self):
        bot = RealEstateBot("test_name")
        assert bot.name == "test_name"


# ---------------------------------------------------------------------------
# Real_Estate_bots.feature_1.Feature1Bot
# ---------------------------------------------------------------------------


class TestFeature1Bot:
    def test_feature1bot_available(self):
        try:
            from Real_Estate_bots.feature_1 import Feature1Bot
        except ImportError:
            pytest.skip("Feature1Bot not importable in this environment")

        bot = Feature1Bot("feature_1")
        bus = RedisEventBus()
        bot.run(bus)
        events = bus.get_events("deal_found")
        assert len(events) == 1
        assert events[0]["profit"] == 20000
        assert events[0]["source"] == "feature_1"


# ---------------------------------------------------------------------------
# core.bot_registry
# ---------------------------------------------------------------------------

from core.bot_registry import register_bot, get_registered_bots, clear_registry


class TestBotRegistry:
    def setup_method(self):
        clear_registry()

    def test_register_and_retrieve(self):
        register_bot({"name": "test_bot", "status": "approved"})
        bots = get_registered_bots()
        assert len(bots) == 1
        assert bots[0]["name"] == "test_bot"

    def test_multiple_registrations(self):
        register_bot({"name": "bot_a"})
        register_bot({"name": "bot_b"})
        assert len(get_registered_bots()) == 2

    def test_clear_registry(self):
        register_bot({"name": "temp"})
        clear_registry()
        assert get_registered_bots() == []

    def test_returns_copy(self):
        register_bot({"name": "copy_test"})
        bots = get_registered_bots()
        bots.append({"name": "injected"})
        # Should not affect the registry
        assert len(get_registered_bots()) == 1


# ---------------------------------------------------------------------------
# core.bot_validator
# ---------------------------------------------------------------------------

from core.bot_validator import validate_bot


class TestBotValidator:
    def _write_tmp(self, code: str) -> str:
        fd, path = tempfile.mkstemp(suffix=".py")
        with os.fdopen(fd, "w") as fh:
            fh.write(code)
        return path

    def test_safe_code_passes(self):
        path = self._write_tmp("print('hello world')\n")
        valid, msg = validate_bot(path)
        assert valid is True
        assert msg == "Safe"
        os.unlink(path)

    def test_os_system_blocked(self):
        path = self._write_tmp("import os\nos.system('ls')\n")
        valid, msg = validate_bot(path)
        assert valid is False
        assert "os.system" in msg
        os.unlink(path)

    def test_subprocess_blocked(self):
        path = self._write_tmp("import subprocess\n")
        valid, msg = validate_bot(path)
        assert valid is False
        os.unlink(path)

    def test_eval_blocked(self):
        path = self._write_tmp("eval('1+1')\n")
        valid, msg = validate_bot(path)
        assert valid is False
        os.unlink(path)

    def test_open_not_blocked(self):
        """Reading files is legitimate; open() should not be blocked."""
        path = self._write_tmp("with open('/tmp/test.txt', 'r') as f: pass\n")
        valid, msg = validate_bot(path)
        assert valid is True
        os.unlink(path)

    def test_nonexistent_file_raises(self):
        with pytest.raises(FileNotFoundError):
            validate_bot("/tmp/definitely_does_not_exist_xyz.py")


# ---------------------------------------------------------------------------
# core.sandbox_runner
# ---------------------------------------------------------------------------

from core.sandbox_runner import run_in_sandbox


class TestSandboxRunner:
    def _write_tmp(self, code: str) -> str:
        fd, path = tempfile.mkstemp(suffix=".py")
        with os.fdopen(fd, "w") as fh:
            fh.write(code)
        return path

    def test_successful_script(self):
        path = self._write_tmp("print('sandbox_ok')\n")
        result = run_in_sandbox(path)
        assert result["success"] is True
        assert "sandbox_ok" in result["output"]
        os.unlink(path)

    def test_failing_script(self):
        path = self._write_tmp("raise RuntimeError('intentional')\n")
        result = run_in_sandbox(path)
        assert result["success"] is False
        os.unlink(path)

    def test_timeout(self):
        path = self._write_tmp("import time\ntime.sleep(60)\n")
        result = run_in_sandbox(path, timeout=2)
        assert result["success"] is False
        assert "timed out" in result["error"].lower()
        os.unlink(path)


# ---------------------------------------------------------------------------
# core.bot_lab.BotLab
# ---------------------------------------------------------------------------

from core.bot_lab import BotLab


class TestBotLab:
    def setup_method(self):
        self.lab = BotLab()

    def test_load_bot_valid(self):
        bot = self.lab.load_bot("python_bots.real_estate.bot", "RealEstateBot")
        assert bot is not None
        assert bot.name == "RealEstateBot"

    def test_load_bot_invalid_module(self):
        bot = self.lab.load_bot("nonexistent.module.xyz", "NoBot")
        assert bot is None

    def test_load_bot_invalid_class(self):
        bot = self.lab.load_bot("python_bots.real_estate.bot", "NonexistentClass")
        assert bot is None

    def test_test_bot_success(self):
        bot = self.lab.load_bot("python_bots.real_estate.bot", "RealEstateBot")
        bus = RedisEventBus()
        passed = self.lab.test_bot(bot, bus)
        assert passed is True

    def test_test_bot_failure(self):
        class BrokenBot:
            name = "broken"

            def run(self, bus):
                raise RuntimeError("I am broken")

        passed = self.lab.test_bot(BrokenBot(), RedisEventBus())
        assert passed is False

    def test_train_bot(self):
        bot = self.lab.load_bot("python_bots.real_estate.bot", "RealEstateBot")
        result = self.lab.train_bot(bot)
        assert result is True

    def test_process_upload_safe_file(self):
        fd, path = tempfile.mkstemp(suffix=".py")
        with os.fdopen(fd, "w") as fh:
            fh.write("print('hello from uploaded bot')\n")
        result = self.lab.process_upload(path)
        os.unlink(path)
        assert result["status"] == "approved"

    def test_process_upload_blocked_file(self):
        fd, path = tempfile.mkstemp(suffix=".py")
        with os.fdopen(fd, "w") as fh:
            fh.write("import subprocess\n")
        result = self.lab.process_upload(path)
        os.unlink(path)
        assert result["status"] == "rejected"

    def test_process_upload_failing_script(self):
        fd, path = tempfile.mkstemp(suffix=".py")
        with os.fdopen(fd, "w") as fh:
            fh.write("raise RuntimeError('crash')\n")
        result = self.lab.process_upload(path)
        os.unlink(path)
        assert result["status"] == "failed"


# ---------------------------------------------------------------------------
# core.orchestrator.Orchestrator
# ---------------------------------------------------------------------------

from core.orchestrator import Orchestrator, handle_deal


class TestOrchestrator:
    def test_instantiates(self):
        orch = Orchestrator(repo_root=REPO_ROOT, auto_discover=False)
        assert orch is not None

    def test_start_runs_without_error(self):
        orch = Orchestrator(repo_root=REPO_ROOT, auto_discover=False)
        orch.start()  # should not raise

    def test_deal_events_emitted(self):
        orch = Orchestrator(repo_root=REPO_ROOT, auto_discover=False)
        orch.start()
        events = orch.bus.get_events("deal_found")
        assert len(events) >= 1

    def test_handle_deal_high_value(self, capsys):
        handle_deal({"profit": 50000, "address": "789 Profit Rd"})
        captured = capsys.readouterr()
        assert "HIGH VALUE DEAL" in captured.out

    def test_handle_deal_low_value(self, capsys):
        handle_deal({"profit": 100})
        captured = capsys.readouterr()
        assert "DEAL RECEIVED" in captured.out
        assert "HIGH VALUE DEAL" not in captured.out


# ---------------------------------------------------------------------------
# api.upload_api Flask endpoints
# ---------------------------------------------------------------------------

import io
from api.upload_api import app as flask_app


class TestUploadApi:
    def setup_method(self):
        flask_app.config["TESTING"] = True
        self.client = flask_app.test_client()
        clear_registry()

    def test_upload_safe_bot(self):
        data = {"file": (io.BytesIO(b"print('safe')\n"), "safe_bot.py")}
        resp = self.client.post(
            "/upload_bot",
            data=data,
            content_type="multipart/form-data",
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["status"] == "approved"

    def test_upload_blocked_bot(self):
        data = {"file": (io.BytesIO(b"import subprocess\n"), "bad_bot.py")}
        resp = self.client.post(
            "/upload_bot",
            data=data,
            content_type="multipart/form-data",
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["status"] == "rejected"

    def test_upload_non_py_rejected(self):
        data = {"file": (io.BytesIO(b"console.log('hi')"), "bot.js")}
        resp = self.client.post(
            "/upload_bot",
            data=data,
            content_type="multipart/form-data",
        )
        assert resp.status_code == 400

    def test_upload_no_file_returns_400(self):
        resp = self.client.post("/upload_bot", data={}, content_type="multipart/form-data")
        assert resp.status_code == 400

    def test_list_bots_endpoint(self):
        resp = self.client.get("/bots")
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    def test_upload_registers_bot(self):
        data = {"file": (io.BytesIO(b"print('registered')\n"), "reg_bot.py")}
        self.client.post(
            "/upload_bot",
            data=data,
            content_type="multipart/form-data",
        )
        bots = get_registered_bots()
        names = [b["name"] for b in bots]
        assert "reg_bot.py" in names
