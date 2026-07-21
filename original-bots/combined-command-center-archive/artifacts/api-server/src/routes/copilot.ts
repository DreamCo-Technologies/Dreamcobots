import { Router, type IRouter } from "express";
import {
  DREAMCOBOTS_REPO,
  GITHUB_ORG,
  ghFetch,
} from "../lib/githubClient";

const router: IRouter = Router();

const COPILOT_USERS = new Set([
  "copilot-swe-agent[bot]",
  "github-copilot[bot]",
  "Copilot",
  "copilot",
]);

type GhPr = {
  number: number;
  title: string;
  html_url: string;
  user: { login: string; type?: string };
  created_at: string;
  mergeable?: boolean | null;
  mergeable_state?: string;
};

type GhFile = { filename: string };

function isCopilotAuthor(login: string, type?: string): boolean {
  if (COPILOT_USERS.has(login)) return true;
  if (type === "Bot" && login.toLowerCase().includes("copilot")) return true;
  return login.toLowerCase().includes("copilot");
}

function analyzeFiles(files: string[]): {
  contractCompliant: boolean;
  complianceReason: string;
  touchedDirs: string[];
  manifestPresent: boolean;
} {
  const touched = new Set<string>();
  let touchedNonBot = false;
  let manifestPresent = false;
  for (const f of files) {
    if (f.startsWith("bots/")) {
      const parts = f.split("/");
      if (parts.length >= 2 && parts[1]) {
        touched.add(parts[1]);
        if (parts[parts.length - 1] === "bot.manifest.json") {
          manifestPresent = true;
        }
      }
    } else {
      touchedNonBot = true;
    }
  }
  const dirs = Array.from(touched);
  if (touchedNonBot) {
    return {
      contractCompliant: false,
      complianceReason: "Touches files outside bots/* — violates one-folder rule",
      touchedDirs: dirs,
      manifestPresent,
    };
  }
  if (dirs.length === 0) {
    return {
      contractCompliant: false,
      complianceReason: "No bot folder touched",
      touchedDirs: dirs,
      manifestPresent,
    };
  }
  if (dirs.length > 1) {
    return {
      contractCompliant: false,
      complianceReason: `Touches ${dirs.length} bot folders (must be exactly 1)`,
      touchedDirs: dirs,
      manifestPresent,
    };
  }
  if (!manifestPresent) {
    return {
      contractCompliant: false,
      complianceReason: "Missing bot.manifest.json",
      touchedDirs: dirs,
      manifestPresent,
    };
  }
  return {
    contractCompliant: true,
    complianceReason: "Single-folder PR with manifest",
    touchedDirs: dirs,
    manifestPresent,
  };
}

let prCache: object[] | null = null;
let prCacheTime = 0;
const CACHE_TTL = 30_000;

router.get("/copilot/prs", async (req, res): Promise<void> => {
  const now = Date.now();
  if (prCache && now - prCacheTime < CACHE_TTL) {
    res.json(prCache);
    return;
  }
  try {
    const prs = await ghFetch<GhPr[]>(
      `/repos/${GITHUB_ORG}/${DREAMCOBOTS_REPO}/pulls?state=open&per_page=100`,
    );
    const copilotPrs = prs.filter((p) =>
      isCopilotAuthor(p.user?.login ?? "", p.user?.type),
    );
    const enriched = await Promise.all(
      copilotPrs.map(async (pr) => {
        let files: string[] = [];
        try {
          const f = await ghFetch<GhFile[]>(
            `/repos/${GITHUB_ORG}/${DREAMCOBOTS_REPO}/pulls/${pr.number}/files?per_page=100`,
          );
          files = f.map((x) => x.filename);
        } catch {
          // ignore
        }
        const analysis = analyzeFiles(files);
        return {
          number: pr.number,
          title: pr.title,
          url: pr.html_url,
          author: pr.user?.login ?? "unknown",
          createdAt: pr.created_at,
          mergeable: pr.mergeable ?? null,
          mergeableState: pr.mergeable_state ?? null,
          ...analysis,
        };
      }),
    );
    prCache = enriched;
    prCacheTime = now;
    req.log.info({ count: enriched.length }, "Copilot PRs fetched");
    res.json(enriched);
  } catch (err) {
    req.log.warn({ err }, "Failed to fetch Copilot PRs");
    res.json([]);
  }
});

router.post("/copilot/rewrite/:prNumber", async (req, res): Promise<void> => {
  const prNumber = Number(req.params.prNumber);
  if (!Number.isFinite(prNumber)) {
    res.status(404).json({ error: "Invalid PR number" });
    return;
  }
  try {
    const pr = await ghFetch<GhPr>(
      `/repos/${GITHUB_ORG}/${DREAMCOBOTS_REPO}/pulls/${prNumber}`,
    );
    const body = [
      `@copilot please rewrite PR #${prNumber} ("${pr.title}") to fit the bot contract.`,
      "",
      "Requirements:",
      "- All changes inside exactly one `bots/<name>/` directory.",
      "- Include `bot.manifest.json` validated by the schema at the repo root.",
      "- Do not edit shared files (workflows, registries, catalogues).",
      "",
      `Original PR: ${pr.html_url}`,
    ].join("\n");
    const issue = await ghFetch<{ number: number; html_url: string }>(
      `/repos/${GITHUB_ORG}/${DREAMCOBOTS_REPO}/issues`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: `[contract-rewrite] PR #${prNumber}: ${pr.title}`,
          body,
          labels: ["copilot-rewrite", "bot-contract"],
        }),
      },
    );
    res.json({ issueNumber: issue.number, issueUrl: issue.html_url });
  } catch (err) {
    req.log.warn({ err, prNumber }, "Failed to create rewrite issue");
    res.status(404).json({ error: "PR not found or GitHub API unavailable" });
  }
});

export default router;
