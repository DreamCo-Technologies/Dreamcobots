#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLIENT = ROOT / "client" / "src"

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

LUCIDE_IMPORT_RE = re.compile(r'import\s*\{(?P<body>.*?)\}\s*from\s*["\']lucide-react["\'];?', re.DOTALL)
LOCAL_GITHUB_IMPORT = 'import { Github } from "@/lib/lucide-react-compat";'


def migrate_github_icon_imports() -> list[str]:
    changed: list[str] = []
    for path in sorted(CLIENT.rglob("*.tsx")):
        text = path.read_text(encoding="utf-8")
        original = text

        def replace(match: re.Match[str]) -> str:
            body = match.group("body")
            names = [item.strip() for item in body.replace("\n", " ").split(",") if item.strip()]
            if "Github" not in names:
                return match.group(0)
            names = [name for name in names if name != "Github"]
            if not names:
                return ""
            if "\n" in body:
                rendered = "\n  " + ",\n  ".join(names) + ",\n"
            else:
                rendered = " " + ", ".join(names) + " "
            return f'import {{{rendered}}} from "lucide-react";'

        text = LUCIDE_IMPORT_RE.sub(replace, text)
        if text != original and LOCAL_GITHUB_IMPORT not in text:
            lines = text.splitlines()
            insert_at = 0
            while insert_at < len(lines) and lines[insert_at].startswith("import "):
                insert_at += 1
            lines.insert(insert_at, LOCAL_GITHUB_IMPORT)
            text = "\n".join(lines) + ("\n" if original.endswith("\n") else "")

        if text != original:
            path.write_text(text, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))
    return changed


def main() -> int:
    changed = []
    already_current = []
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
