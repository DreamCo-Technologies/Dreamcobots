import type { Request } from "express";
import { timingSafeEqual } from "node:crypto";

export function billingOwnerAuthorized(req: Pick<Request, "header">): boolean {
  const expected = process.env.OWNER_BILLING_TOKEN;
  const provided = req.header("authorization")?.replace(/^Bearer\s+/i, "") ?? "";
  if (!expected || !provided || expected.length !== provided.length) return false;
  return timingSafeEqual(Buffer.from(expected), Buffer.from(provided));
}
