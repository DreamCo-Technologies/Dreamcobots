"""
Pytest configuration and shared fixtures for the DreamCobots test suite.
"""

import os
import sys
import pytest

# Ensure tools/ is on sys.path so tests can import check_bot_framework
# directly without relying on a prior test having inserted the path.
_TOOLS_DIR = os.path.join(os.path.dirname(__file__), "..", "tools")
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

# Generic module names that multiple bot directories each provide their own
# version of (e.g. bots/211-resource-eligibility-bot/bot.py vs
# bots/saas-selling-bot/bot.py).  If any of these are imported at module
# collection time they get stashed in sys.modules and then the wrong copy
# is returned when a later test tries to import the same name from a
# different directory.  We clear them before every test so each test gets a
# fresh, path-aware import.
_GENERIC_BOT_MODULES = frozenset({"bot"})


@pytest.fixture(autouse=True)
def _isolate_sys_modules():
    """Snapshot and restore sys.modules and sys.path between tests.

    This prevents sys.modules cache pollution where a test file that inserts
    a bot directory into sys.path (e.g. bots/211-resource-eligibility-bot)
    causes its local tiers.py to be cached as sys.modules['tiers'], breaking
    downstream tests that expect a different tiers module.
    """
    modules_snapshot = dict(sys.modules)
    path_snapshot = list(sys.path)
    # Remove generic single-file module names that are shared across many bot
    # directories so they are always re-imported from the correct sys.path
    # entry at the start of every test.
    for mod in _GENERIC_BOT_MODULES:
        sys.modules.pop(mod, None)
    yield
    for key in list(sys.modules.keys()):
        if key not in modules_snapshot:
            del sys.modules[key]
        elif sys.modules[key] is not modules_snapshot[key]:
            sys.modules[key] = modules_snapshot[key]
    sys.path[:] = path_snapshot
