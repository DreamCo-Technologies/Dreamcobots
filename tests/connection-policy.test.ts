import assert from "node:assert/strict";
import test from "node:test";
import {
  connectionPlanRequestSchema,
  createSignupHandoff,
  signupHandoffRequestSchema,
  toPublicConnection,
  toStoredConnection,
} from "../server/connection-policy";
import type { PlatformConnection } from "../shared/schema";

test("connection plans store references rather than credential values", () => {
  const parsed = connectionPlanRequestSchema.parse({
    platform: "custom-api",
    name: "Client API",
    officialUrl: "https://api.example.com/docs",
    authMethod: "api_key",
    requestedScopes: ["records.read"],
    secretProvider: "environment",
    secretReference: "CLIENT_API_KEY",
  });
  const stored = toStoredConnection(parsed);
  assert.equal(stored.secretReference, "CLIENT_API_KEY");
  assert.equal(stored.callbackUrl, "");
  assert.equal(stored.status, "planned");
  assert.equal((stored.config as Record<string, unknown>).officialOrigin, "https://api.example.com");
});

test("token-shaped values and credential-bearing URLs are rejected", () => {
  const token = connectionPlanRequestSchema.safeParse({
    platform: "custom-api",
    name: "Client API",
    officialUrl: "https://api.example.com",
    authMethod: "api_key",
    requestedScopes: [],
    secretProvider: "managed_vault",
    secretReference: "sk_live_1234567890123456",
  });
  assert.equal(token.success, false);

  const opaqueToken = connectionPlanRequestSchema.safeParse({
    platform: "custom-api",
    name: "Client API",
    officialUrl: "https://api.example.com",
    authMethod: "api_key",
    requestedScopes: [],
    secretProvider: "managed_vault",
    secretReference: "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6",
  });
  assert.equal(opaqueToken.success, false);

  const embedded = connectionPlanRequestSchema.safeParse({
    platform: "custom-api",
    name: "Client API",
    officialUrl: "https://user:password@example.com",
    authMethod: "oauth_pkce",
    requestedScopes: [],
  });
  assert.equal(embedded.success, false);
});

test("public connection responses never expose secret references", () => {
  const row = {
    id: 7,
    platform: "custom-api",
    name: "Client API",
    callbackUrl: "https://private.example.com/callback?secret=value",
    secretReference: "CLIENT_API_KEY",
    status: "planned",
    config: {
      officialOrigin: "https://api.example.com",
      authMethod: "api_key",
      requestedScopes: ["records.read"],
      requiresUserApproval: true,
    },
    createdAt: new Date("2026-07-21T00:00:00Z"),
  } satisfies PlatformConnection;
  const publicValue = toPublicConnection(row);
  const serialized = JSON.stringify(publicValue);
  assert.equal(publicValue.secretReferenceConfigured, true);
  assert.equal(publicValue.rawCredentialsExposed, false);
  assert.equal(serialized.includes("CLIENT_API_KEY"), false);
  assert.equal(serialized.includes("secret=value"), false);
});

test("signup handoffs cannot submit protected steps", () => {
  const input = signupHandoffRequestSchema.parse({
    appName: "Client Workspace",
    signupUrl: "https://accounts.example.com/signup",
    accountPurpose: "Manage an approved client project",
  });
  const handoff = createSignupHandoff(input);
  assert.equal(handoff.automaticSubmission, false);
  assert.equal(handoff.rawCredentialsAccepted, false);
  assert.ok(handoff.userPresenceGates.includes("terms_and_privacy"));
  assert.ok(handoff.userPresenceGates.includes("captcha"));
  assert.ok(handoff.userPresenceGates.includes("payment"));
});
