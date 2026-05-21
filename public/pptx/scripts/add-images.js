#!/usr/bin/env node
/**
 * add-images.js
 * Demonstrates image placement options in pptxgenjs.
 * Usage: node add-images.js [image-path] [output.pptx]
 */

const PptxGenJS = require('pptxgenjs');
const path = require('path');
const fs = require('fs');

const imgArg = process.argv[2];
const outputPath = process.argv[3] || path.join(__dirname, 'images-demo.pptx');

// Tiny placeholder PNG (1x1 white pixel)
const PLACEHOLDER_B64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwADhQGAWjR9awAAAABJRU5ErkJggg==';

async function main() {
  const pres = new PptxGenJS();

  const imageOpts = imgArg && fs.existsSync(imgArg)
    ? { path: imgArg }
    : { data: PLACEHOLDER_B64 };

  console.log(imageOpts.path ? `Using image: ${imageOpts.path}` : 'Using placeholder image');

  // Slide 1: Basic inline images
  const s1 = pres.addSlide();
  s1.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: '100%', h: 0.9, fill: '1F4E79' });
  s1.addText('Image Placement', { x: 0.4, y: 0.1, w: 9, h: 0.7, fontSize: 28, bold: true, color: 'FFFFFF' });

  // Small thumbnail
  s1.addImage({ ...imageOpts, x: 0.5, y: 1.1, w: 2, h: 1.5 });
  s1.addText('Small (2"×1.5")', { x: 0.5, y: 2.7, w: 2, h: 0.4, fontSize: 11, color: '555555', align: 'center' });

  // Medium
  s1.addImage({ ...imageOpts, x: 3, y: 1.1, w: 3, h: 2.5 });
  s1.addText('Medium (3"×2.5")', { x: 3, y: 3.7, w: 3, h: 0.4, fontSize: 11, color: '555555', align: 'center' });

  // Large
  s1.addImage({ ...imageOpts, x: 6.5, y: 1.1, w: 3, h: 3.8 });
  s1.addText('Large (3"×3.8")', { x: 6.5, y: 5.0, w: 3, h: 0.4, fontSize: 11, color: '555555', align: 'center' });

  // Slide 2: Sizing modes
  const s2 = pres.addSlide();
  s2.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: '100%', h: 0.9, fill: '1F4E79' });
  s2.addText('Image Sizing Modes', { x: 0.4, y: 0.1, w: 9, h: 0.7, fontSize: 28, bold: true, color: 'FFFFFF' });

  const sizingTypes = ['contain', 'cover', 'crop'];
  sizingTypes.forEach((type, i) => {
    const x = 0.4 + i * 3.2;
    s2.addImage({
      ...imageOpts,
      x, y: 1.1, w: 2.8, h: 2.8,
      sizing: { type, w: 2.8, h: 2.8 },
    });
    s2.addText(`sizing: '${type}'`, { x, y: 4.1, w: 2.8, h: 0.4, fontSize: 12, color: '333333', align: 'center' });
  });

  // Slide 3: Rounded & rotated
  const s3 = pres.addSlide();
  s3.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: '100%', h: 0.9, fill: '1F4E79' });
  s3.addText('Rounded & Rotated', { x: 0.4, y: 0.1, w: 9, h: 0.7, fontSize: 28, bold: true, color: 'FFFFFF' });

  // Circular
  s3.addImage({ ...imageOpts, x: 0.5, y: 1.3, w: 3, h: 3, rounding: true });
  s3.addText('rounding: true (circular)', { x: 0.5, y: 4.4, w: 3, h: 0.4, fontSize: 11, color: '555555' });

  // Rotated
  s3.addImage({ ...imageOpts, x: 5, y: 1.5, w: 3, h: 2.5, rotate: 15 });
  s3.addText('rotate: 15°', { x: 5, y: 4.2, w: 3, h: 0.4, fontSize: 11, color: '555555' });

  await pres.writeFile({ fileName: outputPath });
  console.log(`Images demo: ${outputPath}`);
}

main().catch((err) => { console.error(err); process.exit(1); });
