# Excel Spreadsheet Manipulation — SKILL.md

Practical guide for working with Excel files using SheetJS (`xlsx`) and ExcelJS.

## Choosing a Library

| Need | Use |
|------|-----|
| Fast read/write, minimal formatting | SheetJS (`xlsx`) |
| Rich cell styles, images, charts | ExcelJS (`exceljs`) |
| CSV / ODS / XLS support | SheetJS |
| Conditional formatting | ExcelJS |
| Streaming large files | ExcelJS streaming API |

## SheetJS Cheatsheet

```js
const XLSX = require('xlsx');

// Read
const wb = XLSX.readFile('file.xlsx', { cellDates: true });
const ws = wb.Sheets[wb.SheetNames[0]];
const rows = XLSX.utils.sheet_to_json(ws);

// Create & write
const newWb = XLSX.utils.book_new();
const newWs = XLSX.utils.json_to_sheet(rows);
ws['!cols'] = [{ wch: 20 }, { wch: 15 }];
XLSX.utils.book_append_sheet(newWb, newWs, 'Sheet1');
XLSX.writeFile(newWb, 'out.xlsx');
```

## ExcelJS Cheatsheet

```js
const ExcelJS = require('exceljs');

async function run() {
  const wb = new ExcelJS.Workbook();
  const ws = wb.addWorksheet('Data');
  ws.columns = [
    { header: 'Name',  key: 'name',  width: 20 },
    { header: 'Score', key: 'score', width: 10, style: { numFmt: '0.00' } },
  ];
  ws.addRow({ name: 'Alice', score: 94.5 });
  ws.addRow({ name: 'Bob',   score: 87.0 });
  // Style header
  ws.getRow(1).font = { bold: true };
  ws.getRow(1).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1F4E79' } };
  await wb.xlsx.writeFile('out.xlsx');
}
run();
```

## Reading All Sheets

```js
const XLSX = require('xlsx');
const wb = XLSX.readFile('multi-sheet.xlsx');

wb.SheetNames.forEach((name) => {
  const rows = XLSX.utils.sheet_to_json(wb.Sheets[name]);
  console.log(`${name}: ${rows.length} rows`);
});
```

## Formulas

```js
// SheetJS
ws['B10'] = { t: 'f', f: 'SUM(B2:B9)' };

// ExcelJS
sheet.getCell('B10').value = { formula: 'SUM(B2:B9)', result: 0 };
```

## Formatting Numbers & Dates

```js
// ExcelJS numFmt codes
'$#,##0.00'      // currency
'0.00%'          // percentage
'yyyy-mm-dd'     // ISO date
'#,##0'          // thousands separator
'0.000E+00'      // scientific
```

## Conditional Formatting (ExcelJS)

```js
sheet.addConditionalFormatting({
  ref: 'B2:B50',
  rules: [{
    type: 'colorScale',
    colorScale: {
      cfvo: [{ type: 'min' }, { type: 'max' }],
      color: [{ argb: 'FFF8696B' }, { argb: 'FF63BE7B' }],
    },
  }],
});
```

## Data Validation (ExcelJS)

```js
sheet.dataValidations.add('C2:C100', {
  type: 'list',
  formulae: ['"Apple,Banana,Cherry"'],
  showErrorMessage: true,
});
```

## Streaming Large Files

```js
// ExcelJS streaming write
const workbook = new ExcelJS.stream.xlsx.WorkbookWriter({ filename: 'big.xlsx' });
const sheet = workbook.addWorksheet('Data');
sheet.columns = [{ header: 'ID', key: 'id' }, { header: 'Val', key: 'val' }];

for (let i = 0; i < 1_000_000; i++) {
  sheet.addRow({ id: i, val: Math.random() }).commit();
}
await sheet.commit();
await workbook.commit();
```

## CSV Export

```js
// SheetJS
const csv = XLSX.utils.sheet_to_csv(ws);
fs.writeFileSync('data.csv', csv);

// ExcelJS
await workbook.csv.writeFile('data.csv');
```

## Tips

- Use `cellDates: true` in SheetJS to get JavaScript `Date` objects.
- ExcelJS ARGB = `FF` + 6-char hex (e.g. `FF1F4E79`).
- Freeze header: `ws.views = [{ state: 'frozen', ySplit: 1 }]`.
- Auto-fit columns by measuring longest string in each column before setting `wch`.
