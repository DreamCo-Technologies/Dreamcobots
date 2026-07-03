import assert from "node:assert/strict";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { buildReplitMigrationManifest, ingestReplitManifest } from "./migration";

test("buildReplitMigrationManifest discovers Replit assets", async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "replit-manifest-"));
  await fs.mkdir(path.join(root, "bots", "bot-a"), { recursive: true });
  await fs.writeFile(
    path.join(root, "bots", "bot-a", "replit_profile.json"),
    JSON.stringify({ slug: "bot-a", displayName: "Bot A", division: "CommandCore" }),
    "utf-8",
  );
  const manifest = await buildReplitMigrationManifest(root, 5);
  assert.equal(manifest.discoveredAssets, 1);
  assert.equal(manifest.expectedTotal, 5);
  assert.equal(manifest.entries[0]?.slug, "bot-a");
});

test("ingestReplitManifest reports unaccounted records under 1200 target", async () => {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "replit-ingest-"));
  await fs.mkdir(path.join(root, "bots", "bot-a"), { recursive: true });
  await fs.mkdir(path.join(root, "bots", "bot-b"), { recursive: true });
  await fs.writeFile(
    path.join(root, "bots", "bot-a", "replit_profile.json"),
    JSON.stringify({ slug: "bot-a", displayName: "Bot A", division: "CommandCore" }),
    "utf-8",
  );
  await fs.writeFile(
    path.join(root, "bots", "bot-b", "replit_profile.json"),
    JSON.stringify({ slug: "bot-b", displayName: "Bot B", division: "DreamFinance" }),
    "utf-8",
  );

  const created: string[] = [];
  const result = await ingestReplitManifest(
    root,
    {
      async listBotProfiles() {
        return [{ slug: "bot-a" }];
      },
      async createBotProfile(input) {
        created.push(input.slug);
      },
    },
    1200,
  );

  assert.equal(result.report.imported, 1);
  assert.equal(result.report.deduped, 1);
  assert.equal(result.report.failed, 0);
  assert.equal(result.report.unaccounted, 1198);
  assert.equal(result.report.complete, false);
  assert.deepEqual(created, ["bot-b"]);
});
