# Word Document Manipulation — SKILL.md

This document provides detailed, practical guidance for working with `.docx` files using the `docx` npm package.

## Setup

```bash
npm install docx
npm install mammoth   # for reading existing .docx files
```

## Creating Your First Document

```js
const { Document, Packer, Paragraph, TextRun } = require('docx');
const fs = require('fs');

async function main() {
  const doc = new Document({
    sections: [{
      children: [
        new Paragraph({
          children: [
            new TextRun({ text: 'Hello ', bold: true }),
            new TextRun({ text: 'World', italics: true }),
          ],
        }),
      ],
    }],
  });

  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync('hello.docx', buffer);
  console.log('Created hello.docx');
}
main();
```

## Paragraph Options

```js
new Paragraph({
  text: 'Simple text',               // shorthand for single TextRun
  heading: HeadingLevel.HEADING_1,  // built-in heading style
  alignment: AlignmentType.CENTER,  // text alignment
  pageBreakBefore: true,            // force new page before paragraph
  keepLines: true,                  // keep all lines on same page
  keepNext: true,                   // keep with next paragraph
  outlineLevel: 0,                  // outline hierarchy level (0=top)
  numbering: {                      // list numbering reference
    reference: 'my-list',
    level: 0,
  },
  indent: {
    left: 720,                      // indent in twips
    firstLine: 360,                 // first-line indent
  },
  spacing: {
    before: 200,                    // space before paragraph (twips)
    after: 200,                     // space after paragraph (twips)
    line: 360,                      // line spacing (240=single, 480=double)
    lineRule: LineRuleType.AUTO,
  },
  border: {
    top: { style: BorderStyle.SINGLE, size: 6, color: '000000', space: 1 },
  },
  shading: {
    type: ShadingType.SOLID,
    color: 'E7F3FF',
  },
})
```

## TextRun Options

```js
new TextRun({
  text: 'Content',
  bold: true,
  italics: true,
  underline: { type: UnderlineType.SINGLE },
  strike: true,
  color: '1F4E79',        // hex, no #
  size: 28,               // half-points (28 = 14pt)
  font: {
    name: 'Calibri',
    hint: 'default',
  },
  highlight: 'yellow',    // 'yellow', 'cyan', 'magenta', 'green', etc.
  allCaps: false,
  smallCaps: false,
  superScript: false,
  subScript: false,
  characterSpacing: 0,    // twips
  break: 1,               // number of line breaks to insert after
})
```

## Tables

```js
const { Table, TableRow, TableCell, WidthType } = require('docx');

new Table({
  width: { size: 9000, type: WidthType.DXA },
  rows: [
    new TableRow({
      children: [
        new TableCell({
          width: { size: 4500, type: WidthType.DXA },
          children: [new Paragraph({ text: 'Cell 1' })],
          margins: { top: 100, bottom: 100, left: 150, right: 150 },
        }),
        new TableCell({
          children: [new Paragraph({ text: 'Cell 2' })],
        }),
      ],
    }),
  ],
  borders: {
    top: { style: BorderStyle.SINGLE, size: 1, color: '000000' },
    bottom: { style: BorderStyle.SINGLE, size: 1, color: '000000' },
    left: { style: BorderStyle.SINGLE, size: 1, color: '000000' },
    right: { style: BorderStyle.SINGLE, size: 1, color: '000000' },
    insideHorizontal: { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC' },
    insideVertical: { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC' },
  },
})
```

## Images

```js
const { ImageRun } = require('docx');
const fs = require('fs');

// Basic inline image
new Paragraph({
  children: [
    new ImageRun({
      data: fs.readFileSync('photo.png'),
      transformation: { width: 300, height: 200 }, // pixels
    }),
  ],
})

// Floating image
new Paragraph({
  children: [
    new ImageRun({
      data: fs.readFileSync('logo.png'),
      transformation: { width: 100, height: 50 },
      floating: {
        horizontalPosition: {
          relative: HorizontalPositionRelativeFrom.MARGIN,
          align: HorizontalPositionAlign.RIGHT,
        },
        verticalPosition: {
          relative: VerticalPositionRelativeFrom.PARAGRAPH,
          offset: 0,
        },
        wrap: { type: TextWrappingType.SQUARE, side: TextWrappingSide.BOTH },
        margins: { top: 100, bottom: 100, left: 100, right: 100 },
      },
    }),
  ],
})
```

## Numbering / Lists

Define numbering at the Document level, reference in Paragraphs:

```js
const { LevelFormat, AlignmentType } = require('docx');

const doc = new Document({
  numbering: {
    config: [
      {
        reference: 'bullet-list',
        levels: [
          {
            level: 0,
            format: LevelFormat.BULLET,
            text: '\u2022',
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } },
          },
        ],
      },
      {
        reference: 'numbered-list',
        levels: [
          {
            level: 0,
            format: LevelFormat.DECIMAL,
            text: '%1.',
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } },
          },
          {
            level: 1,
            format: LevelFormat.LOWER_LETTER,
            text: '%2.',
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 1440, hanging: 360 } } },
          },
        ],
      },
    ],
  },
  sections: [{
    children: [
      new Paragraph({ text: 'Item A', numbering: { reference: 'bullet-list', level: 0 } }),
      new Paragraph({ text: 'Item B', numbering: { reference: 'bullet-list', level: 0 } }),
      new Paragraph({ text: 'Step 1', numbering: { reference: 'numbered-list', level: 0 } }),
      new Paragraph({ text: 'Sub-step a', numbering: { reference: 'numbered-list', level: 1 } }),
    ],
  }],
});
```

## Multiple Sections

```js
const doc = new Document({
  sections: [
    {
      properties: { page: { orientation: PageOrientation.PORTRAIT } },
      children: [new Paragraph({ text: 'Portrait section' })],
    },
    {
      properties: {
        type: SectionType.NEXT_PAGE,
        page: { orientation: PageOrientation.LANDSCAPE },
      },
      children: [new Paragraph({ text: 'Landscape section' })],
    },
  ],
});
```

## Reading Existing .docx (mammoth)

```js
const mammoth = require('mammoth');

// Extract text only
async function extractText(filePath) {
  const { value } = await mammoth.extractRawText({ path: filePath });
  return value;
}

// Convert to structured HTML
async function toHtml(filePath) {
  const { value, messages } = await mammoth.convertToHtml(
    { path: filePath },
    {
      styleMap: [
        "p[style-name='Heading 1'] => h1:fresh",
        "p[style-name='Heading 2'] => h2:fresh",
      ],
    }
  );
  messages.forEach((m) => console.warn(m));
  return value;
}

// Extract images
async function extractImages(filePath, outputDir) {
  await mammoth.convertToHtml(
    { path: filePath },
    {
      convertImage: mammoth.images.imgElement(async (image) => {
        const buffer = await image.read();
        const ext = image.contentType.split('/')[1];
        const name = `image_${Date.now()}.${ext}`;
        fs.writeFileSync(path.join(outputDir, name), buffer);
        return { src: name };
      }),
    }
  );
}
```

## Packing Options

```js
// Save to file
const buf = await Packer.toBuffer(doc);
fs.writeFileSync('output.docx', buf);

// Get base64 (e.g. for embedding in email)
const b64 = await Packer.toBase64String(doc);

// Stream to HTTP response
app.get('/download', (req, res) => {
  res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document');
  res.setHeader('Content-Disposition', 'attachment; filename=report.docx');
  Packer.toStream(doc).pipe(res);
});
```

## Best Practices

- **Units**: sizes in half-points, spacing/margins in twips (1440 twips = 1 inch).
- **Colors**: hex without `#` (e.g., `'1F4E79'` not `'#1F4E79'`).
- **Images**: always read as `fs.readFileSync()` `Buffer` before passing.
- **Lists**: define numbering once in `Document.numbering`, reuse by reference.
- **Performance**: for 100+ page documents, generate sections in chunks.
- **Fonts**: embedded fonts require the font to exist on the reader's machine; stick to `Calibri`, `Arial`, `Times New Roman` for portability.
