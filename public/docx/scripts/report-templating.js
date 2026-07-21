'use strict';
/**
 * @file report-templating.js
 * @description Business report templating engine using the docx npm package.
 *   Supports executive summaries, sales reports, project status, and annual reports.
 * @module public/docx/scripts
 * Requires: npm install docx
 */
const {
  Document, Packer, Paragraph, Table, TableRow, TableCell,
  TextRun, AlignmentType, WidthType, BorderStyle, ShadingType,
  TableLayoutType, VerticalAlign, Header, Footer,
  convertInchesToTwip, PageNumber, HeadingLevel,
} = require('docx');
const fs = require('fs');
const path = require('path');

const REPORT_COLORS = {
  PRIMARY: '1D4ED8', SECONDARY: '1E3A8A', ACCENT: 'DBEAFE',
  TEXT_DARK: '111827', TEXT_MED: '374151', TEXT_LIGHT: '6B7280',
  BORDER: 'E5E7EB', WHITE: 'FFFFFF', TABLE_HDR: '1E3A8A',
  TABLE_ALT: 'F8FAFC', SUCCESS: '15803D', DANGER: 'DC2626',
  WARNING: 'D97706', SECTION_BG: 'F1F5F9', CHART_BG: 'E0E7FF',
};

const SAMPLE_SALES_DATA = {
  reportTitle: 'Q1 2024 Sales Performance Report',
  company: 'DreamCo Technologies LLC',
  period: 'January 1 – March 31, 2024',
  preparedBy: 'Sarah Johnson, VP of Sales',
  preparedDate: 'April 5, 2024',
  summary: 'Q1 2024 demonstrated exceptional growth across all sales channels, with total revenue exceeding targets by 23%. North America led performance while APAC showed promising early-stage growth.',
  kpis: [
    { name: 'Total Revenue', value: '\$4.2M', target: '\$3.4M', status: 'Exceeded' },
    { name: 'New Customers', value: '147', target: '120', status: 'Exceeded' },
    { name: 'Customer Retention Rate', value: '94.2%', target: '90%', status: 'Exceeded' },
    { name: 'Average Deal Size', value: '\$28,571', target: '\$25,000', status: 'Exceeded' },
    { name: 'Sales Cycle (days)', value: '42', target: '45', status: 'Exceeded' },
    { name: 'Pipeline Coverage', value: '4.2x', target: '3.5x', status: 'Exceeded' },
  ],
  regions: [
    { region: 'North America', revenue: '\$2,100,000', customers: 68, growth: '+31%', target: 'Exceeded' },
    { region: 'Europe', revenue: '\$1,260,000', customers: 45, growth: '+18%', target: 'Met' },
    { region: 'Asia Pacific', revenue: '\$630,000', customers: 28, growth: '+45%', target: 'Exceeded' },
    { region: 'Latin America', revenue: '\$210,000', customers: 6, growth: '+12%', target: 'Below' },
  ],
  topProducts: [
    { product: 'CloudSync Pro', revenue: '\$1,680,000', units: 420, growth: '+28%' },
    { product: 'DataFlow Enterprise', revenue: '\$1,050,000', units: 105, growth: '+35%' },
    { product: 'SecureVault Suite', revenue: '\$756,000', units: 252, growth: '+22%' },
    { product: 'Analytics Dashboard', revenue: '\$504,000', units: 336, growth: '+15%' },
    { product: 'Collaboration Hub', revenue: '\$210,000', units: 700, growth: '+8%' },
  ],
};

const SAMPLE_PROJECT_DATA = {
  projectName: 'DreamCo Platform v3.0 — Public Launch',
  projectManager: 'Michael Torres',
  reportDate: 'March 15, 2024',
  startDate: 'October 1, 2023',
  targetEndDate: 'May 31, 2024',
  status: 'On Track',
  completionPercent: 72,
  budget: { total: 850000, spent: 612000, forecast: 840000 },
  summary: 'Platform v3.0 is on track for its May 31 launch. Core infrastructure work is complete, frontend development is 85% done, and QA testing began this week. A minor delay in the third-party payment integration has been resolved.',
  milestones: [
    { name: 'Project Kickoff', date: 'Oct 1, 2023', status: 'Complete', owner: 'M. Torres' },
    { name: 'Architecture Design Approved', date: 'Oct 31, 2023', status: 'Complete', owner: 'A. Chen' },
    { name: 'Backend API v1 Complete', date: 'Dec 15, 2023', status: 'Complete', owner: 'Dev Team' },
    { name: 'Frontend Beta Ready', date: 'Feb 28, 2024', status: 'Complete', owner: 'Dev Team' },
    { name: 'QA Testing Start', date: 'Mar 11, 2024', status: 'In Progress', owner: 'QA Team' },
    { name: 'Security Audit', date: 'Apr 15, 2024', status: 'Upcoming', owner: 'Security' },
    { name: 'User Acceptance Testing', date: 'May 1, 2024', status: 'Upcoming', owner: 'Product' },
    { name: 'Production Launch', date: 'May 31, 2024', status: 'Upcoming', owner: 'All Teams' },
  ],
  risks: [
    { risk: 'Third-party API rate limits under load', severity: 'Medium', probability: 'Low', mitigation: 'Implemented local caching layer', owner: 'Backend Team' },
    { risk: 'Browser compatibility issues (IE11)', severity: 'Low', probability: 'Medium', mitigation: 'IE11 officially dropped from support list', owner: 'Frontend' },
    { risk: 'Regulatory compliance delay (GDPR)', severity: 'High', probability: 'Low', mitigation: 'Legal review scheduled for March 25', owner: 'Legal Team' },
  ],
};

const SAMPLE_ANNUAL_DATA = {
  company: 'DreamCo Technologies LLC',
  year: '2023',
  ceoMessage: 'The year 2023 was transformational for DreamCo. We surpassed \$15M in annual recurring revenue, expanded to three new markets, and grew our team from 45 to 112 employees. We are deeply grateful to our customers, partners, and team for their trust and dedication.',
  financials: {
    revenue: '\$15.2M', revenueGrowth: '+67%',
    grossProfit: '\$10.1M', grossMargin: '66.4%',
    operatingIncome: '\$2.1M', netIncome: '\$1.8M',
    arr: '\$18.5M', arrGrowth: '+72%',
  },
  highlights: [
    'Launched Platform v2.5 with 40+ new features',
    'Expanded to European market (UK, Germany, France)',
    'Closed \$12M Series A funding round (January 2023)',
    'Achieved SOC 2 Type II certification',
    'Grew customer base from 210 to 680 clients',
    'Awarded "Best B2B SaaS Platform" by TechCrunch',
  ],
  departments: [
    { name: 'Engineering', headcount: 48, budget: '\$5.2M', keyAchievements: 'Shipped 3 major platform versions, 99.97% uptime' },
    { name: 'Sales', headcount: 22, budget: '\$2.8M', keyAchievements: '\$15.2M revenue, 147 enterprise clients' },
    { name: 'Customer Success', headcount: 15, budget: '\$1.4M', keyAchievements: '94% retention, NPS score of 72' },
    { name: 'Marketing', headcount: 12, budget: '\$1.8M', keyAchievements: '3.2M website visits, 400% organic growth' },
    { name: 'Operations', headcount: 15, budget: '\$2.1M', keyAchievements: 'Opened London and Berlin offices' },
  ],
};

// ─────────────────────────────────────────────────────────────────────────────
// UTILITY HELPERS
// ─────────────────────────────────────────────────────────────────────────────

function t(text, opts = {}) {
  return new TextRun({ text: String(text), bold: opts.bold || false, italics: opts.italic || false, size: opts.size || 22, color: opts.color || REPORT_COLORS.TEXT_DARK, font: opts.font || 'Calibri' });
}

function blank(after = 120) { return new Paragraph({ children: [], spacing: { before: 0, after } }); }

function sectionHeader(label, color) {
  return new Paragraph({
    children: [new TextRun({ text: label.toUpperCase(), bold: true, size: 28, color: REPORT_COLORS.WHITE, font: 'Calibri' })],
    shading: { fill: color || REPORT_COLORS.TABLE_HDR, type: ShadingType.CLEAR },
    spacing: { before: 320, after: 0 },
    indent: { left: 0 },
  });
}

function hdrCell(text, width) {
  return new TableCell({
    children: [new Paragraph({ children: [t(text, { bold: true, size: 20, color: REPORT_COLORS.WHITE })], alignment: AlignmentType.CENTER })],
    shading: { fill: REPORT_COLORS.TABLE_HDR, type: ShadingType.CLEAR },
    width: { size: width, type: WidthType.PERCENTAGE },
    borders: { top: { style: BorderStyle.SINGLE, size: 1, color: REPORT_COLORS.BORDER }, bottom: { style: BorderStyle.SINGLE, size: 1, color: REPORT_COLORS.BORDER }, left: { style: BorderStyle.SINGLE, size: 1, color: REPORT_COLORS.BORDER }, right: { style: BorderStyle.SINGLE, size: 1, color: REPORT_COLORS.BORDER } },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    verticalAlign: VerticalAlign.CENTER,
  });
}

function dataCell(text, opts = {}) {
  return new TableCell({
    children: [new Paragraph({ children: [t(String(text), { bold: opts.bold, size: opts.size || 20, color: opts.color })], alignment: opts.align === 'center' ? AlignmentType.CENTER : opts.align === 'right' ? AlignmentType.RIGHT : AlignmentType.LEFT })],
    shading: opts.bg ? { fill: opts.bg, type: ShadingType.CLEAR } : undefined,
    width: opts.width ? { size: opts.width, type: WidthType.PERCENTAGE } : undefined,
    borders: { top: { style: BorderStyle.SINGLE, size: 1, color: REPORT_COLORS.BORDER }, bottom: { style: BorderStyle.SINGLE, size: 1, color: REPORT_COLORS.BORDER }, left: { style: BorderStyle.SINGLE, size: 1, color: REPORT_COLORS.BORDER }, right: { style: BorderStyle.SINGLE, size: 1, color: REPORT_COLORS.BORDER } },
    margins: { top: 60, bottom: 60, left: 120, right: 120 },
    verticalAlign: VerticalAlign.CENTER,
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// TABLE BUILDERS
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Creates a KPI summary table with four columns: KPI name, value, target, status.
 * @param {Object[]} kpis - Array of {name, value, target, status} objects
 * @returns {Table} Formatted KPI table
 */
function createKPITable(kpis) {
  const headerRow = new TableRow({ tableHeader: true, children: [hdrCell('KPI', 35), hdrCell('Actual', 20), hdrCell('Target', 20), hdrCell('Status', 25)] });
  const rows = kpis.map((kpi, idx) => {
    const bg = idx % 2 === 0 ? REPORT_COLORS.WHITE : REPORT_COLORS.TABLE_ALT;
    const statusColor = kpi.status === 'Exceeded' || kpi.status === 'Met' ? REPORT_COLORS.SUCCESS : kpi.status === 'Below' ? REPORT_COLORS.DANGER : REPORT_COLORS.WARNING;
    return new TableRow({ children: [dataCell(kpi.name, { bg, width: 35 }), dataCell(kpi.value, { bg, align: 'center', bold: true, width: 20 }), dataCell(kpi.target, { bg, align: 'center', width: 20 }), dataCell(kpi.status, { bg, align: 'center', bold: true, color: statusColor, width: 25 })] });
  });
  return new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, layout: TableLayoutType.FIXED, rows: [headerRow, ...rows] });
}

/**
 * Creates a generic styled data table from headers and rows.
 * @param {string[]} headers - Column header labels
 * @param {string[][]} rows - 2D array of row data
 * @param {Object} [options={}] - Table styling options
 * @returns {Table} Formatted data table
 */
function createDataTable(headers, rows, options = {}) {
  const colWidth = Math.floor(100 / headers.length);
  const hdrCells = headers.map(h => hdrCell(h, colWidth));
  const headerRow = new TableRow({ tableHeader: true, children: hdrCells });

  const dataRows = rows.map((row, rowIdx) => {
    const bg = rowIdx % 2 === 0 ? (options.evenBg || REPORT_COLORS.WHITE) : (options.oddBg || REPORT_COLORS.TABLE_ALT);
    return new TableRow({ children: row.map((cell, cellIdx) => dataCell(cell, { bg, width: colWidth, align: options.columnAlignments?.[cellIdx] || 'left' })) });
  });

  return new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, layout: TableLayoutType.FIXED, rows: [headerRow, ...dataRows] });
}

/**
 * Creates a placeholder block for a chart or graph, with title and description.
 * @param {string} title - Chart title
 * @param {string} description - Chart description or data summary
 * @returns {Paragraph[]} Array of paragraph elements representing the chart placeholder
 */
function createChartPlaceholder(title, description) {
  return [
    new Paragraph({
      children: [t('[CHART: ' + title + ']', { bold: true, size: 22, color: REPORT_COLORS.PRIMARY })],
      border: { top: { style: BorderStyle.SINGLE, size: 4, color: REPORT_COLORS.PRIMARY }, bottom: { style: BorderStyle.SINGLE, size: 4, color: REPORT_COLORS.PRIMARY }, left: { style: BorderStyle.SINGLE, size: 4, color: REPORT_COLORS.PRIMARY }, right: { style: BorderStyle.SINGLE, size: 4, color: REPORT_COLORS.PRIMARY } },
      shading: { fill: REPORT_COLORS.CHART_BG, type: ShadingType.CLEAR },
      alignment: AlignmentType.CENTER,
      spacing: { before: 160, after: 40 },
      indent: { left: 720, right: 720 },
    }),
    new Paragraph({
      children: [t(description, { size: 18, color: REPORT_COLORS.TEXT_LIGHT, italic: true })],
      alignment: AlignmentType.CENTER,
      spacing: { before: 0, after: 160 },
    }),
    blank(80),
  ];
}

// ─────────────────────────────────────────────────────────────────────────────
// REPORT GENERATORS
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Generates an executive summary report Document.
 * @param {Object} data - Report data with company, summary, kpis, highlights
 * @returns {Document} docx Document instance
 */
function generateExecutiveSummary(data) {
  const children = [
    new Paragraph({ children: [new TextRun({ text: data.company || 'Company Name', bold: true, size: 48, color: REPORT_COLORS.PRIMARY, font: 'Calibri' })], spacing: { before: 0, after: 80 } }),
    new Paragraph({ children: [t(data.reportTitle || 'Executive Summary', { size: 36, bold: true })], spacing: { before: 0, after: 40 } }),
    new Paragraph({ children: [t('Period: ' + (data.period || '') + '  |  Prepared: ' + (data.preparedDate || '') + '  |  By: ' + (data.preparedBy || ''), { size: 18, color: REPORT_COLORS.TEXT_LIGHT })], spacing: { before: 0, after: 280 } }),
    sectionHeader('Executive Summary'),
    blank(100),
    new Paragraph({ children: [t(data.summary || '', { size: 22 })], spacing: { before: 80, after: 160 }, alignment: AlignmentType.JUSTIFIED }),
    sectionHeader('Key Performance Indicators'),
    blank(100),
    createKPITable(data.kpis || []),
    blank(200),
    ...(data.highlights && data.highlights.length > 0 ? [
      sectionHeader('Key Highlights'),
      blank(100),
      ...data.highlights.map(h => new Paragraph({ children: [t('✓  ' + h, { size: 22, color: REPORT_COLORS.SUCCESS })], spacing: { before: 60, after: 60 }, indent: { left: 360 } })),
    ] : []),
  ];

  return new Document({
    creator: data.preparedBy || 'Report System',
    title: data.reportTitle || 'Executive Summary',
    sections: [{
      properties: { page: { margin: { top: convertInchesToTwip(1), right: convertInchesToTwip(1), bottom: convertInchesToTwip(1), left: convertInchesToTwip(1) } } },
      headers: { default: new Header({ children: [new Paragraph({ children: [t(data.company + '  |  ' + (data.reportTitle || 'Report'), { size: 16, color: REPORT_COLORS.TEXT_LIGHT })], alignment: AlignmentType.RIGHT })] }) },
      footers: { default: new Footer({ children: [new Paragraph({ children: [new TextRun({ children: ['Page ', PageNumber.CURRENT, ' of ', PageNumber.TOTAL_PAGES], size: 16, color: REPORT_COLORS.TEXT_LIGHT, font: 'Calibri' })], alignment: AlignmentType.CENTER })] }) },
      children,
    }],
  });
}

/**
 * Generates a sales performance report Document with regional and product breakdowns.
 * @param {Object} data - Sales report data
 * @returns {Document} docx Document instance
 */
function generateSalesReport(data) {
  const regionRows = (data.regions || []).map(r => [r.region, r.revenue, String(r.customers), r.growth, r.target]);
  const productRows = (data.topProducts || []).map(p => [p.product, p.revenue, String(p.units), p.growth]);

  const children = [
    new Paragraph({ children: [new TextRun({ text: data.company || '', bold: true, size: 48, color: REPORT_COLORS.PRIMARY, font: 'Calibri' })], spacing: { before: 0, after: 80 } }),
    new Paragraph({ children: [t(data.reportTitle || 'Sales Performance Report', { size: 36, bold: true })], spacing: { before: 0, after: 40 } }),
    new Paragraph({ children: [t('Period: ' + (data.period || '') + '  |  Prepared by: ' + (data.preparedBy || '') + '  |  Date: ' + (data.preparedDate || ''), { size: 18, color: REPORT_COLORS.TEXT_LIGHT })], spacing: { before: 0, after: 280 } }),
    sectionHeader('Summary'),
    blank(100),
    new Paragraph({ children: [t(data.summary || '', { size: 22 })], spacing: { before: 80, after: 200 }, alignment: AlignmentType.JUSTIFIED }),
    sectionHeader('KPI Dashboard'),
    blank(100),
    createKPITable(data.kpis || []),
    blank(200),
    ...createChartPlaceholder('Revenue Trend (Q1 2024 vs Q1 2023)', 'Monthly revenue comparison bar chart showing 67% YoY growth'),
    sectionHeader('Regional Performance'),
    blank(100),
    createDataTable(['Region', 'Revenue', 'Customers', 'Growth', 'vs Target'], regionRows, { columnAlignments: ['left', 'right', 'center', 'center', 'center'] }),
    blank(200),
    ...createChartPlaceholder('Revenue by Region – Pie Chart', 'Revenue distribution: NA 50%, EU 30%, APAC 15%, LATAM 5%'),
    sectionHeader('Top Products'),
    blank(100),
    createDataTable(['Product', 'Revenue', 'Units Sold', 'Growth'], productRows, { columnAlignments: ['left', 'right', 'center', 'center'] }),
    blank(200),
  ];

  return new Document({
    creator: data.preparedBy || 'Sales Team',
    title: data.reportTitle || 'Sales Report',
    sections: [{
      properties: { page: { margin: { top: convertInchesToTwip(1), right: convertInchesToTwip(1), bottom: convertInchesToTwip(1), left: convertInchesToTwip(1) } } },
      headers: { default: new Header({ children: [new Paragraph({ children: [t(data.company + '  |  ' + data.reportTitle, { size: 16, color: REPORT_COLORS.TEXT_LIGHT })], alignment: AlignmentType.RIGHT })] }) },
      footers: { default: new Footer({ children: [new Paragraph({ children: [new TextRun({ children: ['Page ', PageNumber.CURRENT, ' of ', PageNumber.TOTAL_PAGES], size: 16, color: REPORT_COLORS.TEXT_LIGHT, font: 'Calibri' })], alignment: AlignmentType.CENTER })] }) },
      children,
    }],
  });
}

/**
 * Generates a project status report Document with milestones, risks, and budget.
 * @param {Object} project - Project data object
 * @returns {Document} docx Document instance
 */
function generateProjectStatusReport(project) {
  const budgetSpentPct = Math.round((project.budget.spent / project.budget.total) * 100);
  const budgetForecastPct = Math.round((project.budget.forecast / project.budget.total) * 100);
  const milestoneRows = (project.milestones || []).map(m => [m.name, m.date, m.status, m.owner]);
  const riskRows = (project.risks || []).map(r => [r.risk, r.severity, r.probability, r.mitigation, r.owner]);
  const budgetRows = [
    ['Total Budget', '\$' + project.budget.total.toLocaleString(), '100%'],
    ['Spent to Date', '\$' + project.budget.spent.toLocaleString(), budgetSpentPct + '%'],
    ['Remaining', '\$' + (project.budget.total - project.budget.spent).toLocaleString(), (100 - budgetSpentPct) + '%'],
    ['Forecast at Completion', '\$' + project.budget.forecast.toLocaleString(), budgetForecastPct + '%'],
  ];

  const children = [
    new Paragraph({ children: [new TextRun({ text: project.projectName || 'Project Status Report', bold: true, size: 40, color: REPORT_COLORS.PRIMARY, font: 'Calibri' })], spacing: { before: 0, after: 80 } }),
    new Paragraph({ children: [t('Project Manager: ' + project.projectManager + '  |  Report Date: ' + project.reportDate, { size: 18, color: REPORT_COLORS.TEXT_LIGHT })], spacing: { before: 0, after: 40 } }),
    new Paragraph({ children: [t('Start: ' + project.startDate + '  |  Target End: ' + project.targetEndDate + '  |  Status: ', { size: 20 }), t(project.status || 'On Track', { bold: true, size: 20, color: project.status === 'On Track' ? REPORT_COLORS.SUCCESS : REPORT_COLORS.DANGER })], spacing: { before: 0, after: 280 } }),
    sectionHeader('Project Summary'),
    blank(100),
    new Paragraph({ children: [t(project.summary || '', { size: 22 })], spacing: { before: 80, after: 200 }, alignment: AlignmentType.JUSTIFIED }),
    new Paragraph({ children: [t('Overall Completion: ' + project.completionPercent + '%', { bold: true, size: 24, color: REPORT_COLORS.PRIMARY })], spacing: { before: 0, after: 200 }, alignment: AlignmentType.CENTER }),
    sectionHeader('Milestone Tracker'),
    blank(100),
    createDataTable(['Milestone', 'Target Date', 'Status', 'Owner'], milestoneRows, { columnAlignments: ['left', 'center', 'center', 'center'] }),
    blank(200),
    sectionHeader('Risk Register'),
    blank(100),
    createDataTable(['Risk Description', 'Severity', 'Probability', 'Mitigation Plan', 'Owner'], riskRows),
    blank(200),
    sectionHeader('Budget Summary'),
    blank(100),
    createDataTable(['Category', 'Amount', '% of Budget'], budgetRows, { columnAlignments: ['left', 'right', 'center'] }),
    blank(200),
  ];

  return new Document({
    creator: project.projectManager,
    title: project.projectName + ' – Status Report',
    sections: [{
      properties: { page: { margin: { top: convertInchesToTwip(1), right: convertInchesToTwip(1), bottom: convertInchesToTwip(1), left: convertInchesToTwip(1) } } },
      children,
    }],
  });
}

/**
 * Generates a comprehensive annual report Document.
 * @param {Object} data - Annual report data with financials, highlights, and departments
 * @returns {Document} docx Document instance
 */
function generateAnnualReport(data) {
  const deptRows = (data.departments || []).map(d => [d.name, String(d.headcount), d.budget, d.keyAchievements]);
  const finKPIs = [
    { name: 'Annual Revenue', value: data.financials?.revenue || 'N/A', target: 'Previous Year', status: 'See Growth' },
    { name: 'Revenue Growth', value: data.financials?.revenueGrowth || 'N/A', target: '>30%', status: 'Exceeded' },
    { name: 'Gross Margin', value: data.financials?.grossMargin || 'N/A', target: '>60%', status: 'Exceeded' },
    { name: 'ARR', value: data.financials?.arr || 'N/A', target: 'N/A', status: 'See Growth' },
    { name: 'ARR Growth', value: data.financials?.arrGrowth || 'N/A', target: '>50%', status: 'Exceeded' },
    { name: 'Net Income', value: data.financials?.netIncome || 'N/A', target: 'Profitable', status: 'Met' },
  ];

  const children = [
    new Paragraph({ children: [new TextRun({ text: data.company || '', bold: true, size: 56, color: REPORT_COLORS.PRIMARY, font: 'Calibri' })], alignment: AlignmentType.CENTER, spacing: { before: 0, after: 120 } }),
    new Paragraph({ children: [t('Annual Report ' + (data.year || ''), { size: 40, bold: true })], alignment: AlignmentType.CENTER, spacing: { before: 0, after: 80 } }),
    new Paragraph({ children: [t('Fiscal Year Ending December 31, ' + (data.year || ''), { size: 22, color: REPORT_COLORS.TEXT_LIGHT })], alignment: AlignmentType.CENTER, spacing: { before: 0, after: 400 } }),
    sectionHeader("Letter from the CEO"),
    blank(100),
    new Paragraph({ children: [t(data.ceoMessage || '', { size: 22 })], spacing: { before: 80, after: 160 }, alignment: AlignmentType.JUSTIFIED }),
    new Paragraph({ children: [t('Sincerely,', { size: 22 })], spacing: { before: 160, after: 40 } }),
    new Paragraph({ children: [t(data.ceoName || 'Chief Executive Officer', { bold: true, size: 22 })], spacing: { before: 40, after: 80 } }),
    new Paragraph({ children: [t(data.company || '', { size: 20, color: REPORT_COLORS.TEXT_LIGHT })], spacing: { before: 0, after: 280 } }),
    sectionHeader('Financial Highlights ' + (data.year || '')),
    blank(100),
    createKPITable(finKPIs),
    blank(200),
    ...createChartPlaceholder('Annual Revenue Growth (5-Year Trend)', 'Line chart showing compound annual growth rate from ' + ((parseInt(data.year) - 4) || 2019) + ' to ' + (data.year || '')),
    sectionHeader('Year in Review'),
    blank(100),
    ...(data.highlights || []).map((h, idx) => new Paragraph({ children: [t((idx + 1) + '.  ' + h, { size: 22 })], spacing: { before: 80, after: 80 }, indent: { left: 360 } })),
    blank(200),
    sectionHeader('Departmental Overview'),
    blank(100),
    createDataTable(['Department', 'Headcount', 'Budget', 'Key Achievements'], deptRows),
    blank(200),
    ...createChartPlaceholder('Headcount Growth by Department', 'Stacked bar chart showing team growth throughout ' + (data.year || '')),
    sectionHeader('Outlook for ' + ((parseInt(data.year) + 1) || '')),
    blank(100),
    new Paragraph({ children: [t('Looking ahead, ' + (data.company || '') + ' is positioned for continued growth and innovation. We expect to exceed ' + (data.financials?.arr || '') + ' ARR, expand to 5 new markets, and launch 2 major product lines. Our investment in talent, technology, and partnerships will drive sustainable long-term value for all stakeholders.', { size: 22 })], spacing: { before: 80, after: 200 }, alignment: AlignmentType.JUSTIFIED }),
  ];

  return new Document({
    creator: data.company,
    title: data.company + ' – Annual Report ' + data.year,
    sections: [{
      properties: { page: { margin: { top: convertInchesToTwip(1), right: convertInchesToTwip(1), bottom: convertInchesToTwip(1), left: convertInchesToTwip(1) } } },
      headers: { default: new Header({ children: [new Paragraph({ children: [t(data.company + '  |  Annual Report ' + data.year, { size: 16, color: REPORT_COLORS.TEXT_LIGHT })], alignment: AlignmentType.RIGHT })] }) },
      footers: { default: new Footer({ children: [new Paragraph({ children: [new TextRun({ children: ['Page ', PageNumber.CURRENT, ' of ', PageNumber.TOTAL_PAGES], size: 16, color: REPORT_COLORS.TEXT_LIGHT, font: 'Calibri' })], alignment: AlignmentType.CENTER })] }) },
      children,
    }],
  });
}

async function saveReport(doc, filePath) {
  const buffer = await Packer.toBuffer(doc);
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(filePath, buffer);
  return filePath;
}

module.exports = {
  generateExecutiveSummary, generateSalesReport, generateProjectStatusReport, generateAnnualReport,
  createKPITable, createDataTable, createChartPlaceholder, saveReport,
  sectionHeader, hdrCell, dataCell, t, blank,
  REPORT_COLORS, SAMPLE_SALES_DATA, SAMPLE_PROJECT_DATA, SAMPLE_ANNUAL_DATA,
};
