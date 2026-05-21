#!/usr/bin/env node
/**
 * add-content.js
 * Demonstrates adding content to an existing PDF using pdf-lib.
 * Usage: node add-content.js <input.pdf> [output.pdf]
 */

const { PDFDocument, rgb, StandardFonts, degrees } = require('pdf-lib');
const fs = require('fs');
const path = require('path');

const inputPath  = process.argv[2];
const outputPath = process.argv[3] || path.join(__dirname, 'annotated.pdf');

async function main() {
  let pdfDoc;

  if (inputPath && fs.existsSync(inputPath)) {
    pdfDoc = await PDFDocument.load(fs.readFileSync(inputPath));
    console.log(`Loaded: ${inputPath} (${pdfDoc.getPageCount()} pages)`);
  } else {
    // Create a demo PDF to annotate
    pdfDoc = await PDFDocument.create();
    const page = pdfDoc.addPage([595, 842]);
    const font = await pdfDoc.embedFont(StandardFonts.TimesRoman);
    page.drawText('Original Document Content', { x: 100, y: 750, size: 20, font, color: rgb(0, 0, 0) });
    page.drawText('This is the body of the original document.', { x: 100, y: 700, size: 12, font });
    console.log('No input file provided — created demo document.');
  }

  const font = await pdfDoc.embedFont(StandardFonts.Helvetica);
  const boldFont = await pdfDoc.embedFont(StandardFonts.HelveticaBold);
  const firstPage = pdfDoc.getPage(0);
  const { width, height } = firstPage.getSize();

  // 1. Add watermark (rotated, semi-transparent)
  firstPage.drawText('CONFIDENTIAL', {
    x: 120, y: height / 2 - 30,
    size: 72,
    font: boldFont,
    color: rgb(0.85, 0.85, 0.85),
    opacity: 0.25,
    rotate: degrees(45),
  });

  // 2. Add header bar on all pages
  pdfDoc.getPages().forEach((page, i) => {
    const { w, h } = { w: page.getWidth(), h: page.getHeight() };
    page.drawRectangle({ x: 0, y: h - 40, width: w, height: 40, color: rgb(0.12, 0.31, 0.47) });
    page.drawText('DreamCo Technologies — Confidential', {
      x: 20, y: h - 26, size: 10, font, color: rgb(1, 1, 1),
    });
    page.drawText(`Page ${i + 1}`, {
      x: w - 60, y: h - 26, size: 10, font, color: rgb(1, 1, 1),
    });
  });

  // 3. Add footer on first page
  firstPage.drawLine({
    start: { x: 40, y: 40 },
    end:   { x: width - 40, y: 40 },
    thickness: 0.5,
    color: rgb(0.7, 0.7, 0.7),
  });
  firstPage.drawText(
    `Generated on ${new Date().toLocaleDateString()} | info@dreamco.com`,
    { x: 40, y: 24, size: 8, font, color: rgb(0.5, 0.5, 0.5) }
  );

  // 4. Add annotation box
  firstPage.drawRectangle({
    x: 40, y: 60, width: width - 80, height: 50,
    color: rgb(0.95, 0.98, 1),
    borderColor: rgb(0.12, 0.31, 0.47),
    borderWidth: 1.5,
  });
  firstPage.drawText('Note: This document has been annotated programmatically using pdf-lib.', {
    x: 50, y: 80, size: 10, font, color: rgb(0.12, 0.31, 0.47),
  });
  firstPage.drawText('Original content is preserved unchanged.', {
    x: 50, y: 66, size: 9, font, color: rgb(0.4, 0.4, 0.4),
  });

  // Set metadata
  pdfDoc.setTitle('Annotated Document');
  pdfDoc.setAuthor('Dreamcobots');
  pdfDoc.setModificationDate(new Date());

  fs.writeFileSync(outputPath, await pdfDoc.save());
  console.log(`Annotated PDF saved: ${outputPath}`);
}

main().catch((err) => { console.error(err); process.exit(1); });
