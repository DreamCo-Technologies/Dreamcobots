#!/usr/bin/env node
/**
 * create-presentation.js
 * Creates a complete corporate PowerPoint presentation.
 * Usage: node create-presentation.js [output.pptx]
 */

const PptxGenJS = require('pptxgenjs');
const path = require('path');

const outputPath = process.argv[2] || path.join(__dirname, 'presentation.pptx');

const BLUE   = '1F4E79';
const LBLUE  = '2E75B6';
const LLBLUE = 'DEEAF1';
const WHITE  = 'FFFFFF';
const GRAY   = '555555';

async function main() {
  const pres = new PptxGenJS();
  pres.layout  = 'LAYOUT_16x9';
  pres.author  = 'Dreamcobots';
  pres.company = 'DreamCo Technologies';
  pres.title   = 'Quarterly Business Review';

  // ── Define slide master ──────────────────────────────────────────────────────
  pres.defineSlideMaster({
    title: 'CORP',
    background: { fill: 'FAFAFA' },
    objects: [
      { rect: { x: 0, y: 5.25, w: '100%', h: 0.375, fill: BLUE } },
      { text: { text: 'DreamCo Technologies — Confidential', options: { x: 0.4, y: 5.28, fontSize: 8, color: 'AAAAAA', w: 7 } } },
    ],
    slideNumber: { x: 9.2, y: 5.28, color: 'AAAAAA', fontSize: 8 },
  });

  // ── Slide 1: Title ───────────────────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { fill: BLUE };
    s.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: '100%', h: '100%', fill: BLUE });
    s.addShape(pres.ShapeType.rect, { x: 0, y: 3.8, w: '100%', h: 1.825, fill: '163859' });
    s.addText('Q4 2024', { x: 0.8, y: 0.6, w: 8, h: 0.8, fontSize: 20, color: '9DC3E6', bold: false });
    s.addText('Quarterly Business Review', { x: 0.8, y: 1.3, w: 8.4, h: 1.8, fontSize: 44, bold: true, color: WHITE });
    s.addText('DreamCo Technologies', { x: 0.8, y: 3.95, w: 6, h: 0.5, fontSize: 18, color: '9DC3E6' });
    s.addText(new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }), {
      x: 0.8, y: 4.5, w: 6, h: 0.4, fontSize: 14, color: '9DC3E6',
    });
  }

  // ── Slide 2: Agenda ──────────────────────────────────────────────────────────
  {
    const s = pres.addSlide({ masterName: 'CORP' });
    s.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: '100%', h: 1, fill: BLUE });
    s.addText('Agenda', { x: 0.5, y: 0.15, w: 9, h: 0.7, fontSize: 30, bold: true, color: WHITE });
    const items = [
      '1.  Financial Highlights',
      '2.  Sales Performance',
      '3.  Regional Breakdown',
      '4.  Product Updates',
      '5.  Q1 2025 Outlook',
    ];
    s.addText(
      items.map((t) => ({ text: t, options: { paraSpaceAfter: 8 } })),
      { x: 1, y: 1.3, w: 8, h: 3.5, fontSize: 20, color: '333333' }
    );
  }

  // ── Slide 3: Key Metrics ─────────────────────────────────────────────────────
  {
    const s = pres.addSlide({ masterName: 'CORP' });
    s.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: '100%', h: 1, fill: BLUE });
    s.addText('Financial Highlights', { x: 0.5, y: 0.15, w: 9, h: 0.7, fontSize: 30, bold: true, color: WHITE });

    const kpis = [
      { label: 'Revenue', value: '$12.4M', change: '+18%', good: true },
      { label: 'Gross Margin', value: '38.2%', change: '+2.1pp', good: true },
      { label: 'Operating Costs', value: '$7.7M', change: '+12%', good: false },
      { label: 'Net Income', value: '$2.1M', change: '+24%', good: true },
    ];

    kpis.forEach((kpi, i) => {
      const col = i % 2;
      const row = Math.floor(i / 2);
      const x = 0.4 + col * 4.7;
      const y = 1.3 + row * 1.9;

      s.addShape(pres.ShapeType.roundRect, { x, y, w: 4.2, h: 1.6, fill: LLBLUE, line: { color: LBLUE, width: 1 }, rectRadius: 0.1 });
      s.addText(kpi.label, { x: x + 0.2, y: y + 0.1, w: 3.8, h: 0.4, fontSize: 13, color: GRAY });
      s.addText(kpi.value,  { x: x + 0.2, y: y + 0.45, w: 2.5, h: 0.7, fontSize: 30, bold: true, color: BLUE });
      s.addText(kpi.change, { x: x + 2.8, y: y + 0.55, w: 1.2, h: 0.5, fontSize: 16, bold: true, color: kpi.good ? '276221' : 'C00000', align: 'right' });
    });
  }

  // ── Slide 4: Chart ───────────────────────────────────────────────────────────
  {
    const s = pres.addSlide({ masterName: 'CORP' });
    s.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: '100%', h: 1, fill: BLUE });
    s.addText('Sales Performance', { x: 0.5, y: 0.15, w: 9, h: 0.7, fontSize: 30, bold: true, color: WHITE });

    s.addChart(pres.ChartType.bar,
      [
        { name: 'Actual',  labels: ['Q1','Q2','Q3','Q4'], values: [9200, 10500, 11800, 12400] },
        { name: 'Target',  labels: ['Q1','Q2','Q3','Q4'], values: [9000, 10000, 11000, 12000] },
      ],
      {
        x: 0.4, y: 1.1, w: 9.2, h: 3.9,
        barDir: 'col', barGrouping: 'clustered',
        chartColors: [BLUE, '9DC3E6'],
        showLegend: true, legendPos: 'b',
        showValue: true, dataLabelFontSize: 9, dataLabelColor: WHITE,
        title: 'Quarterly Revenue ($K)', showTitle: true, titleFontSize: 14,
        valAxisLabelColor: GRAY, catAxisLabelColor: GRAY,
      }
    );
  }

  // ── Slide 5: Closing ─────────────────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { fill: BLUE };
    s.addText('Thank You', { x: 1, y: 1.5, w: 8, h: 1.5, fontSize: 54, bold: true, color: WHITE, align: 'center' });
    s.addText('Questions & Discussion', { x: 1, y: 3.2, w: 8, h: 0.6, fontSize: 22, color: '9DC3E6', align: 'center' });
    s.addText('info@dreamco.com', {
      x: 3, y: 4.1, w: 4, h: 0.5, fontSize: 16, color: '9DC3E6', align: 'center',
      hyperlink: { url: 'mailto:info@dreamco.com' },
    });
  }

  await pres.writeFile({ fileName: outputPath });
  console.log(`Presentation created: ${outputPath}`);
}

main().catch((err) => { console.error(err); process.exit(1); });
