const REPO_OWNER = "DreamCo-Technologies";
const REPO_NAME = "Dreamcobots";
const GITHUB_API = "https://api.github.com";

function getToken(): string {
  const token = process.env.GITHUB_TOKEN;
  if (!token) throw new Error("GITHUB_TOKEN secret is not set. Add it in Replit Secrets.");
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
  const body: any = {
    message,
    content: Buffer.from(content).toString("base64"),
  };
  if (sha) body.sha = sha;
  await ghFetch(`/repos/${REPO_OWNER}/${REPO_NAME}/contents/${filePath}`, {
    method: "PUT",
    body: JSON.stringify(body),
  });
}

export function classifyBotLanguage(bot: any): "python" | "java" | "typescript" | "general" {
  const text = `${bot.displayName} ${bot.description} ${JSON.stringify(bot.capabilities)} ${bot.division} ${bot.category}`.toLowerCase();
  const pythonKeywords = ["python", "fastapi", "django", "flask", "pytorch", "tensorflow", "pandas", "numpy", "sklearn", "pydantic", "celery", "asyncio", "starlette", "langchain", "llama", "hugging face", "jupyter", "matplotlib", "seaborn", "polars", "sqlalchemy", "alembic", "scrapy", "boto3", "aws lambda python", "google cloud python"];
  const javaKeywords = ["java", "spring", "kotlin", "android", "gradle", "maven", "hibernate", "jpa", "micronaut", "quarkus", "ktor", "jetpack", "compose", "junit", "mockito", "testng", "vertx", "grpc java", "akka", "scala", "play framework", "groovy"];
  const tsKeywords = ["typescript", "javascript", "react", "nextjs", "node", "express", "nestjs", "vue", "angular", "svelte", "vite", "webpack", "tailwind", "prisma", "drizzle", "trpc", "graphql", "socket.io", "electron", "tauri", "expo", "react native"];

  const pyScore = pythonKeywords.filter(k => text.includes(k)).length;
  const javaScore = javaKeywords.filter(k => text.includes(k)).length;
  const tsScore = tsKeywords.filter(k => text.includes(k)).length;

  if (pyScore === 0 && javaScore === 0 && tsScore === 0) return "general";
  if (pyScore >= javaScore && pyScore >= tsScore) return "python";
  if (javaScore >= pyScore && javaScore >= tsScore) return "java";
  if (tsScore > 0) return "typescript";
  return "general";
}

export function botToJsonFile(bot: any): string {
  return JSON.stringify({
    slug: bot.slug,
    displayName: bot.displayName,
    division: bot.division,
    category: bot.category,
    tier: bot.tier,
    description: bot.description,
    capabilities: bot.capabilities,
    systemPrompt: bot.systemPrompt,
    revenueModel: bot.revenueModel,
    targetUsers: bot.targetUsers,
    priceRange: bot.priceRange,
    status: bot.status,
    traits: bot.traits,
  }, null, 2);
}

export function botToPythonFile(bot: any): string {
  const caps = (bot.capabilities ?? []).slice(0, 8).map((c: string) => `    # - ${c}`).join("\n");
  return `"""
${bot.displayName}
Division: ${bot.division} | Category: ${bot.category} | Tier: ${bot.tier}
${bot.description}

Capabilities:
${(bot.capabilities ?? []).slice(0, 8).map((c: string) => `  - ${c}`).join("\n")}

Revenue Model: ${bot.revenueModel}
Target Users: ${bot.targetUsers}
Price: ${bot.priceRange}
"""

import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM_PROMPT = """${bot.systemPrompt?.replace(/`/g, "'")}"""

BOT_CONFIG = {
    "slug": "${bot.slug}",
    "display_name": "${bot.displayName}",
    "division": "${bot.division}",
    "category": "${bot.category}",
    "tier": "${bot.tier}",
    "capabilities": ${JSON.stringify(bot.capabilities ?? []).replace(/"/g, '"')},
}


def run(user_message: str, history: list = None) -> str:
    """Run the ${bot.displayName} bot with a user message."""
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


if __name__ == "__main__":
    print(f"Running {BOT_CONFIG['display_name']} bot...")
    result = run("Hello! What can you help me with today?")
    print(result)
`;
}

export function botToJavaFile(bot: any): string {
  const className = bot.displayName.replace(/[^a-zA-Z0-9]/g, "") + "Bot";
  return `package com.dreamco.bots.${bot.division.toLowerCase()};

import java.net.URI;
import java.net.http.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.*;

/**
 * ${bot.displayName}
 * Division: ${bot.division} | Category: ${bot.category} | Tier: ${bot.tier}
 * ${bot.description}
 *
 * Capabilities:
${(bot.capabilities ?? []).slice(0, 8).map((c: string) => ` * - ${c}`).join("\n")}
 *
 * Revenue Model: ${bot.revenueModel}
 * Target Users: ${bot.targetUsers}
 * Price: ${bot.priceRange}
 */
public class ${className} {

    private static final String SYSTEM_PROMPT = "${(bot.systemPrompt ?? "").replace(/"/g, '\\"').replace(/\n/g, "\\n").slice(0, 500)}...";
    private static final String MODEL = "gpt-4o-mini";
    private static final String API_URL = "https://api.openai.com/v1/chat/completions";

    private final HttpClient httpClient;
    private final ObjectMapper mapper;
    private final String apiKey;

    public ${className}() {
        this.httpClient = HttpClient.newHttpClient();
        this.mapper = new ObjectMapper();
        this.apiKey = System.getenv("OPENAI_API_KEY");
    }

    public String run(String userMessage) throws Exception {
        Map<String, Object> body = new HashMap<>();
        body.put("model", MODEL);
        body.put("max_tokens", 2000);
        body.put("messages", List.of(
            Map.of("role", "system", "content", SYSTEM_PROMPT),
            Map.of("role", "user", "content", userMessage)
        ));

        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(API_URL))
            .header("Authorization", "Bearer " + apiKey)
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(mapper.writeValueAsString(body)))
            .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        Map<?, ?> json = mapper.readValue(response.body(), Map.class);
        List<?> choices = (List<?>) json.get("choices");
        Map<?, ?> first = (Map<?, ?>) choices.get(0);
        Map<?, ?> message = (Map<?, ?>) first.get("message");
        return (String) message.get("content");
    }

    public static void main(String[] args) throws Exception {
        ${className} bot = new ${className}();
        System.out.println("Running ${bot.displayName}...");
        System.out.println(bot.run("Hello! What can you help me with today?"));
    }
}
`;
}

export async function pushAllBotsToGitHub(bots: any[]): Promise<{ pushed: number; errors: string[] }> {
  const errors: string[] = [];
  let pushed = 0;

  const byLang: Record<string, any[]> = { python: [], java: [], typescript: [], general: [] };
  for (const bot of bots) {
    const lang = classifyBotLanguage(bot);
    byLang[lang].push(bot);
  }

  // Push bot files organized by language
  for (const [lang, langBots] of Object.entries(byLang)) {
    for (const bot of langBots) {
      try {
        const folder = `bots/${lang}`;
        const slug = bot.slug.replace(/[^a-z0-9-]/g, "-");

        if (lang === "python") {
          await pushFile(`${folder}/${slug}.py`, botToPythonFile(bot), `feat: add/update ${bot.displayName} (Python bot)`);
        } else if (lang === "java") {
          await pushFile(`${folder}/${slug}.java`, botToJavaFile(bot), `feat: add/update ${bot.displayName} (Java bot)`);
        } else {
          await pushFile(`${folder}/${slug}.json`, botToJsonFile(bot), `feat: add/update ${bot.displayName} bot`);
        }
        pushed++;
      } catch (e: any) {
        errors.push(`${bot.slug}: ${e.message}`);
      }
    }
  }

  // Push README
  const summary = `# DreamCo Empire OS — Bot Repository

> **${bots.length} total bots** across 45 divisions | All self-learning | Buddy Bot connected

## Bot Organization
| Folder | Count | Description |
|--------|-------|-------------|
| \`bots/python/\` | ${byLang.python.length} | Python-powered bots (FastAPI, PyTorch, LangChain, etc.) |
| \`bots/java/\` | ${byLang.java.length} | Java/Kotlin bots (Spring Boot, Android, Ktor, etc.) |
| \`bots/typescript/\` | ${byLang.typescript.length} | TypeScript/JS bots (React, Node.js, Next.js, etc.) |
| \`bots/general/\` | ${byLang.general.length} | Multi-domain business bots |

## Divisions
${[...new Set(bots.map(b => b.division))].map(d => `- **${d}**`).join("\n")}

## Quick Start
\`\`\`bash
# Python bot
python bots/python/buddy-bot.py

# Java bot
javac bots/java/BuddyBot.java && java BuddyBot

# Set your OpenAI key
export OPENAI_API_KEY=your_key_here
\`\`\`

## System
Built with DreamCo Empire OS — the world's most advanced autonomous AI empire.
`;

  try {
    await pushFile("README.md", summary, "docs: update README with bot organization");
  } catch (e: any) {
    errors.push(`README: ${e.message}`);
  }

  return { pushed, errors };
}

export async function getRepoInfo(): Promise<any> {
  return ghFetch(`/repos/${REPO_OWNER}/${REPO_NAME}`);
}

export async function getPullRequests(): Promise<any[]> {
  return ghFetch(`/repos/${REPO_OWNER}/${REPO_NAME}/pulls?state=all&per_page=100`);
}

export async function getRepoContents(path = ""): Promise<any[]> {
  try {
    const data = await ghFetch(`/repos/${REPO_OWNER}/${REPO_NAME}/contents/${path}`);
    return Array.isArray(data) ? data : [data];
  } catch {
    return [];
  }
}
