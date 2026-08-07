import { z } from "zod";

export const USER_DEVICE_ACTIONS = [
  "copy",
  "paste",
  "share",
  "screenshot",
  "screen_record",
  "upload",
  "download",
  "open_app",
  "switch_app",
  "fill_form",
  "send_message",
  "post_content",
  "save_file",
  "move_file",
  "rename_file",
  "print",
] as const;

export const deviceActionGrantSchema = z.object({
  action: z.enum(USER_DEVICE_ACTIONS),
  allowed: z.boolean(),
  allowedApps: z.array(z.string().trim().min(2).max(160)).max(200).default([]),
  allowedDataClasses: z.array(z.enum(["public", "personal", "internal", "confidential", "restricted"])).default(["public", "personal"]),
  freshApprovalRequired: z.boolean().default(true),
  expiresAt: z.string().datetime().nullable().default(null),
}).strict();

export const personalDeviceAuthoritySchema = z.object({
  schema: z.literal("dreamco.personal_device_authority.v1"),
  ownerProfileId: z.string().trim().min(3).max(120),
  deviceId: z.string().trim().min(3).max(160),
  ownerConfirmed: z.literal(true),
  grants: z.array(deviceActionGrantSchema).max(100),
  controls: z.object({
    userCanPauseAllActions: z.literal(true),
    userCanRevokeAnyGrant: z.literal(true),
    actionLogVisibleToUser: z.literal(true),
    backgroundScreenCaptureDisabledByDefault: z.boolean().default(true),
    sensitiveFieldCaptureDisabledByDefault: z.boolean().default(true),
  }).strict(),
}).strict();

export const enterpriseBuddyPermissionSchema = z.object({
  schema: z.literal("dreamco.enterprise_buddy_permissions.v1"),
  tenantId: z.string().trim().min(3).max(120),
  roleId: z.string().trim().min(2).max(120),
  managedDeviceRequired: z.boolean().default(false),
  allowedActions: z.array(z.enum(USER_DEVICE_ACTIONS)).max(USER_DEVICE_ACTIONS.length),
  deniedActions: z.array(z.enum(USER_DEVICE_ACTIONS)).max(USER_DEVICE_ACTIONS.length),
  allowedApps: z.array(z.string().trim().min(2).max(160)).max(500).default([]),
  deniedApps: z.array(z.string().trim().min(2).max(160)).max(500).default([]),
  allowedDataClasses: z.array(z.enum(["public", "internal", "confidential", "restricted"])).default(["public", "internal"]),
  requireFreshApprovalForExternalShare: z.boolean().default(true),
  requireFreshApprovalForPublicPost: z.boolean().default(true),
  allowScreenshot: z.boolean().default(false),
  allowClipboardBridge: z.boolean().default(false),
  auditAllActions: z.boolean().default(true),
  employeeCanViewEffectivePolicy: z.boolean().default(true),
}).strict();

export function evaluateUserDeviceAction(
  authority: z.infer<typeof personalDeviceAuthoritySchema>,
  input: { action: typeof USER_DEVICE_ACTIONS[number]; app?: string; dataClass?: "public"|"personal"|"internal"|"confidential"|"restricted"; approvedNow?: boolean }
) {
  const grant = authority.grants.find((item) => item.action === input.action);
  if (!grant || !grant.allowed) return { allowed: false, reason: "action_not_granted" } as const;
  if (grant.expiresAt && new Date(grant.expiresAt).getTime() <= Date.now()) return { allowed: false, reason: "grant_expired" } as const;
  if (input.app && grant.allowedApps.length && !grant.allowedApps.includes(input.app)) return { allowed: false, reason: "app_not_granted" } as const;
  if (input.dataClass && !grant.allowedDataClasses.includes(input.dataClass)) return { allowed: false, reason: "data_class_not_granted" } as const;
  if (grant.freshApprovalRequired && !input.approvedNow) return { allowed: false, reason: "fresh_approval_required" } as const;
  return { allowed: true, reason: "owner_authorized" } as const;
}
