import { randomUUID } from "node:crypto";
import type { RequestHandler, Response } from "express";

type RequestCounter = {
  total: number;
  failed: number;
  byStatus: Record<string, number>;
};

const counters: RequestCounter = {
  total: 0,
  failed: 0,
  byStatus: {},
};

function statusBucket(statusCode: number) {
  return `${Math.floor(statusCode / 100)}xx`;
}

function emitStructuredLog(payload: Record<string, unknown>) {
  console.log(JSON.stringify({ service: "dreamco-buddy", ...payload }));
}

export function observeRequests(): RequestHandler {
  return (req, res, next) => {
    const requestId = req.get("x-request-id") || randomUUID();
    const startedAt = Date.now();
    res.locals.requestId = requestId;
    res.setHeader("x-request-id", requestId);

    res.on("finish", () => {
      if (!req.path.startsWith("/api")) return;
      counters.total += 1;
      if (res.statusCode >= 500) counters.failed += 1;
      const bucket = statusBucket(res.statusCode);
      counters.byStatus[bucket] = (counters.byStatus[bucket] || 0) + 1;
      emitStructuredLog({
        event: "api_request",
        requestId,
        method: req.method,
        path: req.path,
        statusCode: res.statusCode,
        durationMs: Date.now() - startedAt,
      });
    });

    next();
  };
}

export function attachRequestIdToErrors(): RequestHandler {
  return (req, res, next) => {
    const originalJson = res.json.bind(res);
    res.json = (body: unknown) => {
      if (res.statusCode >= 400 && body && typeof body === "object" && !Array.isArray(body)) {
        return originalJson({ requestId: res.locals.requestId, ...body });
      }
      return originalJson(body);
    };
    next();
  };
}

type DatabaseProbe = (signal: AbortSignal) => Promise<unknown>;
let databaseProbe: DatabaseProbe | undefined;
let pendingProbe: { promise: Promise<boolean>; controller: AbortController } | undefined;

// Register only after the complete application routes have initialized.
export function setRuntimeReadiness(probe?: DatabaseProbe) {
  pendingProbe?.controller.abort();
  databaseProbe = probe;
}

export function isRuntimeInitialized() {
  return databaseProbe !== undefined;
}

export function requireRuntime(): RequestHandler {
  return (_req, res, next) => {
    if (!isRuntimeInitialized()) {
      res.status(503).json({ error: "Application runtime is unavailable" });
      return;
    }
    next();
  };
}

export function productionReadinessSnapshot(databaseReachable = false) {
  const databaseConfigured = Boolean(process.env.DATABASE_URL);
  const stripeConfigured = Boolean(process.env.STRIPE_SECRET_KEY || process.env.STRIPE_LIVE_SECRET_KEY);
  const stripeWebhookConfigured = Boolean(process.env.STRIPE_WEBHOOK_SECRET);
  const openaiConfigured = Boolean(
    process.env.AI_INTEGRATIONS_OPENAI_API_KEY ||
    process.env.OPENAI_API_KEY ||
    process.env.OPENAI_ADMIN_KEY,
  );
  return {
    ready: isRuntimeInitialized() && databaseReachable && databaseConfigured && stripeConfigured && stripeWebhookConfigured,
    checks: {
      runtimeInitialized: isRuntimeInitialized(),
      databaseReachable,
      databaseConfigured,
      stripeConfigured,
      stripeWebhookConfigured,
      openaiConfigured,
    },
    requestCounters: counters,
  };
}

export async function checkProductionReadiness() {
  if (!databaseProbe || !process.env.DATABASE_URL) return productionReadinessSnapshot();
  if (!pendingProbe) {
    const probe = databaseProbe;
    const controller = new AbortController();
    const operation = Promise.resolve().then(() => probe(controller.signal));
    let timer: ReturnType<typeof setTimeout>;
    const promise = Promise.race([
      operation.then(() => true, () => false),
      new Promise<boolean>(resolve => {
        timer = setTimeout(() => {
          controller.abort();
          resolve(false);
        }, 2000);
      }),
    ]).finally(() => clearTimeout(timer));
    const pending = { promise, controller };
    pendingProbe = pending;
    // Retain a timed-out operation until its cleanup settles. Even a faulty
    // adapter that ignores cancellation cannot accumulate more probes.
    const release = () => { if (pendingProbe === pending) pendingProbe = undefined; };
    void operation.then(release, release);
  }
  return productionReadinessSnapshot(await pendingProbe.promise);
}

export async function sendReadiness(res: Response) {
  const snapshot = await checkProductionReadiness();
  res.status(snapshot.ready ? 200 : 503).json(snapshot);
}
