"""Tests for LibraryManager."""

import pytest
from BuddyAI.library_manager import LibraryManager, LibraryInstallError


@pytest.fixture
def manager():
    return LibraryManager()


def test_is_available_stdlib(manager):
    # 'os' is always available
    assert manager.is_available("os") is True


def test_is_available_nonexistent(manager):
    assert manager.is_available("_nonexistent_pkg_xyz_123") is False


def test_load_library_stdlib(manager):
    mod = manager.load_library("os")
    import os
    assert mod is os


def test_load_library_cached(manager):
    mod1 = manager.load_library("os")
    mod2 = manager.load_library("os")
    assert mod1 is mod2


def test_test_library_valid(manager):
    assert manager.test_library("os") is True


def test_test_library_nonexistent(manager):
    assert manager.test_library("_nonexistent_pkg_xyz") is False


def test_validate_blocked_package(manager):
    with pytest.raises(ValueError, match="blocked"):
        manager.install_library("os")


def test_validate_disallowed_characters(manager):
    with pytest.raises(ValueError, match="disallowed"):
        manager.install_library("rm -rf /")


def test_ensure_library_stdlib(manager):
    import json
    mod = manager.ensure_library("json")
    assert mod is json
