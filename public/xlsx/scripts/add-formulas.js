#!/usr/bin/env node
/**
 * add-formulas.js
 * Demonstrates Excel formulas, named ranges, and calculated columns.
 * Usage: node add-formulas.js [output.xlsx]
 */

const ExcelJS = require('exceljs');
const path = require('path');

const outputPath = process.argv[2] || path.join(__dirname, 'formulas-demo.xlsx');

const data = [
  { month: 'January',   revenue: 42500, costs: 28000 },
  { month: 'February',  revenue: 38900, costs: 25600 },
  { month: 'March',     revenue: 51200, costs: 31400 },
  { month: 'April',     revenue: 47800, costs: 29800 },
  { month: 'May',       revenue: 55300, costs: 34100 },
  { month: 'June',      revenue: 61200, costs: 38500 },
];

async function main() {
  const wb = new ExcelJS.Workbook();
  const ws = wb.addWorksheet('Financial Model', { views: [{ state: 'frozen', ySplit: 1 }] });

  ws.columns = [
    { header: 'Month',      key: 'month',   width: 14 },
    { header: 'Revenue',    key: 'revenue', width: 14, style: { numFmt: '$#,##0' } },
    { header: 'Costs',      key: 'costs',   width: 14, style: { numFmt: '$#,##0' } },
    { header: 'Gross Profit', key: 'profit', width: 16, style: { numFmt: '$#,##0' } },
    { header: 'Margin %',   key: 'margin',  width: 12, style: { numFmt: '0.0%' } },
    { header: 'vs Prior',   key: 'prior',   width: 12, style: { numFmt: '$#,##0;($#,##0)' } },
    { header: 'Cumulative', key: 'cumul',   width: 14, style: { numFmt: '$#,##0' } },
  ];

  // Header style
  ws.getRow(1).eachCell((cell) => {
    cell.font = { bold: true, color: { argb: 'FFFFFFFF' } };
    cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1F4E79' } };
    cell.alignment = { horizontal: 'center' };
  });

  data.forEach((row, i) => {
    const r = i + 2;
    ws.addRow({
      month:   row.month,
      revenue: row.revenue,
      costs:   row.costs,
      profit:  { formula: `B${r}-C${r}` },
      margin:  { formula: `IF(B${r}=0,0,D${r}/B${r})` },
      prior:   i === 0
        ? { formula: '0' }
        : { formula: `D${r}-D${r - 1}` },
      cumul: i === 0
        ? { formula: `D${r}` }
        : { formula: `G${r - 1}+D${r}` },
    });
  });

  // Totals row
  const lastData = data.length + 1;
  const totalsRow = lastData + 1;
  ws.addRow({
    month:   'TOTAL',
    revenue: { formula: `SUM(B2:B${lastData})` },
    costs:   { formula: `SUM(C2:C${lastData})` },
    profit:  { formula: `SUM(D2:D${lastData})` },
    margin:  { formula: `IF(B${totalsRow}=0,0,D${totalsRow}/B${totalsRow})` },
    prior:   '',
    cumul:   { formula: `G${lastData}` },
  });
  ws.getRow(totalsRow).font = { bold: true };
  ws.getRow(totalsRow).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFDEEAF1' } };

  // Conditional formatting for margin
  ws.addConditionalFormatting({
    ref: `E2:E${lastData}`,
    rules: [{
      type: 'colorScale',
      colorScale: {
        cfvo: [{ type: 'min' }, { type: 'max' }],
        color: [{ argb: 'FFF8696B' }, { argb: 'FF63BE7B' }],
      },
    }],
  });

  await wb.xlsx.writeFile(outputPath);
  console.log(`Formulas workbook created: ${outputPath}`);
}

main().catch((err) => { console.error(err); process.exit(1); });
