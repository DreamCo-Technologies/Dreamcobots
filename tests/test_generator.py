"""Tests for bots/bot_generator_bot/generator.py"""
import sys
import os
import shutil
import tempfile

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest
from bots.bot_generator_bot.generator import Generator, _to_snake_case, _to_class_name


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

class TestToSnakeCase:
    def test_simple_name(self):
        assert _to_snake_case("Lead Bot") == "lead_bot"

    def test_already_snake_case(self):
        assert _to_snake_case("lead_bot") == "lead_bot"

    def test_multiple_spaces(self):
        assert _to_snake_case("Real Estate Bot") == "real_estate_bot"

    def test_camel_case(self):
        assert _to_snake_case("LeadBot") == "lead_bot"

    def test_strips_special_chars(self):
        result = _to_snake_case("Lead-Bot!")
        assert "!" not in result


class TestToClassName:
    def test_simple_name(self):
        assert _to_class_name("Lead Bot") == "LeadBot"

    def test_snake_case_input(self):
        assert _to_class_name("lead_bot") == "LeadBot"

    def test_hyphenated_input(self):
        assert _to_class_name("lead-scraper-bot") == "LeadScraperBot"

    def test_multiple_words(self):
        assert _to_class_name("Real Estate Deal Finder Bot") == "RealEstateDealFinderBot"


# ---------------------------------------------------------------------------
# Generator with temp bots directory
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_bots_dir():
    """Provide a temporary directory as the bots root."""
    d = tempfile.mkdtemp(prefix="dreamco_bots_")
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def generator(tmp_bots_dir):
    return Generator(bots_root=tmp_bots_dir)


# ---------------------------------------------------------------------------
# Instantiation
# ---------------------------------------------------------------------------

class TestGeneratorInstantiation:
    def test_instantiates(self, tmp_bots_dir):
        gen = Generator(bots_root=tmp_bots_dir)
        assert gen is not None

    def test_bots_root_is_absolute(self, generator):
        assert os.path.isabs(generator.bots_root)

    def test_initial_generation_log_empty(self, generator):
        assert generator.get_generation_log() == []

    def test_initial_summary_zero_bots(self, generator):
        summary = generator.get_summary()
        assert summary["total_bots_generated"] == 0


# ---------------------------------------------------------------------------
# Dry run
# ---------------------------------------------------------------------------

class TestDryRun:
    def test_dry_run_returns_result(self, generator):
        result = generator.create_bot("Test Bot", dry_run=True)
        assert result["bot_name"] == "Test Bot"
        assert result["dry_run"] is True

    def test_dry_run_does_not_create_directory(self, generator, tmp_bots_dir):
        generator.create_bot("Phantom Bot", dry_run=True)
        expected = os.path.join(tmp_bots_dir, "phantom_bot")
        assert not os.path.exists(expected)

    def test_dry_run_logs_to_generation_log(self, generator):
        generator.create_bot("Log Bot", dry_run=True)
        assert len(generator.get_generation_log()) == 1


# ---------------------------------------------------------------------------
# Real creation
# ---------------------------------------------------------------------------

class TestBotCreation:
    def test_creates_bot_directory(self, generator, tmp_bots_dir):
        generator.create_bot("New Bot", register=False)
        bot_dir = os.path.join(tmp_bots_dir, "new_bot")
        assert os.path.isdir(bot_dir)

    def test_creates_main_python_file(self, generator, tmp_bots_dir):
        generator.create_bot("New Bot", register=False)
        main_file = os.path.join(tmp_bots_dir, "new_bot", "new_bot.py")
        assert os.path.isfile(main_file)

    def test_creates_init_file(self, generator, tmp_bots_dir):
        generator.create_bot("New Bot", register=False)
        init_file = os.path.join(tmp_bots_dir, "new_bot", "__init__.py")
        assert os.path.isfile(init_file)

    def test_creates_readme_file(self, generator, tmp_bots_dir):
        generator.create_bot("New Bot", register=False)
        readme = os.path.join(tmp_bots_dir, "new_bot", "README.md")
        assert os.path.isfile(readme)

    def test_main_file_contains_class(self, generator, tmp_bots_dir):
        generator.create_bot("New Bot", register=False)
        with open(os.path.join(tmp_bots_dir, "new_bot", "new_bot.py")) as f:
            content = f.read()
        assert "class NewBot" in content

    def test_main_file_has_run_method(self, generator, tmp_bots_dir):
        generator.create_bot("My Scraper Bot", register=False)
        with open(os.path.join(tmp_bots_dir, "my_scraper_bot", "my_scraper_bot.py")) as f:
            content = f.read()
        assert "def run(" in content

    def test_main_file_has_global_ai_sources_flow(self, generator, tmp_bots_dir):
        generator.create_bot("AI Bot", register=False)
        with open(os.path.join(tmp_bots_dir, "ai_bot", "ai_bot.py")) as f:
            content = f.read()
        assert "GlobalAISourcesFlow" in content

    def test_result_dict_has_expected_keys(self, generator):
        result = generator.create_bot("KeyBot", register=False)
        for key in ("bot_name", "module_name", "class_name", "bot_dir", "files", "dry_run", "registered"):
            assert key in result

    def test_module_name_is_snake_case(self, generator):
        result = generator.create_bot("Lead Scraper Bot", register=False)
        assert result["module_name"] == "lead_scraper_bot"

    def test_class_name_is_pascal_case(self, generator):
        result = generator.create_bot("Lead Scraper Bot", register=False)
        assert result["class_name"] == "LeadScraperBot"

    def test_generation_log_updated(self, generator):
        generator.create_bot("Log Bot A", register=False)
        generator.create_bot("Log Bot B", register=False)
        assert len(generator.get_generation_log()) == 2

    def test_summary_counts_correctly(self, generator):
        generator.create_bot("Bot One", register=False)
        generator.create_bot("Bot Two", register=False)
        summary = generator.get_summary()
        assert summary["total_bots_generated"] == 2

    def test_create_bots_bulk(self, generator):
        results = generator.create_bots_bulk(["Alpha Bot", "Beta Bot", "Gamma Bot"], register=False)
        assert len(results) == 3

    def test_custom_template_used(self, generator, tmp_bots_dir):
        custom_tpl = "# custom\nclass {class_name}:\n    pass\n"
        generator.create_bot("Custom Bot", template=custom_tpl, register=False)
        with open(os.path.join(tmp_bots_dir, "custom_bot", "custom_bot.py")) as f:
            content = f.read()
        assert "# custom" in content


# ---------------------------------------------------------------------------
# Registration (with mock controller)
# ---------------------------------------------------------------------------

class _MockController:
    def __init__(self):
        self.registered = {}

    def register_bot(self, name, instance):
        self.registered[name] = instance


class TestGeneratorRegistration:
    def test_set_controller(self, generator):
        ctrl = _MockController()
        generator.set_controller(ctrl)
        assert generator._controller is ctrl

    def test_registered_false_without_controller(self, generator):
        result = generator.create_bot("Lone Bot", register=True)
        assert result["registered"] is False
