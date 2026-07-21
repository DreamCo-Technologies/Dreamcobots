/**
 * DreamCo Control Tower — Revenue Tracker
 *
 * Aggregates payment data from Stripe and PayPal.
 * Falls back gracefully when API keys are not configured.
 */

// ---------------------------------------------------------------------------
// Stripe
// ---------------------------------------------------------------------------

/**
 * Fetch total revenue and recent charges from Stripe.
 * @param {string} secretKey - Stripe secret key
 * @param {number} [limit=100] - Number of charges to fetch
 * @returns {Promise<{ total: number, entries: object[], error?: string }>}
 */
export async function getStripeRevenue(secretKey, limit = 100) {
  if (!secretKey) {
    return { total: 0, entries: [], error: 'Stripe secret key not configured.' };
  }
  try {
    const Stripe = (await import('stripe')).default;
    const stripe = new Stripe(secretKey);
    const paymentIntents = await stripe.paymentIntents.list({ limit });
    const entries = paymentIntents.data.map((p) => ({
      id: p.id,
      amount_usd: p.amount / 100,
      currency: p.currency,
      status: p.status,
      created: new Date(p.created * 1000).toISOString(),
      description: p.description || '',
    }));
    const total = entries
      .filter((e) => e.status === 'succeeded')
      .reduce((sum, e) => sum + e.amount_usd, 0);
    return { total: Math.round(total * 100) / 100, entries };
  } catch (err) {
    return { total: 0, entries: [], error: err.message };
  }
}

// ---------------------------------------------------------------------------
// PayPal
// ---------------------------------------------------------------------------

/**
 * Fetch PayPal transactions using the REST API.
 * @param {string} clientId
 * @param {string} clientSecret
 * @param {"sandbox"|"live"} [mode="sandbox"]
 * @returns {Promise<{ total: number, entries: object[], error?: string }>}
 */
export async function getPayPalRevenue(clientId, clientSecret, mode = 'sandbox') {
  if (!clientId || !clientSecret) {
    return { total: 0, entries: [], error: 'PayPal credentials not configured.' };
  }
  const baseUrl = mode === 'live' ? 'https://api-m.paypal.com' : 'https://api-m.sandbox.paypal.com';
  try {
    // Get access token
    const tokenResp = await fetch(`${baseUrl}/v1/oauth2/token`, {
      method: 'POST',
      headers: {
        Authorization: 'Basic ' + Buffer.from(`${clientId}:${clientSecret}`).toString('base64'),
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: 'grant_type=client_credentials',
    });
    const tokenData = await tokenResp.json();
    const accessToken = tokenData.access_token;

    // Fetch recent transactions (last 30 days)
    const endDate = new Date().toISOString();
    const startDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString();
    const txResp = await fetch(
      `${baseUrl}/v1/reporting/transactions?start_date=${startDate}&end_date=${endDate}&fields=all`,
      {
        headers: { Authorization: `Bearer ${accessToken}` },
      }
    );
    const txData = await txResp.json();

    const entries = (txData.transaction_details || []).map((t) => ({
      id: t.transaction_info?.transaction_id,
      amount_usd: parseFloat(t.transaction_info?.transaction_amount?.value || 0),
      status: t.transaction_info?.transaction_status,
      created: t.transaction_info?.transaction_initiation_date,
    }));
    const total = entries.filter((e) => e.status === 'S').reduce((sum, e) => sum + e.amount_usd, 0);
    return { total: Math.round(total * 100) / 100, entries };
  } catch (err) {
    return { total: 0, entries: [], error: err.message };
  }
}

// ---------------------------------------------------------------------------
// Aggregate
// ---------------------------------------------------------------------------

/**
 * Return a combined revenue summary from all configured payment providers.
 * @returns {Promise<{ total_usd: number, by_provider: object, timestamp: string }>}
 */
export async function getRevenueSummary() {
  const [stripe, paypal] = await Promise.all([
    getStripeRevenue(process.env.STRIPE_SECRET_KEY),
    getPayPalRevenue(
      process.env.PAYPAL_CLIENT_ID,
      process.env.PAYPAL_CLIENT_SECRET,
      process.env.PAYPAL_MODE || 'sandbox'
    ),
  ]);

  const total = (stripe.total || 0) + (paypal.total || 0);
  return {
    total_usd: Math.round(total * 100) / 100,
    by_provider: {
      stripe: { total: stripe.total, error: stripe.error },
      paypal: { total: paypal.total, error: paypal.error },
    },
    timestamp: new Date().toISOString(),
  };
}

export default { getStripeRevenue, getPayPalRevenue, getRevenueSummary };
