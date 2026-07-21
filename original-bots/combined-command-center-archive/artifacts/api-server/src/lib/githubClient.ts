import { logger } from "./logger";

export const GITHUB_ORG = "DreamCo-Technologies";
export const DREAMCOBOTS_REPO = "Dreamcobots";

const GITHUB_TOKEN = process.env.GITHUB_PERSONAL_ACCESS_TOKEN;

export async function ghFetch<T = unknown>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const res = await fetch(`https://api.github.com${path}`, {
    ...init,
    headers: {
      Authorization: GITHUB_TOKEN ? `token ${GITHUB_TOKEN}` : "",
      "User-Agent": "dreamco-dashboard",
      Accept: "application/vnd.github.v3+json",
      ...(init?.headers || {}),
    },
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`GitHub API ${res.status} ${path}: ${body.slice(0, 200)}`);
  }
  return (await res.json()) as T;
}

export async function ghFetchRaw(path: string): Promise<string | null> {
  try {
    const res = await fetch(`https://api.github.com${path}`, {
      headers: {
        Authorization: GITHUB_TOKEN ? `token ${GITHUB_TOKEN}` : "",
        "User-Agent": "dreamco-dashboard",
        Accept: "application/vnd.github.raw",
      },
    });
    if (!res.ok) return null;
    return await res.text();
  } catch (err) {
    logger.warn({ err, path }, "ghFetchRaw failed");
    return null;
  }
}
