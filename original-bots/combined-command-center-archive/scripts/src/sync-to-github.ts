/**
 * Push the current working tree to the DreamCo GitHub repository in one command.
 *
 * Uploads every git-tracked file (excluding generated/vendor noise) that differs
 * from the remote, at its real path, in a single commit. This is an additive/
 * update sync: it does NOT delete files on the remote that were removed locally.
 * Run with:  pnpm --filter @workspace/scripts run sync
 *
 * Requires env: GITHUB_PERSONAL_ACCESS_TOKEN
 */
import fs from "node:fs";
import crypto from "node:crypto";
import { execSync } from "node:child_process";

const TOKEN = process.env.GITHUB_PERSONAL_ACCESS_TOKEN;
const OWNER = process.env.DREAMCO_REPO_OWNER ?? "DreamCo-Technologies";
const REPO = process.env.DREAMCO_REPO_NAME ?? "DreamCo-Command-Center";
const BRANCH = process.env.DREAMCO_REPO_BRANCH ?? "main";

const EXCLUDE = [/^\.local\//, /^\.cache\//, /node_modules\//, /\/dist\//, /^dist\//, /\.dreamco-artifact\//, /\.tsbuildinfo$/];
const BINARY = /\.(jpg|jpeg|png|gif|webp|ico|pdf|woff2?|ttf|eot|zip|mp3|mp4|wav)$/i;

if (!TOKEN) {
  console.error("GITHUB_PERSONAL_ACCESS_TOKEN is not set. Cannot sync.");
  process.exit(1);
}

async function gh(path: string, init: RequestInit = {}): Promise<any> {
  const r = await fetch(`https://api.github.com${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${TOKEN}`,
      Accept: "application/vnd.github+json",
      "User-Agent": "dreamco-sync",
      ...(init.headers ?? {}),
    },
  });
  if (!r.ok) throw new Error(`${init.method ?? "GET"} ${path} ${r.status}: ${(await r.text()).slice(0, 300)}`);
  return r.json();
}

function blobSha(buf: Buffer): string {
  const h = crypto.createHash("sha1");
  h.update(`blob ${buf.length}\0`);
  h.update(buf);
  return h.digest("hex");
}

async function main(): Promise<void> {
  // Anchor on the repo root so paths are correct regardless of the cwd the
  // package runner uses (pnpm runs scripts with cwd = the package dir).
  const root = execSync("git rev-parse --show-toplevel").toString().trim();
  process.chdir(root);

  // Include tracked files AND new untracked-but-not-gitignored files, so
  // freshly created files are pushed too (plain `git ls-files` omits untracked).
  const listed = execSync("git ls-files --cached --others --exclude-standard", { cwd: root, maxBuffer: 1 << 26 })
    .toString()
    .split("\n")
    .filter(Boolean);
  const local = [...new Set(listed)].filter((f) => !EXCLUDE.some((rx) => rx.test(f)) && fs.existsSync(f));

  const ref = await gh(`/repos/${OWNER}/${REPO}/git/refs/heads/${BRANCH}`);
  const base = await gh(`/repos/${OWNER}/${REPO}/git/commits/${ref.object.sha}`);
  const treeResp = await gh(`/repos/${OWNER}/${REPO}/git/trees/${base.tree.sha}?recursive=1`);
  if (treeResp.truncated) console.warn("WARNING: remote tree truncated — diff may be incomplete.");
  const remote = new Map<string, string>(
    treeResp.tree.filter((t: any) => t.type === "blob").map((t: any) => [t.path, t.sha]),
  );

  const toPush = local.filter((f) => {
    const sha = blobSha(fs.readFileSync(f));
    return remote.get(f) !== sha;
  });

  if (toPush.length === 0) {
    console.log(`Already in sync — ${local.length} files match the repo. Nothing to push.`);
    return;
  }

  const tree: Array<{ path: string; mode: string; type: string; sha: string }> = [];
  for (const f of toPush) {
    const bin = BINARY.test(f);
    const content = bin ? fs.readFileSync(f).toString("base64") : fs.readFileSync(f, "utf8");
    const blob = await gh(`/repos/${OWNER}/${REPO}/git/blobs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content, encoding: bin ? "base64" : "utf-8" }),
    });
    tree.push({ path: f, mode: "100644", type: "blob", sha: blob.sha });
    process.stdout.write(".");
  }
  process.stdout.write("\n");

  const t = await gh(`/repos/${OWNER}/${REPO}/git/trees`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ base_tree: base.tree.sha, tree }),
  });
  const c = await gh(`/repos/${OWNER}/${REPO}/git/commits`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: `chore(sync): mirror working tree — ${toPush.length} file(s) updated`,
      tree: t.sha,
      parents: [ref.object.sha],
    }),
  });
  await gh(`/repos/${OWNER}/${REPO}/git/refs/heads/${BRANCH}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sha: c.sha }),
  });
  console.log(`Synced ${toPush.length} file(s) -> https://github.com/${OWNER}/${REPO}/commit/${c.sha}`);
}

main().catch((err) => {
  console.error(err instanceof Error ? err.message : err);
  process.exit(1);
});
