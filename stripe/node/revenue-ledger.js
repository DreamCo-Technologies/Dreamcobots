const fs = require('fs');
const path = require('path');

const DEFAULT_DATA_DIR = path.resolve(process.cwd(), '../../data/stripe');

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function safeReadJson(filePath, fallback) {
  try {
    if (!fs.existsSync(filePath)) return fallback;
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch (error) {
    return fallback;
  }
}

function writeJson(filePath, data) {
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, `${JSON.stringify(data, null, 2)}\n`);
}

function cents(value) {
  return typeof value === 'number' ? value : 0;
}

function dollars(value) {
  return (cents(value) / 100).toFixed(2);
}

function isoNow() {
  return new Date().toISOString();
}

function normalizeEvent(event) {
  const object = event.data && event.data.object ? event.data.object : {};
  const metadata = object.metadata || {};

  const amount = cents(object.amount_total)
    || cents(object.amount_paid)
    || cents(object.amount_received)
    || cents(object.amount)
    || cents(object.total)
    || 0;

  return {
    id: event.id,
    type: event.type,
    createdAt: event.created ? new Date(event.created * 1000).toISOString() : isoNow(),
    objectId: object.id || null,
    objectType: object.object || null,
    amountCents: amount,
    currency: (object.currency || 'usd').toUpperCase(),
    customerId: object.customer || object.customer_id || null,
    customerEmail: object.customer_email || object.receipt_email || null,
    subscriptionId: object.subscription || null,
    paymentIntentId: object.payment_intent || object.id || null,
    status: object.status || null,
    botId: metadata.bot_id || metadata.botId || 'unassigned',
    offerId: metadata.offer_id || metadata.offerId || 'unassigned',
    workflowId: metadata.workflow_id || metadata.workflowId || 'unassigned',
    source: metadata.source || 'stripe_webhook',
    rawObject: object,
  };
}

class RevenueLedger {
  constructor(dataDir = process.env.DREAMCO_STRIPE_DATA_DIR || DEFAULT_DATA_DIR) {
    this.dataDir = dataDir;
    this.eventsPath = path.join(dataDir, 'events.json');
    this.summaryPath = path.join(dataDir, 'summary.json');
    this.botSummaryPath = path.join(dataDir, 'bot-summary.json');
  }

  readEvents() {
    return safeReadJson(this.eventsPath, []);
  }

  recordEvent(event) {
    const normalized = normalizeEvent(event);
    const events = this.readEvents();
    const existingIndex = events.findIndex((item) => item.id === normalized.id);

    if (existingIndex >= 0) {
      events[existingIndex] = normalized;
    } else {
      events.push(normalized);
    }

    events.sort((a, b) => a.createdAt.localeCompare(b.createdAt));
    writeJson(this.eventsPath, events);
    this.writeSummaries(events);
    return normalized;
  }

  writeSummaries(events = this.readEvents()) {
    const summary = {
      generatedAt: isoNow(),
      totalEvents: events.length,
      checkoutCompleted: 0,
      paymentSucceeded: 0,
      paymentFailed: 0,
      invoicePaid: 0,
      invoiceFailed: 0,
      invoiceFinalized: 0,
      invoiceVoided: 0,
      subscriptionsCreated: 0,
      subscriptionsUpdated: 0,
      subscriptionsCanceled: 0,
      paymentLinksCreated: 0,
      paymentLinksUpdated: 0,
      refunds: 0,
      refundedRevenueCents: 0,
      disputesCreated: 0,
      disputesUpdated: 0,
      disputesClosed: 0,
      disputedRevenueCents: 0,
      payoutsCreated: 0,
      payoutsPaid: 0,
      payoutsFailed: 0,
      payoutsCanceled: 0,
      grossRevenueCents: 0,
      failedRevenueCents: 0,
      byCurrency: {},
    };

    const byBot = {};

    for (const event of events) {
      const currency = event.currency || 'USD';
      if (!summary.byCurrency[currency]) {
        summary.byCurrency[currency] = { grossRevenueCents: 0, failedRevenueCents: 0 };
      }

      if (!byBot[event.botId]) {
        byBot[event.botId] = {
          botId: event.botId,
          events: 0,
          grossRevenueCents: 0,
          failedRevenueCents: 0,
          checkoutCompleted: 0,
          paymentSucceeded: 0,
          paymentFailed: 0,
          invoicePaid: 0,
        invoiceFailed: 0,
        refunds: 0,
        refundedRevenueCents: 0,
        disputesCreated: 0,
        disputedRevenueCents: 0,
        offers: {},
        workflows: {},
        };
      }

      const bot = byBot[event.botId];
      bot.events += 1;
      bot.offers[event.offerId] = (bot.offers[event.offerId] || 0) + 1;
      bot.workflows[event.workflowId] = (bot.workflows[event.workflowId] || 0) + 1;

      switch (event.type) {
        case 'checkout.session.completed':
          summary.checkoutCompleted += 1;
          bot.checkoutCompleted += 1;
          break;
        case 'payment_intent.succeeded':
          summary.paymentSucceeded += 1;
          bot.paymentSucceeded += 1;
          summary.grossRevenueCents += event.amountCents;
          summary.byCurrency[currency].grossRevenueCents += event.amountCents;
          bot.grossRevenueCents += event.amountCents;
          break;
        case 'payment_intent.payment_failed':
          summary.paymentFailed += 1;
          bot.paymentFailed += 1;
          summary.failedRevenueCents += event.amountCents;
          summary.byCurrency[currency].failedRevenueCents += event.amountCents;
          bot.failedRevenueCents += event.amountCents;
          break;
        case 'invoice.paid':
          summary.invoicePaid += 1;
          bot.invoicePaid += 1;
          summary.grossRevenueCents += event.amountCents;
          summary.byCurrency[currency].grossRevenueCents += event.amountCents;
          bot.grossRevenueCents += event.amountCents;
          break;
        case 'invoice.payment_failed':
          summary.invoiceFailed += 1;
          bot.invoiceFailed += 1;
          summary.failedRevenueCents += event.amountCents;
          summary.byCurrency[currency].failedRevenueCents += event.amountCents;
          bot.failedRevenueCents += event.amountCents;
          break;
        case 'invoice.finalized':
          summary.invoiceFinalized += 1;
          break;
        case 'invoice.voided':
          summary.invoiceVoided += 1;
          break;
        case 'customer.subscription.created':
          summary.subscriptionsCreated += 1;
          break;
        case 'customer.subscription.updated':
          summary.subscriptionsUpdated += 1;
          break;
        case 'customer.subscription.deleted':
          summary.subscriptionsCanceled += 1;
          break;
        case 'payment_link.created':
          summary.paymentLinksCreated += 1;
          break;
        case 'payment_link.updated':
          summary.paymentLinksUpdated += 1;
          break;
        case 'charge.refunded':
        case 'refund.created':
        case 'refund.updated':
          summary.refunds += 1;
          summary.refundedRevenueCents += event.amountCents;
          bot.refunds += 1;
          bot.refundedRevenueCents += event.amountCents;
          break;
        case 'charge.dispute.created':
          summary.disputesCreated += 1;
          summary.disputedRevenueCents += event.amountCents;
          bot.disputesCreated += 1;
          bot.disputedRevenueCents += event.amountCents;
          break;
        case 'charge.dispute.updated':
          summary.disputesUpdated += 1;
          break;
        case 'charge.dispute.closed':
          summary.disputesClosed += 1;
          break;
        case 'payout.created':
          summary.payoutsCreated += 1;
          break;
        case 'payout.paid':
          summary.payoutsPaid += 1;
          break;
        case 'payout.failed':
          summary.payoutsFailed += 1;
          break;
        case 'payout.canceled':
          summary.payoutsCanceled += 1;
          break;
        default:
          break;
      }
    }

    writeJson(this.summaryPath, summary);
    writeJson(this.botSummaryPath, Object.values(byBot));
    return { summary, byBot: Object.values(byBot) };
  }

  writeMarkdownReport(reportPath = path.resolve(process.cwd(), '../../reports/stripe-revenue-report.md')) {
    const events = this.readEvents();
    const { summary, byBot } = this.writeSummaries(events);
    const lines = [
      '# DreamCo Stripe Revenue Report',
      '',
      `Generated: ${summary.generatedAt}`,
      '',
      `- Total Stripe events tracked: ${summary.totalEvents}`,
      `- Gross tracked revenue: $${dollars(summary.grossRevenueCents)}`,
      `- Failed attempted revenue: $${dollars(summary.failedRevenueCents)}`,
      `- Checkout completions: ${summary.checkoutCompleted}`,
      `- Successful payments: ${summary.paymentSucceeded}`,
      `- Failed payments: ${summary.paymentFailed}`,
      `- Paid invoices: ${summary.invoicePaid}`,
      `- Failed invoices: ${summary.invoiceFailed}`,
      `- Finalized invoices: ${summary.invoiceFinalized}`,
      `- Voided invoices: ${summary.invoiceVoided}`,
      `- Subscriptions created: ${summary.subscriptionsCreated}`,
      `- Subscriptions updated: ${summary.subscriptionsUpdated}`,
      `- Subscriptions canceled: ${summary.subscriptionsCanceled}`,
      `- Payment links created: ${summary.paymentLinksCreated}`,
      `- Payment links updated: ${summary.paymentLinksUpdated}`,
      `- Refund events: ${summary.refunds}`,
      `- Refunded amount tracked: $${dollars(summary.refundedRevenueCents)}`,
      `- Disputes created: ${summary.disputesCreated}`,
      `- Disputed amount tracked: $${dollars(summary.disputedRevenueCents)}`,
      `- Payouts created: ${summary.payoutsCreated}`,
      `- Payouts paid: ${summary.payoutsPaid}`,
      `- Payouts failed: ${summary.payoutsFailed}`,
      `- Payouts canceled: ${summary.payoutsCanceled}`,
      '',
      '## Revenue By Bot',
      '',
      '| Bot | Events | Gross | Failed | Paid invoices | Failed invoices |',
      '| --- | ---: | ---: | ---: | ---: | ---: |',
    ];

    for (const bot of byBot.sort((a, b) => b.grossRevenueCents - a.grossRevenueCents)) {
      lines.push(`| ${bot.botId} | ${bot.events} | $${dollars(bot.grossRevenueCents)} | $${dollars(bot.failedRevenueCents)} | ${bot.invoicePaid} | ${bot.invoiceFailed} |`);
    }

    if (!byBot.length) {
      lines.push('| No bot revenue events yet | 0 | $0.00 | $0.00 | 0 | 0 |');
    }

    lines.push('', '## What To Fix If Revenue Is Zero', '');
    lines.push('- Confirm Stripe account is in live mode, not only test mode.');
    lines.push('- Confirm products, prices, checkout links, and subscriptions are live.');
    lines.push('- Confirm bots attach `bot_id`, `offer_id`, and `workflow_id` metadata to every Stripe object.');
    lines.push('- Confirm webhooks are configured and delivering to the production endpoint.');
    lines.push('- Confirm failed payment events are reviewed and followed up.');
    lines.push('- Confirm payouts are enabled and bank account verification is complete in Stripe.');

    ensureDir(path.dirname(reportPath));
    fs.writeFileSync(reportPath, `${lines.join('\n')}\n`);
    return reportPath;
  }
}

module.exports = { RevenueLedger, normalizeEvent };
