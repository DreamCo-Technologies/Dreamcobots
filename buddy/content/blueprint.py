#!/usr/bin/env python3
"""Where a clone would be trained. The live site does not train one."""
from __future__ import annotations

import json


def plan() -> dict:
    return {
        "live_site": "https://dreamco-technologies.github.io/Dreamcobots/clone-blueprint.html",
        "pages_trains": False,
        "samples_uploaded": False,
        "training_runs_on": "the user's own machine",
        "a18_8gb_can_train": False,
        "minimum_memory_gb": 16,
        "production_ready": False,
        "downloaded_model": False,
        "steps": [
            "Use the live site to write scripts and to record an adult's permission. Do not upload recordings or photos.",
            "On your own computer, put only files you are allowed to use in buddy/content/samples. That folder is not committed.",
            "Add consent.txt with the owner's name and the word allow. Do not include a child.",
            "Another adult can play the original file only after the owner writes that permission. Playback is not training.",
            "Run python3 buddy/content/train_clone.py on that same computer. It refuses while samples, consent, or memory are missing.",
            "An A18 with 8GB cannot train a voice or image clone. Use a machine with at least 16GB before a later training run is even considered.",
            "Do not download a model that can copy a stranger from a short clip. No such model is part of this site.",
        ],
    }


if __name__ == "__main__":
    made = plan()
    assert made["pages_trains"] is False and made["a18_8gb_can_train"] is False and made["production_ready"] is False
    assert made["minimum_memory_gb"] >= 16 and len(made["steps"]) == 7
    print(json.dumps({"pages_trains": False, "steps": len(made["steps"]), "minimum_memory_gb": made["minimum_memory_gb"]}))
