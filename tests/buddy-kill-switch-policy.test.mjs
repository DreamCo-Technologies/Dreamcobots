import assert from "node:assert/strict";
import test from "node:test";
import { readFileSync } from "node:fs";
import { buddyExecutionBlocked, createBuddyExecutionGuard } from "../server/buddy-kill-switch-policy.ts";

async function invoke(readSetting) {
  let nextCalls = 0;
  const res = {
    statusCode: 200,
    body: undefined,
    status(code) { this.statusCode = code; return this; },
    json(body) { this.body = body; return this; },
  };
  await createBuddyExecutionGuard(readSetting)({}, res, () => { nextCalls++; });
  return { status: res.statusCode, body: res.body, nextCalls };
}

test("missing setting preserves existing unlocked default", async () => {
  assert.equal(buddyExecutionBlocked(undefined), false);
  assert.deepEqual(await invoke(async () => undefined), { status: 200, body: undefined, nextCalls: 1 });
});

test("explicit false permits execution", async () => {
  assert.equal(buddyExecutionBlocked({ value: { enabled: false } }), false);
  assert.equal((await invoke(async () => ({ value: { enabled: false } }))).nextCalls, 1);
});

test("enabled kill switch blocks before the route", async () => {
  const result = await invoke(async () => ({ value: { enabled: true } }));
  assert.equal(result.status, 423);
  assert.equal(result.nextCalls, 0);
});

test("malformed persisted state fails closed", async () => {
  for (const state of [{ value: { enabled: "false" } }, { value: {} }, { value: null }, {}]) {
    assert.equal(buddyExecutionBlocked(state), true);
    const result = await invoke(async () => state);
    assert.equal(result.status, 423);
    assert.equal(result.nextCalls, 0);
  }
});

test("storage failure fails closed without exposing details", async () => {
  const result = await invoke(async () => { throw Error("database unavailable"); });
  assert.equal(result.status, 503);
  assert.equal(result.nextCalls, 0);
  assert.doesNotMatch(JSON.stringify(result.body), /database unavailable/);
});

test("sensitive routes are registered behind shared guard", () => {
  const source = readFileSync(new URL("../server/routes.ts", import.meta.url), "utf8");
  const guard = source.indexOf("app.use(BUDDY_HIGH_RISK_ROUTES, createBuddyExecutionGuard");
  assert.ok(guard >= 0);
  for (const route of ["/api/buddy/execute-code", "/api/buddy/agent-run", "/api/buddy/analyze-image"]) {
    assert.ok(guard < source.indexOf('app.post("' + route + '"'), route + " must be after guard");
  }
});
