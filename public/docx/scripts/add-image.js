#!/usr/bin/env node
/**
 * add-image.js
 * Demonstrates embedding and floating images in a Word document.
 * Usage: node add-image.js <image-path> [output.docx]
 */

const {
  Document, Packer, Paragraph, TextRun, ImageRun, HeadingLevel,
  AlignmentType, HorizontalPositionRelativeFrom, VerticalPositionRelativeFrom,
  HorizontalPositionAlign, VerticalPositionAlign,
  TextWrappingType, TextWrappingSide,
} = require('docx');
const fs = require('fs');
const path = require('path');

const imagePath = process.argv[2];
const outputPath = process.argv[3] || path.join(__dirname, 'image-demo.docx');

async function main() {
  // Use a placeholder if no image provided
  let imageData;
  let imageWidth = 300;
  let imageHeight = 200;

  if (imagePath && fs.existsSync(imagePath)) {
    imageData = fs.readFileSync(imagePath);
    console.log(`Using image: ${imagePath}`);
  } else {
    // Generate a 1x1 white PNG as placeholder (base64)
    imageData = Buffer.from(
      'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwADhQGAWjR9awAAAABJRU5ErkJggg==',
      'base64'
    );
    imageWidth = 200;
    imageHeight = 100;
    console.warn('No image provided, using placeholder. Usage: node add-image.js <image-path>');
  }

  const doc = new Document({
    sections: [{
      children: [
        new Paragraph({
          text: 'Image Embedding Demo',
          heading: HeadingLevel.HEADING_1,
          spacing: { after: 300 },
        }),

        // 1. Inline image (in-flow with text)
        new Paragraph({
          text: 'Inline Image',
          heading: HeadingLevel.HEADING_2,
          spacing: { before: 200, after: 100 },
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            new ImageRun({
              data: imageData,
              transformation: { width: imageWidth, height: imageHeight },
            }),
          ],
        }),
        new Paragraph({
          spacing: { before: 100, after: 300 },
          children: [
            new TextRun({ text: 'Figure 1: ', bold: true }),
            new TextRun({ text: 'An inline image centered on the page.', italics: true }),
          ],
        }),

        // 2. Resized image
        new Paragraph({
          text: 'Resized Image (thumbnail)',
          heading: HeadingLevel.HEADING_2,
          spacing: { before: 200, after: 100 },
        }),
        new Paragraph({
          children: [
            new ImageRun({
              data: imageData,
              transformation: { width: 80, height: 60 },
            }),
            new TextRun({
              text: '  ← This image is rendered as a 80×60 px thumbnail next to this text.',
              italics: true,
              color: '555555',
            }),
          ],
        }),

        // 3. Body text explaining floating
        new Paragraph({
          text: 'Image Options',
          heading: HeadingLevel.HEADING_2,
          spacing: { before: 300, after: 100 },
        }),
        new Paragraph({
          spacing: { after: 100 },
          children: [
            new TextRun('Images can be placed in two ways:\n'),
            new TextRun({ text: '• Inline: ', bold: true }),
            new TextRun('flows with text, respects paragraph alignment.\n'),
            new TextRun({ text: '• Floating: ', bold: true }),
            new TextRun('positioned absolutely on the page; text wraps around it.'),
          ],
        }),
        new Paragraph({
          spacing: { after: 100 },
          children: [
            new TextRun({ text: 'Supported formats: ', bold: true }),
            new TextRun('PNG, JPEG, GIF, BMP, SVG'),
          ],
        }),
        new Paragraph({
          spacing: { after: 100 },
          children: [
            new TextRun({ text: 'Size units: ', bold: true }),
            new TextRun('pixels in the transformation object (width/height).'),
          ],
        }),
      ],
    }],
  });

  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(outputPath, buffer);
  console.log(`Image document created: ${outputPath}`);
}

main().catch((err) => { console.error(err); process.exit(1); });
