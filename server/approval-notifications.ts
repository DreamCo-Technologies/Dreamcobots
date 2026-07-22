import { randomUUID } from "node:crypto";
import { z } from "zod";

export const APPROVAL_CHANNELS = ["in_app", "email", "sms", "voice_call"] as const;
export type ApprovalChannel = typeof APPROVAL_CHANNELS[number];

const TOKEN_LIKE = /(?:github_pat_|ghs_|(?:sk|rk)_(?:live|test)_|BEGIN .*PRIVATE KEY|[A-Za-z0-9_-]{40,})/i;
const SAFE_REFERENCE = /^[a-z][a-z0-9_.:/-]{2,127}$/;

const safeText = (minimum: number, maximum: number) => z.string().trim().min(minimum).max(maximum).refine(
  (value) => !TOKEN_LIKE.test(value),
  "Approval notifications must not contain credentials or token-like values",
);

const timeZone = z.string().min(3).max(64).refine((value) => {
  try {
    new Intl.DateTimeFormat("en-US", { timeZone: value }).format();
    return true;
  } catch {
    return false;
  }
}, "Use a valid IANA timezone");

export const approvalNotificationRequestSchema = z.object({
  approvalRequestId: z.string().regex(/^approval-[a-zA-Z0-9-]{4,80}$/),
  userId: z.string().regex(/^[A-Za-z0-9_.:-]{2,80}$/),
  botSlug: z.string().regex(/^[a-z0-9][a-z0-9-]{1,79}$/),
  actionType: z.string().regex(/^[a-z][a-z0-9_]{2,63}$/),
  title: safeText(3, 100),
  summary: safeText(10, 500),
  risk: z.enum(["low", "medium", "high", "critical"]),
  expiresInSeconds: z.number().int().min(60).max(86_400).default(900),
}).strict();

export const notificationPreferencesSchema = z.object({
  channels: z.array(z.object({
    channel: z.enum(APPROVAL_CHANNELS),
    enabled: z.boolean(),
    verified: z.boolean(),
    destinationRef: z.string().min(3).max(128).refine(
      (value) => SAFE_REFERENCE.test(value) && !TOKEN_LIKE.test(value) && !value.includes("@"),
      "Use an opaque verified-contact reference, never an email address, phone number, or credential",
    ),
    explicitOptIn: z.boolean(),
  }).strict()).min(1).max(APPROVAL_CHANNELS.length),
  quietHours: z.object({
    enabled: z.boolean(),
    startHourLocal: z.number().int().min(0).max(23),
    endHourLocal: z.number().int().min(0).max(23),
    timezone: timeZone,
    criticalOverride: z.boolean().default(false),
  }).strict().optional(),
}).strict();

export type ApprovalNotificationRequest = z.infer<typeof approvalNotificationRequestSchema>;
export type NotificationPreferences = z.infer<typeof notificationPreferencesSchema>;

export interface ApprovalNotificationEnvelope {
  schema: "dreamco.approval_notification.v1";
  notificationId: string;
  approvalRequestId: string;
  userId: string;
  botSlug: string;
  actionType: string;
  channel: ApprovalChannel;
  destinationRef: string;
  title: string;
  summary: string;
  risk: ApprovalNotificationRequest["risk"];
  reviewPath: string;
  createdAt: string;
  expiresAt: string;
  oneActionOnly: true;
  containsSecrets: false;
}

export interface ApprovalNotificationPlan {
  schema: "dreamco.approval_notification_plan.v1";
  approvalRequestId: string;
  status: "ready_for_adapter_dispatch" | "in_app_only" | "no_verified_channel";
  notifications: ApprovalNotificationEnvelope[];
  skipped: Array<{ channel: ApprovalChannel; reason: string }>;
  providerConfiguration: {
    in_app: "native";
    email: "adapter_required";
    sms: "adapter_required";
    voice_call: "adapter_required";
  };
  policy: {
    verifiedDestinationRequired: true;
    explicitSmsAndCallOptInRequired: true;
    oneApprovalPerAction: true;
    rawContactDetailsReturned: false;
    credentialsAccepted: false;
  };
}

export interface ApprovalNotificationAdapter {
  readonly channel: ApprovalChannel;
  send(envelope: Readonly<ApprovalNotificationEnvelope>): Promise<{ providerMessageId: string }>;
}

export interface ApprovalNotificationReplayGuard {
  claim(notificationId: string, expiresAt: string): Promise<boolean>;
}

function quietHoursBlock(preferences: NotificationPreferences, request: ApprovalNotificationRequest, now: Date) {
  const quiet = preferences.quietHours;
  if (!quiet?.enabled || (request.risk === "critical" && quiet.criticalOverride)) return false;
  const hour = Number(new Intl.DateTimeFormat("en-US", {
    hour: "2-digit",
    hourCycle: "h23",
    timeZone: quiet.timezone,
  }).format(now));
  return quiet.startHourLocal < quiet.endHourLocal
    ? hour >= quiet.startHourLocal && hour < quiet.endHourLocal
    : hour >= quiet.startHourLocal || hour < quiet.endHourLocal;
}

export function createApprovalNotificationPlan(
  requestInput: ApprovalNotificationRequest,
  preferencesInput: NotificationPreferences,
  now = new Date(),
): ApprovalNotificationPlan {
  const request = approvalNotificationRequestSchema.parse(requestInput);
  const preferences = notificationPreferencesSchema.parse(preferencesInput);
  const seen = new Set<ApprovalChannel>();
  const notifications: ApprovalNotificationEnvelope[] = [];
  const skipped: ApprovalNotificationPlan["skipped"] = [];
  const quiet = quietHoursBlock(preferences, request, now);

  for (const preference of preferences.channels) {
    if (seen.has(preference.channel)) {
      skipped.push({ channel: preference.channel, reason: "duplicate_channel" });
      continue;
    }
    seen.add(preference.channel);
    if (!preference.enabled) {
      skipped.push({ channel: preference.channel, reason: "disabled_by_user" });
      continue;
    }
    if (!preference.verified) {
      skipped.push({ channel: preference.channel, reason: "destination_not_verified" });
      continue;
    }
    if (["sms", "voice_call"].includes(preference.channel) && !preference.explicitOptIn) {
      skipped.push({ channel: preference.channel, reason: "explicit_opt_in_required" });
      continue;
    }
    if (quiet && preference.channel !== "in_app") {
      skipped.push({ channel: preference.channel, reason: "quiet_hours" });
      continue;
    }
    notifications.push({
      schema: "dreamco.approval_notification.v1",
      notificationId: `approval-notice-${randomUUID()}`,
      approvalRequestId: request.approvalRequestId,
      userId: request.userId,
      botSlug: request.botSlug,
      actionType: request.actionType,
      channel: preference.channel,
      destinationRef: preference.destinationRef,
      title: request.title,
      summary: request.summary,
      risk: request.risk,
      reviewPath: `/approvals/${encodeURIComponent(request.approvalRequestId)}`,
      createdAt: now.toISOString(),
      expiresAt: new Date(now.getTime() + request.expiresInSeconds * 1000).toISOString(),
      oneActionOnly: true,
      containsSecrets: false,
    });
  }

  const hasExternal = notifications.some((notification) => notification.channel !== "in_app");
  return {
    schema: "dreamco.approval_notification_plan.v1",
    approvalRequestId: request.approvalRequestId,
    status: hasExternal ? "ready_for_adapter_dispatch" : notifications.length ? "in_app_only" : "no_verified_channel",
    notifications,
    skipped,
    providerConfiguration: {
      in_app: "native",
      email: "adapter_required",
      sms: "adapter_required",
      voice_call: "adapter_required",
    },
    policy: {
      verifiedDestinationRequired: true,
      explicitSmsAndCallOptInRequired: true,
      oneApprovalPerAction: true,
      rawContactDetailsReturned: false,
      credentialsAccepted: false,
    },
  };
}

export async function dispatchApprovalNotification(
  envelope: ApprovalNotificationEnvelope,
  adapter: ApprovalNotificationAdapter,
  replayGuard: ApprovalNotificationReplayGuard,
  now = new Date(),
) {
  if (adapter.channel !== envelope.channel) throw new Error("Notification adapter does not match the approved channel");
  if (now.getTime() >= Date.parse(envelope.expiresAt)) throw new Error("Approval notification has expired");
  if (!(await replayGuard.claim(envelope.notificationId, envelope.expiresAt))) {
    throw new Error("Approval notification has already been dispatched");
  }
  const receipt = await adapter.send(envelope);
  return {
    schema: "dreamco.approval_notification_receipt.v1",
    notificationId: envelope.notificationId,
    approvalRequestId: envelope.approvalRequestId,
    channel: envelope.channel,
    providerMessageId: receipt.providerMessageId,
    dispatchedAt: now.toISOString(),
    rawContactDetailsReturned: false,
  } as const;
}
