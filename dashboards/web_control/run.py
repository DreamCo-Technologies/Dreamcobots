"""Entry point for the DreamCo Web Control Dashboard.

Adds the repository root to sys.path so that ``ui.web_dashboard``
and its dependencies can be imported, then starts the Flask server.
"""

from __future__ import annotations

import os
import sys

# Ensure the repo root is on the path so imports resolve correctly.
_repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from ui.web_dashboard import create_app  # noqa: E402

app = create_app()

if __name__ == "__main__":  # pragma: no cover
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=False)
