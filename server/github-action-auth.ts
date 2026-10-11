import { timingSafeEqual } from "node:crypto";
import type { RequestHandler } from "express";

/** Inbound owner authorization is separate from the server's GitHub credential. */
export const requireGitHubActionOwner: RequestHandler = (req, res, next) => {
  if (["GET", "HEAD", "OPTIONS"].includes(req.method)) return next();
  const expected = process.env.OWNER_GITHUB_ACTION_TOKEN;
  const match = /^Bearer ([^\s]+)$/i.exec(req.header("authorization") ?? "");
  const supplied = Buffer.from(match?.[1] ?? "");
  const configured = Buffer.from(expected ?? "");
  if (!configured.length || supplied.length !== configured.length || !timingSafeEqual(supplied, configured)) {
    res.status(403).json({ success: false, error: "GitHub actions require owner authorization." });
    return;
  }
  next();
};

export function approvedWorkflow(workflow: unknown): string | null {
  return workflow === undefined || workflow === "dreamco-live-dashboard.yml" ? "284581909" : null;
}
