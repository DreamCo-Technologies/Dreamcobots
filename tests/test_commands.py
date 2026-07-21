# Unit tests for Dreamcobots commands, communication, content, and rendering.

import sys
import os
import unittest

# Add project root to path so all modules can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from BuddyAI.commands import CommandHandler
from communications.bluetooth_handler import BluetoothHandler
from communications.http_websocket_handler import WebSocketCommunicationHandler
from content.chat_content import ChatContent
from content.movie_info import MovieInfo
from content.random_facts import RandomFacts
from cross_platform.renderer import CrossPlatformRenderer


# =============================================================================
# CommandHandler tests
# =============================================================================

class TestCommandHandler(unittest.TestCase):

    def setUp(self):
        self.handler = CommandHandler()

    def test_run_bot_creates_bot(self):
        result = self.handler.run_bot("bot-1")
        self.assertEqual(result["status"], "running")
        self.assertEqual(result["bot_id"], "bot-1")
        self.assertIn("bot-1", self.handler.bots)

    def test_run_bot_updates_existing(self):
        self.handler.run_bot("bot-1")
        self.handler.pause_bot("bot-1")
        result = self.handler.run_bot("bot-1")
        self.assertEqual(result["status"], "running")

    def test_pause_bot_known(self):
        self.handler.run_bot("bot-2")
        result = self.handler.pause_bot("bot-2")
        self.assertEqual(result["status"], "paused")

    def test_pause_bot_unknown(self):
        result = self.handler.pause_bot("nonexistent-bot")
        self.assertIn("error", result)

    def test_bot_status_specific(self):
        self.handler.run_bot("bot-3")
        result = self.handler.bot_status("bot-3")
        self.assertEqual(result["bot_id"], "bot-3")
        self.assertIn("status", result)

    def test_bot_status_all(self):
        self.handler.run_bot("bot-a")
        self.handler.run_bot("bot-b")
        result = self.handler.bot_status()
        self.assertIn("bots", result)
        self.assertIn("bot-a", result["bots"])
        self.assertIn("bot-b", result["bots"])

    def test_broadcast_message(self):
        self.handler.run_bot("bot-1")
        self.handler.run_bot("bot-2")
        result = self.handler.broadcast_message("Hello bots!")
        self.assertEqual(result["message"], "Hello bots!")
        self.assertGreaterEqual(result["delivered"], 2)

    def test_broadcast_message_targeted(self):
        result = self.handler.broadcast_message("Ping", target_bots=["bot-x"])
        self.assertEqual(result["targets"], ["bot-x"])
        self.assertEqual(result["delivered"], 1)

    def test_analytics_returns_data(self):
        self.handler.run_bot("bot-1")
        result = self.handler.get_analytics()
        self.assertIn("uptime_seconds", result)
        self.assertIn("total_bots", result)
        self.assertGreaterEqual(result["commands_executed"], 1)

    def test_device_register(self):
        result = self.handler.device_register("device-001", "smart_tv", {"brand": "Samsung"})
        self.assertEqual(result["status"], "registered")
        self.assertEqual(result["device_id"], "device-001")
        self.assertIn("device-001", self.handler.devices)

    def test_analytics_increments(self):
        before = self.handler.analytics["commands_executed"]
        self.handler.run_bot("incr-bot")
        self.handler.pause_bot("incr-bot")
        self.handler.get_analytics()
        after = self.handler.analytics["commands_executed"]
        self.assertGreater(after, before)

    def test_dispatch_run_bot(self):
        result = self.handler.dispatch("/run-bot", bot_id="dispatch-bot")
        self.assertEqual(result["status"], "running")

    def test_dispatch_unknown_command(self):
        result = self.handler.dispatch("/nonexistent")
        self.assertIn("error", result)

    def test_device_register_analytics(self):
        before = self.handler.analytics["devices_registered"]
        self.handler.device_register("d-2", "phone")
        after = self.handler.analytics["devices_registered"]
        self.assertEqual(after, before + 1)


# =============================================================================
# BluetoothHandler tests
# =============================================================================

class TestBluetoothHandler(unittest.TestCase):

    def setUp(self):
        self.bt = BluetoothHandler(simulate=True)

    def test_discover_returns_devices(self):
        devices = self.bt.discover()
        self.assertGreater(len(devices), 0)
        for d in devices:
            self.assertIn("address", d)
            self.assertIn("name", d)

    def test_discover_limit(self):
        devices = self.bt.discover(limit=2)
        self.assertLessEqual(len(devices), 2)

    def test_pair_discovered_device(self):
        self.bt.discover()
        address = list(self.bt.discovered_devices.keys())[0]
        result = self.bt.pair(address)
        self.assertEqual(result["status"], "paired")
        self.assertTrue(result["device"]["paired"])

    def test_pair_unknown_device(self):
        result = self.bt.pair("FF:FF:FF:FF:FF:FF")
        self.assertIn("error", result)

    def test_unpair(self):
        self.bt.discover()
        address = list(self.bt.discovered_devices.keys())[0]
        self.bt.pair(address)
        result = self.bt.unpair(address)
        self.assertEqual(result["status"], "unpaired")
        self.assertNotIn(address, self.bt.paired_devices)

    def test_connect_paired_device(self):
        self.bt.discover()
        address = list(self.bt.discovered_devices.keys())[0]
        self.bt.pair(address)
        result = self.bt.connect(address)
        self.assertEqual(result["status"], "connected")

    def test_connect_unpaired_device(self):
        self.bt.discover()
        address = list(self.bt.discovered_devices.keys())[0]
        # pair but then unpair before connecting
        self.bt.pair(address)
        self.bt.unpair(address)
        result = self.bt.connect(address)
        self.assertIn("error", result)

    def test_disconnect(self):
        self.bt.discover()
        address = list(self.bt.discovered_devices.keys())[0]
        self.bt.pair(address)
        self.bt.connect(address)
        result = self.bt.disconnect(address)
        self.assertEqual(result["status"], "disconnected")

    def test_send_data(self):
        self.bt.discover()
        address = list(self.bt.discovered_devices.keys())[0]
        self.bt.pair(address)
        self.bt.connect(address)
        result = self.bt.send_data(address, "Hello device!")
        self.assertEqual(result["direction"], "send")
        self.assertEqual(result["data"], "Hello device!")

    def test_receive_data(self):
        self.bt.discover()
        address = list(self.bt.discovered_devices.keys())[0]
        self.bt.pair(address)
        self.bt.connect(address)
        result = self.bt.receive_data(address, "Ack")
        self.assertEqual(result["direction"], "receive")

    def test_data_log(self):
        self.bt.discover()
        address = list(self.bt.discovered_devices.keys())[0]
        self.bt.pair(address)
        self.bt.connect(address)
        self.bt.send_data(address, "msg1")
        self.bt.receive_data(address, "msg2")
        log = self.bt.get_data_log()
        self.assertEqual(len(log), 2)

    def test_send_data_not_connected(self):
        result = self.bt.send_data("00:00:00:00:00:00", "data")
        self.assertIn("error", result)


# =============================================================================
# WebSocketCommunicationHandler tests
# =============================================================================

class TestWebSocketHandler(unittest.TestCase):

    def setUp(self):
        self.ws = WebSocketCommunicationHandler()

    def test_connect_client(self):
        cid = self.ws.connect_client("client-1")
        self.assertEqual(cid, "client-1")
        self.assertIn("client-1", self.ws.connected_clients)

    def test_disconnect_client(self):
        self.ws.connect_client("client-2")
        self.ws.disconnect_client("client-2")
        self.assertNotIn("client-2", self.ws.connected_clients)

    def test_send_message(self):
        self.ws.connect_client("client-3")
        result = self.ws.send("client-3", "test message")
        self.assertEqual(result["message"], "test message")
        self.assertEqual(result["to"], "client-3")

    def test_send_to_disconnected(self):
        result = self.ws.send("nonexistent", "hi")
        self.assertIn("error", result)

    def test_broadcast(self):
        self.ws.connect_client("c1")
        self.ws.connect_client("c2")
        results = self.ws.broadcast("hello all")
        self.assertEqual(len(results), 2)

    def test_receive_message(self):
        self.ws.connect_client("client-4")
        result = self.ws.receive("client-4", "incoming")
        self.assertEqual(result["from"], "client-4")
        self.assertEqual(result["message"], "incoming")

    def test_message_bus_records(self):
        self.ws.connect_client("c5")
        self.ws.send("c5", "msg1")
        self.ws.receive("c5", "msg2")
        bus = self.ws.get_message_bus()
        self.assertEqual(len(bus), 2)


# =============================================================================
# MovieInfo tests
# =============================================================================

class TestMovieInfo(unittest.TestCase):

    def setUp(self):
        self.movies = MovieInfo()

    def test_get_random_returns_dict(self):
        movie = self.movies.get_random()
        self.assertIsInstance(movie, dict)
        self.assertIn("title", movie)

    def test_search_by_title(self):
        results = self.movies.search_by_title("inception")
        self.assertTrue(any(m["title"] == "Inception" for m in results))

    def test_search_by_title_no_result(self):
        results = self.movies.search_by_title("xyznonexistent")
        self.assertEqual(results, [])

    def test_search_by_genre(self):
        results = self.movies.search_by_genre("Sci-Fi")
        self.assertGreater(len(results), 0)
        for m in results:
            self.assertIn("Sci-Fi", m["genre"])

    def test_get_top_rated(self):
        top = self.movies.get_top_rated(3)
        self.assertEqual(len(top), 3)
        ratings = [m["rating"] for m in top]
        self.assertEqual(ratings, sorted(ratings, reverse=True))

    def test_display_format(self):
        movie = self.movies.search_by_title("Inception")[0]
        text = self.movies.display(movie)
        self.assertIn("Inception", text)
        self.assertIn("Nolan", text)


# =============================================================================
# ChatContent tests
# =============================================================================

class TestChatContent(unittest.TestCase):

    def setUp(self):
        self.chat = ChatContent()

    def test_get_random_joke(self):
        joke = self.chat.get_random_joke()
        self.assertIn("setup", joke)
        self.assertIn("punchline", joke)

    def test_format_joke(self):
        text = self.chat.format_joke()
        self.assertIn("👉", text)

    def test_get_fun_response(self):
        response = self.chat.get_fun_response()
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

    def test_get_greeting(self):
        greeting = self.chat.get_greeting()
        self.assertIsInstance(greeting, str)

    def test_chat_joke_trigger(self):
        reply = self.chat.chat("tell me a joke")
        self.assertIn("👉", reply)

    def test_chat_greeting_trigger(self):
        reply = self.chat.chat("hello there")
        self.assertIsInstance(reply, str)
        self.assertGreater(len(reply), 0)


# =============================================================================
# RandomFacts tests
# =============================================================================

class TestRandomFacts(unittest.TestCase):

    def setUp(self):
        self.facts = RandomFacts()

    def test_get_random_fact(self):
        fact = self.facts.get_random_fact()
        self.assertIsInstance(fact, str)
        self.assertGreater(len(fact), 0)

    def test_get_tech_fact(self):
        fact = self.facts.get_tech_fact()
        self.assertIsInstance(fact, str)

    def test_get_general_fact(self):
        fact = self.facts.get_general_fact()
        self.assertIsInstance(fact, str)

    def test_get_multiple(self):
        facts = self.facts.get_multiple(3)
        self.assertEqual(len(facts), 3)
        self.assertEqual(len(set(facts)), 3)  # all unique

    def test_display_format(self):
        text = self.facts.display()
        self.assertIn("Did you know", text)

    def test_custom_facts(self):
        custom = RandomFacts(custom_facts=["Custom fact here."])
        all_facts = custom.general_facts
        self.assertIn("Custom fact here.", all_facts)


# =============================================================================
# CrossPlatformRenderer tests
# =============================================================================

class TestCrossplatformRenderer(unittest.TestCase):

    def test_computer_render(self):
        renderer = CrossPlatformRenderer("computer")
        output = renderer.render("Hello World")
        self.assertIn("COMPUTER", output)
        self.assertIn("Hello World", output)

    def test_phone_render_wraps(self):
        renderer = CrossPlatformRenderer("phone")
        long_text = "This is a very long text that should be wrapped for phone screens."
        output = renderer.render(long_text)
        # Output must be wrapped so each line <= max_width
        max_width = renderer.profile["max_width"]
        content_lines = output.split("\n")[2:-1]  # skip borders and label
        for line in content_lines:
            self.assertLessEqual(len(line), max_width)

    def test_smart_tv_render(self):
        renderer = CrossPlatformRenderer("smart_tv")
        output = renderer.render("TV Content")
        self.assertIn("SMART_TV", output)

    def test_emoji_stripped_for_other(self):
        renderer = CrossPlatformRenderer("other")
        output = renderer.render("Hello 🎬 World")
        self.assertNotIn("🎬", output)

    def test_render_movie_dict(self):
        renderer = CrossPlatformRenderer("computer")
        movie = {
            "title": "Test Movie",
            "year": 2024,
            "genre": ["Sci-Fi"],
            "director": "Test Director",
            "rating": 9.0,
            "description": "A test movie.",
        }
        output = renderer.render(movie, content_type="movie")
        self.assertIn("Test Movie", output)
        self.assertIn("Test Director", output)

    def test_render_list(self):
        renderer = CrossPlatformRenderer("tablet")
        items = ["Item one", "Item two", "Item three"]
        output = renderer.render_list(items)
        self.assertIn("Item one", output)
        self.assertIn("Item three", output)

    def test_unknown_platform_uses_other(self):
        from cross_platform.renderer import PLATFORM_PROFILES
        renderer = CrossPlatformRenderer("unknown_device")
        self.assertEqual(renderer.profile, PLATFORM_PROFILES["other"])
        output = renderer.render("Test")
        self.assertIsInstance(output, str)


if __name__ == "__main__":
    unittest.main()
