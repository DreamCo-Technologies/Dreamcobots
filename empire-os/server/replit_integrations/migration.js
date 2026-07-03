import fs from "node:fs/promises";
import path from "node:path";
import { DIVISIONS } from "@shared/schema";
const DIVISION_SET = new Set(DIVISIONS);
function toSlug(value) {
    return value
        .toLowerCase()
        .trim()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/(^-|-$)/g, "");
}
async function collectManifestEntries(dir, rootDir) {
    const children = await fs.readdir(dir, { withFileTypes: true });
    const nestedEntries = await Promise.all(children.map(async (child) => {
        const fullPath = path.join(dir, child.name);
        if (child.isDirectory())
            return collectManifestEntries(fullPath, rootDir);
        if (!child.isFile() || child.name !== "replit_profile.json")
            return [];
        try {
            const raw = await fs.readFile(fullPath, "utf-8");
            const parsed = JSON.parse(raw);
            const slug = typeof parsed.slug === "string" && parsed.slug.trim() ? parsed.slug : toSlug(String(parsed.displayName ?? child.name));
            const division = typeof parsed.division === "string" ? parsed.division : "CommandCore";
            return [{
                    slug,
                    division,
                    source: "replit_profile",
                    filePath: path.relative(rootDir, fullPath),
                }];
        }
        catch {
            return [];
        }
    }));
    return nestedEntries.flat();
}
export async function buildReplitMigrationManifest(repositoryRoot, expectedTotal = 1200) {
    const botsDir = path.join(repositoryRoot, "bots");
    const entries = await collectManifestEntries(botsDir, repositoryRoot);
    entries.sort((a, b) => a.slug.localeCompare(b.slug));
    return {
        generatedAt: new Date().toISOString(),
        expectedTotal,
        discoveredAssets: entries.length,
        entries,
    };
}
function normalizeProfile(profile) {
    const slugSource = typeof profile.slug === "string" ? profile.slug : typeof profile.displayName === "string" ? profile.displayName : "";
    const slug = toSlug(slugSource);
    if (!slug)
        return null;
    const displayName = typeof profile.displayName === "string" && profile.displayName.trim() ? profile.displayName : slug;
    const division = typeof profile.division === "string" && DIVISION_SET.has(profile.division) ? profile.division : "CommandCore";
    const category = typeof profile.category === "string" ? profile.category : "general";
    const tier = typeof profile.tier === "string" ? profile.tier : "free";
    const description = typeof profile.description === "string" ? profile.description : `${displayName} imported from Replit`;
    const capabilities = Array.isArray(profile.capabilities) ? profile.capabilities.filter((x) => typeof x === "string") : [];
    return {
        slug,
        displayName,
        division,
        category,
        tier,
        description,
        capabilities,
        revenueModel: typeof profile.revenueModel === "string" ? profile.revenueModel : "Replit migration",
        targetUsers: typeof profile.targetUsers === "string" ? profile.targetUsers : "DreamCo operators",
        status: typeof profile.status === "string" ? profile.status : "active",
        priceRange: typeof profile.priceRange === "string" ? profile.priceRange : "",
        systemPrompt: `You are ${displayName}, imported from Replit into DreamCo Empire OS ${division}. Execute tasks safely and escalate high-risk decisions.`,
        traits: {
            source: "replit_migration",
            version: typeof profile.version === "string" ? profile.version : "1.0",
            importedAt: new Date().toISOString(),
        },
        isDefault: false,
        autonomyLevel: "guided",
        operationalMode: "sandbox",
    };
}
export async function ingestReplitManifest(repositoryRoot, storage, expectedTotal = 1200) {
    const manifest = await buildReplitMigrationManifest(repositoryRoot, expectedTotal);
    const existing = new Set((await storage.listBotProfiles()).map((b) => b.slug));
    const processed = [];
    let imported = 0;
    let deduped = 0;
    let failed = 0;
    let unmapped = 0;
    for (const entry of manifest.entries) {
        const absolutePath = path.join(repositoryRoot, entry.filePath);
        try {
            const raw = await fs.readFile(absolutePath, "utf-8");
            const parsed = JSON.parse(raw);
            const normalized = normalizeProfile(parsed);
            if (!normalized) {
                processed.push({ slug: entry.slug, outcome: "unmapped", reason: "missing_slug_or_name" });
                unmapped += 1;
                continue;
            }
            if (existing.has(normalized.slug)) {
                processed.push({ slug: normalized.slug, outcome: "deduped" });
                deduped += 1;
                continue;
            }
            await storage.createBotProfile(normalized);
            existing.add(normalized.slug);
            processed.push({ slug: normalized.slug, outcome: "imported" });
            imported += 1;
        }
        catch (error) {
            processed.push({ slug: entry.slug, outcome: "failed", reason: error?.message ?? "unknown_error" });
            failed += 1;
        }
    }
    const accounted = imported + deduped + failed + unmapped;
    const unaccounted = Math.max(0, expectedTotal - accounted);
    return {
        processed,
        report: {
            expectedTotal,
            discoveredAssets: manifest.discoveredAssets,
            imported,
            deduped,
            failed,
            unmapped,
            unaccounted,
            complete: unaccounted === 0,
        },
    };
}
