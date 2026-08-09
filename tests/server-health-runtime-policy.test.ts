import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";

const source = fs.readFileSync(path.join(process.cwd(), "server/index.ts"), "utf8");

test("production server exposes a non-secret health endpoint", () => {
  assert.match(source, /app\.get\(['"]\/api\/health['"]/);
  assert.match(source, /ok:\s*true/);
  assert.match(source, /uptimeSeconds/);
  assert.match(source, /stripeConfigured/);
  assert.doesNotMatch(source, /STRIPE_SECRET_KEY\s*[,}]/);
});

test("runtime smoke can disable GitHub auto-sync side effects", () => {
  assert.match(source, /DREAMCO_DISABLE_AUTO_SYNC/);
  assert.match(source, /scheduleAutoSync/);
  assert.match(source, /GitHub auto-sync scheduler unavailable/);
});
