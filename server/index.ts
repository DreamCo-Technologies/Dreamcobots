import express, { type Request, Response, NextFunction } from "express";
import { registerRoutes } from "./routes";
import { registerIntelligentRoutingRoutes } from "./intelligent-routing-routes";
import { serveStatic } from "./static";
import { createServer } from "http";
import { getUncachableStripeClient } from './stripeClient';
import { WebhookHandlers } from './webhookHandlers';
import { seedStripeProducts } from './seed-stripe-products';

const app = express();
const httpServer = createServer(app);
const processStartedAt = Date.now();

const publicExecutionOrigins = new Set([
  "https://dreamco-technologies.github.io",
  ...(process.env.BUDDY_PUBLIC_EXECUTION_ORIGINS || "")
    .split(",")
    .map((value) => value.trim())
    .filter(Boolean),
]);

declare module "http" {
  interface IncomingMessage {
    rawBody: unknown;
  }
}

async function initStripe() {
  if (!process.env.STRIPE_SECRET_KEY && !process.env.STRIPE_LIVE_SECRET_KEY) {
    console.warn('Stripe secrets are not configured; billing routes will remain unavailable.');
    return;
  }

  try {
    await getUncachableStripeClient();
    console.log('Stripe client configured.');

    seedStripeProducts()
      .then(() => console.log('Stripe products ready'))
      .catch((err: any) => console.warn('Stripe product seeding skipped:', err.message));
  } catch (error) {
    console.error('Failed to initialize Stripe:', error);
  }
}

app.use((req, res, next) => {
  const origin = req.headers.origin;
  if (origin && publicExecutionOrigins.has(origin)) {
    res.setHeader("Access-Control-Allow-Origin", origin);
    res.setHeader("Vary", "Origin");
    res.setHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
    res.setHeader("Access-Control-Allow-Headers", "Content-Type");
    res.setHeader("Access-Control-Max-Age", "600");
  }
  if (req.method === "OPTIONS") return res.status(204).end();
  return next();
});

app.get('/api/health', (_req, res) => {
  res.status(200).json({
    ok: true,
    service: 'dreamco-buddy',
    environment: process.env.NODE_ENV || 'development',
    uptimeSeconds: Math.floor((Date.now() - processStartedAt) / 1000),
    stripeConfigured: Boolean(process.env.STRIPE_SECRET_KEY || process.env.STRIPE_LIVE_SECRET_KEY),
    publicExecutionBridge: true,
    timestamp: new Date().toISOString(),
  });
});

app.post(
  '/api/stripe/webhook',
  express.raw({ type: 'application/json' }),
  async (req, res) => {
    const signature = req.headers['stripe-signature'];
    if (!signature) {
      return res.status(400).json({ error: 'Missing stripe-signature' });
    }

    try {
      const sig = Array.isArray(signature) ? signature[0] : signature;
      if (!Buffer.isBuffer(req.body)) {
        console.error('STRIPE WEBHOOK ERROR: req.body is not a Buffer');
        return res.status(500).json({ error: 'Webhook processing error' });
      }

      const event = await WebhookHandlers.processWebhook(req.body as Buffer, sig);
      res.status(200).json({ received: true, eventId: event.id, eventType: event.type });
    } catch (error: any) {
      console.error('Webhook error:', error.message);
      res.status(400).json({ error: 'Webhook processing error' });
    }
  }
);

app.use(
  express.json({
    verify: (req, _res, buf) => {
      req.rawBody = buf;
    },
  }),
);

app.use(express.urlencoded({ extended: false }));
registerIntelligentRoutingRoutes(app);

export function log(message: string, source = "express") {
  const formattedTime = new Date().toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    second: "2-digit",
    hour12: true,
  });

  console.log(`${formattedTime} [${source}] ${message}`);
}

app.use((req, res, next) => {
  const start = Date.now();
  const path = req.path;
  let capturedJsonResponse: Record<string, any> | undefined = undefined;

  const originalResJson = res.json;
  res.json = function (bodyJson, ...args) {
    capturedJsonResponse = bodyJson;
    return originalResJson.apply(res, [bodyJson, ...args]);
  };

  res.on("finish", () => {
    const duration = Date.now() - start;
    if (path.startsWith("/api")) {
      let logLine = `${req.method} ${path} ${res.statusCode} in ${duration}ms`;
      if (capturedJsonResponse) {
        logLine += ` :: ${JSON.stringify(capturedJsonResponse)}`;
      }

      log(logLine);
    }
  });

  next();
});

(async () => {
  await initStripe();
  await registerRoutes(httpServer, app);

  app.use((err: any, _req: Request, res: Response, next: NextFunction) => {
    const status = err.status || err.statusCode || 500;
    const message = err.message || "Internal Server Error";

    console.error("Internal Server Error:", err);

    if (res.headersSent) {
      return next(err);
    }

    return res.status(status).json({ message });
  });

  if (process.env.NODE_ENV === "production") {
    serveStatic(app);
  } else {
    const { setupVite } = await import("./vite");
    await setupVite(httpServer, app);
  }

  const port = parseInt(process.env.PORT || "5000", 10);
  httpServer.listen(
    {
      port,
      host: "0.0.0.0",
      reusePort: true,
    },
    () => {
      log(`serving on port ${port}`);
    },
  );

  if (process.env.DREAMCO_DISABLE_AUTO_SYNC !== "1") {
    import("./github-sync")
      .then(({ scheduleAutoSync }) => {
        scheduleAutoSync();
      })
      .catch((error: unknown) => {
        const message = error instanceof Error ? error.message : String(error);
        console.warn(`GitHub auto-sync scheduler unavailable: ${message}`);
      });
  }
})();