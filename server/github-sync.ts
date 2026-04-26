const REPO_OWNER = "DreamCo-Technologies";
const REPO_NAME = "Dreamcobots";
const GITHUB_API = "https://api.github.com";

function getToken(): string {
  const token = process.env.GITHUB_TOKEN;
  if (!token || token.length < 10) throw new Error("GITHUB_TOKEN not set or invalid. Please add a valid GitHub PAT in Replit Secrets.");
  return token;
}

async function ghFetch(path: string, options: RequestInit = {}): Promise<any> {
  const token = getToken();
  const res = await fetch(`${GITHUB_API}${path}`, {
    ...options,
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`GitHub API ${res.status}: ${err}`);
  }
  const text = await res.text();
  return text ? JSON.parse(text) : null;
}

export async function getFileSha(filePath: string): Promise<string | null> {
  try {
    const data = await ghFetch(`/repos/${REPO_OWNER}/${REPO_NAME}/contents/${filePath}`);
    return data?.sha ?? null;
  } catch {
    return null;
  }
}

export async function pushFile(filePath: string, content: string, message: string): Promise<void> {
  const sha = await getFileSha(filePath);
  const body: any = { message, content: Buffer.from(content).toString("base64") };
  if (sha) body.sha = sha;
  await ghFetch(`/repos/${REPO_OWNER}/${REPO_NAME}/contents/${filePath}`, {
    method: "PUT",
    body: JSON.stringify(body),
  });
}

export function classifyBotLanguage(bot: any): "python" | "java" | "typescript" | "general" {
  const text = `${bot.displayName} ${bot.description} ${JSON.stringify(bot.capabilities ?? [])} ${bot.division} ${bot.category ?? ""}`.toLowerCase();
  const pyScore = ["python","fastapi","django","flask","pytorch","tensorflow","pandas","numpy","sklearn","langchain","llama","hugging face","jupyter","matplotlib","scrapy","boto3","celery","asyncio"].filter(k => text.includes(k)).length;
  const javaScore = ["java","spring","kotlin","android","gradle","maven","hibernate","jpa","micronaut","quarkus","ktor","jetpack","junit","akka","scala","groovy"].filter(k => text.includes(k)).length;
  const tsScore = ["typescript","javascript","react","nextjs","node","express","nestjs","vue","angular","svelte","vite","tailwind","prisma","drizzle","trpc","graphql","electron"].filter(k => text.includes(k)).length;
  if (pyScore === 0 && javaScore === 0 && tsScore === 0) return "general";
  if (pyScore >= javaScore && pyScore >= tsScore) return "python";
  if (javaScore >= pyScore && javaScore >= tsScore) return "java";
  return tsScore > 0 ? "typescript" : "general";
}

export function botToPythonFile(bot: any): string {
  const caps = (bot.capabilities ?? []).map((c: string) => `  # - ${c}`).join("\n");
  return `"""
${bot.displayName}
=========================================
Division : ${bot.division}
Category : ${bot.category ?? "general"}
Tier     : ${bot.tier}
Revenue  : ${bot.revenueModel ?? "SaaS"}
Price    : ${bot.priceRange ?? "$99/mo"}
Users    : ${bot.targetUsers ?? "businesses"}

Description:
${bot.description}

Capabilities:
${(bot.capabilities ?? []).map((c: string) => `  - ${c}`).join("\n")}
"""

import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM_PROMPT = """${(bot.systemPrompt ?? bot.description ?? "You are a helpful AI assistant.").replace(/`/g, "'")}"""

BOT_CONFIG = {
    "slug": "${bot.slug}",
    "display_name": "${bot.displayName}",
    "division": "${bot.division}",
    "category": "${bot.category ?? "general"}",
    "tier": "${bot.tier}",
    "revenue_model": "${bot.revenueModel ?? "SaaS"}",
    "price": "${bot.priceRange ?? "$99/mo"}",
}

MONEY_STRATEGIES = ${JSON.stringify(bot.capabilities ?? [], null, 2)}


def run(user_message: str, history: list = None) -> str:
    """Run ${bot.displayName} — returns AI response."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=2000,
    )
    return response.choices[0].message.content


def make_money(task: str = "Generate revenue opportunities") -> str:
    """Activate money-making mode."""
    return run(f"MONEY MODE: {task}. Use all capabilities to maximize revenue.")


if __name__ == "__main__":
    print(f"🤖 {BOT_CONFIG['display_name']} — {BOT_CONFIG['tier'].upper()} tier")
    print(f"💰 Revenue: {BOT_CONFIG['revenue_model']} | {BOT_CONFIG['price']}")
    print("-" * 60)
    result = run("Hello! What can you help me make money with today?")
    print(result)
`;
}

export function botToJavaFile(bot: any): string {
  const className = bot.displayName.replace(/[^a-zA-Z0-9]/g, "").replace(/^[0-9]/, "_") + "Bot";
  return `package com.dreamco.bots;

import java.net.URI;
import java.net.http.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.*;

/**
 * ${bot.displayName}
 * Division: ${bot.division} | Tier: ${bot.tier}
 * ${bot.description}
 * Revenue: ${bot.revenueModel ?? "SaaS"} | Price: ${bot.priceRange ?? "$99/mo"}
 */
public class ${className} {
    private static final String SYSTEM_PROMPT = "${(bot.systemPrompt ?? bot.description ?? "You are a helpful AI assistant.").replace(/"/g, '\\"').replace(/\n/g, "\\n").slice(0, 500)}";
    private static final String MODEL = "gpt-4o-mini";
    private static final String API_URL = "https://api.openai.com/v1/chat/completions";
    private static final Map<String, String> CONFIG = Map.of(
        "slug", "${bot.slug}",
        "division", "${bot.division}",
        "tier", "${bot.tier}",
        "revenue", "${bot.revenueModel ?? "SaaS"}"
    );

    private final HttpClient http = HttpClient.newHttpClient();
    private final ObjectMapper mapper = new ObjectMapper();
    private final String apiKey = System.getenv("OPENAI_API_KEY");

    public String run(String userMessage) throws Exception {
        var body = mapper.writeValueAsString(Map.of(
            "model", MODEL, "max_tokens", 2000,
            "messages", List.of(
                Map.of("role", "system", "content", SYSTEM_PROMPT),
                Map.of("role", "user", "content", userMessage)
            )
        ));
        var req = HttpRequest.newBuilder().uri(URI.create(API_URL))
            .header("Authorization", "Bearer " + apiKey)
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(body)).build();
        var res = http.send(req, HttpResponse.BodyHandlers.ofString());
        var json = (Map<?, ?>) mapper.readValue(res.body(), Map.class);
        var choices = (List<?>) json.get("choices");
        var msg = (Map<?, ?>) ((Map<?, ?>) choices.get(0)).get("message");
        return (String) msg.get("content");
    }

    public String makeMonev(String task) throws Exception {
        return run("MONEY MODE: " + task + ". Maximize revenue using all capabilities.");
    }

    public static void main(String[] args) throws Exception {
        var bot = new ${className}();
        System.out.println("Running ${bot.displayName}...");
        System.out.println(bot.run("What can you help me make money with today?"));
    }
}
`;
}

export function botToJsonProfile(bot: any): string {
  return JSON.stringify({
    slug: bot.slug, displayName: bot.displayName,
    division: bot.division, category: bot.category, tier: bot.tier,
    description: bot.description, capabilities: bot.capabilities,
    revenueModel: bot.revenueModel, targetUsers: bot.targetUsers,
    priceRange: bot.priceRange, status: bot.status,
    systemPrompt: bot.systemPrompt,
    source: "DreamCo Empire OS — Replit",
    version: "2.0",
  }, null, 2);
}

// ── Push all bots organized by language ────────────────────────────────────
export async function pushAllBotsToGitHub(bots: any[]): Promise<{ pushed: number; errors: string[]; byLang: Record<string, number> }> {
  const errors: string[] = [];
  let pushed = 0;
  const byLang: Record<string, number> = { python: 0, java: 0, typescript: 0, general: 0 };

  for (const bot of bots) {
    const lang = classifyBotLanguage(bot);
    const slug = bot.slug.replace(/[^a-z0-9-]/g, "-");
    try {
      // Always push JSON profile
      await pushFile(`bots/${slug}/replit_profile.json`, botToJsonProfile(bot), `feat: sync ${bot.displayName} profile from Empire OS`);
      // Push language-specific file
      if (lang === "python") {
        await pushFile(`python_bots/${slug}.py`, botToPythonFile(bot), `feat: add ${bot.displayName} Python bot`);
      } else if (lang === "java") {
        await pushFile(`java_bots/${slug}.java`, botToJavaFile(bot), `feat: add ${bot.displayName} Java bot`);
      }
      byLang[lang]++;
      pushed++;
    } catch (e: any) {
      errors.push(`${bot.slug}: ${e.message?.slice(0, 80)}`);
    }
  }
  return { pushed, errors, byLang };
}

// ── Push entire Replit source code ─────────────────────────────────────────
export async function pushSourceFile(repoPath: string, localContent: string, message: string): Promise<void> {
  await pushFile(`empire-os/${repoPath}`, localContent, message);
}

export async function getRepoInfo(): Promise<any> {
  return ghFetch(`/repos/${REPO_OWNER}/${REPO_NAME}`);
}

export async function getPullRequests(): Promise<any[]> {
  return ghFetch(`/repos/${REPO_OWNER}/${REPO_NAME}/pulls?state=all&per_page=10`);
}

export async function getRepoContents(path = ""): Promise<any[]> {
  try {
    const data = await ghFetch(`/repos/${REPO_OWNER}/${REPO_NAME}/contents/${path}`);
    return Array.isArray(data) ? data : [data];
  } catch { return []; }
}

// ── Generate master README ─────────────────────────────────────────────────
export function buildMasterReadme(bots: any[], byLang: Record<string, number>): string {
  const divisions = [...new Set(bots.map(b => b.division))];
  const tiers = bots.reduce((a: Record<string, number>, b) => { a[b.tier] = (a[b.tier] ?? 0) + 1; return a; }, {});
  return `# 🤖 DreamCo Empire OS — Bot Repository

> **The world's most advanced autonomous AI empire**
> ${bots.length} AI bots · 45 divisions · Self-learning · Revenue-generating · Fully deployed

## 🚀 Live System
**Run on Replit:** All ${bots.length} bots are live with AI chat, memory, and autonomous operation.

## 📁 Bot Organization

| Folder | Count | Language | Description |
|--------|-------|----------|-------------|
| \`python_bots/\` | ${byLang.python ?? 0} | Python | FastAPI, PyTorch, LangChain, ML bots |
| \`java_bots/\` | ${byLang.java ?? 0} | Java | Spring Boot, Kotlin, Android bots |
| \`bots/{slug}/replit_profile.json\` | ${bots.length} | All | Complete bot profiles from Empire OS |

## 🏢 Divisions (${divisions.length} total)
${divisions.map(d => `- **${d}**`).join("\n")}

## 💰 Bot Tiers
${Object.entries(tiers).map(([t, c]) => `- **${t}**: ${c} bots`).join("\n")}

## ⚡ Quick Start

### Python Bots
\`\`\`bash
export OPENAI_API_KEY=your_key_here
python python_bots/buddy-bot.py
\`\`\`

### Java Bots
\`\`\`bash
export OPENAI_API_KEY=your_key_here
javac java_bots/BuddyBot.java && java BuddyBot
\`\`\`

### Run All Bots (Python)
\`\`\`bash
python run_all_bots.py
\`\`\`

## 🌐 Empire OS Web App (Full Stack)
The \`empire-os/\` folder contains the complete React + Express + PostgreSQL application:
\`\`\`bash
cd empire-os
npm install
npm run dev
\`\`\`

## 💳 Revenue Streams
Every bot is configured to generate revenue through:
- SaaS subscriptions
- Fiverr/freelance automation
- Real estate lead generation
- Crypto trading signals
- Grant scanning
- Legal payouts
- And 40+ more revenue streams

## 🧠 Self-Learning
All bots use the SELF_LEARNING_PROMPT system — they learn from every conversation and improve over time.

## 🤝 Buddy Bot
Buddy Bot is the master coder covering 500+ libraries. Available in every division as a coding advisor.

---
*Generated by DreamCo Empire OS — Autonomous wealth generation at scale*
`;
}
