import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";

const extension = JSON.parse(fs.readFileSync("config/masterbot-20-extension.json", "utf8"));
const featured = JSON.parse(fs.readFileSync("website/data/masterbot-homepage-featured.json", "utf8"));

test("20 MasterBots are registered as divisions 46-65", () => {
  assert.equal(extension.base_divisions, 45);
  assert.equal(extension.new_masterbots.length, 20);
  assert.deepEqual(extension.new_masterbots.map(x => x.id), Array.from({length: 20}, (_, i) => i + 46));
});

test("homepage contains the same 20 MasterBots", () => {
  assert.equal(featured.items.length, 20);
  assert.deepEqual(featured.items.map(x => x.id), extension.new_masterbots.map(x => x.id));
  assert.equal(new Set(featured.items.map(x => x.name)).size, 20);
});
