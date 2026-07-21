'use strict';
/**
 * @file contract-generator.js
 * @description Legal contract generator using the docx npm package.
 *   Supports service agreements, NDAs, employment contracts, and freelance agreements.
 * @module public/docx/scripts
 * Requires: npm install docx
 */
const {
  Document, Packer, Paragraph, Table, TableRow, TableCell,
  TextRun, AlignmentType, WidthType, BorderStyle, ShadingType,
  TableLayoutType, VerticalAlign, Header, Footer,
  convertInchesToTwip, UnderlineType, PageNumber,
} = require('docx');
const fs = require('fs');
const path = require('path');

const CONTRACT_COLORS = {
  PRIMARY: '1A1A2E', SECONDARY: '16213E', ACCENT: '0F3460',
  HIGHLIGHT: 'E94560', TEXT_DARK: '111827', TEXT_MED: '374151',
  TEXT_LIGHT: '9CA3AF', BORDER: 'D1D5DB', WHITE: 'FFFFFF',
  SECTION_BG: 'F3F4F6', TABLE_HDR: '1F2937', TABLE_ALT: 'F9FAFB',
};

const LEGAL_BOILERPLATE = {
  GOVERNING_LAW: 'This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware, without regard to its conflict of law provisions.',
  ENTIRE_AGREEMENT: 'This Agreement constitutes the entire agreement between the parties with respect to the subject matter hereof and supersedes all prior negotiations, representations, warranties, and understandings of the parties.',
  AMENDMENT: 'This Agreement may not be amended, modified, or supplemented except by a written instrument signed by both parties.',
  SEVERABILITY: 'If any provision of this Agreement is found to be unenforceable or invalid, that provision will be limited or eliminated to the minimum extent necessary so that the Agreement will otherwise remain in full force and effect and enforceable.',
  WAIVER: 'The failure of either party to exercise, in any respect, any right provided for herein shall not be deemed a waiver of any further rights hereunder.',
  NOTICES: 'All notices, requests, demands, and other communications under this Agreement shall be in writing and shall be deemed to have been duly given when delivered personally, sent by certified mail, or by overnight courier service.',
  COUNTERPARTS: 'This Agreement may be executed in one or more counterparts, each of which shall be deemed an original, and all of which together shall constitute one and the same instrument.',
  FORCE_MAJEURE: 'Neither party shall be liable to the other for any delay or failure to perform its obligations under this Agreement if such delay or failure is due to circumstances beyond the reasonable control of the affected party.',
  CONFIDENTIALITY_DEF: '"Confidential Information" means any data or information that is proprietary to the Disclosing Party and not generally known to the public, including but not limited to technical data, trade secrets, know-how, business operations, plans, software, source code, and customer information.',
  INDEMNIFICATION: 'Each party ("Indemnifying Party") shall indemnify, defend, and hold harmless the other party and its officers, directors, employees, agents, and successors from and against any and all claims, damages, losses, costs, and expenses (including reasonable attorneys fees) arising out of or relating to the Indemnifying Party\'s breach of this Agreement.',
};

const SAMPLE_CONTRACT_DATA_1 = {
  title: 'Professional Services Agreement',
  date: 'January 15, 2024',
  effectiveDate: 'February 1, 2024',
  serviceProvider: {
    name: 'DreamCo Technologies LLC',
    type: 'LLC',
    address: '1234 Innovation Drive, Suite 500, San Francisco, CA 94105',
    representative: 'Jane Smith',
    title: 'Chief Executive Officer',
  },
  client: {
    name: 'Acme Corporation',
    type: 'Corporation',
    address: '5678 Business Blvd, Floor 12, New York, NY 10001',
    representative: 'John Doe',
    title: 'Vice President of Technology',
  },
  services: [
    'Full-stack web application development',
    'System architecture design and documentation',
    'API development and third-party integrations',
    'Quality assurance and testing',
    'Deployment and DevOps configuration',
    'Post-launch technical support (30 days)',
  ],
  compensation: { amount: '\$75,000 USD', schedule: 'Net 30 invoicing', milestones: ['25% upon signing', '50% at midpoint delivery', '25% upon final acceptance'] },
  term: { start: 'February 1, 2024', end: 'July 31, 2024', renewalTerms: 'Month-to-month thereafter unless terminated' },
  intellectualProperty: 'All work product created by Service Provider under this Agreement shall be considered work-for-hire and shall be the sole property of Client upon receipt of full payment.',
  terminationNotice: '30 days',
  governingState: 'Delaware',
};

const SAMPLE_CONTRACT_DATA_2 = {
  title: 'Software Development Services Agreement',
  date: 'March 1, 2024',
  effectiveDate: 'March 15, 2024',
  serviceProvider: {
    name: 'Pixel Digital Studio Inc.',
    type: 'Corporation',
    address: '999 Creative Blvd, Austin, TX 78701',
    representative: 'Maria Garcia',
    title: 'Founder & CEO',
  },
  client: {
    name: 'Global Health Systems LLC',
    type: 'LLC',
    address: '2222 Wellness Way, Boston, MA 02101',
    representative: 'Robert Chen',
    title: 'Chief Technology Officer',
  },
  services: ['Healthcare platform mobile app development', 'HIPAA compliance implementation', 'EMR system integration', 'Patient portal development'],
  compensation: { amount: '\$120,000 USD', schedule: 'Monthly milestone invoicing' },
  term: { start: 'March 15, 2024', end: 'December 15, 2024' },
  governingState: 'Delaware',
};

const SAMPLE_NDA_DATA = {
  date: 'January 20, 2024',
  disclosingParty: {
    name: 'InnovaTech Solutions Corp.',
    address: '555 Tech Drive, Palo Alto, CA 94301',
    representative: 'Alice Zhang',
    title: 'CEO',
  },
  receivingParty: {
    name: 'Venture Capital Partners LP',
    address: '100 Sand Hill Road, Menlo Park, CA 94025',
    representative: 'Michael Johnson',
    title: 'Managing Partner',
  },
  purpose: 'Evaluating a potential strategic partnership and investment opportunity in connection with the Disclosing Party\'s Series A funding round.',
  duration: 'Three (3) years from the date of disclosure',
  returnPeriod: 'Ten (10) business days',
};

const SAMPLE_EMPLOYMENT_DATA = {
  date: 'February 1, 2024',
  employer: {
    name: 'DreamCo Technologies LLC', address: '1234 Innovation Drive, San Francisco, CA 94105',
    representative: 'HR Director', title: 'Director of Human Resources',
  },
  employee: {
    name: 'Emily Rodriguez', address: '789 Oak Street, San Francisco, CA 94110',
    position: 'Senior Software Engineer', department: 'Engineering', startDate: 'March 1, 2024',
  },
  compensation: { baseSalary: '\$185,000 per year', paySchedule: 'Bi-weekly', bonus: 'Up to 15% of base salary annually', equity: '0.1% of company equity, vesting over 4 years with 1-year cliff' },
  benefits: ['Comprehensive health, dental, and vision insurance', '401(k) with 4% employer match', 'Unlimited PTO policy', 'Annual \$2,500 professional development stipend', 'Remote work flexibility', '\$1,000 home office setup allowance'],
  probationPeriod: '90 days',
  nonCompete: '12 months post-employment within the United States',
  governingState: 'California',
};

const SAMPLE_FREELANCE_DATA = {
  date: 'April 1, 2024',
  client: { name: 'MediaCo Agency LLC', address: '333 Madison Ave, New York, NY 10017', representative: 'Sarah Kim', title: 'Creative Director' },
  contractor: { name: 'James Wilson', address: '77 Pine Street, Brooklyn, NY 11201', businessName: 'Wilson Creative Works', taxId: 'EIN: 45-6789012' },
  project: {
    name: 'Brand Identity Redesign & Website Overhaul',
    description: 'Complete brand identity system redesign including logo, typography, color palette, brand guidelines document, and full website redesign',
    deliverables: ['New brand identity package (logo files in all formats)', 'Brand guidelines document (50+ pages)', 'Website wireframes and high-fidelity mockups', 'Responsive website (up to 10 pages)', 'Style guide and component library'],
    timeline: '12 weeks from project kickoff',
    fee: '\$18,500 USD',
    paymentSchedule: '40% upfront, 30% at design approval, 30% upon final delivery',
  },
  revisions: 3,
  governingState: 'New York',
};

function t(text, opts = {}) {
  return new TextRun({
    text: String(text), bold: opts.bold || false, italics: opts.italic || false,
    size: opts.size || 22, color: opts.color || CONTRACT_COLORS.TEXT_DARK, font: opts.font || 'Times New Roman',
  });
}

function blank(after = 120) { return new Paragraph({ children: [], spacing: { before: 0, after } }); }

/**
 * Formats a numbered legal clause as an array of Paragraph elements.
 * @param {number|string} number - Clause number or identifier (e.g., 1, 1.1, "2.3")
 * @param {string} title - Clause title/heading
 * @param {string} body - Clause body text
 * @param {Object} [opts={}] - Formatting options
 * @returns {Paragraph[]} Array of paragraph elements
 */
function formatLegalClause(number, title, body, opts = {}) {
  const level = String(number).split('.').length;
  const headingSize = level === 1 ? 26 : level === 2 ? 24 : 22;
  const indentLeft = level === 1 ? 0 : level === 2 ? 360 : 720;

  return [
    new Paragraph({
      children: [t(`${number}.  ${title.toUpperCase()}`, { bold: true, size: headingSize })],
      spacing: { before: 280, after: 80 },
      indent: { left: indentLeft },
    }),
    new Paragraph({
      children: [t(body, { size: 22 })],
      spacing: { before: 0, after: 160 },
      indent: { left: indentLeft + 360 },
      alignment: AlignmentType.JUSTIFIED,
    }),
  ];
}

/**
 * Creates a signature block table for the given list of signatories.
 * @param {Object[]} names - Array of {name, title, company} objects
 * @returns {Table} Signature block table
 */
function insertSignatureBlock(names) {
  const makeSignee = (signee) => new TableCell({
    children: [
      new Paragraph({ children: [t(signee.company || '', { bold: true, size: 22 })], spacing: { before: 0, after: 80 } }),
      blank(200),
      new Paragraph({ children: [t('_'.repeat(40), { size: 22 })], spacing: { before: 0, after: 40 } }),
      new Paragraph({ children: [t('Signature', { size: 18, color: CONTRACT_COLORS.TEXT_LIGHT })], spacing: { before: 0, after: 80 } }),
      new Paragraph({ children: [t(signee.name, { bold: true, size: 22 })], spacing: { before: 0, after: 40 } }),
      new Paragraph({ children: [t(signee.title, { size: 20, color: CONTRACT_COLORS.TEXT_MED })], spacing: { before: 0, after: 80 } }),
      new Paragraph({ children: [t('Date: _____________________', { size: 20 })], spacing: { before: 40, after: 0 } }),
    ],
    width: { size: Math.floor(100 / names.length), type: WidthType.PERCENTAGE },
    borders: { top: { style: BorderStyle.NIL }, bottom: { style: BorderStyle.NIL }, left: { style: BorderStyle.NIL }, right: { style: BorderStyle.NIL } },
    margins: { top: 160, bottom: 160, left: 160, right: 160 },
  });

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    rows: [new TableRow({ children: names.map(makeSignee) })],
  });
}

function contractTitle(title) {
  return new Paragraph({
    children: [new TextRun({ text: title.toUpperCase(), bold: true, size: 36, color: CONTRACT_COLORS.PRIMARY, font: 'Times New Roman' })],
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 240 },
  });
}

function contractPreamble(party1, party2, docType, date) {
  return [
    new Paragraph({
      children: [
        t('This ' + docType + ' (the "Agreement") is entered into as of '),
        t(date, { bold: true }),
        t(' (the "Effective Date"), by and between:'),
      ],
      spacing: { before: 0, after: 200 },
      alignment: AlignmentType.JUSTIFIED,
    }),
    new Paragraph({
      children: [t(party1.name + ', a ' + party1.type + ' ("Party A" or "' + (party1.role || 'Service Provider') + '"), with its principal place of business at ' + party1.address + '; and', { size: 22 })],
      indent: { left: 360 },
      spacing: { before: 0, after: 160 },
      alignment: AlignmentType.JUSTIFIED,
    }),
    new Paragraph({
      children: [t(party2.name + ', a ' + party2.type + ' ("Party B" or "' + (party2.role || 'Client') + '"), with its principal place of business at ' + party2.address + '.', { size: 22 })],
      indent: { left: 360 },
      spacing: { before: 0, after: 200 },
      alignment: AlignmentType.JUSTIFIED,
    }),
    new Paragraph({
      children: [t('NOW, THEREFORE, in consideration of the mutual covenants and agreements set forth herein, and for other good and valuable consideration, the receipt and sufficiency of which are hereby acknowledged, the parties agree as follows:', { size: 22 })],
      spacing: { before: 0, after: 280 },
      alignment: AlignmentType.JUSTIFIED,
    }),
  ];
}

function standardClauses(governingState) {
  return [
    ...formatLegalClause(10, 'Governing Law and Jurisdiction', `${LEGAL_BOILERPLATE.GOVERNING_LAW.replace('Delaware', governingState || 'Delaware')} Any disputes shall be resolved exclusively in the state and federal courts located in ${governingState || 'Delaware'}, and each party hereby irrevocably submits to the personal jurisdiction of such courts.`),
    ...formatLegalClause(11, 'Entire Agreement', LEGAL_BOILERPLATE.ENTIRE_AGREEMENT + ' ' + LEGAL_BOILERPLATE.AMENDMENT),
    ...formatLegalClause(12, 'Severability', LEGAL_BOILERPLATE.SEVERABILITY),
    ...formatLegalClause(13, 'Waiver', LEGAL_BOILERPLATE.WAIVER),
    ...formatLegalClause(14, 'Notices', LEGAL_BOILERPLATE.NOTICES),
    ...formatLegalClause(15, 'Counterparts; Electronic Signatures', LEGAL_BOILERPLATE.COUNTERPARTS + ' Electronic signatures shall be deemed original signatures for all purposes.'),
    ...formatLegalClause(16, 'Force Majeure', LEGAL_BOILERPLATE.FORCE_MAJEURE + ' The affected party shall promptly notify the other party and use commercially reasonable efforts to resume performance.'),
  ];
}

/**
 * Generates a professional service agreement Document.
 * @param {Object} parties - {serviceProvider, client} objects with company details
 * @param {Object} terms - Contract terms including services, compensation, and period
 * @returns {Document} docx Document instance
 */
function generateServiceContract(parties, terms) {
  const sp = parties.serviceProvider || terms.serviceProvider || {};
  const cl = parties.client || terms.client || {};
  const date = terms.date || new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

  const serviceList = (terms.services || []).map(s =>
    new Paragraph({ children: [t('• ' + s, { size: 22 })], indent: { left: 720 }, spacing: { before: 40, after: 40 } })
  );

  const milestoneRows = (terms.compensation?.milestones || []).map(m =>
    new Paragraph({ children: [t('• ' + m, { size: 22 })], indent: { left: 720 }, spacing: { before: 40, after: 40 } })
  );

  const children = [
    contractTitle(terms.title || 'Professional Services Agreement'),
    ...contractPreamble({ ...sp, role: 'Service Provider', type: sp.type || 'LLC' }, { ...cl, role: 'Client', type: cl.type || 'Corporation' }, 'Professional Services Agreement', date),
    ...formatLegalClause(1, 'Services', 'Service Provider agrees to perform the following professional services for Client (the "Services"):'),
    ...serviceList,
    blank(),
    ...formatLegalClause(2, 'Compensation', `Client agrees to pay Service Provider ${terms.compensation?.amount || 'as agreed'} for the Services. Payment shall be made pursuant to the following schedule:`),
    ...milestoneRows,
    blank(),
    new Paragraph({ children: [t('Invoices are payable within ' + (terms.compensation?.schedule || 'Net 30') + '. Late payments shall accrue interest at 1.5% per month.', { size: 22 })], indent: { left: 720 }, spacing: { before: 40, after: 160 } }),
    ...formatLegalClause(3, 'Term and Termination', `This Agreement shall commence on ${terms.term?.start || date} and continue through ${terms.term?.end || 'completion of the Services'}, unless earlier terminated as provided herein. Either party may terminate this Agreement upon ${terms.terminationNotice || '30'} days written notice. In the event of termination, Client shall pay for all Services rendered through the termination date.`),
    ...formatLegalClause(4, 'Intellectual Property', terms.intellectualProperty || 'All deliverables created by Service Provider under this Agreement shall be considered work-made-for-hire and, to the extent permitted by law, shall be the sole and exclusive property of Client upon receipt of full payment. Service Provider assigns all right, title, and interest in such deliverables to Client.'),
    ...formatLegalClause(5, 'Confidentiality', LEGAL_BOILERPLATE.CONFIDENTIALITY_DEF + ' Each party agrees to maintain the confidentiality of the other party\'s Confidential Information using at least the same degree of care it uses to protect its own confidential information, but no less than reasonable care.'),
    ...formatLegalClause(6, 'Independent Contractor', 'Service Provider is an independent contractor and not an employee, agent, or partner of Client. Service Provider shall be solely responsible for all taxes, insurance, and benefits related to its personnel.'),
    ...formatLegalClause(7, 'Warranties', 'Service Provider represents and warrants that: (a) it has the right to enter into this Agreement; (b) the Services will be performed in a professional and workmanlike manner; (c) the deliverables will not infringe any third-party intellectual property rights.'),
    ...formatLegalClause(8, 'Limitation of Liability', 'IN NO EVENT SHALL EITHER PARTY BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES. EACH PARTY\'S TOTAL LIABILITY SHALL NOT EXCEED THE TOTAL FEES PAID OR PAYABLE UNDER THIS AGREEMENT IN THE TWELVE (12) MONTHS PRECEDING THE CLAIM.'),
    ...formatLegalClause(9, 'Indemnification', LEGAL_BOILERPLATE.INDEMNIFICATION),
    ...standardClauses(terms.governingState),
    blank(400),
    new Paragraph({ children: [t('IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.', { size: 22 })], alignment: AlignmentType.JUSTIFIED, spacing: { before: 0, after: 400 } }),
    insertSignatureBlock([
      { name: sp.representative || 'Authorized Signatory', title: sp.title || 'Title', company: sp.name },
      { name: cl.representative || 'Authorized Signatory', title: cl.title || 'Title', company: cl.name },
    ]),
  ];

  return new Document({
    creator: sp.name || 'Contract Generator',
    title: terms.title || 'Professional Services Agreement',
    sections: [{
      properties: { page: { margin: { top: convertInchesToTwip(1.25), right: convertInchesToTwip(1.25), bottom: convertInchesToTwip(1.25), left: convertInchesToTwip(1.25) } } },
      headers: {
        default: new Header({ children: [
          new Paragraph({ children: [new TextRun({ text: (terms.title || 'Professional Services Agreement').toUpperCase() + '  –  CONFIDENTIAL', size: 16, color: CONTRACT_COLORS.TEXT_LIGHT, font: 'Times New Roman' })], alignment: AlignmentType.CENTER }),
        ]}),
      },
      footers: {
        default: new Footer({ children: [
          new Paragraph({ children: [new TextRun({ children: [PageNumber.CURRENT], size: 16, color: CONTRACT_COLORS.TEXT_LIGHT, font: 'Times New Roman' })], alignment: AlignmentType.CENTER }),
        ]}),
      },
      children,
    }],
  });
}

/**
 * Generates a Non-Disclosure Agreement Document.
 * @param {Object} parties - {disclosingParty, receivingParty} objects
 * @param {Object} terms - NDA terms including purpose and duration
 * @returns {Document} docx Document instance
 */
function generateNDA(parties, terms) {
  const dp = parties.disclosingParty || {};
  const rp = parties.receivingParty || {};
  const date = terms.date || new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

  const children = [
    contractTitle('Mutual Non-Disclosure Agreement'),
    new Paragraph({ children: [t('Effective Date: ' + date, { bold: true, size: 22 })], alignment: AlignmentType.CENTER, spacing: { before: 0, after: 320 } }),
    ...contractPreamble(
      { ...dp, role: 'Disclosing Party', type: dp.type || 'Corporation' },
      { ...rp, role: 'Receiving Party', type: rp.type || 'Corporation' },
      'Mutual Non-Disclosure Agreement', date
    ),
    ...formatLegalClause(1, 'Definition of Confidential Information', LEGAL_BOILERPLATE.CONFIDENTIALITY_DEF + ' Confidential Information does not include information that: (a) is or becomes publicly known through no breach of this Agreement; (b) was rightfully known by the Receiving Party prior to disclosure; (c) is independently developed by the Receiving Party without use of Confidential Information; or (d) is required to be disclosed by law or court order.'),
    ...formatLegalClause(2, 'Purpose', 'The parties wish to explore ' + (terms.purpose || 'a potential business relationship') + ' (the "Purpose"). The Receiving Party agrees to use the Confidential Information solely in connection with the Purpose.'),
    ...formatLegalClause(3, 'Obligations of Receiving Party', 'The Receiving Party agrees to: (a) hold the Confidential Information in strict confidence; (b) not disclose Confidential Information to any third party without prior written consent; (c) use the Confidential Information solely for the Purpose; (d) protect Confidential Information using at least the same measures as it uses to protect its own confidential information, but no less than reasonable care; (e) limit access to Confidential Information to employees, contractors, and advisors with a need to know.'),
    ...formatLegalClause(4, 'Term', 'This Agreement shall remain in effect for ' + (terms.duration || 'two (2) years from the Effective Date') + '. The confidentiality obligations shall survive termination for a period of three (3) years.'),
    ...formatLegalClause(5, 'Return or Destruction of Information', 'Upon the Disclosing Party\'s request or termination of this Agreement, the Receiving Party shall promptly return or destroy all Confidential Information within ' + (terms.returnPeriod || 'ten (10) business days') + ' and certify in writing that it has done so.'),
    ...formatLegalClause(6, 'No License', 'Nothing in this Agreement grants the Receiving Party any right or license in or to any Confidential Information, or any intellectual property rights therein, except as expressly set forth herein.'),
    ...formatLegalClause(7, 'Remedies', 'The parties acknowledge that breach of this Agreement would cause irreparable harm for which monetary damages would be inadequate, and the non-breaching party shall be entitled to seek equitable relief, including injunction and specific performance, in addition to all other remedies available at law or in equity.'),
    ...formatLegalClause(8, 'Governing Law', LEGAL_BOILERPLATE.GOVERNING_LAW),
    ...formatLegalClause(9, 'Entire Agreement', LEGAL_BOILERPLATE.ENTIRE_AGREEMENT),
    blank(400),
    new Paragraph({ children: [t('IN WITNESS WHEREOF, the parties have executed this Non-Disclosure Agreement as of the Effective Date.', { size: 22 })], alignment: AlignmentType.JUSTIFIED, spacing: { before: 0, after: 400 } }),
    insertSignatureBlock([
      { name: dp.representative || 'Authorized Representative', title: dp.title || 'Title', company: dp.name },
      { name: rp.representative || 'Authorized Representative', title: rp.title || 'Title', company: rp.name },
    ]),
  ];

  return new Document({
    creator: dp.name || 'NDA Generator',
    title: 'Non-Disclosure Agreement',
    sections: [{ properties: { page: { margin: { top: convertInchesToTwip(1.25), right: convertInchesToTwip(1.25), bottom: convertInchesToTwip(1.25), left: convertInchesToTwip(1.25) } } }, children }],
  });
}

/**
 * Generates an employment contract Document.
 * @param {Object} employer - Employer information object
 * @param {Object} employee - Employee information object
 * @param {Object} terms - Employment terms (compensation, benefits, etc.)
 * @returns {Document} docx Document instance
 */
function generateEmploymentContract(employer, employee, terms) {
  const date = terms.date || new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

  const benefitsList = (terms.benefits || []).map(b =>
    new Paragraph({ children: [t('• ' + b, { size: 22 })], indent: { left: 720 }, spacing: { before: 40, after: 40 } })
  );

  const children = [
    contractTitle('Employment Agreement'),
    new Paragraph({ children: [t('This Employment Agreement is entered into as of ' + date + ', by and between:', { size: 22 })], spacing: { before: 0, after: 200 } }),
    new Paragraph({ children: [t(employer.name + ' ("Employer"), located at ' + employer.address + '; and', { size: 22 })], indent: { left: 360 }, spacing: { before: 0, after: 160 } }),
    new Paragraph({ children: [t(employee.name + ' ("Employee"), residing at ' + employee.address + '.', { size: 22 })], indent: { left: 360 }, spacing: { before: 0, after: 280 } }),
    ...formatLegalClause(1, 'Position and Duties', 'Employer hereby employs Employee in the position of ' + employee.position + ', in the ' + employee.department + ' department. Employee shall report to the position\'s designated manager and shall perform such duties as are reasonably assigned by Employer.'),
    ...formatLegalClause(2, 'Start Date', 'Employee\'s employment shall commence on ' + employee.startDate + '. Employment is contingent upon successful completion of background check and reference verification.'),
    ...formatLegalClause(3, 'Compensation', 'Employee shall receive a base salary of ' + terms.compensation.baseSalary + ', paid ' + terms.compensation.paySchedule + '. Employee is eligible for a performance bonus of ' + terms.compensation.bonus + ', at Employer\'s sole discretion.'),
    ...formatLegalClause(4, 'Equity', terms.compensation.equity ? 'Employee shall be granted ' + terms.compensation.equity + '. Equity grants are subject to the terms of the Company\'s equity incentive plan.' : 'No equity compensation is included in this Agreement at this time.'),
    ...formatLegalClause(5, 'Benefits', 'Employee shall be entitled to the following benefits, subject to the terms of the applicable plans:'),
    ...benefitsList,
    blank(),
    ...formatLegalClause(6, 'Probationary Period', 'Employee shall serve a probationary period of ' + (terms.probationPeriod || '90 days') + ' from the start date, during which either party may terminate this Agreement without cause and without notice.'),
    ...formatLegalClause(7, 'At-Will Employment', 'EMPLOYEE\'S EMPLOYMENT IS AT-WILL. Either party may terminate this Agreement at any time, with or without cause, and with or without notice, except as required by applicable law.'),
    ...formatLegalClause(8, 'Confidentiality and Proprietary Information', 'Employee agrees to hold all Confidential Information of Employer in strict confidence during and after employment. ' + LEGAL_BOILERPLATE.CONFIDENTIALITY_DEF + ' All work product created by Employee during employment shall be the exclusive property of Employer.'),
    ...formatLegalClause(9, 'Non-Compete and Non-Solicitation', 'For a period of ' + (terms.nonCompete || '12 months') + ' following termination, Employee shall not: (a) engage in any business that competes with Employer; (b) solicit Employer\'s clients or customers; (c) solicit or hire any of Employer\'s employees. These restrictions shall apply within the geographic area of the United States.'),
    ...formatLegalClause(10, 'Governing Law', LEGAL_BOILERPLATE.GOVERNING_LAW.replace('Delaware', terms.governingState || 'California')),
    ...formatLegalClause(11, 'Entire Agreement', LEGAL_BOILERPLATE.ENTIRE_AGREEMENT),
    blank(400),
    new Paragraph({ children: [t('IN WITNESS WHEREOF, the parties have executed this Employment Agreement as of the date first written above.', { size: 22 })], alignment: AlignmentType.JUSTIFIED, spacing: { before: 0, after: 400 } }),
    insertSignatureBlock([
      { name: employer.representative || 'HR Director', title: employer.title || 'Director of Human Resources', company: employer.name },
      { name: employee.name, title: employee.position, company: 'Employee' },
    ]),
  ];

  return new Document({
    creator: employer.name,
    title: 'Employment Agreement – ' + employee.name,
    sections: [{ properties: { page: { margin: { top: convertInchesToTwip(1.25), right: convertInchesToTwip(1.25), bottom: convertInchesToTwip(1.25), left: convertInchesToTwip(1.25) } } }, children }],
  });
}

/**
 * Generates a freelance/independent contractor agreement Document.
 * @param {Object} client - Client information
 * @param {Object} contractor - Contractor information
 * @param {Object} project - Project details including deliverables and fees
 * @returns {Document} docx Document instance
 */
function generateFreelanceContract(client, contractor, project) {
  const date = project.date || new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

  const deliverablesList = (project.deliverables || []).map(d =>
    new Paragraph({ children: [t('• ' + d, { size: 22 })], indent: { left: 720 }, spacing: { before: 40, after: 40 } })
  );

  const children = [
    contractTitle('Independent Contractor Agreement'),
    ...contractPreamble(
      { ...client, role: 'Client', type: client.type || 'LLC' },
      { ...contractor, name: contractor.businessName || contractor.name, role: 'Contractor', type: 'Individual/Business' },
      'Independent Contractor Agreement', date
    ),
    ...formatLegalClause(1, 'Project and Scope of Work', 'Contractor agrees to perform the following project for Client (the "Project"): ' + project.name + '. ' + (project.description || '')),
    ...formatLegalClause(2, 'Deliverables', 'Contractor shall provide the following deliverables:'),
    ...deliverablesList,
    blank(),
    ...formatLegalClause(3, 'Timeline', 'Contractor shall complete the Project within ' + (project.timeline || '8 weeks') + ' of the project kickoff date. Time is of the essence for this Agreement.'),
    ...formatLegalClause(4, 'Fees and Payment', 'Client shall pay Contractor a total project fee of ' + (project.fee || 'as agreed') + '. Payment shall be made as follows: ' + (project.paymentSchedule || 'As agreed upon by both parties') + '. Invoices are due within 14 days of receipt.'),
    ...formatLegalClause(5, 'Revisions', 'This Agreement includes ' + (project.revisions || 2) + ' rounds of revisions. Additional revision rounds beyond this limit shall be billed at Contractor\'s standard hourly rate.'),
    ...formatLegalClause(6, 'Independent Contractor Status', 'Contractor is an independent contractor, not an employee of Client. Contractor shall be solely responsible for all taxes, self-employment taxes, insurance, and other obligations. Client shall not withhold any taxes from payments to Contractor.'),
    ...formatLegalClause(7, 'Intellectual Property', 'Upon receipt of full payment, Contractor assigns to Client all right, title, and interest in and to the final deliverables. Contractor retains all rights in tools, frameworks, and pre-existing work used to create the deliverables.'),
    ...formatLegalClause(8, 'Confidentiality', LEGAL_BOILERPLATE.CONFIDENTIALITY_DEF + ' Contractor agrees to maintain the confidentiality of all Confidential Information disclosed by Client and to use it solely for the Purpose of completing this Project.'),
    ...formatLegalClause(9, 'Portfolio Rights', 'Contractor may display the completed deliverables in Contractor\'s portfolio and promotional materials unless Client provides written notice of objection within 30 days of project completion.'),
    ...formatLegalClause(10, 'Limitation of Liability', 'Contractor\'s total liability under this Agreement shall not exceed the total fees paid by Client. IN NO EVENT SHALL EITHER PARTY BE LIABLE FOR INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES.'),
    ...standardClauses(project.governingState || 'New York'),
    blank(400),
    new Paragraph({ children: [t('IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.', { size: 22 })], alignment: AlignmentType.JUSTIFIED, spacing: { before: 0, after: 400 } }),
    insertSignatureBlock([
      { name: client.representative || 'Authorized Signatory', title: client.title || 'Title', company: client.name },
      { name: contractor.name, title: 'Independent Contractor', company: contractor.businessName || contractor.name },
    ]),
  ];

  return new Document({
    creator: contractor.name,
    title: 'Independent Contractor Agreement – ' + project.name,
    sections: [{ properties: { page: { margin: { top: convertInchesToTwip(1.25), right: convertInchesToTwip(1.25), bottom: convertInchesToTwip(1.25), left: convertInchesToTwip(1.25) } } }, children }],
  });
}

async function saveContract(doc, filePath) {
  const buffer = await Packer.toBuffer(doc);
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(filePath, buffer);
  return filePath;
}

module.exports = {
  generateServiceContract, generateNDA, generateEmploymentContract, generateFreelanceContract,
  insertSignatureBlock, formatLegalClause, saveContract, contractTitle, contractPreamble, standardClauses, t, blank,
  CONTRACT_COLORS, LEGAL_BOILERPLATE,
  SAMPLE_CONTRACT_DATA_1, SAMPLE_CONTRACT_DATA_2, SAMPLE_NDA_DATA, SAMPLE_EMPLOYMENT_DATA, SAMPLE_FREELANCE_DATA,
};
