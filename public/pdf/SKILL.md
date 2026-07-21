# PDF Creation & Manipulation — SKILL.md

## Libraries

- **PDFKit** — create PDFs from scratch with a streaming API
- **pdf-lib** — load and modify existing PDFs, fill forms, merge documents

## Setup

```bash
npm install pdfkit pdf-lib
npm install @pdf-lib/fontkit  # for custom fonts in pdf-lib
```

## PDFKit Cheatsheet

```js
const PDFDocument = require('pdfkit');
const fs = require('fs');

const doc = new PDFDocument({ size: 'A4', margin: 50 });
doc.pipe(fs.createWriteStream('out.pdf'));

// Text
doc.font('Helvetica-Bold').fontSize(24).fillColor('#1F4E79').text('Title', { align: 'center' });
doc.moveDown();
doc.font('Helvetica').fontSize(12).fillColor('black').text('Body text here.');

// Shape
doc.rect(50, 200, 495, 2).fill('#1F4E79');

// Image
doc.image('photo.png', 50, 220, { width: 200 });

// New page
doc.addPage();

doc.end();
```

## pdf-lib Cheatsheet

```js
const { PDFDocument, rgb, StandardFonts } = require('pdf-lib');
const fs = require('fs');

async function run() {
  const pdfDoc = await PDFDocument.load(fs.readFileSync('input.pdf'));
  const font = await pdfDoc.embedFont(StandardFonts.Helvetica);
  const page = pdfDoc.getPages()[0];

  page.drawText('Annotation', {
    x: 50, y: 50, size: 12, font, color: rgb(1, 0, 0),
  });

  fs.writeFileSync('output.pdf', await pdfDoc.save());
}
run();
```

## PDFKit Text Options

```js
doc.text('Content', {
  align: 'justify',     // 'left' | 'right' | 'center' | 'justify'
  width: 400,
  lineGap: 4,
  paragraphGap: 10,
  indent: 20,
  columns: 2,
  link: 'https://example.com',
  underline: true,
  strike: false,
  continued: true,      // inline, no newline after
});
```

## PDFKit Built-in Fonts

`Helvetica`, `Helvetica-Bold`, `Helvetica-Oblique`, `Helvetica-BoldOblique`,
`Times-Roman`, `Times-Bold`, `Times-Italic`, `Times-BoldItalic`,
`Courier`, `Courier-Bold`, `Symbol`, `ZapfDingbats`

## Page Sizes (points)

| Size | W × H |
|------|-------|
| A4 | 595 × 842 |
| Letter | 612 × 792 |
| Legal | 612 × 1008 |
| A3 | 842 × 1190 |
| A5 | 420 × 595 |

1 inch = 72 points.

## pdf-lib Standard Fonts

```js
StandardFonts.Helvetica
StandardFonts.HelveticaBold
StandardFonts.TimesRoman
StandardFonts.TimesBold
StandardFonts.Courier
StandardFonts.CourierBold
```

## pdf-lib Color Helpers

```js
const { rgb, cmyk, grayscale } = require('pdf-lib');
rgb(0.12, 0.31, 0.47)     // (r, g, b) all 0–1
cmyk(0, 0.5, 0, 0.2)
grayscale(0.5)
```

## Merging PDFs

```js
const { PDFDocument } = require('pdf-lib');

async function merge(inputPaths, outputPath) {
  const out = await PDFDocument.create();
  for (const p of inputPaths) {
    const src = await PDFDocument.load(require('fs').readFileSync(p));
    const pages = await out.copyPages(src, src.getPageIndices());
    pages.forEach((pg) => out.addPage(pg));
  }
  require('fs').writeFileSync(outputPath, await out.save());
}
```

## Headers & Footers (PDFKit)

```js
const doc = new PDFDocument({ bufferPages: true });
// ... content ...
const n = doc.bufferedPageRange().count;
for (let i = 0; i < n; i++) {
  doc.switchToPage(i);
  doc.fontSize(8).fillColor('#888').text(`Page ${i+1} of ${n}`, 50, doc.page.height - 25, { align: 'center', width: doc.page.width - 100 });
}
doc.flushPages();
doc.end();
```

## Tips

- PDFKit uses **points** (72 pt = 1 inch); position (0,0) = top-left.
- pdf-lib origin (0,0) = **bottom-left** of page.
- Always call `doc.end()` to flush the stream in PDFKit.
- Use `bufferPages: true` + `doc.switchToPage()` for page numbers in PDFKit.
- pdf-lib can embed PNG and JPEG images natively; for other formats convert first.
