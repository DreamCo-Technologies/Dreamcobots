import assert from 'node:assert/strict';
import { once } from 'node:events';
import test from 'node:test';
import express from 'express';

test('locked Express supports the Money OS JSON and routing contract', async () => {
  const app = express();
  app.use(express.json());
  app.get('/health', (_request, response) => response.json({ ok: true }));
  app.post('/api/run', (request, response) => response.status(202).json({ mode: request.body.mode }));
  const server = app.listen(0, '127.0.0.1');
  try {
    await once(server, 'listening');
    const url = `http://127.0.0.1:${server.address().port}`;
    assert.deepEqual(await (await fetch(`${url}/health`)).json(), { ok: true });
    const response = await fetch(`${url}/api/run`, { method: 'POST',
      headers: { 'content-type': 'application/json' }, body: JSON.stringify({ mode: 'dry-run' }) });
    assert.equal(response.status, 202);
    assert.deepEqual(await response.json(), { mode: 'dry-run' });
  } finally {
    server.closeAllConnections();
    await new Promise((resolve, reject) => server.close(error => error ? reject(error) : resolve()));
  }
});
