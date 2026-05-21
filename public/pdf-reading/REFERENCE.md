# PDF Reading API Reference

## pdf-parse

### Install & Import

```bash
npm install pdf-parse
```

```js
const pdfParse = require('pdf-parse');
```

### Function Signature

```js
pdfParse(dataBuffer, options?) → Promise<PDFData>
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `dataBuffer` | Buffer | Raw PDF file content |
| `options.pagerender` | Function | Custom per-page render callback |
| `options.max` | number | Max pages to parse (0 = all) |
| `options.version` | string | pdfjs-dist version string |
| `options.password` | string | Password for encrypted PDFs |

### PDFData Result

| Field | Type | Description |
|-------|------|-------------|
| `numpages` | number | Total page count |
| `numrender` | number | Pages actually rendered |
| `info` | object | PDF Info dictionary |
| `metadata` | object \| null | XMP metadata |
| `version` | string | pdf.js version used |
| `text` | string | Extracted text (all pages) |

---

## pdfjs-dist

### Install & Import

```bash
npm install pdfjs-dist
```

```js
const pdfjsLib = require('pdfjs-dist/legacy/build/pdf');
pdfjsLib.GlobalWorkerOptions.workerSrc = false;  // disable worker in Node
```

### Loading a Document

```js
const loadingTask = pdfjsLib.getDocument({
  url: 'file.pdf',        // or
  data: uint8ArrayBytes,  // or
  password: 'secret',
  verbosity: 0,           // 0 = silent
});
const pdf = await loadingTask.promise;
```

### PDFDocumentProxy Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `getPage(n)` | Promise<PDFPageProxy> | Get page 1-indexed |
| `getMetadata()` | Promise<{info, metadata}> | Document metadata |
| `getOutline()` | Promise<any[]> | Bookmarks/outline |
| `getAttachments()` | Promise<object> | File attachments |
| `getAnnotations()` | Promise<any[]> | (deprecated use page.getAnnotations) |
| `numPages` | number | Total page count |
| `fingerprint` | string | Unique document ID |
| `destroy()` | void | Release resources |

### PDFPageProxy Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `getTextContent(opts?)` | Promise<TextContent> | Text items with positions |
| `getAnnotations(opts?)` | Promise<any[]> | Page annotations |
| `getViewport(opts)` | PageViewport | Rendering viewport |
| `getOperatorList()` | Promise<PDFOperatorList> | Low-level operators |
| `pageNumber` | number | 1-indexed page number |
| `rotate` | number | Page rotation (0/90/180/270) |
| `view` | number[] | `[x1, y1, x2, y2]` media box |

### TextContent Object

```js
{
  items: [
    {
      str: 'Hello World',
      dir: 'ltr',
      transform: [sx, shy, shx, sy, tx, ty],  // 2D matrix
      width: 55.2,
      height: 11.0,
      fontName: 'g_d0_f1',
      hasEOL: false,
    },
    // ...
  ],
  styles: {
    'g_d0_f1': {
      fontFamily: 'sans-serif',
      ascent: 0.9,
      descent: -0.2,
      vertical: false,
    },
  },
}
```

Position from transform matrix: `x = transform[4]`, `y = transform[5]`

---

## pdf-lib (Reading Side)

### Loading

```js
const { PDFDocument } = require('pdf-lib');
const pdfDoc = await PDFDocument.load(bytes, {
  password: 'optional',
  ignoreEncryption: false,
  parseSpeed: ParseSpeeds.Fastest,
  throwOnInvalidObject: false,
});
```

### ParseSpeeds

```js
const { ParseSpeeds } = require('pdf-lib');
ParseSpeeds.Fastest   // 1500
ParseSpeeds.Fast      // 5000
ParseSpeeds.Medium    // 25000
ParseSpeeds.Slow      // Infinity
```

### Metadata Getters

```js
pdfDoc.getTitle()           // → string | undefined
pdfDoc.getAuthor()
pdfDoc.getSubject()
pdfDoc.getKeywords()        // → string[] | undefined
pdfDoc.getProducer()
pdfDoc.getCreator()
pdfDoc.getCreationDate()    // → Date | undefined
pdfDoc.getModificationDate()
pdfDoc.getPageCount()       // → number
pdfDoc.getPageIndices()     // → number[]
```

### Form Reading

```js
const form = pdfDoc.getForm();
form.getFields()                     // → PDFField[]
form.getField('fieldName')           // → PDFField (throws if not found)
form.getTextField('name')            // → PDFTextField
form.getCheckBox('agree')            // → PDFCheckBox
form.getDropdown('country')          // → PDFDropdown
form.getRadioGroup('gender')         // → PDFRadioGroup
form.getOptionList('tags')           // → PDFOptionList
form.getSignature('sig1')            // → PDFSignature
form.fieldExists('fieldName')        // → boolean (pdf-lib >= 1.16)
```

### PDFField Base

```js
field.getName()              // field name string
field.getFullyQualifiedName() // dotted hierarchy name
field.acroField              // raw AcroForm field object
field.doc                    // owning PDFDocument
```
