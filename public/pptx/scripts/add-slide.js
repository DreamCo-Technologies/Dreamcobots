#!/usr/bin/env node
/**
 * add-slide.js
 * Demonstrates various slide layout patterns.
 * Usage: node add-slide.js [output.pptx]
 */

const PptxGenJS = require('pptxgenjs');
const path = require('path');

const outputPath = process.argv[2] || path.join(__dirname, 'slides-demo.pptx');

async function main() {
  const pres = new PptxGenJS();

  // Title Slide
  const titleSlide = pres.addSlide();
  titleSlide.background = { fill: '1F4E79' };
  titleSlide.addText('Slide Layouts Demo', { x: 1, y: 1.5, w: 8, h: 1.5, fontSize: 44, bold: true, color: 'FFFFFF', align: 'center' });
  titleSlide.addText('Various slide types with pptxgenjs', { x: 1, y: 3.2, w: 8, h: 0.6, fontSize: 20, color: '9DC3E6', align: 'center' });

  // Two-column slide
  const twoCol = pres.addSlide();
  twoCol.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: '100%', h: 0.9, fill: '1F4E79' });
  twoCol.addText('Two-Column Layout', { x: 0.4, y: 0.1, w: 9, h: 0.7, fontSize: 28, bold: true, color: 'FFFFFF' });
  // Left column
  twoCol.addShape(pres.ShapeType.roundRect, { x: 0.3, y: 1.1, w: 4.3, h: 4, fill: 'F0F4FF', line: { color: '9DC3E6', width: 1 }, rectRadius: 0.08 });
  twoCol.addText('Left Column', { x: 0.5, y: 1.2, w: 3.9, h: 0.5, fontSize: 16, bold: true, color: '1F4E79' });
  twoCol.addText('Content goes here\n\nBullet points\nand more detail', { x: 0.5, y: 1.8, w: 3.9, h: 3, fontSize: 14, color: '333333' });
  // Right column
  twoCol.addShape(pres.ShapeType.roundRect, { x: 5.1, y: 1.1, w: 4.4, h: 4, fill: 'FFF4F0', line: { color: 'F4A460', width: 1 }, rectRadius: 0.08 });
  twoCol.addText('Right Column', { x: 5.3, y: 1.2, w: 3.9, h: 0.5, fontSize: 16, bold: true, color: 'C25B00' });
  twoCol.addText('Complementary info\n\nSide-by-side comparison\nis easy with shapes', { x: 5.3, y: 1.8, w: 3.9, h: 3, fontSize: 14, color: '333333' });

  // Full-image slide
  const imgSlide = pres.addSlide();
  imgSlide.background = { fill: '222222' };
  imgSlide.addShape(pres.ShapeType.rect, { x: 0, y: 3.5, w: '100%', h: 2.125, fill: { type: 'solid', color: '000000', alpha: 60 } });
  imgSlide.addText('Full-Background Slide', { x: 0.5, y: 3.7, w: 9, h: 0.8, fontSize: 36, bold: true, color: 'FFFFFF', align: 'center' });
  imgSlide.addText('Caption or subtitle here', { x: 0.5, y: 4.5, w: 9, h: 0.5, fontSize: 18, color: 'CCCCCC', align: 'center' });

  // Quote slide
  const quoteSlide = pres.addSlide();
  quoteSlide.background = { fill: 'FAFAFA' };
  quoteSlide.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: 0.15, h: '100%', fill: '1F4E79' });
  quoteSlide.addText('\u201C', { x: 0.5, y: 0.5, w: 1, h: 1.5, fontSize: 120, color: 'DDEEFF', bold: true });
  quoteSlide.addText(
    'Innovation distinguishes between a leader and a follower.',
    { x: 1.5, y: 1.3, w: 7.5, h: 2, fontSize: 28, italic: true, color: '333333' }
  );
  quoteSlide.addText('— Steve Jobs', { x: 5, y: 3.5, w: 4, h: 0.5, fontSize: 16, color: '888888', align: 'right' });

  await pres.writeFile({ fileName: outputPath });
  console.log(`Slides demo: ${outputPath}`);
}

main().catch((err) => { console.error(err); process.exit(1); });
