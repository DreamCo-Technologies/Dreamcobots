import { execFileSync, spawnSync } from "node:child_process";

const repo = process.env.GITHUB_REPOSITORY;
const token = process.env.GITHUB_TOKEN;
const issueNumber = process.env.ISSUE_NUMBER;
const verify = process.env.VERIFY_BEFORE_CLOSE !== "false";

if (!repo || !token || !issueNumber) {
  console.error("GITHUB_REPOSITORY, GITHUB_TOKEN, and ISSUE_NUMBER are required");
  process.exit(2);
}

const [owner, name] = repo.split("/");
const apiBase = `https://api.github.com/repos/${owner}/${name}`;
const headers = {
  Authorization: `Bearer ${token}`,
  Accept: "application/vnd.github+json",
  "X-GitHub-Api-Version": "2022-11-28",
  "Content-Type": "application/json",
};

async function github(path, options = {}) {
  const response = await fetch(`${apiBase}${path}`, { ...options, headers: { ...headers, ...(options.headers || {}) } });
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}: ${await response.text()}`);
  if (response.status === 204) return null;
  return response.json();
}

function normalize(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/`[^`]+`/g, " ")
    .replace(/https?:\/\/\S+/g, " ")
    .replace(/[^a-z0-9_./ -]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function checklist(body) {
  return body.split(/\r?\n/).flatMap((line, index) => {
    const match = line.match(/^\s*[-*]\s+\[([ xX])\]\s+(.+)$/);
    if (!match) return [];
    return [{ line: index, done: match[1].toLowerCase() === "x", text: match[2].trim() }];
  });
}

function keywords(text) {
  const stop = new Set(["the","and","for","with","from","into","that","this","should","must","every","build","implement","add","make","system","buddy"]);
  return [...new Set(normalize(text).split(" ").filter((word) => word.length >= 4 && !stop.has(word)))].slice(0, 8);
}

function repositoryCandidates(text) {
  const terms = keywords(text);
  if (!terms.length) return [];
  const pattern = terms.slice(0, 4).join("|");
  try {
    const output = execFileSync("git", ["grep", "-n", "-I", "-E", pattern, "--", ":(exclude)node_modules", ":(exclude)dist", ":(exclude)tmp"], { encoding: "utf8", maxBuffer: 2_000_000 });
    return output.trim().split("\n").filter(Boolean).slice(0, 12);
  } catch (error) {
    const stdout = error?.stdout ? String(error.stdout) : "";
    return stdout.trim().split("\n").filter(Boolean).slice(0, 12);
  }
}

function hasStrongRepositoryEvidence(item, matches) {
  const terms = keywords(item.text);
  if (terms.length < 2 || matches.length === 0) return false;
  const joined = normalize(matches.join(" "));
  const matched = terms.filter((term) => joined.includes(term));
  return matched.length >= Math.min(3, Math.max(2, Math.ceil(terms.length * 0.5)));
}

const issue = await github(`/issues/${issueNumber}`);
const items = checklist(issue.body || "");
const review = items.map((item) => {
  if (item.done) return { ...item, state: "already_marked_complete", matches: [] };
  const matches = repositoryCandidates(item.text);
  return { ...item, state: hasStrongRepositoryEvidence(item, matches) ? "candidate_already_built" : "remaining_work", matches };
});

const remaining = review.filter((item) => item.state === "remaining_work");
const candidates = review.filter((item) => item.state === "candidate_already_built");

const markerStart = "<!-- dreamco-builder-reconciliation:start -->";
const markerEnd = "<!-- dreamco-builder-reconciliation:end -->";
const active = [
  markerStart,
  "## Builder reconciliation",
  "",
  `Last repository comparison: ${new Date().toISOString()}`,
  "",
  `- Checklist items found: ${items.length}`,
  `- Remaining work: ${remaining.length}`,
  `- Already checked complete: ${review.filter((item) => item.state === "already_marked_complete").length}`,
  `- Candidate existing implementations requiring verification: ${candidates.length}`,
  "",
  "### Active work only",
  ...(remaining.length ? remaining.map((item) => `- [ ] ${item.text}`) : ["- [x] No unmet checklist items detected by repository comparison."]),
  "",
  "### Candidate existing implementations",
  ...(candidates.length ? candidates.map((item) => `- [ ] VERIFY: ${item.text}${item.matches[0] ? ` — candidate evidence: \`${item.matches[0].split(":").slice(0,2).join(":")}\`` : ""}`) : ["- None detected."]),
  "",
  "> Candidate matches are never treated as complete automatically. Builder bots must verify behavior, tests, and acceptance criteria before checking them off.",
  markerEnd,
].join("\n");

const body = String(issue.body || "");
const markerPattern = new RegExp(`${markerStart}[\\s\\S]*?${markerEnd}`, "m");
const updatedBody = markerPattern.test(body) ? body.replace(markerPattern, active) : `${body.trim()}\n\n${active}\n`;
await github(`/issues/${issueNumber}`, { method: "PATCH", body: JSON.stringify({ body: updatedBody }) });

let verificationPassed = false;
if (remaining.length === 0 && candidates.length === 0 && verify) {
  const result = spawnSync("npx", ["tsx", "tools/run_universal_verification.ts"], { stdio: "inherit", env: process.env, timeout: 30 * 60 * 1000 });
  verificationPassed = result.status === 0;
} else if (remaining.length === 0 && candidates.length === 0) {
  verificationPassed = true;
}

if (remaining.length === 0 && candidates.length === 0 && verificationPassed) {
  await github(`/issues/${issueNumber}`, { method: "PATCH", body: JSON.stringify({ state: "closed", state_reason: "completed" }) });
  console.log(`Issue #${issueNumber} closed after repository reconciliation and verification.`);
} else {
  console.log(JSON.stringify({ issue: Number(issueNumber), remaining: remaining.length, candidatesToVerify: candidates.length, verificationPassed }, null, 2));
}
