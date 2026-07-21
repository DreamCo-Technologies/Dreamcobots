"""
LibraryManager - Dynamic library fetching and testing for Buddy.

Enables Buddy's self-learning by downloading, testing, and loading
new Python packages at runtime when it encounters unmet capabilities.
"""

import importlib
import importlib.util
import logging
import subprocess
import sys
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class LibraryInstallError(RuntimeError):
    """Raised when a library cannot be installed."""


class LibraryTestError(RuntimeError):
    """Raised when an installed library fails its smoke-test."""


class LibraryManager:
    """Manages dynamic Python library acquisition and loading.

    Example usage::

        lm = LibraryManager()
        if not lm.is_available("schedule"):
            lm.install_library("schedule")
        mod = lm.load_library("schedule")
    """

    # Packages that must never be installed at runtime for security reasons.
    _BLOCKED_PACKAGES: frozenset = frozenset(
        {"os", "sys", "subprocess", "socket", "ctypes", "builtins"}
    )

    def __init__(self) -> None:
        self._cache: Dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_available(self, package: str) -> bool:
        """Return ``True`` if *package* is importable in the current environment.

        Args:
            package: Import name (e.g. ``"requests"``).
        """
        return importlib.util.find_spec(package) is not None

    def install_library(self, package: str) -> None:
        """Install *package* using pip.

        Args:
            package: PyPI package name (e.g. ``"schedule"``).

        Raises:
            ValueError: If *package* is on the blocked list.
            LibraryInstallError: If pip reports a non-zero exit code.
        """
        self._validate_package_name(package)
        logger.info("Installing package '%s'...", package)
        result = subprocess.run(  # noqa: S603
            [sys.executable, "-m", "pip", "install", package, "--quiet"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise LibraryInstallError(
                f"Failed to install '{package}': {result.stderr.strip()}"
            )
        logger.info("Package '%s' installed successfully.", package)

    def test_library(self, package: str) -> bool:
        """Smoke-test *package* by attempting to import it.

        Args:
            package: Import name of the installed package.

        Returns:
            ``True`` if the import succeeds, ``False`` otherwise.
        """
        try:
            importlib.import_module(package)
            logger.info("Smoke-test passed for '%s'.", package)
            return True
        except ImportError as exc:
            logger.warning("Smoke-test failed for '%s': %s", package, exc)
            return False

    def load_library(self, package: str) -> Any:
        """Import and return the module for *package*.

        The module is cached after the first import so subsequent calls
        are essentially free.

        Args:
            package: Import name of the package.

        Returns:
            The imported module object.

        Raises:
            LibraryInstallError: If the package is not available and
                auto-installation fails.
            LibraryTestError: If the package is installed but fails its
                smoke-test.
        """
        if package in self._cache:
            return self._cache[package]

        if not self.is_available(package):
            logger.info(
                "Package '%s' not found locally; attempting auto-install.", package
            )
            self.install_library(package)

        if not self.test_library(package):
            raise LibraryTestError(
                f"Package '{package}' was installed but failed smoke-test."
            )

        module = importlib.import_module(package)
        self._cache[package] = module
        return module

    def ensure_library(self, package: str) -> Any:
        """Convenience method: ensure *package* is available and return it.

        Combines :meth:`install_library` (if needed) and :meth:`load_library`.
        """
        return self.load_library(package)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _validate_package_name(self, package: str) -> None:
        """Raise :class:`ValueError` if *package* is blocked or looks unsafe."""
        if package in self._BLOCKED_PACKAGES:
            raise ValueError(
                f"Package '{package}' is on the blocked list and cannot be installed."
            )
        # Only allow alphanumeric characters, hyphens, underscores, and dots
        import re  # local import to keep module load fast

        if not re.fullmatch(r"[A-Za-z0-9_.\-]+", package):
            raise ValueError(
                f"Package name '{package}' contains disallowed characters."
            )
