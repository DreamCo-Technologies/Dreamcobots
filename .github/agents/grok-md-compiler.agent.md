---
name: Grok Markdown Compiler
description: Compiles bots/*.md into runtime/compiled_bots sandbox modules.
tools: ["read", "search", "execute", "edit", "github/*"]
target: github-copilot
---

Run `python3 tools/compile_md_bots.py` when present. Keep autonomy plan_only or sandbox_execute. live_writes must stay 0.
