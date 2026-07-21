#!/usr/bin/env node
/**
 * read-document.js
 * Reads and extracts content from an existing .docx file.
 * Usage: node read-document.js <input.docx> [--html] [--json]
 */

const mammoth = require('mammoth');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const inputPath = args.find((a) => !a.startsWith('--'));
const outputHtml = args.includes('--html');
const outputJson = args.includes('--json');

if (!inputPath) {
  console.error('Usage: node read-document.js <input.docx> [--html] [--json]');
  process.exit(1);
}

if (!fs.existsSync(inputPath)) {
  console.error(`File not found: ${inputPath}`);
  process.exit(1);
}

async function readDocument() {
  console.log(`Reading: ${inputPath}`);

  // Extract raw text
  const textResult = await mammoth.extractRawText({ path: inputPath });
  if (textResult.messages.length) {
    textResult.messages.forEach((m) => console.warn(`[WARN] ${m.message}`));
  }

  if (outputJson) {
    const jsonOutput = {
      text: textResult.value,
      characterCount: textResult.value.length,
      wordCount: textResult.value.split(/\s+/).filter(Boolean).length,
      lineCount: textResult.value.split('\n').length,
    };
    const jsonPath = inputPath.replace(/\.docx$/i, '.json');
    fs.writeFileSync(jsonPath, JSON.stringify(jsonOutput, null, 2));
    console.log(`JSON output: ${jsonPath}`);
    console.log(`Words: ${jsonOutput.wordCount}, Characters: ${jsonOutput.characterCount}`);
    return;
  }

  if (outputHtml) {
    const htmlResult = await mammoth.convertToHtml(
      { path: inputPath },
      {
        styleMap: [
          "p[style-name='Heading 1'] => h1:fresh",
          "p[style-name='Heading 2'] => h2:fresh",
          "p[style-name='Heading 3'] => h3:fresh",
          "p[style-name='Title'] => h1.title:fresh",
        ],
      }
    );
    if (htmlResult.messages.length) {
      htmlResult.messages.forEach((m) => console.warn(`[WARN] ${m.message}`));
    }
    const htmlPath = inputPath.replace(/\.docx$/i, '.html');
    const fullHtml = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Extracted Document</title>
  <style>
    body { font-family: Calibri, Arial, sans-serif; max-width: 800px; margin: 40px auto; line-height: 1.6; }
    h1, h2, h3 { color: #1F4E79; }
    table { border-collapse: collapse; width: 100%; }
    td, th { border: 1px solid #ccc; padding: 6px 10px; }
  </style>
</head>
<body>
${htmlResult.value}
</body>
</html>`;
    fs.writeFileSync(htmlPath, fullHtml);
    console.log(`HTML output: ${htmlPath}`);
    return;
  }

  // Default: print text to stdout
  console.log('\n--- Document Contents ---\n');
  console.log(textResult.value);
  console.log('\n--- Statistics ---');
  const words = textResult.value.split(/\s+/).filter(Boolean);
  console.log(`Words: ${words.length}`);
  console.log(`Characters: ${textResult.value.length}`);
  console.log(`Lines: ${textResult.value.split('\n').length}`);
}

readDocument().catch((err) => {
  console.error('Error reading document:', err.message);
  process.exit(1);
});
