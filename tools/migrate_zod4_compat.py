#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REPLACEMENTS = {
    "server/fleet-runtime.ts": [
        ("z.record(z.unknown())", "z.record(z.string(), z.unknown())"),
        (
            "} from \"./buddy-model-policy\";\n",
            "} from \"./buddy-model-policy\";\nimport { selectBestModelForTask } from \"./model-intelligence-router\";\n",
        ),
        (
            "    const preferred = request.preferredBotSlug ? this.runtimes.get(request.preferredBotSlug) : undefined;",
            "    const modelIntelligencePlan = selectBestModelForTask({\n      objective: request.objective,\n      requiredCapabilities: request.requestedCapabilities,\n      allowPaid: request.modelMode === \"premium\" && request.approvePaidModelForThisRequest,\n      qualityPriority: 1,\n      costPriority: 0.25,\n      latencyPriority: 0.25,\n      privacyPriority: 0.35,\n    });\n    const preferred = request.preferredBotSlug ? this.runtimes.get(request.preferredBotSlug) : undefined;",
        ),
        (
            "      modelPlan,\n      execution,",
            "      modelPlan,\n      modelIntelligencePlan,\n      execution,",
        ),
    ],
    "server/media-quality-lab.ts": [
        ("z.record(z.number().min(0).max(1))", "z.record(z.string(), z.number().min(0).max(1))"),
        ("z.record(z.boolean())", "z.record(z.string(), z.boolean())"),
        (
            "const scorecard = catalog.scorecards[modality];",
            "const scorecard = catalog.scorecards[modality] as { dimensions: Record<string, number>; release_threshold: number };",
        ),
    ],
    "server/routes.ts": [
        ("err.errors[0]?.message", "err.issues[0]?.message"),
        ("err.errors[0]?.path", "err.issues[0]?.path"),
    ],
    "server/communication-behavior.ts": [
        (
            "const traitIds = new Set(traitDefinitions.map((trait) => trait.id));",
            "const traitIds = new Set([...traitDefinitions.map((trait) => trait.id), \"clarity\"]);",
        ),
    ],
    "tools/generate_buddy_fleet_quality_program.ts": [
        (
            "  const qualityWorkerRoutes = source.quality_workers.map((worker) => ({\n    requested_slug: worker.slug,\n    resolved_slug: fleetSlugs.has(worker.slug) ? worker.slug : globalMasterSlug,",
            "  const qualityWorkerRoutes = source.quality_workers.map((worker) => ({\n    slug: fleetSlugs.has(worker.slug) ? worker.slug : globalMasterSlug,\n    requested_slug: worker.slug,\n    resolved_slug: fleetSlugs.has(worker.slug) ? worker.slug : globalMasterSlug,",
        ),
    ],
}

# Keep this migration intentionally bounded. GitHub code search on 2026-08-11
# found these DreamCo TSX files importing the removed Lucide Github brand icon.
GITHUB_ICON_FILES = (
    "client/src/components/AppShell.tsx",
    "client/src/pages/ActionsPage.tsx",
    "client/src/pages/BotActivityPage.tsx",
    "client/src/pages/BotBuilderPage.tsx",
    "client/src/pages/BuddyPage.tsx",
    "client/src/pages/ConnectionsPage.tsx",
    "client/src/pages/ConversationPage.tsx",
    "client/src/pages/DreamCodeLabPage.tsx",
    "client/src/pages/LearningMatrixPage.tsx",
    "client/src/pages/SandboxPage.tsx",
    "client/src/pages/SettingsPage.tsx",
)

# The old regex used .*? with DOTALL, which could start at an earlier import and
# consume several unrelated import statements before reaching lucide-react.
# Restricting the body to characters before the first closing brace keeps the
# rewrite inside one named-import declaration.
LUCIDE_IMPORT_RE = re.compile(
    r'import\s*\{(?P<body>[^}]*)\}\s*from\s*["\']lucide-react["\'];?'
)
LOCAL_GITHUB_IMPORT = 'import { Github } from "@/lib/lucide-react-compat";'


def rewrite_github_icon_imports(text: str) -> str:
    changed = False

    def replace(match: re.Match[str]) -> str:
        nonlocal changed
        body = match.group("body")
        names = [item.strip() for item in body.replace("\n", " ").split(",") if item.strip()]
        if "Github" not in names:
            return match.group(0)
        changed = True
        names = [name for name in names if name != "Github"]
        if not names:
            return ""
        if "\n" in body:
            rendered = "\n  " + ",\n  ".join(names) + ",\n"
        else:
            rendered = " " + ", ".join(names) + " "
        return f'import {{{rendered}}} from "lucide-react";'

    updated = LUCIDE_IMPORT_RE.sub(replace, text)
    if changed and LOCAL_GITHUB_IMPORT not in updated:
        # Prepending is deliberately safer than searching for the end of an
        # import block: multi-line imports do not have every line prefixed by
        # the word "import".
        updated = f"{LOCAL_GITHUB_IMPORT}\n{updated}"
    return updated


def migrate_github_icon_imports() -> list[str]:
    changed: list[str] = []
    for rel in GITHUB_ICON_FILES:
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        updated = rewrite_github_icon_imports(text)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed.append(rel)
    return changed


def main() -> int:
    changed: list[str] = []
    already_current: list[str] = []
    for rel, replacements in REPLACEMENTS.items():
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        original = text
        for old, new in replacements:
            if new in text:
                continue
            if old in text:
                text = text.replace(old, new)
                continue
            raise SystemExit(f"Neither legacy nor migrated pattern found in {rel}: {old}")
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed.append(rel)
        else:
            already_current.append(rel)

    changed.extend(migrate_github_icon_imports())
    print({"ok": True, "changed": sorted(set(changed)), "already_current": already_current})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
