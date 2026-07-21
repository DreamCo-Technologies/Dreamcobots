'use strict';
/**
 * @file legal-formatting.js
 * @description Legal document formatting utilities using the docx npm package.
 * @module public/docx/scripts
 * Requires: npm install docx
 */
const { Document, Packer, Paragraph, Table, TableRow, TableCell, TextRun, AlignmentType, WidthType, BorderStyle, ShadingType, TableLayoutType, VerticalAlign, Header, Footer, convertInchesToTwip, PageNumber } = require('docx');
const fs = require('fs');
const path = require('path');

const LEGAL_HEADING_STYLE = { font: 'Times New Roman', size: 28, bold: true, spacing: { before: 320, after: 160 } };
const LEGAL_BODY_STYLE = { font: 'Times New Roman', size: 24, spacing: { before: 0, after: 200 }, lineSpacing: 480 };
const LEGAL_CAPTION_STYLE = { font: 'Times New Roman', size: 22, bold: true, alignment: AlignmentType.CENTER };
const LEGAL_CITATION_STYLE = { font: 'Times New Roman', size: 20, italic: true, indent: { left: 720 } };

const CASE_CITATION_FORMATS = {
  US_SUPREME: '{Case Name}, {volume} U.S. {page} ({year})',
  FEDERAL_APP: '{Case Name}, {volume} F.{series}d {page} ({circuit} Cir. {year})',
  STATE: '{Case Name}, {volume} {reporter} {page} ({state} {year})',
  STATUTE: '{Title} U.S.C. § {section} ({year})',
};

const SAMPLE_CASE_DATA = {
  caseTitle: 'SMITH v. JONES CORPORATION',
  caseNumber: 'No. 24-CV-1234',
  court: 'United States District Court for the Northern District of California',
  judge: 'Hon. Jane Williams',
  plaintiff: { name: 'John Smith', counsel: 'Attorney Alice Brown', firm: 'Brown & Associates LLP', address: '100 Market Street, Suite 300, San Francisco, CA 94105', phone: '(415) 555-0101', bar: 'State Bar No. 123456' },
  defendant: { name: 'Jones Corporation', counsel: 'Attorney Robert Davis', firm: 'Davis Law Group', address: '200 California Street, San Francisco, CA 94111', phone: '(415) 555-0202', bar: 'State Bar No. 789012' },
  filingDate: 'January 15, 2024',
  subject: 'Breach of Contract and Fraud',
  summary: 'Plaintiff brings this action for damages arising from Defendant\'s material breach of a software development contract and fraudulent misrepresentations regarding the scope and timeline of deliverables.',
  arguments: [
    { heading: 'The Court Has Subject Matter Jurisdiction', body: 'This Court has jurisdiction pursuant to 28 U.S.C. § 1332 because the matter in controversy exceeds \$75,000, exclusive of interest and costs, and is between citizens of different states. Plaintiff is a citizen of California, and Defendant is incorporated in Delaware with its principal place of business in New York.' },
    { heading: 'Defendant Materially Breached the Contract', body: 'To establish breach of contract, a plaintiff must prove: (1) existence of a valid contract; (2) plaintiff\'s performance or excuse for nonperformance; (3) defendant\'s breach; and (4) resulting damages. Careau & Co. v. Security Pacific Business Credit, Inc., 222 Cal.App.3d 1371, 1388 (1990). Here, all four elements are clearly established.' },
    { heading: 'Plaintiff Suffered Substantial Damages', body: 'As a direct and proximate result of Defendant\'s breach, Plaintiff suffered damages in an amount to be proven at trial, but no less than \$500,000. These damages include: lost business opportunities, costs of remediation, and consequential damages flowing naturally from the breach.' },
  ],
  citations: [
    { text: 'Careau & Co. v. Security Pacific Business Credit, Inc., 222 Cal.App.3d 1371, 1388 (1990)' },
    { text: 'Aguilera v. Pirelli Armstrong Tire Corp., 223 F.3d 1010 (9th Cir. 2000)' },
    { text: '28 U.S.C. § 1332 (2018)' },
    { text: 'Fed. R. Civ. P. 8(a)(2)' },
  ],
};

const SAMPLE_DEPOSITION_DATA = {
  case: 'SMITH v. JONES CORPORATION',
  caseNumber: 'No. 24-CV-1234',
  deponent: 'Michael Johnson',
  date: 'February 20, 2024',
  location: 'Brown & Associates LLP, 100 Market Street, San Francisco, CA',
  reporterName: 'Patricia Lee, CSR No. 9876',
  examiningAttorney: 'Alice Brown',
  qa: [
    { type: 'Q', text: 'Please state your full name for the record.' },
    { type: 'A', text: 'My name is Michael Robert Johnson.' },
    { type: 'Q', text: 'Mr. Johnson, were you employed by Jones Corporation in January 2023?' },
    { type: 'A', text: 'Yes, I was the Senior Project Manager at Jones Corporation from June 2021 through March 2024.' },
    { type: 'Q', text: 'Were you involved in the software development contract with John Smith?' },
    { type: 'A', text: 'Yes, I was the primary point of contact on that project.' },
    { type: 'Q', text: 'Did you personally review the project timeline before it was presented to Mr. Smith?' },
    { type: 'A', text: 'I did review it, yes. However, I had concerns about whether the six-month timeline was realistic given our team\'s current workload.' },
    { type: 'Q', text: 'Did you communicate those concerns to your supervisors?' },
    { type: 'A', text: 'I raised the issue in an internal meeting. I was told the timeline had to stay as presented to the client.' },
  ],
};

const SAMPLE_COMPLAINT_DATA = {
  caseTitle: 'SMITH v. JONES CORPORATION',
  caseNumber: 'No. 24-CV-1234-PENDING',
  court: 'United States District Court, Northern District of California',
  plaintiff: { name: 'JOHN SMITH, an individual', state: 'California' },
  defendant: { name: 'JONES CORPORATION, a Delaware corporation', state: 'New York' },
  juryDemand: true,
  allegations: [
    { num: 1, text: 'Plaintiff John Smith ("Plaintiff") is an individual residing in San Francisco County, California.' },
    { num: 2, text: 'Defendant Jones Corporation ("Defendant") is a Delaware corporation with its principal place of business at 200 Park Avenue, New York, NY 10166.' },
    { num: 3, text: 'This Court has subject matter jurisdiction pursuant to 28 U.S.C. § 1332(a) because the matter in controversy exceeds \$75,000, exclusive of interest and costs, and the parties are citizens of different states.' },
    { num: 4, text: 'Venue is proper in this District pursuant to 28 U.S.C. § 1391(b)(2) because a substantial part of the events giving rise to Plaintiff\'s claims occurred in this District.' },
    { num: 5, text: 'On or about January 5, 2023, Plaintiff and Defendant entered into a written Software Development Agreement (the "Agreement") whereby Defendant agreed to develop a custom software platform for Plaintiff in exchange for \$500,000.' },
    { num: 6, text: 'Pursuant to the Agreement, Defendant represented that development would be completed within six (6) months, by July 5, 2023.' },
    { num: 7, text: 'Defendant failed to deliver any working software by the contractual deadline, or at any time thereafter, despite receiving full payment of \$500,000.' },
  ],
  causes: [
    { title: 'FIRST CAUSE OF ACTION: Breach of Contract', text: 'Plaintiff re-alleges paragraphs 1 through 7 as if fully set forth herein. Defendant materially breached the Agreement by failing to deliver the software platform. As a direct and proximate result of Defendant\'s breach, Plaintiff has suffered damages in an amount to be proven at trial, but no less than \$750,000.' },
    { title: 'SECOND CAUSE OF ACTION: Fraudulent Misrepresentation', text: 'Plaintiff re-alleges paragraphs 1 through 7 as if fully set forth herein. Defendant knowingly made false representations regarding its ability to complete the project within the agreed timeline. Plaintiff justifiably relied on these representations to his detriment.' },
  ],
  relief: ['Compensatory damages in an amount to be proven at trial, but no less than \$750,000;', 'Consequential and incidental damages;', 'Punitive damages for fraudulent conduct;', 'Pre- and post-judgment interest;', 'Attorneys\' fees and costs;', 'Such other relief as the Court deems just and proper.'],
};

function t(text, opts = {}) {
  return new TextRun({ text: String(text), bold: opts.bold || false, italics: opts.italic || false, size: opts.size || 24, color: opts.color || '111827', font: opts.font || 'Times New Roman' });
}
function blank(after = 200) { return new Paragraph({ children: [], spacing: { before: 0, after } }); }

/**
 * Creates properly numbered paragraphs with legal indent style.
 * @param {Object[]} paragraphs - Array of {num, text} objects
 * @returns {Paragraph[]} Array of numbered Paragraph elements
 */
function createNumberedParagraphs(paragraphs) {
  return paragraphs.map(p => new Paragraph({
    children: [t(p.num + '.  ' + p.text, { size: 24 })],
    spacing: { before: 0, after: 200 },
    alignment: AlignmentType.JUSTIFIED,
    indent: { left: 0, hanging: 0 },
  }));
}

/**
 * Creates an exhibit label paragraph.
 * @param {string} letter - Exhibit letter (A, B, C...)
 * @param {string} description - Description of the exhibit
 * @returns {Paragraph} Exhibit label paragraph
 */
function insertExhibitLabel(letter, description) {
  return new Paragraph({
    children: [new TextRun({ text: 'EXHIBIT ' + letter + ' – ' + description.toUpperCase(), bold: true, size: 24, font: 'Times New Roman' })],
    alignment: AlignmentType.CENTER,
    border: { top: { style: BorderStyle.SINGLE, size: 6, color: '111827' }, bottom: { style: BorderStyle.SINGLE, size: 6, color: '111827' } },
    spacing: { before: 320, after: 320 },
    shading: { fill: 'F3F4F6', type: ShadingType.CLEAR },
  });
}

/**
 * Creates a formatted legal citation block.
 * @param {Object[]} citations - Array of {text} citation objects
 * @returns {Paragraph[]} Array of citation paragraphs
 */
function formatCitationBlock(citations) {
  return [
    new Paragraph({ children: [t('TABLE OF AUTHORITIES', { bold: true, size: 26 })], alignment: AlignmentType.CENTER, spacing: { before: 0, after: 200 } }),
    ...citations.map((cite, idx) => new Paragraph({
      children: [t((idx + 1) + '.  ' + cite.text, { size: 20, italic: true })],
      indent: { left: 360, hanging: 360 },
      spacing: { before: 80, after: 80 },
    })),
  ];
}

/**
 * Generates a court brief document.
 * @param {Object} caseData - Case data with parties, arguments, citations
 * @returns {Document} docx Document
 */
function generateLegalBrief(caseData) {
  const children = [
    new Paragraph({ children: [t(caseData.court.toUpperCase(), { bold: true, size: 24 })], alignment: AlignmentType.CENTER, spacing: { before: 0, after: 80 } }),
    blank(80),
    new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, rows: [new TableRow({ children: [
      new TableCell({ children: [
        new Paragraph({ children: [t(caseData.plaintiff?.name || 'PLAINTIFF', { bold: true, size: 22 })], alignment: AlignmentType.LEFT }),
        new Paragraph({ children: [t('Plaintiff,', { size: 22 })], alignment: AlignmentType.LEFT }),
        blank(80),
        new Paragraph({ children: [t('v.', { italic: true, size: 22 })], alignment: AlignmentType.LEFT }),
        blank(80),
        new Paragraph({ children: [t(caseData.defendant?.name || 'DEFENDANT', { bold: true, size: 22 })], alignment: AlignmentType.LEFT }),
        new Paragraph({ children: [t('Defendant.', { size: 22 })], alignment: AlignmentType.LEFT }),
      ], borders: { top: { style: BorderStyle.NIL }, bottom: { style: BorderStyle.NIL }, left: { style: BorderStyle.NIL }, right: { style: BorderStyle.SINGLE, size: 6, color: '111827' } }, width: { size: 50, type: WidthType.PERCENTAGE }, margins: { top: 80, bottom: 80, left: 0, right: 240 } }),
      new TableCell({ children: [
        new Paragraph({ children: [t('Case No.: ' + caseData.caseNumber, { bold: true, size: 22 })], spacing: { before: 0, after: 80 } }),
        new Paragraph({ children: [t('PLAINTIFF\'S MEMORANDUM OF LAW IN SUPPORT OF MOTION', { bold: true, size: 22 })], spacing: { before: 80, after: 80 } }),
        new Paragraph({ children: [t('Hearing Date: TBD', { size: 20 })], spacing: { before: 0, after: 40 } }),
        new Paragraph({ children: [t('Before: ' + (caseData.judge || ''), { size: 20 })], spacing: { before: 0, after: 40 } }),
      ], borders: { top: { style: BorderStyle.NIL }, bottom: { style: BorderStyle.NIL }, left: { style: BorderStyle.NIL }, right: { style: BorderStyle.NIL } }, width: { size: 50, type: WidthType.PERCENTAGE }, margins: { top: 80, bottom: 80, left: 240, right: 0 } }),
    ]})]  }),
    blank(280),
    ...formatCitationBlock(caseData.citations || []),
    blank(200),
    new Paragraph({ children: [t('INTRODUCTION', { bold: true, size: 28 })], spacing: { before: 0, after: 120 } }),
    new Paragraph({ children: [t(caseData.summary || '', { size: 24 })], spacing: { before: 0, after: 200 }, alignment: AlignmentType.JUSTIFIED }),
    blank(80),
    new Paragraph({ children: [t('ARGUMENT', { bold: true, size: 28 })], spacing: { before: 0, after: 120 } }),
    ...(caseData.arguments || []).flatMap((arg, idx) => [
      new Paragraph({ children: [t((idx + 1) + '.  ' + arg.heading.toUpperCase(), { bold: true, size: 26 })], spacing: { before: 200, after: 100 } }),
      new Paragraph({ children: [t(arg.body, { size: 24 })], spacing: { before: 0, after: 200 }, alignment: AlignmentType.JUSTIFIED }),
    ]),
    blank(200),
    new Paragraph({ children: [t('CONCLUSION', { bold: true, size: 28 })], spacing: { before: 0, after: 120 } }),
    new Paragraph({ children: [t('For the foregoing reasons, Plaintiff respectfully requests that this Court grant the relief requested herein and such other relief as the Court deems just and proper.', { size: 24 })], spacing: { before: 0, after: 200 }, alignment: AlignmentType.JUSTIFIED }),
    blank(280),
    new Paragraph({ children: [t('Respectfully submitted,', { size: 22 })], spacing: { before: 0, after: 200 } }),
    new Paragraph({ children: [t(caseData.plaintiff?.firm || '', { bold: true, size: 22 })], spacing: { before: 0, after: 40 } }),
    blank(200),
    new Paragraph({ children: [t('_'.repeat(40), { size: 22 })], spacing: { before: 0, after: 40 } }),
    new Paragraph({ children: [t(caseData.plaintiff?.counsel || '', { bold: true, size: 22 })], spacing: { before: 0, after: 40 } }),
    new Paragraph({ children: [t(caseData.plaintiff?.address || '', { size: 20 })], spacing: { before: 0, after: 40 } }),
    new Paragraph({ children: [t(caseData.plaintiff?.bar || '', { size: 20 })], spacing: { before: 0, after: 40 } }),
    new Paragraph({ children: [t('Attorney for Plaintiff ' + (caseData.plaintiff?.name || ''), { size: 20, italic: true })], spacing: { before: 0, after: 0 } }),
  ];
  return new Document({ creator: caseData.plaintiff?.counsel || 'Legal System', title: 'Legal Brief – ' + caseData.caseTitle, sections: [{ properties: { page: { margin: { top: convertInchesToTwip(1), right: convertInchesToTwip(1), bottom: convertInchesToTwip(1), left: convertInchesToTwip(1.25) } } }, headers: { default: new Header({ children: [new Paragraph({ children: [t(caseData.caseNumber + '  |  CONFIDENTIAL ATTORNEY WORK PRODUCT', { size: 16, color: '9CA3AF' })], alignment: AlignmentType.CENTER })] }) }, footers: { default: new Footer({ children: [new Paragraph({ children: [new TextRun({ children: [PageNumber.CURRENT], size: 16, color: '9CA3AF', font: 'Times New Roman' })], alignment: AlignmentType.CENTER })] }) }, children }] });
}

/**
 * Generates a deposition transcript document.
 * @param {Object} data - Deposition data with Q&A and metadata
 * @returns {Document} docx Document
 */
function generateDeposition(data) {
  const children = [
    new Paragraph({ children: [t('DEPOSITION TRANSCRIPT', { bold: true, size: 32 })], alignment: AlignmentType.CENTER, spacing: { before: 0, after: 80 } }),
    new Paragraph({ children: [t(data.case || '', { bold: true, size: 26 })], alignment: AlignmentType.CENTER, spacing: { before: 0, after: 80 } }),
    new Paragraph({ children: [t('Case No.: ' + (data.caseNumber || ''), { size: 22 })], alignment: AlignmentType.CENTER, spacing: { before: 0, after: 200 } }),
    blank(80),
    new Paragraph({ children: [t('Deponent: ', { bold: true, size: 22 }), t(data.deponent || '', { size: 22 })], spacing: { before: 0, after: 80 } }),
    new Paragraph({ children: [t('Date: ', { bold: true, size: 22 }), t(data.date || '', { size: 22 })], spacing: { before: 0, after: 80 } }),
    new Paragraph({ children: [t('Location: ', { bold: true, size: 22 }), t(data.location || '', { size: 22 })], spacing: { before: 0, after: 80 } }),
    new Paragraph({ children: [t('Court Reporter: ', { bold: true, size: 22 }), t(data.reporterName || '', { size: 22 })], spacing: { before: 0, after: 80 } }),
    new Paragraph({ children: [t('Examining Attorney: ', { bold: true, size: 22 }), t(data.examiningAttorney || '', { size: 22 })], spacing: { before: 0, after: 200 } }),
    blank(80),
    new Paragraph({ children: [t('─'.repeat(60), { size: 20 })], spacing: { before: 0, after: 200 } }),
    blank(80),
    ...(data.qa || []).map(item => new Paragraph({
      children: [t(item.type + ':  ', { bold: true, size: 22, color: item.type === 'Q' ? '1D4ED8' : '111827' }), t(item.text, { size: 22 })],
      spacing: { before: 100, after: 100 },
      indent: { left: 360, hanging: 360 },
      alignment: AlignmentType.JUSTIFIED,
    })),
  ];
  return new Document({ creator: data.reporterName || 'Court Reporter', title: 'Deposition – ' + data.deponent, sections: [{ properties: { page: { margin: { top: convertInchesToTwip(1.25), right: convertInchesToTwip(1.25), bottom: convertInchesToTwip(1.25), left: convertInchesToTwip(1.5) } } }, children }] });
}

/**
 * Generates a legal complaint document.
 * @param {Object} data - Complaint data with parties, allegations, causes of action
 * @returns {Document} docx Document
 */
function generateComplaint(data) {
  const children = [
    new Paragraph({ children: [t(data.court?.toUpperCase() || 'COURT NAME', { bold: true, size: 24 })], alignment: AlignmentType.CENTER, spacing: { before: 0, after: 80 } }),
    blank(80),
    new Paragraph({ children: [t(data.plaintiff?.name || '', { bold: true, size: 24 })], alignment: AlignmentType.LEFT, spacing: { before: 0, after: 40 } }),
    new Paragraph({ children: [t('Plaintiff,', { size: 22 })], alignment: AlignmentType.LEFT, spacing: { before: 0, after: 80 } }),
    new Paragraph({ children: [t('v.', { italic: true, size: 22 })], alignment: AlignmentType.LEFT, spacing: { before: 0, after: 80 } }),
    new Paragraph({ children: [t(data.defendant?.name || '', { bold: true, size: 24 })], alignment: AlignmentType.LEFT, spacing: { before: 0, after: 40 } }),
    new Paragraph({ children: [t('Defendant.', { size: 22 })], alignment: AlignmentType.LEFT, spacing: { before: 0, after: 80 } }),
    new Paragraph({ children: [t('Case No.: ' + (data.caseNumber || ''), { bold: true, size: 22 })], spacing: { before: 0, after: 280 } }),
    blank(80),
    new Paragraph({ children: [t('COMPLAINT' + (data.juryDemand ? ' AND DEMAND FOR JURY TRIAL' : ''), { bold: true, size: 32 })], alignment: AlignmentType.CENTER, spacing: { before: 0, after: 280 } }),
    blank(80),
    new Paragraph({ children: [t('GENERAL ALLEGATIONS', { bold: true, size: 26 })], spacing: { before: 0, after: 160 } }),
    ...createNumberedParagraphs(data.allegations || []),
    blank(80),
    ...(data.causes || []).flatMap(cause => [
      new Paragraph({ children: [t(cause.title, { bold: true, size: 26 })], spacing: { before: 200, after: 120 } }),
      new Paragraph({ children: [t(cause.text, { size: 24 })], spacing: { before: 0, after: 200 }, alignment: AlignmentType.JUSTIFIED }),
    ]),
    blank(80),
    new Paragraph({ children: [t('PRAYER FOR RELIEF', { bold: true, size: 26 })], spacing: { before: 200, after: 120 } }),
    new Paragraph({ children: [t('WHEREFORE, Plaintiff prays for judgment against Defendant as follows:', { size: 24 })], spacing: { before: 0, after: 120 } }),
    ...(data.relief || []).map((r, idx) => new Paragraph({ children: [t(String.fromCharCode(97 + idx) + '.  ' + r, { size: 22 })], indent: { left: 360 }, spacing: { before: 60, after: 60 } })),
  ];
  return new Document({ creator: 'Legal System', title: 'Complaint – ' + data.caseTitle, sections: [{ properties: { page: { margin: { top: convertInchesToTwip(1.25), right: convertInchesToTwip(1.25), bottom: convertInchesToTwip(1.25), left: convertInchesToTwip(1.5) } } }, children }] });
}

function formatLegalDocument(doc, options = {}) { return doc; }

async function saveDocument(doc, filePath) {
  const buffer = await Packer.toBuffer(doc);
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(filePath, buffer);
  return filePath;
}

module.exports = { formatLegalDocument, generateLegalBrief, generateDeposition, generateComplaint, createNumberedParagraphs, insertExhibitLabel, formatCitationBlock, saveDocument, t, blank, LEGAL_HEADING_STYLE, LEGAL_BODY_STYLE, LEGAL_CAPTION_STYLE, LEGAL_CITATION_STYLE, CASE_CITATION_FORMATS, SAMPLE_CASE_DATA, SAMPLE_DEPOSITION_DATA, SAMPLE_COMPLAINT_DATA };
