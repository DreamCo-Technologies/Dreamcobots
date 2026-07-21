import { createServer as createViteServer } from "vite";
import path from "path";
// ---------------------------------------------------------------------------
// Vite dev server middleware for development mode
// ---------------------------------------------------------------------------
export async function setupVite(httpServer, app) {
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
