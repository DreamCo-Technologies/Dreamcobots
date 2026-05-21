'use strict';
/**
 * @file academic-paper-formatter.js
 * @description Academic paper formatter for APA, MLA, Chicago, and IEEE styles.
 * @module public/docx/scripts
 * Requires: npm install docx
 */
const { Document, Packer, Paragraph, TextRun, AlignmentType, convertInchesToTwip, Header, Footer, PageNumber, BorderStyle, WidthType, Table, TableRow, TableCell } = require('docx');
const fs = require('fs'); const path = require('path');

const APA_STYLE = { font: 'Times New Roman', bodySize: 24, headingSize: 24, titleSize: 24, lineSpacing: 480, margins: { top: convertInchesToTwip(1), right: convertInchesToTwip(1), bottom: convertInchesToTwip(1), left: convertInchesToTwip(1) } };
const MLA_STYLE = { font: 'Times New Roman', bodySize: 24, headingSize: 24, titleSize: 24, lineSpacing: 480, margins: { top: convertInchesToTwip(1), right: convertInchesToTwip(1), bottom: convertInchesToTwip(1), left: convertInchesToTwip(1) } };
const CHICAGO_STYLE = { font: 'Times New Roman', bodySize: 24, headingSize: 24, titleSize: 28, lineSpacing: 480, margins: { top: convertInchesToTwip(1), right: convertInchesToTwip(1), bottom: convertInchesToTwip(1), left: convertInchesToTwip(1) } };
const IEEE_STYLE = { font: 'Times New Roman', bodySize: 20, headingSize: 22, titleSize: 28, lineSpacing: 240, margins: { top: convertInchesToTwip(0.75), right: convertInchesToTwip(0.625), bottom: convertInchesToTwip(1), left: convertInchesToTwip(0.625) } };

const SAMPLE_PAPER_1 = {
  title: 'The Impact of Artificial Intelligence on Software Engineering Practices: A Systematic Review',
  authors: ['Chen, A.', 'Williams, M.', 'Patel, S.'],
  institution: 'Department of Computer Science, MIT',
  course: 'CS 6.S994: Advanced Topics in Software Engineering',
  instructor: 'Prof. Barbara Liskov',
  date: 'April 15, 2024',
  runningHead: 'AI IN SOFTWARE ENGINEERING',
  abstract: 'This systematic review examines the impact of artificial intelligence (AI) tools on software engineering practices over the period 2018–2024. Through analysis of 87 peer-reviewed studies, we identify significant improvements in code quality, developer productivity, and bug detection rates when AI-assisted tools are employed. Our findings suggest that AI pair programming tools reduce time-to-completion by an average of 35% while maintaining or improving code quality metrics. We discuss implications for software engineering education, team structures, and tool adoption strategies.',
  keywords: ['artificial intelligence', 'software engineering', 'code generation', 'developer productivity', 'systematic review'],
  sections: [
    { heading: 'Introduction', body: 'The integration of artificial intelligence into software development workflows has accelerated dramatically in recent years (Brown et al., 2020). Tools such as GitHub Copilot, Amazon CodeWhisperer, and various large language model-based assistants have entered mainstream software development environments. This systematic review aims to synthesize existing research on the impact of these tools on software engineering practices, with particular attention to productivity, code quality, and team dynamics.' },
    { heading: 'Methodology', body: 'We conducted a systematic literature review following PRISMA guidelines. Search terms included "AI code generation," "LLM software engineering," and "automated programming." We searched ACM Digital Library, IEEE Xplore, and Google Scholar, identifying 312 candidate papers. After applying inclusion/exclusion criteria, 87 papers were retained for analysis.' },
    { heading: 'Results', body: 'Our analysis reveals three primary findings. First, AI-assisted development tools increase developer productivity by 25–55% across diverse task types. Second, code produced with AI assistance shows comparable or higher automated test pass rates versus manually written code. Third, AI tools demonstrate strongest impact in boilerplate code generation and weakest impact in architectural design tasks.' },
    { heading: 'Discussion', body: 'The productivity gains observed in our review are consistent with earlier studies on computer-aided programming. However, the magnitude of gains with modern LLM-based tools significantly exceeds earlier IDE-based automation. We note important heterogeneity across studies and caution against overgeneralization to all development contexts.' },
    { heading: 'Conclusion', body: 'AI-assisted software engineering tools represent a significant productivity multiplier for modern development teams. Organizations adopting these tools should invest in training, establish quality review processes, and monitor for over-reliance. Future research should focus on long-term effects on developer skill development and system maintainability.' },
  ],
  references: [
    { authors: 'Brown, T., Mann, B., Ryder, N., et al.', year: '2020', title: 'Language Models are Few-Shot Learners', journal: 'Advances in Neural Information Processing Systems', volume: '33', pages: '1877–1901' },
    { authors: 'Chen, M., Tworek, J., Jun, H., et al.', year: '2021', title: 'Evaluating Large Language Models Trained on Code', journal: 'arXiv preprint arXiv:2107.03374' },
    { authors: 'Ziegler, A., Kalliamvakou, E., Li, X. A., et al.', year: '2022', title: 'Productivity Assessment of Neural Code Completion', journal: 'ACM SIGSOFT International Symposium on the Foundations of Software Engineering', pages: '1–11' },
  ],
};

const SAMPLE_PAPER_2 = {
  title: 'Distributed Consensus Mechanisms in Blockchain Networks: Performance Analysis',
  authors: ['Rivera, J.', 'Kim, S.'],
  institution: 'Stanford University, Department of Computer Science',
  date: 'March 1, 2024',
  abstract: 'We analyze the performance characteristics of four consensus mechanisms used in blockchain networks: Proof of Work (PoW), Proof of Stake (PoS), Delegated Proof of Stake (DPoS), and Practical Byzantine Fault Tolerance (PBFT). Through simulation and benchmarking on standardized test networks, we evaluate throughput, latency, energy consumption, and security guarantees. Our results demonstrate significant trade-offs between decentralization, security, and scalability—consistent with the blockchain trilemma hypothesis.',
  keywords: ['blockchain', 'consensus mechanisms', 'distributed systems', 'proof of stake', 'performance analysis'],
  sections: [
    { heading: 'Introduction', body: 'Blockchain technology has emerged as a foundational infrastructure for decentralized applications, digital currencies, and smart contract platforms. Central to every blockchain network is its consensus mechanism—the protocol by which distributed nodes agree on the canonical state of the ledger. The choice of consensus mechanism has profound implications for network performance, security, and energy efficiency.' },
    { heading: 'Background', body: 'The Bitcoin network introduced Proof of Work as the first practical consensus mechanism for permissionless blockchains (Nakamoto, 2008). Since then, numerous alternatives have been proposed, each addressing specific limitations of PoW while introducing new trade-offs.' },
  ],
  references: [
    { authors: 'Nakamoto, S.', year: '2008', title: 'Bitcoin: A Peer-to-Peer Electronic Cash System', journal: 'Bitcoin.org' },
    { authors: 'Buterin, V.', year: '2014', title: 'A Next-Generation Smart Contract and Decentralized Application Platform', journal: 'Ethereum Whitepaper' },
  ],
};

function t(text, opts = {}) { return new TextRun({ text: String(text), bold: opts.bold || false, italics: opts.italic || false, size: opts.size || 24, color: opts.color || '111827', font: opts.font || 'Times New Roman' }); }
function blank(after = 120) { return new Paragraph({ children: [], spacing: { before: 0, after } }); }

/**
 * Creates an abstract section.
 * @param {string} text - Abstract body text
 * @param {Object} [style=APA_STYLE] - Style configuration
 * @returns {Paragraph[]} Abstract paragraphs
 */
function createAbstract(text, style = APA_STYLE) {
  return [
    new Paragraph({ children: [t('Abstract', { bold: true, size: style.bodySize, font: style.font })], alignment: AlignmentType.CENTER, spacing: { before: 0, after: 120 } }),
    new Paragraph({ children: [t(text, { size: style.bodySize, font: style.font })], spacing: { before: 0, after: 120, line: style.lineSpacing }, alignment: AlignmentType.JUSTIFIED, indent: { firstLine: 720 } }),
  ];
}

/**
 * Creates a references section.
 * @param {Object[]} refs - Array of reference objects
 * @param {string} [format='APA'] - Citation format ('APA', 'MLA', 'Chicago', 'IEEE')
 * @returns {Paragraph[]} References paragraphs
 */
function createReferences(refs, format = 'APA') {
  const elements = [new Paragraph({ children: [t('References', { bold: true, size: 24 })], alignment: AlignmentType.CENTER, spacing: { before: 0, after: 200 } })];
  refs.forEach((ref, idx) => {
    let text = '';
    if (format === 'APA') text = (ref.authors || '') + ' (' + (ref.year || '') + '). ' + (ref.title || '') + '. ' + (ref.journal || '') + (ref.volume ? ', ' + ref.volume : '') + (ref.pages ? ', ' + ref.pages : '') + '.';
    else if (format === 'MLA') text = (ref.authors || '') + '. "' + (ref.title || '') + '." ' + (ref.journal || '') + (ref.volume ? ' ' + ref.volume : '') + ' (' + (ref.year || '') + ')' + (ref.pages ? ': ' + ref.pages : '') + '.';
    else if (format === 'IEEE') text = '[' + (idx + 1) + '] ' + (ref.authors || '') + ', "' + (ref.title || '') + '," ' + (ref.journal || '') + (ref.volume ? ', vol. ' + ref.volume : '') + (ref.pages ? ', pp. ' + ref.pages : '') + ', ' + (ref.year || '') + '.';
    else text = (ref.authors || '') + '. ' + (ref.title || '') + '. ' + (ref.journal || '') + '. ' + (ref.year || '') + '.';
    elements.push(new Paragraph({ children: [t(text, { size: 22 })], spacing: { before: 40, after: 40 }, indent: { left: 720, hanging: 720 } }));
  });
  return elements;
}

/**
 * Creates a figure caption paragraph.
 * @param {number} num - Figure number
 * @param {string} caption - Caption text
 * @returns {Paragraph} Figure caption paragraph
 */
function createFigureCaption(num, caption) {
  return new Paragraph({ children: [t('Figure ' + num + '. ', { bold: true, italic: true, size: 20 }), t(caption, { italic: true, size: 20 })], alignment: AlignmentType.CENTER, spacing: { before: 80, after: 160 } });
}

/**
 * Creates a table caption paragraph.
 * @param {number} num - Table number
 * @param {string} caption - Caption text
 * @returns {Paragraph} Table caption paragraph
 */
function createTableCaption(num, caption) {
  return new Paragraph({ children: [t('Table ' + num + '. ' + caption, { italic: true, size: 20 })], alignment: AlignmentType.LEFT, spacing: { before: 160, after: 80 } });
}

function buildPaperChildren(paper, style, format) {
  const children = [];
  if (format === 'APA') {
    children.push(blank(480));
    children.push(new Paragraph({ children: [t(paper.title, { bold: true, size: style.titleSize, font: style.font })], alignment: AlignmentType.CENTER, spacing: { before: 0, after: 120 } }));
    for (const author of (paper.authors || [])) children.push(new Paragraph({ children: [t(author, { size: style.bodySize, font: style.font })], alignment: AlignmentType.CENTER, spacing: { before: 0, after: 40 } }));
    children.push(new Paragraph({ children: [t(paper.institution || '', { size: style.bodySize, font: style.font })], alignment: AlignmentType.CENTER, spacing: { before: 40, after: 40 } }));
    children.push(new Paragraph({ children: [t(paper.date || '', { size: style.bodySize, font: style.font })], alignment: AlignmentType.CENTER, spacing: { before: 40, after: 280 } }));
    children.push(blank(480));
    if (paper.abstract) { children.push(...createAbstract(paper.abstract, style)); }
    if (paper.keywords) { children.push(new Paragraph({ children: [t('Keywords: ', { italic: true, size: style.bodySize, font: style.font }), t((paper.keywords || []).join(', '), { size: style.bodySize, font: style.font })], spacing: { before: 40, after: 200 } })); }
  } else if (format === 'MLA') {
    children.push(new Paragraph({ children: [t((paper.authors || []).join(', '), { size: style.bodySize, font: style.font })], spacing: { before: 0, after: 0 } }));
    children.push(new Paragraph({ children: [t(paper.instructor || '', { size: style.bodySize, font: style.font })], spacing: { before: 0, after: 0 } }));
    children.push(new Paragraph({ children: [t(paper.course || '', { size: style.bodySize, font: style.font })], spacing: { before: 0, after: 0 } }));
    children.push(new Paragraph({ children: [t(paper.date || '', { size: style.bodySize, font: style.font })], spacing: { before: 0, after: 0 } }));
    children.push(new Paragraph({ children: [t(paper.title, { bold: false, size: style.titleSize, font: style.font })], alignment: AlignmentType.CENTER, spacing: { before: 0, after: 0 } }));
  } else if (format === 'Chicago') {
    children.push(blank(480));
    children.push(new Paragraph({ children: [t(paper.title, { bold: true, size: style.titleSize, font: style.font })], alignment: AlignmentType.CENTER, spacing: { before: 0, after: 280 } }));
    children.push(new Paragraph({ children: [t((paper.authors || []).join(', '), { size: style.bodySize, font: style.font })], alignment: AlignmentType.CENTER, spacing: { before: 0, after: 80 } }));
    children.push(new Paragraph({ children: [t(paper.institution || '', { size: style.bodySize, font: style.font })], alignment: AlignmentType.CENTER, spacing: { before: 0, after: 80 } }));
    children.push(new Paragraph({ children: [t(paper.date || '', { size: style.bodySize, font: style.font })], alignment: AlignmentType.CENTER, spacing: { before: 0, after: 280 } }));
    if (paper.abstract) children.push(...createAbstract(paper.abstract, style));
  } else if (format === 'IEEE') {
    children.push(new Paragraph({ children: [t(paper.title, { bold: true, size: style.titleSize, font: style.font })], alignment: AlignmentType.CENTER, spacing: { before: 0, after: 120 } }));
    children.push(new Paragraph({ children: [t((paper.authors || []).join('; '), { size: style.bodySize, font: style.font })], alignment: AlignmentType.CENTER, spacing: { before: 0, after: 120 } }));
    children.push(new Paragraph({ children: [t(paper.institution || '', { size: style.bodySize, font: style.font })], alignment: AlignmentType.CENTER, spacing: { before: 0, after: 200 } }));
    if (paper.abstract) { children.push(new Paragraph({ children: [t('Abstract—', { bold: true, size: style.bodySize, font: style.font }), t(paper.abstract, { size: style.bodySize, font: style.font })], spacing: { before: 0, after: 120 }, alignment: AlignmentType.JUSTIFIED })); }
    if (paper.keywords) { children.push(new Paragraph({ children: [t('Index Terms—', { italic: true, size: style.bodySize, font: style.font }), t((paper.keywords || []).join(', '), { size: style.bodySize, font: style.font })], spacing: { before: 0, after: 200 } })); }
  }
  for (const section of (paper.sections || [])) {
    children.push(new Paragraph({ children: [t(section.heading, { bold: true, size: style.headingSize + 2, font: style.font })], spacing: { before: 280, after: 120 } }));
    children.push(new Paragraph({ children: [t(section.body, { size: style.bodySize, font: style.font })], spacing: { before: 0, after: 120, line: style.lineSpacing }, alignment: AlignmentType.JUSTIFIED, indent: { firstLine: format === 'APA' || format === 'Chicago' ? 720 : 0 } }));
  }
  if (paper.references && paper.references.length > 0) { children.push(blank(200)); children.push(...createReferences(paper.references, format)); }
  return children;
}

/**
 * Formats a paper in APA 7th edition style.
 * @param {Object} paper - Paper data object
 * @returns {Document} docx Document
 */
function formatAPAPaper(paper) {
  const children = buildPaperChildren(paper, APA_STYLE, 'APA');
  return new Document({ creator: (paper.authors || []).join(', '), title: paper.title, sections: [{ properties: { page: { margin: APA_STYLE.margins } }, headers: { default: new Header({ children: [new Paragraph({ children: [t((paper.runningHead || paper.title.toUpperCase().slice(0, 50)), { size: 20 }), new TextRun({ children: ['                                                                  ', PageNumber.CURRENT], size: 20, font: 'Times New Roman' })], alignment: AlignmentType.LEFT })] }) }, children }] });
}

/**
 * Formats a paper in MLA 9th edition style.
 * @param {Object} paper - Paper data object
 * @returns {Document} docx Document
 */
function formatMLAPaper(paper) {
  const children = buildPaperChildren(paper, MLA_STYLE, 'MLA');
  return new Document({ creator: (paper.authors || []).join(', '), title: paper.title, sections: [{ properties: { page: { margin: MLA_STYLE.margins } }, headers: { default: new Header({ children: [new Paragraph({ children: [t((paper.authors?.[0] || '').split(',')[0] + ' ', { size: 20 }), new TextRun({ children: [PageNumber.CURRENT], size: 20, font: 'Times New Roman' })], alignment: AlignmentType.RIGHT })] }) }, children }] });
}

/**
 * Formats a paper in Chicago 17th edition style.
 * @param {Object} paper - Paper data object
 * @returns {Document} docx Document
 */
function formatChicagoPaper(paper) {
  const children = buildPaperChildren(paper, CHICAGO_STYLE, 'Chicago');
  return new Document({ creator: (paper.authors || []).join(', '), title: paper.title, sections: [{ properties: { page: { margin: CHICAGO_STYLE.margins } }, children }] });
}

/**
 * Formats a paper in IEEE style.
 * @param {Object} paper - Paper data object
 * @returns {Document} docx Document
 */
function formatIEEEPaper(paper) {
  const children = buildPaperChildren(paper, IEEE_STYLE, 'IEEE');
  return new Document({ creator: (paper.authors || []).join(', '), title: paper.title, sections: [{ properties: { page: { margin: IEEE_STYLE.margins } }, children }] });
}

async function savePaper(doc, filePath) {
  const buffer = await Packer.toBuffer(doc);
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(filePath, buffer);
  return filePath;
}

module.exports = { formatAPAPaper, formatMLAPaper, formatChicagoPaper, formatIEEEPaper, createAbstract, createReferences, createFigureCaption, createTableCaption, savePaper, t, blank, APA_STYLE, MLA_STYLE, CHICAGO_STYLE, IEEE_STYLE, SAMPLE_PAPER_1, SAMPLE_PAPER_2 };
