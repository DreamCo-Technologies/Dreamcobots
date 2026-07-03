import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { build } from "esbuild";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, "..");
const distDir = path.join(projectRoot, "dist");
const publicDir = path.join(distDir, "public");

await mkdir(publicDir, { recursive: true });

const placeholderHtml = `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>DreamCo Empire OS</title>
  </head>
  <body>
    <div id="root">Build completed.</div>
  </body>
</html>
`;

await writeFile(path.join(publicDir, "index.html"), placeholderHtml, "utf8");

await build({
  entryPoints: [path.join(projectRoot, "server", "index.ts")],
  bundle: true,
  platform: "node",
  format: "esm",
  target: "node20",
  outfile: path.join(distDir, "index.js"),
  packages: "external",
  sourcemap: true,
});
