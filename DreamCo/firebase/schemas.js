'use strict';

/**
 * DreamCo Firestore Schemas — 8 collection schemas for the Money OS.
 */

const deals = {
  collection: 'deals',
  fields: {
    id: 'string',
    name: 'string',
    source: 'string',
    type: 'string',
    category: 'string',
    price: 'number',
    current: 'number',
    resale: 'number',
    coupon: 'number',
    cashback: 'number',
    profit: 'number',
    effort: 'number',
    fast_payout: 'boolean',
    rank_score: 'number',
    created_at: 'timestamp',
    updated_at: 'timestamp',
  },
};

const flips = {
  collection: 'flips',
  fields: {
    id: 'string',
    name: 'string',
    category: 'string',
    buyPrice: 'number',
    sellPrice: 'number',
    profit: 'number',
    city: 'string',
    source: 'string',
    status: 'string',
    userId: 'string',
    created_at: 'timestamp',
  },
};

const pennyDeals = {
  collection: 'pennyDeals',
  fields: {
    id: 'string',
    name: 'string',
    store: 'string',
    current: 'number',
    original: 'number',
    savings: 'number',
    type: 'string',
    verified: 'boolean',
    created_at: 'timestamp',
  },
};

const receipts = {
  collection: 'receipts',
  fields: {
    id: 'string',
    userId: 'string',
    items: 'array',
    totalCashback: 'number',
    sources: 'array',
    status: 'string',
    imageUrl: 'string',
    created_at: 'timestamp',
  },
};

const legalPayouts = {
  collection: 'legalPayouts',
  fields: {
    id: 'string',
    claimType: 'string',
    amount: 'number',
    status: 'string',
    filingDate: 'timestamp',
    settlementDate: 'timestamp',
    userId: 'string',
    caseNumber: 'string',
    created_at: 'timestamp',
  },
};

const grants = {
  collection: 'grants',
  fields: {
    id: 'string',
    name: 'string',
    amount: 'number',
    deadline: 'timestamp',
    eligibility: 'array',
    status: 'string',
    applicationUrl: 'string',
    expectedValue: 'number',
    created_at: 'timestamp',
  },
};

const fiverrGigs = {
  collection: 'fiverrGigs',
  fields: {
    id: 'string',
    title: 'string',
    category: 'string',
    price: 'number',
    deliveryDays: 'number',
    rating: 'number',
    reviews: 'number',
    revenue: 'number',
    userId: 'string',
    status: 'string',
    created_at: 'timestamp',
  },
};

const realEstate = {
  collection: 'realEstate',
  fields: {
    id: 'string',
    address: 'string',
    city: 'string',
    state: 'string',
    listPrice: 'number',
    arv: 'number',
    rehab: 'number',
    profit: 'number',
    dealType: 'string',
    status: 'string',
    userId: 'string',
    created_at: 'timestamp',
  },
};

const domains = {
  collection: 'domains',
  fields: {
    id: 'string',
    name: 'string',
    registrar: 'string',
    registrationCost: 'number',
    askPrice: 'number',
    soldPrice: 'number',
    profit: 'number',
    estimatedValue: 'number',
    status: 'string',       // owned | listed | sold | flipped
    userId: 'string',
    expiryDate: 'string',   // YYYY-MM-DD
    notes: 'string',
    registered_at: 'timestamp',
    updated_at: 'timestamp',
  },
};

const SCHEMAS = {
  deals,
  flips,
  pennyDeals,
  receipts,
  legalPayouts,
  grants,
  fiverrGigs,
  realEstate,
  domains,
};

module.exports = SCHEMAS;
