import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";

const nav = fs.readFileSync("website/nav.js", "utf8");

test("main navigation exposes owner operational surfaces", () => {
  for (const label of ["Actions Center", "Repository Revamp", "Test Center", "Data & Memory", "Security", "Models"]) {
    assert.ok(nav.includes(label), `missing navigation label: ${label}`);
  }
});

test("navigation does not embed raw secrets or credentials", () => {
  assert.doesNotMatch(nav, /sk-[A-Za-z0-9_-]{20,}/);
  assert.doesNotMatch(nav, /BEGIN PRIVATE KEY/);
});
