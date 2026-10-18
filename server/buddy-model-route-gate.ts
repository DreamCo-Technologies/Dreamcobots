import type { NextFunction, Request, Response } from "express";

import {
  type BuddyModelAccess,
  type BuddyModelCallerRole,
  getBuddyModelRouterConfig,
  resolveBuddyModelPlan,
} from "./buddy-model-policy";
import { readBuddyAuthSession } from "./oauth-login";

export const BUDDY_MODEL_ROUTE_GATE_SCHEMA = "dreamco.buddy_model_route_gate.v1";

/**
 * catalog: read-only model catalog/audit data.
 * selection: returns ranked model choices; allowlist-only unless the owner opts into discovery.
 * plan: benchmark/improvement/comparison/capability plans; never executes a provider call.
 * discovery_plan: official-catalog discovery planning; owner only, never executed.
 */
export type BuddyModelRouteKind = "catalog" | "selection" | "plan" | "discovery_plan";

/** Every model-related API route. tests/buddy-model-route-gate.test.ts fails if routes.ts drifts from this list. */
export const BUDDY_MODEL_ROUTES = [
  { method: "GET", path: "/api/buddy/model-benchmarks/catalog-audit", kind: "catalog" },
  { method: "GET", path: "/api/buddy/models/encyclopedia", kind: "catalog" },
  { method: "GET", path: "/api/buddy/models/connections", kind: "catalog" },
  { method: "GET", path: "/api/buddy/models/progress", kind: "catalog" },
  { method: "GET", path: "/api/buddy/models/council", kind: "selection" },
  { method: "GET", path: "/api/buddy/models/demand-ontology", kind: "catalog" },
  { method: "POST", path: "/api/buddy/models/demand-match", kind: "selection" },
  { method: "POST", path: "/api/buddy/models/select", kind: "selection" },
  { method: "POST", path: "/api/buddy/model-benchmarks/plan", kind: "plan" },
  { method: "POST", path: "/api/buddy/models/improvement-plan", kind: "plan" },
  { method: "GET", path: "/api/buddy/open-model-lab/catalog", kind: "catalog" },
  { method: "POST", path: "/api/buddy/open-model-lab/comparison-plan", kind: "plan" },
  { method: "POST", path: "/api/buddy/open-secure-ai-defense/model-discovery-plan", kind: "discovery_plan" },
  { method: "POST", path: "/api/buddy/route-capability", kind: "plan" },
] as const satisfies ReadonlyArray<{ method: "GET" | "POST"; path: string; kind: BuddyModelRouteKind }>;

export type BuddyModelCaller = {
  provider: string;
  subject: string;
  email?: string;
  role: BuddyModelCallerRole;
};

/** Owner identities are existing OAuth session identities, listed as provider:subject (comma separated). */
export function buddyModelOwnerSubjects(environment: NodeJS.ProcessEnv = process.env) {
  return new Set((environment.BUDDY_MODEL_OWNER_SUBJECTS || "")
    .split(",")
    .map((value) => value.trim())
    .filter((value) => /^[a-z]+:.+$/.test(value)));
}

export function resolveBuddyModelCaller(
  request: Request,
  environment: NodeJS.ProcessEnv = process.env,
): BuddyModelCaller | undefined {
  const session = readBuddyAuthSession(request);
  if (!session) return undefined;
  const role: BuddyModelCallerRole = buddyModelOwnerSubjects(environment).has(`${session.provider}:${session.sub}`)
    ? "owner"
    : "user";
  return { provider: session.provider, subject: session.sub, email: session.email, role };
}

function requestedModelPlan(request: Request) {
  const body = request.body && typeof request.body === "object" ? request.body as Record<string, unknown> : {};
  const query = (request.query || {}) as Record<string, unknown>;
  const source = { ...query, ...body };
  const premium = source.modelMode === "premium" || source.mode === "premium" || source.preferredTier === "premium";
  const approved = [
    source.approvePaidModelForThisRequest,
    source.approvePaidModelsForThisRequest,
    source.approvePaidModelsForThisRun,
  ].some((value) => value === true || value === "true");
  return {
    modelMode: premium ? "premium" as const : "free" as const,
    approvePaidModelForThisRequest: premium && approved,
  };
}

function deny(response: Response, status: number, code: string, error: string) {
  return response.status(status).json({ error, code, policy: BUDDY_MODEL_ROUTE_GATE_SCHEMA, providerCallExecuted: false });
}

/** Requires a signed-in caller (existing Buddy OAuth session) and runs the Buddy model policy before the route. */
export function buddyModelRouteGate(kind: BuddyModelRouteKind, environment: NodeJS.ProcessEnv = process.env) {
  return (request: Request, response: Response, next: NextFunction) => {
    const caller = resolveBuddyModelCaller(request, environment);
    if (!caller) return deny(response, 401, "caller_identity_required", "Sign in to Buddy before using model routes.");
    const body = request.body && typeof request.body === "object" ? request.body as Record<string, unknown> : {};
    if (caller.role !== "owner" && (kind === "discovery_plan" || body.allowDiscovery === true)) {
      return deny(response, 403, "discovery_owner_only", "Model discovery is available to the owner only.");
    }
    const policy = getBuddyModelRouterConfig().policy;
    if (policy.automatic_paid_upgrade !== false
      || policy.paid_use_requires_per_request_approval !== true
      || policy.free_fallback_required !== true) {
      return deny(response, 503, "model_policy_invariant_failed", "Buddy model policy is misconfigured; model routes are closed.");
    }
    let plan: ReturnType<typeof resolveBuddyModelPlan>;
    try {
      plan = resolveBuddyModelPlan(requestedModelPlan(request), environment);
    } catch (error) {
      return deny(response, 400, "model_policy_rejected", error instanceof Error ? error.message : "Invalid model request");
    }
    if (plan.automaticPaidUpgrade !== false || plan.providerCallExecuted !== false) {
      return deny(response, 503, "model_policy_invariant_failed", "Buddy model policy is misconfigured; model routes are closed.");
    }
    const access: BuddyModelAccess = { role: caller.role };
    response.locals.buddyModelAccess = { kind, caller, access, plan };
    response.setHeader("X-Buddy-Model-Policy", BUDDY_MODEL_ROUTE_GATE_SCHEMA);
    response.setHeader("X-Buddy-Model-Plan-Status", plan.status);
    return next();
  };
}

/** Caller access attached by buddyModelRouteGate; defaults to the least-privileged user role. */
export function buddyModelAccessFrom(response: Response): BuddyModelAccess {
  const role = response.locals.buddyModelAccess?.access?.role;
  return { role: role === "owner" ? "owner" : "user" };
}
