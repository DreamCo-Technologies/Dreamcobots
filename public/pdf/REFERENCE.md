# PDF Libraries API Reference

## PDFKit API Reference

### PDFDocument Constructor Options

```js
new PDFDocument({
  size: 'A4',             // string or [width, height] in points
  layout: 'portrait',     // 'portrait' | 'landscape'
  margin: 72,             // uniform margin (points)
  margins: { top, bottom, left, right },
  bufferPages: false,     // keep all pages in memory
  autoFirstPage: true,    // create page on instantiation
  compress: true,         // compress content streams
  userPassword: null,     // encrypt document
  ownerPassword: null,
  permissions: {
    printing: 'highResolution',   // 'lowResolution' | 'highResolution' | false
    modifying: false,
    copying: false,
    annotating: true,
    fillingForms: true,
    contentAccessibility: true,
    documentAssembly: false,
  },
  pdfVersion: '1.3',      // PDF version string
  info: {
    Title: '',
    Author: '',
    Subject: '',
    Keywords: '',
    CreationDate: new Date(),
    ModDate: new Date(),
  },
})
```

### Text Methods

| Method | Description |
|--------|-------------|
| `doc.text(str, [x, y], [opts])` | Add text at position |
| `doc.fontSize(n)` | Set font size |
| `doc.font(name)` | Set font |
| `doc.fillColor(color)` | Set text/fill color |
| `doc.strokeColor(color)` | Set stroke color |
| `doc.moveDown([n])` | Move cursor down n lines |
| `doc.moveUp([n])` | Move cursor up n lines |
| `doc.currentLineHeight([incGap])` | Get current line height |
| `doc.widthOfString(str)` | Measure text width |
| `doc.heightOfString(str, [opts])` | Measure text height |

### Text Options Object

```js
{
  lineBreak: true,        // wrap text
  width: 400,             // wrap width
  height: 200,            // clipping height
  align: 'left',
  lineGap: 0,
  paragraphGap: 0,
  indent: 0,
  wordSpacing: 0,
  characterSpacing: 0,
  fill: true,
  stroke: false,
  link: null,             // URL string
  goTo: null,             // page number
  underline: false,
  strike: false,
  oblique: false,
  baseline: 'alphabetic',
  continued: false,
  columns: 0,
  columnGap: 18,
  ellipsis: false,        // truncate overflow
}
```

### Graphics Methods

| Method | Description |
|--------|-------------|
| `doc.rect(x, y, w, h)` | Rectangle path |
| `doc.roundedRect(x, y, w, h, r)` | Rounded rect |
| `doc.ellipse(cx, cy, rx, [ry])` | Ellipse |
| `doc.circle(cx, cy, r)` | Circle |
| `doc.polygon(...pts)` | Polygon |
| `doc.path(d)` | SVG path string |
| `doc.moveTo(x, y)` | Move path cursor |
| `doc.lineTo(x, y)` | Line to point |
| `doc.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, x, y)` | Cubic Bézier |
| `doc.quadraticCurveTo(cpx, cpy, x, y)` | Quadratic Bézier |
| `doc.closePath()` | Close current path |
| `doc.stroke()` | Stroke path |
| `doc.fill([rule])` | Fill path |
| `doc.fillAndStroke([fillColor], [strokeColor])` | Fill + stroke |
| `doc.clip()` | Set clip region |
| `doc.save()` | Save graphics state |
| `doc.restore()` | Restore graphics state |
| `doc.rotate(deg, [opts])` | Rotate transform |
| `doc.scale(x, [y], [opts])` | Scale transform |
| `doc.translate(x, y)` | Translate transform |

### Line / Stroke Options

```js
doc.lineWidth(2);
doc.lineCap('butt');    // 'butt' | 'round' | 'square'
doc.lineJoin('miter');  // 'miter' | 'round' | 'bevel'
doc.miterLimit(10);
doc.dash(4, { space: 2, phase: 0 });
doc.undash();
doc.opacity(0.5);       // sets both fillOpacity and strokeOpacity
doc.fillOpacity(0.8);
doc.strokeOpacity(0.5);
```

### Image Methods

```js
doc.image(src, [x, y], opts)

// opts:
{
  width: 200,
  height: 150,
  fit: [200, 150],      // fit within box
  cover: [200, 150],    // cover box (crop)
  align: 'center',      // 'left' | 'center' | 'right'
  valign: 'center',     // 'top' | 'center' | 'bottom'
  link: 'https://...',
  goTo: 2,
}
```

Supported formats: **JPEG**, **PNG**

### Page Methods

```js
doc.addPage([opts])
doc.switchToPage(n)         // requires bufferPages: true
doc.bufferedPageRange()     // { start, count }
doc.flushPages()
doc.page.width              // current page width
doc.page.height
doc.page.margins            // { top, left, bottom, right }
```

---

## pdf-lib API Reference

### PDFDocument Static Methods

```js
PDFDocument.create()              // new empty document
PDFDocument.load(bytes, opts?)    // load existing PDF
```

### PDFDocument Instance Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `getPages()` | PDFPage[] | All pages |
| `getPageCount()` | number | Page count |
| `getPage(index)` | PDFPage | Page at index |
| `addPage([size])` | PDFPage | Append blank page |
| `insertPage(index, [size])` | PDFPage | Insert blank page |
| `removePage(index)` | void | Remove a page |
| `copyPages(src, indices)` | Promise<PDFPage[]> | Copy pages from another doc |
| `embedFont(fontData)` | Promise<PDFFont> | Embed font |
| `embedStandardFont(font)` | PDFFont | Embed standard font |
| `embedPng(data)` | Promise<PDFImage> | Embed PNG |
| `embedJpg(data)` | Promise<PDFImage> | Embed JPEG |
| `embedPdf(data, indices?)` | Promise<PDFEmbeddedPage[]> | Embed PDF pages |
| `getForm()` | PDFForm | Access AcroForm |
| `save(opts?)` | Promise<Uint8Array> | Serialize to bytes |
| `saveAsBase64(opts?)` | Promise<string> | Serialize as base64 |
| `setTitle(str)` | void | Set title metadata |
| `setAuthor(str)` | void |  |
| `setSubject(str)` | void |  |
| `setKeywords(arr)` | void |  |
| `setProducer(str)` | void |  |
| `setCreator(str)` | void |  |
| `setCreationDate(date)` | void |  |
| `setModificationDate(date)` | void |  |

### PDFPage Methods

| Method | Description |
|--------|-------------|
| `getSize()` | `{ width, height }` in points |
| `getWidth()` | Page width |
| `getHeight()` | Page height |
| `setSize(w, h)` | Resize page |
| `setRotation(deg)` | Rotate page |
| `drawText(str, opts)` | Draw text |
| `drawRectangle(opts)` | Draw rectangle |
| `drawSquare(opts)` | Draw square |
| `drawEllipse(opts)` | Draw ellipse |
| `drawCircle(opts)` | Draw circle |
| `drawLine(opts)` | Draw line |
| `drawImage(img, opts)` | Draw image |
| `drawPage(page, opts)` | Draw embedded page |
| `pushOperators(...ops)` | Raw PDF operators |

### PDFPage drawText Options

```js
page.drawText('Hello', {
  x: 50, y: 700,
  size: 12,
  font: embeddedFont,
  color: rgb(0, 0, 0),
  opacity: 1,
  rotate: degrees(0),
  xSkewAngle: degrees(0),
  ySkewAngle: degrees(0),
  lineHeight: 14,
  maxWidth: 400,
  wordBreaks: [' '],
})
```

### PDFPage drawRectangle Options

```js
page.drawRectangle({
  x: 50, y: 100,
  width: 200, height: 80,
  color: rgb(0.87, 0.93, 0.95),
  borderColor: rgb(0.12, 0.31, 0.47),
  borderWidth: 2,
  borderDashArray: [5, 3],
  opacity: 1,
  borderOpacity: 1,
  rotate: degrees(0),
})
```

### PDFImage Methods

```js
const img = await pdfDoc.embedPng(pngBytes);
img.width          // native width
img.height         // native height
img.scale(factor)  // returns { width, height }
img.size()         // same as scale(1)
```

### Color Helpers

```js
const { rgb, cmyk, grayscale } = require('pdf-lib');
rgb(r, g, b)               // all 0–1
cmyk(c, m, y, k)           // all 0–1
grayscale(g)               // 0–1
```

### Standard Page Sizes

```js
const { PageSizes } = require('pdf-lib');
PageSizes.A0   // [2383.94, 3370.39]
PageSizes.A1
PageSizes.A2
PageSizes.A3
PageSizes.A4   // [595.28, 841.89]
PageSizes.A5
PageSizes.Letter  // [612, 792]
PageSizes.Legal   // [612, 1008]
PageSizes.Tabloid // [792, 1224]
```

### StandardFonts Enum

```js
const { StandardFonts } = require('pdf-lib');
StandardFonts.Courier
StandardFonts.CourierBold
StandardFonts.CourierBoldOblique
StandardFonts.CourierOblique
StandardFonts.Helvetica
StandardFonts.HelveticaBold
StandardFonts.HelveticaBoldOblique
StandardFonts.HelveticaOblique
StandardFonts.Symbol
StandardFonts.TimesRoman
StandardFonts.TimesBold
StandardFonts.TimesBoldItalic
StandardFonts.TimesItalic
StandardFonts.ZapfDingbats
```
