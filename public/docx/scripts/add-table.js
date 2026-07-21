#!/usr/bin/env node
/**
 * add-table.js
 * Demonstrates creating rich tables in a Word document.
 * Usage: node add-table.js [output.docx]
 */

const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, WidthType, BorderStyle, ShadingType,
  VerticalAlign, TableLayoutType,
} = require('docx');
const fs = require('fs');
const path = require('path');

const outputPath = process.argv[2] || path.join(__dirname, 'table-demo.docx');

// Sample data
const salesData = [
  { region: 'North America', q1: 42500, q2: 48300, q3: 51200, q4: 55800 },
  { region: 'Europe',        q1: 31200, q2: 33900, q3: 29800, q4: 38100 },
  { region: 'Asia Pacific',  q1: 27400, q2: 32100, q3: 35600, q4: 41200 },
  { region: 'Latin America', q1: 12800, q2: 14200, q3: 15600, q4: 17300 },
  { region: 'Middle East',   q1: 8900,  q2: 9700,  q3: 10300, q4: 11800 },
];

function formatCurrency(n) {
  return `$${n.toLocaleString()}`;
}

function headerCell(text) {
  return new TableCell({
    children: [
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text, bold: true, color: 'FFFFFF', size: 20 })],
      }),
    ],
    shading: { type: ShadingType.SOLID, color: '1F4E79' },
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: 100, bottom: 100, left: 120, right: 120 },
  });
}

function dataCell(text, isHighlighted = false) {
  return new TableCell({
    children: [
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text, size: 20 })],
      }),
    ],
    shading: isHighlighted ? { type: ShadingType.SOLID, color: 'EBF3FB' } : undefined,
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: 80, bottom: 80, left: 100, right: 100 },
  });
}

async function main() {
  // Calculate totals row
  const totals = salesData.reduce(
    (acc, row) => {
      acc.q1 += row.q1; acc.q2 += row.q2; acc.q3 += row.q3; acc.q4 += row.q4;
      return acc;
    },
    { q1: 0, q2: 0, q3: 0, q4: 0 }
  );

  const table = new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    layout: TableLayoutType.FIXED,
    borders: {
      top:              { style: BorderStyle.SINGLE, size: 2, color: '1F4E79' },
      bottom:           { style: BorderStyle.SINGLE, size: 2, color: '1F4E79' },
      left:             { style: BorderStyle.SINGLE, size: 2, color: '1F4E79' },
      right:            { style: BorderStyle.SINGLE, size: 2, color: '1F4E79' },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 1, color: 'AAAAAA' },
      insideVertical:   { style: BorderStyle.SINGLE, size: 1, color: 'AAAAAA' },
    },
    rows: [
      // Header row
      new TableRow({
        tableHeader: true,
        children: [
          headerCell('Region'),
          headerCell('Q1'),
          headerCell('Q2'),
          headerCell('Q3'),
          headerCell('Q4'),
        ],
      }),
      // Data rows (alternating shading)
      ...salesData.map((row, i) =>
        new TableRow({
          children: [
            new TableCell({
              children: [
                new Paragraph({
                  children: [new TextRun({ text: row.region, bold: true, size: 20 })],
                }),
              ],
              margins: { top: 80, bottom: 80, left: 100, right: 100 },
              shading: i % 2 === 0 ? undefined : { type: ShadingType.SOLID, color: 'F5F5F5' },
            }),
            dataCell(formatCurrency(row.q1), i % 2 !== 0),
            dataCell(formatCurrency(row.q2), i % 2 !== 0),
            dataCell(formatCurrency(row.q3), i % 2 !== 0),
            dataCell(formatCurrency(row.q4), i % 2 !== 0),
          ],
        })
      ),
      // Totals row
      new TableRow({
        children: [
          new TableCell({
            children: [
              new Paragraph({
                children: [new TextRun({ text: 'TOTAL', bold: true, color: 'FFFFFF', size: 20 })],
              }),
            ],
            shading: { type: ShadingType.SOLID, color: '2E75B6' },
            margins: { top: 100, bottom: 100, left: 100, right: 100 },
          }),
          ...[totals.q1, totals.q2, totals.q3, totals.q4].map(
            (val) =>
              new TableCell({
                children: [
                  new Paragraph({
                    alignment: AlignmentType.CENTER,
                    children: [new TextRun({ text: formatCurrency(val), bold: true, color: 'FFFFFF', size: 20 })],
                  }),
                ],
                shading: { type: ShadingType.SOLID, color: '2E75B6' },
                margins: { top: 100, bottom: 100, left: 100, right: 100 },
              })
          ),
        ],
      }),
    ],
  });

  const doc = new Document({
    sections: [{
      children: [
        new Paragraph({
          text: 'Regional Sales Report',
          heading: HeadingLevel.HEADING_1,
          spacing: { after: 200 },
        }),
        new Paragraph({
          text: 'Quarterly revenue by region (USD)',
          spacing: { after: 300 },
          children: [new TextRun({ text: 'Quarterly revenue by region (USD)', italics: true, color: '555555' })],
        }),
        table,
        new Paragraph({
          spacing: { before: 200 },
          children: [
            new TextRun({ text: 'Note: ', bold: true }),
            new TextRun('All figures in US dollars. Totals may include rounding.'),
          ],
        }),
      ],
    }],
  });

  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(outputPath, buffer);
  console.log(`Table document created: ${outputPath}`);
}

main().catch((err) => { console.error(err); process.exit(1); });
