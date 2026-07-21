# PDF Reading & Content Extraction — SKILL.md

## Quick Start

```bash
npm install pdf-parse pdf-lib pdfjs-dist
```

### Extract All Text (Simplest)

```js
const pdfParse = require('pdf-parse');
const fs = require('fs');

async function getText(pdfPath) {
  const { text, numpages, info } = await pdfParse(fs.readFileSync(pdfPath));
  console.log(`${numpages} pages, ${text.length} characters`);
  return text;
}
```

### Per-Page Text

```js
const pdfParse = require('pdf-parse');
const fs = require('fs');

const pages = [];

async function getPageTexts(pdfPath) {
  await pdfParse(fs.readFileSync(pdfPath), {
    pagerender: async (pageData) => {
      const { items } = await pageData.getTextContent();
      pages.push(items.map((i) => i.str).join(' '));
      return '';
    },
  });
  return pages;
}
```

### Metadata

```js
const { PDFDocument } = require('pdf-lib');
const fs = require('fs');

async function getMeta(pdfPath) {
  const doc = await PDFDocument.load(fs.readFileSync(pdfPath));
  return {
    title:  doc.getTitle(),
    author: doc.getAuthor(),
    pages:  doc.getPageCount(),
  };
}
```

### Form Field Values

```js
const { PDFDocument } = require('pdf-lib');
const fs = require('fs');

async function getFormValues(pdfPath) {
  const doc = await PDFDocument.load(fs.readFileSync(pdfPath));
  const form = doc.getForm();
  const values = {};
  form.getFields().forEach((f) => {
    const n = f.getName();
    const t = f.constructor.name;
    if (t === 'PDFTextField') values[n] = f.getText();
    else if (t === 'PDFCheckBox') values[n] = f.isChecked();
    else if (t === 'PDFDropdown') values[n] = f.getSelected();
  });
  return values;
}
```

## pdf-parse Result Object

```js
{
  numpages: 5,        // total pages
  numrender: 5,       // pages rendered
  info: {             // PDF Info dictionary
    PDFFormatVersion: '1.5',
    IsAcroFormPresent: false,
    IsXFAPresent: false,
    Title: 'My Report',
    Author: 'Jane Doe',
    Creator: 'Microsoft Word',
    Producer: 'Mac OS X PDF',
    CreationDate: "D:20240115120000+00'00'",
    ModDate: "D:20240115120000+00'00'",
  },
  metadata: null,     // XMP metadata (may be null)
  version: '1.10.100',
  text: 'Full text...',
}
```

## Searching Text

```js
async function search(pdfPath, query) {
  const { text } = await require('pdf-parse')(require('fs').readFileSync(pdfPath));
  const lc = text.toLowerCase();
  const term = query.toLowerCase();
  const results = [];
  let pos = 0;
  while ((pos = lc.indexOf(term, pos)) !== -1) {
    results.push(text.slice(Math.max(0, pos - 80), pos + query.length + 80));
    pos++;
  }
  return results;
}
```

## Handling Scanned PDFs

Scanned PDFs contain images, not machine-readable text. Use OCR:

```bash
npm install tesseract.js
```

```js
const { createWorker } = require('tesseract.js');
const pdfjsLib = require('pdfjs-dist/legacy/build/pdf');

async function ocrPage(pdfPath, pageNum = 1) {
  const doc = await pdfjsLib.getDocument(pdfPath).promise;
  const page = await doc.getPage(pageNum);
  const viewport = page.getViewport({ scale: 2 });
  // Render to canvas, then pass to tesseract
  // ... (requires canvas package in Node)
  const worker = await createWorker('eng');
  const { data: { text } } = await worker.recognize(imageData);
  await worker.terminate();
  return text;
}
```

## Password-Protected PDFs

```js
const pdfParse = require('pdf-parse');
const { PDFDocument } = require('pdf-lib');

// pdf-parse
const data = await pdfParse(buffer, { password: 'secret123' });

// pdf-lib
const doc = await PDFDocument.load(bytes, { password: 'secret123' });
```

## Tips

- **pdf-parse** calls pdfjs internally — it's the simplest extraction API.
- For layout-aware extraction (columns, tables), use **pdfjs-dist** directly with coordinate data.
- `text` from pdf-parse may have poor whitespace — normalize with `.replace(/\s+/g, ' ')`.
- For tabular data in PDFs, consider **camelot** (Python) or **tabula** via subprocess.
- Always handle potential errors: some PDFs are encrypted, corrupt, or image-only.
