import { z } from "zod";
import { randomUUID } from "crypto";
import type { InsertPlatformConnection, PlatformConnection } from "@shared/schema";

export const AUTH_METHODS = [
  "oauth_pkce",
  "oauth_device",
  "api_key",
  "webhook_hmac",
  "passkey_webauthn",
  "browser_session_handoff",
  "oidc_saml",
  "custom_rest",
] as const;

const SECRET_METHODS = new Set(["api_key", "webhook_hmac", "custom_rest"]);
const SECRET_REFERENCE = /^[A-Za-z][A-Za-z0-9_.:/-]{2,127}$/;
const TOKEN_LIKE = /(?:github_pat_|ghs_|(?:sk|rk)_(?:live|test)_|BEGIN .*PRIVATE KEY)/i;

const httpsUrl = z.string().url().refine((value) => {
  const parsed = new URL(value);
  return parsed.protocol === "https:" && !parsed.username && !parsed.password;
}, "Use an official HTTPS URL without embedded credentials");

const secretReference = z.string().min(3).max(128).refine(
  (value) => SECRET_REFERENCE.test(value) && !TOKEN_LIKE.test(value),
  "Use a secret name or vault locator, never a credential value",
);

export const connectionPlanRequestSchema = z.object({
  platform: z.string().trim().min(2).max(64),
  name: z.string().trim().min(2).max(80),
  officialUrl: httpsUrl,
  authMethod: z.enum(AUTH_METHODS),
  requestedScopes: z.array(z.string().regex(/^[A-Za-z0-9._:/-]{1,80}$/)).max(40).default([]),
  secretProvider: z.enum(["environment", "os_keychain", "managed_vault"]).optional(),
  secretReference: secretReference.optional(),
}).superRefine((value, context) => {
  if (SECRET_METHODS.has(value.authMethod) && (!value.secretProvider || !value.secretReference)) {
    context.addIssue({
      code: z.ZodIssueCode.custom,
      message: "This authentication method requires an approved secret reference",
      path: ["secretReference"],
    });
  }
  if (!SECRET_METHODS.has(value.authMethod) && (value.secretProvider || value.secretReference)) {
    context.addIssue({
      code: z.ZodIssueCode.custom,
      message: "This authentication method must not receive a secret reference",
      path: ["secretReference"],
    });
  }
  if (value.secretReference && value.secretReference.length >= 32 && /^[A-Za-z0-9_-]+$/.test(value.secretReference)) {
    context.addIssue({
      code: z.ZodIssueCode.custom,
      message: "High-entropy values are not valid secret references",
      path: ["secretReference"],
    });
  }
  if (value.secretProvider === "environment" && value.secretReference && !/^[A-Z][A-Z0-9_]{2,127}$/.test(value.secretReference)) {
    context.addIssue({
      code: z.ZodIssueCode.custom,
      message: "Environment secret references must use an uppercase variable name",
      path: ["secretReference"],
    });
  }
});

export const connectionStatusUpdateSchema = z.object({
  status: z.enum([
    "planned",
    "sandbox_ready",
    "user_action_required",
    "connected",
    "disconnected",
    "error",
  ]),
});

export const signupHandoffRequestSchema = z.object({
  appName: z.string().trim().min(2).max(80),
  signupUrl: httpsUrl,
  accountPurpose: z.string().trim().min(5).max(240),
});

export type ConnectionPlanRequest = z.infer<typeof connectionPlanRequestSchema>;

export function toStoredConnection(input: ConnectionPlanRequest): InsertPlatformConnection {
  const officialOrigin = new URL(input.officialUrl).origin;
  return {
    platform: input.platform,
    name: input.name,
    callbackUrl: "",
    secretReference: input.secretReference ?? "",
    status: "planned",
    config: {
      policyVersion: "dreamco.connection_policy.v1",
      officialOrigin,
      authMethod: input.authMethod,
      requestedScopes: [...new Set(input.requestedScopes)],
      secretProvider: input.secretProvider ?? null,
      rawCredentialsAccepted: false,
      requiresUserApproval: true,
    },
  };
}

export function toPublicConnection(connection: PlatformConnection) {
  const config = connection.config && typeof connection.config === "object"
    ? connection.config as Record<string, unknown>
    : {};
  return {
    id: connection.id,
    platform: connection.platform,
    name: connection.name,
    status: connection.status,
    createdAt: connection.createdAt,
    officialOrigin: typeof config.officialOrigin === "string" ? config.officialOrigin : null,
    authMethod: typeof config.authMethod === "string" ? config.authMethod : "legacy",
    requestedScopes: Array.isArray(config.requestedScopes) ? config.requestedScopes : [],
    secretReferenceConfigured: Boolean(connection.secretReference),
    credentialStorage: "reference_only",
    rawCredentialsExposed: false,
    requiresUserApproval: config.requiresUserApproval !== false,
  };
}

export function createSignupHandoff(input: z.infer<typeof signupHandoffRequestSchema>) {
  const officialOrigin = new URL(input.signupUrl).origin;
  return {
    schema: "dreamco.buddy_signup_handoff.v1",
    handoffId: `signup-${randomUUID()}`,
    appName: input.appName,
    officialOrigin,
    accountPurpose: input.accountPurpose,
    status: "user_action_required",
    automaticSubmission: false,
    rawCredentialsAccepted: false,
    userPresenceGates: [
      "official_domain_review",
      "terms_and_privacy",
      "contact_verification",
      "identity_or_business_check",
      "captcha",
      "mfa_or_passkey",
      "payment",
      "account_recovery",
    ],
  };
}
