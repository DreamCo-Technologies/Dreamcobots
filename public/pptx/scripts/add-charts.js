#!/usr/bin/env node
/**
 * add-charts.js
 * Demonstrates various chart types in pptxgenjs.
 * Usage: node add-charts.js [output.pptx]
 */

const PptxGenJS = require('pptxgenjs');
const path = require('path');

const outputPath = process.argv[2] || path.join(__dirname, 'charts-demo.pptx');

const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun'];
const REVENUE  = [42500, 38900, 51200, 47800, 55300, 61200];
const TARGET   = [40000, 42000, 44000, 46000, 48000, 50000];
const EXPENSES = [28000, 25600, 31400, 29800, 34100, 38500];

async function main() {
  const pres = new PptxGenJS();

  function titleSlide(title) {
    const s = pres.addSlide();
    s.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: '100%', h: 0.9, fill: '1F4E79' });
    s.addText(title, { x: 0.4, y: 0.1, w: 9.2, h: 0.7, fontSize: 26, bold: true, color: 'FFFFFF' });
    return s;
  }

  // Bar chart
  const s1 = titleSlide('Clustered Bar Chart');
  s1.addChart(pres.ChartType.bar,
    [
      { name: 'Revenue',  labels: MONTHS, values: REVENUE },
      { name: 'Target',   labels: MONTHS, values: TARGET },
      { name: 'Expenses', labels: MONTHS, values: EXPENSES },
    ],
    { x: 0.3, y: 1, w: 9.4, h: 4.2, barDir: 'col', barGrouping: 'clustered',
      chartColors: ['1F4E79','2E75B6','9DC3E6'], showLegend: true, legendPos: 'b',
      showValue: false, valAxisLabelColor: '555555', catAxisLabelColor: '555555' }
  );

  // Line chart
  const s2 = titleSlide('Line Chart — Revenue Trend');
  s2.addChart(pres.ChartType.line,
    [
      { name: 'Revenue',  labels: MONTHS, values: REVENUE },
      { name: 'Target',   labels: MONTHS, values: TARGET },
    ],
    { x: 0.3, y: 1, w: 9.4, h: 4.2, lineSize: 2.5, lineSmooth: true,
      showDot: true, dotSize: 6, chartColors: ['1F4E79', 'E74C3C'],
      showLegend: true, legendPos: 'b', valAxisLabelColor: '555555' }
  );

  // Pie chart
  const s3 = titleSlide('Pie Chart — Market Share');
  s3.addChart(pres.ChartType.pie,
    [{ name: 'Share', labels: ['North America','Europe','Asia Pacific','Other'], values: [38, 27, 24, 11] }],
    { x: 1, y: 1, w: 8, h: 4.2, showLegend: true, legendPos: 'r',
      showPercent: true, chartColors: ['1F4E79','2E75B6','9DC3E6','D6E4F0'],
      dataLabelFontSize: 13, dataLabelColor: 'FFFFFF' }
  );

  // Doughnut
  const s4 = titleSlide('Doughnut Chart — Product Mix');
  s4.addChart(pres.ChartType.doughnut,
    [{ name: 'Mix', labels: ['Widget A','Widget B','Widget C','Services'], values: [35, 28, 22, 15] }],
    { x: 1, y: 1, w: 8, h: 4.2, holeSize: 55, showLegend: true, legendPos: 'b',
      showPercent: true, chartColors: ['1F4E79','2E75B6','9DC3E6','BDD7EE'] }
  );

  // Stacked bar
  const s5 = titleSlide('Stacked Bar — Cost Breakdown');
  s5.addChart(pres.ChartType.bar,
    [
      { name: 'COGS',   labels: MONTHS, values: [18000,16000,20000,19000,22000,24000] },
      { name: 'OpEx',   labels: MONTHS, values: [8000, 8000, 9000, 9000, 10000, 12000] },
      { name: 'Other',  labels: MONTHS, values: [2000, 1600, 2400, 1800, 2100, 2500] },
    ],
    { x: 0.3, y: 1, w: 9.4, h: 4.2, barDir: 'col', barGrouping: 'stacked',
      chartColors: ['1F4E79','2E75B6','9DC3E6'], showLegend: true, legendPos: 'b' }
  );

  await pres.writeFile({ fileName: outputPath });
  console.log(`Charts demo: ${outputPath}`);
}

main().catch((err) => { console.error(err); process.exit(1); });
