'use strict';
/**
 * @file resume-builder.js
 * @description Professional resume and CV generator using the docx npm package.
 *   Supports multiple formats: standard, modern two-column, and academic CV.
 * @module public/docx/scripts
 *
 * Requires: npm install docx
 */

const {
  Document, Packer, Paragraph, Table, TableRow, TableCell,
  TextRun, HeadingLevel, AlignmentType, WidthType, BorderStyle,
  ShadingType, TableLayoutType, VerticalAlign, Header, Footer,
  convertInchesToTwip, UnderlineType, PageNumber,
} = require('docx');

const fs = require('fs');
const path = require('path');

// ─────────────────────────────────────────────────────────────────────────────
// CONSTANTS
// ─────────────────────────────────────────────────────────────────────────────

const RESUME_COLORS = {
  PRIMARY:   '1A56DB',
  SECONDARY: '1E429F',
  ACCENT:    'E1EFFE',
  TEXT_DARK: '111928',
  TEXT_MED:  '374151',
  TEXT_LIGHT:'6B7280',
  BORDER:    'E5E7EB',
  WHITE:     'FFFFFF',
  DIVIDER:   'D1D5DB',
  SUCCESS:   '057A55',
  MODERN_L:  '1F2937',
  MODERN_R:  'F9FAFB',
};

const RESUME_FONTS = {
  HEADING: 'Calibri',
  BODY:    'Calibri',
  MONO:    'Courier New',
  MODERN:  'Segoe UI',
};

const SECTION_LABELS = {
  EXPERIENCE:   'PROFESSIONAL EXPERIENCE',
  EDUCATION:    'EDUCATION',
  SKILLS:       'SKILLS & TECHNOLOGIES',
  PUBLICATIONS: 'PUBLICATIONS',
  AWARDS:       'AWARDS & HONORS',
  CERTIFICATIONS: 'CERTIFICATIONS',
  PROJECTS:     'PROJECTS',
  LANGUAGES:    'LANGUAGES',
  VOLUNTEER:    'VOLUNTEER EXPERIENCE',
  REFERENCES:   'REFERENCES',
  SUMMARY:      'PROFESSIONAL SUMMARY',
  RESEARCH:     'RESEARCH EXPERIENCE',
  TEACHING:     'TEACHING EXPERIENCE',
  GRANTS:       'GRANTS & FUNDING',
  CONFERENCES:  'CONFERENCE PRESENTATIONS',
};

// ─────────────────────────────────────────────────────────────────────────────
// SAMPLE DATA FIXTURES
// ─────────────────────────────────────────────────────────────────────────────

const SAMPLE_PROFILE_1 = {
  name: 'Alexandra Chen',
  title: 'Senior Full-Stack Software Engineer',
  email: 'alexandra.chen@email.com',
  phone: '+1 (415) 555-0123',
  location: 'San Francisco, CA',
  linkedin: 'linkedin.com/in/alexandrachen',
  github: 'github.com/alexandrachen',
  website: 'alexandrachen.dev',
  summary: 'Results-driven Senior Software Engineer with 8+ years of experience designing and building scalable web applications. Proven track record of leading cross-functional teams, architecting microservices, and delivering high-impact products used by millions. Passionate about clean code, developer experience, and mentoring junior engineers.',
  experience: [
    {
      title: 'Senior Software Engineer',
      company: 'TechCorp Inc.',
      location: 'San Francisco, CA',
      startDate: 'March 2020',
      endDate: 'Present',
      bullets: [
        'Architected and implemented a distributed microservices platform handling 50M+ daily API requests with 99.99% uptime',
        'Led a team of 6 engineers to redesign the core payment processing pipeline, reducing latency by 40%',
        'Introduced automated testing practices (Jest, Cypress) increasing code coverage from 45% to 92%',
        'Mentored 4 junior engineers through structured code reviews and weekly 1:1s',
        'Reduced infrastructure costs by \$200K/year by optimizing database queries and introducing Redis caching',
      ],
    },
    {
      title: 'Software Engineer II',
      company: 'StartupVentures',
      location: 'San Francisco, CA',
      startDate: 'June 2018',
      endDate: 'February 2020',
      bullets: [
        'Built a real-time collaborative document editor using WebSockets and React, serving 100K+ monthly active users',
        'Designed the data model and REST API for the company\'s core product using Node.js and PostgreSQL',
        'Implemented CI/CD pipeline with GitHub Actions, cutting deployment time from 2 hours to 8 minutes',
        'Collaborated with Product and Design to ship 12 major feature releases on schedule',
      ],
    },
    {
      title: 'Junior Software Engineer',
      company: 'WebAgency Co.',
      location: 'San Jose, CA',
      startDate: 'July 2016',
      endDate: 'May 2018',
      bullets: [
        'Developed responsive web applications for 20+ clients using React, Vue.js, and Angular',
        'Integrated third-party APIs including Stripe, Twilio, and Google Maps',
        'Improved page load times by 60% through code splitting, lazy loading, and CDN optimization',
      ],
    },
  ],
  education: [
    {
      degree: 'Bachelor of Science in Computer Science',
      institution: 'University of California, Berkeley',
      location: 'Berkeley, CA',
      graduationDate: 'May 2016',
      gpa: '3.82/4.00',
      honors: 'Magna Cum Laude, Dean\'s List (6 semesters)',
    },
  ],
  skills: {
    'Languages':    ['JavaScript (ES2022+)', 'TypeScript', 'Python', 'Go', 'SQL', 'HTML5/CSS3'],
    'Frameworks':   ['React', 'Next.js', 'Node.js', 'Express', 'FastAPI', 'GraphQL'],
    'Databases':    ['PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch', 'DynamoDB'],
    'Cloud/DevOps': ['AWS (EC2, S3, Lambda, RDS)', 'Docker', 'Kubernetes', 'Terraform', 'CI/CD'],
    'Tools':        ['Git', 'JIRA', 'Figma', 'Postman', 'DataDog', 'Sentry'],
  },
  certifications: [
    { name: 'AWS Certified Solutions Architect – Professional', issuer: 'Amazon Web Services', date: '2023', expires: '2026' },
    { name: 'Google Cloud Professional Data Engineer', issuer: 'Google Cloud', date: '2022', expires: '2024' },
  ],
  projects: [
    { name: 'OpenFlow', description: 'Open-source workflow automation tool (2.1K GitHub stars)', url: 'github.com/alexandrachen/openflow' },
    { name: 'ResumeAI', description: 'AI-powered resume analyzer and optimizer using GPT-4', url: 'resumeai.app' },
  ],
};

const SAMPLE_PROFILE_2 = {
  name: 'Dr. Marcus Williams',
  title: 'Associate Professor of Computer Science',
  email: 'mwilliams@university.edu',
  phone: '+1 (617) 555-0456',
  location: 'Cambridge, MA',
  orcid: 'orcid.org/0000-0001-2345-6789',
  website: 'cs.university.edu/~mwilliams',
  summary: 'Computer scientist specializing in distributed systems, machine learning infrastructure, and cloud computing. 12 years of research experience, 45+ peer-reviewed publications, and \$3.2M in competitive research funding. Active contributor to open-source ML frameworks.',
  experience: [
    {
      title: 'Associate Professor, Dept. of Computer Science',
      company: 'MIT — Massachusetts Institute of Technology',
      location: 'Cambridge, MA',
      startDate: 'September 2019',
      endDate: 'Present',
      bullets: [
        'Lead the Distributed Systems & AI Infrastructure Lab with 8 PhD students and 3 postdocs',
        'Teach graduate courses in Distributed Computing (6.824) and ML Systems (6.S894)',
        'Secured \$1.8M NSF CAREER Award for research on fault-tolerant ML training pipelines',
        'Co-organized the OSDI 2023 program committee',
      ],
    },
    {
      title: 'Assistant Professor, Dept. of Computer Science',
      company: 'Carnegie Mellon University',
      location: 'Pittsburgh, PA',
      startDate: 'September 2015',
      endDate: 'August 2019',
      bullets: [
        'Founded the CloudSystems research group; graduated 3 PhD students',
        'Published 22 peer-reviewed papers at top venues (SOSP, OSDI, EuroSys, NSDI)',
        'Received Outstanding Teaching Award, School of Computer Science, 2017',
      ],
    },
  ],
  education: [
    {
      degree: 'Doctor of Philosophy in Computer Science',
      institution: 'Stanford University',
      location: 'Stanford, CA',
      graduationDate: 'June 2015',
      advisor: 'Prof. Jennifer Widom',
      thesis: 'Consistent and Available Distributed Storage Systems at Scale',
    },
    {
      degree: 'Bachelor of Science in Computer Science & Mathematics',
      institution: 'Harvard University',
      location: 'Cambridge, MA',
      graduationDate: 'May 2010',
      gpa: '4.00/4.00',
      honors: 'Summa Cum Laude, Phi Beta Kappa',
    },
  ],
  publications: [
    { authors: 'Williams, M., Zhang, L., Patel, R.', title: 'Raft-ML: Consensus-Based Gradient Aggregation for Distributed Training', venue: 'SOSP 2023', year: '2023' },
    { authors: 'Williams, M., Kim, S.', title: 'Elastic Consistency: Trading Accuracy for Availability in ML Inference', venue: 'OSDI 2022', year: '2022' },
    { authors: 'Williams, M., Garcia, E., Brown, T.', title: 'ByteStore: A Multi-Tenant Key-Value Store for Heterogeneous Workloads', venue: 'EuroSys 2021', year: '2021' },
    { authors: 'Williams, M.', title: 'Temporal Causal Consistency in Geo-Distributed Databases', venue: 'NSDI 2020', year: '2020' },
  ],
  skills: {
    'Research Areas': ['Distributed Systems', 'ML Infrastructure', 'Cloud Computing', 'Storage Systems'],
    'Programming':    ['C++', 'Python', 'Go', 'Rust', 'Java'],
    'Frameworks':     ['PyTorch', 'TensorFlow', 'Kubernetes', 'gRPC', 'Apache Kafka'],
  },
};

const SAMPLE_PROFILE_3 = {
  name: 'Jordan Rivera',
  title: 'Product Designer & UX Lead',
  email: 'jordan.rivera@design.co',
  phone: '+1 (323) 555-0789',
  location: 'Los Angeles, CA',
  linkedin: 'linkedin.com/in/jordanrivera',
  portfolio: 'jordanrivera.design',
  dribbble: 'dribbble.com/jordanrivera',
  summary: 'Creative and user-centered Product Designer with 6 years of experience crafting intuitive digital experiences for consumer and enterprise products. Expert in Design Systems, user research, and cross-functional collaboration. Previously led design at two YC-backed startups.',
  experience: [
    {
      title: 'Lead Product Designer',
      company: 'Notion Labs',
      location: 'San Francisco, CA (Remote)',
      startDate: 'January 2022',
      endDate: 'Present',
      bullets: [
        'Own the design of Notion\'s core editor experience, used by 30M+ users',
        'Built and maintain the Notion Design System (400+ components) used by 25 designers',
        'Conducted 60+ user research sessions informing 3 major product launches',
        'Partnered with Engineering to establish a component-driven development workflow',
      ],
    },
    {
      title: 'Senior Product Designer',
      company: 'Figma',
      location: 'San Francisco, CA',
      startDate: 'May 2019',
      endDate: 'December 2021',
      bullets: [
        'Designed the FigJam collaborative whiteboard experience from 0 to GA',
        'Created interactive prototypes and shipped designs for 8 major features',
        'Established accessibility standards adopted across all product teams',
      ],
    },
  ],
  education: [
    {
      degree: 'Bachelor of Fine Arts in Interaction Design',
      institution: 'California College of the Arts',
      location: 'San Francisco, CA',
      graduationDate: 'May 2018',
      gpa: '3.91/4.00',
    },
  ],
  skills: {
    'Design Tools':   ['Figma', 'Sketch', 'Adobe Creative Suite', 'Principle', 'ProtoPie'],
    'Research':       ['User Interviews', 'Usability Testing', 'A/B Testing', 'Surveys', 'Card Sorting'],
    'Development':    ['HTML/CSS', 'React basics', 'Storybook', 'Zeroheight'],
    'Soft Skills':    ['Design Leadership', 'Stakeholder Presentations', 'Design Critique', 'Mentoring'],
  },
};

// ─────────────────────────────────────────────────────────────────────────────
// UTILITY HELPERS
// ─────────────────────────────────────────────────────────────────────────────

function t(text, opts = {}) {
  return new TextRun({
    text: String(text),
    bold: opts.bold || false,
    italics: opts.italic || false,
    size: opts.size || 22,
    color: opts.color || RESUME_COLORS.TEXT_DARK,
    font: opts.font || RESUME_FONTS.BODY,
    underline: opts.underline ? { type: UnderlineType.SINGLE } : undefined,
  });
}

function blank(spacing = 120) {
  return new Paragraph({ children: [], spacing: { before: 0, after: spacing } });
}

function sectionHeading(label) {
  return new Paragraph({
    children: [
      new TextRun({ text: label, bold: true, size: 24, color: RESUME_COLORS.PRIMARY, font: RESUME_FONTS.HEADING }),
    ],
    spacing: { before: 320, after: 80 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: RESUME_COLORS.PRIMARY } },
  });
}

function bullet(text, opts = {}) {
  return new Paragraph({
    children: [t(text, { size: opts.size || 20, color: opts.color || RESUME_COLORS.TEXT_MED })],
    bullet: { level: opts.level || 0 },
    spacing: { before: 40, after: 40 },
    indent: { left: 360, hanging: 180 },
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// SECTION BUILDERS
// ─────────────────────────────────────────────────────────────────────────────

function createContactHeader(profile) {
  const rows = [];
  rows.push(new Paragraph({
    children: [new TextRun({ text: profile.name, bold: true, size: 64, color: RESUME_COLORS.TEXT_DARK, font: RESUME_FONTS.HEADING })],
    spacing: { before: 0, after: 80 },
  }));
  if (profile.title) {
    rows.push(new Paragraph({
      children: [t(profile.title, { size: 28, color: RESUME_COLORS.PRIMARY })],
      spacing: { before: 0, after: 120 },
    }));
  }
  const contactParts = [];
  if (profile.email)    contactParts.push(profile.email);
  if (profile.phone)    contactParts.push(profile.phone);
  if (profile.location) contactParts.push(profile.location);
  if (profile.linkedin) contactParts.push(profile.linkedin);
  if (profile.github)   contactParts.push(profile.github);
  if (profile.website)  contactParts.push(profile.website);
  if (profile.orcid)    contactParts.push('ORCID: ' + profile.orcid);
  if (profile.portfolio)contactParts.push(profile.portfolio);

  if (contactParts.length > 0) {
    rows.push(new Paragraph({
      children: [t(contactParts.join('  •  '), { size: 18, color: RESUME_COLORS.TEXT_LIGHT })],
      spacing: { before: 0, after: 40 },
    }));
  }
  return rows;
}

function createSummarySection(summary) {
  if (!summary) return [];
  return [
    sectionHeading(SECTION_LABELS.SUMMARY),
    new Paragraph({
      children: [t(summary, { size: 20, color: RESUME_COLORS.TEXT_MED })],
      spacing: { before: 80, after: 80 },
    }),
  ];
}

function createExperienceSection(jobs) {
  if (!jobs || jobs.length === 0) return [];
  const elements = [sectionHeading(SECTION_LABELS.EXPERIENCE)];

  for (const job of jobs) {
    elements.push(new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      rows: [new TableRow({
        children: [
          new TableCell({
            children: [
              new Paragraph({ children: [t(job.title, { bold: true, size: 24 })] }),
              new Paragraph({ children: [t(job.company, { size: 22, color: RESUME_COLORS.PRIMARY })] }),
            ],
            borders: { top: { style: BorderStyle.NIL }, bottom: { style: BorderStyle.NIL }, left: { style: BorderStyle.NIL }, right: { style: BorderStyle.NIL } },
            width: { size: 70, type: WidthType.PERCENTAGE },
          }),
          new TableCell({
            children: [
              new Paragraph({ children: [t(job.location || '', { size: 20, color: RESUME_COLORS.TEXT_LIGHT })], alignment: AlignmentType.RIGHT }),
              new Paragraph({ children: [t(`${job.startDate} – ${job.endDate}`, { size: 20, color: RESUME_COLORS.TEXT_LIGHT })], alignment: AlignmentType.RIGHT }),
            ],
            borders: { top: { style: BorderStyle.NIL }, bottom: { style: BorderStyle.NIL }, left: { style: BorderStyle.NIL }, right: { style: BorderStyle.NIL } },
            width: { size: 30, type: WidthType.PERCENTAGE },
          }),
        ],
      })],
    }));

    for (const b of (job.bullets || [])) {
      elements.push(bullet(b));
    }
    elements.push(blank(80));
  }
  return elements;
}

function createEducationSection(edu) {
  if (!edu || edu.length === 0) return [];
  const elements = [sectionHeading(SECTION_LABELS.EDUCATION)];

  for (const e of edu) {
    elements.push(new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      rows: [new TableRow({
        children: [
          new TableCell({
            children: [
              new Paragraph({ children: [t(e.degree, { bold: true, size: 22 })] }),
              new Paragraph({ children: [t(e.institution, { size: 20, color: RESUME_COLORS.PRIMARY })] }),
              ...(e.gpa ? [new Paragraph({ children: [t('GPA: ' + e.gpa, { size: 19, color: RESUME_COLORS.TEXT_LIGHT })] })] : []),
              ...(e.honors ? [new Paragraph({ children: [t(e.honors, { size: 19, italic: true, color: RESUME_COLORS.TEXT_LIGHT })] })] : []),
              ...(e.advisor ? [new Paragraph({ children: [t('Advisor: ' + e.advisor, { size: 19, color: RESUME_COLORS.TEXT_LIGHT })] })] : []),
              ...(e.thesis ? [new Paragraph({ children: [t('Thesis: ' + e.thesis, { size: 19, italic: true, color: RESUME_COLORS.TEXT_LIGHT })] })] : []),
            ],
            borders: { top: { style: BorderStyle.NIL }, bottom: { style: BorderStyle.NIL }, left: { style: BorderStyle.NIL }, right: { style: BorderStyle.NIL } },
            width: { size: 70, type: WidthType.PERCENTAGE },
          }),
          new TableCell({
            children: [
              new Paragraph({ children: [t(e.location || '', { size: 20, color: RESUME_COLORS.TEXT_LIGHT })], alignment: AlignmentType.RIGHT }),
              new Paragraph({ children: [t(e.graduationDate || '', { size: 20, color: RESUME_COLORS.TEXT_LIGHT })], alignment: AlignmentType.RIGHT }),
            ],
            borders: { top: { style: BorderStyle.NIL }, bottom: { style: BorderStyle.NIL }, left: { style: BorderStyle.NIL }, right: { style: BorderStyle.NIL } },
            width: { size: 30, type: WidthType.PERCENTAGE },
          }),
        ],
      })],
    }));
    elements.push(blank(80));
  }
  return elements;
}

function createSkillsSection(skills) {
  if (!skills) return [];
  const elements = [sectionHeading(SECTION_LABELS.SKILLS)];

  for (const [category, items] of Object.entries(skills)) {
    elements.push(new Paragraph({
      children: [
        t(category + ': ', { bold: true, size: 20 }),
        t(Array.isArray(items) ? items.join(', ') : items, { size: 20, color: RESUME_COLORS.TEXT_MED }),
      ],
      spacing: { before: 60, after: 60 },
    }));
  }
  return elements;
}

function createPublicationsSection(publications) {
  if (!publications || publications.length === 0) return [];
  const elements = [sectionHeading(SECTION_LABELS.PUBLICATIONS)];

  publications.forEach((pub, idx) => {
    elements.push(new Paragraph({
      children: [
        t(`[${idx + 1}] `, { bold: true, size: 20, color: RESUME_COLORS.PRIMARY }),
        t(pub.authors + '. ', { size: 20 }),
        t('"' + pub.title + '." ', { size: 20, italic: true }),
        t(`${pub.venue}, ${pub.year}.`, { bold: true, size: 20, color: RESUME_COLORS.TEXT_LIGHT }),
      ],
      spacing: { before: 60, after: 60 },
    }));
  });
  return elements;
}

function createCertificationsSection(certifications) {
  if (!certifications || certifications.length === 0) return [];
  const elements = [sectionHeading(SECTION_LABELS.CERTIFICATIONS)];

  for (const cert of certifications) {
    elements.push(new Paragraph({
      children: [
        t(cert.name, { bold: true, size: 20 }),
        t(`  |  ${cert.issuer}  |  Issued: ${cert.date}${cert.expires ? '  |  Expires: ' + cert.expires : ''}`, { size: 19, color: RESUME_COLORS.TEXT_LIGHT }),
      ],
      spacing: { before: 60, after: 60 },
      bullet: { level: 0 },
      indent: { left: 360, hanging: 180 },
    }));
  }
  return elements;
}

function createProjectsSection(projects) {
  if (!projects || projects.length === 0) return [];
  const elements = [sectionHeading(SECTION_LABELS.PROJECTS)];

  for (const proj of projects) {
    elements.push(new Paragraph({
      children: [
        t(proj.name, { bold: true, size: 20, color: RESUME_COLORS.PRIMARY }),
        t('  –  ' + proj.description, { size: 20 }),
        ...(proj.url ? [t('  (' + proj.url + ')', { size: 18, color: RESUME_COLORS.TEXT_LIGHT })] : []),
      ],
      spacing: { before: 60, after: 60 },
      bullet: { level: 0 },
      indent: { left: 360, hanging: 180 },
    }));
  }
  return elements;
}

// ─────────────────────────────────────────────────────────────────────────────
// RESUME BUILDERS
// ─────────────────────────────────────────────────────────────────────────────

function buildResume(profile) {
  const children = [
    ...createContactHeader(profile),
    ...createSummarySection(profile.summary),
    ...createExperienceSection(profile.experience),
    ...createEducationSection(profile.education),
    ...createSkillsSection(profile.skills),
    ...createCertificationsSection(profile.certifications),
    ...createProjectsSection(profile.projects),
  ];

  return new Document({
    creator: profile.name,
    title: profile.name + ' – Resume',
    description: 'Professional resume',
    sections: [{
      properties: {
        page: {
          margin: {
            top: convertInchesToTwip(0.75),
            right: convertInchesToTwip(0.75),
            bottom: convertInchesToTwip(0.75),
            left: convertInchesToTwip(0.75),
          },
        },
      },
      children,
    }],
  });
}

function buildModernResume(profile) {
  const leftChildren = [];
  const rightChildren = [];

  // Left column: contact, skills, certifications
  leftChildren.push(new Paragraph({
    children: [new TextRun({ text: profile.name, bold: true, size: 48, color: RESUME_COLORS.WHITE, font: RESUME_FONTS.HEADING })],
    spacing: { before: 0, after: 120 },
  }));
  if (profile.title) {
    leftChildren.push(new Paragraph({
      children: [t(profile.title, { size: 22, color: RESUME_COLORS.ACCENT })],
      spacing: { before: 0, after: 200 },
    }));
  }

  const addLeftSection = (label, items) => {
    leftChildren.push(new Paragraph({
      children: [new TextRun({ text: label, bold: true, size: 20, color: RESUME_COLORS.WHITE, font: RESUME_FONTS.HEADING })],
      spacing: { before: 200, after: 100 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: RESUME_COLORS.ACCENT } },
    }));
    for (const item of items) {
      leftChildren.push(new Paragraph({
        children: [t(item, { size: 18, color: RESUME_COLORS.ACCENT })],
        spacing: { before: 40, after: 40 },
      }));
    }
  };

  // Contact info in left
  const contactItems = [];
  if (profile.email)    contactItems.push('✉  ' + profile.email);
  if (profile.phone)    contactItems.push('📞  ' + profile.phone);
  if (profile.location) contactItems.push('📍  ' + profile.location);
  if (profile.linkedin) contactItems.push('🔗  ' + profile.linkedin);
  if (profile.github)   contactItems.push('⌨  ' + profile.github);
  addLeftSection('CONTACT', contactItems);

  // Skills in left
  if (profile.skills) {
    for (const [cat, items] of Object.entries(profile.skills)) {
      leftChildren.push(new Paragraph({
        children: [t(cat, { size: 18, bold: true, color: RESUME_COLORS.WHITE })],
        spacing: { before: 160, after: 60 },
      }));
      for (const skill of (Array.isArray(items) ? items : [items])) {
        leftChildren.push(new Paragraph({
          children: [t('• ' + skill, { size: 18, color: RESUME_COLORS.ACCENT })],
          spacing: { before: 20, after: 20 },
        }));
      }
    }
  }

  // Right column: summary, experience, education
  rightChildren.push(...createSummarySection(profile.summary));
  rightChildren.push(...createExperienceSection(profile.experience));
  rightChildren.push(...createEducationSection(profile.education));
  rightChildren.push(...createProjectsSection(profile.projects));

  const mainTable = new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    layout: TableLayoutType.FIXED,
    rows: [new TableRow({
      children: [
        new TableCell({
          children: leftChildren,
          width: { size: 32, type: WidthType.PERCENTAGE },
          shading: { fill: RESUME_COLORS.MODERN_L, type: ShadingType.CLEAR },
          margins: { top: convertInchesToTwip(0.5), bottom: convertInchesToTwip(0.5), left: convertInchesToTwip(0.4), right: convertInchesToTwip(0.3) },
          borders: { top: { style: BorderStyle.NIL }, bottom: { style: BorderStyle.NIL }, left: { style: BorderStyle.NIL }, right: { style: BorderStyle.NIL } },
        }),
        new TableCell({
          children: rightChildren,
          width: { size: 68, type: WidthType.PERCENTAGE },
          margins: { top: convertInchesToTwip(0.5), bottom: convertInchesToTwip(0.5), left: convertInchesToTwip(0.4), right: convertInchesToTwip(0.4) },
          borders: { top: { style: BorderStyle.NIL }, bottom: { style: BorderStyle.NIL }, left: { style: BorderStyle.NIL }, right: { style: BorderStyle.NIL } },
        }),
      ],
    })],
  });

  return new Document({
    creator: profile.name,
    title: profile.name + ' – Modern Resume',
    sections: [{
      properties: {
        page: {
          margin: { top: 0, right: 0, bottom: 0, left: 0 },
        },
      },
      children: [mainTable],
    }],
  });
}

function buildAcademicCV(profile) {
  const children = [
    ...createContactHeader(profile),
    ...createSummarySection(profile.summary),
    ...createExperienceSection(profile.experience),
    ...createEducationSection(profile.education),
    ...createPublicationsSection(profile.publications),
    ...createSkillsSection(profile.skills),
    ...createCertificationsSection(profile.certifications),
  ];

  if (profile.grants && profile.grants.length > 0) {
    children.push(sectionHeading(SECTION_LABELS.GRANTS));
    for (const g of profile.grants) {
      children.push(new Paragraph({
        children: [
          t(g.title, { bold: true, size: 20 }),
          t(`  |  ${g.agency}  |  ${g.amount}  |  ${g.years}`, { size: 19, color: RESUME_COLORS.TEXT_LIGHT }),
        ],
        spacing: { before: 60, after: 60 },
        bullet: { level: 0 },
        indent: { left: 360, hanging: 180 },
      }));
    }
  }

  if (profile.teaching && profile.teaching.length > 0) {
    children.push(sectionHeading(SECTION_LABELS.TEACHING));
    for (const course of profile.teaching) {
      children.push(new Paragraph({
        children: [
          t(course.code + ': ' + course.name, { bold: true, size: 20 }),
          t('  |  ' + course.term, { size: 19, color: RESUME_COLORS.TEXT_LIGHT }),
        ],
        spacing: { before: 60, after: 60 },
        bullet: { level: 0 },
        indent: { left: 360, hanging: 180 },
      }));
    }
  }

  return new Document({
    creator: profile.name,
    title: profile.name + ' – Academic CV',
    description: 'Curriculum Vitae',
    sections: [{
      properties: {
        page: {
          margin: {
            top: convertInchesToTwip(1),
            right: convertInchesToTwip(1),
            bottom: convertInchesToTwip(1),
            left: convertInchesToTwip(1.25),
          },
        },
      },
      children,
    }],
  });
}

async function saveResume(doc, filePath) {
  const buffer = await Packer.toBuffer(doc);
  const dir = require('path').dirname(filePath);
  if (!require('fs').existsSync(dir)) require('fs').mkdirSync(dir, { recursive: true });
  require('fs').writeFileSync(filePath, buffer);
  return filePath;
}

module.exports = {
  buildResume,
  buildModernResume,
  buildAcademicCV,
  createContactHeader,
  createSummarySection,
  createExperienceSection,
  createEducationSection,
  createSkillsSection,
  createPublicationsSection,
  createCertificationsSection,
  createProjectsSection,
  saveResume,
  sectionHeading,
  bullet,
  blank,
  t,
  RESUME_COLORS,
  RESUME_FONTS,
  SECTION_LABELS,
  SAMPLE_PROFILE_1,
  SAMPLE_PROFILE_2,
  SAMPLE_PROFILE_3,
};
