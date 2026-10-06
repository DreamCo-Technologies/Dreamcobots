import assert from "node:assert/strict";
import { createHmac } from "node:crypto";
import type { AddressInfo } from "node:net";
import { after, before, describe, test } from "node:test";
import express, { type Request } from "express";

import { readAuthSession, registerOAuthLoginRoutes } from "../server/oauth-login.ts";

// Covers the session helpers in server/oauth-login.ts that the global /api guard (server/api-auth.ts) relies on.
const SESSION_SECRET = "test-session-secret-for-oauth-login";

function sealValue(payload: unknown, secret = SESSION_SECRET): string {
  const value = Buffer.from(JSON.stringify(payload)).toString("base64url");
  return `${value}.${createHmac("sha256", secret).update(value).digest("base64url")}`;
}
const now = () => Math.floor(Date.now() / 1000);
const requestWithCookie = (cookie?: string) => ({ headers: cookie === undefined ? {} : { cookie } }) as unknown as Request;

describe("readAuthSession", () => {
  const previous = process.env.AUTH_SESSION_SECRET;
  before(() => { process.env.AUTH_SESSION_SECRET = SESSION_SECRET; });
  after(() => {
    if (previous === undefined) delete process.env.AUTH_SESSION_SECRET;
    else process.env.AUTH_SESSION_SECRET = previous;
  });

  test("returns the verified, unexpired session from the buddy_auth_session cookie", () => {
    const payload = { provider: "google", sub: "user-1", email: "user@example.com", name: "User", exp: now() + 60 };
    assert.deepEqual(readAuthSession(requestWithCookie(`other=1; buddy_auth_session=${sealValue(payload)}`)), payload);
  });

  test("rejects missing, forged, tampered, expired, malformed, and exp-less sessions", () => {
    const valid = sealValue({ provider: "google", sub: "user-1", exp: now() + 60 });
    const [body, signature] = valid.split(".");
    const cases: Record<string, string | undefined> = {
      "no cookie header": undefined,
      "empty cookie header": "",
      "other cookie only": "buddy_oauth_state=abc",
      "wrong signing secret": `buddy_auth_session=${sealValue({ provider: "google", sub: "x", exp: now() + 60 }, "wrong-secret")}`,
      "tampered body": `buddy_auth_session=${Buffer.from(JSON.stringify({ provider: "google", sub: "admin", exp: now() + 60 })).toString("base64url")}.${signature}`,
      "extra segment": `buddy_auth_session=${body}.${signature}.extra`,
      "missing signature": `buddy_auth_session=${body}`,
      expired: `buddy_auth_session=${sealValue({ provider: "google", sub: "x", exp: now() - 1 })}`,
      "expires now": `buddy_auth_session=${sealValue({ provider: "google", sub: "x", exp: now() })}`,
      "no exp": `buddy_auth_session=${sealValue({ provider: "google", sub: "x" })}`,
      "string exp": `buddy_auth_session=${sealValue({ provider: "google", sub: "x", exp: String(now() + 60) })}`,
      "signed non-JSON body": (() => { const raw = Buffer.from("not json").toString("base64url"); return `buddy_auth_session=${raw}.${createHmac("sha256", SESSION_SECRET).update(raw).digest("base64url")}`; })(),
    };
    for (const [name, cookie] of Object.entries(cases)) assert.equal(readAuthSession(requestWithCookie(cookie)), undefined, name);
  });

  test("fails closed when AUTH_SESSION_SECRET is not configured", () => {
    const cookie = `buddy_auth_session=${sealValue({ provider: "google", sub: "user-1", exp: now() + 60 }, "")}`;
    delete process.env.AUTH_SESSION_SECRET;
    try {
      assert.equal(readAuthSession(requestWithCookie(cookie)), undefined);
    } finally {
      process.env.AUTH_SESSION_SECRET = SESSION_SECRET;
    }
  });
});

describe("GET /api/auth/session", () => {
  let server: import("node:http").Server;
  let base = "";
  const previous = process.env.AUTH_SESSION_SECRET;

  before(async () => {
    process.env.AUTH_SESSION_SECRET = SESSION_SECRET;
    const app = express();
    registerOAuthLoginRoutes(app);
    await new Promise<void>((resolve) => { server = app.listen(0, "127.0.0.1", () => resolve()); });
    base = `http://127.0.0.1:${(server.address() as AddressInfo).port}`;
  });

  after(async () => {
    await new Promise<void>((resolve) => server.close(() => resolve()));
    if (previous === undefined) delete process.env.AUTH_SESSION_SECRET;
    else process.env.AUTH_SESSION_SECRET = previous;
  });

  test("reports the signed-in profile only for a valid session", async () => {
    const cookie = `buddy_auth_session=${sealValue({ provider: "apple", sub: "user-2", email: "u2@example.com", exp: now() + 60 })}`;
    assert.deepEqual(await (await fetch(`${base}/api/auth/session`, { headers: { cookie } })).json(), {
      authenticated: true,
      provider: "apple",
      profile: { subject: "user-2", email: "u2@example.com" },
    });
    const expired = `buddy_auth_session=${sealValue({ provider: "apple", sub: "user-2", exp: now() - 1 })}`;
    assert.deepEqual(await (await fetch(`${base}/api/auth/session`, { headers: { cookie: expired } })).json(), { authenticated: false });
  });

  test("is rate limited per client (120 requests per minute)", async () => {
    let lastOk = 0;
    let limited = false;
    for (let i = 0; i < 130; i += 1) {
      const response = await fetch(`${base}/api/auth/session`);
      if (response.status === 200) { lastOk = i + 1; await response.arrayBuffer(); continue; }
      assert.equal(response.status, 429, `request ${i + 1}`);
      assert.match((await response.json()).error, /Too many session checks/);
      limited = true;
      break;
    }
    assert.ok(limited, "the session route must start returning 429 within 130 requests");
    // The previous test used 2 requests from the same client, normally inside this window.
    assert.ok(lastOk >= 118 && lastOk <= 120, `expected 118-120 allowed requests, got ${lastOk}`);
  });
});
