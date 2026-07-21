'use strict';

/**
 * DreamCo — Automated Checkout & Payment Processing
 *
 * Creates orders, processes payments (Stripe/PayPal/Crypto simulation),
 * applies discount codes, and generates invoices.
 */

const crypto = require('crypto');

/** In-memory order store: orderId → order. */
const orders = new Map();

/** Total revenue accumulator. */
let totalRevenue = 0;

/** Pre-loaded discount codes. */
const DISCOUNT_CODES = {
  DREAMCO10: { type: 'percent', value: 10, description: '10% off all orders' },
  DREAMCO25: { type: 'percent', value: 25, description: '25% off (seasonal)' },
  FLAT50: { type: 'fixed', value: 50, description: '$50 off orders over $200' },
  NEWUSER: { type: 'percent', value: 15, description: '15% off for new users' },
  VIP100: { type: 'fixed', value: 100, description: '$100 off VIP orders' },
};

/**
 * Create a new order.
 * @param {Object[]} items - Array of line items { name, price, quantity }.
 * @param {string} customerId - Customer identifier.
 * @param {'stripe'|'paypal'|'crypto'} paymentMethod - Payment method.
 * @returns {Object} The created order.
 */
function createOrder(items, customerId, paymentMethod) {
  if (!Array.isArray(items) || items.length === 0) {
    throw new Error('Order must contain at least one item.');
  }
  const validMethods = ['stripe', 'paypal', 'crypto'];
  if (!validMethods.includes(paymentMethod)) {
    throw new Error(`Invalid payment method. Must be one of: ${validMethods.join(', ')}`);
  }

  const orderId = `ord_${crypto.randomBytes(8).toString('hex')}`;
  const subtotal = items.reduce((sum, item) => sum + item.price * (item.quantity || 1), 0);
  const order = {
    orderId,
    customerId,
    items,
    subtotal: Number(subtotal.toFixed(2)),
    discount: 0,
    discountCode: null,
    total: Number(subtotal.toFixed(2)),
    paymentMethod,
    status: 'pending',
    paymentDetails: null,
    createdAt: new Date().toISOString(),
    paidAt: null,
  };
  orders.set(orderId, order);
  return order;
}

/**
 * Process payment for an order.
 * @param {string} orderId - The order identifier.
 * @param {Object} paymentDetails - Payment details (card, token, wallet).
 * @returns {Object} Payment result with transaction ID.
 */
function processPayment(orderId, paymentDetails) {
  const order = orders.get(orderId);
  if (!order) {
    throw new Error(`Order '${orderId}' not found.`);
  }
  if (order.status === 'paid') {
    throw new Error(`Order '${orderId}' is already paid.`);
  }

  // Simulate payment processing per processor
  const txnId = `txn_${crypto.randomBytes(10).toString('hex')}`;
  let processorResponse;

  if (order.paymentMethod === 'stripe') {
    processorResponse = {
      processor: 'stripe',
      transactionId: `ch_${crypto.randomBytes(12).toString('hex')}`,
      status: 'succeeded',
      amount: order.total,
      currency: 'usd',
    };
  } else if (order.paymentMethod === 'paypal') {
    processorResponse = {
      processor: 'paypal',
      transactionId: `PAY-${crypto.randomBytes(10).toString('hex').toUpperCase()}`,
      status: 'COMPLETED',
      amount: order.total,
      currency: 'USD',
    };
  } else {
    processorResponse = {
      processor: 'crypto',
      transactionId: `0x${crypto.randomBytes(32).toString('hex')}`,
      status: 'confirmed',
      amount: order.total,
      currency: 'USDC',
    };
  }

  order.status = 'paid';
  order.paymentDetails = { ...paymentDetails, txnId, processorResponse };
  order.paidAt = new Date().toISOString();
  totalRevenue += order.total;

  return { orderId, txnId, processorResponse, total: order.total };
}

/**
 * Apply a discount code to an order.
 * @param {string} orderId - The order identifier.
 * @param {string} code - Discount code string.
 * @returns {Object} Updated order with new total.
 */
function applyDiscount(orderId, code) {
  const order = orders.get(orderId);
  if (!order) {
    throw new Error(`Order '${orderId}' not found.`);
  }
  if (order.status === 'paid') {
    throw new Error('Cannot apply discount to a paid order.');
  }
  const discount = DISCOUNT_CODES[code.toUpperCase()];
  if (!discount) {
    throw new Error(`Discount code '${code}' is invalid or expired.`);
  }

  let discountAmount;
  if (discount.type === 'percent') {
    discountAmount = Number(((order.subtotal * discount.value) / 100).toFixed(2));
  } else {
    discountAmount = Math.min(discount.value, order.subtotal);
  }

  order.discount = discountAmount;
  order.discountCode = code.toUpperCase();
  order.total = Number((order.subtotal - discountAmount).toFixed(2));
  return order;
}

/**
 * Generate an invoice object for an order.
 * @param {string} orderId - The order identifier.
 * @returns {Object} Invoice data.
 */
function generateInvoice(orderId) {
  const order = orders.get(orderId);
  if (!order) {
    throw new Error(`Order '${orderId}' not found.`);
  }
  const invoiceId = `inv_${crypto.randomBytes(8).toString('hex')}`;
  return {
    invoiceId,
    orderId,
    customerId: order.customerId,
    items: order.items,
    subtotal: order.subtotal,
    discount: order.discount,
    discountCode: order.discountCode,
    total: order.total,
    status: order.status,
    paymentMethod: order.paymentMethod,
    issuedAt: new Date().toISOString(),
    dueAt:
      order.status === 'paid'
        ? null
        : new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
    paidAt: order.paidAt,
  };
}

/**
 * Get an order by ID.
 * @param {string} orderId - The order identifier.
 * @returns {Object|null} The order or null if not found.
 */
function getOrder(orderId) {
  return orders.get(orderId) || null;
}

/**
 * Get total checkout revenue.
 * @returns {{ total: number, orderCount: number }}
 */
function getRevenue() {
  return {
    total: Number(totalRevenue.toFixed(2)),
    orderCount: Array.from(orders.values()).filter((o) => o.status === 'paid').length,
  };
}

module.exports = {
  DISCOUNT_CODES,
  createOrder,
  processPayment,
  applyDiscount,
  generateInvoice,
  getOrder,
  getRevenue,
};
