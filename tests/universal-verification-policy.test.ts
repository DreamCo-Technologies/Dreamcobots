import assert from "node:assert/strict";
import test from "node:test";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { persistVerificationLog } from "../shared/universal-verification-diagnostics.js";
import { isVerificationRunSuccessful } from "../shared/universal-verification-policy.js";

test("quick mode passes completed selected checks without claiming merge readiness", () => {
  assert.equal(isVerificationRunSuccessful({
    mode: "quick",
    failed: 0,
    blocked: 0,
    mergeReady: false,
    productionReady: false,
  }), true);
});

test("quick mode fails any selected failure or blocked check", () => {
  assert.equal(isVerificationRunSuccessful({
    mode: "quick",
    failed: 1,
    blocked: 0,
    mergeReady: false,
    productionReady: false,
  }), false);
  assert.equal(isVerificationRunSuccessful({
    mode: "quick",
    failed: 0,
    blocked: 1,
    mergeReady: false,
    productionReady: false,
  }), false);
});

test("ci and full modes retain their stronger readiness gates", () => {
  assert.equal(isVerificationRunSuccessful({
    mode: "ci",
    failed: 0,
    blocked: 0,
    mergeReady: true,
    productionReady: false,
  }), true);
  assert.equal(isVerificationRunSuccessful({
    mode: "full",
    failed: 0,
    blocked: 0,
    mergeReady: true,
    productionReady: false,
  }), false);
});

test("verification diagnostics preserve complete failure output in an artifact-ready log", () => {
  const root = mkdtempSync(join(tmpdir(), "dreamco-verification-"));
  try {
    const output = "first line\\nnot ok 7 - a representative regression\\nfull stack details";
    const path = persistVerificationLog(root, "governed-tests", output);
    assert.equal(readFileSync(path, "utf8"), output);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test("verification diagnostics reject unsafe expectation IDs", () => {
  const root = mkdtempSync(join(tmpdir(), "dreamco-verification-"));
  try {
    assert.throws(() => persistVerificationLog(root, "../escape", "output"), /Invalid verification expectation ID/);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});
