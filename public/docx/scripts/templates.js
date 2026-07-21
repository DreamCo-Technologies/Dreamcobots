/**
 * @fileoverview Document template system for generating structured docx files
 * @module docx-templates
 * @version 2.0.0
 * @description Provides pre-built templates and a template builder API for common
 *   document types: reports, invoices, contracts, resumes, letters, and more.
 */

'use strict';

const {
  Document,
  Paragraph,
  TextRun,
  Table,
  TableRow,
  TableCell,
  WidthType,
  AlignmentType,
  HeadingLevel,
  BorderStyle,
  ShadingType,
  ImageRun,
  Header,
  Footer,
  PageNumber,
  NumberOfPages,
  ExternalHyperlink,
  InternalHyperlink,
  Bookmark,
  BookmarkStart,
  BookmarkEnd,
  TableOfContents,
  Packer,
  UnderlineType,
  PageOrientation,
  LineRuleType,
  SectionType,
  LevelFormat,
  NumberFormat,
  TabStopType,
  TabStopPosition,
} = require('docx');

const fs = require('fs');
const path = require('path');

// ─── Type Definitions ─────────────────────────────────────────────────────────

/**
 * @typedef {Object} TemplateConfig
 * @property {string} name - Template name
 * @property {string} [description] - Template description
 * @property {PageConfig} [page] - Page configuration
 * @property {StyleConfig} [styles] - Custom styles
 * @property {BrandConfig} [branding] - Branding options
 * @property {boolean} [includeHeaderFooter=true] - Include header/footer
 * @property {boolean} [includeToc=false] - Include table of contents
 * @property {boolean} [includePageNumbers=true] - Include page numbers
 * @property {Object} [metadata] - Document metadata
 */

/**
 * @typedef {Object} PageConfig
 * @property {'portrait'|'landscape'} [orientation='portrait'] - Page orientation
 * @property {'letter'|'a4'|'legal'|'a3'} [size='letter'] - Page size
 * @property {number} [marginTop=1440] - Top margin in twips
 * @property {number} [marginRight=1440] - Right margin in twips
 * @property {number} [marginBottom=1440] - Bottom margin in twips
 * @property {number} [marginLeft=1440] - Left margin in twips
 */

/**
 * @typedef {Object} BrandConfig
 * @property {string} [primaryColor='003366'] - Primary brand color (hex)
 * @property {string} [secondaryColor='2980B9'] - Secondary brand color
 * @property {string} [accentColor='ED7D31'] - Accent color
 * @property {string} [companyName] - Company name for headers
 * @property {Buffer|string} [logo] - Logo image buffer or path
 * @property {string} [tagline] - Company tagline
 * @property {string} [font='Calibri'] - Primary font
 * @property {string} [headingFont='Calibri Light'] - Heading font
 */

// ─── Page Size Constants ──────────────────────────────────────────────────────

const PAGE_SIZES = {
  LETTER: { width: 12240, height: 15840 },       // 8.5 x 11 inches
  A4: { width: 11906, height: 16838 },            // 210 x 297 mm
  LEGAL: { width: 12240, height: 20160 },         // 8.5 x 14 inches
  A3: { width: 16838, height: 23811 },            // 297 x 420 mm
  TABLOID: { width: 15840, height: 24480 },       // 11 x 17 inches
};

const PAGE_MARGINS = {
  NORMAL: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
  NARROW: { top: 720, right: 720, bottom: 720, left: 720 },
  WIDE: { top: 1440, right: 2880, bottom: 1440, left: 2880 },
  MODERATE: { top: 1440, right: 1080, bottom: 1440, left: 1080 },
};

// ─── Default Styles ───────────────────────────────────────────────────────────

/**
 * Get default document styles configuration.
 * @param {BrandConfig} [branding] - Branding options
 * @returns {Object} Styles configuration object
 */
function getDefaultDocumentStyles(branding = {}) {
  const {
    primaryColor = '003366',
    secondaryColor = '2980B9',
    font = 'Calibri',
    headingFont = 'Calibri Light',
  } = branding;

  return {
    default: {
      document: {
        run: { size: 22, font, color: '333333' },
        paragraph: { spacing: { line: 276, lineRule: LineRuleType.AUTO } },
      },
      heading1: {
        run: { size: 36, bold: false, color: primaryColor, font: headingFont },
        paragraph: { spacing: { before: 240, after: 120 } },
      },
      heading2: {
        run: { size: 28, bold: false, color: primaryColor, font: headingFont },
        paragraph: { spacing: { before: 200, after: 80 } },
      },
      heading3: {
        run: { size: 24, bold: true, color: secondaryColor, font },
        paragraph: { spacing: { before: 160, after: 60 } },
      },
      heading4: {
        run: { size: 22, bold: true, color: '555555', font },
        paragraph: { spacing: { before: 120, after: 60 } },
      },
      listParagraph: {
        run: { size: 22, font },
        paragraph: { indent: { left: 720, hanging: 360 } },
      },
    },
    paragraphStyles: [
      {
        id: 'caption',
        name: 'Caption',
        basedOn: 'Normal',
        run: { italics: true, size: 18, color: '666666' },
        paragraph: { alignment: AlignmentType.CENTER, spacing: { before: 60, after: 200 } },
      },
      {
        id: 'blockquote',
        name: 'Block Quote',
        basedOn: 'Normal',
        run: { size: 22, italics: true, color: '555555' },
        paragraph: {
          indent: { left: 720, right: 360 },
          spacing: { before: 120, after: 120 },
          border: { left: { style: BorderStyle.THICK, size: 12, color: primaryColor } },
        },
      },
      {
        id: 'codeBlock',
        name: 'Code Block',
        basedOn: 'Normal',
        run: { size: 18, font: { name: 'Courier New' }, color: '1E1E1E' },
        paragraph: {
          shading: { type: ShadingType.SOLID, color: 'F8F8F8' },
          border: {
            top: { style: BorderStyle.SINGLE, size: 4, color: 'DDDDDD' },
            bottom: { style: BorderStyle.SINGLE, size: 4, color: 'DDDDDD' },
            left: { style: BorderStyle.THICK, size: 12, color: primaryColor },
            right: { style: BorderStyle.SINGLE, size: 4, color: 'DDDDDD' },
          },
          indent: { left: 360, right: 360 },
          spacing: { before: 80, after: 80 },
        },
      },
      {
        id: 'calloutInfo',
        name: 'Callout Info',
        basedOn: 'Normal',
        run: { size: 22, color: '1A5276' },
        paragraph: {
          shading: { type: ShadingType.SOLID, color: 'D6EAF8' },
          border: { left: { style: BorderStyle.THICK, size: 16, color: '2980B9' } },
          indent: { left: 360, right: 180 },
          spacing: { before: 120, after: 120 },
        },
      },
      {
        id: 'calloutWarning',
        name: 'Callout Warning',
        basedOn: 'Normal',
        run: { size: 22, color: '7D6608' },
        paragraph: {
          shading: { type: ShadingType.SOLID, color: 'FEF9E7' },
          border: { left: { style: BorderStyle.THICK, size: 16, color: 'F1C40F' } },
          indent: { left: 360 },
          spacing: { before: 120, after: 120 },
        },
      },
      {
        id: 'calloutDanger',
        name: 'Callout Danger',
        basedOn: 'Normal',
        run: { size: 22, color: '922B21' },
        paragraph: {
          shading: { type: ShadingType.SOLID, color: 'FADBD8' },
          border: { left: { style: BorderStyle.THICK, size: 16, color: 'E74C3C' } },
          indent: { left: 360 },
          spacing: { before: 120, after: 120 },
        },
      },
    ],
  };
}

// ─── Header & Footer Builders ─────────────────────────────────────────────────

/**
 * Create document header.
 * @param {Object} config - Header configuration
 * @param {BrandConfig} [branding] - Branding options
 * @returns {Header} Document header object
 */
function createDocumentHeader(config = {}, branding = {}) {
  const {
    showLogo = true,
    showCompanyName = true,
    showDate = false,
    showDocument = false,
    documentTitle = '',
    dividerColor = 'CCCCCC',
  } = config;

  const runs = [];

  if (showCompanyName && branding.companyName) {
    runs.push(new TextRun({ text: branding.companyName, bold: true, size: 20, color: branding.primaryColor || '003366' }));
    runs.push(new TextRun({ text: '\t' }));
  }

  if (showDocument && documentTitle) {
    runs.push(new TextRun({ text: documentTitle, size: 18, color: '666666', italics: true }));
  }

  if (showDate) {
    runs.push(new TextRun({ text: new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }), size: 18, color: '666666' }));
  }

  return new Header({
    children: [
      new Paragraph({
        children: runs,
        tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
        border: { bottom: { color: dividerColor, size: 6, style: BorderStyle.SINGLE } },
        spacing: { after: 60 },
      })
    ]
  });
}

/**
 * Create document footer.
 * @param {Object} config - Footer configuration
 * @param {BrandConfig} [branding] - Branding options
 * @returns {Footer} Document footer object
 */
function createDocumentFooter(config = {}, branding = {}) {
  const {
    showPageNumbers = true,
    showCompanyName = true,
    showConfidential = false,
    confidentialText = 'CONFIDENTIAL',
    dividerColor = 'CCCCCC',
    pageFormat = 'Page {n} of {total}',
  } = config;

  const leftRuns = [];
  const rightRuns = [];

  if (showCompanyName && branding.companyName) {
    leftRuns.push(new TextRun({ text: branding.companyName, size: 16, color: '888888' }));
  }

  if (showConfidential) {
    leftRuns.push(new TextRun({ text: confidentialText, size: 16, bold: true, color: 'CC0000' }));
  }

  if (showPageNumbers) {
    rightRuns.push(new TextRun({ text: 'Page ' }));
    rightRuns.push(new TextRun({ children: [PageNumber.CURRENT] }));
    rightRuns.push(new TextRun({ text: ' of ' }));
    rightRuns.push(new TextRun({ children: [NumberOfPages.NUMBER_OF_PAGES] }));
  }

  return new Footer({
    children: [
      new Paragraph({
        children: [
          ...leftRuns,
          new TextRun({ text: '\t' }),
          ...rightRuns,
        ],
        tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
        border: { top: { color: dividerColor, size: 6, style: BorderStyle.SINGLE } },
        spacing: { before: 60 },
      })
    ]
  });
}

// ─── Pre-Built Templates ──────────────────────────────────────────────────────

/**
 * Generate a professional business report document.
 * @param {Object} report - Report data
 * @param {string} report.title - Report title
 * @param {string} report.subtitle - Report subtitle
 * @param {string} report.author - Author name
 * @param {string} report.date - Report date
 * @param {Array} report.sections - Report sections
 * @param {Object} [options] - Template options
 * @param {BrandConfig} [options.branding] - Branding options
 * @returns {Promise<Buffer>} Document buffer
 *
 * @example
 * const buffer = await generateReport({
 *   title: 'Annual Performance Report',
 *   subtitle: 'Fiscal Year 2024',
 *   author: 'Analytics Team',
 *   date: 'January 2025',
 *   sections: [
 *     { heading: 'Executive Summary', body: '...' },
 *     { heading: 'Financial Results', body: '...', table: financeData },
 *   ]
 * }, { branding: { companyName: 'ACME Corp', primaryColor: '003366' } });
 */
async function generateReport(report, options = {}) {
  const { branding = {}, page = {}, includeTableOfContents = true } = options;
  const styles = getDefaultDocumentStyles(branding);
  const header = createDocumentHeader({ showCompanyName: true, showDate: true, documentTitle: report.title }, branding);
  const footer = createDocumentFooter({ showPageNumbers: true, showCompanyName: true }, branding);

  const children = [];

  // Cover page
  children.push(...createCoverPage(report, branding));
  children.push(new Paragraph({ pageBreakBefore: true, children: [] }));

  // Table of contents
  if (includeTableOfContents) {
    children.push(new Paragraph({ children: [new TextRun({ text: 'Table of Contents', bold: true, size: 32, color: branding.primaryColor || '003366' })], spacing: { after: 240 } }));
    children.push(new TableOfContents('Table of Contents', { hyperlink: true, headingStyleRange: '1-3' }));
    children.push(new Paragraph({ pageBreakBefore: true, children: [] }));
  }

  // Report sections
  for (const section of (report.sections || [])) {
    if (section.heading) {
      children.push(new Paragraph({
        children: [new TextRun({ text: section.heading })],
        heading: HeadingLevel.HEADING_1,
      }));
    }

    if (section.subheading) {
      children.push(new Paragraph({
        children: [new TextRun({ text: section.subheading })],
        heading: HeadingLevel.HEADING_2,
      }));
    }

    if (section.body) {
      const lines = section.body.split('\n');
      lines.forEach(line => {
        children.push(new Paragraph({
          children: [new TextRun({ text: line })],
          spacing: { after: 120 },
        }));
      });
    }

    if (section.bullets) {
      section.bullets.forEach(bullet => {
        children.push(new Paragraph({
          children: [new TextRun({ text: bullet })],
          bullet: { level: 0 },
          spacing: { after: 60 },
        }));
      });
    }

    if (section.table) {
      children.push(buildDataTable(section.table, branding));
    }

    if (section.pageBreakAfter) {
      children.push(new Paragraph({ pageBreakBefore: true, children: [] }));
    }
  }

  const doc = new Document({
    styles,
    sections: [{
      headers: { default: header },
      footers: { default: footer },
      properties: {
        page: {
          size: PAGE_SIZES[page.size?.toUpperCase()] || PAGE_SIZES.LETTER,
          margin: PAGE_MARGINS[page.margin?.toUpperCase()] || PAGE_MARGINS.NORMAL,
          orientation: page.orientation === 'landscape' ? PageOrientation.LANDSCAPE : PageOrientation.PORTRAIT,
        },
        titlePage: true,
      },
      children,
    }],
  });

  return await Packer.toBuffer(doc);
}

/**
 * Generate a professional invoice document.
 * @param {Object} invoice - Invoice data
 * @param {Object} [options] - Options
 * @returns {Promise<Buffer>} Document buffer
 *
 * @example
 * const buffer = await generateInvoice({
 *   number: 'INV-2024-001',
 *   date: '2024-01-15',
 *   dueDate: '2024-02-14',
 *   from: { name: 'My Company', address: '...', email: 'billing@company.com' },
 *   to: { name: 'Client Corp', address: '...', contact: 'Accounts Payable' },
 *   items: [{ description: 'Service A', qty: 10, rate: 150, amount: 1500 }],
 *   subtotal: 1500, tax: 135, total: 1635,
 *   notes: 'Payment due in 30 days.',
 *   bankDetails: { bank: 'First National', account: '...', routing: '...' },
 * });
 */
async function generateInvoice(invoice, options = {}) {
  const { branding = {} } = options;
  const primaryColor = branding.primaryColor || '003366';

  const children = [
    // Invoice title + number
    new Paragraph({
      children: [
        new TextRun({ text: 'INVOICE', size: 60, bold: true, color: primaryColor }),
        new TextRun({ text: `  #${invoice.number}`, size: 36, color: '666666' }),
      ],
      spacing: { after: 400 },
    }),

    // From / To section
    buildInvoiceParties(invoice, primaryColor),

    // Dates table
    buildInvoiceDates(invoice, primaryColor),

    // Line items table
    buildLineItemsTable(invoice.items, primaryColor),

    // Totals
    buildInvoiceTotals(invoice, primaryColor),

    // Notes
    ...(invoice.notes ? [
      new Paragraph({ children: [new TextRun({ text: 'Notes', bold: true, size: 22 })], spacing: { before: 240, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: invoice.notes, size: 20, color: '555555' })] }),
    ] : []),

    // Bank details
    ...(invoice.bankDetails ? buildBankDetails(invoice.bankDetails, primaryColor) : []),
  ];

  const doc = new Document({
    styles: getDefaultDocumentStyles(branding),
    sections: [{
      properties: {
        page: { size: PAGE_SIZES.LETTER, margin: PAGE_MARGINS.NORMAL }
      },
      children,
    }]
  });

  return await Packer.toBuffer(doc);
}

function buildInvoiceParties(invoice, color) {
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE }, insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE } },
    rows: [
      new TableRow({
        children: [
          new TableCell({
            width: { size: 50, type: WidthType.PERCENTAGE },
            children: [
              new Paragraph({ children: [new TextRun({ text: 'FROM', size: 16, bold: true, color })], spacing: { after: 60 } }),
              new Paragraph({ children: [new TextRun({ text: invoice.from?.name || '', bold: true, size: 22 })] }),
              ...(invoice.from?.address?.split('\n') || []).map(line => new Paragraph({ children: [new TextRun({ text: line, size: 20 })] })),
              ...(invoice.from?.email ? [new Paragraph({ children: [new TextRun({ text: invoice.from.email, size: 20 })] })] : []),
            ],
          }),
          new TableCell({
            width: { size: 50, type: WidthType.PERCENTAGE },
            children: [
              new Paragraph({ children: [new TextRun({ text: 'BILL TO', size: 16, bold: true, color })], spacing: { after: 60 } }),
              new Paragraph({ children: [new TextRun({ text: invoice.to?.name || '', bold: true, size: 22 })] }),
              ...(invoice.to?.address?.split('\n') || []).map(line => new Paragraph({ children: [new TextRun({ text: line, size: 20 })] })),
            ],
          }),
        ]
      })
    ]
  });
}

function buildLineItemsTable(items, primaryColor) {
  const headerRow = new TableRow({
    tableHeader: true,
    children: [
      makeHeaderCell('Description', primaryColor, 50),
      makeHeaderCell('Qty', primaryColor, 10),
      makeHeaderCell('Rate', primaryColor, 20),
      makeHeaderCell('Amount', primaryColor, 20),
    ]
  });

  const itemRows = (items || []).map((item, i) => new TableRow({
    children: [
      new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.description || '' })] })] }),
      new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: String(item.qty || '') })], alignment: AlignmentType.RIGHT })] }),
      new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: formatCurrencySimple(item.rate) })], alignment: AlignmentType.RIGHT })] }),
      new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: formatCurrencySimple(item.amount) })], alignment: AlignmentType.RIGHT })] }),
    ],
    shading: i % 2 === 0 ? undefined : { type: ShadingType.SOLID, color: 'F9F9F9' },
  }));

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    rows: [headerRow, ...itemRows],
    spacing: { before: 240 },
  });
}

function makeHeaderCell(text, color, widthPct) {
  return new TableCell({
    width: { size: widthPct, type: WidthType.PERCENTAGE },
    shading: { type: ShadingType.SOLID, color },
    children: [new Paragraph({ children: [new TextRun({ text, bold: true, color: 'FFFFFF', size: 20 })] })],
  });
}

function buildInvoiceDates(invoice, color) {
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE }, insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE } },
    rows: [new TableRow({ children: [
      new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: `Invoice Date: ${invoice.date || ''}`, size: 20 })] })] }),
      new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: `Due Date: ${invoice.dueDate || ''}`, size: 20, bold: true })] })] }),
    ]})],
    spacing: { before: 200, after: 200 },
  });
}

function buildInvoiceTotals(invoice, color) {
  const rows = [
    ['Subtotal', formatCurrencySimple(invoice.subtotal)],
    ...(invoice.discount ? [['Discount', `-${formatCurrencySimple(invoice.discount)}`]] : []),
    ['Tax', formatCurrencySimple(invoice.tax)],
    ['TOTAL DUE', formatCurrencySimple(invoice.total)],
  ];

  return new Table({
    width: { size: 50, type: WidthType.PERCENTAGE },
    float: { horizontalAnchor: 'margin', absoluteHorizontalPosition: 0 },
    rows: rows.map(([label, value], i) => {
      const isTotal = i === rows.length - 1;
      return new TableRow({
        children: [
          new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: label, bold: isTotal, size: isTotal ? 24 : 20 })] })] }),
          new TableCell({
            children: [new Paragraph({ children: [new TextRun({ text: value, bold: isTotal, size: isTotal ? 24 : 20 })], alignment: AlignmentType.RIGHT })],
            shading: isTotal ? { type: ShadingType.SOLID, color } : undefined,
          }),
        ]
      });
    }),
    spacing: { before: 240 },
  });
}

function buildBankDetails(bank, color) {
  return [
    new Paragraph({ children: [new TextRun({ text: 'Payment Details', bold: true, size: 22, color })], spacing: { before: 400, after: 80 } }),
    new Paragraph({ children: [new TextRun({ text: `Bank: ${bank.bank || ''}`, size: 20 })] }),
    new Paragraph({ children: [new TextRun({ text: `Account: ${bank.account || ''}`, size: 20 })] }),
    new Paragraph({ children: [new TextRun({ text: `Routing: ${bank.routing || ''}`, size: 20 })] }),
  ];
}

function formatCurrencySimple(value) {
  if (value === null || value === undefined) return '$0.00';
  return '$' + parseFloat(value).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

/**
 * Generate a professional resume document.
 * @param {Object} resume - Resume data
 * @param {Object} [options] - Options
 * @returns {Promise<Buffer>} Document buffer
 */
async function generateResume(resume, options = {}) {
  const { branding = {} } = options;
  const primaryColor = branding.primaryColor || '1A5276';
  const children = [
    // Name and title
    new Paragraph({ children: [new TextRun({ text: resume.name || '', bold: true, size: 48, color: primaryColor })], spacing: { after: 60 } }),
    new Paragraph({ children: [new TextRun({ text: resume.title || '', size: 28, color: '666666' })], spacing: { after: 120 } }),

    // Contact info
    new Paragraph({
      children: [
        new TextRun({ text: [resume.email, resume.phone, resume.location].filter(Boolean).join(' | '), size: 18, color: '555555' })
      ],
      border: { bottom: { color: primaryColor, size: 6, style: BorderStyle.SINGLE } },
      spacing: { after: 240 },
    }),

    // Summary
    ...(resume.summary ? [
      new Paragraph({ children: [new TextRun({ text: 'PROFESSIONAL SUMMARY', bold: true, size: 22, color: primaryColor })], spacing: { before: 120, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: resume.summary, size: 20 })], spacing: { after: 200 } }),
    ] : []),

    // Experience
    ...(resume.experience?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'WORK EXPERIENCE', bold: true, size: 22, color: primaryColor })], spacing: { before: 120, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),
      ...resume.experience.flatMap(job => [
        new Paragraph({ children: [new TextRun({ text: `${job.title || ''} — ${job.company || ''}`, bold: true, size: 22 })], spacing: { before: 120, after: 40 } }),
        new Paragraph({ children: [new TextRun({ text: `${job.period || ''}${job.location ? ' | ' + job.location : ''}`, size: 18, color: '666666', italics: true })], spacing: { after: 80 } }),
        ...(job.bullets || []).map(b => new Paragraph({ children: [new TextRun({ text: b, size: 20 })], bullet: { level: 0 }, spacing: { after: 40 } })),
      ]),
    ] : []),

    // Skills
    ...(resume.skills?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'SKILLS', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),
      new Paragraph({ children: [new TextRun({ text: resume.skills.join(' • '), size: 20 })], spacing: { after: 120 } }),
    ] : []),

    // Education
    ...(resume.education?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'EDUCATION', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),
      ...resume.education.flatMap(edu => [
        new Paragraph({ children: [new TextRun({ text: edu.degree || '', bold: true, size: 22 })], spacing: { before: 80, after: 40 } }),
        new Paragraph({ children: [new TextRun({ text: `${edu.school || ''} | ${edu.year || ''}`, size: 20, color: '666666' })], spacing: { after: 80 } }),
      ]),
    ] : []),
  ];

  const doc = new Document({
    styles: getDefaultDocumentStyles(branding),
    sections: [{
      properties: { page: { size: PAGE_SIZES.LETTER, margin: { top: 720, right: 1080, bottom: 720, left: 1080 } } },
      children,
    }]
  });

  return await Packer.toBuffer(doc);
}

// ─── Template Builder API ─────────────────────────────────────────────────────

/**
 * Create a fluent template builder.
 * @param {TemplateConfig} config - Template configuration
 * @returns {TemplateBuilder} Fluent builder instance
 *
 * @example
 * const buffer = await createTemplate({ name: 'MyReport' })
 *   .withBranding({ companyName: 'ACME', primaryColor: '003366' })
 *   .withHeader({ showDate: true })
 *   .withFooter({ showPageNumbers: true })
 *   .addCoverPage({ title: 'Q4 Report', subtitle: '2024' })
 *   .addTableOfContents()
 *   .addSection({ heading: 'Results', body: 'We achieved...' })
 *   .build();
 */
function createTemplate(config = {}) {
  return new TemplateBuilder(config);
}

class TemplateBuilder {
  constructor(config) {
    this._config = config;
    this._branding = {};
    this._headerConfig = null;
    this._footerConfig = null;
    this._children = [];
    this._pageConfig = {};
  }

  withBranding(branding) { this._branding = branding; return this; }
  withHeader(config) { this._headerConfig = config; return this; }
  withFooter(config) { this._footerConfig = config; return this; }
  withPage(config) { this._pageConfig = config; return this; }

  addCoverPage(data) {
    this._children.push(...createCoverPage(data, this._branding));
    this._children.push(new Paragraph({ pageBreakBefore: true, children: [] }));
    return this;
  }

  addTableOfContents(title = 'Table of Contents') {
    this._children.push(new Paragraph({ children: [new TextRun({ text: title, bold: true, size: 32 })], spacing: { after: 200 } }));
    this._children.push(new TableOfContents(title, { hyperlink: true, headingStyleRange: '1-3' }));
    this._children.push(new Paragraph({ pageBreakBefore: true, children: [] }));
    return this;
  }

  addHeading(text, level = 1) {
    this._children.push(new Paragraph({
      children: [new TextRun({ text })],
      heading: HeadingLevel[`HEADING_${level}`] || HeadingLevel.HEADING_1,
    }));
    return this;
  }

  addParagraph(text, style) {
    this._children.push(new Paragraph({
      children: [new TextRun({ text })],
      style,
      spacing: { after: 120 },
    }));
    return this;
  }

  addBullets(items, level = 0) {
    items.forEach(item => {
      this._children.push(new Paragraph({
        children: [new TextRun({ text: item })],
        bullet: { level },
        spacing: { after: 60 },
      }));
    });
    return this;
  }

  addTable(data, options = {}) {
    this._children.push(buildDataTable(data, this._branding, options));
    return this;
  }

  addSection(section) {
    if (section.heading) this.addHeading(section.heading, section.headingLevel || 1);
    if (section.body) this.addParagraph(section.body);
    if (section.bullets) this.addBullets(section.bullets);
    if (section.table) this.addTable(section.table);
    if (section.pageBreakAfter) this._children.push(new Paragraph({ pageBreakBefore: true, children: [] }));
    return this;
  }

  addPageBreak() {
    this._children.push(new Paragraph({ pageBreakBefore: true, children: [] }));
    return this;
  }

  async build() {
    const styles = getDefaultDocumentStyles(this._branding);
    const sections = [{
      ...(this._headerConfig ? { headers: { default: createDocumentHeader(this._headerConfig, this._branding) } } : {}),
      ...(this._footerConfig ? { footers: { default: createDocumentFooter(this._footerConfig, this._branding) } } : {}),
      properties: {
        page: {
          size: PAGE_SIZES.LETTER,
          margin: PAGE_MARGINS.NORMAL,
          orientation: this._pageConfig.orientation === 'landscape' ? PageOrientation.LANDSCAPE : PageOrientation.PORTRAIT,
        },
        titlePage: true,
      },
      children: this._children,
    }];

    const doc = new Document({ styles, sections });
    return await Packer.toBuffer(doc);
  }
}

// ─── Shared Helpers ───────────────────────────────────────────────────────────

function createCoverPage(data, branding = {}) {
  const color = branding.primaryColor || '003366';
  return [
    new Paragraph({ children: [new TextRun({ text: ' ' })], spacing: { after: 2880 } }),
    new Paragraph({ children: [new TextRun({ text: data.title || '', bold: true, size: 72, color })], alignment: AlignmentType.CENTER }),
    new Paragraph({ children: [new TextRun({ text: data.subtitle || '', size: 36, color: '666666' })], alignment: AlignmentType.CENTER, spacing: { after: 240 } }),
    new Paragraph({ children: [new TextRun({ text: data.author || '', size: 24, color: '555555', italics: true })], alignment: AlignmentType.CENTER }),
    new Paragraph({ children: [new TextRun({ text: data.date || new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' }), size: 22, color: '555555' })], alignment: AlignmentType.CENTER }),
  ];
}

function buildDataTable(data, branding = {}, options = {}) {
  const color = branding.primaryColor || '003366';
  const { headers = [], rows = [], striped = true } = data;

  const headerRow = new TableRow({
    tableHeader: true,
    children: headers.map(h => new TableCell({
      children: [new Paragraph({ children: [new TextRun({ text: String(h), bold: true, color: 'FFFFFF' })] })],
      shading: { type: ShadingType.SOLID, color },
    }))
  });

  const dataRows = rows.map((row, i) => new TableRow({
    children: (Array.isArray(row) ? row : Object.values(row)).map(cell => new TableCell({
      children: [new Paragraph({ children: [new TextRun({ text: String(cell || '') })] })],
      shading: (striped && i % 2 !== 0) ? { type: ShadingType.SOLID, color: 'F9F9F9' } : undefined,
    }))
  }));

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    rows: [headerRow, ...dataRows],
  });
}

// ─── Exports ──────────────────────────────────────────────────────────────────

module.exports = {
  // Template generators
  generateReport,
  generateInvoice,
  generateResume,
  // Builder API
  createTemplate,
  TemplateBuilder,
  // Helpers
  getDefaultDocumentStyles,
  createDocumentHeader,
  createDocumentFooter,
  createCoverPage,
  buildDataTable,
  // Constants
  PAGE_SIZES,
  PAGE_MARGINS,
};


// ─── Additional Template Utilities ───────────────────────────────────────────

/**
 * Generate a contract or agreement document.
 * @param {Object} contract - Contract data
 * @param {Object} [options] - Template options
 * @returns {Promise<Buffer>} Document buffer
 *
 * @example
 * const buffer = await generateContract({
 *   title: 'Service Agreement',
 *   parties: [
 *     { role: 'Client', name: 'ACME Corp', address: '123 Main St', representative: 'John Smith', title: 'CEO' },
 *     { role: 'Provider', name: 'TechCo LLC', address: '456 Oak Ave', representative: 'Jane Doe', title: 'Managing Director' },
 *   ],
 *   effectiveDate: 'January 1, 2025',
 *   termination: 'December 31, 2025',
 *   clauses: [
 *     { title: '1. Services', body: 'Provider agrees to...' },
 *     { title: '2. Payment', body: 'Client agrees to pay...' },
 *     { title: '3. Confidentiality', body: 'Both parties agree...' },
 *   ],
 *   governingLaw: 'New York, USA',
 * });
 */
async function generateContract(contract, options = {}) {
  const { branding = {} } = options;
  const primaryColor = branding.primaryColor || '1A237E';

  const children = [
    // Title
    new Paragraph({
      children: [new TextRun({ text: (contract.title || 'AGREEMENT').toUpperCase(), bold: true, size: 36, color: primaryColor })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 240 },
    }),

    new Paragraph({
      children: [new TextRun({ text: `Effective Date: ${contract.effectiveDate || ''}`, size: 20, italics: true })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 400 },
    }),

    // Parties
    new Paragraph({ children: [new TextRun({ text: 'PARTIES', bold: true, size: 24, color: primaryColor })], spacing: { before: 120, after: 80 } }),

    ...(contract.parties || []).flatMap(party => [
      new Paragraph({ children: [new TextRun({ text: `${party.role}: `, bold: true, size: 22 }), new TextRun({ text: party.name, size: 22 })] }),
      new Paragraph({ children: [new TextRun({ text: `Address: ${party.address || ''}`, size: 20, color: '555555' })] }),
      new Paragraph({ children: [new TextRun({ text: `Representative: ${party.representative || ''}, ${party.title || ''}`, size: 20, color: '555555' })], spacing: { after: 120 } }),
    ]),

    // Recitals
    ...(contract.recitals ? [
      new Paragraph({ children: [new TextRun({ text: 'RECITALS', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: contract.recitals, size: 20 })], spacing: { after: 200 } }),
    ] : []),

    // Terms
    new Paragraph({ children: [new TextRun({ text: 'TERMS AND CONDITIONS', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),

    // Clauses
    ...(contract.clauses || []).flatMap(clause => [
      new Paragraph({ children: [new TextRun({ text: clause.title, bold: true, size: 22 })], spacing: { before: 160, after: 80 } }),
      ...clause.body.split('\n').map(line => new Paragraph({ children: [new TextRun({ text: line, size: 20 })], spacing: { after: 80 } })),
    ]),

    // Governing law
    ...(contract.governingLaw ? [
      new Paragraph({ children: [new TextRun({ text: `Governing Law`, bold: true, size: 22 })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: `This Agreement shall be governed by the laws of ${contract.governingLaw}.`, size: 20 })], spacing: { after: 200 } }),
    ] : []),

    // Signature block
    new Paragraph({ children: [new TextRun({ text: 'SIGNATURES', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),

    buildSignatureTable(contract.parties || []),
  ];

  const doc = new Document({
    styles: getDefaultDocumentStyles(branding),
    sections: [{
      properties: { page: { size: PAGE_SIZES.LETTER, margin: PAGE_MARGINS.NORMAL } },
      children,
    }]
  });

  return await Packer.toBuffer(doc);
}

function buildSignatureTable(parties) {
  const cols = Math.min(parties.length, 3);
  const colWidth = Math.floor(100 / cols);

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE }, insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE } },
    rows: [
      new TableRow({
        children: parties.slice(0, cols).map(party => new TableCell({
          width: { size: colWidth, type: WidthType.PERCENTAGE },
          children: [
            new Paragraph({ children: [new TextRun({ text: party.role, bold: true, size: 20 })], spacing: { after: 400 } }),
            new Paragraph({ children: [new TextRun({ text: '_________________________', size: 20 })], spacing: { after: 60 } }),
            new Paragraph({ children: [new TextRun({ text: `Signature`, size: 16, color: '999999' })], spacing: { after: 200 } }),
            new Paragraph({ children: [new TextRun({ text: party.representative || '', bold: true, size: 20 })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: party.title || '', size: 18, color: '666666' })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: party.name, size: 18, color: '666666' })], spacing: { after: 200 } }),
            new Paragraph({ children: [new TextRun({ text: '_________________________', size: 20 })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: 'Date', size: 16, color: '999999' })] }),
          ],
        }))
      })
    ]
  });
}

/**
 * Generate a meeting minutes document.
 * @param {Object} meeting - Meeting data
 * @returns {Promise<Buffer>} Document buffer
 */
async function generateMeetingMinutes(meeting, options = {}) {
  const { branding = {} } = options;
  const primaryColor = branding.primaryColor || '1B5E20';

  const children = [
    new Paragraph({ children: [new TextRun({ text: 'MEETING MINUTES', bold: true, size: 40, color: primaryColor })], alignment: AlignmentType.CENTER, spacing: { after: 80 } }),
    new Paragraph({ children: [new TextRun({ text: meeting.title || '', size: 28, color: '333333' })], alignment: AlignmentType.CENTER, spacing: { after: 240 } }),

    // Meeting details table
    new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      rows: [
        ['Date', meeting.date || ''],
        ['Time', `${meeting.startTime || ''} - ${meeting.endTime || ''}`],
        ['Location', meeting.location || ''],
        ['Facilitator', meeting.facilitator || ''],
        ['Note Taker', meeting.noteTaker || ''],
      ].map(([label, value]) => new TableRow({
        children: [
          new TableCell({ width: { size: 20, type: WidthType.PERCENTAGE }, shading: { type: ShadingType.SOLID, color: 'F0F4F8' }, children: [new Paragraph({ children: [new TextRun({ text: label, bold: true, size: 20 })] })] }),
          new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: value, size: 20 })] })] }),
        ]
      })),
      spacing: { after: 240 },
    }),

    // Attendees
    new Paragraph({ children: [new TextRun({ text: 'ATTENDEES', bold: true, size: 22, color: primaryColor })], spacing: { before: 120, after: 80 } }),
    ...(meeting.attendees || []).map(a => new Paragraph({ children: [new TextRun({ text: `${a.name || a} — ${a.role || ''}`, size: 20 })], bullet: { level: 0 }, spacing: { after: 40 } })),

    // Agenda
    ...(meeting.agenda?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'AGENDA', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      ...meeting.agenda.map((item, i) => new Paragraph({ children: [new TextRun({ text: `${i + 1}. ${item}`, size: 20 })], spacing: { after: 40 } })),
    ] : []),

    // Discussion points
    ...(meeting.discussionPoints?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'DISCUSSION', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),
      ...meeting.discussionPoints.flatMap(point => [
        new Paragraph({ children: [new TextRun({ text: point.topic, bold: true, size: 22 })], spacing: { before: 120, after: 60 } }),
        new Paragraph({ children: [new TextRun({ text: point.summary || '', size: 20 })], spacing: { after: 80 } }),
        ...(point.decisions || []).map(d => new Paragraph({ children: [new TextRun({ text: `Decision: ${d}`, size: 20, bold: true, color: primaryColor })], spacing: { after: 40 } })),
      ]),
    ] : []),

    // Action items
    ...(meeting.actionItems?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'ACTION ITEMS', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),
      new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        rows: [
          new TableRow({
            tableHeader: true,
            children: ['Action', 'Owner', 'Due Date', 'Status'].map(h => new TableCell({ shading: { type: ShadingType.SOLID, color: primaryColor }, children: [new Paragraph({ children: [new TextRun({ text: h, bold: true, color: 'FFFFFF', size: 20 })] })] }))
          }),
          ...(meeting.actionItems || []).map((item, i) => new TableRow({
            children: [
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.action || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.owner || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.dueDate || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.status || 'Open', size: 20 })] })] }),
            ],
            shading: i % 2 !== 0 ? { type: ShadingType.SOLID, color: 'F9F9F9' } : undefined,
          }))
        ]
      }),
    ] : []),

    // Next meeting
    ...(meeting.nextMeeting ? [
      new Paragraph({ children: [new TextRun({ text: 'NEXT MEETING', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: `Date: ${meeting.nextMeeting.date || ''}`, size: 20 })], spacing: { after: 40 } }),
      new Paragraph({ children: [new TextRun({ text: `Location: ${meeting.nextMeeting.location || ''}`, size: 20 })], spacing: { after: 40 } }),
    ] : []),
  ];

  const doc = new Document({
    styles: getDefaultDocumentStyles(branding),
    sections: [{ properties: { page: { size: PAGE_SIZES.LETTER, margin: PAGE_MARGINS.NORMAL } }, children }]
  });

  return await Packer.toBuffer(doc);
}

Object.assign(module.exports, {
  generateContract,
  generateMeetingMinutes,
});


// ─── Additional Template Utilities ───────────────────────────────────────────

/**
 * Generate a contract or agreement document.
 * @param {Object} contract - Contract data
 * @param {Object} [options] - Template options
 * @returns {Promise<Buffer>} Document buffer
 *
 * @example
 * const buffer = await generateContract({
 *   title: 'Service Agreement',
 *   parties: [
 *     { role: 'Client', name: 'ACME Corp', address: '123 Main St', representative: 'John Smith', title: 'CEO' },
 *     { role: 'Provider', name: 'TechCo LLC', address: '456 Oak Ave', representative: 'Jane Doe', title: 'Managing Director' },
 *   ],
 *   effectiveDate: 'January 1, 2025',
 *   termination: 'December 31, 2025',
 *   clauses: [
 *     { title: '1. Services', body: 'Provider agrees to...' },
 *     { title: '2. Payment', body: 'Client agrees to pay...' },
 *     { title: '3. Confidentiality', body: 'Both parties agree...' },
 *   ],
 *   governingLaw: 'New York, USA',
 * });
 */
async function generateContract(contract, options = {}) {
  const { branding = {} } = options;
  const primaryColor = branding.primaryColor || '1A237E';

  const children = [
    // Title
    new Paragraph({
      children: [new TextRun({ text: (contract.title || 'AGREEMENT').toUpperCase(), bold: true, size: 36, color: primaryColor })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 240 },
    }),

    new Paragraph({
      children: [new TextRun({ text: `Effective Date: ${contract.effectiveDate || ''}`, size: 20, italics: true })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 400 },
    }),

    // Parties
    new Paragraph({ children: [new TextRun({ text: 'PARTIES', bold: true, size: 24, color: primaryColor })], spacing: { before: 120, after: 80 } }),

    ...(contract.parties || []).flatMap(party => [
      new Paragraph({ children: [new TextRun({ text: `${party.role}: `, bold: true, size: 22 }), new TextRun({ text: party.name, size: 22 })] }),
      new Paragraph({ children: [new TextRun({ text: `Address: ${party.address || ''}`, size: 20, color: '555555' })] }),
      new Paragraph({ children: [new TextRun({ text: `Representative: ${party.representative || ''}, ${party.title || ''}`, size: 20, color: '555555' })], spacing: { after: 120 } }),
    ]),

    // Recitals
    ...(contract.recitals ? [
      new Paragraph({ children: [new TextRun({ text: 'RECITALS', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: contract.recitals, size: 20 })], spacing: { after: 200 } }),
    ] : []),

    // Terms
    new Paragraph({ children: [new TextRun({ text: 'TERMS AND CONDITIONS', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),

    // Clauses
    ...(contract.clauses || []).flatMap(clause => [
      new Paragraph({ children: [new TextRun({ text: clause.title, bold: true, size: 22 })], spacing: { before: 160, after: 80 } }),
      ...clause.body.split('\n').map(line => new Paragraph({ children: [new TextRun({ text: line, size: 20 })], spacing: { after: 80 } })),
    ]),

    // Governing law
    ...(contract.governingLaw ? [
      new Paragraph({ children: [new TextRun({ text: `Governing Law`, bold: true, size: 22 })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: `This Agreement shall be governed by the laws of ${contract.governingLaw}.`, size: 20 })], spacing: { after: 200 } }),
    ] : []),

    // Signature block
    new Paragraph({ children: [new TextRun({ text: 'SIGNATURES', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),

    buildSignatureTable(contract.parties || []),
  ];

  const doc = new Document({
    styles: getDefaultDocumentStyles(branding),
    sections: [{
      properties: { page: { size: PAGE_SIZES.LETTER, margin: PAGE_MARGINS.NORMAL } },
      children,
    }]
  });

  return await Packer.toBuffer(doc);
}

function buildSignatureTable(parties) {
  const cols = Math.min(parties.length, 3);
  const colWidth = Math.floor(100 / cols);

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE }, insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE } },
    rows: [
      new TableRow({
        children: parties.slice(0, cols).map(party => new TableCell({
          width: { size: colWidth, type: WidthType.PERCENTAGE },
          children: [
            new Paragraph({ children: [new TextRun({ text: party.role, bold: true, size: 20 })], spacing: { after: 400 } }),
            new Paragraph({ children: [new TextRun({ text: '_________________________', size: 20 })], spacing: { after: 60 } }),
            new Paragraph({ children: [new TextRun({ text: `Signature`, size: 16, color: '999999' })], spacing: { after: 200 } }),
            new Paragraph({ children: [new TextRun({ text: party.representative || '', bold: true, size: 20 })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: party.title || '', size: 18, color: '666666' })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: party.name, size: 18, color: '666666' })], spacing: { after: 200 } }),
            new Paragraph({ children: [new TextRun({ text: '_________________________', size: 20 })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: 'Date', size: 16, color: '999999' })] }),
          ],
        }))
      })
    ]
  });
}

/**
 * Generate a meeting minutes document.
 * @param {Object} meeting - Meeting data
 * @returns {Promise<Buffer>} Document buffer
 */
async function generateMeetingMinutes(meeting, options = {}) {
  const { branding = {} } = options;
  const primaryColor = branding.primaryColor || '1B5E20';

  const children = [
    new Paragraph({ children: [new TextRun({ text: 'MEETING MINUTES', bold: true, size: 40, color: primaryColor })], alignment: AlignmentType.CENTER, spacing: { after: 80 } }),
    new Paragraph({ children: [new TextRun({ text: meeting.title || '', size: 28, color: '333333' })], alignment: AlignmentType.CENTER, spacing: { after: 240 } }),

    // Meeting details table
    new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      rows: [
        ['Date', meeting.date || ''],
        ['Time', `${meeting.startTime || ''} - ${meeting.endTime || ''}`],
        ['Location', meeting.location || ''],
        ['Facilitator', meeting.facilitator || ''],
        ['Note Taker', meeting.noteTaker || ''],
      ].map(([label, value]) => new TableRow({
        children: [
          new TableCell({ width: { size: 20, type: WidthType.PERCENTAGE }, shading: { type: ShadingType.SOLID, color: 'F0F4F8' }, children: [new Paragraph({ children: [new TextRun({ text: label, bold: true, size: 20 })] })] }),
          new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: value, size: 20 })] })] }),
        ]
      })),
      spacing: { after: 240 },
    }),

    // Attendees
    new Paragraph({ children: [new TextRun({ text: 'ATTENDEES', bold: true, size: 22, color: primaryColor })], spacing: { before: 120, after: 80 } }),
    ...(meeting.attendees || []).map(a => new Paragraph({ children: [new TextRun({ text: `${a.name || a} — ${a.role || ''}`, size: 20 })], bullet: { level: 0 }, spacing: { after: 40 } })),

    // Agenda
    ...(meeting.agenda?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'AGENDA', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      ...meeting.agenda.map((item, i) => new Paragraph({ children: [new TextRun({ text: `${i + 1}. ${item}`, size: 20 })], spacing: { after: 40 } })),
    ] : []),

    // Discussion points
    ...(meeting.discussionPoints?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'DISCUSSION', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),
      ...meeting.discussionPoints.flatMap(point => [
        new Paragraph({ children: [new TextRun({ text: point.topic, bold: true, size: 22 })], spacing: { before: 120, after: 60 } }),
        new Paragraph({ children: [new TextRun({ text: point.summary || '', size: 20 })], spacing: { after: 80 } }),
        ...(point.decisions || []).map(d => new Paragraph({ children: [new TextRun({ text: `Decision: ${d}`, size: 20, bold: true, color: primaryColor })], spacing: { after: 40 } })),
      ]),
    ] : []),

    // Action items
    ...(meeting.actionItems?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'ACTION ITEMS', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),
      new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        rows: [
          new TableRow({
            tableHeader: true,
            children: ['Action', 'Owner', 'Due Date', 'Status'].map(h => new TableCell({ shading: { type: ShadingType.SOLID, color: primaryColor }, children: [new Paragraph({ children: [new TextRun({ text: h, bold: true, color: 'FFFFFF', size: 20 })] })] }))
          }),
          ...(meeting.actionItems || []).map((item, i) => new TableRow({
            children: [
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.action || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.owner || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.dueDate || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.status || 'Open', size: 20 })] })] }),
            ],
            shading: i % 2 !== 0 ? { type: ShadingType.SOLID, color: 'F9F9F9' } : undefined,
          }))
        ]
      }),
    ] : []),

    // Next meeting
    ...(meeting.nextMeeting ? [
      new Paragraph({ children: [new TextRun({ text: 'NEXT MEETING', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: `Date: ${meeting.nextMeeting.date || ''}`, size: 20 })], spacing: { after: 40 } }),
      new Paragraph({ children: [new TextRun({ text: `Location: ${meeting.nextMeeting.location || ''}`, size: 20 })], spacing: { after: 40 } }),
    ] : []),
  ];

  const doc = new Document({
    styles: getDefaultDocumentStyles(branding),
    sections: [{ properties: { page: { size: PAGE_SIZES.LETTER, margin: PAGE_MARGINS.NORMAL } }, children }]
  });

  return await Packer.toBuffer(doc);
}

Object.assign(module.exports, {
  generateContract,
  generateMeetingMinutes,
});


// ─── Additional Template Utilities ───────────────────────────────────────────

/**
 * Generate a contract or agreement document.
 * @param {Object} contract - Contract data
 * @param {Object} [options] - Template options
 * @returns {Promise<Buffer>} Document buffer
 *
 * @example
 * const buffer = await generateContract({
 *   title: 'Service Agreement',
 *   parties: [
 *     { role: 'Client', name: 'ACME Corp', address: '123 Main St', representative: 'John Smith', title: 'CEO' },
 *     { role: 'Provider', name: 'TechCo LLC', address: '456 Oak Ave', representative: 'Jane Doe', title: 'Managing Director' },
 *   ],
 *   effectiveDate: 'January 1, 2025',
 *   termination: 'December 31, 2025',
 *   clauses: [
 *     { title: '1. Services', body: 'Provider agrees to...' },
 *     { title: '2. Payment', body: 'Client agrees to pay...' },
 *     { title: '3. Confidentiality', body: 'Both parties agree...' },
 *   ],
 *   governingLaw: 'New York, USA',
 * });
 */
async function generateContract(contract, options = {}) {
  const { branding = {} } = options;
  const primaryColor = branding.primaryColor || '1A237E';

  const children = [
    // Title
    new Paragraph({
      children: [new TextRun({ text: (contract.title || 'AGREEMENT').toUpperCase(), bold: true, size: 36, color: primaryColor })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 240 },
    }),

    new Paragraph({
      children: [new TextRun({ text: `Effective Date: ${contract.effectiveDate || ''}`, size: 20, italics: true })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 400 },
    }),

    // Parties
    new Paragraph({ children: [new TextRun({ text: 'PARTIES', bold: true, size: 24, color: primaryColor })], spacing: { before: 120, after: 80 } }),

    ...(contract.parties || []).flatMap(party => [
      new Paragraph({ children: [new TextRun({ text: `${party.role}: `, bold: true, size: 22 }), new TextRun({ text: party.name, size: 22 })] }),
      new Paragraph({ children: [new TextRun({ text: `Address: ${party.address || ''}`, size: 20, color: '555555' })] }),
      new Paragraph({ children: [new TextRun({ text: `Representative: ${party.representative || ''}, ${party.title || ''}`, size: 20, color: '555555' })], spacing: { after: 120 } }),
    ]),

    // Recitals
    ...(contract.recitals ? [
      new Paragraph({ children: [new TextRun({ text: 'RECITALS', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: contract.recitals, size: 20 })], spacing: { after: 200 } }),
    ] : []),

    // Terms
    new Paragraph({ children: [new TextRun({ text: 'TERMS AND CONDITIONS', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),

    // Clauses
    ...(contract.clauses || []).flatMap(clause => [
      new Paragraph({ children: [new TextRun({ text: clause.title, bold: true, size: 22 })], spacing: { before: 160, after: 80 } }),
      ...clause.body.split('\n').map(line => new Paragraph({ children: [new TextRun({ text: line, size: 20 })], spacing: { after: 80 } })),
    ]),

    // Governing law
    ...(contract.governingLaw ? [
      new Paragraph({ children: [new TextRun({ text: `Governing Law`, bold: true, size: 22 })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: `This Agreement shall be governed by the laws of ${contract.governingLaw}.`, size: 20 })], spacing: { after: 200 } }),
    ] : []),

    // Signature block
    new Paragraph({ children: [new TextRun({ text: 'SIGNATURES', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),

    buildSignatureTable(contract.parties || []),
  ];

  const doc = new Document({
    styles: getDefaultDocumentStyles(branding),
    sections: [{
      properties: { page: { size: PAGE_SIZES.LETTER, margin: PAGE_MARGINS.NORMAL } },
      children,
    }]
  });

  return await Packer.toBuffer(doc);
}

function buildSignatureTable(parties) {
  const cols = Math.min(parties.length, 3);
  const colWidth = Math.floor(100 / cols);

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE }, insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE } },
    rows: [
      new TableRow({
        children: parties.slice(0, cols).map(party => new TableCell({
          width: { size: colWidth, type: WidthType.PERCENTAGE },
          children: [
            new Paragraph({ children: [new TextRun({ text: party.role, bold: true, size: 20 })], spacing: { after: 400 } }),
            new Paragraph({ children: [new TextRun({ text: '_________________________', size: 20 })], spacing: { after: 60 } }),
            new Paragraph({ children: [new TextRun({ text: `Signature`, size: 16, color: '999999' })], spacing: { after: 200 } }),
            new Paragraph({ children: [new TextRun({ text: party.representative || '', bold: true, size: 20 })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: party.title || '', size: 18, color: '666666' })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: party.name, size: 18, color: '666666' })], spacing: { after: 200 } }),
            new Paragraph({ children: [new TextRun({ text: '_________________________', size: 20 })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: 'Date', size: 16, color: '999999' })] }),
          ],
        }))
      })
    ]
  });
}

/**
 * Generate a meeting minutes document.
 * @param {Object} meeting - Meeting data
 * @returns {Promise<Buffer>} Document buffer
 */
async function generateMeetingMinutes(meeting, options = {}) {
  const { branding = {} } = options;
  const primaryColor = branding.primaryColor || '1B5E20';

  const children = [
    new Paragraph({ children: [new TextRun({ text: 'MEETING MINUTES', bold: true, size: 40, color: primaryColor })], alignment: AlignmentType.CENTER, spacing: { after: 80 } }),
    new Paragraph({ children: [new TextRun({ text: meeting.title || '', size: 28, color: '333333' })], alignment: AlignmentType.CENTER, spacing: { after: 240 } }),

    // Meeting details table
    new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      rows: [
        ['Date', meeting.date || ''],
        ['Time', `${meeting.startTime || ''} - ${meeting.endTime || ''}`],
        ['Location', meeting.location || ''],
        ['Facilitator', meeting.facilitator || ''],
        ['Note Taker', meeting.noteTaker || ''],
      ].map(([label, value]) => new TableRow({
        children: [
          new TableCell({ width: { size: 20, type: WidthType.PERCENTAGE }, shading: { type: ShadingType.SOLID, color: 'F0F4F8' }, children: [new Paragraph({ children: [new TextRun({ text: label, bold: true, size: 20 })] })] }),
          new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: value, size: 20 })] })] }),
        ]
      })),
      spacing: { after: 240 },
    }),

    // Attendees
    new Paragraph({ children: [new TextRun({ text: 'ATTENDEES', bold: true, size: 22, color: primaryColor })], spacing: { before: 120, after: 80 } }),
    ...(meeting.attendees || []).map(a => new Paragraph({ children: [new TextRun({ text: `${a.name || a} — ${a.role || ''}`, size: 20 })], bullet: { level: 0 }, spacing: { after: 40 } })),

    // Agenda
    ...(meeting.agenda?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'AGENDA', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      ...meeting.agenda.map((item, i) => new Paragraph({ children: [new TextRun({ text: `${i + 1}. ${item}`, size: 20 })], spacing: { after: 40 } })),
    ] : []),

    // Discussion points
    ...(meeting.discussionPoints?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'DISCUSSION', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),
      ...meeting.discussionPoints.flatMap(point => [
        new Paragraph({ children: [new TextRun({ text: point.topic, bold: true, size: 22 })], spacing: { before: 120, after: 60 } }),
        new Paragraph({ children: [new TextRun({ text: point.summary || '', size: 20 })], spacing: { after: 80 } }),
        ...(point.decisions || []).map(d => new Paragraph({ children: [new TextRun({ text: `Decision: ${d}`, size: 20, bold: true, color: primaryColor })], spacing: { after: 40 } })),
      ]),
    ] : []),

    // Action items
    ...(meeting.actionItems?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'ACTION ITEMS', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),
      new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        rows: [
          new TableRow({
            tableHeader: true,
            children: ['Action', 'Owner', 'Due Date', 'Status'].map(h => new TableCell({ shading: { type: ShadingType.SOLID, color: primaryColor }, children: [new Paragraph({ children: [new TextRun({ text: h, bold: true, color: 'FFFFFF', size: 20 })] })] }))
          }),
          ...(meeting.actionItems || []).map((item, i) => new TableRow({
            children: [
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.action || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.owner || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.dueDate || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.status || 'Open', size: 20 })] })] }),
            ],
            shading: i % 2 !== 0 ? { type: ShadingType.SOLID, color: 'F9F9F9' } : undefined,
          }))
        ]
      }),
    ] : []),

    // Next meeting
    ...(meeting.nextMeeting ? [
      new Paragraph({ children: [new TextRun({ text: 'NEXT MEETING', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: `Date: ${meeting.nextMeeting.date || ''}`, size: 20 })], spacing: { after: 40 } }),
      new Paragraph({ children: [new TextRun({ text: `Location: ${meeting.nextMeeting.location || ''}`, size: 20 })], spacing: { after: 40 } }),
    ] : []),
  ];

  const doc = new Document({
    styles: getDefaultDocumentStyles(branding),
    sections: [{ properties: { page: { size: PAGE_SIZES.LETTER, margin: PAGE_MARGINS.NORMAL } }, children }]
  });

  return await Packer.toBuffer(doc);
}

Object.assign(module.exports, {
  generateContract,
  generateMeetingMinutes,
});


// ─── Additional Template Utilities ───────────────────────────────────────────

/**
 * Generate a contract or agreement document.
 * @param {Object} contract - Contract data
 * @param {Object} [options] - Template options
 * @returns {Promise<Buffer>} Document buffer
 *
 * @example
 * const buffer = await generateContract({
 *   title: 'Service Agreement',
 *   parties: [
 *     { role: 'Client', name: 'ACME Corp', address: '123 Main St', representative: 'John Smith', title: 'CEO' },
 *     { role: 'Provider', name: 'TechCo LLC', address: '456 Oak Ave', representative: 'Jane Doe', title: 'Managing Director' },
 *   ],
 *   effectiveDate: 'January 1, 2025',
 *   termination: 'December 31, 2025',
 *   clauses: [
 *     { title: '1. Services', body: 'Provider agrees to...' },
 *     { title: '2. Payment', body: 'Client agrees to pay...' },
 *     { title: '3. Confidentiality', body: 'Both parties agree...' },
 *   ],
 *   governingLaw: 'New York, USA',
 * });
 */
async function generateContract(contract, options = {}) {
  const { branding = {} } = options;
  const primaryColor = branding.primaryColor || '1A237E';

  const children = [
    // Title
    new Paragraph({
      children: [new TextRun({ text: (contract.title || 'AGREEMENT').toUpperCase(), bold: true, size: 36, color: primaryColor })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 240 },
    }),

    new Paragraph({
      children: [new TextRun({ text: `Effective Date: ${contract.effectiveDate || ''}`, size: 20, italics: true })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 400 },
    }),

    // Parties
    new Paragraph({ children: [new TextRun({ text: 'PARTIES', bold: true, size: 24, color: primaryColor })], spacing: { before: 120, after: 80 } }),

    ...(contract.parties || []).flatMap(party => [
      new Paragraph({ children: [new TextRun({ text: `${party.role}: `, bold: true, size: 22 }), new TextRun({ text: party.name, size: 22 })] }),
      new Paragraph({ children: [new TextRun({ text: `Address: ${party.address || ''}`, size: 20, color: '555555' })] }),
      new Paragraph({ children: [new TextRun({ text: `Representative: ${party.representative || ''}, ${party.title || ''}`, size: 20, color: '555555' })], spacing: { after: 120 } }),
    ]),

    // Recitals
    ...(contract.recitals ? [
      new Paragraph({ children: [new TextRun({ text: 'RECITALS', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: contract.recitals, size: 20 })], spacing: { after: 200 } }),
    ] : []),

    // Terms
    new Paragraph({ children: [new TextRun({ text: 'TERMS AND CONDITIONS', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),

    // Clauses
    ...(contract.clauses || []).flatMap(clause => [
      new Paragraph({ children: [new TextRun({ text: clause.title, bold: true, size: 22 })], spacing: { before: 160, after: 80 } }),
      ...clause.body.split('\n').map(line => new Paragraph({ children: [new TextRun({ text: line, size: 20 })], spacing: { after: 80 } })),
    ]),

    // Governing law
    ...(contract.governingLaw ? [
      new Paragraph({ children: [new TextRun({ text: `Governing Law`, bold: true, size: 22 })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: `This Agreement shall be governed by the laws of ${contract.governingLaw}.`, size: 20 })], spacing: { after: 200 } }),
    ] : []),

    // Signature block
    new Paragraph({ children: [new TextRun({ text: 'SIGNATURES', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),

    buildSignatureTable(contract.parties || []),
  ];

  const doc = new Document({
    styles: getDefaultDocumentStyles(branding),
    sections: [{
      properties: { page: { size: PAGE_SIZES.LETTER, margin: PAGE_MARGINS.NORMAL } },
      children,
    }]
  });

  return await Packer.toBuffer(doc);
}

function buildSignatureTable(parties) {
  const cols = Math.min(parties.length, 3);
  const colWidth = Math.floor(100 / cols);

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE }, insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE } },
    rows: [
      new TableRow({
        children: parties.slice(0, cols).map(party => new TableCell({
          width: { size: colWidth, type: WidthType.PERCENTAGE },
          children: [
            new Paragraph({ children: [new TextRun({ text: party.role, bold: true, size: 20 })], spacing: { after: 400 } }),
            new Paragraph({ children: [new TextRun({ text: '_________________________', size: 20 })], spacing: { after: 60 } }),
            new Paragraph({ children: [new TextRun({ text: `Signature`, size: 16, color: '999999' })], spacing: { after: 200 } }),
            new Paragraph({ children: [new TextRun({ text: party.representative || '', bold: true, size: 20 })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: party.title || '', size: 18, color: '666666' })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: party.name, size: 18, color: '666666' })], spacing: { after: 200 } }),
            new Paragraph({ children: [new TextRun({ text: '_________________________', size: 20 })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: 'Date', size: 16, color: '999999' })] }),
          ],
        }))
      })
    ]
  });
}

/**
 * Generate a meeting minutes document.
 * @param {Object} meeting - Meeting data
 * @returns {Promise<Buffer>} Document buffer
 */
async function generateMeetingMinutes(meeting, options = {}) {
  const { branding = {} } = options;
  const primaryColor = branding.primaryColor || '1B5E20';

  const children = [
    new Paragraph({ children: [new TextRun({ text: 'MEETING MINUTES', bold: true, size: 40, color: primaryColor })], alignment: AlignmentType.CENTER, spacing: { after: 80 } }),
    new Paragraph({ children: [new TextRun({ text: meeting.title || '', size: 28, color: '333333' })], alignment: AlignmentType.CENTER, spacing: { after: 240 } }),

    // Meeting details table
    new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      rows: [
        ['Date', meeting.date || ''],
        ['Time', `${meeting.startTime || ''} - ${meeting.endTime || ''}`],
        ['Location', meeting.location || ''],
        ['Facilitator', meeting.facilitator || ''],
        ['Note Taker', meeting.noteTaker || ''],
      ].map(([label, value]) => new TableRow({
        children: [
          new TableCell({ width: { size: 20, type: WidthType.PERCENTAGE }, shading: { type: ShadingType.SOLID, color: 'F0F4F8' }, children: [new Paragraph({ children: [new TextRun({ text: label, bold: true, size: 20 })] })] }),
          new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: value, size: 20 })] })] }),
        ]
      })),
      spacing: { after: 240 },
    }),

    // Attendees
    new Paragraph({ children: [new TextRun({ text: 'ATTENDEES', bold: true, size: 22, color: primaryColor })], spacing: { before: 120, after: 80 } }),
    ...(meeting.attendees || []).map(a => new Paragraph({ children: [new TextRun({ text: `${a.name || a} — ${a.role || ''}`, size: 20 })], bullet: { level: 0 }, spacing: { after: 40 } })),

    // Agenda
    ...(meeting.agenda?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'AGENDA', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      ...meeting.agenda.map((item, i) => new Paragraph({ children: [new TextRun({ text: `${i + 1}. ${item}`, size: 20 })], spacing: { after: 40 } })),
    ] : []),

    // Discussion points
    ...(meeting.discussionPoints?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'DISCUSSION', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),
      ...meeting.discussionPoints.flatMap(point => [
        new Paragraph({ children: [new TextRun({ text: point.topic, bold: true, size: 22 })], spacing: { before: 120, after: 60 } }),
        new Paragraph({ children: [new TextRun({ text: point.summary || '', size: 20 })], spacing: { after: 80 } }),
        ...(point.decisions || []).map(d => new Paragraph({ children: [new TextRun({ text: `Decision: ${d}`, size: 20, bold: true, color: primaryColor })], spacing: { after: 40 } })),
      ]),
    ] : []),

    // Action items
    ...(meeting.actionItems?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'ACTION ITEMS', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),
      new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        rows: [
          new TableRow({
            tableHeader: true,
            children: ['Action', 'Owner', 'Due Date', 'Status'].map(h => new TableCell({ shading: { type: ShadingType.SOLID, color: primaryColor }, children: [new Paragraph({ children: [new TextRun({ text: h, bold: true, color: 'FFFFFF', size: 20 })] })] }))
          }),
          ...(meeting.actionItems || []).map((item, i) => new TableRow({
            children: [
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.action || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.owner || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.dueDate || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.status || 'Open', size: 20 })] })] }),
            ],
            shading: i % 2 !== 0 ? { type: ShadingType.SOLID, color: 'F9F9F9' } : undefined,
          }))
        ]
      }),
    ] : []),

    // Next meeting
    ...(meeting.nextMeeting ? [
      new Paragraph({ children: [new TextRun({ text: 'NEXT MEETING', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: `Date: ${meeting.nextMeeting.date || ''}`, size: 20 })], spacing: { after: 40 } }),
      new Paragraph({ children: [new TextRun({ text: `Location: ${meeting.nextMeeting.location || ''}`, size: 20 })], spacing: { after: 40 } }),
    ] : []),
  ];

  const doc = new Document({
    styles: getDefaultDocumentStyles(branding),
    sections: [{ properties: { page: { size: PAGE_SIZES.LETTER, margin: PAGE_MARGINS.NORMAL } }, children }]
  });

  return await Packer.toBuffer(doc);
}

Object.assign(module.exports, {
  generateContract,
  generateMeetingMinutes,
});


// ─── Additional Template Utilities ───────────────────────────────────────────

/**
 * Generate a contract or agreement document.
 * @param {Object} contract - Contract data
 * @param {Object} [options] - Template options
 * @returns {Promise<Buffer>} Document buffer
 *
 * @example
 * const buffer = await generateContract({
 *   title: 'Service Agreement',
 *   parties: [
 *     { role: 'Client', name: 'ACME Corp', address: '123 Main St', representative: 'John Smith', title: 'CEO' },
 *     { role: 'Provider', name: 'TechCo LLC', address: '456 Oak Ave', representative: 'Jane Doe', title: 'Managing Director' },
 *   ],
 *   effectiveDate: 'January 1, 2025',
 *   termination: 'December 31, 2025',
 *   clauses: [
 *     { title: '1. Services', body: 'Provider agrees to...' },
 *     { title: '2. Payment', body: 'Client agrees to pay...' },
 *     { title: '3. Confidentiality', body: 'Both parties agree...' },
 *   ],
 *   governingLaw: 'New York, USA',
 * });
 */
async function generateContract(contract, options = {}) {
  const { branding = {} } = options;
  const primaryColor = branding.primaryColor || '1A237E';

  const children = [
    // Title
    new Paragraph({
      children: [new TextRun({ text: (contract.title || 'AGREEMENT').toUpperCase(), bold: true, size: 36, color: primaryColor })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 240 },
    }),

    new Paragraph({
      children: [new TextRun({ text: `Effective Date: ${contract.effectiveDate || ''}`, size: 20, italics: true })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 400 },
    }),

    // Parties
    new Paragraph({ children: [new TextRun({ text: 'PARTIES', bold: true, size: 24, color: primaryColor })], spacing: { before: 120, after: 80 } }),

    ...(contract.parties || []).flatMap(party => [
      new Paragraph({ children: [new TextRun({ text: `${party.role}: `, bold: true, size: 22 }), new TextRun({ text: party.name, size: 22 })] }),
      new Paragraph({ children: [new TextRun({ text: `Address: ${party.address || ''}`, size: 20, color: '555555' })] }),
      new Paragraph({ children: [new TextRun({ text: `Representative: ${party.representative || ''}, ${party.title || ''}`, size: 20, color: '555555' })], spacing: { after: 120 } }),
    ]),

    // Recitals
    ...(contract.recitals ? [
      new Paragraph({ children: [new TextRun({ text: 'RECITALS', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: contract.recitals, size: 20 })], spacing: { after: 200 } }),
    ] : []),

    // Terms
    new Paragraph({ children: [new TextRun({ text: 'TERMS AND CONDITIONS', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),

    // Clauses
    ...(contract.clauses || []).flatMap(clause => [
      new Paragraph({ children: [new TextRun({ text: clause.title, bold: true, size: 22 })], spacing: { before: 160, after: 80 } }),
      ...clause.body.split('\n').map(line => new Paragraph({ children: [new TextRun({ text: line, size: 20 })], spacing: { after: 80 } })),
    ]),

    // Governing law
    ...(contract.governingLaw ? [
      new Paragraph({ children: [new TextRun({ text: `Governing Law`, bold: true, size: 22 })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: `This Agreement shall be governed by the laws of ${contract.governingLaw}.`, size: 20 })], spacing: { after: 200 } }),
    ] : []),

    // Signature block
    new Paragraph({ children: [new TextRun({ text: 'SIGNATURES', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),

    buildSignatureTable(contract.parties || []),
  ];

  const doc = new Document({
    styles: getDefaultDocumentStyles(branding),
    sections: [{
      properties: { page: { size: PAGE_SIZES.LETTER, margin: PAGE_MARGINS.NORMAL } },
      children,
    }]
  });

  return await Packer.toBuffer(doc);
}

function buildSignatureTable(parties) {
  const cols = Math.min(parties.length, 3);
  const colWidth = Math.floor(100 / cols);

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE }, insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE } },
    rows: [
      new TableRow({
        children: parties.slice(0, cols).map(party => new TableCell({
          width: { size: colWidth, type: WidthType.PERCENTAGE },
          children: [
            new Paragraph({ children: [new TextRun({ text: party.role, bold: true, size: 20 })], spacing: { after: 400 } }),
            new Paragraph({ children: [new TextRun({ text: '_________________________', size: 20 })], spacing: { after: 60 } }),
            new Paragraph({ children: [new TextRun({ text: `Signature`, size: 16, color: '999999' })], spacing: { after: 200 } }),
            new Paragraph({ children: [new TextRun({ text: party.representative || '', bold: true, size: 20 })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: party.title || '', size: 18, color: '666666' })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: party.name, size: 18, color: '666666' })], spacing: { after: 200 } }),
            new Paragraph({ children: [new TextRun({ text: '_________________________', size: 20 })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: 'Date', size: 16, color: '999999' })] }),
          ],
        }))
      })
    ]
  });
}

/**
 * Generate a meeting minutes document.
 * @param {Object} meeting - Meeting data
 * @returns {Promise<Buffer>} Document buffer
 */
async function generateMeetingMinutes(meeting, options = {}) {
  const { branding = {} } = options;
  const primaryColor = branding.primaryColor || '1B5E20';

  const children = [
    new Paragraph({ children: [new TextRun({ text: 'MEETING MINUTES', bold: true, size: 40, color: primaryColor })], alignment: AlignmentType.CENTER, spacing: { after: 80 } }),
    new Paragraph({ children: [new TextRun({ text: meeting.title || '', size: 28, color: '333333' })], alignment: AlignmentType.CENTER, spacing: { after: 240 } }),

    // Meeting details table
    new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      rows: [
        ['Date', meeting.date || ''],
        ['Time', `${meeting.startTime || ''} - ${meeting.endTime || ''}`],
        ['Location', meeting.location || ''],
        ['Facilitator', meeting.facilitator || ''],
        ['Note Taker', meeting.noteTaker || ''],
      ].map(([label, value]) => new TableRow({
        children: [
          new TableCell({ width: { size: 20, type: WidthType.PERCENTAGE }, shading: { type: ShadingType.SOLID, color: 'F0F4F8' }, children: [new Paragraph({ children: [new TextRun({ text: label, bold: true, size: 20 })] })] }),
          new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: value, size: 20 })] })] }),
        ]
      })),
      spacing: { after: 240 },
    }),

    // Attendees
    new Paragraph({ children: [new TextRun({ text: 'ATTENDEES', bold: true, size: 22, color: primaryColor })], spacing: { before: 120, after: 80 } }),
    ...(meeting.attendees || []).map(a => new Paragraph({ children: [new TextRun({ text: `${a.name || a} — ${a.role || ''}`, size: 20 })], bullet: { level: 0 }, spacing: { after: 40 } })),

    // Agenda
    ...(meeting.agenda?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'AGENDA', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      ...meeting.agenda.map((item, i) => new Paragraph({ children: [new TextRun({ text: `${i + 1}. ${item}`, size: 20 })], spacing: { after: 40 } })),
    ] : []),

    // Discussion points
    ...(meeting.discussionPoints?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'DISCUSSION', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),
      ...meeting.discussionPoints.flatMap(point => [
        new Paragraph({ children: [new TextRun({ text: point.topic, bold: true, size: 22 })], spacing: { before: 120, after: 60 } }),
        new Paragraph({ children: [new TextRun({ text: point.summary || '', size: 20 })], spacing: { after: 80 } }),
        ...(point.decisions || []).map(d => new Paragraph({ children: [new TextRun({ text: `Decision: ${d}`, size: 20, bold: true, color: primaryColor })], spacing: { after: 40 } })),
      ]),
    ] : []),

    // Action items
    ...(meeting.actionItems?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'ACTION ITEMS', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),
      new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        rows: [
          new TableRow({
            tableHeader: true,
            children: ['Action', 'Owner', 'Due Date', 'Status'].map(h => new TableCell({ shading: { type: ShadingType.SOLID, color: primaryColor }, children: [new Paragraph({ children: [new TextRun({ text: h, bold: true, color: 'FFFFFF', size: 20 })] })] }))
          }),
          ...(meeting.actionItems || []).map((item, i) => new TableRow({
            children: [
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.action || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.owner || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.dueDate || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.status || 'Open', size: 20 })] })] }),
            ],
            shading: i % 2 !== 0 ? { type: ShadingType.SOLID, color: 'F9F9F9' } : undefined,
          }))
        ]
      }),
    ] : []),

    // Next meeting
    ...(meeting.nextMeeting ? [
      new Paragraph({ children: [new TextRun({ text: 'NEXT MEETING', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: `Date: ${meeting.nextMeeting.date || ''}`, size: 20 })], spacing: { after: 40 } }),
      new Paragraph({ children: [new TextRun({ text: `Location: ${meeting.nextMeeting.location || ''}`, size: 20 })], spacing: { after: 40 } }),
    ] : []),
  ];

  const doc = new Document({
    styles: getDefaultDocumentStyles(branding),
    sections: [{ properties: { page: { size: PAGE_SIZES.LETTER, margin: PAGE_MARGINS.NORMAL } }, children }]
  });

  return await Packer.toBuffer(doc);
}

Object.assign(module.exports, {
  generateContract,
  generateMeetingMinutes,
});


// ─── Additional Template Utilities ───────────────────────────────────────────

/**
 * Generate a contract or agreement document.
 * @param {Object} contract - Contract data
 * @param {Object} [options] - Template options
 * @returns {Promise<Buffer>} Document buffer
 *
 * @example
 * const buffer = await generateContract({
 *   title: 'Service Agreement',
 *   parties: [
 *     { role: 'Client', name: 'ACME Corp', address: '123 Main St', representative: 'John Smith', title: 'CEO' },
 *     { role: 'Provider', name: 'TechCo LLC', address: '456 Oak Ave', representative: 'Jane Doe', title: 'Managing Director' },
 *   ],
 *   effectiveDate: 'January 1, 2025',
 *   termination: 'December 31, 2025',
 *   clauses: [
 *     { title: '1. Services', body: 'Provider agrees to...' },
 *     { title: '2. Payment', body: 'Client agrees to pay...' },
 *     { title: '3. Confidentiality', body: 'Both parties agree...' },
 *   ],
 *   governingLaw: 'New York, USA',
 * });
 */
async function generateContract(contract, options = {}) {
  const { branding = {} } = options;
  const primaryColor = branding.primaryColor || '1A237E';

  const children = [
    // Title
    new Paragraph({
      children: [new TextRun({ text: (contract.title || 'AGREEMENT').toUpperCase(), bold: true, size: 36, color: primaryColor })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 240 },
    }),

    new Paragraph({
      children: [new TextRun({ text: `Effective Date: ${contract.effectiveDate || ''}`, size: 20, italics: true })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 400 },
    }),

    // Parties
    new Paragraph({ children: [new TextRun({ text: 'PARTIES', bold: true, size: 24, color: primaryColor })], spacing: { before: 120, after: 80 } }),

    ...(contract.parties || []).flatMap(party => [
      new Paragraph({ children: [new TextRun({ text: `${party.role}: `, bold: true, size: 22 }), new TextRun({ text: party.name, size: 22 })] }),
      new Paragraph({ children: [new TextRun({ text: `Address: ${party.address || ''}`, size: 20, color: '555555' })] }),
      new Paragraph({ children: [new TextRun({ text: `Representative: ${party.representative || ''}, ${party.title || ''}`, size: 20, color: '555555' })], spacing: { after: 120 } }),
    ]),

    // Recitals
    ...(contract.recitals ? [
      new Paragraph({ children: [new TextRun({ text: 'RECITALS', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: contract.recitals, size: 20 })], spacing: { after: 200 } }),
    ] : []),

    // Terms
    new Paragraph({ children: [new TextRun({ text: 'TERMS AND CONDITIONS', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),

    // Clauses
    ...(contract.clauses || []).flatMap(clause => [
      new Paragraph({ children: [new TextRun({ text: clause.title, bold: true, size: 22 })], spacing: { before: 160, after: 80 } }),
      ...clause.body.split('\n').map(line => new Paragraph({ children: [new TextRun({ text: line, size: 20 })], spacing: { after: 80 } })),
    ]),

    // Governing law
    ...(contract.governingLaw ? [
      new Paragraph({ children: [new TextRun({ text: `Governing Law`, bold: true, size: 22 })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: `This Agreement shall be governed by the laws of ${contract.governingLaw}.`, size: 20 })], spacing: { after: 200 } }),
    ] : []),

    // Signature block
    new Paragraph({ children: [new TextRun({ text: 'SIGNATURES', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),

    buildSignatureTable(contract.parties || []),
  ];

  const doc = new Document({
    styles: getDefaultDocumentStyles(branding),
    sections: [{
      properties: { page: { size: PAGE_SIZES.LETTER, margin: PAGE_MARGINS.NORMAL } },
      children,
    }]
  });

  return await Packer.toBuffer(doc);
}

function buildSignatureTable(parties) {
  const cols = Math.min(parties.length, 3);
  const colWidth = Math.floor(100 / cols);

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE }, insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE } },
    rows: [
      new TableRow({
        children: parties.slice(0, cols).map(party => new TableCell({
          width: { size: colWidth, type: WidthType.PERCENTAGE },
          children: [
            new Paragraph({ children: [new TextRun({ text: party.role, bold: true, size: 20 })], spacing: { after: 400 } }),
            new Paragraph({ children: [new TextRun({ text: '_________________________', size: 20 })], spacing: { after: 60 } }),
            new Paragraph({ children: [new TextRun({ text: `Signature`, size: 16, color: '999999' })], spacing: { after: 200 } }),
            new Paragraph({ children: [new TextRun({ text: party.representative || '', bold: true, size: 20 })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: party.title || '', size: 18, color: '666666' })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: party.name, size: 18, color: '666666' })], spacing: { after: 200 } }),
            new Paragraph({ children: [new TextRun({ text: '_________________________', size: 20 })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: 'Date', size: 16, color: '999999' })] }),
          ],
        }))
      })
    ]
  });
}

/**
 * Generate a meeting minutes document.
 * @param {Object} meeting - Meeting data
 * @returns {Promise<Buffer>} Document buffer
 */
async function generateMeetingMinutes(meeting, options = {}) {
  const { branding = {} } = options;
  const primaryColor = branding.primaryColor || '1B5E20';

  const children = [
    new Paragraph({ children: [new TextRun({ text: 'MEETING MINUTES', bold: true, size: 40, color: primaryColor })], alignment: AlignmentType.CENTER, spacing: { after: 80 } }),
    new Paragraph({ children: [new TextRun({ text: meeting.title || '', size: 28, color: '333333' })], alignment: AlignmentType.CENTER, spacing: { after: 240 } }),

    // Meeting details table
    new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      rows: [
        ['Date', meeting.date || ''],
        ['Time', `${meeting.startTime || ''} - ${meeting.endTime || ''}`],
        ['Location', meeting.location || ''],
        ['Facilitator', meeting.facilitator || ''],
        ['Note Taker', meeting.noteTaker || ''],
      ].map(([label, value]) => new TableRow({
        children: [
          new TableCell({ width: { size: 20, type: WidthType.PERCENTAGE }, shading: { type: ShadingType.SOLID, color: 'F0F4F8' }, children: [new Paragraph({ children: [new TextRun({ text: label, bold: true, size: 20 })] })] }),
          new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: value, size: 20 })] })] }),
        ]
      })),
      spacing: { after: 240 },
    }),

    // Attendees
    new Paragraph({ children: [new TextRun({ text: 'ATTENDEES', bold: true, size: 22, color: primaryColor })], spacing: { before: 120, after: 80 } }),
    ...(meeting.attendees || []).map(a => new Paragraph({ children: [new TextRun({ text: `${a.name || a} — ${a.role || ''}`, size: 20 })], bullet: { level: 0 }, spacing: { after: 40 } })),

    // Agenda
    ...(meeting.agenda?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'AGENDA', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      ...meeting.agenda.map((item, i) => new Paragraph({ children: [new TextRun({ text: `${i + 1}. ${item}`, size: 20 })], spacing: { after: 40 } })),
    ] : []),

    // Discussion points
    ...(meeting.discussionPoints?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'DISCUSSION', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),
      ...meeting.discussionPoints.flatMap(point => [
        new Paragraph({ children: [new TextRun({ text: point.topic, bold: true, size: 22 })], spacing: { before: 120, after: 60 } }),
        new Paragraph({ children: [new TextRun({ text: point.summary || '', size: 20 })], spacing: { after: 80 } }),
        ...(point.decisions || []).map(d => new Paragraph({ children: [new TextRun({ text: `Decision: ${d}`, size: 20, bold: true, color: primaryColor })], spacing: { after: 40 } })),
      ]),
    ] : []),

    // Action items
    ...(meeting.actionItems?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'ACTION ITEMS', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),
      new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        rows: [
          new TableRow({
            tableHeader: true,
            children: ['Action', 'Owner', 'Due Date', 'Status'].map(h => new TableCell({ shading: { type: ShadingType.SOLID, color: primaryColor }, children: [new Paragraph({ children: [new TextRun({ text: h, bold: true, color: 'FFFFFF', size: 20 })] })] }))
          }),
          ...(meeting.actionItems || []).map((item, i) => new TableRow({
            children: [
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.action || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.owner || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.dueDate || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.status || 'Open', size: 20 })] })] }),
            ],
            shading: i % 2 !== 0 ? { type: ShadingType.SOLID, color: 'F9F9F9' } : undefined,
          }))
        ]
      }),
    ] : []),

    // Next meeting
    ...(meeting.nextMeeting ? [
      new Paragraph({ children: [new TextRun({ text: 'NEXT MEETING', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: `Date: ${meeting.nextMeeting.date || ''}`, size: 20 })], spacing: { after: 40 } }),
      new Paragraph({ children: [new TextRun({ text: `Location: ${meeting.nextMeeting.location || ''}`, size: 20 })], spacing: { after: 40 } }),
    ] : []),
  ];

  const doc = new Document({
    styles: getDefaultDocumentStyles(branding),
    sections: [{ properties: { page: { size: PAGE_SIZES.LETTER, margin: PAGE_MARGINS.NORMAL } }, children }]
  });

  return await Packer.toBuffer(doc);
}

Object.assign(module.exports, {
  generateContract,
  generateMeetingMinutes,
});


// ─── Additional Template Utilities ───────────────────────────────────────────

/**
 * Generate a contract or agreement document.
 * @param {Object} contract - Contract data
 * @param {Object} [options] - Template options
 * @returns {Promise<Buffer>} Document buffer
 *
 * @example
 * const buffer = await generateContract({
 *   title: 'Service Agreement',
 *   parties: [
 *     { role: 'Client', name: 'ACME Corp', address: '123 Main St', representative: 'John Smith', title: 'CEO' },
 *     { role: 'Provider', name: 'TechCo LLC', address: '456 Oak Ave', representative: 'Jane Doe', title: 'Managing Director' },
 *   ],
 *   effectiveDate: 'January 1, 2025',
 *   termination: 'December 31, 2025',
 *   clauses: [
 *     { title: '1. Services', body: 'Provider agrees to...' },
 *     { title: '2. Payment', body: 'Client agrees to pay...' },
 *     { title: '3. Confidentiality', body: 'Both parties agree...' },
 *   ],
 *   governingLaw: 'New York, USA',
 * });
 */
async function generateContract(contract, options = {}) {
  const { branding = {} } = options;
  const primaryColor = branding.primaryColor || '1A237E';

  const children = [
    // Title
    new Paragraph({
      children: [new TextRun({ text: (contract.title || 'AGREEMENT').toUpperCase(), bold: true, size: 36, color: primaryColor })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 240 },
    }),

    new Paragraph({
      children: [new TextRun({ text: `Effective Date: ${contract.effectiveDate || ''}`, size: 20, italics: true })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 400 },
    }),

    // Parties
    new Paragraph({ children: [new TextRun({ text: 'PARTIES', bold: true, size: 24, color: primaryColor })], spacing: { before: 120, after: 80 } }),

    ...(contract.parties || []).flatMap(party => [
      new Paragraph({ children: [new TextRun({ text: `${party.role}: `, bold: true, size: 22 }), new TextRun({ text: party.name, size: 22 })] }),
      new Paragraph({ children: [new TextRun({ text: `Address: ${party.address || ''}`, size: 20, color: '555555' })] }),
      new Paragraph({ children: [new TextRun({ text: `Representative: ${party.representative || ''}, ${party.title || ''}`, size: 20, color: '555555' })], spacing: { after: 120 } }),
    ]),

    // Recitals
    ...(contract.recitals ? [
      new Paragraph({ children: [new TextRun({ text: 'RECITALS', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: contract.recitals, size: 20 })], spacing: { after: 200 } }),
    ] : []),

    // Terms
    new Paragraph({ children: [new TextRun({ text: 'TERMS AND CONDITIONS', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),

    // Clauses
    ...(contract.clauses || []).flatMap(clause => [
      new Paragraph({ children: [new TextRun({ text: clause.title, bold: true, size: 22 })], spacing: { before: 160, after: 80 } }),
      ...clause.body.split('\n').map(line => new Paragraph({ children: [new TextRun({ text: line, size: 20 })], spacing: { after: 80 } })),
    ]),

    // Governing law
    ...(contract.governingLaw ? [
      new Paragraph({ children: [new TextRun({ text: `Governing Law`, bold: true, size: 22 })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: `This Agreement shall be governed by the laws of ${contract.governingLaw}.`, size: 20 })], spacing: { after: 200 } }),
    ] : []),

    // Signature block
    new Paragraph({ children: [new TextRun({ text: 'SIGNATURES', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),

    buildSignatureTable(contract.parties || []),
  ];

  const doc = new Document({
    styles: getDefaultDocumentStyles(branding),
    sections: [{
      properties: { page: { size: PAGE_SIZES.LETTER, margin: PAGE_MARGINS.NORMAL } },
      children,
    }]
  });

  return await Packer.toBuffer(doc);
}

function buildSignatureTable(parties) {
  const cols = Math.min(parties.length, 3);
  const colWidth = Math.floor(100 / cols);

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE }, insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE } },
    rows: [
      new TableRow({
        children: parties.slice(0, cols).map(party => new TableCell({
          width: { size: colWidth, type: WidthType.PERCENTAGE },
          children: [
            new Paragraph({ children: [new TextRun({ text: party.role, bold: true, size: 20 })], spacing: { after: 400 } }),
            new Paragraph({ children: [new TextRun({ text: '_________________________', size: 20 })], spacing: { after: 60 } }),
            new Paragraph({ children: [new TextRun({ text: `Signature`, size: 16, color: '999999' })], spacing: { after: 200 } }),
            new Paragraph({ children: [new TextRun({ text: party.representative || '', bold: true, size: 20 })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: party.title || '', size: 18, color: '666666' })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: party.name, size: 18, color: '666666' })], spacing: { after: 200 } }),
            new Paragraph({ children: [new TextRun({ text: '_________________________', size: 20 })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: 'Date', size: 16, color: '999999' })] }),
          ],
        }))
      })
    ]
  });
}

/**
 * Generate a meeting minutes document.
 * @param {Object} meeting - Meeting data
 * @returns {Promise<Buffer>} Document buffer
 */
async function generateMeetingMinutes(meeting, options = {}) {
  const { branding = {} } = options;
  const primaryColor = branding.primaryColor || '1B5E20';

  const children = [
    new Paragraph({ children: [new TextRun({ text: 'MEETING MINUTES', bold: true, size: 40, color: primaryColor })], alignment: AlignmentType.CENTER, spacing: { after: 80 } }),
    new Paragraph({ children: [new TextRun({ text: meeting.title || '', size: 28, color: '333333' })], alignment: AlignmentType.CENTER, spacing: { after: 240 } }),

    // Meeting details table
    new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      rows: [
        ['Date', meeting.date || ''],
        ['Time', `${meeting.startTime || ''} - ${meeting.endTime || ''}`],
        ['Location', meeting.location || ''],
        ['Facilitator', meeting.facilitator || ''],
        ['Note Taker', meeting.noteTaker || ''],
      ].map(([label, value]) => new TableRow({
        children: [
          new TableCell({ width: { size: 20, type: WidthType.PERCENTAGE }, shading: { type: ShadingType.SOLID, color: 'F0F4F8' }, children: [new Paragraph({ children: [new TextRun({ text: label, bold: true, size: 20 })] })] }),
          new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: value, size: 20 })] })] }),
        ]
      })),
      spacing: { after: 240 },
    }),

    // Attendees
    new Paragraph({ children: [new TextRun({ text: 'ATTENDEES', bold: true, size: 22, color: primaryColor })], spacing: { before: 120, after: 80 } }),
    ...(meeting.attendees || []).map(a => new Paragraph({ children: [new TextRun({ text: `${a.name || a} — ${a.role || ''}`, size: 20 })], bullet: { level: 0 }, spacing: { after: 40 } })),

    // Agenda
    ...(meeting.agenda?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'AGENDA', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      ...meeting.agenda.map((item, i) => new Paragraph({ children: [new TextRun({ text: `${i + 1}. ${item}`, size: 20 })], spacing: { after: 40 } })),
    ] : []),

    // Discussion points
    ...(meeting.discussionPoints?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'DISCUSSION', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),
      ...meeting.discussionPoints.flatMap(point => [
        new Paragraph({ children: [new TextRun({ text: point.topic, bold: true, size: 22 })], spacing: { before: 120, after: 60 } }),
        new Paragraph({ children: [new TextRun({ text: point.summary || '', size: 20 })], spacing: { after: 80 } }),
        ...(point.decisions || []).map(d => new Paragraph({ children: [new TextRun({ text: `Decision: ${d}`, size: 20, bold: true, color: primaryColor })], spacing: { after: 40 } })),
      ]),
    ] : []),

    // Action items
    ...(meeting.actionItems?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'ACTION ITEMS', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),
      new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        rows: [
          new TableRow({
            tableHeader: true,
            children: ['Action', 'Owner', 'Due Date', 'Status'].map(h => new TableCell({ shading: { type: ShadingType.SOLID, color: primaryColor }, children: [new Paragraph({ children: [new TextRun({ text: h, bold: true, color: 'FFFFFF', size: 20 })] })] }))
          }),
          ...(meeting.actionItems || []).map((item, i) => new TableRow({
            children: [
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.action || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.owner || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.dueDate || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.status || 'Open', size: 20 })] })] }),
            ],
            shading: i % 2 !== 0 ? { type: ShadingType.SOLID, color: 'F9F9F9' } : undefined,
          }))
        ]
      }),
    ] : []),

    // Next meeting
    ...(meeting.nextMeeting ? [
      new Paragraph({ children: [new TextRun({ text: 'NEXT MEETING', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: `Date: ${meeting.nextMeeting.date || ''}`, size: 20 })], spacing: { after: 40 } }),
      new Paragraph({ children: [new TextRun({ text: `Location: ${meeting.nextMeeting.location || ''}`, size: 20 })], spacing: { after: 40 } }),
    ] : []),
  ];

  const doc = new Document({
    styles: getDefaultDocumentStyles(branding),
    sections: [{ properties: { page: { size: PAGE_SIZES.LETTER, margin: PAGE_MARGINS.NORMAL } }, children }]
  });

  return await Packer.toBuffer(doc);
}

Object.assign(module.exports, {
  generateContract,
  generateMeetingMinutes,
});


// ─── Additional Template Utilities ───────────────────────────────────────────

/**
 * Generate a contract or agreement document.
 * @param {Object} contract - Contract data
 * @param {Object} [options] - Template options
 * @returns {Promise<Buffer>} Document buffer
 *
 * @example
 * const buffer = await generateContract({
 *   title: 'Service Agreement',
 *   parties: [
 *     { role: 'Client', name: 'ACME Corp', address: '123 Main St', representative: 'John Smith', title: 'CEO' },
 *     { role: 'Provider', name: 'TechCo LLC', address: '456 Oak Ave', representative: 'Jane Doe', title: 'Managing Director' },
 *   ],
 *   effectiveDate: 'January 1, 2025',
 *   termination: 'December 31, 2025',
 *   clauses: [
 *     { title: '1. Services', body: 'Provider agrees to...' },
 *     { title: '2. Payment', body: 'Client agrees to pay...' },
 *     { title: '3. Confidentiality', body: 'Both parties agree...' },
 *   ],
 *   governingLaw: 'New York, USA',
 * });
 */
async function generateContract(contract, options = {}) {
  const { branding = {} } = options;
  const primaryColor = branding.primaryColor || '1A237E';

  const children = [
    // Title
    new Paragraph({
      children: [new TextRun({ text: (contract.title || 'AGREEMENT').toUpperCase(), bold: true, size: 36, color: primaryColor })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 240 },
    }),

    new Paragraph({
      children: [new TextRun({ text: `Effective Date: ${contract.effectiveDate || ''}`, size: 20, italics: true })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 400 },
    }),

    // Parties
    new Paragraph({ children: [new TextRun({ text: 'PARTIES', bold: true, size: 24, color: primaryColor })], spacing: { before: 120, after: 80 } }),

    ...(contract.parties || []).flatMap(party => [
      new Paragraph({ children: [new TextRun({ text: `${party.role}: `, bold: true, size: 22 }), new TextRun({ text: party.name, size: 22 })] }),
      new Paragraph({ children: [new TextRun({ text: `Address: ${party.address || ''}`, size: 20, color: '555555' })] }),
      new Paragraph({ children: [new TextRun({ text: `Representative: ${party.representative || ''}, ${party.title || ''}`, size: 20, color: '555555' })], spacing: { after: 120 } }),
    ]),

    // Recitals
    ...(contract.recitals ? [
      new Paragraph({ children: [new TextRun({ text: 'RECITALS', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: contract.recitals, size: 20 })], spacing: { after: 200 } }),
    ] : []),

    // Terms
    new Paragraph({ children: [new TextRun({ text: 'TERMS AND CONDITIONS', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),

    // Clauses
    ...(contract.clauses || []).flatMap(clause => [
      new Paragraph({ children: [new TextRun({ text: clause.title, bold: true, size: 22 })], spacing: { before: 160, after: 80 } }),
      ...clause.body.split('\n').map(line => new Paragraph({ children: [new TextRun({ text: line, size: 20 })], spacing: { after: 80 } })),
    ]),

    // Governing law
    ...(contract.governingLaw ? [
      new Paragraph({ children: [new TextRun({ text: `Governing Law`, bold: true, size: 22 })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: `This Agreement shall be governed by the laws of ${contract.governingLaw}.`, size: 20 })], spacing: { after: 200 } }),
    ] : []),

    // Signature block
    new Paragraph({ children: [new TextRun({ text: 'SIGNATURES', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),

    buildSignatureTable(contract.parties || []),
  ];

  const doc = new Document({
    styles: getDefaultDocumentStyles(branding),
    sections: [{
      properties: { page: { size: PAGE_SIZES.LETTER, margin: PAGE_MARGINS.NORMAL } },
      children,
    }]
  });

  return await Packer.toBuffer(doc);
}

function buildSignatureTable(parties) {
  const cols = Math.min(parties.length, 3);
  const colWidth = Math.floor(100 / cols);

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE }, insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE } },
    rows: [
      new TableRow({
        children: parties.slice(0, cols).map(party => new TableCell({
          width: { size: colWidth, type: WidthType.PERCENTAGE },
          children: [
            new Paragraph({ children: [new TextRun({ text: party.role, bold: true, size: 20 })], spacing: { after: 400 } }),
            new Paragraph({ children: [new TextRun({ text: '_________________________', size: 20 })], spacing: { after: 60 } }),
            new Paragraph({ children: [new TextRun({ text: `Signature`, size: 16, color: '999999' })], spacing: { after: 200 } }),
            new Paragraph({ children: [new TextRun({ text: party.representative || '', bold: true, size: 20 })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: party.title || '', size: 18, color: '666666' })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: party.name, size: 18, color: '666666' })], spacing: { after: 200 } }),
            new Paragraph({ children: [new TextRun({ text: '_________________________', size: 20 })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: 'Date', size: 16, color: '999999' })] }),
          ],
        }))
      })
    ]
  });
}

/**
 * Generate a meeting minutes document.
 * @param {Object} meeting - Meeting data
 * @returns {Promise<Buffer>} Document buffer
 */
async function generateMeetingMinutes(meeting, options = {}) {
  const { branding = {} } = options;
  const primaryColor = branding.primaryColor || '1B5E20';

  const children = [
    new Paragraph({ children: [new TextRun({ text: 'MEETING MINUTES', bold: true, size: 40, color: primaryColor })], alignment: AlignmentType.CENTER, spacing: { after: 80 } }),
    new Paragraph({ children: [new TextRun({ text: meeting.title || '', size: 28, color: '333333' })], alignment: AlignmentType.CENTER, spacing: { after: 240 } }),

    // Meeting details table
    new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      rows: [
        ['Date', meeting.date || ''],
        ['Time', `${meeting.startTime || ''} - ${meeting.endTime || ''}`],
        ['Location', meeting.location || ''],
        ['Facilitator', meeting.facilitator || ''],
        ['Note Taker', meeting.noteTaker || ''],
      ].map(([label, value]) => new TableRow({
        children: [
          new TableCell({ width: { size: 20, type: WidthType.PERCENTAGE }, shading: { type: ShadingType.SOLID, color: 'F0F4F8' }, children: [new Paragraph({ children: [new TextRun({ text: label, bold: true, size: 20 })] })] }),
          new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: value, size: 20 })] })] }),
        ]
      })),
      spacing: { after: 240 },
    }),

    // Attendees
    new Paragraph({ children: [new TextRun({ text: 'ATTENDEES', bold: true, size: 22, color: primaryColor })], spacing: { before: 120, after: 80 } }),
    ...(meeting.attendees || []).map(a => new Paragraph({ children: [new TextRun({ text: `${a.name || a} — ${a.role || ''}`, size: 20 })], bullet: { level: 0 }, spacing: { after: 40 } })),

    // Agenda
    ...(meeting.agenda?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'AGENDA', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      ...meeting.agenda.map((item, i) => new Paragraph({ children: [new TextRun({ text: `${i + 1}. ${item}`, size: 20 })], spacing: { after: 40 } })),
    ] : []),

    // Discussion points
    ...(meeting.discussionPoints?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'DISCUSSION', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),
      ...meeting.discussionPoints.flatMap(point => [
        new Paragraph({ children: [new TextRun({ text: point.topic, bold: true, size: 22 })], spacing: { before: 120, after: 60 } }),
        new Paragraph({ children: [new TextRun({ text: point.summary || '', size: 20 })], spacing: { after: 80 } }),
        ...(point.decisions || []).map(d => new Paragraph({ children: [new TextRun({ text: `Decision: ${d}`, size: 20, bold: true, color: primaryColor })], spacing: { after: 40 } })),
      ]),
    ] : []),

    // Action items
    ...(meeting.actionItems?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'ACTION ITEMS', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),
      new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        rows: [
          new TableRow({
            tableHeader: true,
            children: ['Action', 'Owner', 'Due Date', 'Status'].map(h => new TableCell({ shading: { type: ShadingType.SOLID, color: primaryColor }, children: [new Paragraph({ children: [new TextRun({ text: h, bold: true, color: 'FFFFFF', size: 20 })] })] }))
          }),
          ...(meeting.actionItems || []).map((item, i) => new TableRow({
            children: [
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.action || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.owner || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.dueDate || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.status || 'Open', size: 20 })] })] }),
            ],
            shading: i % 2 !== 0 ? { type: ShadingType.SOLID, color: 'F9F9F9' } : undefined,
          }))
        ]
      }),
    ] : []),

    // Next meeting
    ...(meeting.nextMeeting ? [
      new Paragraph({ children: [new TextRun({ text: 'NEXT MEETING', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: `Date: ${meeting.nextMeeting.date || ''}`, size: 20 })], spacing: { after: 40 } }),
      new Paragraph({ children: [new TextRun({ text: `Location: ${meeting.nextMeeting.location || ''}`, size: 20 })], spacing: { after: 40 } }),
    ] : []),
  ];

  const doc = new Document({
    styles: getDefaultDocumentStyles(branding),
    sections: [{ properties: { page: { size: PAGE_SIZES.LETTER, margin: PAGE_MARGINS.NORMAL } }, children }]
  });

  return await Packer.toBuffer(doc);
}

Object.assign(module.exports, {
  generateContract,
  generateMeetingMinutes,
});


// ─── Additional Template Utilities ───────────────────────────────────────────

/**
 * Generate a contract or agreement document.
 * @param {Object} contract - Contract data
 * @param {Object} [options] - Template options
 * @returns {Promise<Buffer>} Document buffer
 *
 * @example
 * const buffer = await generateContract({
 *   title: 'Service Agreement',
 *   parties: [
 *     { role: 'Client', name: 'ACME Corp', address: '123 Main St', representative: 'John Smith', title: 'CEO' },
 *     { role: 'Provider', name: 'TechCo LLC', address: '456 Oak Ave', representative: 'Jane Doe', title: 'Managing Director' },
 *   ],
 *   effectiveDate: 'January 1, 2025',
 *   termination: 'December 31, 2025',
 *   clauses: [
 *     { title: '1. Services', body: 'Provider agrees to...' },
 *     { title: '2. Payment', body: 'Client agrees to pay...' },
 *     { title: '3. Confidentiality', body: 'Both parties agree...' },
 *   ],
 *   governingLaw: 'New York, USA',
 * });
 */
async function generateContract(contract, options = {}) {
  const { branding = {} } = options;
  const primaryColor = branding.primaryColor || '1A237E';

  const children = [
    // Title
    new Paragraph({
      children: [new TextRun({ text: (contract.title || 'AGREEMENT').toUpperCase(), bold: true, size: 36, color: primaryColor })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 240 },
    }),

    new Paragraph({
      children: [new TextRun({ text: `Effective Date: ${contract.effectiveDate || ''}`, size: 20, italics: true })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 400 },
    }),

    // Parties
    new Paragraph({ children: [new TextRun({ text: 'PARTIES', bold: true, size: 24, color: primaryColor })], spacing: { before: 120, after: 80 } }),

    ...(contract.parties || []).flatMap(party => [
      new Paragraph({ children: [new TextRun({ text: `${party.role}: `, bold: true, size: 22 }), new TextRun({ text: party.name, size: 22 })] }),
      new Paragraph({ children: [new TextRun({ text: `Address: ${party.address || ''}`, size: 20, color: '555555' })] }),
      new Paragraph({ children: [new TextRun({ text: `Representative: ${party.representative || ''}, ${party.title || ''}`, size: 20, color: '555555' })], spacing: { after: 120 } }),
    ]),

    // Recitals
    ...(contract.recitals ? [
      new Paragraph({ children: [new TextRun({ text: 'RECITALS', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: contract.recitals, size: 20 })], spacing: { after: 200 } }),
    ] : []),

    // Terms
    new Paragraph({ children: [new TextRun({ text: 'TERMS AND CONDITIONS', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),

    // Clauses
    ...(contract.clauses || []).flatMap(clause => [
      new Paragraph({ children: [new TextRun({ text: clause.title, bold: true, size: 22 })], spacing: { before: 160, after: 80 } }),
      ...clause.body.split('\n').map(line => new Paragraph({ children: [new TextRun({ text: line, size: 20 })], spacing: { after: 80 } })),
    ]),

    // Governing law
    ...(contract.governingLaw ? [
      new Paragraph({ children: [new TextRun({ text: `Governing Law`, bold: true, size: 22 })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: `This Agreement shall be governed by the laws of ${contract.governingLaw}.`, size: 20 })], spacing: { after: 200 } }),
    ] : []),

    // Signature block
    new Paragraph({ children: [new TextRun({ text: 'SIGNATURES', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),

    buildSignatureTable(contract.parties || []),
  ];

  const doc = new Document({
    styles: getDefaultDocumentStyles(branding),
    sections: [{
      properties: { page: { size: PAGE_SIZES.LETTER, margin: PAGE_MARGINS.NORMAL } },
      children,
    }]
  });

  return await Packer.toBuffer(doc);
}

function buildSignatureTable(parties) {
  const cols = Math.min(parties.length, 3);
  const colWidth = Math.floor(100 / cols);

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE }, insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE } },
    rows: [
      new TableRow({
        children: parties.slice(0, cols).map(party => new TableCell({
          width: { size: colWidth, type: WidthType.PERCENTAGE },
          children: [
            new Paragraph({ children: [new TextRun({ text: party.role, bold: true, size: 20 })], spacing: { after: 400 } }),
            new Paragraph({ children: [new TextRun({ text: '_________________________', size: 20 })], spacing: { after: 60 } }),
            new Paragraph({ children: [new TextRun({ text: `Signature`, size: 16, color: '999999' })], spacing: { after: 200 } }),
            new Paragraph({ children: [new TextRun({ text: party.representative || '', bold: true, size: 20 })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: party.title || '', size: 18, color: '666666' })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: party.name, size: 18, color: '666666' })], spacing: { after: 200 } }),
            new Paragraph({ children: [new TextRun({ text: '_________________________', size: 20 })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: 'Date', size: 16, color: '999999' })] }),
          ],
        }))
      })
    ]
  });
}

/**
 * Generate a meeting minutes document.
 * @param {Object} meeting - Meeting data
 * @returns {Promise<Buffer>} Document buffer
 */
async function generateMeetingMinutes(meeting, options = {}) {
  const { branding = {} } = options;
  const primaryColor = branding.primaryColor || '1B5E20';

  const children = [
    new Paragraph({ children: [new TextRun({ text: 'MEETING MINUTES', bold: true, size: 40, color: primaryColor })], alignment: AlignmentType.CENTER, spacing: { after: 80 } }),
    new Paragraph({ children: [new TextRun({ text: meeting.title || '', size: 28, color: '333333' })], alignment: AlignmentType.CENTER, spacing: { after: 240 } }),

    // Meeting details table
    new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      rows: [
        ['Date', meeting.date || ''],
        ['Time', `${meeting.startTime || ''} - ${meeting.endTime || ''}`],
        ['Location', meeting.location || ''],
        ['Facilitator', meeting.facilitator || ''],
        ['Note Taker', meeting.noteTaker || ''],
      ].map(([label, value]) => new TableRow({
        children: [
          new TableCell({ width: { size: 20, type: WidthType.PERCENTAGE }, shading: { type: ShadingType.SOLID, color: 'F0F4F8' }, children: [new Paragraph({ children: [new TextRun({ text: label, bold: true, size: 20 })] })] }),
          new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: value, size: 20 })] })] }),
        ]
      })),
      spacing: { after: 240 },
    }),

    // Attendees
    new Paragraph({ children: [new TextRun({ text: 'ATTENDEES', bold: true, size: 22, color: primaryColor })], spacing: { before: 120, after: 80 } }),
    ...(meeting.attendees || []).map(a => new Paragraph({ children: [new TextRun({ text: `${a.name || a} — ${a.role || ''}`, size: 20 })], bullet: { level: 0 }, spacing: { after: 40 } })),

    // Agenda
    ...(meeting.agenda?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'AGENDA', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      ...meeting.agenda.map((item, i) => new Paragraph({ children: [new TextRun({ text: `${i + 1}. ${item}`, size: 20 })], spacing: { after: 40 } })),
    ] : []),

    // Discussion points
    ...(meeting.discussionPoints?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'DISCUSSION', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),
      ...meeting.discussionPoints.flatMap(point => [
        new Paragraph({ children: [new TextRun({ text: point.topic, bold: true, size: 22 })], spacing: { before: 120, after: 60 } }),
        new Paragraph({ children: [new TextRun({ text: point.summary || '', size: 20 })], spacing: { after: 80 } }),
        ...(point.decisions || []).map(d => new Paragraph({ children: [new TextRun({ text: `Decision: ${d}`, size: 20, bold: true, color: primaryColor })], spacing: { after: 40 } })),
      ]),
    ] : []),

    // Action items
    ...(meeting.actionItems?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'ACTION ITEMS', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),
      new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        rows: [
          new TableRow({
            tableHeader: true,
            children: ['Action', 'Owner', 'Due Date', 'Status'].map(h => new TableCell({ shading: { type: ShadingType.SOLID, color: primaryColor }, children: [new Paragraph({ children: [new TextRun({ text: h, bold: true, color: 'FFFFFF', size: 20 })] })] }))
          }),
          ...(meeting.actionItems || []).map((item, i) => new TableRow({
            children: [
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.action || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.owner || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.dueDate || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.status || 'Open', size: 20 })] })] }),
            ],
            shading: i % 2 !== 0 ? { type: ShadingType.SOLID, color: 'F9F9F9' } : undefined,
          }))
        ]
      }),
    ] : []),

    // Next meeting
    ...(meeting.nextMeeting ? [
      new Paragraph({ children: [new TextRun({ text: 'NEXT MEETING', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: `Date: ${meeting.nextMeeting.date || ''}`, size: 20 })], spacing: { after: 40 } }),
      new Paragraph({ children: [new TextRun({ text: `Location: ${meeting.nextMeeting.location || ''}`, size: 20 })], spacing: { after: 40 } }),
    ] : []),
  ];

  const doc = new Document({
    styles: getDefaultDocumentStyles(branding),
    sections: [{ properties: { page: { size: PAGE_SIZES.LETTER, margin: PAGE_MARGINS.NORMAL } }, children }]
  });

  return await Packer.toBuffer(doc);
}

Object.assign(module.exports, {
  generateContract,
  generateMeetingMinutes,
});


// ─── Additional Template Utilities ───────────────────────────────────────────

/**
 * Generate a contract or agreement document.
 * @param {Object} contract - Contract data
 * @param {Object} [options] - Template options
 * @returns {Promise<Buffer>} Document buffer
 *
 * @example
 * const buffer = await generateContract({
 *   title: 'Service Agreement',
 *   parties: [
 *     { role: 'Client', name: 'ACME Corp', address: '123 Main St', representative: 'John Smith', title: 'CEO' },
 *     { role: 'Provider', name: 'TechCo LLC', address: '456 Oak Ave', representative: 'Jane Doe', title: 'Managing Director' },
 *   ],
 *   effectiveDate: 'January 1, 2025',
 *   termination: 'December 31, 2025',
 *   clauses: [
 *     { title: '1. Services', body: 'Provider agrees to...' },
 *     { title: '2. Payment', body: 'Client agrees to pay...' },
 *     { title: '3. Confidentiality', body: 'Both parties agree...' },
 *   ],
 *   governingLaw: 'New York, USA',
 * });
 */
async function generateContract(contract, options = {}) {
  const { branding = {} } = options;
  const primaryColor = branding.primaryColor || '1A237E';

  const children = [
    // Title
    new Paragraph({
      children: [new TextRun({ text: (contract.title || 'AGREEMENT').toUpperCase(), bold: true, size: 36, color: primaryColor })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 240 },
    }),

    new Paragraph({
      children: [new TextRun({ text: `Effective Date: ${contract.effectiveDate || ''}`, size: 20, italics: true })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 400 },
    }),

    // Parties
    new Paragraph({ children: [new TextRun({ text: 'PARTIES', bold: true, size: 24, color: primaryColor })], spacing: { before: 120, after: 80 } }),

    ...(contract.parties || []).flatMap(party => [
      new Paragraph({ children: [new TextRun({ text: `${party.role}: `, bold: true, size: 22 }), new TextRun({ text: party.name, size: 22 })] }),
      new Paragraph({ children: [new TextRun({ text: `Address: ${party.address || ''}`, size: 20, color: '555555' })] }),
      new Paragraph({ children: [new TextRun({ text: `Representative: ${party.representative || ''}, ${party.title || ''}`, size: 20, color: '555555' })], spacing: { after: 120 } }),
    ]),

    // Recitals
    ...(contract.recitals ? [
      new Paragraph({ children: [new TextRun({ text: 'RECITALS', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: contract.recitals, size: 20 })], spacing: { after: 200 } }),
    ] : []),

    // Terms
    new Paragraph({ children: [new TextRun({ text: 'TERMS AND CONDITIONS', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),

    // Clauses
    ...(contract.clauses || []).flatMap(clause => [
      new Paragraph({ children: [new TextRun({ text: clause.title, bold: true, size: 22 })], spacing: { before: 160, after: 80 } }),
      ...clause.body.split('\n').map(line => new Paragraph({ children: [new TextRun({ text: line, size: 20 })], spacing: { after: 80 } })),
    ]),

    // Governing law
    ...(contract.governingLaw ? [
      new Paragraph({ children: [new TextRun({ text: `Governing Law`, bold: true, size: 22 })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: `This Agreement shall be governed by the laws of ${contract.governingLaw}.`, size: 20 })], spacing: { after: 200 } }),
    ] : []),

    // Signature block
    new Paragraph({ children: [new TextRun({ text: 'SIGNATURES', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),

    buildSignatureTable(contract.parties || []),
  ];

  const doc = new Document({
    styles: getDefaultDocumentStyles(branding),
    sections: [{
      properties: { page: { size: PAGE_SIZES.LETTER, margin: PAGE_MARGINS.NORMAL } },
      children,
    }]
  });

  return await Packer.toBuffer(doc);
}

function buildSignatureTable(parties) {
  const cols = Math.min(parties.length, 3);
  const colWidth = Math.floor(100 / cols);

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE }, insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE } },
    rows: [
      new TableRow({
        children: parties.slice(0, cols).map(party => new TableCell({
          width: { size: colWidth, type: WidthType.PERCENTAGE },
          children: [
            new Paragraph({ children: [new TextRun({ text: party.role, bold: true, size: 20 })], spacing: { after: 400 } }),
            new Paragraph({ children: [new TextRun({ text: '_________________________', size: 20 })], spacing: { after: 60 } }),
            new Paragraph({ children: [new TextRun({ text: `Signature`, size: 16, color: '999999' })], spacing: { after: 200 } }),
            new Paragraph({ children: [new TextRun({ text: party.representative || '', bold: true, size: 20 })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: party.title || '', size: 18, color: '666666' })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: party.name, size: 18, color: '666666' })], spacing: { after: 200 } }),
            new Paragraph({ children: [new TextRun({ text: '_________________________', size: 20 })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: 'Date', size: 16, color: '999999' })] }),
          ],
        }))
      })
    ]
  });
}

/**
 * Generate a meeting minutes document.
 * @param {Object} meeting - Meeting data
 * @returns {Promise<Buffer>} Document buffer
 */
async function generateMeetingMinutes(meeting, options = {}) {
  const { branding = {} } = options;
  const primaryColor = branding.primaryColor || '1B5E20';

  const children = [
    new Paragraph({ children: [new TextRun({ text: 'MEETING MINUTES', bold: true, size: 40, color: primaryColor })], alignment: AlignmentType.CENTER, spacing: { after: 80 } }),
    new Paragraph({ children: [new TextRun({ text: meeting.title || '', size: 28, color: '333333' })], alignment: AlignmentType.CENTER, spacing: { after: 240 } }),

    // Meeting details table
    new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      rows: [
        ['Date', meeting.date || ''],
        ['Time', `${meeting.startTime || ''} - ${meeting.endTime || ''}`],
        ['Location', meeting.location || ''],
        ['Facilitator', meeting.facilitator || ''],
        ['Note Taker', meeting.noteTaker || ''],
      ].map(([label, value]) => new TableRow({
        children: [
          new TableCell({ width: { size: 20, type: WidthType.PERCENTAGE }, shading: { type: ShadingType.SOLID, color: 'F0F4F8' }, children: [new Paragraph({ children: [new TextRun({ text: label, bold: true, size: 20 })] })] }),
          new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: value, size: 20 })] })] }),
        ]
      })),
      spacing: { after: 240 },
    }),

    // Attendees
    new Paragraph({ children: [new TextRun({ text: 'ATTENDEES', bold: true, size: 22, color: primaryColor })], spacing: { before: 120, after: 80 } }),
    ...(meeting.attendees || []).map(a => new Paragraph({ children: [new TextRun({ text: `${a.name || a} — ${a.role || ''}`, size: 20 })], bullet: { level: 0 }, spacing: { after: 40 } })),

    // Agenda
    ...(meeting.agenda?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'AGENDA', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      ...meeting.agenda.map((item, i) => new Paragraph({ children: [new TextRun({ text: `${i + 1}. ${item}`, size: 20 })], spacing: { after: 40 } })),
    ] : []),

    // Discussion points
    ...(meeting.discussionPoints?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'DISCUSSION', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),
      ...meeting.discussionPoints.flatMap(point => [
        new Paragraph({ children: [new TextRun({ text: point.topic, bold: true, size: 22 })], spacing: { before: 120, after: 60 } }),
        new Paragraph({ children: [new TextRun({ text: point.summary || '', size: 20 })], spacing: { after: 80 } }),
        ...(point.decisions || []).map(d => new Paragraph({ children: [new TextRun({ text: `Decision: ${d}`, size: 20, bold: true, color: primaryColor })], spacing: { after: 40 } })),
      ]),
    ] : []),

    // Action items
    ...(meeting.actionItems?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'ACTION ITEMS', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),
      new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        rows: [
          new TableRow({
            tableHeader: true,
            children: ['Action', 'Owner', 'Due Date', 'Status'].map(h => new TableCell({ shading: { type: ShadingType.SOLID, color: primaryColor }, children: [new Paragraph({ children: [new TextRun({ text: h, bold: true, color: 'FFFFFF', size: 20 })] })] }))
          }),
          ...(meeting.actionItems || []).map((item, i) => new TableRow({
            children: [
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.action || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.owner || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.dueDate || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.status || 'Open', size: 20 })] })] }),
            ],
            shading: i % 2 !== 0 ? { type: ShadingType.SOLID, color: 'F9F9F9' } : undefined,
          }))
        ]
      }),
    ] : []),

    // Next meeting
    ...(meeting.nextMeeting ? [
      new Paragraph({ children: [new TextRun({ text: 'NEXT MEETING', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: `Date: ${meeting.nextMeeting.date || ''}`, size: 20 })], spacing: { after: 40 } }),
      new Paragraph({ children: [new TextRun({ text: `Location: ${meeting.nextMeeting.location || ''}`, size: 20 })], spacing: { after: 40 } }),
    ] : []),
  ];

  const doc = new Document({
    styles: getDefaultDocumentStyles(branding),
    sections: [{ properties: { page: { size: PAGE_SIZES.LETTER, margin: PAGE_MARGINS.NORMAL } }, children }]
  });

  return await Packer.toBuffer(doc);
}

Object.assign(module.exports, {
  generateContract,
  generateMeetingMinutes,
});


// ─── Additional Template Utilities ───────────────────────────────────────────

/**
 * Generate a contract or agreement document.
 * @param {Object} contract - Contract data
 * @param {Object} [options] - Template options
 * @returns {Promise<Buffer>} Document buffer
 *
 * @example
 * const buffer = await generateContract({
 *   title: 'Service Agreement',
 *   parties: [
 *     { role: 'Client', name: 'ACME Corp', address: '123 Main St', representative: 'John Smith', title: 'CEO' },
 *     { role: 'Provider', name: 'TechCo LLC', address: '456 Oak Ave', representative: 'Jane Doe', title: 'Managing Director' },
 *   ],
 *   effectiveDate: 'January 1, 2025',
 *   termination: 'December 31, 2025',
 *   clauses: [
 *     { title: '1. Services', body: 'Provider agrees to...' },
 *     { title: '2. Payment', body: 'Client agrees to pay...' },
 *     { title: '3. Confidentiality', body: 'Both parties agree...' },
 *   ],
 *   governingLaw: 'New York, USA',
 * });
 */
async function generateContract(contract, options = {}) {
  const { branding = {} } = options;
  const primaryColor = branding.primaryColor || '1A237E';

  const children = [
    // Title
    new Paragraph({
      children: [new TextRun({ text: (contract.title || 'AGREEMENT').toUpperCase(), bold: true, size: 36, color: primaryColor })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 240 },
    }),

    new Paragraph({
      children: [new TextRun({ text: `Effective Date: ${contract.effectiveDate || ''}`, size: 20, italics: true })],
      alignment: AlignmentType.CENTER,
      spacing: { after: 400 },
    }),

    // Parties
    new Paragraph({ children: [new TextRun({ text: 'PARTIES', bold: true, size: 24, color: primaryColor })], spacing: { before: 120, after: 80 } }),

    ...(contract.parties || []).flatMap(party => [
      new Paragraph({ children: [new TextRun({ text: `${party.role}: `, bold: true, size: 22 }), new TextRun({ text: party.name, size: 22 })] }),
      new Paragraph({ children: [new TextRun({ text: `Address: ${party.address || ''}`, size: 20, color: '555555' })] }),
      new Paragraph({ children: [new TextRun({ text: `Representative: ${party.representative || ''}, ${party.title || ''}`, size: 20, color: '555555' })], spacing: { after: 120 } }),
    ]),

    // Recitals
    ...(contract.recitals ? [
      new Paragraph({ children: [new TextRun({ text: 'RECITALS', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: contract.recitals, size: 20 })], spacing: { after: 200 } }),
    ] : []),

    // Terms
    new Paragraph({ children: [new TextRun({ text: 'TERMS AND CONDITIONS', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),

    // Clauses
    ...(contract.clauses || []).flatMap(clause => [
      new Paragraph({ children: [new TextRun({ text: clause.title, bold: true, size: 22 })], spacing: { before: 160, after: 80 } }),
      ...clause.body.split('\n').map(line => new Paragraph({ children: [new TextRun({ text: line, size: 20 })], spacing: { after: 80 } })),
    ]),

    // Governing law
    ...(contract.governingLaw ? [
      new Paragraph({ children: [new TextRun({ text: `Governing Law`, bold: true, size: 22 })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: `This Agreement shall be governed by the laws of ${contract.governingLaw}.`, size: 20 })], spacing: { after: 200 } }),
    ] : []),

    // Signature block
    new Paragraph({ children: [new TextRun({ text: 'SIGNATURES', bold: true, size: 24, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),

    buildSignatureTable(contract.parties || []),
  ];

  const doc = new Document({
    styles: getDefaultDocumentStyles(branding),
    sections: [{
      properties: { page: { size: PAGE_SIZES.LETTER, margin: PAGE_MARGINS.NORMAL } },
      children,
    }]
  });

  return await Packer.toBuffer(doc);
}

function buildSignatureTable(parties) {
  const cols = Math.min(parties.length, 3);
  const colWidth = Math.floor(100 / cols);

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE }, insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE } },
    rows: [
      new TableRow({
        children: parties.slice(0, cols).map(party => new TableCell({
          width: { size: colWidth, type: WidthType.PERCENTAGE },
          children: [
            new Paragraph({ children: [new TextRun({ text: party.role, bold: true, size: 20 })], spacing: { after: 400 } }),
            new Paragraph({ children: [new TextRun({ text: '_________________________', size: 20 })], spacing: { after: 60 } }),
            new Paragraph({ children: [new TextRun({ text: `Signature`, size: 16, color: '999999' })], spacing: { after: 200 } }),
            new Paragraph({ children: [new TextRun({ text: party.representative || '', bold: true, size: 20 })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: party.title || '', size: 18, color: '666666' })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: party.name, size: 18, color: '666666' })], spacing: { after: 200 } }),
            new Paragraph({ children: [new TextRun({ text: '_________________________', size: 20 })], spacing: { after: 40 } }),
            new Paragraph({ children: [new TextRun({ text: 'Date', size: 16, color: '999999' })] }),
          ],
        }))
      })
    ]
  });
}

/**
 * Generate a meeting minutes document.
 * @param {Object} meeting - Meeting data
 * @returns {Promise<Buffer>} Document buffer
 */
async function generateMeetingMinutes(meeting, options = {}) {
  const { branding = {} } = options;
  const primaryColor = branding.primaryColor || '1B5E20';

  const children = [
    new Paragraph({ children: [new TextRun({ text: 'MEETING MINUTES', bold: true, size: 40, color: primaryColor })], alignment: AlignmentType.CENTER, spacing: { after: 80 } }),
    new Paragraph({ children: [new TextRun({ text: meeting.title || '', size: 28, color: '333333' })], alignment: AlignmentType.CENTER, spacing: { after: 240 } }),

    // Meeting details table
    new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      rows: [
        ['Date', meeting.date || ''],
        ['Time', `${meeting.startTime || ''} - ${meeting.endTime || ''}`],
        ['Location', meeting.location || ''],
        ['Facilitator', meeting.facilitator || ''],
        ['Note Taker', meeting.noteTaker || ''],
      ].map(([label, value]) => new TableRow({
        children: [
          new TableCell({ width: { size: 20, type: WidthType.PERCENTAGE }, shading: { type: ShadingType.SOLID, color: 'F0F4F8' }, children: [new Paragraph({ children: [new TextRun({ text: label, bold: true, size: 20 })] })] }),
          new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: value, size: 20 })] })] }),
        ]
      })),
      spacing: { after: 240 },
    }),

    // Attendees
    new Paragraph({ children: [new TextRun({ text: 'ATTENDEES', bold: true, size: 22, color: primaryColor })], spacing: { before: 120, after: 80 } }),
    ...(meeting.attendees || []).map(a => new Paragraph({ children: [new TextRun({ text: `${a.name || a} — ${a.role || ''}`, size: 20 })], bullet: { level: 0 }, spacing: { after: 40 } })),

    // Agenda
    ...(meeting.agenda?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'AGENDA', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      ...meeting.agenda.map((item, i) => new Paragraph({ children: [new TextRun({ text: `${i + 1}. ${item}`, size: 20 })], spacing: { after: 40 } })),
    ] : []),

    // Discussion points
    ...(meeting.discussionPoints?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'DISCUSSION', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),
      ...meeting.discussionPoints.flatMap(point => [
        new Paragraph({ children: [new TextRun({ text: point.topic, bold: true, size: 22 })], spacing: { before: 120, after: 60 } }),
        new Paragraph({ children: [new TextRun({ text: point.summary || '', size: 20 })], spacing: { after: 80 } }),
        ...(point.decisions || []).map(d => new Paragraph({ children: [new TextRun({ text: `Decision: ${d}`, size: 20, bold: true, color: primaryColor })], spacing: { after: 40 } })),
      ]),
    ] : []),

    // Action items
    ...(meeting.actionItems?.length ? [
      new Paragraph({ children: [new TextRun({ text: 'ACTION ITEMS', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 }, border: { bottom: { color: primaryColor, size: 4, style: BorderStyle.SINGLE } } }),
      new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        rows: [
          new TableRow({
            tableHeader: true,
            children: ['Action', 'Owner', 'Due Date', 'Status'].map(h => new TableCell({ shading: { type: ShadingType.SOLID, color: primaryColor }, children: [new Paragraph({ children: [new TextRun({ text: h, bold: true, color: 'FFFFFF', size: 20 })] })] }))
          }),
          ...(meeting.actionItems || []).map((item, i) => new TableRow({
            children: [
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.action || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.owner || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.dueDate || '', size: 20 })] })] }),
              new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: item.status || 'Open', size: 20 })] })] }),
            ],
            shading: i % 2 !== 0 ? { type: ShadingType.SOLID, color: 'F9F9F9' } : undefined,
          }))
        ]
      }),
    ] : []),

    // Next meeting
    ...(meeting.nextMeeting ? [
      new Paragraph({ children: [new TextRun({ text: 'NEXT MEETING', bold: true, size: 22, color: primaryColor })], spacing: { before: 200, after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: `Date: ${meeting.nextMeeting.date || ''}`, size: 20 })], spacing: { after: 40 } }),
      new Paragraph({ children: [new TextRun({ text: `Location: ${meeting.nextMeeting.location || ''}`, size: 20 })], spacing: { after: 40 } }),
    ] : []),
  ];

  const doc = new Document({
    styles: getDefaultDocumentStyles(branding),
    sections: [{ properties: { page: { size: PAGE_SIZES.LETTER, margin: PAGE_MARGINS.NORMAL } }, children }]
  });

  return await Packer.toBuffer(doc);
}

Object.assign(module.exports, {
  generateContract,
  generateMeetingMinutes,
});
