#!/usr/bin/env node
/**
 * fill-form.js
 * Demonstrates creating and filling PDF forms using pdf-lib.
 * Usage: node fill-form.js [--create] [--fill <input.pdf>] [output.pdf]
 */

const { PDFDocument, StandardFonts, rgb } = require('pdf-lib');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const doCreate = args.includes('--create') || !args.includes('--fill');
const fillIdx  = args.indexOf('--fill');
const fillPath = fillIdx >= 0 ? args[fillIdx + 1] : null;
const outputPath = args.find((a) => !a.startsWith('--') && a !== fillPath) ||
                   path.join(__dirname, doCreate ? 'form-template.pdf' : 'form-filled.pdf');

// ── Create a PDF form template ───────────────────────────────────────────────
async function createFormTemplate(outPath) {
  const pdfDoc = await PDFDocument.create();
  const page = pdfDoc.addPage([595, 842]);
  const font = await pdfDoc.embedFont(StandardFonts.Helvetica);
  const boldFont = await pdfDoc.embedFont(StandardFonts.HelveticaBold);
  const form = pdfDoc.getForm();
  const { height } = page.getSize();
  const BLUE = rgb(0.12, 0.31, 0.47);
  const GRAY = rgb(0.4, 0.4, 0.4);

  // Header
  page.drawRectangle({ x: 0, y: height - 60, width: 595, height: 60, color: BLUE });
  page.drawText('Contact Form', { x: 50, y: height - 38, size: 20, font: boldFont, color: rgb(1,1,1) });

  function label(text, x, y) {
    page.drawText(text, { x, y, size: 9, font, color: GRAY });
  }

  function textField(name, x, y, w, h = 20) {
    const f = form.createTextField(name);
    f.addToPage(page, {
      x, y, width: w, height: h,
      borderColor: rgb(0.7, 0.7, 0.7),
      backgroundColor: rgb(0.98, 0.98, 0.98),
      textColor: rgb(0, 0, 0),
      fontSize: 10,
    });
    return f;
  }

  function checkField(name, x, y) {
    const f = form.createCheckBox(name);
    f.addToPage(page, { x, y, width: 13, height: 13, borderColor: rgb(0.5,0.5,0.5) });
    return f;
  }

  function dropdown(name, options, x, y, w) {
    const f = form.createDropdown(name);
    f.addOptions(options);
    f.addToPage(page, {
      x, y, width: w, height: 20,
      borderColor: rgb(0.7, 0.7, 0.7),
      backgroundColor: rgb(0.98, 0.98, 0.98),
      textColor: rgb(0, 0, 0),
      fontSize: 10,
    });
    return f;
  }

  // Personal details
  let y = height - 100;
  page.drawText('Personal Details', { x: 50, y, size: 12, font: boldFont, color: BLUE });

  y -= 30; label('First Name', 50, y); label('Last Name', 305, y);
  y -= 22; textField('firstName', 50, y, 230); textField('lastName', 305, y, 240);

  y -= 40; label('Email Address', 50, y);
  y -= 22; textField('email', 50, y, 495);

  y -= 40; label('Phone Number', 50, y); label('Company', 305, y);
  y -= 22; textField('phone', 50, y, 230); textField('company', 305, y, 240);

  // Address
  y -= 50;
  page.drawText('Address', { x: 50, y, size: 12, font: boldFont, color: BLUE });

  y -= 30; label('Street Address', 50, y);
  y -= 22; textField('street', 50, y, 495);

  y -= 40; label('City', 50, y); label('Country', 305, y);
  y -= 22; textField('city', 50, y, 230);
  dropdown('country', ['United States','Canada','United Kingdom','Australia','India','Other'], 305, y, 240);

  // Preferences
  y -= 50;
  page.drawText('Preferences', { x: 50, y, size: 12, font: boldFont, color: BLUE });

  y -= 30;
  checkField('newsletter', 50, y);
  page.drawText('Subscribe to newsletter', { x: 68, y: y + 2, size: 10, font, color: GRAY });

  y -= 25;
  checkField('smsAlerts', 50, y);
  page.drawText('Receive SMS notifications', { x: 68, y: y + 2, size: 10, font, color: GRAY });

  // Comments
  y -= 50; label('Additional Comments', 50, y);
  y -= 70;
  const comments = form.createTextField('comments');
  comments.enableMultiline();
  comments.addToPage(page, {
    x: 50, y, width: 495, height: 60,
    borderColor: rgb(0.7, 0.7, 0.7),
    backgroundColor: rgb(0.98, 0.98, 0.98),
    textColor: rgb(0, 0, 0),
    fontSize: 10,
  });

  // Terms checkbox
  y -= 30;
  checkField('agreeTerms', 50, y);
  page.drawText('I agree to the Terms of Service and Privacy Policy', { x: 68, y: y + 2, size: 10, font, color: GRAY });

  const pdfBytes = await pdfDoc.save();
  fs.writeFileSync(outPath, pdfBytes);
  console.log(`Form template created: ${outPath}`);
}

// ── Fill an existing form ────────────────────────────────────────────────────
async function fillExistingForm(inputPath, outPath) {
  const pdfDoc = await PDFDocument.load(fs.readFileSync(inputPath));
  const form = pdfDoc.getForm();

  const data = {
    firstName: 'Jane',
    lastName:  'Doe',
    email:     'jane.doe@example.com',
    phone:     '+1 (555) 123-4567',
    company:   'Acme Corporation',
    street:    '123 Main Street',
    city:      'San Francisco',
    country:   'United States',
    newsletter: true,
    smsAlerts:  false,
    agreeTerms: true,
    comments:   'Looking forward to working with your team.',
  };

  for (const [key, value] of Object.entries(data)) {
    try {
      const field = form.getField(key);
      const type = field.constructor.name;
      if (type === 'PDFTextField') field.setText(String(value));
      else if (type === 'PDFCheckBox') value ? field.check() : field.uncheck();
      else if (type === 'PDFDropdown') field.select(String(value));
      else if (type === 'PDFRadioGroup') field.select(String(value));
    } catch (e) {
      console.warn(`Field "${key}" not found or incompatible: ${e.message}`);
    }
  }

  // Flatten (make non-editable)
  form.flatten();

  fs.writeFileSync(outPath, await pdfDoc.save());
  console.log(`Filled form saved: ${outPath}`);
}

async function main() {
  if (fillPath) {
    if (!fs.existsSync(fillPath)) {
      console.error(`Input file not found: ${fillPath}`);
      process.exit(1);
    }
    await fillExistingForm(fillPath, outputPath);
  } else {
    await createFormTemplate(outputPath);
    console.log('\nTo fill this form, run:');
    console.log(`  node fill-form.js --fill ${outputPath} filled-output.pdf`);
  }
}

main().catch((err) => { console.error(err); process.exit(1); });
