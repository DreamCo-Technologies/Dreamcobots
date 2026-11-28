import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const migration = readFileSync(new URL("../migrations/0002_lead_engine_crm.sql", import.meta.url), "utf8");
const storage = readFileSync(new URL("../server/lead-engine-storage.ts", import.meta.url), "utf8");
const schema = readFileSync(new URL("../shared/schema.ts", import.meta.url), "utf8");

test("Lead Engine CRM tables enforce owner-scoped PostgreSQL row security", () => {
  for (const table of ["lead_engine_records", "lead_engine_activities"]) {
    assert.match(migration, new RegExp(`ALTER TABLE ${table} ENABLE ROW LEVEL SECURITY`, "i"));
    assert.match(migration, new RegExp(`ALTER TABLE ${table} FORCE ROW LEVEL SECURITY`, "i"));
    assert.match(migration, new RegExp(`CREATE POLICY ${table}_owner_isolation`, "i"));
  }
  assert.match(migration, /current_setting\('app\.owner_id', true\)/);
  assert.match(migration, /FOREIGN KEY \(owner_id, lead_id\)/);
});

test("Lead Engine storage sets transaction-local owner context before each operation", () => {
  assert.match(storage, /set_config\('app\.owner_id'/);
  assert.match(storage, /return db\.transaction\(async \(tx\)/);
  assert.match(storage, /parsedRecord\.ownerUserId !== parsedOwner/);
  for (const method of [
    "saveLeadEngineRecord",
    "getLeadEngineRecord",
    "listLeadEngineRecords",
    "appendLeadEngineActivity",
    "listLeadEngineActivities",
  ]) {
    assert.match(storage, new RegExp(`export async function ${method}\\(`));
    assert.match(storage.slice(storage.indexOf(`export async function ${method}`)), /withOwner\(/);
  }
});

test("Lead Engine database schema defines owner and idempotency indexes", () => {
  assert.match(schema, /export const leadEngineRecords = pgTable\("lead_engine_records"/);
  assert.match(schema, /lead_engine_records_owner_lead_uq/);
  assert.match(schema, /export const leadEngineActivities = pgTable\("lead_engine_activities"/);
  assert.match(schema, /lead_engine_activities_owner_event_uq/);
});

test("activity history is append-only at the database layer", () => {
  assert.match(migration, /BEFORE UPDATE OR DELETE ON lead_engine_activities/);
  assert.match(migration, /lead engine activity history is append-only/);
});
