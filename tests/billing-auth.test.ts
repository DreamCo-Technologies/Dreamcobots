import assert from "node:assert/strict";
import { billingOwnerAuthorized } from "../server/billing-auth.ts";

const previous = process.env.OWNER_BILLING_TOKEN;
process.env.OWNER_BILLING_TOKEN = "owner-secret";

assert.equal(billingOwnerAuthorized({ header: () => undefined }), false);
assert.equal(billingOwnerAuthorized({ header: () => "Bearer wrong-secret" }), false);
assert.equal(billingOwnerAuthorized({ header: () => "Bearer owner-secret" }), true);

process.env.OWNER_BILLING_TOKEN = previous;
console.log("billing auth passed");
