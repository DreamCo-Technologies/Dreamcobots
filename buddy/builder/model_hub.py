"""Model hub choices. A download happens only after approval.

This list is a set of sections and search links. It is not every weight on
the planet, and it does not claim a frontier contest win.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SECTIONS = {
    "frontier": "https://huggingface.co/models?pipeline_tag=text-generation&sort=trending",
    "open-source": "https://huggingface.co/models?license=license:apache-2.0&sort=trending",
    "open-weight": "https://huggingface.co/models?pipeline_tag=text-generation&sort=downloads",
}


def approve(section: str, approved: bool) -> dict:
    if section not in SECTIONS:
        raise ValueError(f"unknown section: {section}")
    return {"section": section, "approved": approved, "weights_downloaded": False, "frontier_claim": False}


def main() -> int:
    report = {"sections": [{"name": name, "search": url, "weights_downloaded": False} for name, url in SECTIONS.items()], "all_weights_hosted": False, "frontier_claim": False}
    (ROOT / "reports" / "MODEL_HUB.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    blocks = []
    for name, url in SECTIONS.items():
        blocks.append(f'<section class="actions-review"><h2>{name}</h2><p><a class="btn btn-outline" href="{url}">Browse {name} models</a> <button class="btn btn-primary" type="button" data-approve="{name}">Approve a download</button></p><p>Approval records the choice. It does not download a file.</p></section>')
    html = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Model hub | Buddy</title><link rel="stylesheet" href="styles.css?v=41"><link rel="stylesheet" href="actions.css?v=4"></head>
<body><div id="nav-placeholder"></div><script src="nav.js"></script><main class="actions-shell">
<header class="actions-header"><div><p class="actions-kicker">Models</p><h1>Frontier, open source, and open weight</h1><p>These are search links. Buddy does not host every weight.</p></div><p><a class="btn btn-primary" href="self-training.html">Self-training</a></p></header>
{''.join(blocks)}
<p id="hub-status">No download approved.</p>
</main>
<script>
document.querySelectorAll("[data-approve]").forEach((button) => button.addEventListener("click", () => {{ localStorage.setItem("dreamco.weight-download", button.dataset.approve); document.getElementById("hub-status").textContent = button.dataset.approve + " download approved. No file downloaded."; }}));
</script>
</body></html>
'''
    (ROOT / "website" / "model-hub.html").write_text(html)
    print(json.dumps({"sections": len(SECTIONS), "all_weights_hosted": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
