import importlib

from dreamco_import_paths import configure_import_paths


def test_legacy_local_modules_are_importable():
    configure_import_paths()

    modules = [
        "tiers",
        "government_contract_grant_bot",
        "hustle_bot",
        "referral_bot",
        "resume_parser",
        "ai_integration",
        "bot_manager",
        "repo_manager",
        "auto_upgrader",
        "algorithmic_trading_bot",
        "color_palette_generator",
        "recipe_scaling_tool",
        "workplace_audit_tool",
    ]

    for module_name in modules:
        assert importlib.import_module(module_name)

