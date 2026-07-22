import type {
  ApprovalChannel,
  ApprovalNotificationAdapter,
  ApprovalNotificationEnvelope,
} from "./approval-notifications";

export type SecretResolver = (reference: string) => string | undefined;

export type WebhookAdapterConfig = {
  id: string;
  endpoint: string;
  secretReference?: string;
  timeoutMs?: number;
};

function validatedEndpoint(value: string) {
  const endpoint = new URL(value);
  const localhost = ["localhost", "127.0.0.1", "::1"].includes(endpoint.hostname);
  if (endpoint.protocol !== "https:" && !(localhost && endpoint.protocol === "http:")) {
    throw new Error("Outbound adapters require HTTPS, except for a localhost sandbox");
  }
  if (endpoint.username || endpoint.password) throw new Error("Adapter URLs must not contain credentials");
  return endpoint;
}

function validatedSecretReference(value: string | undefined) {
  if (!value) return undefined;
  if (!/^[A-Z][A-Z0-9_]{2,127}$/.test(value)) {
    throw new Error("Adapter secret references must be uppercase environment variable names");
  }
  return value;
}

export class SecureJsonWebhookAdapter {
  readonly id: string;
  readonly endpoint: URL;
  readonly secretReference?: string;
  readonly timeoutMs: number;

  constructor(
    config: WebhookAdapterConfig,
    private readonly resolveSecret: SecretResolver = (reference) => process.env[reference],
    private readonly fetchImplementation: typeof fetch = fetch,
  ) {
    this.id = config.id;
    this.endpoint = validatedEndpoint(config.endpoint);
    this.secretReference = validatedSecretReference(config.secretReference);
    this.timeoutMs = Math.min(Math.max(config.timeoutMs ?? 8_000, 250), 30_000);
  }

  async send(payload: Readonly<Record<string, unknown>>, idempotencyKey: string) {
    const secret = this.secretReference ? this.resolveSecret(this.secretReference) : undefined;
    if (this.secretReference && !secret) throw new Error(`Secret reference ${this.secretReference} is not configured`);

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeoutMs);
    try {
      const response = await this.fetchImplementation(this.endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Idempotency-Key": idempotencyKey,
          ...(secret ? { Authorization: `Bearer ${secret}` } : {}),
        },
        body: JSON.stringify(payload),
        redirect: "error",
        signal: controller.signal,
      });
      if (!response.ok) throw new Error(`Adapter ${this.id} returned HTTP ${response.status}`);
      const contentLength = Number(response.headers.get("content-length") || 0);
      if (contentLength > 1_000_000) throw new Error(`Adapter ${this.id} response exceeded 1 MB`);
      const body = await response.text();
      if (body.length > 1_000_000) throw new Error(`Adapter ${this.id} response exceeded 1 MB`);
      let parsed: Record<string, unknown> = {};
      if (body) {
        try {
          parsed = JSON.parse(body) as Record<string, unknown>;
        } catch {
          parsed = {};
        }
      }
      return {
        adapterId: this.id,
        providerMessageId: String(parsed.providerMessageId || parsed.id || idempotencyKey),
        status: "accepted" as const,
      };
    } finally {
      clearTimeout(timer);
    }
  }
}

export class LocalApprovalInboxAdapter implements ApprovalNotificationAdapter {
  readonly channel = "in_app" as const;
  private readonly inbox = new Map<string, ApprovalNotificationEnvelope[]>();

  constructor(private readonly maximumPerDestination = 250) {}

  async send(envelope: Readonly<ApprovalNotificationEnvelope>) {
    const current = this.inbox.get(envelope.destinationRef) ?? [];
    current.push({ ...envelope });
    if (current.length > this.maximumPerDestination) current.splice(0, current.length - this.maximumPerDestination);
    this.inbox.set(envelope.destinationRef, current);
    return { providerMessageId: `local-inbox:${envelope.notificationId}` };
  }

  list(destinationRef: string) {
    return [...(this.inbox.get(destinationRef) ?? [])].map((item) => ({ ...item }));
  }
}

export class WebhookApprovalNotificationAdapter implements ApprovalNotificationAdapter {
  constructor(
    readonly channel: Exclude<ApprovalChannel, "in_app">,
    private readonly webhook: SecureJsonWebhookAdapter,
  ) {}

  async send(envelope: Readonly<ApprovalNotificationEnvelope>) {
    const result = await this.webhook.send(
      {
        schema: envelope.schema,
        notificationId: envelope.notificationId,
        approvalRequestId: envelope.approvalRequestId,
        destinationRef: envelope.destinationRef,
        channel: envelope.channel,
        title: envelope.title,
        summary: envelope.summary,
        risk: envelope.risk,
        reviewPath: envelope.reviewPath,
        expiresAt: envelope.expiresAt,
      },
      envelope.notificationId,
    );
    return { providerMessageId: result.providerMessageId };
  }
}

export function outboundAdapterReadiness(env: NodeJS.ProcessEnv = process.env) {
  const channels = {
    in_app: { status: "ready", adapter: "LocalApprovalInboxAdapter" },
    email: {
      status: env.BUDDY_EMAIL_WEBHOOK_URL ? "configured" : "configuration_required",
      adapter: "SecureJsonWebhookAdapter",
      endpointReference: "BUDDY_EMAIL_WEBHOOK_URL",
    },
    sms: {
      status: env.BUDDY_SMS_WEBHOOK_URL ? "configured" : "configuration_required",
      adapter: "SecureJsonWebhookAdapter",
      endpointReference: "BUDDY_SMS_WEBHOOK_URL",
    },
    voice_call: {
      status: env.BUDDY_VOICE_CALL_WEBHOOK_URL ? "configured" : "configuration_required",
      adapter: "SecureJsonWebhookAdapter",
      endpointReference: "BUDDY_VOICE_CALL_WEBHOOK_URL",
    },
    social_publish: {
      status: env.BUDDY_SOCIAL_WEBHOOK_URL ? "configured" : "configuration_required",
      adapter: "SecureJsonWebhookAdapter",
      endpointReference: "BUDDY_SOCIAL_WEBHOOK_URL",
    },
    custom_api: {
      status: "adapter_ready",
      adapter: "SecureJsonWebhookAdapter",
      configuration: "HTTPS endpoint plus optional environment secret reference",
    },
  } as const;
  return {
    schema: "dreamco.outbound_adapter_readiness.v1",
    channels,
    credentialsStoredInProfiles: false,
    secretReferencesOnly: true,
  };
}
