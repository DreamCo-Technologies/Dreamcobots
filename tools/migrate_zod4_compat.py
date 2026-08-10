#!/usr/bin/env python3
from __future__ import annotations

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
    print({"ok": True, "changed": changed, "already_current": already_current})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
