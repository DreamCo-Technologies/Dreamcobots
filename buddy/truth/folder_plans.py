#!/usr/bin/env python3
"""A realistic next step for every top-level folder. Files stay put."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKIP = {".git", "node_modules", "dist", "logs"}
PLANS = {
    ".agents": ("Agent notes", "Keep these notes out of the site deploy.", "Do not treat an agent note as a running service."),
    ".github": ("Workflow files", "Record one real passing Actions run. A static check is not that run.", "Do not mark 72 unknown workflows as passing."),
    "App_bots": ("Division lists", "Keep each division count equal to the bots named in its file.", "Do not call a list a live bot."),
    "DreamPayments": ("Payment notes and a benchmark", "Leave charges off until a provider is connected by the owner.", "Do not claim revenue from this folder."),
    "attached_assets": ("Imported assets", "Use an asset only where a page already references it.", "Do not add unused copies."),
    "automation-tools": ("Automation notes", "Point any new tool at a workflow that already exists.", "Do not start a second scheduler."),
    "benchmarks": ("Benchmark notes", "Read the scorecard in website/data/benchmarks.json before adding a gate.", "Do not invent a public exam score."),
    "bots": ("1,101 markdown profiles", "Leave production_ready false until a bot has an adapter, a sandbox, sign-in, and telemetry.", "Do not turn a profile into a claim that the bot is live."),
    "buddy": ("Local Buddy code", "Keep the scorecard, the task runner, and the note model on the checks they already pass.", "Do not call this folder a frontier model."),
    "buddy_os": ("Operating-system notes", "Link a note to the website page that implements it, or mark it as a note.", "Do not claim the OS is installed."),
    "capabilities": ("Capability notes", "Add a capability only when a function in buddy/ or website/ performs it.", "Do not list a capability that has no code."),
    "client": ("Browser client files", "Change the client only alongside the website page it feeds.", "Do not start a second public site."),
    "clients": ("Client placeholder", "Leave it until a real client program is specified.", "Do not add an empty app here."),
    "command-center": ("Generated inventory", "Regenerate it after a file is added or removed, then run the check.", "Do not edit the generated counts by hand."),
    "config": ("Catalogs and policies", "A catalog entry is not a connection. Say setup is required until a check passes.", "Do not treat a JSON list as a live integration."),
    "data": ("Small data folder", "Put a new dataset only if its license and source are named.", "Do not host someone else's files here."),
    "docs": ("Written docs", "Update a doc only after the code it describes has changed.", "Do not let a doc overrule the release file."),
    "dreamco_platform": ("Platform sketches", "Promote one sketch into website/ only after it runs.", "Do not describe a sketch as shipped."),
    "evidence": ("Evidence notes", "Add evidence only from a command that was run.", "Do not paste a claim without a command."),
    "foundry": ("Model-building sketches", "Keep weight files and remote code off this site.", "Do not say a plan file trained a model."),
    "framework": ("Framework notes, including a game-engine note", "The playable builder is website/game-builder.html. Point here back to that page.", "Do not start a second engine in this folder."),
    "huggingface": ("Hub sync notes", "Sync only through the existing Action, and only with the owner's token.", "Do not call a sync a trained model."),
    "marketplace": ("One exchange sketch", "Leave selling off until a product page states the price and the limit.", "Do not invent an order."),
    "money": ("Hustle notes", "Keep money actions as plans. Live charges stay off.", "Do not promise income."),
    "money_os": ("Money-system notes", "Same rule as money/. A note is not a payment processor.", "Do not connect a card from this folder."),
    "original-bots": ("Earlier bot notes", "Keep the 212-bot catalog separate from the 1,101 markdown files.", "Do not merge the two counts."),
    "reports": ("Scan reports", "Regenerate a report when its source changes. Date the report.", "Do not quote an old count as current."),
    "schemas": ("Data shapes", "Change a schema only with the reader that uses it.", "Do not add a shape nothing reads."),
    "script": ("One script folder", "Prefer tools/ for a new command.", "Do not add a third script home."),
    "scripts": ("A few scripts", "Prefer tools/ for a new command.", "Do not duplicate a tool that already exists."),
    "server": ("Policy and route files", "A policy file is not a running server. Start it only for a test you can stop.", "Do not claim the server is deployed."),
    "settings": ("Setting notes", "The weight settings page does not load weight files. Keep that true.", "Do not store a secret in this folder."),
    "shared": ("Shared helpers", "Use a helper only if two callers already need it.", "Do not add a helper for one call."),
    "systems": ("System notes", "Point a system note at the folder that implements it.", "Do not add a new top-level system for one page."),
    "team": ("Team placeholder", "Leave it until there is a real roster to store.", "Do not invent members."),
    "tests": ("Tests", "Run npm run test:repository and record the result.", "Do not count an unrun test as passing."),
    "tools": ("Generators and gates", "Run npm run production:readiness:strict and keep the release file honest.", "Do not flip production_ready by hand."),
    "website": ("The public site", "Ship a page only when its button runs. Deploy main to Pages.", "Do not claim the site is the whole product."),
}


def status() -> dict:
    folders = sorted(path.name for path in ROOT.iterdir() if path.is_dir() and path.name not in SKIP)
    missing = [name for name in folders if name not in PLANS]
    extra = [name for name in PLANS if name not in folders]
    if missing or extra:
        raise SystemExit(f"Folder plans drifted. missing={missing} extra={extra}")
    rows = [{"folder": name, "role": PLANS[name][0], "next": PLANS[name][1], "not": PLANS[name][2]} for name in folders]
    return {"files_moved": False, "production_ready": False, "folders": len(rows), "plans": rows}


if __name__ == "__main__":
    made = status()
    assert made["files_moved"] is False and made["folders"] == len(PLANS)
    print(json.dumps({"folders": made["folders"], "files_moved": False}))
