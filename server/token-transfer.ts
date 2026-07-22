import { randomUUID } from "crypto";
import { z } from "zod";

const SECRET_REFERENCE = /^[A-Za-z][A-Za-z0-9_.:/-]{2,127}$/;
const TOKEN_LIKE = /(?:github_pat_|ghs_|(?:sk|rk)_(?:live|test)_|BEGIN .*PRIVATE KEY)/i;
const SCOPE = /^[A-Za-z0-9._:/-]{1,80}$/;

const referenceName = z.string().min(3).max(128).refine(
  (value) => SECRET_REFERENCE.test(value) && !TOKEN_LIKE.test(value),
  "Use a secret name or vault locator, never a token value",
).refine(
  (value) => value.length < 32 || !/^[A-Za-z0-9_-]+$/.test(value),
  "High-entropy values are not valid secret references",
);

const httpsAudience = z.string().url().refine((value) => {
  const parsed = new URL(value);
  return parsed.protocol === "https:" && !parsed.username && !parsed.password && !parsed.search && !parsed.hash;
}, "Use an official HTTPS audience without embedded credentials, query parameters, or fragments");

const safeReason = z.string().trim().min(5).max(240).refine(
  (value) => !TOKEN_LIKE.test(value) && !/[A-Za-z0-9_-]{32,}/.test(value),
  "Transfer reason must not contain a token or credential value",
);

const sourceReferenceSchema = z.object({
  provider: z.enum(["environment", "os_keychain", "managed_vault"]),
  locator: referenceName,
}).strict();

const destinationReferenceSchema = z.object({
  provider: z.enum(["os_keychain", "managed_vault"]),
  locator: referenceName,
}).strict();

export const TOKEN_KINDS = [
  "api_token",
  "oauth_access_token",
  "oauth_refresh_token",
] as const;

export const tokenTransferPlanRequestSchema = z.object({
  connectorId: z.string().regex(/^[a-z][a-z0-9-]{2,63}$/),
  tokenKind: z.enum(TOKEN_KINDS),
  source: sourceReferenceSchema,
  destination: destinationReferenceSchema,
  sourceAudience: httpsAudience,
  destinationAudience: httpsAudience,
  scopes: z.array(z.string().regex(SCOPE)).max(40).default([]),
  reason: safeReason,
  ttlSeconds: z.number().int().min(30).max(300).default(120),
  explicitUserApproval: z.boolean().default(false),
}).strict().superRefine((value, context) => {
  if (value.source.provider === "environment" && !/^[A-Z][A-Z0-9_]{2,127}$/.test(value.source.locator)) {
    context.addIssue({
      code: z.ZodIssueCode.custom,
      path: ["source", "locator"],
      message: "Environment references must use an uppercase variable name",
    });
  }
  if (value.source.provider === value.destination.provider && value.source.locator === value.destination.locator) {
    context.addIssue({
      code: z.ZodIssueCode.custom,
      path: ["destination", "locator"],
      message: "Source and destination references must be different",
    });
  }
  if (new URL(value.sourceAudience).origin !== new URL(value.destinationAudience).origin) {
    context.addIssue({
      code: z.ZodIssueCode.custom,
      path: ["destinationAudience"],
      message: "Tokens cannot move between app audiences; authorize the destination app separately",
    });
  }
});

export type TokenTransferPlanRequest = z.infer<typeof tokenTransferPlanRequestSchema>;

export interface PrivateTokenTransferPlan {
  transferId: string;
  connectorId: string;
  tokenKind: typeof TOKEN_KINDS[number];
  status: "approval_required" | "backend_vault_execution_required";
  audience: string;
  scopes: string[];
  reason: string;
  source: TokenTransferPlanRequest["source"];
  destination: TokenTransferPlanRequest["destination"];
  createdAt: string;
  expiresAt: string;
  explicitUserApproval: boolean;
}

export interface PublicTokenTransferPlan {
  schema: "dreamco.buddy_token_transfer.v1";
  transferId: string;
  connectorId: string;
  tokenKind: typeof TOKEN_KINDS[number];
  status: PrivateTokenTransferPlan["status"];
  audience: string;
  scopes: string[];
  reason: string;
  sourceProvider: TokenTransferPlanRequest["source"]["provider"];
  destinationProvider: TokenTransferPlanRequest["destination"]["provider"];
  sourceReferenceConfigured: true;
  destinationReferenceConfigured: true;
  createdAt: string;
  expiresAt: string;
  oneTime: true;
  sameAudienceRequired: true;
  rawTokenAccepted: false;
}

export function createPrivateTokenTransferPlan(
  input: TokenTransferPlanRequest,
  now = new Date(),
): PrivateTokenTransferPlan {
  const value = tokenTransferPlanRequestSchema.parse(input);
  const scopes = [...new Set(value.scopes)];
  return {
    transferId: `transfer-${randomUUID()}`,
    connectorId: value.connectorId,
    tokenKind: value.tokenKind,
    status: value.explicitUserApproval ? "backend_vault_execution_required" : "approval_required",
    audience: new URL(value.sourceAudience).origin,
    scopes,
    reason: value.reason,
    source: value.source,
    destination: value.destination,
    createdAt: now.toISOString(),
    expiresAt: new Date(now.getTime() + value.ttlSeconds * 1000).toISOString(),
    explicitUserApproval: value.explicitUserApproval,
  };
}

export function toPublicTokenTransferPlan(plan: PrivateTokenTransferPlan): PublicTokenTransferPlan {
  return {
    schema: "dreamco.buddy_token_transfer.v1",
    transferId: plan.transferId,
    connectorId: plan.connectorId,
    tokenKind: plan.tokenKind,
    status: plan.status,
    audience: plan.audience,
    scopes: plan.scopes,
    reason: plan.reason,
    sourceProvider: plan.source.provider,
    destinationProvider: plan.destination.provider,
    sourceReferenceConfigured: true,
    destinationReferenceConfigured: true,
    createdAt: plan.createdAt,
    expiresAt: plan.expiresAt,
    oneTime: true,
    sameAudienceRequired: true,
    rawTokenAccepted: false,
  };
}

export interface SecretVaultAdapter {
  readonly provider: TokenTransferPlanRequest["source"]["provider"];
  // Return a dedicated mutable buffer; the broker zeroes it after the write attempt.
  read(locator: string): Promise<Uint8Array>;
  // Implementations must copy the value into an atomic vault write before resolving.
  write(
    locator: string,
    value: Uint8Array,
    metadata: Readonly<{ connectorId: string; tokenKind: string; audience: string; scopes: string[] }>,
  ): Promise<void>;
}

export interface TransferReplayGuard {
  // Production implementations must claim atomically in a shared durable store.
  claim(transferId: string, expiresAt: string): Promise<boolean>;
}

export interface TokenTransferReceipt {
  schema: "dreamco.buddy_token_transfer_receipt.v1";
  transferId: string;
  connectorId: string;
  status: "transferred";
  audience: string;
  tokenKind: string;
  sourceProvider: string;
  destinationProvider: string;
  transferredAt: string;
  rawTokenReturned: false;
}

export async function executeTokenTransfer(
  plan: PrivateTokenTransferPlan,
  sourceVault: SecretVaultAdapter,
  destinationVault: SecretVaultAdapter,
  replayGuard: TransferReplayGuard,
  onAudit?: (receipt: TokenTransferReceipt) => Promise<void> | void,
  now = new Date(),
): Promise<TokenTransferReceipt> {
  if (!plan.explicitUserApproval || plan.status !== "backend_vault_execution_required") {
    throw new Error("Explicit user approval is required before token transfer");
  }
  if (now.getTime() >= Date.parse(plan.expiresAt)) {
    throw new Error("Token transfer plan has expired");
  }
  if (sourceVault.provider !== plan.source.provider || destinationVault.provider !== plan.destination.provider) {
    throw new Error("Vault adapter does not match the approved transfer plan");
  }
  if (!(await replayGuard.claim(plan.transferId, plan.expiresAt))) {
    throw new Error("Token transfer plan has already been used");
  }

  let token: Uint8Array | undefined;
  try {
    token = await sourceVault.read(plan.source.locator);
    if (token.byteLength < 1 || token.byteLength > 65_536) {
      throw new Error("Source vault returned an invalid token payload");
    }
    await destinationVault.write(plan.destination.locator, token, {
      connectorId: plan.connectorId,
      tokenKind: plan.tokenKind,
      audience: plan.audience,
      scopes: [...plan.scopes],
    });
    const receipt: TokenTransferReceipt = {
      schema: "dreamco.buddy_token_transfer_receipt.v1",
      transferId: plan.transferId,
      connectorId: plan.connectorId,
      status: "transferred",
      audience: plan.audience,
      tokenKind: plan.tokenKind,
      sourceProvider: plan.source.provider,
      destinationProvider: plan.destination.provider,
      transferredAt: now.toISOString(),
      rawTokenReturned: false,
    };
    await onAudit?.(receipt);
    return receipt;
  } finally {
    token?.fill(0);
  }
}
