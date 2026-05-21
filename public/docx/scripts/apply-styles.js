#!/usr/bin/env node
/**
 * apply-styles.js
 * Demonstrates custom paragraph and character styles in docx.
 * Usage: node apply-styles.js [output.docx]
 */

const {
  Document, Packer, Paragraph, TextRun,
  HeadingLevel, AlignmentType, BorderStyle,
  ShadingType, UnderlineType, LevelFormat,
} = require('docx');
const fs = require('fs');
const path = require('path');

const outputPath = process.argv[2] || path.join(__dirname, 'styles-demo.docx');

async function main() {
  const doc = new Document({
    styles: {
      paragraphStyles: [
        {
          id: 'CalloutBox',
          name: 'Callout Box',
          basedOn: 'Normal',
          next: 'Normal',
          run: { size: 22, color: '1F4E79', italics: true },
          paragraph: {
            spacing: { before: 200, after: 200 },
            shading: { type: ShadingType.SOLID, color: 'DEEAF1' },
            border: {
              left: { style: BorderStyle.THICK, size: 12, color: '1F4E79', space: 8 },
            },
          },
        },
        {
          id: 'CodeBlock',
          name: 'Code Block',
          basedOn: 'Normal',
          run: { size: 20, font: 'Courier New', color: '333333' },
          paragraph: {
            spacing: { before: 100, after: 100, line: 276 },
            shading: { type: ShadingType.SOLID, color: 'F4F4F4' },
            border: {
              top:    { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC', space: 4 },
              bottom: { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC', space: 4 },
              left:   { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC', space: 4 },
              right:  { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC', space: 4 },
            },
          },
        },
        {
          id: 'Subtitle',
          name: 'Subtitle',
          basedOn: 'Normal',
          run: { size: 28, color: '595959', italics: true },
          paragraph: { alignment: AlignmentType.CENTER, spacing: { after: 400 } },
        },
      ],
      characterStyles: [
        {
          id: 'Keyword',
          name: 'Keyword',
          basedOn: 'DefaultParagraphFont',
          run: {
            bold: true,
            color: 'BF0000',
            font: 'Courier New',
            size: 20,
          },
        },
        {
          id: 'ImportantTerm',
          name: 'Important Term',
          basedOn: 'DefaultParagraphFont',
          run: {
            bold: true,
            italics: true,
            color: '1F4E79',
            underline: { type: UnderlineType.SINGLE },
          },
        },
      ],
    },
    numbering: {
      config: [
        {
          reference: 'bullet',
          levels: [
            {
              level: 0,
              format: LevelFormat.BULLET,
              text: '\u2022',
              alignment: AlignmentType.LEFT,
              style: { paragraph: { indent: { left: 720, hanging: 360 } } },
            },
            {
              level: 1,
              format: LevelFormat.BULLET,
              text: '\u25E6',
              alignment: AlignmentType.LEFT,
              style: { paragraph: { indent: { left: 1440, hanging: 360 } } },
            },
          ],
        },
      ],
    },
    sections: [{
      children: [
        new Paragraph({ text: 'Document Styles Demo', heading: HeadingLevel.TITLE, alignment: AlignmentType.CENTER }),
        new Paragraph({ text: 'Using custom paragraph and character styles', style: 'Subtitle' }),

        new Paragraph({ text: 'Callout Box', heading: HeadingLevel.HEADING_1, spacing: { before: 400 } }),
        new Paragraph({
          style: 'CalloutBox',
          text: 'This is a callout box paragraph with a left border accent and blue background. Use this style to highlight important notes or tips.',
        }),

        new Paragraph({ text: 'Code Block', heading: HeadingLevel.HEADING_1, spacing: { before: 300 } }),
        new Paragraph({ style: 'CodeBlock', text: 'const result = await fetchData(endpoint);' }),
        new Paragraph({ style: 'CodeBlock', text: 'console.log(JSON.stringify(result, null, 2));' }),

        new Paragraph({ text: 'Character Styles', heading: HeadingLevel.HEADING_1, spacing: { before: 300, after: 150 } }),
        new Paragraph({
          spacing: { after: 200, line: 360 },
          children: [
            new TextRun('Use the '),
            new TextRun({ text: 'Keyword', style: 'Keyword' }),
            new TextRun(' character style for code references, and '),
            new TextRun({ text: 'ImportantTerm', style: 'ImportantTerm' }),
            new TextRun(' for defined vocabulary terms.'),
          ],
        }),

        new Paragraph({ text: 'Bulleted List', heading: HeadingLevel.HEADING_1, spacing: { before: 300, after: 100 } }),
        new Paragraph({ text: 'First item', numbering: { reference: 'bullet', level: 0 } }),
        new Paragraph({ text: 'Second item', numbering: { reference: 'bullet', level: 0 } }),
        new Paragraph({ text: 'Nested sub-item', numbering: { reference: 'bullet', level: 1 } }),
        new Paragraph({ text: 'Third item', numbering: { reference: 'bullet', level: 0 } }),
      ],
    }],
  });

  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(outputPath, buffer);
  console.log(`Styles document created: ${outputPath}`);
}

main().catch((err) => { console.error(err); process.exit(1); });
