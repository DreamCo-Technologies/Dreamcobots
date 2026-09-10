import test from "node:test";
import assert from "node:assert/strict";
import { getLocalTestEntitlement } from "../server/local-test-entitlement";

test("local test entitlement defaults to elite when enabled outside production", () => {
  const entitlement = getLocalTestEntitlement({
    NODE_ENV: "development",
    DREAMCO_ENABLE_LOCAL_TEST_ACCOUNT: "1",
    DREAMCO_LOCAL_TEST_OWNER: "irean jordan",
  });

  assert.equal(entitlement?.hasActiveSubscription, true);
  assert.equal(entitlement?.tier, "elite");
  assert.equal(entitlement?.source, "local_test_entitlement");
  assert.equal(entitlement?.isTestEntitlement, true);
});

test("local test entitlement accepts valid lower tiers for feature-gate testing", () => {
  const entitlement = getLocalTestEntitlement({
    NODE_ENV: "test",
    DREAMCO_ENABLE_LOCAL_TEST_ACCOUNT: "true",
    DREAMCO_LOCAL_TEST_OWNER: "irean jordan",
    DREAMCO_LOCAL_TEST_TIER: "pro",
  });

  assert.equal(entitlement?.tier, "pro");
});

test("local test entitlement never activates in production", () => {
  const entitlement = getLocalTestEntitlement({
    NODE_ENV: "production",
    DREAMCO_ENABLE_LOCAL_TEST_ACCOUNT: "1",
    DREAMCO_LOCAL_TEST_TIER: "elite",
  });

  assert.equal(entitlement, null);
});
