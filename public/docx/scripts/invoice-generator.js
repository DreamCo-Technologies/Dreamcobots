'use strict';
/**
 * @file invoice-generator.js
 * @description Full invoice generation system using the docx npm package.
 *   Provides professional invoice creation, batch processing, line item tables,
 *   currency formatting, and sample data fixtures.
 * @module public/docx/scripts
 *
 * Requires: npm install docx
 */

const {
  Document, Packer, Paragraph, Table, TableRow, TableCell,
  TextRun, HeadingLevel, AlignmentType, WidthType, BorderStyle,
  ShadingType, TableLayoutType, VerticalAlign, PageOrientation,
  Header, Footer, ImageRun, SectionType, PageBreak,
  convertInchesToTwip, UnderlineType, PageNumber, NumberFormat,
} = require('docx');

const fs = require('fs');
const path = require('path');

// ─────────────────────────────────────────────────────────────────────────────
// CONSTANTS
// ─────────────────────────────────────────────────────────────────────────────

/** @constant {string} DEFAULT_CURRENCY - Default currency code */
const DEFAULT_CURRENCY = 'USD';

/** @constant {string} DEFAULT_FONT - Primary font for invoice documents */
const DEFAULT_FONT = 'Calibri';

/** @constant {number} DEFAULT_FONT_SIZE - Base font size in half-points */
const DEFAULT_FONT_SIZE = 22;

/** @constant {Object} INVOICE_COLORS - Color palette for invoice styling */
const INVOICE_COLORS = {
  PRIMARY:    '2563EB',
  SECONDARY:  '1E40AF',
  ACCENT:     'DBEAFE',
  TEXT_DARK:  '1F2937',
  TEXT_LIGHT: '6B7280',
  BORDER:     'E5E7EB',
  TABLE_HDR:  '1E3A5F',
  TABLE_ALT:  'F8FAFC',
  SUCCESS:    '16A34A',
  WARNING:    'D97706',
  WHITE:      'FFFFFF',
};

/** @constant {Object} CURRENCY_SYMBOLS - Currency code to symbol mapping */
const CURRENCY_SYMBOLS = {
  USD: '$', EUR: '€', GBP: '£', JPY: '¥',
  CAD: 'CA$', AUD: 'AU$', CHF: 'Fr.', CNY: '¥',
  INR: '₹', MXN: 'MX$', BRL: 'R$', KRW: '₩',
  SGD: 'S$', HKD: 'HK$', NOK: 'kr', SEK: 'kr',
  DKK: 'kr', NZD: 'NZ$', ZAR: 'R', RUB: '₽',
};

/** @constant {string[]} PAYMENT_TERMS - Standard payment term options */
const PAYMENT_TERMS = [
  'Net 15', 'Net 30', 'Net 45', 'Net 60',
  'Due on Receipt', '2/10 Net 30', 'CIA', 'COD',
];

// ─────────────────────────────────────────────────────────────────────────────
// SAMPLE DATA FIXTURES
// ─────────────────────────────────────────────────────────────────────────────

/**
 * @constant {Object} SAMPLE_INVOICE_1 - Tech consulting invoice sample
 */
const SAMPLE_INVOICE_1 = {
  invoiceNumber: 'INV-2024-0001',
  issueDate: '2024-01-15',
  dueDate: '2024-02-14',
  currency: 'USD',
  paymentTerms: 'Net 30',
  company: {
    name: 'DreamCo Technologies LLC',
    address: '1234 Innovation Drive, Suite 500',
    city: 'San Francisco',
    state: 'CA',
    zip: '94105',
    country: 'USA',
    phone: '+1 (415) 555-0100',
    email: 'billing@dreamco.tech',
    website: 'www.dreamco.tech',
    taxId: 'EIN: 12-3456789',
  },
  billTo: {
    name: 'Acme Corporation',
    contactName: 'John Smith',
    address: '5678 Business Blvd, Floor 12',
    city: 'New York',
    state: 'NY',
    zip: '10001',
    country: 'USA',
    email: 'john.smith@acme.com',
    phone: '+1 (212) 555-0200',
  },
  lineItems: [
    { description: 'Full-Stack Web Application Development', quantity: 80, unitPrice: 150.00, taxRate: 0.08 },
    { description: 'UI/UX Design and Prototyping', quantity: 40, unitPrice: 125.00, taxRate: 0.08 },
    { description: 'Cloud Infrastructure Setup (AWS)', quantity: 20, unitPrice: 175.00, taxRate: 0.08 },
    { description: 'API Integration Services', quantity: 24, unitPrice: 160.00, taxRate: 0.08 },
    { description: 'Quality Assurance & Testing', quantity: 16, unitPrice: 110.00, taxRate: 0.08 },
    { description: 'Project Management', quantity: 10, unitPrice: 130.00, taxRate: 0.08 },
    { description: 'Technical Documentation', quantity: 8, unitPrice: 100.00, taxRate: 0.08 },
    { description: 'Deployment & DevOps Setup', quantity: 12, unitPrice: 165.00, taxRate: 0.08 },
  ],
  taxRate: 0.08,
  discountPercent: 5,
  notes: 'Thank you for your business! Payment is due within 30 days of invoice date. Please include the invoice number on your check or bank transfer. Late payments are subject to a 1.5% monthly interest charge.',
  bankDetails: {
    bankName: 'First National Bank of California',
    accountName: 'DreamCo Technologies LLC',
    accountNumber: '****4521',
    routingNumber: '****8734',
    swiftCode: 'FNBCUS33',
    iban: 'US12 FNBC 0000 0000 4521',
  },
};

/**
 * @constant {Object} SAMPLE_INVOICE_2 - Creative agency invoice sample
 */
const SAMPLE_INVOICE_2 = {
  invoiceNumber: 'INV-2024-0042',
  issueDate: '2024-02-01',
  dueDate: '2024-03-02',
  currency: 'EUR',
  paymentTerms: 'Net 30',
  company: {
    name: 'Pixel Perfect Creative Studio',
    address: '89 Rue de la Paix',
    city: 'Paris',
    state: 'Île-de-France',
    zip: '75002',
    country: 'France',
    phone: '+33 1 23 45 67 89',
    email: 'invoices@pixelperfect.fr',
    website: 'www.pixelperfect.fr',
    taxId: 'TVA: FR12345678901',
  },
  billTo: {
    name: 'Global Brands International',
    contactName: 'Marie Dupont',
    address: '45 Avenue des Champs-Élysées',
    city: 'Paris',
    state: 'Île-de-France',
    zip: '75008',
    country: 'France',
    email: 'marie.dupont@globalbrands.com',
    phone: '+33 1 98 76 54 32',
  },
  lineItems: [
    { description: 'Brand Identity Package (Logo, Colors, Typography)', quantity: 1, unitPrice: 3500.00, taxRate: 0.20 },
    { description: 'Marketing Campaign Design (10 Ads)', quantity: 10, unitPrice: 250.00, taxRate: 0.20 },
    { description: 'Social Media Graphics Pack', quantity: 1, unitPrice: 1200.00, taxRate: 0.20 },
    { description: 'Print Collateral Design (Business Cards, Brochure)', quantity: 1, unitPrice: 800.00, taxRate: 0.20 },
    { description: 'Website Banner Set (5 sizes)', quantity: 5, unitPrice: 150.00, taxRate: 0.20 },
    { description: 'Brand Guidelines Document', quantity: 1, unitPrice: 600.00, taxRate: 0.20 },
  ],
  taxRate: 0.20,
  discountPercent: 0,
  notes: 'Merci pour votre confiance. Les fichiers sources seront livrés après réception du paiement intégral. Les droits de propriété intellectuelle sont transférés à la réception du paiement.',
  bankDetails: {
    bankName: 'BNP Paribas',
    accountName: 'Pixel Perfect Creative Studio SARL',
    accountNumber: '****7823',
    routingNumber: 'N/A',
    swiftCode: 'BNPAFRPP',
    iban: 'FR76 3000 4028 3700 0123 4567 890',
  },
};

/**
 * @constant {Object} SAMPLE_INVOICE_3 - SaaS subscription invoice sample
 */
const SAMPLE_INVOICE_3 = {
  invoiceNumber: 'INV-2024-SUB-0099',
  issueDate: '2024-03-01',
  dueDate: '2024-03-15',
  currency: 'USD',
  paymentTerms: 'Net 15',
  company: {
    name: 'CloudSync SaaS Inc.',
    address: '999 Tech Park Way',
    city: 'Austin',
    state: 'TX',
    zip: '78701',
    country: 'USA',
    phone: '+1 (512) 555-0300',
    email: 'subscriptions@cloudsync.io',
    website: 'www.cloudsync.io',
    taxId: 'EIN: 98-7654321',
  },
  billTo: {
    name: 'StartupVentures Ltd',
    contactName: 'Sarah Johnson',
    address: '2222 Startup Lane',
    city: 'Austin',
    state: 'TX',
    zip: '78702',
    country: 'USA',
    email: 'sarah@startupventures.com',
    phone: '+1 (512) 555-0400',
  },
  lineItems: [
    { description: 'CloudSync Pro Plan - Monthly Subscription (March 2024)', quantity: 1, unitPrice: 499.00, taxRate: 0.0825 },
    { description: 'Additional Storage - 500GB (March 2024)', quantity: 1, unitPrice: 49.99, taxRate: 0.0825 },
    { description: 'Premium Support Package', quantity: 1, unitPrice: 199.00, taxRate: 0.0825 },
    { description: 'API Rate Limit Increase (10M calls/month)', quantity: 1, unitPrice: 149.99, taxRate: 0.0825 },
    { description: 'White-Label Branding Add-on', quantity: 1, unitPrice: 99.00, taxRate: 0.0825 },
    { description: 'SSO/SAML Integration', quantity: 1, unitPrice: 79.00, taxRate: 0.0825 },
  ],
  taxRate: 0.0825,
  discountPercent: 10,
  notes: 'This invoice covers your CloudSync Pro subscription for March 2024. Your subscription auto-renews on the 1st of each month. To cancel or modify your subscription, please log in to your account dashboard or contact our support team.',
  bankDetails: {
    bankName: 'Silicon Valley Bank',
    accountName: 'CloudSync SaaS Inc.',
    accountNumber: '****3310',
    routingNumber: '****2211',
    swiftCode: 'SVBKUS6S',
    iban: 'US88 SVBK 0000 0000 3310',
  },
};

/**
 * @constant {Object} SAMPLE_INVOICE_4 - Freelance development invoice
 */
const SAMPLE_INVOICE_4 = {
  invoiceNumber: 'INV-FREELANCE-2024-007',
  issueDate: '2024-04-01',
  dueDate: '2024-04-16',
  currency: 'GBP',
  paymentTerms: 'Net 15',
  company: {
    name: 'James Harrison - Freelance Developer',
    address: '14 Camden High Street, Flat 3',
    city: 'London',
    state: 'England',
    zip: 'NW1 0JH',
    country: 'United Kingdom',
    phone: '+44 20 7946 0123',
    email: 'james@jamesharrison.dev',
    website: 'www.jamesharrison.dev',
    taxId: 'UTR: 1234567890',
  },
  billTo: {
    name: 'MediaWave Digital Agency',
    contactName: 'Claire Thompson',
    address: '77 Old Street',
    city: 'London',
    state: 'England',
    zip: 'EC1V 9HX',
    country: 'United Kingdom',
    email: 'claire@mediawave.co.uk',
    phone: '+44 20 7946 0456',
  },
  lineItems: [
    { description: 'React.js Frontend Development (Week 1)', quantity: 5, unitPrice: 600.00, taxRate: 0.20 },
    { description: 'React.js Frontend Development (Week 2)', quantity: 5, unitPrice: 600.00, taxRate: 0.20 },
    { description: 'Node.js Backend API Development', quantity: 3, unitPrice: 650.00, taxRate: 0.20 },
    { description: 'Database Design & Migration', quantity: 2, unitPrice: 575.00, taxRate: 0.20 },
    { description: 'Code Review & Refactoring', quantity: 1, unitPrice: 550.00, taxRate: 0.20 },
    { description: 'Deployment Configuration', quantity: 1, unitPrice: 500.00, taxRate: 0.20 },
  ],
  taxRate: 0.20,
  discountPercent: 0,
  notes: 'VAT Invoice. Please include invoice number INV-FREELANCE-2024-007 with your payment. Bank transfer preferred. All rates quoted are day rates unless otherwise stated.',
  bankDetails: {
    bankName: 'Barclays Bank PLC',
    accountName: 'James Harrison',
    accountNumber: '****5647',
    routingNumber: 'Sort Code: 20-**-**',
    swiftCode: 'BARCGB22',
    iban: 'GB29 BARC 2000 0055 5647 00',
  },
};

// ─────────────────────────────────────────────────────────────────────────────
// UTILITY FUNCTIONS
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Formats a numeric amount as a currency string.
 * @param {number} amount - The numeric amount to format
 * @param {string} [currency='USD'] - ISO 4217 currency code
 * @param {number} [decimals=2] - Number of decimal places
 * @returns {string} Formatted currency string (e.g., "$1,234.56")
 */
function formatCurrency(amount, currency = DEFAULT_CURRENCY, decimals = 2) {
  const symbol = CURRENCY_SYMBOLS[currency] || currency + ' ';
  const formatted = Math.abs(amount).toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  return amount < 0 ? `(${symbol}${formatted})` : `${symbol}${formatted}`;
}

/**
 * Formats a date string into a human-readable format.
 * @param {string} dateStr - ISO date string (YYYY-MM-DD)
 * @returns {string} Formatted date (e.g., "January 15, 2024")
 */
function formatDate(dateStr) {
  const months = ['January','February','March','April','May','June',
                  'July','August','September','October','November','December'];
  const [year, month, day] = dateStr.split('-').map(Number);
  return `${months[month - 1]} ${day}, ${year}`;
}

/**
 * Calculates invoice totals from line items.
 * @param {Object[]} lineItems - Array of line item objects
 * @param {number} [discountPercent=0] - Discount percentage (0–100)
 * @returns {Object} Totals: { subtotal, discount, taxableAmount, tax, total }
 */
function calculateTotals(lineItems, discountPercent = 0) {
  const subtotal = lineItems.reduce((sum, item) => sum + (item.quantity * item.unitPrice), 0);
  const discount = subtotal * (discountPercent / 100);
  const taxableAmount = subtotal - discount;
  const tax = lineItems.reduce((sum, item) => {
    const lineTotal = item.quantity * item.unitPrice;
    const lineDiscount = lineTotal * (discountPercent / 100);
    return sum + (lineTotal - lineDiscount) * (item.taxRate || 0);
  }, 0);
  const total = taxableAmount + tax;
  return { subtotal, discount, taxableAmount, tax, total };
}

/**
 * Creates a styled text run with consistent formatting.
 * @param {string} text - Text content
 * @param {Object} [options={}] - Formatting options
 * @param {boolean} [options.bold=false] - Bold text
 * @param {boolean} [options.italic=false] - Italic text
 * @param {number} [options.size=22] - Font size in half-points
 * @param {string} [options.color='1F2937'] - Hex color
 * @param {string} [options.font='Calibri'] - Font family
 * @returns {TextRun} Configured TextRun instance
 */
function createStyledText(text, options = {}) {
  return new TextRun({
    text: String(text),
    bold: options.bold || false,
    italics: options.italic || false,
    size: options.size || DEFAULT_FONT_SIZE,
    color: options.color || INVOICE_COLORS.TEXT_DARK,
    font: options.font || DEFAULT_FONT,
    underline: options.underline ? { type: UnderlineType.SINGLE } : undefined,
  });
}

/**
 * Creates an empty paragraph (blank line spacer).
 * @returns {Paragraph} Empty paragraph
 */
function emptyParagraph() {
  return new Paragraph({ children: [], spacing: { before: 60, after: 60 } });
}

/**
 * Creates a horizontal divider paragraph using Unicode character.
 * @returns {Paragraph} Divider paragraph
 */
function dividerParagraph() {
  return new Paragraph({
    children: [createStyledText('─'.repeat(80), { color: INVOICE_COLORS.BORDER, size: 18 })],
    spacing: { before: 80, after: 80 },
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// TABLE BUILDING FUNCTIONS
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Creates a styled table cell with options.
 * @param {string|TextRun[]} content - Cell content text or array of TextRuns
 * @param {Object} [opts={}] - Cell options
 * @param {string} [opts.background] - Background hex color
 * @param {boolean} [opts.bold=false] - Bold text
 * @param {string} [opts.alignment='left'] - Text alignment
 * @param {number} [opts.fontSize=22] - Font size in half-points
 * @param {string} [opts.color] - Text color hex
 * @param {number} [opts.width] - Column width percentage
 * @param {number} [opts.colSpan=1] - Column span
 * @param {boolean} [opts.noBorder=false] - Remove borders
 * @returns {TableCell} Configured TableCell
 */
function createCell(content, opts = {}) {
  const textRuns = Array.isArray(content) ? content : [
    createStyledText(String(content), {
      bold: opts.bold,
      size: opts.fontSize || DEFAULT_FONT_SIZE,
      color: opts.color || (opts.background === INVOICE_COLORS.TABLE_HDR ? INVOICE_COLORS.WHITE : INVOICE_COLORS.TEXT_DARK),
    })
  ];

  const borders = opts.noBorder ? {
    top:    { style: BorderStyle.NIL },
    bottom: { style: BorderStyle.NIL },
    left:   { style: BorderStyle.NIL },
    right:  { style: BorderStyle.NIL },
  } : {
    top:    { style: BorderStyle.SINGLE, size: 1, color: INVOICE_COLORS.BORDER },
    bottom: { style: BorderStyle.SINGLE, size: 1, color: INVOICE_COLORS.BORDER },
    left:   { style: BorderStyle.SINGLE, size: 1, color: INVOICE_COLORS.BORDER },
    right:  { style: BorderStyle.SINGLE, size: 1, color: INVOICE_COLORS.BORDER },
  };

  return new TableCell({
    children: [new Paragraph({
      children: textRuns,
      alignment: opts.alignment === 'center' ? AlignmentType.CENTER
                 : opts.alignment === 'right' ? AlignmentType.RIGHT
                 : AlignmentType.LEFT,
    })],
    shading: opts.background ? { fill: opts.background, type: ShadingType.CLEAR, color: 'auto' } : undefined,
    columnSpan: opts.colSpan || 1,
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    borders,
    width: opts.width ? { size: opts.width, type: WidthType.PERCENTAGE } : undefined,
    verticalAlign: VerticalAlign.CENTER,
  });
}

/**
 * Builds a fully styled line items table from invoice line items.
 * @param {Object[]} items - Array of line item objects
 * @param {string} [currency='USD'] - Currency code for formatting
 * @param {number} [discountPercent=0] - Discount percentage applied
 * @returns {Table} Styled docx Table object
 */
function createLineItemsTable(items, currency = DEFAULT_CURRENCY, discountPercent = 0) {
  const headerRow = new TableRow({
    tableHeader: true,
    children: [
      createCell('#',           { background: INVOICE_COLORS.TABLE_HDR, bold: true, alignment: 'center', fontSize: 20, width: 5 }),
      createCell('Description', { background: INVOICE_COLORS.TABLE_HDR, bold: true, fontSize: 20, width: 45 }),
      createCell('Qty',         { background: INVOICE_COLORS.TABLE_HDR, bold: true, alignment: 'center', fontSize: 20, width: 8 }),
      createCell('Unit Price',  { background: INVOICE_COLORS.TABLE_HDR, bold: true, alignment: 'right', fontSize: 20, width: 15 }),
      createCell('Tax %',       { background: INVOICE_COLORS.TABLE_HDR, bold: true, alignment: 'center', fontSize: 20, width: 12 }),
      createCell('Amount',      { background: INVOICE_COLORS.TABLE_HDR, bold: true, alignment: 'right', fontSize: 20, width: 15 }),
    ],
  });

  const dataRows = items.map((item, idx) => {
    const lineTotal = item.quantity * item.unitPrice;
    const bg = idx % 2 === 0 ? INVOICE_COLORS.WHITE : INVOICE_COLORS.TABLE_ALT;
    return new TableRow({
      children: [
        createCell(String(idx + 1),                               { background: bg, alignment: 'center', fontSize: 20 }),
        createCell(item.description,                              { background: bg, fontSize: 20 }),
        createCell(String(item.quantity),                         { background: bg, alignment: 'center', fontSize: 20 }),
        createCell(formatCurrency(item.unitPrice, currency),      { background: bg, alignment: 'right', fontSize: 20 }),
        createCell(`${((item.taxRate || 0) * 100).toFixed(1)}%`,  { background: bg, alignment: 'center', fontSize: 20 }),
        createCell(formatCurrency(lineTotal, currency),           { background: bg, alignment: 'right', fontSize: 20 }),
      ],
    });
  });

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    layout: TableLayoutType.FIXED,
    rows: [headerRow, ...dataRows],
  });
}

/**
 * Creates the totals summary table (subtotal, discount, tax, total).
 * @param {Object} totals - Calculated totals object
 * @param {string} [currency='USD'] - Currency code
 * @param {number} [discountPercent=0] - Discount percentage shown in label
 * @returns {Table} Totals table
 */
function createTotalsTable(totals, currency = DEFAULT_CURRENCY, discountPercent = 0) {
  const makeRow = (label, value, isBold = false, isTotal = false) => new TableRow({
    children: [
      createCell('', { noBorder: true }),
      createCell('', { noBorder: true }),
      createCell('', { noBorder: true }),
      createCell(label, {
        background: isTotal ? INVOICE_COLORS.PRIMARY : INVOICE_COLORS.WHITE,
        bold: isBold,
        alignment: 'right',
        fontSize: isTotal ? 24 : 20,
        color: isTotal ? INVOICE_COLORS.WHITE : INVOICE_COLORS.TEXT_DARK,
      }),
      createCell(value, {
        background: isTotal ? INVOICE_COLORS.PRIMARY : INVOICE_COLORS.WHITE,
        bold: isBold,
        alignment: 'right',
        fontSize: isTotal ? 24 : 20,
        color: isTotal ? INVOICE_COLORS.WHITE : INVOICE_COLORS.TEXT_DARK,
      }),
    ],
  });

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    layout: TableLayoutType.FIXED,
    rows: [
      makeRow('Subtotal:', formatCurrency(totals.subtotal, currency), false),
      ...(discountPercent > 0 ? [makeRow(`Discount (${discountPercent}%):`, `(${formatCurrency(totals.discount, currency)})`, false)] : []),
      makeRow(`Tax:`, formatCurrency(totals.tax, currency), false),
      makeRow('TOTAL DUE:', formatCurrency(totals.total, currency), true, true),
    ],
  });
}

/**
 * Creates a two-column info block (label: value pairs side by side).
 * @param {Object[]} leftItems - [{label, value}] for left column
 * @param {Object[]} rightItems - [{label, value}] for right column
 * @returns {Table} Two-column info table
 */
function createInfoBlock(leftItems, rightItems) {
  const makeContent = (items) => items.flatMap(item => [
    new Paragraph({
      children: [
        createStyledText(item.label + ': ', { bold: true, size: 20, color: INVOICE_COLORS.TEXT_LIGHT }),
        createStyledText(item.value, { size: 20, color: INVOICE_COLORS.TEXT_DARK }),
      ],
      spacing: { before: 40, after: 40 },
    }),
  ]);

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    layout: TableLayoutType.FIXED,
    rows: [
      new TableRow({
        children: [
          new TableCell({
            children: makeContent(leftItems),
            width: { size: 50, type: WidthType.PERCENTAGE },
            borders: { top: { style: BorderStyle.NIL }, bottom: { style: BorderStyle.NIL }, left: { style: BorderStyle.NIL }, right: { style: BorderStyle.NIL } },
            margins: { top: 0, bottom: 0, left: 0, right: 240 },
          }),
          new TableCell({
            children: makeContent(rightItems),
            width: { size: 50, type: WidthType.PERCENTAGE },
            borders: { top: { style: BorderStyle.NIL }, bottom: { style: BorderStyle.NIL }, left: { style: BorderStyle.NIL }, right: { style: BorderStyle.NIL } },
            margins: { top: 0, bottom: 0, left: 240, right: 0 },
          }),
        ],
      }),
    ],
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// HEADER / FOOTER BUILDERS
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Creates the invoice header with company info and invoice metadata.
 * @param {Object} company - Company information object
 * @param {string} invoiceNumber - Invoice number string
 * @param {string} issueDate - Issue date string
 * @param {string} dueDate - Due date string
 * @returns {Object[]} Array of docx content elements for the header area
 */
function buildInvoiceHeader(company, invoiceNumber, issueDate, dueDate) {
  const elements = [];

  // Company name as large heading
  elements.push(new Paragraph({
    children: [
      new TextRun({
        text: company.name,
        bold: true,
        size: 48,
        color: INVOICE_COLORS.PRIMARY,
        font: DEFAULT_FONT,
      }),
    ],
    spacing: { before: 0, after: 120 },
  }));

  // Company address block
  elements.push(new Paragraph({
    children: [createStyledText(company.address, { size: 18, color: INVOICE_COLORS.TEXT_LIGHT })],
    spacing: { before: 0, after: 40 },
  }));
  elements.push(new Paragraph({
    children: [createStyledText(`${company.city}, ${company.state} ${company.zip}, ${company.country}`, { size: 18, color: INVOICE_COLORS.TEXT_LIGHT })],
    spacing: { before: 0, after: 40 },
  }));
  elements.push(new Paragraph({
    children: [createStyledText(`Phone: ${company.phone}  |  Email: ${company.email}`, { size: 18, color: INVOICE_COLORS.TEXT_LIGHT })],
    spacing: { before: 0, after: 40 },
  }));
  elements.push(new Paragraph({
    children: [createStyledText(`Web: ${company.website}  |  ${company.taxId}`, { size: 18, color: INVOICE_COLORS.TEXT_LIGHT })],
    spacing: { before: 0, after: 200 },
  }));

  // Big INVOICE label with number
  elements.push(new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    rows: [
      new TableRow({
        children: [
          new TableCell({
            children: [
              new Paragraph({
                children: [new TextRun({ text: 'INVOICE', bold: true, size: 72, color: INVOICE_COLORS.WHITE, font: DEFAULT_FONT })],
              }),
            ],
            shading: { fill: INVOICE_COLORS.PRIMARY, type: ShadingType.CLEAR },
            margins: { top: 160, bottom: 160, left: 240, right: 240 },
            width: { size: 60, type: WidthType.PERCENTAGE },
            borders: { top: { style: BorderStyle.NIL }, bottom: { style: BorderStyle.NIL }, left: { style: BorderStyle.NIL }, right: { style: BorderStyle.NIL } },
          }),
          new TableCell({
            children: [
              new Paragraph({
                children: [
                  createStyledText('Invoice #: ', { bold: true, size: 22, color: INVOICE_COLORS.TEXT_LIGHT }),
                  createStyledText(invoiceNumber, { bold: true, size: 22, color: INVOICE_COLORS.PRIMARY }),
                ],
                spacing: { before: 40, after: 40 },
              }),
              new Paragraph({
                children: [
                  createStyledText('Issue Date: ', { bold: true, size: 20, color: INVOICE_COLORS.TEXT_LIGHT }),
                  createStyledText(formatDate(issueDate), { size: 20 }),
                ],
                spacing: { before: 40, after: 40 },
              }),
              new Paragraph({
                children: [
                  createStyledText('Due Date: ', { bold: true, size: 20, color: INVOICE_COLORS.TEXT_LIGHT }),
                  createStyledText(formatDate(dueDate), { bold: true, size: 20, color: INVOICE_COLORS.WARNING }),
                ],
                spacing: { before: 40, after: 40 },
              }),
            ],
            width: { size: 40, type: WidthType.PERCENTAGE },
            borders: { top: { style: BorderStyle.NIL }, bottom: { style: BorderStyle.NIL }, left: { style: BorderStyle.NIL }, right: { style: BorderStyle.NIL } },
            margins: { top: 80, bottom: 80, left: 240, right: 0 },
            verticalAlign: VerticalAlign.CENTER,
          }),
        ],
      }),
    ],
  }));

  return elements;
}

/**
 * Builds the Bill-To section of the invoice.
 * @param {Object} billTo - Billing contact information
 * @returns {Object[]} Array of paragraph elements
 */
function buildBillToSection(billTo) {
  return [
    emptyParagraph(),
    new Paragraph({
      children: [new TextRun({ text: 'BILL TO', bold: true, size: 20, color: INVOICE_COLORS.WHITE, font: DEFAULT_FONT })],
      shading: { fill: INVOICE_COLORS.SECONDARY, type: ShadingType.CLEAR },
      spacing: { before: 0, after: 0 },
      indent: { left: 0, right: 0 },
    }),
    new Paragraph({
      children: [createStyledText(billTo.name, { bold: true, size: 26 })],
      spacing: { before: 80, after: 40 },
      border: { left: { style: BorderStyle.THICK, size: 12, color: INVOICE_COLORS.PRIMARY } },
      indent: { left: 120 },
    }),
    new Paragraph({
      children: [createStyledText(`Attn: ${billTo.contactName}`, { size: 20 })],
      spacing: { before: 40, after: 40 },
      indent: { left: 120 },
    }),
    new Paragraph({
      children: [createStyledText(billTo.address, { size: 20 })],
      spacing: { before: 40, after: 40 },
      indent: { left: 120 },
    }),
    new Paragraph({
      children: [createStyledText(`${billTo.city}, ${billTo.state} ${billTo.zip}`, { size: 20 })],
      spacing: { before: 40, after: 40 },
      indent: { left: 120 },
    }),
    new Paragraph({
      children: [createStyledText(billTo.country, { size: 20 })],
      spacing: { before: 40, after: 40 },
      indent: { left: 120 },
    }),
    new Paragraph({
      children: [createStyledText(`Email: ${billTo.email}  |  Phone: ${billTo.phone}`, { size: 20, color: INVOICE_COLORS.TEXT_LIGHT })],
      spacing: { before: 40, after: 120 },
      indent: { left: 120 },
    }),
  ];
}

/**
 * Creates the bank / payment details section.
 * @param {Object} bankDetails - Bank account information
 * @param {string} paymentTerms - Payment terms string
 * @returns {Object[]} Array of paragraph and table elements
 */
function buildPaymentSection(bankDetails, paymentTerms) {
  return [
    emptyParagraph(),
    new Paragraph({
      children: [new TextRun({ text: 'PAYMENT DETAILS', bold: true, size: 22, color: INVOICE_COLORS.WHITE, font: DEFAULT_FONT })],
      shading: { fill: INVOICE_COLORS.SECONDARY, type: ShadingType.CLEAR },
      spacing: { before: 0, after: 0 },
    }),
    emptyParagraph(),
    createInfoBlock(
      [
        { label: 'Bank', value: bankDetails.bankName },
        { label: 'Account Name', value: bankDetails.accountName },
        { label: 'Account Number', value: bankDetails.accountNumber },
        { label: 'Routing Number', value: bankDetails.routingNumber },
      ],
      [
        { label: 'SWIFT/BIC', value: bankDetails.swiftCode },
        { label: 'IBAN', value: bankDetails.iban },
        { label: 'Payment Terms', value: paymentTerms },
      ]
    ),
  ];
}

/**
 * Creates the notes / additional information section.
 * @param {string} notes - Invoice notes text
 * @returns {Object[]} Array of paragraph elements
 */
function buildNotesSection(notes) {
  if (!notes) return [];
  return [
    emptyParagraph(),
    new Paragraph({
      children: [new TextRun({ text: 'NOTES & TERMS', bold: true, size: 22, color: INVOICE_COLORS.WHITE, font: DEFAULT_FONT })],
      shading: { fill: INVOICE_COLORS.SECONDARY, type: ShadingType.CLEAR },
      spacing: { before: 0, after: 0 },
    }),
    emptyParagraph(),
    new Paragraph({
      children: [createStyledText(notes, { size: 19, color: INVOICE_COLORS.TEXT_LIGHT })],
      spacing: { before: 60, after: 60 },
    }),
  ];
}

// ─────────────────────────────────────────────────────────────────────────────
// MAIN INVOICE GENERATION
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Generates a complete professional invoice as a docx Document.
 * @param {Object} data - Invoice data object
 * @param {string} data.invoiceNumber - Unique invoice identifier
 * @param {string} data.issueDate - Issue date in ISO format (YYYY-MM-DD)
 * @param {string} data.dueDate - Due date in ISO format (YYYY-MM-DD)
 * @param {string} [data.currency='USD'] - ISO 4217 currency code
 * @param {string} [data.paymentTerms='Net 30'] - Payment terms string
 * @param {Object} data.company - Issuing company information
 * @param {Object} data.billTo - Billing recipient information
 * @param {Object[]} data.lineItems - Array of invoice line items
 * @param {number} [data.discountPercent=0] - Discount percentage (0–100)
 * @param {string} [data.notes] - Invoice notes and terms
 * @param {Object} [data.bankDetails] - Payment/bank account details
 * @returns {Document} docx Document instance ready for packing
 */
function generateInvoice(data) {
  const {
    invoiceNumber, issueDate, dueDate,
    currency = DEFAULT_CURRENCY,
    paymentTerms = 'Net 30',
    company, billTo, lineItems,
    discountPercent = 0, notes,
    bankDetails = {},
  } = data;

  const totals = calculateTotals(lineItems, discountPercent);

  const headerSection = buildInvoiceHeader(company, invoiceNumber, issueDate, dueDate);
  const billToSection = buildBillToSection(billTo);
  const lineItemsSection = [
    emptyParagraph(),
    new Paragraph({
      children: [new TextRun({ text: 'LINE ITEMS', bold: true, size: 22, color: INVOICE_COLORS.WHITE, font: DEFAULT_FONT })],
      shading: { fill: INVOICE_COLORS.SECONDARY, type: ShadingType.CLEAR },
      spacing: { before: 0, after: 0 },
    }),
    emptyParagraph(),
    createLineItemsTable(lineItems, currency, discountPercent),
    emptyParagraph(),
    createTotalsTable(totals, currency, discountPercent),
  ];
  const paymentSection = bankDetails.bankName ? buildPaymentSection(bankDetails, paymentTerms) : [];
  const notesSection = buildNotesSection(notes);

  const thankYouParagraph = new Paragraph({
    children: [
      new TextRun({
        text: 'Thank you for your business!',
        bold: true, size: 26,
        color: INVOICE_COLORS.PRIMARY,
        font: DEFAULT_FONT,
      }),
    ],
    alignment: AlignmentType.CENTER,
    spacing: { before: 400, after: 200 },
  });

  const doc = new Document({
    creator: company.name,
    title: `Invoice ${invoiceNumber}`,
    description: `Invoice from ${company.name} to ${billTo.name}`,
    subject: `Invoice ${invoiceNumber} - Due ${formatDate(dueDate)}`,
    keywords: 'invoice, billing, payment',
    lastModifiedBy: company.name,
    sections: [{
      properties: {
        page: {
          margin: {
            top: convertInchesToTwip(1),
            right: convertInchesToTwip(1),
            bottom: convertInchesToTwip(1),
            left: convertInchesToTwip(1),
          },
        },
      },
      headers: {
        default: new Header({
          children: [
            new Paragraph({
              children: [
                createStyledText(`${company.name}  |  Invoice ${invoiceNumber}  |  Due: ${formatDate(dueDate)}`, {
                  size: 16, color: INVOICE_COLORS.TEXT_LIGHT,
                }),
              ],
              alignment: AlignmentType.RIGHT,
            }),
          ],
        }),
      },
      footers: {
        default: new Footer({
          children: [
            new Paragraph({
              children: [
                createStyledText('Page ', { size: 16, color: INVOICE_COLORS.TEXT_LIGHT }),
                new TextRun({ children: [PageNumber.CURRENT], size: 16, color: INVOICE_COLORS.TEXT_LIGHT, font: DEFAULT_FONT }),
                createStyledText(' of ', { size: 16, color: INVOICE_COLORS.TEXT_LIGHT }),
                new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 16, color: INVOICE_COLORS.TEXT_LIGHT, font: DEFAULT_FONT }),
                createStyledText(`  |  ${company.name}  |  ${company.email}  |  ${company.website}`, {
                  size: 16, color: INVOICE_COLORS.TEXT_LIGHT,
                }),
              ],
              alignment: AlignmentType.CENTER,
            }),
          ],
        }),
      },
      children: [
        ...headerSection,
        ...billToSection,
        ...lineItemsSection,
        ...paymentSection,
        ...notesSection,
        thankYouParagraph,
      ],
    }],
  });

  return doc;
}

/**
 * Generates multiple invoice documents from an array of invoice data objects.
 * @param {Object[]} invoicesArray - Array of invoice data objects
 * @param {Object} [options={}] - Batch options
 * @param {string} [options.outputDir='./invoices'] - Directory to save generated files
 * @param {boolean} [options.returnBuffers=false] - If true, returns buffers instead of saving
 * @returns {Promise<Object[]>} Array of results: [{invoiceNumber, filePath|buffer, success}]
 */
async function generateInvoiceBatch(invoicesArray, options = {}) {
  const { outputDir = './invoices', returnBuffers = false } = options;

  if (!returnBuffers && !fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const results = [];

  for (const invoiceData of invoicesArray) {
    try {
      const doc = generateInvoice(invoiceData);
      const buffer = await Packer.toBuffer(doc);

      if (returnBuffers) {
        results.push({ invoiceNumber: invoiceData.invoiceNumber, buffer, success: true });
      } else {
        const safeName = invoiceData.invoiceNumber.replace(/[^a-zA-Z0-9-_]/g, '_');
        const filePath = path.join(outputDir, `${safeName}.docx`);
        fs.writeFileSync(filePath, buffer);
        results.push({ invoiceNumber: invoiceData.invoiceNumber, filePath, success: true });
      }
    } catch (err) {
      results.push({ invoiceNumber: invoiceData.invoiceNumber, error: err.message, success: false });
    }
  }

  return results;
}

/**
 * Saves a generated invoice document to a file.
 * @param {Document} doc - The docx Document to save
 * @param {string} filePath - Full path including filename (e.g., './output/inv-001.docx')
 * @returns {Promise<string>} Resolves with the file path on success
 */
async function saveInvoice(doc, filePath) {
  const buffer = await Packer.toBuffer(doc);
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(filePath, buffer);
  return filePath;
}

/**
 * Returns invoice as a base64-encoded string (useful for email attachments).
 * @param {Document} doc - The docx Document instance
 * @returns {Promise<string>} Base64-encoded docx content
 */
async function invoiceToBase64(doc) {
  const buffer = await Packer.toBuffer(doc);
  return buffer.toString('base64');
}

/**
 * Creates a minimal invoice with only required fields, using defaults for optional fields.
 * @param {string} invoiceNumber - Invoice number
 * @param {Object} company - Company info
 * @param {Object} billTo - Bill-to info
 * @param {Object[]} lineItems - Line items
 * @returns {Document} Generated invoice document
 */
function generateSimpleInvoice(invoiceNumber, company, billTo, lineItems) {
  const today = new Date();
  const due = new Date(today);
  due.setDate(due.getDate() + 30);
  return generateInvoice({
    invoiceNumber,
    issueDate: today.toISOString().slice(0, 10),
    dueDate: due.toISOString().slice(0, 10),
    company, billTo, lineItems,
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// EXPORTS
// ─────────────────────────────────────────────────────────────────────────────

module.exports = {
  generateInvoice,
  generateInvoiceBatch,
  generateSimpleInvoice,
  createLineItemsTable,
  createTotalsTable,
  createInfoBlock,
  saveInvoice,
  invoiceToBase64,
  formatCurrency,
  formatDate,
  calculateTotals,
  buildInvoiceHeader,
  buildBillToSection,
  buildPaymentSection,
  buildNotesSection,
  createStyledText,
  emptyParagraph,
  dividerParagraph,
  createCell,
  // Constants
  INVOICE_COLORS,
  CURRENCY_SYMBOLS,
  PAYMENT_TERMS,
  DEFAULT_CURRENCY,
  DEFAULT_FONT,
  // Sample fixtures
  SAMPLE_INVOICE_1,
  SAMPLE_INVOICE_2,
  SAMPLE_INVOICE_3,
  SAMPLE_INVOICE_4,
};
