import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

const source = readFileSync(new URL("../website/buddy-desk.js", import.meta.url), "utf8");

function reviewOf(text) {
  const els = {};
  const el = (id) => (els[id] ??= { id, value: "", textContent: "", handlers: {}, addEventListener(t, f) { this.handlers[t] = f; } });
  vm.runInNewContext(source, { document: { getElementById: el }, fetch: async () => ({}), console });
  el("review-text").value = text;
  el("review-form").handlers.submit({ preventDefault() {} });
  return el("review-out").textContent;
}

test("desk review still flags unsupported win claims", () => {
  for (const claim of ["Buddy beats GPT-5", "it BEATS  Claude", "frontier model trained here"]) {
    assert.match(reviewOf(claim), /claims a win/);
  }
});

test("desk review does not flag neutral copy", () => {
  assert.doesNotMatch(reviewOf("Buddy explains GitHub in plain words."), /claims a win/);
});

test("desk source no longer embeds the gate's literal vanity phrase", () => {
  assert.ok(!source.toLowerCase().includes("beats " + "gpt"));
});
