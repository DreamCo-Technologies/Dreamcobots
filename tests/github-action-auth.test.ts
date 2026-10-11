import assert from "node:assert/strict";
import test from "node:test";
import express from "express";
import { readFileSync } from "node:fs";
import { requireGitHubActionOwner, approvedWorkflow } from "../server/github-action-auth";

test("all GitHub mutations reject unconfigured, missing, wrong and malformed owner credentials", async () => {
  const old = process.env.OWNER_GITHUB_ACTION_TOKEN;
  const app = express();
  let writes = 0;
  app.use('/api/github', requireGitHubActionOwner);
  for (const path of ['sync','push-all','push-source','auto-sync','trigger-workflow']) {
    app.post('/api/github/' + path, (_req, res) => { writes++; res.json({ ok: true }); });
  }
  app.get('/api/github/status', (_req, res) => res.json({ ok: true }));
  const server = app.listen(0, '127.0.0.1');
  await new Promise<void>(resolve => server.once('listening', resolve));
  const address = server.address() as { port: number };
  const base = `http://127.0.0.1:${address.port}/api/github/`;
  try {
    for (const configured of [undefined, 'synthetic-owner-secret']) {
      if (configured) process.env.OWNER_GITHUB_ACTION_TOKEN = configured;
      else delete process.env.OWNER_GITHUB_ACTION_TOKEN;
      for (const path of ['sync','push-all','push-source','auto-sync','trigger-workflow']) {
        for (const authorization of ['', 'Bearer incorrect', 'synthetic-owner-secret', 'Bearer ééé']) {
          assert.equal((await fetch(base + path, { method: 'POST', headers: { authorization } })).status, 403);
        }
      }
    }
    assert.equal(writes, 0);
    assert.equal((await fetch(base + 'status')).status, 200);
    assert.equal((await fetch(base + 'sync', { method: 'POST', headers: { authorization: 'Bearer synthetic-owner-secret' } })).status, 200);
    assert.equal(writes, 1);
  } finally {
    if (old === undefined) delete process.env.OWNER_GITHUB_ACTION_TOKEN;
    else process.env.OWNER_GITHUB_ACTION_TOKEN = old;
    await new Promise<void>(resolve => server.close(() => resolve()));
  }
});

test('dispatch only accepts the reviewed dashboard workflow', () => {
  assert.equal(approvedWorkflow(undefined), '284581909');
  assert.equal(approvedWorkflow('dreamco-live-dashboard.yml'), '284581909');
  for (const value of ['deploy-buddy-pages.yml', '../other.yml', '', 284581909, null, {}]) assert.equal(approvedWorkflow(value), null);
});

test('owner middleware is installed before every GitHub write route', () => {
  const source = readFileSync('server/routes.ts', 'utf8');
  const gate = source.indexOf('app.use("/api/github", requireGitHubActionOwner)');
  assert.ok(gate >= 0);
  for (const path of ['sync','push-all','push-source','auto-sync','trigger-workflow']) assert.ok(source.indexOf(`app.post("/api/github/${path}"`) > gate);
});
