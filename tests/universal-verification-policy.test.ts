import assert from "node:assert/strict";
import test from "node:test";
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
