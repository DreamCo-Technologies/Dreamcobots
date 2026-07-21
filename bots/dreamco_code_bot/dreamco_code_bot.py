"""DreamCo Code Bot — cloud code platform for code building and execution."""
import sys
import os
import uuid
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.dreamco_code_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401


class DreamCoCodeBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class DreamCoCodeBotError(Exception):
    """Raised when a code execution operation fails."""


class CodeSession:
    """Represents a persistent code execution session."""

    def __init__(self, session_id: str, language: str, user_id: str = "user"):
        self.session_id = session_id
        self.language = language
        self.user_id = user_id
        self.history: list = []
        self.packages: list = []
        self.created_at = time.time()

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "language": self.language,
            "user_id": self.user_id,
            "history_count": len(self.history),
            "packages": list(self.packages),
            "created_at": self.created_at,
        }


class ExecutionResult:
    """Represents the result of a code execution."""

    def __init__(self, stdout: str, stderr: str, exit_code: int,
                 execution_time_ms: float, language: str):
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.execution_time_ms = execution_time_ms
        self.language = language
        self.success = (exit_code == 0)

    def to_dict(self) -> dict:
        return {
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "execution_time_ms": self.execution_time_ms,
            "language": self.language,
            "success": self.success,
        }


class DreamCoCodeBot:
    """
    DreamCo Code Bot — autonomous code execution platform for DreamCo-owned cloud code execution.

    Provides cloud-based code building, execution, and collaboration with
    multi-language support, persistent sessions, and AI-powered suggestions.

    Tiers
    -----
    FREE       : 2 languages, 100 executions/month, basic sandbox.
    PRO        : 10 languages, 1,000 executions/month, packages, sessions.
    ENTERPRISE : All languages, unlimited executions, CI/CD, containers.
    """

    FREE_LANGUAGES = ["python", "javascript"]
    PRO_LANGUAGES = [
        "python", "javascript", "typescript", "ruby", "go",
        "java", "c", "cpp", "rust", "php",
    ]
    ALL_LANGUAGES = PRO_LANGUAGES + [
        "kotlin", "swift", "scala", "r", "julia",
        "bash", "powershell", "lua", "haskell", "elixir",
    ]

    LANGUAGE_LIMITS = {
        Tier.FREE: FREE_LANGUAGES,
        Tier.PRO: PRO_LANGUAGES,
        Tier.ENTERPRISE: ALL_LANGUAGES,
    }

    EXECUTION_LIMITS = {
        Tier.FREE: 100,
        Tier.PRO: 1000,
        Tier.ENTERPRISE: None,
    }

    # Simulated outputs for demo purposes (mock sandbox)
    _MOCK_OUTPUTS = {
        "python": {"stdout": "Hello from DreamCo Code Bot (Python)\n", "exit_code": 0},
        "javascript": {"stdout": "Hello from DreamCo Code Bot (JavaScript)\n", "exit_code": 0},
        "typescript": {"stdout": "Hello from DreamCo Code Bot (TypeScript)\n", "exit_code": 0},
        "ruby": {"stdout": "Hello from DreamCo Code Bot (Ruby)\n", "exit_code": 0},
        "go": {"stdout": "Hello from DreamCo Code Bot (Go)\n", "exit_code": 0},
        "java": {"stdout": "Hello from DreamCo Code Bot (Java)\n", "exit_code": 0},
        "c": {"stdout": "Hello from DreamCo Code Bot (C)\n", "exit_code": 0},
        "cpp": {"stdout": "Hello from DreamCo Code Bot (C++)\n", "exit_code": 0},
        "rust": {"stdout": "Hello from DreamCo Code Bot (Rust)\n", "exit_code": 0},
        "php": {"stdout": "Hello from DreamCo Code Bot (PHP)\n", "exit_code": 0},
    }

    def __init__(self, tier: Tier = Tier.FREE, user_id: str = "user"):
        self.tier = tier
        self.config = get_tier_config(tier)
        self.user_id = user_id
        self._execution_count: int = 0
        self._sessions: dict = {}
        self._snippets: dict = {}

    # ------------------------------------------------------------------
    # Tier enforcement
    # ------------------------------------------------------------------

    def _require(self, feature: str) -> None:
        if feature not in BOT_FEATURES[self.tier.value]:
            upgrade = get_upgrade_path(self.tier)
            raise DreamCoCodeBotTierError(
                f"Feature '{feature}' is not available on the {self.config.name} tier. "
                f"Upgrade to {upgrade} for access."
            )

    def _check_execution_limit(self) -> None:
        limit = self.EXECUTION_LIMITS[self.tier]
        if limit is not None and self._execution_count >= limit:
            raise DreamCoCodeBotTierError(
                f"Monthly execution limit of {limit} reached on {self.config.name} tier. "
                f"Upgrade to get more executions."
            )

    # ------------------------------------------------------------------
    # Language support
    # ------------------------------------------------------------------

    def list_languages(self) -> list:
        """Return list of supported languages for this tier."""
        return list(self.LANGUAGE_LIMITS[self.tier])

    def supports_language(self, language: str) -> bool:
        """Return True if the given language is supported on this tier."""
        return language.lower() in self.LANGUAGE_LIMITS[self.tier]

    # ------------------------------------------------------------------
    # Code execution
    # ------------------------------------------------------------------

    def execute(self, code: str, language: str,
                stdin: str = "", session_id: str = None) -> ExecutionResult:
        """
        Execute code in the specified language.

        Parameters
        ----------
        code : str
            Source code to execute.
        language : str
            Target language (must be supported on this tier).
        stdin : str
            Optional standard input to supply to the program.
        session_id : str, optional
            Existing session ID for persistent execution context (PRO+).

        Returns
        -------
        ExecutionResult
        """
        language = language.lower()
        if not self.supports_language(language):
            allowed = self.LANGUAGE_LIMITS[self.tier]
            raise DreamCoCodeBotTierError(
                f"Language '{language}' not available on {self.config.name} tier. "
                f"Allowed: {allowed}. Upgrade for more language support."
            )
        self._check_execution_limit()

        start = time.time()
        mock = self._MOCK_OUTPUTS.get(language, {"stdout": f"Executed {language} code.\n", "exit_code": 0})
        execution_time_ms = (time.time() - start) * 1000 + 50  # simulate ~50 ms

        result = ExecutionResult(
            stdout=mock["stdout"],
            stderr="",
            exit_code=mock["exit_code"],
            execution_time_ms=round(execution_time_ms, 2),
            language=language,
        )

        self._execution_count += 1

        if session_id and session_id in self._sessions:
            self._sessions[session_id].history.append({
                "code": code,
                "result": result.to_dict(),
            })

        return result

    # ------------------------------------------------------------------
    # Package management (PRO+)
    # ------------------------------------------------------------------

    def install_package(self, package_name: str, session_id: str = None) -> dict:
        """
        Install a package into the execution environment.
        Requires PRO tier or higher.
        """
        if self.tier == Tier.FREE:
            raise DreamCoCodeBotTierError(
                f"Package installation not available on {self.config.name} tier. "
                f"Upgrade to PRO or ENTERPRISE."
            )
        result = {
            "package": package_name,
            "status": "installed",
            "version": "latest",
            "tier": self.tier.value,
        }
        if session_id and session_id in self._sessions:
            self._sessions[session_id].packages.append(package_name)
        return result

    # ------------------------------------------------------------------
    # Sessions (PRO+)
    # ------------------------------------------------------------------

    def create_session(self, language: str) -> CodeSession:
        """
        Create a persistent code session.
        Requires PRO tier or higher.
        """
        if self.tier == Tier.FREE:
            raise DreamCoCodeBotTierError(
                f"Persistent sessions not available on {self.config.name} tier. "
                f"Upgrade to PRO or ENTERPRISE."
            )
        language = language.lower()
        if not self.supports_language(language):
            raise DreamCoCodeBotError(
                f"Language '{language}' not supported on {self.config.name} tier."
            )
        session = CodeSession(
            session_id=str(uuid.uuid4()),
            language=language,
            user_id=self.user_id,
        )
        self._sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> CodeSession:
        """Return an existing session by ID."""
        if session_id not in self._sessions:
            raise DreamCoCodeBotError(f"Session '{session_id}' not found.")
        return self._sessions[session_id]

    def list_sessions(self) -> list:
        """Return all active sessions."""
        return [s.to_dict() for s in self._sessions.values()]

    # ------------------------------------------------------------------
    # Snippets (PRO+)
    # ------------------------------------------------------------------

    def share_snippet(self, code: str, language: str, title: str = "") -> dict:
        """
        Create a shareable code snippet.
        Requires PRO tier or higher.
        """
        if self.tier == Tier.FREE:
            raise DreamCoCodeBotTierError(
                f"Shareable snippets not available on {self.config.name} tier. "
                f"Upgrade to PRO or ENTERPRISE."
            )
        snippet_id = str(uuid.uuid4())[:8]
        snippet = {
            "snippet_id": snippet_id,
            "title": title or f"Snippet {snippet_id}",
            "language": language,
            "code": code,
            "url": f"https://code.dreamco.ai/s/{snippet_id}",
            "tier": self.tier.value,
        }
        self._snippets[snippet_id] = snippet
        return snippet

    # ------------------------------------------------------------------
    # AI Suggestions (PRO+)
    # ------------------------------------------------------------------

    def get_ai_suggestion(self, code: str, language: str) -> dict:
        """
        Return AI-powered code improvement suggestions.
        Requires PRO tier or higher.
        """
        if self.tier == Tier.FREE:
            raise DreamCoCodeBotTierError(
                f"AI code suggestions not available on {self.config.name} tier. "
                f"Upgrade to PRO or ENTERPRISE."
            )
        return {
            "language": language,
            "suggestions": [
                "Consider adding type hints for better readability.",
                "Extract repeated logic into helper functions.",
                "Use list comprehensions where applicable.",
            ],
            "quality_score": 85,
            "tier": self.tier.value,
        }

    # ------------------------------------------------------------------
    # CI/CD Pipeline (ENTERPRISE)
    # ------------------------------------------------------------------

    def create_pipeline(self, name: str, steps: list) -> dict:
        """
        Create a CI/CD pipeline.
        Requires ENTERPRISE tier.
        """
        if self.tier != Tier.ENTERPRISE:
            raise DreamCoCodeBotTierError(
                f"CI/CD pipelines not available on {self.config.name} tier. "
                f"Upgrade to ENTERPRISE."
            )
        return {
            "pipeline_id": str(uuid.uuid4()),
            "name": name,
            "steps": steps,
            "status": "created",
            "tier": self.tier.value,
        }

    # ------------------------------------------------------------------
    # Tier info
    # ------------------------------------------------------------------

    def get_tier_info(self) -> dict:
        """Return tier configuration and feature details."""
        return get_bot_tier_info(self.tier)

    def get_execution_stats(self) -> dict:
        """Return execution statistics for the current session."""
        limit = self.EXECUTION_LIMITS[self.tier]
        return {
            "executions_used": self._execution_count,
            "executions_limit": limit,
            "executions_remaining": (limit - self._execution_count) if limit is not None else None,
            "sessions_active": len(self._sessions),
            "snippets_shared": len(self._snippets),
            "tier": self.tier.value,
        }

    # ------------------------------------------------------------------
    # Chat interface
    # ------------------------------------------------------------------

    def chat(self, message: str) -> dict:
        """
        Unified natural-language chat interface.

        Interprets common intents and dispatches to the appropriate method.
        """
        msg = message.lower()

        if any(kw in msg for kw in ("languages", "what languages", "supported")):
            langs = self.list_languages()
            return {"message": f"Supported languages: {', '.join(langs)}", "data": langs}

        if any(kw in msg for kw in ("execute", "run", "build")):
            lang = "python"
            for candidate in self.list_languages():
                if candidate in msg:
                    lang = candidate
                    break
            result = self.execute("# demo code", lang)
            return {
                "message": f"Code executed in {lang}. Output: {result.stdout.strip()}",
                "data": result.to_dict(),
            }

        if "install" in msg and "package" in msg:
            if self.tier == Tier.FREE:
                return {
                    "message": "Package installation requires PRO tier. Upgrade to unlock.",
                    "data": {"upgrade_required": True},
                }
            pkg = "example-package"
            result = self.install_package(pkg)
            return {"message": f"Package '{pkg}' installed.", "data": result}

        if any(kw in msg for kw in ("stats", "usage", "executions")):
            stats = self.get_execution_stats()
            return {"message": "Execution statistics retrieved.", "data": stats}

        if "tier" in msg or "features" in msg or "upgrade" in msg:
            info = self.get_tier_info()
            return {"message": f"Current tier: {info['tier']}. Features: {info['features']}", "data": info}

        return {
            "message": (
                "DreamCo Code Bot ready. I can execute code, manage sessions, "
                "install packages (PRO+), and run CI/CD pipelines (ENTERPRISE). "
                "What would you like to build today?"
            ),
            "data": {"tier": self.tier.value},
        }
