'use strict';

/**
 * DreamCo — Money Module Aggregator
 *
 * Single entry point that exposes all monetization engines.
 */

module.exports = {
  affiliateEngine: require('./affiliate_engine'),
  leadSeller: require('./lead_seller'),
  autoCheckout: require('./auto_checkout'),
  pricingEngine: require('./pricing_engine'),
};
