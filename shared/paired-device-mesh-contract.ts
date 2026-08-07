import { z } from "zod";

export const DEVICE_TRANSPORTS = ["wifi_lan", "bluetooth", "usb", "cloud_account", "browser_extension", "local_agent"] as const;
export const DEVICE_TYPES = ["desktop", "laptop", "phone", "tablet", "tv", "speaker", "printer", "camera", "wearable", "vehicle", "iot", "server", "other"] as const;

export const enrolledDeviceSchema = z.object({
  deviceId: z.string().trim().regex(/^[A-Za-z0-9_.:-]{3,160}$/),
  displayName: z.string().trim().min(2).max(160),
  deviceType: z.enum(DEVICE_TYPES),
  transports: z.array(z.enum(DEVICE_TRANSPORTS)).min(1).max(6),
  ownerApproved: z.literal(true),
  pairingEvidenceReference: z.string().trim().min(2).max(512),
  connectorId: z.string().trim().min(2).max(160),
  capabilities: z.array(z.string().trim().min(2).max(160)).max(200).default([]),
  allowedScopes: z.array(z.string().trim().min(2).max(160)).max(200).default([]),
  dangerousActions: z.array(z.string().trim().min(2).max(160)).max(100).default([]),
  online: z.boolean().default(false),
  lastHealthCheckAt: z.string().datetime().nullable().default(null),
  revokedAt: z.string().datetime().nullable().default(null),
}).strict();

export const deviceMeshActionSchema = z.object({
  actionId: z.string().trim().regex(/^[A-Za-z0-9_.:-]{3,160}$/),
  deviceId: z.string().trim().min(3).max(160),
  action: z.string().trim().min(2).max(240),
  scopes: z.array(z.string().trim().min(2).max(160)).min(1).max(50),
  preview: z.string().trim().min(3).max(2000),
  sideEffect: z.boolean().default(false),
  exactApproval: z.boolean().default(false),
  expiresAt: z.string().datetime(),
}).strict();

export function canExecuteDeviceAction(device: z.infer<typeof enrolledDeviceSchema>, action: z.infer<typeof deviceMeshActionSchema>) {
  if (device.revokedAt) return { allowed: false, reason: "device_revoked" } as const;
  if (!device.online) return { allowed: false, reason: "device_offline" } as const;
  if (device.deviceId !== action.deviceId) return { allowed: false, reason: "device_mismatch" } as const;
  const missingScopes = action.scopes.filter((scope) => !device.allowedScopes.includes(scope));
  if (missingScopes.length) return { allowed: false, reason: "scope_not_granted", missingScopes } as const;
  if (action.sideEffect && !action.exactApproval) return { allowed: false, reason: "fresh_approval_required" } as const;
  if (new Date(action.expiresAt).getTime() <= Date.now()) return { allowed: false, reason: "approval_expired" } as const;
  return { allowed: true, reason: "approved_enrolled_device" } as const;
}
