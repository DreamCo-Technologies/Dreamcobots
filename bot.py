"""
DreamCo Bot — main bot entry point.

Defines the Flask ``app`` instance used by the DreamCo platform and exposes a
minimal health-check endpoint so CI can verify the bot is running.

Usage
-----
    python bot.py          # starts on port 5000 (development)
    gunicorn bot:app       # production WSGI
"""

from __future__ import annotations

try:
    from flask import Flask  # type: ignore[import]

    _FLASK_AVAILABLE = True
except ImportError:  # pragma: no cover
    _FLASK_AVAILABLE = False

if _FLASK_AVAILABLE:
    app = Flask(__name__)

    @app.route("/")
    def home() -> str:
        """Root health check — confirms DreamCo Bot is running."""
        return "DreamCo Bot Running"

    @app.route("/health")
    def health():
        """Structured health check used by CI/CD probes."""
        from flask import Response, jsonify  # type: ignore[import]

        response: Response = jsonify({"status": "ok", "service": "dreamco-bot"})
        return response

else:  # pragma: no cover
    # Flask is not installed — define a minimal stub so that imports never fail
    class _FakeApp:  # type: ignore[no-redef]
        """Minimal stub that satisfies ``bot.app`` attribute checks when Flask is absent."""

        name = "dreamco-bot"

        def route(self, *args, **kwargs):
            def decorator(f):
                return f

            return decorator

        def run(self, *args, **kwargs):
            pass

    app = _FakeApp()  # type: ignore[assignment]


if __name__ == "__main__":
    if _FLASK_AVAILABLE:
        app.run(host="0.0.0.0", port=5000, debug=False)
    else:
        print("Flask is not installed. Install it with: pip install flask")
