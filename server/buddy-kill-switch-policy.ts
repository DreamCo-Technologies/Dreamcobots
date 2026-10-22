import type { RequestHandler } from "express";

/** Missing state preserves the existing unlocked default; malformed state fails closed. */
export function buddyExecutionBlocked(setting: unknown): boolean {
  if (setting === null || setting === undefined) return false;
  if (typeof setting !== "object" || !("value" in setting)) return true;
  const value = (setting as { value?: unknown }).value;
  if (!value || typeof value !== "object" || !("enabled" in value)) return true;
  return (value as { enabled?: unknown }).enabled !== false;
}

/** Protect execution from enabled or unreadable safety state. Not an authorization gate. */
export function createBuddyExecutionGuard(readKillSwitch: () => Promise<unknown>): RequestHandler {
  return async (_req, res, next) => {
    try {
      const setting = await readKillSwitch();
      if (buddyExecutionBlocked(setting)) {
        res.status(423).json({ error: "Buddy execution is locked by the kill switch" });
        return;
      }
      next();
    } catch {
      res.status(503).json({ error: "Buddy execution safety state unavailable" });
    }
  };
}
