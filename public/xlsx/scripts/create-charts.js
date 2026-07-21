#!/usr/bin/env node
/**
 * create-charts.js
 * Creates an Excel workbook with chart data and instructions for chart creation.
 * Note: ExcelJS has limited chart support. For full chart embedding use xlsx-chart package.
 * Usage: node create-charts.js [output.xlsx]
 */

const ExcelJS = require('exceljs');
const path = require('path');

const outputPath = process.argv[2] || path.join(__dirname, 'charts-demo.xlsx');

const monthlyData = [
  { month: 'Jan', sales: 42500, target: 40000, expenses: 28000 },
  { month: 'Feb', sales: 38900, target: 41000, expenses: 25600 },
  { month: 'Mar', sales: 51200, target: 42000, expenses: 31400 },
  { month: 'Apr', sales: 47800, target: 43000, expenses: 29800 },
  { month: 'May', sales: 55300, target: 44000, expenses: 34100 },
  { month: 'Jun', sales: 61200, target: 45000, expenses: 38500 },
];

async function main() {
  const wb = new ExcelJS.Workbook();

  // Data sheet
  const ws = wb.addWorksheet('Chart Data', { views: [{ state: 'frozen', ySplit: 1 }] });
  ws.columns = [
    { header: 'Month',    key: 'month',    width: 10 },
    { header: 'Sales',    key: 'sales',    width: 14, style: { numFmt: '$#,##0' } },
    { header: 'Target',   key: 'target',   width: 14, style: { numFmt: '$#,##0' } },
    { header: 'Expenses', key: 'expenses', width: 14, style: { numFmt: '$#,##0' } },
    { header: 'Variance', key: 'variance', width: 14, style: { numFmt: '$#,##0;($#,##0)' } },
    { header: 'Var %',    key: 'varPct',   width: 10, style: { numFmt: '0.0%' } },
  ];

  ws.getRow(1).eachCell((c) => {
    c.font = { bold: true, color: { argb: 'FFFFFFFF' } };
    c.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1F4E79' } };
  });

  monthlyData.forEach((row, i) => {
    const r = i + 2;
    ws.addRow({
      ...row,
      variance: { formula: `B${r}-C${r}` },
      varPct:   { formula: `IF(C${r}=0,0,(B${r}-C${r})/C${r})` },
    });
  });

  // Conditional formatting for variance
  ws.addConditionalFormatting({
    ref: `E2:E${monthlyData.length + 1}`,
    rules: [
      {
        type: 'cellIs',
        operator: 'greaterThan',
        formulae: [0],
        style: { font: { color: { argb: 'FF276221' } }, fill: { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFC6EFCE' } } },
      },
      {
        type: 'cellIs',
        operator: 'lessThan',
        formulae: [0],
        style: { font: { color: { argb: 'FF9C0006' } }, fill: { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFFFC7CE' } } },
      },
    ],
  });

  // Instructions sheet
  const instrSheet = wb.addWorksheet('Chart Instructions');
  instrSheet.getColumn(1).width = 80;

  const instructions = [
    'HOW TO CREATE CHARTS FROM THIS DATA',
    '',
    'Excel charts can be created manually or via VBA/OpenXML after opening this file.',
    '',
    '1. Select the data range in "Chart Data" sheet (A1:D7)',
    '2. Insert > Chart > Select chart type (Bar, Line, Pie, etc.)',
    '3. Suggested charts for this dataset:',
    '   - Clustered Bar: Compare Sales vs Target per month',
    '   - Line Chart: Show Sales trend over time',
    '   - Combo Chart: Bars for Sales/Target, Line for Expenses',
    '',
    'For programmatic chart creation, use:',
    '  npm install xlsx-chart',
    '',
    'Example with xlsx-chart:',
    "  const XLSXChart = require('xlsx-chart');",
    "  const xlsxChart = new XLSXChart();",
    '  const opts = {',
    "    chart: 'bar',",
    "    titles: ['Month', 'Sales', 'Target'],",
    "    fields: ['month', 'sales', 'target'],",
    '    data: monthlyData,',
    "    chartTitle: 'Monthly Sales vs Target',",
    '  };',
    "  xlsxChart.generate(opts, (err, data) => {",
    "    fs.writeFileSync('chart.xlsx', data);",
    '  });',
  ];

  instructions.forEach((line, i) => {
    const row = instrSheet.addRow([line]);
    if (i === 0) row.font = { size: 14, bold: true, color: { argb: 'FF1F4E79' } };
    else if (line.startsWith('   -') || line.startsWith('  ') ) row.font = { name: 'Courier New', size: 10 };
  });

  await wb.xlsx.writeFile(outputPath);
  console.log(`Charts demo workbook created: ${outputPath}`);
}

main().catch((err) => { console.error(err); process.exit(1); });
