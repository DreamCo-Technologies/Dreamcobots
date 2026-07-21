"""
DreamCo API — Bot Upload Endpoint

Provides a REST API for clients to submit their bot files to the DreamCo OS
platform.  Uploaded files are validated and sandbox-tested before being
registered.

Usage
-----
    python api/upload_api.py        # starts on port 5000

Endpoints
---------
POST /upload_bot
    Upload a ``.py`` bot file.  Returns JSON with ``status`` and metadata.

GET /bots
    List all registered bots.
"""

from __future__ import annotations

import os
import sys

# Ensure repo root is on sys.path so core/* imports resolve correctly
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

try:
    from flask import Flask, jsonify, request  # type: ignore[import]
    from werkzeug.utils import secure_filename  # type: ignore[import]
    _FLASK_AVAILABLE = True
except ImportError:
    _FLASK_AVAILABLE = False

from core.bot_lab import BotLab
from core.bot_registry import get_registered_bots, register_bot

if _FLASK_AVAILABLE:
    app = Flask(__name__)
else:
    app = None  # type: ignore[assignment]
UPLOAD_FOLDER = os.path.join(_REPO_ROOT, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

_lab = BotLab()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


def _make_routes(flask_app: Any) -> None:  # type: ignore[name-defined]
    """Register routes on *flask_app*."""

    @flask_app.route("/upload_bot", methods=["POST"])
    def upload_bot():
        """
        Upload a bot ``.py`` file for validation and sandbox testing.

        Expects a multipart form-data request with a ``file`` field.

        Returns JSON::

            {
                "status": "approved" | "rejected" | "failed",
                "path": "<saved path>",
                ...
            }
        """
        if "file" not in request.files:
            return jsonify({"error": "No file field in request"}), 400

        uploaded = request.files["file"]
        raw_filename = uploaded.filename or "unknown_bot.py"
        filename = secure_filename(raw_filename)

        if not filename:
            return jsonify({"error": "Invalid filename"}), 400

        # Reject non-Python files early
        if not filename.endswith(".py"):
            return jsonify({"error": "Only .py files are accepted"}), 400

        # Resolve and validate the save path is within UPLOAD_FOLDER
        upload_root = os.path.realpath(UPLOAD_FOLDER)
        save_path = os.path.realpath(os.path.join(UPLOAD_FOLDER, filename))
        if os.path.commonpath([save_path, upload_root]) != upload_root:
            return jsonify({"error": "Invalid file path"}), 400

        uploaded.save(save_path)

        result = _lab.process_upload(save_path)

        if result["status"] == "approved":
            register_bot({"name": filename, "path": save_path, "type": "client_bot", "status": "approved"})

        return jsonify({"path": save_path, **result})

    @flask_app.route("/bots", methods=["GET"])
    def list_bots():
        """Return all registered bots as JSON."""
        return jsonify(get_registered_bots())


if _FLASK_AVAILABLE and app is not None:
    _make_routes(app)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5000)
