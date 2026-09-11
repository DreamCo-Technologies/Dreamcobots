#!/usr/bin/env node

import { spawn, spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const localTsx = resolve(root, "node_modules", ".bin", "tsx");
const portIndex = process.argv.indexOf("--port");
const port = portIndex >= 0 ? process.argv[portIndex + 1] : process.env.PORT || "5000";
const ownerIndex = process.argv.indexOf("--owner");
const owner = ownerIndex >= 0 ? process.argv[ownerIndex + 1] : process.env.DREAMCO_LOCAL_TEST_OWNER || "irean jordan";
const tierIndex = process.argv.indexOf("--tier");
const tier = tierIndex >= 0 ? process.argv[tierIndex + 1] : process.env.DREAMCO_LOCAL_TEST_TIER || "elite";
const bundledPnpm = "/Users/mamas/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback/pnpm";
const databaseUrl = process.env.DATABASE_URL || "postgres://dreamco_local:local@127.0.0.1:5432/dreamco_local";

function commandExists(command) {
  const result = spawnSync(command, ["--version"], { stdio: "ignore" });
  return result.status === 0;
}

function devRunner() {
  if (existsSync(localTsx)) return { command: localTsx, args: ["server/index.ts"] };
  if (process.env.DREAMCO_PACKAGE_RUNNER && commandExists(process.env.DREAMCO_PACKAGE_RUNNER)) {
    return { command: process.env.DREAMCO_PACKAGE_RUNNER, args: ["run", "dev"] };
  }
  if (commandExists("npm")) return { command: "npm", args: ["run", "dev"] };
  if (existsSync(bundledPnpm)) return { command: bundledPnpm, args: ["run", "dev"] };
  if (commandExists("pnpm")) return { command: "pnpm", args: ["run", "dev"] };
  return null;
}

if (!existsSync(resolve(root, "package.json"))) {
  console.error("Run this command from inside the Dreamcobots repository.");
  process.exit(1);
}

console.log("Starting Buddy laptop app in local test mode.");
console.log(`- URL: http://localhost:${port}/buddy`);
console.log(`- Pricing/account check: http://localhost:${port}/pricing`);
console.log(`- Local test owner: ${owner}`);
console.log(`- Local test tier: ${tier}`);
console.log("- Stripe billing is not modified by this launcher.");
if (!process.env.DATABASE_URL) {
  console.log("- DATABASE_URL is not set; using a local placeholder so frontend/test entitlement routes can boot.");
  console.log("- Database-backed API routes still need a real local Postgres DATABASE_URL.");
}
if (!process.env.AI_INTEGRATIONS_OPENAI_API_KEY && !process.env.OPENAI_API_KEY && !process.env.OPENAI_ADMIN_KEY) {
  console.log("- OpenAI key is not set; using a local placeholder so provider clients can initialize.");
  console.log("- Real model, image, audio, and agent calls still need a real approved API key.");
}

const runner = devRunner();
if (!runner) {
  console.error("No package runner found. Install Node.js/npm or set DREAMCO_PACKAGE_RUNNER to npm/pnpm.");
  process.exit(1);
}

const child = spawn(runner.command, runner.args, {
  cwd: root,
  stdio: "inherit",
  env: {
    ...process.env,
    NODE_ENV: "development",
    PORT: port,
    HOST: process.env.HOST || "127.0.0.1",
    DATABASE_URL: databaseUrl,
    DREAMCO_DATABASE_PLACEHOLDER: process.env.DATABASE_URL ? "0" : "1",
    AI_INTEGRATIONS_OPENAI_API_KEY:
      process.env.AI_INTEGRATIONS_OPENAI_API_KEY ||
      process.env.OPENAI_API_KEY ||
      process.env.OPENAI_ADMIN_KEY ||
      "sk-local-test-placeholder",
    OPENAI_API_KEY:
      process.env.OPENAI_API_KEY ||
      process.env.AI_INTEGRATIONS_OPENAI_API_KEY ||
      process.env.OPENAI_ADMIN_KEY ||
      "sk-local-test-placeholder",
    PATH: `${resolve(process.execPath, "..")}:${process.env.PATH || ""}`,
    DREAMCO_DISABLE_AUTO_SYNC: process.env.DREAMCO_DISABLE_AUTO_SYNC || "1",
    DREAMCO_ENABLE_LOCAL_TEST_ACCOUNT: "1",
    DREAMCO_LOCAL_TEST_OWNER: owner,
    DREAMCO_LOCAL_TEST_TIER: tier,
  },
});

child.on("exit", (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }
  process.exit(code ?? 0);
});
