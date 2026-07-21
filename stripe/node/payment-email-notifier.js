const fs = require('fs');
const path = require('path');

const DEFAULT_DATA_DIR = path.resolve(process.cwd(), '../../data/stripe');
const EMAIL_EVENTS = new Set([
  'checkout.session.completed',
  'checkout.session.expired',
  'payment_intent.succeeded',
  'payment_intent.payment_failed',
  'invoice.paid',
  'invoice.payment_failed',
  'invoice.finalized',
  'invoice.voided',
  'customer.subscription.created',
  'customer.subscription.updated',
  'customer.subscription.deleted',
  'payment_link.created',
  'payment_link.updated',
  'charge.refunded',
  'refund.created',
  'refund.updated',
  'charge.dispute.created',
  'charge.dispute.updated',
  'charge.dispute.closed',
  'payout.created',
  'payout.paid',
  'payout.failed',
  'payout.canceled',
]);
const GITHUB_NOTIFICATIONS_ENABLED = ['1', 'true', 'yes'].includes(
  String(process.env.PAYMENT_GITHUB_NOTIFICATIONS || '').toLowerCase(),
);

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function safeReadJson(filePath, fallback) {
  try {
    if (!fs.existsSync(filePath)) return fallback;
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch (_error) {
    return fallback;
  }
}

function writeJson(filePath, data) {
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, `${JSON.stringify(data, null, 2)}\n`);
}

function parseRecipients() {
  const raw = process.env.STRIPE_PAYMENT_ALERT_EMAILS || process.env.PAYMENT_ALERT_EMAILS || '';
  return raw
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);
}

function maskEmail(email) {
  const [name, domain] = String(email).split('@');
  if (!name || !domain) return 'invalid-email';
  return `${name.slice(0, 2)}***@${domain}`;
}

function dollars(cents) {
  return ((Number(cents) || 0) / 100).toFixed(2);
}

function subjectFor(event) {
  const amount = `$${dollars(event.amountCents)} ${event.currency || 'USD'}`;
  switch (event.type) {
    case 'payment_intent.succeeded':
      return `DreamCo payment received: ${amount}`;
    case 'checkout.session.completed':
      return `DreamCo checkout completed: ${amount}`;
    case 'checkout.session.expired':
      return `DreamCo checkout expired: ${amount}`;
    case 'invoice.paid':
      return `DreamCo invoice paid: ${amount}`;
    case 'payment_intent.payment_failed':
      return `DreamCo payment failed: ${amount}`;
    case 'invoice.payment_failed':
      return `DreamCo invoice payment failed: ${amount}`;
    case 'invoice.finalized':
      return `DreamCo invoice finalized: ${amount}`;
    case 'invoice.voided':
      return `DreamCo invoice voided: ${amount}`;
    case 'customer.subscription.created':
      return 'DreamCo subscription created';
    case 'customer.subscription.updated':
      return 'DreamCo subscription updated';
    case 'customer.subscription.deleted':
      return 'DreamCo subscription canceled';
    case 'payment_link.created':
      return 'DreamCo payment link created';
    case 'payment_link.updated':
      return 'DreamCo payment link updated';
    case 'charge.refunded':
    case 'refund.created':
    case 'refund.updated':
      return `DreamCo refund event: ${amount}`;
    case 'charge.dispute.created':
      return `DreamCo dispute created: ${amount}`;
    case 'charge.dispute.updated':
      return `DreamCo dispute updated: ${amount}`;
    case 'charge.dispute.closed':
      return `DreamCo dispute closed: ${amount}`;
    case 'payout.created':
      return `DreamCo payout created: ${amount}`;
    case 'payout.paid':
      return `DreamCo payout paid: ${amount}`;
    case 'payout.failed':
      return `DreamCo payout failed: ${amount}`;
    case 'payout.canceled':
      return `DreamCo payout canceled: ${amount}`;
    default:
      return `DreamCo Stripe event: ${event.type}`;
  }
}

function buildNotice(event) {
  const recipients = parseRecipients();
  return {
    id: `${event.id || event.objectId || Date.now()}:payment-email`,
    createdAt: new Date().toISOString(),
    eventId: event.id,
    eventType: event.type,
    objectId: event.objectId,
    botId: event.botId,
    offerId: event.offerId,
    workflowId: event.workflowId,
    amountCents: event.amountCents,
    currency: event.currency,
    customerId: event.customerId,
    customerEmail: event.customerEmail,
    subject: subjectFor(event),
    recipientCount: recipients.length,
    recipientsMasked: recipients.map(maskEmail),
    provider: process.env.PAYMENT_EMAIL_PROVIDER || (process.env.RESEND_API_KEY ? 'resend' : 'outbox_only'),
    status: recipients.length ? 'queued' : 'blocked_missing_recipients',
  };
}

function githubRepo() {
  return process.env.PAYMENT_GITHUB_REPOSITORY || process.env.GITHUB_REPOSITORY || '';
}

function githubIssueTitle(notice) {
  return `[Payment Alert] ${notice.subject}`;
}

function githubIssueBody(notice) {
  return [
    '## Payment Alert',
    '',
    `- Event: ${notice.eventType}`,
    `- Bot: ${notice.botId}`,
    `- Offer: ${notice.offerId}`,
    `- Workflow: ${notice.workflowId}`,
    `- Amount: $${dollars(notice.amountCents)} ${notice.currency}`,
    `- Customer: ${notice.customerEmail || notice.customerId || 'unknown'}`,
    `- Stripe object: ${notice.objectId || 'unknown'}`,
    `- Created: ${notice.createdAt}`,
    '',
    'This notification was generated by the DreamCo Stripe webhook.',
  ].join('\n');
}

async function sendGitHubNotification(notice) {
  const repo = githubRepo();
  const token = process.env.PAYMENT_GITHUB_TOKEN || process.env.GITHUB_TOKEN;
  if (!GITHUB_NOTIFICATIONS_ENABLED) {
    return { status: 'github_disabled' };
  }
  if (!repo) {
    return { status: 'github_missing_repository' };
  }
  if (!token) {
    return { status: 'github_missing_token' };
  }

  const response = await fetch(`https://api.github.com/repos/${repo}/issues`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: 'application/vnd.github+json',
      'Content-Type': 'application/json',
      'X-GitHub-Api-Version': '2022-11-28',
    },
    body: JSON.stringify({
      title: githubIssueTitle(notice),
      body: githubIssueBody(notice),
      labels: ['payment-alert', 'stripe'],
    }),
  });

  return {
    status: response.ok ? 'github_issue_created' : 'github_issue_failed',
    providerStatus: response.status,
  };
}

function readOutbox(dataDir = process.env.DREAMCO_STRIPE_DATA_DIR || DEFAULT_DATA_DIR) {
  return safeReadJson(path.join(dataDir, 'payment-email-outbox.json'), []);
}

function writeNotice(notice, dataDir = process.env.DREAMCO_STRIPE_DATA_DIR || DEFAULT_DATA_DIR) {
  const outboxPath = path.join(dataDir, 'payment-email-outbox.json');
  const outbox = readOutbox(dataDir);
  const existingIndex = outbox.findIndex((item) => item.id === notice.id);
  if (existingIndex >= 0) {
    outbox[existingIndex] = notice;
  } else {
    outbox.push(notice);
  }
  writeJson(outboxPath, outbox);
  return notice;
}

async function sendWithResend(notice, recipients) {
  if (!process.env.RESEND_API_KEY) {
    return { sent: false, status: 'queued_requires_resend_api_key' };
  }
  const from = process.env.PAYMENT_EMAIL_FROM || 'DreamCo Payments <payments@dreamco.ai>';
  const response = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${process.env.RESEND_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      from,
      to: recipients,
      subject: notice.subject,
      text: [
        notice.subject,
        '',
        `Event: ${notice.eventType}`,
        `Bot: ${notice.botId}`,
        `Offer: ${notice.offerId}`,
        `Workflow: ${notice.workflowId}`,
        `Amount: $${dollars(notice.amountCents)} ${notice.currency}`,
        `Customer: ${notice.customerEmail || notice.customerId || 'unknown'}`,
        `Stripe object: ${notice.objectId || 'unknown'}`,
      ].join('\n'),
    }),
  });
  return {
    sent: response.ok,
    status: response.ok ? 'sent' : 'send_failed',
    providerStatus: response.status,
  };
}

async function recordPaymentEmailNotice(event, dataDir = process.env.DREAMCO_STRIPE_DATA_DIR || DEFAULT_DATA_DIR) {
  if (!EMAIL_EVENTS.has(event.type)) {
    return null;
  }
  const recipients = parseRecipients();
  const notice = buildNotice(event);

  if (recipients.length && notice.provider === 'resend') {
    try {
      const result = await sendWithResend(notice, recipients);
      notice.status = result.status;
      notice.sentAt = result.sent ? new Date().toISOString() : null;
      notice.providerStatus = result.providerStatus || null;
    } catch (_error) {
      notice.status = 'send_failed';
    }
  } else if (recipients.length) {
    notice.status = 'queued_requires_email_provider';
  }

  try {
    const github = await sendGitHubNotification(notice);
    notice.githubStatus = github.status;
    notice.githubProviderStatus = github.providerStatus || null;
  } catch (_error) {
    notice.githubStatus = 'github_issue_failed';
  }

  return writeNotice(notice, dataDir);
}

module.exports = {
  EMAIL_EVENTS,
  buildNotice,
  parseRecipients,
  readOutbox,
  recordPaymentEmailNotice,
  sendGitHubNotification,
};
