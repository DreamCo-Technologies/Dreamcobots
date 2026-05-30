import type { Server } from "http";
import type { Express } from "express";
import { createServer as createViteServer } from "vite";
import path from "path";

// ---------------------------------------------------------------------------
// Vite dev server middleware for development mode
// ---------------------------------------------------------------------------

export async function setupVite(httpServer: Server, app: Express): Promise<void> {
  const vite = await createViteServer({
    configFile: path.resolve(process.cwd(), "vite.config.ts"),
    server: {
      middlewareMode: true,
      hmr: { server: httpServer },
    },
    appType: "spa",
  });

  app.use(vite.middlewares);
}
