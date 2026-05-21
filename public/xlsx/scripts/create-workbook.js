#!/usr/bin/env node
/**
 * create-workbook.js
 * Creates a formatted Excel workbook with multiple sheets.
 * Usage: node create-workbook.js [output.xlsx]
 */

const ExcelJS = require('exceljs');
const path = require('path');

const outputPath = process.argv[2] || path.join(__dirname, 'workbook.xlsx');

const HEADER_FILL  = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1F4E79' } };
const ALT_ROW_FILL = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFF2F8FF' } };
const HEADER_FONT  = { bold: true, color: { argb: 'FFFFFFFF' }, size: 11 };
const BORDER_THIN  = { style: 'thin', color: { argb: 'FFCCCCCC' } };
const ALL_BORDERS  = { top: BORDER_THIN, left: BORDER_THIN, bottom: BORDER_THIN, right: BORDER_THIN };

const salesData = [
  { id: 1, rep: 'Alice Johnson', region: 'North', product: 'Widget A', qty: 150, price: 29.99, date: new Date('2024-01-15') },
  { id: 2, rep: 'Bob Smith',     region: 'South', product: 'Widget B', qty: 80,  price: 49.99, date: new Date('2024-01-18') },
  { id: 3, rep: 'Carol White',   region: 'East',  product: 'Widget A', qty: 200, price: 29.99, date: new Date('2024-01-20') },
  { id: 4, rep: 'Dave Brown',    region: 'West',  product: 'Widget C', qty: 60,  price: 99.99, date: new Date('2024-01-22') },
  { id: 5, rep: 'Eve Davis',     region: 'North', product: 'Widget B', qty: 120, price: 49.99, date: new Date('2024-01-25') },
];

async function main() {
  const wb = new ExcelJS.Workbook();
  wb.creator = 'Dreamcobots';
  wb.created = new Date();

  // ── Sheet 1: Sales Data ──────────────────────────────────────────────────────
  const salesSheet = wb.addWorksheet('Sales Data', {
    views: [{ state: 'frozen', ySplit: 1 }],
    pageSetup: { paperSize: 9, fitToPage: true, fitToWidth: 1 },
  });

  salesSheet.columns = [
    { header: 'ID',         key: 'id',      width: 6  },
    { header: 'Sales Rep',  key: 'rep',     width: 22 },
    { header: 'Region',     key: 'region',  width: 12 },
    { header: 'Product',    key: 'product', width: 16 },
    { header: 'Qty',        key: 'qty',     width: 8,  style: { numFmt: '#,##0' } },
    { header: 'Unit Price', key: 'price',   width: 12, style: { numFmt: '$#,##0.00' } },
    { header: 'Revenue',    key: 'revenue', width: 14, style: { numFmt: '$#,##0.00' } },
    { header: 'Date',       key: 'date',    width: 14, style: { numFmt: 'yyyy-mm-dd' } },
  ];

  // Style header
  salesSheet.getRow(1).eachCell((cell) => {
    cell.font = HEADER_FONT;
    cell.fill = HEADER_FILL;
    cell.border = ALL_BORDERS;
    cell.alignment = { horizontal: 'center', vertical: 'middle' };
  });
  salesSheet.getRow(1).height = 22;

  // Add data rows
  salesData.forEach((row, i) => {
    const rowIndex = i + 2;
    const excelRow = salesSheet.addRow({
      ...row,
      revenue: { formula: `E${rowIndex}*F${rowIndex}` },
    });
    if (i % 2 === 1) {
      excelRow.eachCell((cell) => { cell.fill = ALT_ROW_FILL; });
    }
    excelRow.eachCell((cell) => { cell.border = ALL_BORDERS; });
  });

  // Totals row
  const totalRow = salesData.length + 2;
  salesSheet.addRow({
    rep: 'TOTAL',
    qty:     { formula: `SUM(E2:E${totalRow - 1})` },
    revenue: { formula: `SUM(G2:G${totalRow - 1})` },
  });
  const tRow = salesSheet.getRow(totalRow);
  tRow.font = { bold: true };
  tRow.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFDEEAF1' } };
  tRow.eachCell((cell) => { cell.border = ALL_BORDERS; });

  // Auto-filter
  salesSheet.autoFilter = { from: 'A1', to: 'H1' };

  // ── Sheet 2: Summary ─────────────────────────────────────────────────────────
  const summarySheet = wb.addWorksheet('Summary');
  summarySheet.getCell('A1').value = 'Sales Summary';
  summarySheet.getCell('A1').font = { size: 16, bold: true, color: { argb: 'FF1F4E79' } };
  summarySheet.mergeCells('A1:D1');

  const summaryHeaders = ['Metric', 'Value'];
  summarySheet.addRow(summaryHeaders).eachCell((cell) => {
    cell.font = HEADER_FONT;
    cell.fill = HEADER_FILL;
  });

  const metrics = [
    ['Total Transactions', salesData.length],
    ['Total Revenue', { formula: "'Sales Data'!G" + totalRow }],
    ['Average Unit Price', { formula: `AVERAGE('Sales Data'!F2:F${totalRow - 1})` }],
  ];
  metrics.forEach(([label, val]) => {
    summarySheet.addRow([label, val]);
  });
  summarySheet.getColumn(1).width = 25;
  summarySheet.getColumn(2).width = 18;
  summarySheet.getColumn(2).numFmt = '$#,##0.00';

  // ── Save ─────────────────────────────────────────────────────────────────────
  await wb.xlsx.writeFile(outputPath);
  console.log(`Workbook created: ${outputPath}`);
}

main().catch((err) => { console.error(err.message); process.exit(1); });
