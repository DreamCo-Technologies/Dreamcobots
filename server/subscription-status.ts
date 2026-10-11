/** Customer-scoped subscription lookup. Identity/mapping must be server-authenticated. */
export async function subscriptionStatus(customerId: string | null, client: {
  subscriptions: { list: (params: {customer: string; status: 'all'; limit: number; expand: string[]}) => Promise<{data: Array<{customer: string | {id: string}; status: string; items?: {data?: Array<{price?: {product?: unknown}}>}}>; has_more?: boolean}> }
}) {
  if (!customerId || !/^cus_[A-Za-z0-9]+$/.test(customerId)) {
    return {hasActiveSubscription: false, tier: null, status: 'customer_unlinked'};
  }
  const result = await client.subscriptions.list({customer: customerId, status: 'all', limit: 100, expand: ['data.items.data.price.product']});
  const active = result.data.find(s => (typeof s.customer === 'string' ? s.customer : s.customer.id) === customerId && ['active','trialing'].includes(s.status));
  if (!active) return {hasActiveSubscription: false, tier: null, status: result.has_more ? 'incomplete' : 'inactive'};
  const product = active.items?.data?.[0]?.price?.product;
  const metadata = product && typeof product === 'object' && 'metadata' in product ? product.metadata as Record<string,unknown> : undefined;
  return {hasActiveSubscription: true, tier: typeof metadata?.tier === 'string' ? metadata.tier : null, status: 'active'};
}
