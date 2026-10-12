import assert from "node:assert/strict";
import test from "node:test";
import { readFileSync } from "node:fs";

const ontology = JSON.parse(readFileSync("config/generated/buddy_demand_ontology.json", "utf8"));
const ROUTE = new Set(["Reasoning","Coding","Data Analysis","Search and Retrieval","Research","Agents","Safety and Moderation","Multilingual and Translation","Image Generation","Image Editing","Video","Accessibility","Simulation","Forecasting"]);

test("every demand reason routes to a task category and capabilities", () => {
  assert.equal(ontology.reasons.length, 300);
  for (const reason of ontology.reasons) {
    assert.ok(ROUTE.has(reason.taskCategory), reason.id);
    assert.ok(reason.capabilities.length >= 1, reason.id);
    assert.equal(reason.providerCallExecuted, undefined);
  }
});
