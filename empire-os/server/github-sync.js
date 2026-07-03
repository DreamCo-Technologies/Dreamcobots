import * as fs from "fs";
const REPO_OWNER = "DreamCo-Technologies";
const REPO_NAME = "Dreamcobots";
const GITHUB_API = "https://api.github.com";
// ─── auth ────────────────────────────────────────────────────────────────────
function getToken() {
    const t = process.env.GITHUB_PERSONAL_ACCESS_TOKEN || process.env.GITHUB_TOKEN || "";
    if (t.length < 10)
        throw new Error("GitHub token not set. Add GITHUB_PERSONAL_ACCESS_TOKEN in Replit Secrets.");
    return t;
}
async function gh(path, opts = {}) {
    const r = await fetch(`${GITHUB_API}${path}`, {
        ...opts,
        headers: {
            Authorization: `Bearer ${getToken()}`,
            Accept: "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
            ...(opts.headers ?? {}),
        },
    });
    const text = await r.text();
    if (!r.ok)
        throw new Error(`GitHub ${r.status}: ${text.slice(0, 200)}`);
    return text ? JSON.parse(text) : null;
}
// ─── low-level tree helpers ──────────────────────────────────────────────────
async function getRef() {
    const ref = await gh(`/repos/${REPO_OWNER}/${REPO_NAME}/git/ref/heads/main`);
    const commit = await gh(`/repos/${REPO_OWNER}/${REPO_NAME}/git/commits/${ref.object.sha}`);
    return { sha: ref.object.sha, treeSha: commit.tree.sha };
}
/** Push many files in ONE commit using the Git Trees API */
export async function batchPush(files, message) {
    if (files.length === 0)
        return { committed: 0, sha: "" };
    const { sha: headSha, treeSha: baseTreeSha } = await getRef();
    const tree = files.map(f => ({
        path: f.path,
        mode: "100644",
        type: "blob",
        content: f.content,
    }));
    const newTree = await gh(`/repos/${REPO_OWNER}/${REPO_NAME}/git/trees`, {
        method: "POST",
        body: JSON.stringify({ base_tree: baseTreeSha, tree }),
    });
    const newCommit = await gh(`/repos/${REPO_OWNER}/${REPO_NAME}/git/commits`, {
        method: "POST",
        body: JSON.stringify({ message, tree: newTree.sha, parents: [headSha] }),
    });
    await gh(`/repos/${REPO_OWNER}/${REPO_NAME}/git/refs/heads/main`, {
        method: "PATCH",
        body: JSON.stringify({ sha: newCommit.sha }),
    });
    return { committed: files.length, sha: newCommit.sha };
}
// ─── single-file helper (still available for small updates) ─────────────────
export async function pushFile(path, content, message) {
    await batchPush([{ path, content }], message);
}
// ─── bot classification ──────────────────────────────────────────────────────
export function classifyBotLanguage(bot) {
    const txt = `${bot.displayName} ${bot.description} ${JSON.stringify(bot.capabilities ?? [])} ${bot.division} ${bot.category ?? ""}`.toLowerCase();
    const py = ["python", "fastapi", "django", "flask", "pytorch", "tensorflow", "pandas", "numpy", "sklearn", "langchain", "llama", "hugging face", "jupyter", "matplotlib", "scrapy", "boto3", "celery", "asyncio"].filter(k => txt.includes(k)).length;
    const jv = ["java", "spring", "kotlin", "android", "gradle", "maven", "hibernate", "jpa", "micronaut", "quarkus", "ktor", "jetpack", "junit", "akka", "scala", "groovy"].filter(k => txt.includes(k)).length;
    const ts = ["typescript", "javascript", "react", "nextjs", "node", "express", "nestjs", "vue", "angular", "svelte", "vite", "tailwind", "prisma", "drizzle", "trpc", "graphql", "electron"].filter(k => txt.includes(k)).length;
    if (!py && !jv && !ts)
        return "general";
    if (py >= jv && py >= ts)
        return "python";
    if (jv >= py && jv >= ts)
        return "java";
    return ts > 0 ? "typescript" : "general";
}
// ─── bot renderers ───────────────────────────────────────────────────────────
function botPy(b) {
    return `"""${b.displayName}
Division: ${b.division} | Tier: ${b.tier}
${b.description}
Revenue: ${b.revenueModel ?? "SaaS"} | Price: ${b.priceRange ?? "$99/mo"}
"""
import os
from openai import OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
SYSTEM_PROMPT = """${(b.systemPrompt ?? b.description ?? "You are a helpful AI assistant.").replace(/\\/g, "\\\\").replace(/"""/g, "'''").slice(0, 800)}"""
BOT = {"slug":"${b.slug}","division":"${b.division}","tier":"${b.tier}","revenue":"${b.revenueModel ?? "SaaS"}"}
def run(msg, history=None):
    msgs = [{"role":"system","content":SYSTEM_PROMPT}]
    if history: msgs.extend(history)
    msgs.append({"role":"user","content":msg})
    return client.chat.completions.create(model="gpt-4o-mini",messages=msgs,max_tokens=2000).choices[0].message.content
def make_money(task="Generate revenue opportunities"):
    return run(f"MONEY MODE: {task}")
if __name__=="__main__":
    print(f"🤖 {BOT['display_name'] if 'display_name' in BOT else '${b.displayName}'} | {BOT['tier'].upper()}")
    print(run("What can you help me make money with today?"))
`;
}
function botJava(b) {
    const cls = b.displayName.replace(/[^a-zA-Z0-9]/g, "").replace(/^[0-9]/, "_") + "Bot";
    const prompt = (b.systemPrompt ?? b.description ?? "You are a helpful AI assistant.").replace(/"/g, '\\"').replace(/\n/g, "\\n").slice(0, 400);
    return `package com.dreamco.bots;
import java.net.URI; import java.net.http.*; import com.fasterxml.jackson.databind.ObjectMapper; import java.util.*;
/** ${b.displayName} — ${b.division} | ${b.tier} | ${b.revenueModel ?? "SaaS"} */
public class ${cls} {
    static final String PROMPT="${prompt}";
    static final String MODEL="gpt-4o-mini";
    final HttpClient http=HttpClient.newHttpClient(); final ObjectMapper m=new ObjectMapper();
    final String key=System.getenv("OPENAI_API_KEY");
    public String run(String msg) throws Exception {
        var body=m.writeValueAsString(Map.of("model",MODEL,"max_tokens",2000,"messages",List.of(Map.of("role","system","content",PROMPT),Map.of("role","user","content",msg))));
        var req=HttpRequest.newBuilder().uri(URI.create("https://api.openai.com/v1/chat/completions")).header("Authorization","Bearer "+key).header("Content-Type","application/json").POST(HttpRequest.BodyPublishers.ofString(body)).build();
        var res=http.send(req,HttpResponse.BodyHandlers.ofString());
        var json=(Map<?,?>)m.readValue(res.body(),Map.class);
        return (String)((Map<?,?>)((Map<?,?>)((List<?>)json.get("choices")).get(0)).get("message")).get("content");
    }
    public static void main(String[] a) throws Exception { System.out.println(new ${cls}().run("What can you help me make money with today?")); }
}`;
}
function botJson(b) {
    return JSON.stringify({ slug: b.slug, displayName: b.displayName, division: b.division, category: b.category, tier: b.tier, description: b.description, capabilities: b.capabilities, revenueModel: b.revenueModel, targetUsers: b.targetUsers, priceRange: b.priceRange, status: b.status, source: "DreamCo Empire OS", version: "2.0" }, null, 2);
}
// ─── master push: all bots in ONE commit ────────────────────────────────────
export async function pushAllBotsToGitHub(bots) {
    const byLang = { python: 0, java: 0, typescript: 0, general: 0 };
    const files = [];
    const errors = [];
    for (const bot of bots) {
        try {
            const lang = classifyBotLanguage(bot);
            const slug = bot.slug.replace(/[^a-z0-9-]/g, "-");
            // JSON profile for every bot
            files.push({ path: `bots/${slug}/replit_profile.json`, content: botJson(bot) });
            // language-specific file
            if (lang === "python")
                files.push({ path: `python_bots/${slug}.py`, content: botPy(bot) });
            else if (lang === "java")
                files.push({ path: `java_bots/${slug}.java`, content: botJava(bot) });
            byLang[lang]++;
        }
        catch (e) {
            errors.push(`${bot.slug}: ${e.message?.slice(0, 60)}`);
        }
    }
    const { committed, sha } = await batchPush(files, `feat: sync all ${bots.length} Empire OS bots — python:${byLang.python} java:${byLang.java} ts:${byLang.typescript} general:${byLang.general}`);
    return { pushed: committed, sha, byLang, errors };
}
// ─── source-code push: all Replit files in ONE commit ───────────────────────
export async function pushSourceCode() {
    const files = [];
    const errors = [];
    const localFiles = [
        { local: "shared/schema.ts", remote: "empire-os/shared/schema.ts" },
        { local: "shared/tool-belt.ts", remote: "empire-os/shared/tool-belt.ts" },
        { local: "shared/ai-models.ts", remote: "empire-os/shared/ai-models.ts" },
        { local: "shared/ai-ecosystem.ts", remote: "empire-os/shared/ai-ecosystem.ts" },
        { local: "shared/formula-library.ts", remote: "empire-os/shared/formula-library.ts" },
        { local: "shared/division-formulas.ts", remote: "empire-os/shared/division-formulas.ts" },
        { local: "server/seed-bots.ts", remote: "empire-os/server/seed-bots.ts" },
        { local: "server/seed-buddy-bot.ts", remote: "empire-os/server/seed-buddy-bot.ts" },
        { local: "server/seed-codelabs.ts", remote: "empire-os/server/seed-codelabs.ts" },
        { local: "server/seed-github-bots.ts", remote: "empire-os/server/seed-github-bots.ts" },
        { local: "server/routes.ts", remote: "empire-os/server/routes.ts" },
        { local: "server/storage.ts", remote: "empire-os/server/storage.ts" },
        { local: "server/github-sync.ts", remote: "empire-os/server/github-sync.ts" },
        { local: "server/index.ts", remote: "empire-os/server/index.ts" },
        { local: "server/db.ts", remote: "empire-os/server/db.ts" },
        { local: ".env.example", remote: "empire-os/.env.example" },
        { local: "package.json", remote: "empire-os/package.json" },
        { local: "drizzle.config.ts", remote: "empire-os/drizzle.config.ts" },
        { local: "tailwind.config.ts", remote: "empire-os/tailwind.config.ts" },
        { local: "vite.config.ts", remote: "empire-os/vite.config.ts" },
        { local: "tsconfig.json", remote: "empire-os/tsconfig.json" },
        { local: "postcss.config.js", remote: "empire-os/postcss.config.js" },
        { local: "replit.md", remote: "empire-os/replit.md" },
        { local: "client/src/App.tsx", remote: "empire-os/client/src/App.tsx" },
        { local: "client/index.html", remote: "empire-os/client/index.html" },
    ];
    // Add all pages
    try {
        const pages = fs.readdirSync("client/src/pages").filter(f => f.endsWith(".tsx") || f.endsWith(".ts"));
        for (const p of pages)
            localFiles.push({ local: `client/src/pages/${p}`, remote: `empire-os/client/src/pages/${p}` });
    }
    catch { }
    // Add components
    try {
        const comps = fs.readdirSync("client/src/components").filter(f => f.endsWith(".tsx") || f.endsWith(".ts"));
        for (const c of comps)
            localFiles.push({ local: `client/src/components/${c}`, remote: `empire-os/client/src/components/${c}` });
    }
    catch { }
    // Add hooks
    try {
        const hooks = fs.readdirSync("client/src/hooks").filter(f => f.endsWith(".tsx") || f.endsWith(".ts"));
        for (const h of hooks)
            localFiles.push({ local: `client/src/hooks/${h}`, remote: `empire-os/client/src/hooks/${h}` });
    }
    catch { }
    // Add lib files
    try {
        const libs = fs.readdirSync("client/src/lib").filter(f => f.endsWith(".tsx") || f.endsWith(".ts"));
        for (const l of libs)
            localFiles.push({ local: `client/src/lib/${l}`, remote: `empire-os/client/src/lib/${l}` });
    }
    catch { }
    for (const { local, remote } of localFiles) {
        try {
            if (!fs.existsSync(local))
                continue;
            files.push({ path: remote, content: fs.readFileSync(local, "utf-8") });
        }
        catch (e) {
            errors.push(`${local}: ${e.message?.slice(0, 60)}`);
        }
    }
    const { committed, sha } = await batchPush(files, `feat: sync full Empire OS source (${files.length} files) from Replit`);
    return { pushed: committed, sha, errors };
}
// ─── repo info ───────────────────────────────────────────────────────────────
export async function getRepoInfo() {
    return gh(`/repos/${REPO_OWNER}/${REPO_NAME}`);
}
export async function getPullRequests() {
    return gh(`/repos/${REPO_OWNER}/${REPO_NAME}/pulls?state=all&per_page=10`);
}
export async function getRepoContents(path = "") {
    try {
        const d = await gh(`/repos/${REPO_OWNER}/${REPO_NAME}/contents/${path}`);
        return Array.isArray(d) ? d : [d];
    }
    catch {
        return [];
    }
}
// ─── master README ───────────────────────────────────────────────────────────
export function buildMasterReadme(bots, byLang) {
    const divisions = [...new Set(bots.map(b => b.division))];
    const tiers = bots.reduce((a, b) => { a[b.tier] = (a[b.tier] ?? 0) + 1; return a; }, {});
    return `# 🤖 DreamCo Empire OS — Bot Repository

> **${bots.length} AI bots · 45 divisions · Self-learning · Revenue-generating · Fully deployed on Replit**

## 📁 Repository Structure

| Folder | Files | Description |
|--------|-------|-------------|
| \`bots/{slug}/replit_profile.json\` | ${bots.length} | Every bot profile synced from Empire OS |
| \`python_bots/\` | ${byLang.python ?? 0} | Python bots (FastAPI, PyTorch, LangChain, etc.) |
| \`java_bots/\` | ${byLang.java ?? 0} | Java/Kotlin bots (Spring Boot, Android, etc.) |
| \`empire-os/\` | 80+ | Full React + Express source code |
| \`workflows.json\` | 1 | Automated revenue workflows |

## 🏢 Divisions (${divisions.length})
${divisions.map(d => `- **${d}**`).join("\n")}

## 💰 Bot Tiers
${Object.entries(tiers).map(([t, c]) => `- **${t}**: ${c} bots`).join("\n")}

## ⚡ Quick Start

### Python bots
\`\`\`bash
export OPENAI_API_KEY=sk-...
python python_bots/dream-bot.py
\`\`\`

### Java bots
\`\`\`bash
export OPENAI_API_KEY=sk-...
javac java_bots/DreamBot.java && java DreamBot
\`\`\`

### Full Empire OS web app
\`\`\`bash
cd empire-os
cp .env.example .env   # fill in your keys
npm install
npm run dev            # runs on http://localhost:5000
\`\`\`

## 🧠 Self-Learning System
Every bot logs learnings after each conversation using the \`SELF_LEARNING_PROMPT\` protocol. Memory is stored per-bot in PostgreSQL and injected at the start of every new session.

## 🤝 Buddy Bot
The master coding brain covering 500+ libraries. Every other bot routes coding tasks through Buddy Bot automatically.

---
*Synced from DreamCo Empire OS on Replit — Autonomous wealth generation at scale*
`;
}
