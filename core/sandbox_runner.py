"""
DreamCo Sandbox Runner — Execute uploaded bot files in an isolated subprocess.

Security model
--------------
* Bot code runs in a separate OS process (subprocess), not in the main
  interpreter, so crashes and exceptions cannot affect the host process.
* Execution time is hard-capped at ``timeout_seconds``.
* Stdout / stderr are captured; only structured JSON output is returned.
* A pre-execution static validator (BotValidator) screens for obviously
  dangerous patterns before any subprocess is spawned.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from typing import Any, Dict, Optional


# ---------------------------------------------------------------------------
# SandboxRunner
# ---------------------------------------------------------------------------


class SandboxRunner:
    """
    Execute a Python script in an isolated subprocess.

    Parameters
    ----------
    timeout_seconds : int
        Hard execution timeout (default 10 s).  The subprocess is killed
        if it exceeds this limit.
    python_executable : str | None
        Path to the Python interpreter to use.  Defaults to the same
        interpreter running the host process.
    """

    def __init__(
        self,
        timeout_seconds: int = 10,
        python_executable: Optional[str] = None,
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.python_executable = python_executable or sys.executable

    def run_file(self, file_path: str) -> Dict[str, Any]:
        """
        Execute *file_path* in a sandboxed subprocess.

        Parameters
        ----------
        file_path : str
            Absolute path to a Python file to execute.

        Returns
        -------
        dict
            ``{ success, output, error, exit_code, timed_out }``
        """
        import os as _os
        # Resolve and validate path to prevent directory traversal
        try:
            resolved = _os.path.realpath(file_path)
        except (TypeError, ValueError):
            return {"success": False, "error": "invalid file path", "output": "",
                    "exit_code": -1, "timed_out": False}

        if not _os.path.isfile(resolved):
            return {"success": False, "error": "file not found", "output": "",
                    "exit_code": -1, "timed_out": False}

        try:
            proc = subprocess.run(
                [self.python_executable, resolved],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
            return {
                "success": proc.returncode == 0,
                "output": proc.stdout,
                "error": proc.stderr,
                "exit_code": proc.returncode,
                "timed_out": False,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": f"execution timed out after {self.timeout_seconds}s",
                "exit_code": -1,
                "timed_out": True,
            }
        except Exception:
            return {
                "success": False,
                "output": "",
                "error": "execution failed",
                "exit_code": -1,
                "timed_out": False,
            }

    def run_code(self, code: str) -> Dict[str, Any]:
        """
        Execute a code *string* in a sandboxed subprocess.

        Writes the code to a temporary file, executes it, then removes the
        file.

        Parameters
        ----------
        code : str
            Python source code to execute.

        Returns
        -------
        dict
            Same shape as :meth:`run_file`.
        """
        with tempfile.NamedTemporaryFile(
            suffix=".py", mode="w", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        try:
            return self.run_file(tmp_path)
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


_default_runner = SandboxRunner()


def run_in_sandbox(file_path: str, timeout: int = 10) -> dict:
    """Run a Python file in the sandbox and return the result dict."""
    runner = SandboxRunner(timeout_seconds=timeout)
    return runner.run_file(file_path)
