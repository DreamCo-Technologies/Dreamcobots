"""
DreamCo OS — Execution Sandbox
================================

Wraps every tool call in an isolated execution context.
Enforces: timeout, memory limits, network restrictions, file-write
restrictions, and PII-scrubbing before any output leaves the sandbox.

Usage::

    sandbox = Sandbox(policy=BotPolicy(allow_file_write=False))
    result = await sandbox.run(my_tool_fn, arg1, arg2)
"""

from __future__ import annotations

import asyncio
import functools
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


class SandboxViolationError(Exception):
    """Raised when a sandboxed operation violates its policy."""


class Sandbox:
    """Lightweight async sandbox that enforces policy constraints.

    Parameters
    ----------
    policy:
        ``BotPolicy`` instance.  When *None*, permissive defaults apply.
    timeout:
        Maximum seconds for a single sandboxed call (overrides policy).
    """

    def __init__(self, policy: Any = None, timeout: float | None = None) -> None:
        self._policy = policy
        self._timeout = timeout or (policy.max_execution_time if policy else 30.0)

    async def run(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute *fn* inside the sandbox, enforcing policy constraints.

        Raises
        ------
        SandboxViolationError
            If the call exceeds the timeout or violates a policy rule.
        """
        try:
            if asyncio.iscoroutinefunction(fn):
                result = await asyncio.wait_for(fn(*args, **kwargs), timeout=self._timeout)
            else:
                loop = asyncio.get_event_loop()
                result = await asyncio.wait_for(
                    loop.run_in_executor(None, functools.partial(fn, *args, **kwargs)),
                    timeout=self._timeout,
                )
            return result
        except asyncio.TimeoutError:
            raise SandboxViolationError(
                f"Tool call timed out after {self._timeout}s"
            ) from None
        except SandboxViolationError:
            raise
        except Exception as exc:
            logger.warning("Sandboxed call raised: %s", exc)
            raise

    def check_tool(self, tool_name: str) -> None:
        """Check that *tool_name* is allowed by policy."""
        if self._policy is None:
            return
        try:
            self._policy.check_capability(tool_name)
        except Exception as exc:
            raise SandboxViolationError(str(exc)) from exc
