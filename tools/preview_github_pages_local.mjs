#!/usr/bin/env node

import { spawn, spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const websiteDir = resolve(root, "website");
const portIndex = process.argv.indexOf("--port");
const port = portIndex >= 0 ? process.argv[portIndex + 1] : process.env.BUDDY_PAGES_PORT || "4173";

if (!existsSync(websiteDir)) {
  console.error("Missing website directory. Cannot preview GitHub Pages locally.");
  process.exit(1);
}

console.log("Running Buddy GitHub Pages preflight before local preview...");
const preflight = spawnSync("python3", ["tools/build_buddy_public_site.py", "--check"], {
  cwd: root,
  stdio: "inherit",
});

if (preflight.status !== 0) {
  console.error("Buddy Pages preflight failed. Local preview was not started.");
  process.exit(preflight.status ?? 1);
}

console.log(`Serving the GitHub Pages website locally at http://localhost:${port}/buddy.html`);
console.log("This is the static Pages surface; private backend/API features still require the laptop app.");

const child = spawn("python3", ["-m", "http.server", port, "--directory", websiteDir], {
  cwd: root,
  stdio: "inherit",
});

child.on("exit", (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }
  process.exit(code ?? 0);
});
