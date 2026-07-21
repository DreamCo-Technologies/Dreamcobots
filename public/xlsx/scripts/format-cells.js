#!/usr/bin/env node
/**
 * format-cells.js
 * Demonstrates comprehensive cell formatting: fonts, fills, borders, alignment, number formats.
 * Usage: node format-cells.js [output.xlsx]
 */

const ExcelJS = require('exceljs');
const path = require('path');

const outputPath = process.argv[2] || path.join(__dirname, 'formatting-demo.xlsx');

async function main() {
  const wb = new ExcelJS.Workbook();
  const ws = wb.addWorksheet('Formatting Demo');
  ws.getColumn(1).width = 28;
  ws.getColumn(2).width = 32;

  function addDemoRow(label, cell, applyFn) {
    const row = ws.addRow([label, cell]);
    applyFn(row.getCell(2));
    row.height = 20;
  }

  // Section: Fonts
  ws.addRow(['FONTS']).font = { size: 14, bold: true, color: { argb: 'FF1F4E79' } };
  addDemoRow('Bold',         'Bold Text',         (c) => { c.font = { bold: true }; });
  addDemoRow('Italic',       'Italic Text',       (c) => { c.font = { italic: true }; });
  addDemoRow('Underline',    'Underlined Text',   (c) => { c.font = { underline: 'single' }; });
  addDemoRow('Strikethrough','Struck Out',        (c) => { c.font = { strike: true }; });
  addDemoRow('Colour',       'Coloured Text',     (c) => { c.font = { color: { argb: 'FFE74C3C' } }; });
  addDemoRow('Large Font',   'Large 16pt Text',   (c) => { c.font = { size: 16 }; });
  addDemoRow('Small Font',   'Small 8pt Text',    (c) => { c.font = { size: 8 }; });
  addDemoRow('Custom Font',  'Times New Roman',   (c) => { c.font = { name: 'Times New Roman', size: 12 }; });

  ws.addRow([]);
  // Section: Fills
  ws.addRow(['FILLS']).font = { size: 14, bold: true, color: { argb: 'FF1F4E79' } };
  addDemoRow('Solid Fill',      'Blue Background',    (c) => { c.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1F4E79' } }; c.font = { color: { argb: 'FFFFFFFF' } }; });
  addDemoRow('Light Fill',      'Light Blue',         (c) => { c.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFDEEAF1' } }; });
  addDemoRow('Yellow Highlight','Yellow',             (c) => { c.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFFFFF00' } }; });
  addDemoRow('Gray Fill',       'Gray',               (c) => { c.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFF2F2F2' } }; });

  ws.addRow([]);
  // Section: Borders
  ws.addRow(['BORDERS']).font = { size: 14, bold: true, color: { argb: 'FF1F4E79' } };
  const bStyles = ['thin', 'medium', 'thick', 'dashed', 'dotted', 'double'];
  bStyles.forEach((style) => {
    const b = { style, color: { argb: 'FF000000' } };
    addDemoRow(style, `${style} border`, (c) => {
      c.border = { top: b, left: b, bottom: b, right: b };
    });
  });

  ws.addRow([]);
  // Section: Alignment
  ws.addRow(['ALIGNMENT']).font = { size: 14, bold: true, color: { argb: 'FF1F4E79' } };
  addDemoRow('Left',       'Left aligned',   (c) => { c.alignment = { horizontal: 'left' }; });
  addDemoRow('Center',     'Centered',        (c) => { c.alignment = { horizontal: 'center' }; });
  addDemoRow('Right',      'Right aligned',  (c) => { c.alignment = { horizontal: 'right' }; });
  addDemoRow('Wrap Text',  'This text is long and will wrap within the cell if the column is narrow enough.', (c) => {
    c.alignment = { wrapText: true };
  });
  ws.getRow(ws.rowCount).height = 40;

  ws.addRow([]);
  // Section: Number Formats
  ws.addRow(['NUMBER FORMATS']).font = { size: 14, bold: true, color: { argb: 'FF1F4E79' } };
  const numFmts = [
    ['Currency',      1234567.89, '$#,##0.00'],
    ['Percentage',    0.1547,     '0.00%'],
    ['Integer',       98765,      '#,##0'],
    ['Scientific',    0.0000123,  '0.000E+00'],
    ['Date',          new Date(), 'yyyy-mm-dd'],
    ['Date+Time',     new Date(), 'yyyy-mm-dd hh:mm'],
    ['Fraction',      0.375,      '# ??/??'],
  ];
  numFmts.forEach(([label, val, fmt]) => {
    addDemoRow(label, val, (c) => { c.numFmt = fmt; });
  });

  await wb.xlsx.writeFile(outputPath);
  console.log(`Formatting demo created: ${outputPath}`);
}

main().catch((err) => { console.error(err); process.exit(1); });
