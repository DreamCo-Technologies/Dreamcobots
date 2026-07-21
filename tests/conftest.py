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
    yield
    for key in list(sys.modules.keys()):
        if key not in modules_snapshot:
            del sys.modules[key]
        elif sys.modules[key] is not modules_snapshot[key]:
            sys.modules[key] = modules_snapshot[key]
    sys.path[:] = path_snapshot
