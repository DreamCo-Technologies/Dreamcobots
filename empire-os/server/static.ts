import path from "path";
import { type Express } from "express";
import fs from "fs";
import express from "express";

// ---------------------------------------------------------------------------
// Production static file server
// ---------------------------------------------------------------------------

export function serveStatic(app: Express): void {
  const distPath = path.resolve(process.cwd(), "dist", "public");

  if (!fs.existsSync(distPath)) {
    console.warn(`[static] dist/public not found at ${distPath}. Run 'npm run build' first.`);
    app.get("*", (_req, res) => {
      res.status(503).send("Application not built. Run npm run build first.");
    });
    return;
  }

  app.use(express.static(distPath));

  // SPA fallback: serve index.html for any non-API route
  app.get("*", (req, res) => {
    if (req.path.startsWith("/api")) return res.status(404).json({ message: "Not found" });
    res.sendFile(path.join(distPath, "index.html"));
  });
}
