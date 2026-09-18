---
name: Grok Legacy Placer
description: Places original-bots into current App_bots divisions without duplicating the 1051 baseline.
tools: ["read", "search", "execute", "edit", "github/*"]
target: github-copilot
---

Run `python3 tools/place_original_bots.py` when present. Merge overlaps. Do not delete historical files.
