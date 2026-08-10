import assert from "node:assert/strict";
import test from "node:test";

import { PersonalDataFabric } from "../server/personal-data-fabric";

const SHA = "a".repeat(64);

function sample(overrides: Record<string, unknown> = {}) {
  return {
    ownerId: "owner-1",
    dataClass: "notes" as const,
    title: "DreamCo idea notes",
    source: "manual upload",
    mimeType: "text/markdown",
    byteLength: 120,
    sha256Hex: SHA,
    userSelectedStorageRef: "local://DreamCo/notes/idea.md",
    consentScope: "Use this note to personalize Buddy for DreamCo planning.",
    sensitivity: "private" as const,
    retention: "until_user_deletes" as const,
    tags: ["dreamco", "ideas"],
    ...overrides,
  };
}

test("personal data fabric keeps storage user-selected and searchable", () => {
  const fabric = new PersonalDataFabric();
  const record = fabric.createRecord(sample());
  assert.equal(record.storageRef, "local://DreamCo/notes/idea.md");
  assert.equal(fabric.search("owner-1", "dreamco").length, 1);
  assert.equal(fabric.search("owner-2", "dreamco").length, 0);
  assert.equal(fabric.summary("owner-1").cloudCopyDefault, false);
});

test("personal data exports metadata without silently copying raw bytes", () => {
  const fabric = new PersonalDataFabric();
  fabric.createRecord(sample());
  const manifest = fabric.exportOwnerManifest("owner-1");
  assert.equal(manifest.records.length, 1);
  assert.equal(manifest.rawBytesIncluded, false);
});

test("personal data can be deleted by the owning user", () => {
  const fabric = new PersonalDataFabric();
  const record = fabric.createRecord(sample());
  assert.equal(fabric.deleteRecord("owner-2", record.id), false);
  assert.equal(fabric.deleteRecord("owner-1", record.id), true);
  assert.equal(fabric.search("owner-1").length, 0);
});

test("connector revocation detaches imported records without destroying user storage", () => {
  const fabric = new PersonalDataFabric();
  const record = fabric.createRecord(sample({ appConnector: "example-app", source: "example-app export" }));
  assert.equal(fabric.revokeConnector("owner-1", "example-app"), 1);
  const updated = fabric.search("owner-1")[0];
  assert.equal(updated.id, record.id);
  assert.equal(updated.appConnector, undefined);
  assert.match(updated.source, /connector revoked/);
});
