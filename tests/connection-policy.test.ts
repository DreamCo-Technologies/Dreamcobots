import assert from "node:assert/strict";
import test from "node:test";
import {
  connectionPlanRequestSchema,
  createSignupHandoff,
  signupHandoffRequestSchema,
  toPublicConnection,
  toStoredConnection,
} from "../server/connection-policy";
import {
  createPrivateTokenTransferPlan,
  executeTokenTransfer,
  tokenTransferPlanRequestSchema,
  toPublicTokenTransferPlan,
  type SecretVaultAdapter,
  type TransferReplayGuard,
} from "../server/token-transfer";
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

test("token handoff accepts references only and blocks cross-app audiences", () => {
  const rawToken = tokenTransferPlanRequestSchema.safeParse({
    connectorId: "client-app",
    tokenKind: "api_token",
    source: { provider: "environment", locator: "CLIENT_API_TOKEN" },
    destination: { provider: "managed_vault", locator: "clients/client-app/api-token" },
    sourceAudience: "https://app.example.com",
    destinationAudience: "https://app.example.com",
    reason: "Move the approved token into managed storage.",
    explicitUserApproval: true,
    token: "sk_live_1234567890123456",
  });
  assert.equal(rawToken.success, false);

  const crossApp = tokenTransferPlanRequestSchema.safeParse({
    connectorId: "client-app",
    tokenKind: "oauth_access_token",
    source: { provider: "environment", locator: "CLIENT_ACCESS_TOKEN" },
    destination: { provider: "managed_vault", locator: "clients/client-app/access-token" },
    sourceAudience: "https://app.example.com",
    destinationAudience: "https://other.example.com",
    reason: "Move the approved token into managed storage.",
    explicitUserApproval: true,
  });
  assert.equal(crossApp.success, false);

  const tokenInReason = tokenTransferPlanRequestSchema.safeParse({
    connectorId: "client-app",
    tokenKind: "api_token",
    source: { provider: "environment", locator: "CLIENT_API_TOKEN" },
    destination: { provider: "managed_vault", locator: "clients/client-app/api-token" },
    sourceAudience: "https://app.example.com",
    destinationAudience: "https://app.example.com",
    reason: "Move sk_live_1234567890123456 into storage.",
    explicitUserApproval: true,
  });
  assert.equal(tokenInReason.success, false);
});

test("token handoff is one-time, clears source memory, and returns metadata only", async () => {
  const input = tokenTransferPlanRequestSchema.parse({
    connectorId: "client-app",
    tokenKind: "oauth_access_token",
    source: { provider: "environment", locator: "CLIENT_ACCESS_TOKEN" },
    destination: { provider: "managed_vault", locator: "clients/client-app/access-token" },
    sourceAudience: "https://app.example.com/oauth",
    destinationAudience: "https://app.example.com/api",
    scopes: ["profile.read"],
    reason: "Move the approved token into managed storage.",
    ttlSeconds: 60,
    explicitUserApproval: true,
  });
  const now = new Date("2026-07-21T12:00:00Z");
  const plan = createPrivateTokenTransferPlan(input, now);
  const publicPlan = toPublicTokenTransferPlan(plan);
  assert.equal(JSON.stringify(publicPlan).includes("CLIENT_ACCESS_TOKEN"), false);
  assert.equal(JSON.stringify(publicPlan).includes("clients/client-app/access-token"), false);

  const sourceBytes = new TextEncoder().encode("private-test-token");
  let destinationCopy = new Uint8Array();
  const sourceVault: SecretVaultAdapter = {
    provider: "environment",
    async read() { return sourceBytes; },
    async write() { throw new Error("Source vault is read-only"); },
  };
  const destinationVault: SecretVaultAdapter = {
    provider: "managed_vault",
    async read() { throw new Error("Destination read is unused"); },
    async write(_locator, value) { destinationCopy = Uint8Array.from(value); },
  };
  const claimed = new Set<string>();
  const replayGuard: TransferReplayGuard = {
    async claim(id) {
      if (claimed.has(id)) return false;
      claimed.add(id);
      return true;
    },
  };

  const receipt = await executeTokenTransfer(
    plan,
    sourceVault,
    destinationVault,
    replayGuard,
    undefined,
    new Date("2026-07-21T12:00:10Z"),
  );
  assert.equal(new TextDecoder().decode(destinationCopy), "private-test-token");
  assert.ok(sourceBytes.every((value) => value === 0));
  assert.equal(receipt.rawTokenReturned, false);
  assert.equal(JSON.stringify(receipt).includes("private-test-token"), false);
  await assert.rejects(
    executeTokenTransfer(plan, sourceVault, destinationVault, replayGuard, undefined, new Date("2026-07-21T12:00:20Z")),
    /already been used/,
  );
});
