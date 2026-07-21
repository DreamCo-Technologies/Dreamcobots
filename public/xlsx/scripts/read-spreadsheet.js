#!/usr/bin/env node
/**
 * read-spreadsheet.js
 * Reads an Excel file and outputs contents as JSON or CSV.
 * Usage: node read-spreadsheet.js <file.xlsx> [--sheet=<name>] [--csv] [--all]
 */

const XLSX = require('xlsx');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const filePath = args.find((a) => !a.startsWith('--'));
const sheetArg = args.find((a) => a.startsWith('--sheet='));
const sheetName = sheetArg ? sheetArg.split('=')[1] : null;
const outputCsv = args.includes('--csv');
const allSheets = args.includes('--all');

if (!filePath) {
  console.error('Usage: node read-spreadsheet.js <file.xlsx> [--sheet=<name>] [--csv] [--all]');
  process.exit(1);
}
if (!fs.existsSync(filePath)) {
  console.error(`File not found: ${filePath}`);
  process.exit(1);
}

function processSheet(ws, name) {
  const range = XLSX.utils.decode_range(ws['!ref'] || 'A1:A1');
  const rowCount = range.e.r - range.s.r + 1;
  const colCount = range.e.c - range.s.c + 1;
  console.log(`\n=== Sheet: "${name}" (${rowCount} rows × ${colCount} cols) ===`);

  if (outputCsv) {
    const csv = XLSX.utils.sheet_to_csv(ws);
    const outFile = `${path.basename(filePath, path.extname(filePath))}_${name}.csv`;
    fs.writeFileSync(outFile, csv);
    console.log(`CSV saved: ${outFile}`);
  } else {
    const rows = XLSX.utils.sheet_to_json(ws, { defval: null });
    console.log(JSON.stringify(rows.slice(0, 5), null, 2));
    if (rows.length > 5) console.log(`... (${rows.length - 5} more rows)`);
  }
}

const wb = XLSX.readFile(filePath, { cellDates: true, cellNF: true });
console.log(`Opened: ${filePath}`);
console.log(`Sheets: ${wb.SheetNames.join(', ')}`);

if (allSheets) {
  wb.SheetNames.forEach((name) => processSheet(wb.Sheets[name], name));
} else {
  const name = sheetName || wb.SheetNames[0];
  if (!wb.Sheets[name]) {
    console.error(`Sheet "${name}" not found. Available: ${wb.SheetNames.join(', ')}`);
    process.exit(1);
  }
  processSheet(wb.Sheets[name], name);
}
