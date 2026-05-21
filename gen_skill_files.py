import os

BASE = "/home/runner/work/Dreamcobots/Dreamcobots/public"

# ===== docx.skill =====
docx_content = """
## Complete docx npm Package API Reference

### Installation
```bash
npm install docx
# or
yarn add docx
```

### Document Constructor
```javascript
const { Document, Packer } = require("docx");

const doc = new Document({
  creator: "Your App",
  description: "Document description",
  title: "Document Title",
  subject: "Subject",
  keywords: "keyword1, keyword2",
  lastModifiedBy: "Author Name",
  revision: 1,
  styles: { ... },       // Custom styles object
  numbering: { ... },    // Numbering config
  background: { color: "FFFFFF" },
  sections: [{ children: [] }],
  features: { updateFields: true },
});
```

### Paragraph Constructor - ALL Parameters
```javascript
const { Paragraph, TextRun, AlignmentType, HeadingLevel } = require("docx");

const para = new Paragraph({
  text: "Simple paragraph text",
  heading: HeadingLevel.HEADING_1,    // H1-H6 or TITLE
  alignment: AlignmentType.CENTER,    // LEFT, CENTER, RIGHT, JUSTIFIED, DISTRIBUTE
  indent: {
    left: 720,         // twips (1 inch = 1440 twips)
    right: 720,
    firstLine: 360,
    hanging: 360,
  },
  spacing: {
    before: 200,       // pt * 20
    after: 200,
    line: 276,         // line spacing in twips
    lineRule: "auto",  // "auto" | "exact" | "atLeast"
  },
  border: {
    top:    { color: "FF0000", space: 4, style: "single", size: 6 },
    bottom: { color: "FF0000", space: 4, style: "single", size: 6 },
    left:   { color: "FF0000", space: 4, style: "single", size: 6 },
    right:  { color: "FF0000", space: 4, style: "single", size: 6 },
  },
  shading: { type: ShadingType.CLEAR, fill: "FFFF00" },
  numbering: { reference: "my-numbering", level: 0 },
  pageBreakBefore: true,
  keepLines: true,
  keepNext: true,
  outlineLevel: 1,
  run: {               // default run properties
    font: "Calibri",
    size: 24,
    bold: false,
  },
  children: [          // array of TextRun, ImageRun, etc.
    new TextRun("Hello"),
  ],
  bidirectional: false,
  style: "Normal",    // named paragraph style
  bullet: { level: 0 },
  tabStops: [
    { type: TabStopType.LEFT, position: 2268 },
    { type: TabStopType.RIGHT, position: 9026 },
  ],
  contextualSpacing: true,
  wordWrap: true,
  scale: 100,
  suppressLineNumbers: false,
  suppressAutoHyphens: false,
  frame: { width: 2000, height: 1000, anchor: "text" },
  snapToGrid: true,
  links: [],
});
```

### TextRun Constructor - ALL Parameters
```javascript
const { TextRun, UnderlineType } = require("docx");

const run = new TextRun({
  text: "Sample text",
  bold: true,
  italics: true,
  underline: { type: UnderlineType.SINGLE, color: "FF0000" },
  // UnderlineType: SINGLE, DOUBLE, THICK, DOTTED, DASH, DOT_DASH, DOT_DOT_DASH, WAVE, WORDS
  strike: false,
  doubleStrike: false,
  subScript: false,
  superScript: false,
  smallCaps: false,
  allCaps: false,
  font: { name: "Arial", hint: "default" },
  size: 24,           // half-points (24 = 12pt)
  sizeComplexScript: 24,
  color: "000000",    // hex color without #
  highlight: "yellow", // yellow, green, cyan, magenta, blue, red, darkBlue, darkCyan, darkGreen, darkMagenta, darkRed, darkYellow, darkGray, lightGray, none
  shading: { type: ShadingType.CLEAR, fill: "FFFF00" },
  rtl: false,
  language: { value: "en-US" },
  style: "emphasis",  // named character style
  characterSpacing: 100, // twips
  positionalTab: { alignment: "center", relativeTo: "margin", leader: "none" },
  revision: { id: 1, author: "John", date: "2024-01-01T00:00:00Z" },
  border: { color: "auto", space: 1, style: "single", size: 6 },
  vanish: false,
  specVanish: false,
  emboss: false,
  imprint: false,
  noProof: false,
  snapToGrid: true,
  break: BreakType.PAGE,  // PAGE | COLUMN | TEXT_WRAPPING
});
```

### Table Constructor - ALL Parameters
```javascript
const { Table, TableRow, TableCell, WidthType, BorderStyle } = require("docx");

const table = new Table({
  rows: [
    new TableRow({
      children: [
        new TableCell({
          children: [new Paragraph("Cell 1")],
          width: { size: 3000, type: WidthType.DXA },
          columnSpan: 2,
          rowSpan: 1,
          shading: { fill: "E6E6E6", type: ShadingType.CLEAR },
          borders: {
            top:    { style: BorderStyle.SINGLE, size: 3, color: "000000" },
            bottom: { style: BorderStyle.SINGLE, size: 3, color: "000000" },
            left:   { style: BorderStyle.SINGLE, size: 3, color: "000000" },
            right:  { style: BorderStyle.SINGLE, size: 3, color: "000000" },
          },
          margins: { top: 100, bottom: 100, left: 100, right: 100 },
          verticalAlign: VerticalAlign.CENTER, // TOP | CENTER | BOTTOM
          textDirection: TextDirection.LEFT_TO_RIGHT_TOP_TO_BOTTOM,
        }),
      ],
      cantSplit: false,
      tableHeader: false,
      height: { value: 300, rule: HeightRule.EXACT },
    }),
  ],
  width: { size: 100, type: WidthType.PERCENTAGE },
  indent: { size: 720, type: WidthType.DXA },
  float: {
    horizontalAnchor: TableAnchorType.TEXT,
    verticalAnchor: TableAnchorType.TEXT,
    relativeHorizontalPosition: RelativeHorizontalPosition.RIGHT,
    relativeVerticalPosition: RelativeVerticalPosition.BOTTOM,
    leftFromText: 180,
    rightFromText: 180,
    topFromText: 180,
    bottomFromText: 180,
  },
  layout: TableLayoutType.FIXED,
  style: "TableGrid",
  borders: {
    top:           { style: BorderStyle.SINGLE, size: 3, color: "auto" },
    bottom:        { style: BorderStyle.SINGLE, size: 3, color: "auto" },
    left:          { style: BorderStyle.SINGLE, size: 3, color: "auto" },
    right:         { style: BorderStyle.SINGLE, size: 3, color: "auto" },
    insideHorizontal: { style: BorderStyle.SINGLE, size: 3, color: "auto" },
    insideVertical:   { style: BorderStyle.SINGLE, size: 3, color: "auto" },
  },
  margins: { top: 100, bottom: 100, left: 100, right: 100 },
  columnWidths: [1500, 1500, 1500, 1500],
  visuallyRightToLeft: false,
});
```

### ImageRun - ALL Parameters
```javascript
const { ImageRun } = require("docx");
const fs = require("fs");

const image = new ImageRun({
  data: fs.readFileSync("image.png"),  // Buffer
  transformation: {
    width: 200,         // pixels
    height: 150,
    rotation: 0,        // degrees
    flip: { horizontal: false, vertical: false },
  },
  type: "png",          // png | jpg | gif | bmp | svg
  altText: { title: "Alt text", description: "Description" },
  floating: {
    horizontalPosition: {
      offset: 1014400,  // EMUs (914400 EMU = 1 inch)
      relative: HorizontalPositionRelativeFrom.PAGE,
      align: HorizontalPositionAlign.LEFT,
    },
    verticalPosition: {
      offset: 1014400,
      relative: VerticalPositionRelativeFrom.PAGE,
      align: VerticalPositionAlign.TOP,
    },
    wrap: { type: TextWrappingType.SQUARE, side: TextWrappingSide.BOTH_SIDES },
    lockAnchor: false,
    allowOverlap: true,
    behindDocument: false,
    layoutInCell: true,
    margins: { top: 72000, bottom: 72000, left: 72000, right: 72000 },
  },
});
```

### Header and Footer
```javascript
const { Header, Footer, PageNumber, NumberFormat } = require("docx");

const header = new Header({
  children: [
    new Paragraph({
      children: [
        new TextRun("Company Name  "),
        new TextRun({ children: [PageNumber.CURRENT] }),
        new TextRun(" of "),
        new TextRun({ children: [PageNumber.TOTAL_PAGES] }),
      ],
      border: { bottom: { style: BorderStyle.SINGLE, size: 6 } },
    }),
  ],
});

const footer = new Footer({
  children: [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [
        new TextRun("Confidential - Page "),
        new TextRun({ children: [PageNumber.CURRENT] }),
      ],
    }),
  ],
});

// In document sections:
const section = {
  headers: {
    default: header,
    first: new Header({ children: [new Paragraph("First Page Header")] }),
    even: new Header({ children: [new Paragraph("Even Page Header")] }),
  },
  footers: {
    default: footer,
    first: new Footer({ children: [new Paragraph("First Page Footer")] }),
  },
  properties: {
    titlePage: true,
    evenAndOddHeaderAndFooters: true,
  },
  children: [],
};
```

### Hyperlink
```javascript
const { ExternalHyperlink, InternalHyperlink, Bookmark } = require("docx");

// External link
const extLink = new ExternalHyperlink({
  link: "https://example.com",
  children: [
    new TextRun({
      text: "Click here",
      style: "Hyperlink",
      color: "0000EE",
      underline: { type: UnderlineType.SINGLE },
    }),
  ],
});

// Internal bookmark link
const intLink = new InternalHyperlink({
  anchor: "chapter-1",  // matches bookmark id
  children: [new TextRun("Go to Chapter 1")],
});

// Bookmark definition
const bookmark = new Bookmark({
  id: "chapter-1",
  children: [new TextRun("Chapter 1")],
});
```

### Section Properties - ALL Options
```javascript
const { SectionType, PageOrientation, PageBreakType } = require("docx");

const sectionProps = {
  type: SectionType.NEXT_PAGE,  // CONTINUOUS | NEXT_PAGE | ODD_PAGE | EVEN_PAGE | NEXT_COLUMN
  page: {
    size: {
      orientation: PageOrientation.LANDSCAPE,  // PORTRAIT | LANDSCAPE
      width: 15840,   // twips (8.5 inches * 1440)
      height: 12240,  // twips (11 inches * 1440)
    },
    margin: {
      top: 1440,      // 1 inch
      right: 1440,
      bottom: 1440,
      left: 1440,
      header: 720,
      footer: 720,
      gutter: 0,
    },
    pageNumbers: {
      start: 1,
      formatType: NumberFormat.DECIMAL,  // BULLET | DECIMAL | LOWER_LETTER | etc.
    },
  },
  column: {
    count: 2,
    space: 720,
    separate: true,
  },
  lineNumbers: {
    countBy: 1,
    restart: LineNumberRestartFormat.NEW_PAGE,
    distance: 720,
  },
  verticalAlign: VerticalAlignSection.TOP,
};
```

### Numbering (Lists)
```javascript
const { LevelFormat, LevelSuffix, AlignmentType } = require("docx");

const numbering = {
  config: [
    {
      reference: "my-bullet-list",
      levels: [
        {
          level: 0,
          format: LevelFormat.BULLET,
          text: "\u2022",
          alignment: AlignmentType.LEFT,
          style: {
            paragraph: { indent: { left: 720, hanging: 360 } },
            run: { font: "Symbol" },
          },
        },
        {
          level: 1,
          format: LevelFormat.BULLET,
          text: "\u25E6",
          alignment: AlignmentType.LEFT,
          style: {
            paragraph: { indent: { left: 1440, hanging: 360 } },
          },
        },
      ],
    },
    {
      reference: "my-numbered-list",
      levels: [
        {
          level: 0,
          format: LevelFormat.DECIMAL,
          text: "%1.",
          alignment: AlignmentType.LEFT,
          style: {
            paragraph: { indent: { left: 720, hanging: 360 } },
          },
        },
        {
          level: 1,
          format: LevelFormat.LOWER_LETTER,
          text: "%2)",
          alignment: AlignmentType.LEFT,
          style: {
            paragraph: { indent: { left: 1440, hanging: 360 } },
          },
        },
      ],
    },
  ],
};
```

### Custom Styles
```javascript
const styles = {
  default: {
    heading1: {
      run: { size: 56, bold: true, color: "2E74B5", font: "Calibri" },
      paragraph: { spacing: { before: 240, after: 60 } },
    },
    heading2: {
      run: { size: 36, bold: true, color: "2E74B5", font: "Calibri" },
      paragraph: { spacing: { before: 240, after: 60 } },
    },
  },
  paragraphStyles: [
    {
      id: "CustomStyle1",
      name: "Custom Style 1",
      basedOn: "Normal",
      next: "Normal",
      run: { font: "Arial", size: 24, color: "333333" },
      paragraph: { spacing: { before: 120, after: 120 } },
    },
  ],
  characterStyles: [
    {
      id: "CodeChar",
      name: "Code Char",
      basedOn: "DefaultParagraphFont",
      run: { font: "Courier New", size: 20, color: "C7254E" },
    },
  ],
};
```

### Tracked Changes API
```javascript
const {
  InsertedRun,
  DeletedRun,
  InsertedTextRun,
  DeletedTextRun,
} = require("docx");

// Insert tracked change
const inserted = new InsertedRun({
  id: 1,
  author: "John Doe",
  date: "2024-01-15T10:30:00Z",
  children: [new TextRun("This text was inserted")],
});

// Delete tracked change
const deleted = new DeletedRun({
  id: 2,
  author: "Jane Smith",
  date: "2024-01-15T11:00:00Z",
  children: [new DeletedTextRun({ text: "This text was deleted" })],
});
```

### Watermark Implementation
```javascript
const { Header, Paragraph, TextRun, AlignmentType } = require("docx");

function createWatermark(text = "DRAFT") {
  return new Header({
    children: [
      new Paragraph({
        children: [
          new TextRun({
            text,
            bold: true,
            size: 160,
            color: "D3D3D3",
            // Rotate text using the run properties
          }),
        ],
        alignment: AlignmentType.CENTER,
        frame: {
          position: { x: 3000, y: 3800 },
          width: 6000,
          height: 1000,
          anchor: { horizontal: "page", vertical: "page" },
          allowOverlap: "1",
        },
      }),
    ],
  });
}
```

### Page Numbering - All Formats
```javascript
const { NumberFormat } = require("docx");

// NumberFormat values:
// BULLET, CARDINAL_TEXT, CHICAGO, DECIMAL, DECIMAL_ENCLOSED_CIRCLE,
// DECIMAL_ENCLOSED_FULLSTOP, DECIMAL_ENCLOSED_PARENTHESES, DECIMAL_FULL_WIDTH,
// DECIMAL_FULL_WIDTH_2, DECIMAL_ZERO, GANADA, HEX, HEBREW_1, HEBREW_2,
// HEX_UPPER, HINDI_CONSONANTS, HINDI_COUNTING, HINDI_NUMBERS, HINDI_VOWELS,
// IDEOGRAPH_DIGITAL, IDEOGRAPH_ENCLOSED_CIRCLE, IDEOGRAPH_LEGAL_TRADITIONAL,
// IDEOGRAPH_TRADITIONAL, IDEOGRAPH_ZODIAC, IDEOGRAPH_ZODIAC_TRADITIONAL,
// IROHA, IROHA_FULL_WIDTH, JAPANESE_COUNTING, JAPANESE_DIGITAL_TEN_THOUSAND,
// JAPANESE_LEGAL, KOREAN_COUNTING, KOREAN_DIGITAL, KOREAN_DIGITAL_2,
// KOREAN_LEGAL, LOWER_LETTER, LOWER_ROMAN, NONE, NUMBER_IN_DASH, ORDINAL,
// ORDINAL_TEXT, RUSSIAN_LOWER, RUSSIAN_UPPER, TAIWANESE_COUNTING,
// TAIWANESE_COUNTING_THOUSAND, TAIWANESE_DIGITAL, THAI_COUNTING, THAI_LETTERS,
// THAI_NUMBERS, UPPER_LETTER, UPPER_ROMAN, VIETNAMESE_COUNTING
```

### Complete Working Example 1: Business Report
```javascript
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, HeadingLevel, AlignmentType, BorderStyle,
  WidthType, PageNumber, UnderlineType,
} = require("docx");
const fs = require("fs");

async function createBusinessReport(data) {
  const doc = new Document({
    creator: data.author,
    title: data.title,
    description: data.description,
    styles: {
      paragraphStyles: [
        {
          id: "ReportTitle",
          name: "Report Title",
          basedOn: "Title",
          run: { size: 72, bold: true, color: "1F3864", font: "Calibri" },
          paragraph: { alignment: AlignmentType.CENTER, spacing: { after: 240 } },
        },
      ],
    },
    sections: [
      {
        headers: {
          default: new Header({
            children: [
              new Paragraph({
                children: [
                  new TextRun({ text: data.companyName, bold: true }),
                  new TextRun("  |  "),
                  new TextRun(data.title),
                ],
                alignment: AlignmentType.RIGHT,
              }),
            ],
          }),
        },
        footers: {
          default: new Footer({
            children: [
              new Paragraph({
                children: [
                  new TextRun("Page "),
                  new TextRun({ children: [PageNumber.CURRENT] }),
                  new TextRun(" of "),
                  new TextRun({ children: [PageNumber.TOTAL_PAGES] }),
                ],
                alignment: AlignmentType.CENTER,
              }),
            ],
          }),
        },
        children: [
          new Paragraph({ text: data.title, style: "ReportTitle" }),
          new Paragraph({
            text: `Prepared by: ${data.author}  |  Date: ${data.date}`,
            alignment: AlignmentType.CENTER,
            spacing: { after: 480 },
          }),
          new Paragraph({ text: "Executive Summary", heading: HeadingLevel.HEADING_1 }),
          new Paragraph({ text: data.executiveSummary }),
          new Paragraph({ text: "Key Findings", heading: HeadingLevel.HEADING_1 }),
          ...data.findings.map((f) =>
            new Paragraph({ text: `• ${f}`, indent: { left: 720 } })
          ),
          new Paragraph({ text: "Data Analysis", heading: HeadingLevel.HEADING_1 }),
          createDataTable(data.tableData),
          new Paragraph({ text: "Recommendations", heading: HeadingLevel.HEADING_1 }),
          ...data.recommendations.map((r, i) =>
            new Paragraph({ text: `${i + 1}. ${r}` })
          ),
          new Paragraph({ text: "Conclusion", heading: HeadingLevel.HEADING_1 }),
          new Paragraph({ text: data.conclusion }),
        ],
      },
    ],
  });

  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(`${data.filename}.docx`, buffer);
  return buffer;
}
```

### Complete Working Example 2: Mail Merge Letter
```javascript
async function createMailMergeLetter(template, recipients) {
  const results = [];
  for (const recipient of recipients) {
    const doc = new Document({
      sections: [{
        children: [
          new Paragraph({
            children: [new TextRun({ text: new Date().toLocaleDateString(), italics: true })],
            alignment: AlignmentType.RIGHT,
            spacing: { after: 480 },
          }),
          new Paragraph(`${recipient.salutation} ${recipient.lastName},`),
          new Paragraph({ spacing: { before: 240 } }),
          new Paragraph(
            template.body.replace(/\{\{(\w+)\}\}/g, (_, k) => recipient[k] || "")
          ),
          new Paragraph({ spacing: { before: 240 } }),
          new Paragraph("Sincerely,"),
          new Paragraph({ spacing: { before: 480 } }),
          new Paragraph({ text: template.senderName, bold: true }),
          new Paragraph(template.senderTitle),
          new Paragraph(template.companyName),
        ],
      }],
    });
    const buffer = await Packer.toBuffer(doc);
    results.push({ recipient, buffer });
  }
  return results;
}
```

### Complete Working Example 3: Invoice Generator
```javascript
function createInvoice(invoiceData) {
  const headerRow = new TableRow({
    children: ["Description", "Qty", "Unit Price", "Total"].map(
      (text) =>
        new TableCell({
          children: [new Paragraph({ children: [new TextRun({ text, bold: true })] })],
          shading: { fill: "1F3864", type: ShadingType.CLEAR },
          run: { color: "FFFFFF" },
          margins: { top: 100, bottom: 100, left: 150, right: 150 },
        })
    ),
    tableHeader: true,
  });

  const itemRows = invoiceData.items.map(
    (item) =>
      new TableRow({
        children: [
          item.description,
          String(item.quantity),
          `$${item.unitPrice.toFixed(2)}`,
          `$${(item.quantity * item.unitPrice).toFixed(2)}`,
        ].map((text) =>
          new TableCell({
            children: [new Paragraph(text)],
            margins: { top: 80, bottom: 80, left: 150, right: 150 },
          })
        ),
      })
  );

  const total = invoiceData.items.reduce(
    (sum, item) => sum + item.quantity * item.unitPrice,
    0
  );

  return new Table({
    rows: [headerRow, ...itemRows,
      new TableRow({
        children: [
          new TableCell({ children: [new Paragraph("")], columnSpan: 2 }),
          new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "TOTAL:", bold: true })] })] }),
          new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: `$${total.toFixed(2)}`, bold: true })] })] }),
        ],
      }),
    ],
    width: { size: 100, type: WidthType.PERCENTAGE },
  });
}
```

### Complete Working Example 4: Document with TOC
```javascript
const { TableOfContents } = require("docx");

function createDocumentWithTOC(title, sections) {
  return new Document({
    features: { updateFields: true },
    sections: [{
      children: [
        new Paragraph({ text: title, heading: HeadingLevel.TITLE }),
        new TableOfContents("Table of Contents", {
          hyperlink: true,
          headingStyleRange: "1-3",
          stylesWithLevels: [
            { styleId: "Heading1", level: 1 },
            { styleId: "Heading2", level: 2 },
            { styleId: "Heading3", level: 3 },
          ],
        }),
        new Paragraph({ pageBreakBefore: true }),
        ...sections.flatMap((section) => [
          new Paragraph({ text: section.title, heading: HeadingLevel.HEADING_1 }),
          ...section.paragraphs.map((p) => new Paragraph(p)),
        ]),
      ],
    }],
  });
}
```

### Complete Working Example 5: Multi-Column Layout
```javascript
function createMultiColumnDocument(content) {
  return new Document({
    sections: [
      {
        properties: {
          page: {
            margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 },
          },
          column: { count: 2, space: 720, separate: true },
        },
        children: content.paragraphs.map((text) => new Paragraph(text)),
      },
    ],
  });
}
```

### Packer - Export Formats
```javascript
const { Packer } = require("docx");

// To Buffer (for file writing or upload)
const buffer = await Packer.toBuffer(doc);
fs.writeFileSync("output.docx", buffer);

// To Base64 String (for embedding or download links)
const base64 = await Packer.toBase64String(doc);
const dataUrl = `data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,${base64}`;

// To Blob (browser environment)
const blob = await Packer.toBlob(doc);
const url = URL.createObjectURL(blob);
const a = document.createElement("a");
a.href = url;
a.download = "document.docx";
a.click();

// To Stream (Node.js)
const stream = Packer.toStream(doc);
stream.pipe(fs.createWriteStream("output.docx"));
```

### Complete Working Example 6: Table of Contents with Custom Styles
```javascript
function createStyledTOCDocument(config) {
  const tocStyle = {
    id: "TOCHeading",
    name: "TOC Heading",
    basedOn: "Heading1",
    run: { size: 36, bold: true, color: "1F3864" },
    paragraph: { spacing: { before: 240, after: 120 } },
  };
  
  const doc = new Document({
    styles: {
      paragraphStyles: [tocStyle],
    },
    sections: [{
      children: [
        new TableOfContents("Contents", {
          hyperlink: true,
          headingStyleRange: "1-4",
          tabLeader: TabStopLeader.DOT,
        }),
        new Paragraph({ pageBreakBefore: true }),
        ...config.sections.flatMap(section => [
          new Paragraph({ text: section.heading, heading: HeadingLevel.HEADING_1 }),
          new Paragraph({ text: section.body }),
          ...section.subsections?.map(sub => [
            new Paragraph({ text: sub.heading, heading: HeadingLevel.HEADING_2 }),
            new Paragraph({ text: sub.body }),
          ]).flat() || [],
        ]),
      ],
    }],
  });
  return doc;
}
```

### Complete Working Example 7: Form Document
```javascript
function createFormDocument(formConfig) {
  const formFields = formConfig.fields.map(field => {
    const labelPara = new Paragraph({
      children: [new TextRun({ text: field.label, bold: true })],
      spacing: { before: 240, after: 40 },
    });
    
    const inputLine = new Paragraph({
      children: [new TextRun({ text: "_".repeat(field.lineLength || 60) })],
      spacing: { after: 200 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "808080" } },
    });
    
    return [labelPara, inputLine];
  }).flat();

  return new Document({
    sections: [{
      children: [
        new Paragraph({
          text: formConfig.title,
          heading: HeadingLevel.HEADING_1,
          alignment: AlignmentType.CENTER,
        }),
        new Paragraph({
          text: formConfig.subtitle || "",
          alignment: AlignmentType.CENTER,
          spacing: { after: 480 },
        }),
        ...formFields,
        new Paragraph({ spacing: { before: 480 } }),
        new Paragraph({
          children: [
            new TextRun({ text: "Signature: ", bold: true }),
            new TextRun("________________________  "),
            new TextRun({ text: "Date: ", bold: true }),
            new TextRun("______________"),
          ],
        }),
      ],
    }],
  });
}
```

### Complete Working Example 8: Nested Lists
```javascript
function createNestedListDocument(items) {
  const numberingConfig = {
    config: [
      {
        reference: "nested-numbering",
        levels: [
          { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
          { level: 1, format: LevelFormat.LOWER_LETTER, text: "%2)", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 1440, hanging: 360 } } } },
          { level: 2, format: LevelFormat.LOWER_ROMAN, text: "%3.", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 2160, hanging: 360 } } } },
        ],
      },
    ],
  };

  function renderItems(items, level = 0) {
    return items.flatMap(item => [
      new Paragraph({
        text: item.text,
        numbering: { reference: "nested-numbering", level },
      }),
      ...(item.children ? renderItems(item.children, level + 1) : []),
    ]);
  }

  return new Document({
    numbering: numberingConfig,
    sections: [{ children: renderItems(items) }],
  });
}
```

### Complete Working Example 9: Document Comparison
```javascript
const mammoth = require("mammoth");
const Diff = require("diff");

async function compareDocuments(file1Path, file2Path) {
  const [result1, result2] = await Promise.all([
    mammoth.extractRawText({ path: file1Path }),
    mammoth.extractRawText({ path: file2Path }),
  ]);

  const diffs = Diff.diffWords(result1.value, result2.value);
  const changes = diffs.filter(d => d.added || d.removed).length;

  return {
    totalChanges: changes,
    additions: diffs.filter(d => d.added).reduce((s, d) => s + d.value.length, 0),
    deletions: diffs.filter(d => d.removed).reduce((s, d) => s + d.value.length, 0),
    diffs,
  };
}
```

### Complete Working Example 10: Batch Document Generation
```javascript
const path = require("path");

async function batchGenerateDocuments(templateFn, dataArray, outputDir) {
  const results = { success: [], failed: [] };
  for (const data of dataArray) {
    try {
      const doc = await templateFn(data);
      const buffer = await Packer.toBuffer(doc);
      const filename = path.join(outputDir, `${data.id || Date.now()}.docx`);
      fs.writeFileSync(filename, buffer);
      results.success.push(filename);
    } catch (err) {
      results.failed.push({ data, error: err.message });
    }
  }
  return results;
}
```

### Integration with Mammoth (DOCX to HTML)
```javascript
const mammoth = require("mammoth");

async function docxToHtml(filePath, options = {}) {
  const defaultOptions = {
    styleMap: [
      "p[style-name='Heading 1'] => h1:fresh",
      "p[style-name='Heading 2'] => h2:fresh",
      "p[style-name='Code']      => pre > code",
      "r[style-name='Code Char'] => code",
    ],
    includeDefaultStyleMap: true,
    convertImage: mammoth.images.imgElement(async (image) => {
      const base64 = await image.read("base64");
      return { src: `data:${image.contentType};base64,${base64}` };
    }),
  };

  const result = await mammoth.convertToHtml(
    { path: filePath },
    { ...defaultOptions, ...options }
  );
  return { html: result.value, messages: result.messages };
}

async function docxToMarkdown(filePath) {
  const result = await mammoth.convertToMarkdown({ path: filePath });
  return result.value;
}
```

### Integration with docxtemplater
```javascript
const Docxtemplater = require("docxtemplater");
const PizZip = require("pizzip");

function fillTemplate(templateBuffer, data) {
  const zip = new PizZip(templateBuffer);
  const doc = new Docxtemplater(zip, {
    paragraphLoop: true,
    linebreaks: true,
    modules: [],
    delimiters: { start: "{{", end: "}}" },
  });

  doc.setData(data);
  doc.render();

  return doc.getZip().generate({ type: "nodebuffer" });
}

// Usage:
const template = fs.readFileSync("template.docx");
const filled = fillTemplate(template, {
  customer_name: "John Doe",
  order_items: [
    { name: "Widget A", price: 9.99, qty: 2 },
    { name: "Widget B", price: 14.99, qty: 1 },
  ],
  total: 34.97,
});
fs.writeFileSync("filled-document.docx", filled);
```

### Troubleshooting Guide

#### Issue 1: "Cannot read property of undefined" when creating Table
**Cause:** Empty children array in TableRow or TableCell  
**Solution:** Always provide at least one Paragraph in each TableCell:
```javascript
new TableCell({ children: [new Paragraph("")] })
```

#### Issue 2: Images not appearing in output
**Cause:** Incorrect Buffer format or missing type property  
**Solution:** Ensure you pass a proper Buffer and specify type:
```javascript
const data = fs.readFileSync("image.png"); // Returns Buffer
new ImageRun({ data, transformation: { width: 100, height: 100 }, type: "png" })
```

#### Issue 3: Custom styles not applying
**Cause:** Style ID mismatch between definition and usage  
**Solution:** Ensure the `id` in paragraphStyles matches the `style` property in Paragraph:
```javascript
// Define: { id: "MyCustom", name: "My Custom", ... }
// Use:    new Paragraph({ text: "Hello", style: "MyCustom" })
```

#### Issue 4: Large documents causing memory issues
**Solution:** Use streaming and chunked processing:
```javascript
const stream = Packer.toStream(doc);
const writeStream = fs.createWriteStream("large-output.docx");
stream.pipe(writeStream);
await new Promise((resolve, reject) => {
  writeStream.on("finish", resolve);
  writeStream.on("error", reject);
});
```

#### Issue 5: Page numbers not showing in footer
**Cause:** Missing `{ children: [PageNumber.CURRENT] }` syntax  
**Solution:**
```javascript
new TextRun({ children: [PageNumber.CURRENT] }) // Not text: PageNumber.CURRENT
```

#### Issue 6: Table borders not rendering
**Cause:** Borders object nested incorrectly  
**Solution:** Check border structure: each border (top/bottom/left/right) needs style, size, color:
```javascript
borders: {
  top: { style: BorderStyle.SINGLE, size: 3, color: "000000" },
}
```

#### Issue 7: Numbering not incrementing correctly
**Cause:** Missing or incorrect numbering reference  
**Solution:** Ensure numbering config reference matches exactly:
```javascript
// Config: reference: "bullet-list"
// Usage:  numbering: { reference: "bullet-list", level: 0 }
```

#### Issue 8: Headers/footers not appearing on all pages
**Cause:** `titlePage: true` set but first-page header not defined  
**Solution:** When using titlePage, define both default and first headers:
```javascript
headers: { default: mainHeader, first: firstPageHeader }
properties: { titlePage: true }
```

#### Issue 9: Special characters corrupted in output
**Cause:** Encoding issues when building strings  
**Solution:** Use Unicode escape sequences or ensure UTF-8 strings:
```javascript
new TextRun("Copyright \u00A9 2024")
new TextRun("Em dash \u2014 like this")
```

#### Issue 10: Column widths not respected
**Cause:** Table layout set to AUTO instead of FIXED  
**Solution:**
```javascript
new Table({
  layout: TableLayoutType.FIXED,
  columnWidths: [2500, 2500, 2500, 2500], // must match total page width
  ...
})
```

#### Issue 11: PDF export quality
**Note:** docx package does not natively export PDF. Use LibreOffice CLI or Microsoft's conversion API:
```javascript
// Using LibreOffice:
const { execSync } = require("child_process");
execSync(`libreoffice --headless --convert-to pdf output.docx --outdir ./pdfs`);
```

#### Issue 12: Text alignment in table cells
**Cause:** Alignment set on TextRun instead of Paragraph  
**Solution:** Set alignment on the Paragraph inside the TableCell:
```javascript
new TableCell({
  children: [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun("Centered")],
    }),
  ],
})
```

#### Issue 13: Multiple sections not working correctly
**Cause:** Incorrect section properties for continuous vs page breaks  
**Solution:** Use correct SectionType values:
```javascript
// Continuous section break (no new page):
type: SectionType.CONTINUOUS

// New page section break:
type: SectionType.NEXT_PAGE
```

#### Issue 14: Table of Contents not updating
**Cause:** updateFields feature not enabled  
**Solution:**
```javascript
new Document({
  features: { updateFields: true },
  ...
})
```

#### Issue 15: Document corrupted when opened
**Cause:** Missing required section properties or empty sections array  
**Solution:** Every document must have at least one section with a children array:
```javascript
sections: [{ children: [new Paragraph("")] }]
```

### Migration Guide from python-docx
```
python-docx                  ->  docx (npm)
-------------------------------------------
Document()                   ->  new Document({ sections: [...] })
doc.add_paragraph(text)      ->  new Paragraph(text)
doc.add_heading(text, level) ->  new Paragraph({ text, heading: HeadingLevel.HEADING_N })
doc.add_table(rows, cols)    ->  new Table({ rows: [...] })
para.add_run(text)           ->  new TextRun(text) in children array
run.bold = True              ->  new TextRun({ text, bold: true })
run.font.color.rgb = Color   ->  new TextRun({ text, color: "RRGGBB" })
doc.save(path)               ->  Packer.toBuffer(doc) then fs.writeFileSync
```

### Migration Guide from docxtemplater
```javascript
// Before (docxtemplater):
const zip = new PizZip(content);
const doc = new Docxtemplater(zip);
doc.setData({ name: "John" });
doc.render();
const buffer = doc.getZip().generate({ type: "nodebuffer" });

// After (docx npm package):
const doc = new Document({
  sections: [{
    children: [new Paragraph({ text: `Hello, ${name}` })],
  }],
});
const buffer = await Packer.toBuffer(doc);
```

### Performance Tips
1. **Reuse style objects** - Create style constants once and reuse across documents
2. **Batch Packer calls** - Use Promise.all for multiple concurrent exports
3. **Stream large documents** - Use Packer.toStream() for files > 10MB
4. **Pre-calculate table widths** - Use fixed table layout with pre-calculated column widths
5. **Minimize ImageRun instances** - Reuse image buffers across multiple ImageRun instances
6. **Use references for numbering** - Define numbering once in the Document constructor
7. **Avoid deep nesting** - Keep table nesting to 2 levels maximum
8. **Cache compiled styles** - Compute style objects outside render loops
```javascript
// Good: styles computed once
const HEADING_STYLE = { heading: HeadingLevel.HEADING_1 };
paragraphs.map(text => new Paragraph({ text, ...HEADING_STYLE }));

// Bad: new object created every iteration  
paragraphs.map(text => new Paragraph({ text, heading: HeadingLevel.HEADING_1 }));
```

### Font Reference
```javascript
// Web-safe fonts available in most Word environments:
const FONTS = {
  serif:      ["Times New Roman", "Georgia", "Palatino Linotype"],
  sansSerif:  ["Arial", "Calibri", "Helvetica", "Trebuchet MS", "Verdana"],
  monospace:  ["Courier New", "Consolas", "Lucida Console"],
  display:    ["Impact", "Comic Sans MS", "Arial Black"],
};

// Setting document default font:
const doc = new Document({
  styles: {
    default: {
      document: {
        run: { font: "Calibri", size: 22, color: "333333" },
      },
    },
  },
  ...
});
```

### Custom Document Properties
```javascript
const doc = new Document({
  externalRelationships: [],
  background: { color: "FFFFFF" },
  creator: "MyApp v1.0",
  description: "Auto-generated report",
  title: "Quarterly Report Q1 2024",
  subject: "Financial Report",
  keywords: "finance, quarterly, report, 2024",
  lastModifiedBy: "System",
  revision: 1,
  sections: [...],
});
```
"""

# Write docx.skill content
with open(f"{BASE}/docx.skill", "a", encoding="utf-8") as f:
    f.write(docx_content)

size = os.path.getsize(f"{BASE}/docx.skill")
print(f"docx.skill: {size} bytes ({size/1024:.1f} KB)")
