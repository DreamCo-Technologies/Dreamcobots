"""
Comprehensive test suite for the Dreamcobots platform.

Covers all 8 requirement areas:
1. Bot System Integration (autonomy & scaling)
2. Communication Bot
3. Military-Grade Sandbox Tests
4. 3-Tier Pricing & Membership System
5. Best-in-Class Tools (file, media, text)
6. Niche Industry AI (healthcare, real estate, construction)
7. Bot Marketplace
8. Bot feature implementations
"""

import os
import sys
import tempfile
import uuid
from datetime import date

# Ensure the repo root is on the path for all imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

# ---------------------------------------------------------------------------
# 1. Core – Bot Base (autonomy & scaling)
# ---------------------------------------------------------------------------

from core.bot_base import AutonomyLevel, BotBase, ScalingLevel, SCALING_MULTIPLIERS


class TestBotBase:
    def test_default_state(self):
        bot = BotBase("TestBot")
        assert bot.name == "TestBot"
        assert bot.autonomy == AutonomyLevel.MANUAL
        assert bot.scaling == ScalingLevel.MODERATE
        assert not bot.is_running

    def test_start_stop(self):
        bot = BotBase("TestBot")
        bot.start()
        assert bot.is_running
        bot.stop()
        assert not bot.is_running

    def test_set_autonomy(self):
        bot = BotBase("TestBot")
        bot.set_autonomy(AutonomyLevel.FULLY_AUTONOMOUS)
        assert bot.autonomy == AutonomyLevel.FULLY_AUTONOMOUS

    def test_set_scaling(self):
        bot = BotBase("TestBot")
        bot.set_scaling(ScalingLevel.AGGRESSIVE)
        assert bot.scaling == ScalingLevel.AGGRESSIVE

    def test_scaling_multipliers(self):
        assert SCALING_MULTIPLIERS[ScalingLevel.CONSERVATIVE] == 1.0
        assert SCALING_MULTIPLIERS[ScalingLevel.MODERATE] == 2.5
        assert SCALING_MULTIPLIERS[ScalingLevel.AGGRESSIVE] == 5.0

    def test_execute_task_when_not_running(self):
        bot = BotBase("TestBot")
        result = bot.execute_task({"type": "test"})
        assert result["status"] == "error"

    def test_execute_task_manual(self):
        bot = BotBase("TestBot")
        bot.start()
        result = bot.execute_task({"type": "test"})
        assert result["status"] == "ok"

    def test_execute_task_semi_autonomous_no_validation(self):
        bot = BotBase("TestBot", autonomy=AutonomyLevel.SEMI_AUTONOMOUS)
        bot.start()
        result = bot.execute_task({"type": "test"})
        assert result["status"] == "pending_confirmation"

    def test_execute_task_semi_autonomous_validated(self):
        bot = BotBase("TestBot", autonomy=AutonomyLevel.SEMI_AUTONOMOUS)
        bot.start()
        result = bot.execute_task({"type": "test", "validated": True})
        assert result["status"] == "ok"

    def test_execute_task_fully_autonomous(self):
        bot = BotBase("TestBot", autonomy=AutonomyLevel.FULLY_AUTONOMOUS)
        bot.start()
        result = bot.execute_task({"type": "test"})
        assert result["status"] == "ok"

    def test_task_history(self):
        bot = BotBase("TestBot")
        bot.start()
        bot.execute_task({"type": "a"})
        bot.execute_task({"type": "b"})
        history = bot.get_task_history()
        assert len(history) == 2

    def test_get_status(self):
        bot = BotBase("TestBot")
        bot.start()
        status = bot.get_status()
        assert status["name"] == "TestBot"
        assert status["running"] is True
        assert "autonomy" in status
        assert "scaling" in status


# ---------------------------------------------------------------------------
# 2. Communication Bot
# ---------------------------------------------------------------------------

from communication_bot.communication_bot import CommunicationBot


class TestCommunicationBot:
    def setup_method(self):
        self.bot = CommunicationBot()
        self.bot.start()

    def test_send_message_valid_channel(self):
        msg = self.bot.send_message("email", "alice", "bob", "Hello Bob")
        assert msg.status == "sent"
        assert msg.channel == "email"

    def test_send_message_invalid_channel(self):
        with pytest.raises(ValueError):
            self.bot.send_message("fax", "a", "b", "test")

    def test_receive_message(self):
        msg = self.bot.receive_message("chat", "bob", "alice", "Hi Alice")
        assert msg.status == "delivered"
        inbox = self.bot.get_inbox(channel="chat")
        assert len(inbox) == 1

    def test_all_supported_channels(self):
        for channel in CommunicationBot.SUPPORTED_CHANNELS:
            msg = self.bot.send_message(channel, "x", "y", "test")
            assert msg.status == "sent"

    def test_initiate_and_close_deal(self):
        deal = self.bot.initiate_deal("Vendor A", {"price": 5000, "units": 10})
        assert deal["status"] == "initiated"
        assert self.bot.close_deal(deal["deal_id"])
        closed = next(d for d in self.bot.get_deals() if d["deal_id"] == deal["deal_id"])
        assert closed["status"] == "closed"

    def test_close_nonexistent_deal(self):
        assert not self.bot.close_deal(str(uuid.uuid4()))

    def test_bluetooth_transfer(self):
        transfer = self.bot.initiate_bluetooth_transfer("device-XYZ", "song.mp3", 5_000_000)
        assert transfer.status == "in_progress"
        assert self.bot.complete_bluetooth_transfer(transfer.transfer_id)
        assert self.bot.get_bluetooth_transfers()[0].status == "complete"

    def test_verification_notification(self):
        notif = self.bot.create_verification_notification("KYC pending", "https://app.dreamcobots.com/verify/123")
        assert not notif.resolved
        pending = self.bot.get_pending_notifications()
        assert len(pending) == 1
        assert self.bot.resolve_notification(notif.notification_id)
        assert len(self.bot.get_pending_notifications()) == 0

    def test_execute_task_send_message(self):
        result = self.bot.execute_task({
            "type": "send_message",
            "channel": "text",
            "sender": "bot",
            "recipient": "user-1",
            "content": "Hello!",
            "validated": True,
        })
        assert result["status"] == "ok"
        assert "message_id" in result


# ---------------------------------------------------------------------------
# 3. Sandbox
# ---------------------------------------------------------------------------

from sandbox.sandbox import SandboxTester, Scenario


class TestSandbox:
    def setup_method(self):
        self.bot = BotBase("SandboxBot")
        self.bot.start()
        self.tester = SandboxTester(iterations=10)

    def test_run_with_no_scenarios(self):
        results = self.tester.run(self.bot)
        assert results == {}

    def test_run_scenario(self):
        scenario = Scenario(
            name="basic_task",
            description="Simple task execution",
            task={"type": "generic"},
            expected_status="ok",
        )
        self.tester.add_scenario(scenario)
        results = self.tester.run(self.bot)
        assert "basic_task" in results
        metrics = results["basic_task"]
        assert metrics.total_iterations == 10
        assert metrics.pass_rate == 100.0

    def test_remove_scenario(self):
        scenario = Scenario("s1", "desc", {"type": "x"})
        self.tester.add_scenario(scenario)
        assert self.tester.remove_scenario(scenario.scenario_id)
        assert len(self.tester.get_scenarios()) == 0

    def test_dashboard_no_results(self):
        output = self.tester.dashboard()
        assert "No results" in output

    def test_dashboard_with_results(self):
        scenario = Scenario("perf_test", "desc", {"type": "generic"})
        self.tester.add_scenario(scenario)
        self.tester.run(self.bot)
        output = self.tester.dashboard()
        assert "perf_test" in output

    def test_stress_test(self):
        metrics = self.tester.run_stress_test(self.bot, {"type": "generic"}, duration_seconds=0.1)
        assert metrics.total_iterations > 0
        assert metrics.throughput_ops_per_second > 0

    def test_roi_calculation(self):
        scenario = Scenario("roi_test", "desc", {"type": "generic"})
        self.tester.add_scenario(scenario)
        results = self.tester.run(self.bot)
        # All tasks pass so ROI should be 50%
        assert results["roi_test"].roi_percent == 50.0


# ---------------------------------------------------------------------------
# 4. Pricing & Membership
# ---------------------------------------------------------------------------

from pricing.membership import BillingCycle, MembershipManager, MembershipPlan, MembershipTier


class TestMembership:
    def setup_method(self):
        self.manager = MembershipManager()

    def test_subscribe(self):
        sub = self.manager.subscribe("user-1", MembershipTier.PREMIUM, BillingCycle.MONTHLY)
        assert sub.plan.tier == MembershipTier.PREMIUM
        assert sub.plan.billing_cycle == BillingCycle.MONTHLY
        assert sub.active

    def test_cancel(self):
        self.manager.subscribe("user-2", MembershipTier.FREE, BillingCycle.MONTHLY)
        assert self.manager.cancel("user-2")
        sub = self.manager.get_subscription("user-2")
        assert not sub.active

    def test_upgrade(self):
        self.manager.subscribe("user-3", MembershipTier.FREE, BillingCycle.MONTHLY)
        upgraded = self.manager.upgrade("user-3", MembershipTier.ELITE)
        assert upgraded.plan.tier == MembershipTier.ELITE

    def test_has_feature_free(self):
        self.manager.subscribe("user-4", MembershipTier.FREE, BillingCycle.MONTHLY)
        assert self.manager.has_feature("user-4", "Basic bot services")
        assert not self.manager.has_feature("user-4", "Unlimited access to all bots and tools")

    def test_has_feature_elite(self):
        self.manager.subscribe("user-5", MembershipTier.ELITE, BillingCycle.YEARLY)
        assert self.manager.has_feature("user-5", "Unlimited access to all bots and tools")

    def test_plan_prices(self):
        free = MembershipPlan(MembershipTier.FREE, BillingCycle.MONTHLY)
        assert free.price == 0.0

        premium_monthly = MembershipPlan(MembershipTier.PREMIUM, BillingCycle.MONTHLY)
        premium_yearly = MembershipPlan(MembershipTier.PREMIUM, BillingCycle.YEARLY)
        assert premium_yearly.price < premium_monthly.price * 12  # annual discount

    def test_list_plans_covers_all_tiers_and_cycles(self):
        plans = self.manager.list_plans()
        tiers = {p["tier"] for p in plans}
        cycles = {p["billing_cycle"] for p in plans}
        assert tiers == {"free", "premium", "elite"}
        assert cycles == {"weekly", "monthly", "yearly"}

    def test_active_subscribers(self):
        self.manager.subscribe("u-a", MembershipTier.FREE, BillingCycle.MONTHLY)
        self.manager.subscribe("u-b", MembershipTier.PREMIUM, BillingCycle.MONTHLY)
        self.manager.cancel("u-b")
        active = self.manager.active_subscribers()
        ids = [s.member_id for s in active]
        assert "u-a" in ids
        assert "u-b" not in ids


# ---------------------------------------------------------------------------
# 5. Tools – File Utils
# ---------------------------------------------------------------------------

from tools.file_utils import FileUtils


class TestFileUtils:
    def test_checksum_bytes(self):
        data = b"hello world"
        digest = FileUtils.checksum_bytes(data)
        assert len(digest) == 64  # SHA-256 hex

    def test_split_bytes(self):
        data = b"x" * 100
        chunks = FileUtils.split_bytes(data, chunk_size=30)
        assert len(chunks) == 4  # 30+30+30+10
        assert sum(len(c) for c in chunks) == 100

    def test_compress_decompress(self):
        fu = FileUtils()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write a test file
            src = os.path.join(tmpdir, "test.txt")
            with open(src, "w") as f:
                f.write("Dreamcobots test content")

            archive = os.path.join(tmpdir, "archive.zip")
            fu.compress([src], archive)
            assert os.path.isfile(archive)

            out_dir = os.path.join(tmpdir, "extracted")
            os.makedirs(out_dir)
            extracted = fu.decompress(archive, out_dir)
            assert len(extracted) == 1
            with open(extracted[0]) as f:
                assert "Dreamcobots" in f.read()

    def test_copy_large_file(self):
        fu = FileUtils()
        with tempfile.TemporaryDirectory() as tmpdir:
            src = os.path.join(tmpdir, "src.bin")
            dst = os.path.join(tmpdir, "dst.bin")
            data = b"A" * (1024 * 1024)  # 1 MB
            with open(src, "wb") as f:
                f.write(data)
            bytes_copied = fu.copy_large_file(src, dst)
            assert bytes_copied == len(data)
            assert fu.checksum(src) == fu.checksum(dst)

    def test_metadata(self):
        fu = FileUtils()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "meta.txt")
            with open(path, "w") as f:
                f.write("test")
            meta = fu.get_metadata(path)
            assert meta["exists"] is True
            assert meta["extension"] == ".txt"
            assert meta["size_bytes"] == 4


# ---------------------------------------------------------------------------
# 5. Tools – Media Recognition
# ---------------------------------------------------------------------------

from tools.media_recognition import MediaRecognition, MediaTrack


class TestMediaRecognition:
    def setup_method(self):
        self.mr = MediaRecognition()

    def _make_track(self):
        audio = b"fake audio data for testing purposes" * 100
        fp = MediaRecognition.compute_fingerprint(audio)
        track = MediaTrack(
            title="Test Song", artist="Test Artist", album="Test Album",
            genre="Pop", duration_seconds=180.0, fingerprint=fp,
            download_url="https://cdn.dreamcobots.com/test.mp3",
        )
        self.mr.register_track(track)
        return audio, track

    def test_exact_match(self):
        audio, track = self._make_track()
        result = self.mr.recognize(audio)
        assert result.success
        assert result.confidence == 1.0
        assert result.track.title == "Test Song"

    def test_empty_audio(self):
        result = self.mr.recognize(b"")
        assert not result.success

    def test_unknown_audio(self):
        result = self.mr.recognize(b"completely different audio content xyz" * 50)
        # May or may not match depending on hash similarity, just check structure
        assert isinstance(result.success, bool)

    def test_download_options(self):
        _, track = self._make_track()
        options = self.mr.get_download_options(track)
        assert len(options) == 4
        apps = [o["app"] for o in options]
        assert "Spotify" in apps
        assert "Direct Download" in apps

    def test_detect_media_type(self):
        assert MediaRecognition.detect_media_type("song.mp3") == "audio/mpeg"
        assert MediaRecognition.detect_media_type("video.mp4") == "video/mp4"

    def test_catalogue(self):
        _, track = self._make_track()
        catalogue = self.mr.get_catalogue()
        assert len(catalogue) == 1
        assert catalogue[0].title == "Test Song"


# ---------------------------------------------------------------------------
# 5. Tools – Text Processing
# ---------------------------------------------------------------------------

from tools.text_processing import TextProcessor


class TestTextProcessor:
    def setup_method(self):
        self.tp = TextProcessor()

    def test_create_overlay(self):
        overlay = self.tp.create_overlay("Hello World", 0.0, 5.0)
        assert overlay.text == "Hello World"
        assert len(self.tp.get_overlays()) == 1

    def test_overlay_validation_empty_text(self):
        with pytest.raises(ValueError):
            self.tp.create_overlay("   ", 0.0, 5.0)

    def test_overlay_validation_bad_times(self):
        with pytest.raises(ValueError):
            self.tp.create_overlay("test", 5.0, 3.0)

    def test_remove_overlay(self):
        overlay = self.tp.create_overlay("Bye", 1.0, 4.0)
        assert self.tp.remove_overlay(overlay.overlay_id)
        assert len(self.tp.get_overlays()) == 0

    def test_generate_ffmpeg_drawtext(self):
        overlay = self.tp.create_overlay("Hi", 0.0, 5.0, position=(20, 30))
        cmd = self.tp.generate_ffmpeg_drawtext(overlay)
        assert "drawtext" in cmd
        assert "x=20" in cmd
        assert "y=30" in cmd

    def test_translate_known(self):
        result = self.tp.translate("hello", "es")
        assert result.translated_text == "hola"
        assert result.target_language == "es"

    def test_translate_same_language(self):
        result = self.tp.translate("hello", "en")
        assert result.translated_text == "hello"

    def test_translate_unsupported_language(self):
        with pytest.raises(ValueError):
            self.tp.translate("hello", "xx")

    def test_batch_translate(self):
        results = self.tp.batch_translate(["hello", "goodbye"], "fr")
        assert results[0].translated_text == "bonjour"
        assert results[1].translated_text == "au revoir"

    def test_synthesize_speech(self):
        seg = self.tp.synthesize_speech("Hello Dreamcobots", voice="en-US", speed=1.0, pitch=1.0)
        assert seg.text == "Hello Dreamcobots"
        assert len(self.tp.get_speech_queue()) == 1

    def test_synthesize_speech_bad_speed(self):
        with pytest.raises(ValueError):
            self.tp.synthesize_speech("test", speed=3.0)

    def test_synthesize_speech_bad_format(self):
        with pytest.raises(ValueError):
            self.tp.synthesize_speech("test", audio_format="flac")

    def test_sanitize(self):
        raw = "Hello\x00\x01World"
        assert TextProcessor.sanitize(raw) == "HelloWorld"

    def test_word_count(self):
        assert TextProcessor.word_count("one two three") == 3

    def test_extract_keywords(self):
        kw = TextProcessor.extract_keywords("Dreamcobots builds amazing intelligent bots for automation")
        assert "dreamcobots" in kw
        assert "amazing" in kw
        # Short words excluded
        assert "for" not in kw


# ---------------------------------------------------------------------------
# 6. Industry – Healthcare AI
# ---------------------------------------------------------------------------

from industry.healthcare_ai import HealthcareAI, Patient, TriageResult


class TestHealthcareAI:
    def setup_method(self):
        self.bot = HealthcareAI(autonomy=AutonomyLevel.MANUAL)
        self.bot.start()
        self.patient = Patient("p-001", "Alice Smith", date(1990, 5, 15))
        self.bot.add_patient(self.patient)

    def test_add_and_get_patient(self):
        p = self.bot.get_patient("p-001")
        assert p.name == "Alice Smith"

    def test_triage_emergency(self):
        result = self.bot.triage("p-001", ["chest pain", "difficulty breathing"])
        assert result.urgency == "emergency"
        assert result.confidence >= 0.9

    def test_triage_high(self):
        result = self.bot.triage("p-001", ["high fever", "severe headache"])
        assert result.urgency == "high"

    def test_triage_moderate(self):
        result = self.bot.triage("p-001", ["mild cough", "runny nose"])
        assert result.urgency == "moderate"

    def test_triage_low_no_symptoms(self):
        result = self.bot.triage("p-001", [])
        assert result.urgency == "low"

    def test_schedule_appointment(self):
        appt = self.bot.schedule_appointment("p-001", date(2026, 4, 1), "Dr. Jones", "Follow-up")
        assert appt["status"] == "scheduled"
        assert len(self.bot.get_appointments("p-001")) == 1

    def test_generate_report(self):
        self.bot.triage("p-001", ["chest pain"])
        report = self.bot.generate_report()
        assert report["total_patients"] == 1
        assert report["triage_summary"]["emergency"] == 1


# ---------------------------------------------------------------------------
# 6. Industry – Real Estate AI
# ---------------------------------------------------------------------------

from industry.real_estate import Lead, Property, RealEstateAI


class TestRealEstateAI:
    def setup_method(self):
        self.bot = RealEstateAI(autonomy=AutonomyLevel.MANUAL)
        self.bot.start()
        self.prop = Property("prop-1", "123 Main St", "Austin", "TX", "78701", "sale", 400000, 3, 2.0, 1800)
        self.bot.add_property(self.prop)

    def test_add_and_get_property(self):
        p = self.bot.get_property("prop-1")
        assert p.address == "123 Main St"

    def test_search_by_city(self):
        results = self.bot.search_properties(city="Austin")
        assert len(results) == 1

    def test_search_by_price(self):
        results = self.bot.search_properties(max_price=300000)
        assert len(results) == 0

    def test_update_property_status(self):
        assert self.bot.update_property_status("prop-1", "sold")
        assert self.bot.get_property("prop-1").status == "sold"

    def test_estimate_value(self):
        self.bot.record_market_data("Austin", 300000, 100, "2026-01")
        value = self.bot.estimate_value(1500, 3, "Austin")
        assert value > 0

    def test_add_and_qualify_lead(self):
        lead = Lead("lead-1", "Bob", "bob@test.com", "555-0000", "buy", 500000, ["Austin"])
        self.bot.add_lead(lead)
        assert self.bot.qualify_lead("lead-1")
        assert self.bot.get_lead("lead-1").status == "qualified"

    def test_generate_report(self):
        report = self.bot.generate_report()
        assert report["total_listings"] == 1
        assert report["active_listings"] == 1


# ---------------------------------------------------------------------------
# 6. Industry – Construction AI
# ---------------------------------------------------------------------------

from industry.construction import ConstructionAI, ConstructionProject


class TestConstructionAI:
    def setup_method(self):
        self.bot = ConstructionAI(autonomy=AutonomyLevel.MANUAL)
        self.bot.start()
        self.project = ConstructionProject(
            "proj-1", "Office Tower", "Acme Corp", "Dallas, TX",
            date(2026, 1, 1), date(2026, 12, 31), 2_000_000.0
        )
        self.bot.create_project(self.project)

    def test_create_and_get_project(self):
        p = self.bot.get_project("proj-1")
        assert p.name == "Office Tower"

    def test_update_progress(self):
        assert self.bot.update_progress("proj-1", 50.0)
        assert self.bot.get_project("proj-1").progress_percent == 50.0

    def test_update_progress_completes_at_100(self):
        self.bot.update_progress("proj-1", 100.0)
        assert self.bot.get_project("proj-1").status == "complete"

    def test_generate_phase_schedule(self):
        phases = ["Foundation", "Structure", "Finishing"]
        schedule = self.bot.generate_phase_schedule("proj-1", phases)
        assert len(schedule) == 3

    def test_allocate_resource_and_cost(self):
        self.bot.allocate_resource("proj-1", "labour", 100, "workers", 150)
        costs = self.bot.estimate_total_cost("proj-1")
        assert costs["raw_cost"] == 15000.0
        assert costs["overhead"] == round(15000.0 * 0.15, 2)
        assert costs["total_cost"] == costs["raw_cost"] + costs["overhead"]

    def test_safety_check(self):
        self.bot.record_safety_check("proj-1", "PPE", True, "All workers wearing hard hats")
        self.bot.record_safety_check("proj-1", "scaffolding", False, "Scaffolding tag expired")
        summary = self.bot.get_safety_summary("proj-1")
        assert summary["passed"] == 1
        assert summary["failed"] == 1
        assert summary["compliance_rate"] == 50.0

    def test_generate_report(self):
        report = self.bot.generate_report()
        assert report["total_projects"] == 1


# ---------------------------------------------------------------------------
# 7. Marketplace
# ---------------------------------------------------------------------------

from marketplace.marketplace import BotListing, BotMarketplace


class TestMarketplace:
    def setup_method(self):
        self.market = BotMarketplace()
        self.listing = BotListing(
            name="CRM Bot",
            description="Automates CRM workflows.",
            category="business",
            price_usd=49.99,
            seller_id="seller-1",
            tags=["crm", "automation"],
            instructions="Deploy via `python crm_bot.py`",
        )
        self.market.list_bot(self.listing)

    def test_list_and_get(self):
        retrieved = self.market.get_listing(self.listing.listing_id)
        assert retrieved.name == "CRM Bot"

    def test_browse_all(self):
        results = self.market.browse()
        assert len(results) == 1

    def test_browse_by_category(self):
        assert len(self.market.browse(category="business")) == 1
        assert len(self.market.browse(category="healthcare")) == 0

    def test_browse_by_price(self):
        assert len(self.market.browse(max_price=100.0)) == 1
        assert len(self.market.browse(max_price=10.0)) == 0

    def test_browse_by_tag(self):
        assert len(self.market.browse(tag="crm")) == 1
        assert len(self.market.browse(tag="unknown")) == 0

    def test_search(self):
        assert len(self.market.search("CRM")) == 1
        assert len(self.market.search("healthcare")) == 0

    def test_purchase(self):
        purchase = self.market.purchase("buyer-1", self.listing.listing_id)
        assert purchase.buyer_id == "buyer-1"
        assert purchase.price_paid_usd == 49.99

    def test_purchase_unavailable(self):
        self.market.delist_bot(self.listing.listing_id, "seller-1")
        with pytest.raises(ValueError):
            self.market.purchase("buyer-2", self.listing.listing_id)

    def test_purchase_nonexistent(self):
        with pytest.raises(ValueError):
            self.market.purchase("buyer-1", "nonexistent-id")

    def test_deploy(self):
        purchase = self.market.purchase("buyer-3", self.listing.listing_id)
        assert self.market.deploy(purchase.purchase_id)
        purchases = self.market.get_purchases("buyer-3")
        assert purchases[0].deployed

    def test_delist(self):
        assert self.market.delist_bot(self.listing.listing_id, "seller-1")
        assert not self.market.get_listing(self.listing.listing_id).available

    def test_delist_wrong_seller(self):
        assert not self.market.delist_bot(self.listing.listing_id, "wrong-seller")

    def test_marketplace_stats(self):
        self.market.purchase("buyer-4", self.listing.listing_id)
        stats = self.market.marketplace_stats()
        assert stats["total_listings"] == 1
        assert stats["total_purchases"] == 1
        assert stats["total_revenue_usd"] == 49.99
