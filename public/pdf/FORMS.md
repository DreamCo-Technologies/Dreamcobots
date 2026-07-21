# PDF Forms — Creating, Reading, and Filling

## Overview

PDF forms (AcroForms) contain interactive fields: text inputs, checkboxes, radio buttons, dropdowns, and signature fields. The **pdf-lib** library provides full support for creating and filling these forms.

## Installation

```bash
npm install pdf-lib
npm install @pdf-lib/fontkit  # required for custom fonts in forms
```

---

## Reading Existing Form Fields

```js
const { PDFDocument } = require('pdf-lib');
const fs = require('fs');

async function readFormFields(pdfPath) {
  const pdfDoc = await PDFDocument.load(fs.readFileSync(pdfPath));
  const form = pdfDoc.getForm();
  const fields = form.getFields();

  fields.forEach((field) => {
    const type = field.constructor.name;
    const name = field.getName();
    console.log(`${type}: ${name}`);

    // Get current values
    if (type === 'PDFTextField') {
      console.log('  Value:', field.getText());
    } else if (type === 'PDFCheckBox') {
      console.log('  Checked:', field.isChecked());
    } else if (type === 'PDFDropdown') {
      console.log('  Selected:', field.getSelected());
    } else if (type === 'PDFRadioGroup') {
      console.log('  Selected:', field.getSelected());
    } else if (type === 'PDFOptionList') {
      console.log('  Selected:', field.getSelected());
    }
  });
}
```

---

## Filling an Existing Form

```js
const { PDFDocument } = require('pdf-lib');
const fs = require('fs');

async function fillForm(inputPath, outputPath, data) {
  const pdfDoc = await PDFDocument.load(fs.readFileSync(inputPath));
  const form = pdfDoc.getForm();

  // Fill text fields
  if (data.name) form.getTextField('name').setText(data.name);
  if (data.email) form.getTextField('email').setText(data.email);
  if (data.address) form.getTextField('address').setText(data.address);

  // Check/uncheck checkboxes
  if (data.agreeTerms) form.getCheckBox('agreeTerms').check();
  else form.getCheckBox('agreeTerms').uncheck();

  // Select dropdown option
  if (data.country) form.getDropdown('country').select(data.country);

  // Select radio button
  if (data.gender) form.getRadioGroup('gender').select(data.gender);

  // Flatten (make non-editable)
  if (data.flatten) form.flatten();

  const pdfBytes = await pdfDoc.save();
  fs.writeFileSync(outputPath, pdfBytes);
  console.log(`Filled form saved to ${outputPath}`);
}

// Usage
fillForm('template.pdf', 'filled.pdf', {
  name: 'Jane Doe',
  email: 'jane@example.com',
  country: 'United States',
  gender: 'female',
  agreeTerms: true,
  flatten: true,
});
```

---

## Creating a Form from Scratch

```js
const { PDFDocument, StandardFonts, rgb, PDFName, PDFString } = require('pdf-lib');
const fs = require('fs');

async function createForm(outputPath) {
  const pdfDoc = await PDFDocument.create();
  const page = pdfDoc.addPage([595, 842]);  // A4
  const font = await pdfDoc.embedFont(StandardFonts.Helvetica);
  const boldFont = await pdfDoc.embedFont(StandardFonts.HelveticaBold);
  const form = pdfDoc.getForm();

  const BLUE = rgb(0.12, 0.31, 0.47);
  const GRAY = rgb(0.4, 0.4, 0.4);
  const { height } = page.getSize();

  // Title
  page.drawText('Registration Form', { x: 50, y: height - 60, size: 22, font: boldFont, color: BLUE });
  page.drawLine({ start: { x: 50, y: height - 70 }, end: { x: 545, y: height - 70 }, thickness: 1.5, color: BLUE });

  // Helper: add labeled text field
  function addTextField(label, fieldName, x, y, w, h = 20, multiline = false) {
    page.drawText(label, { x, y: y + h + 4, size: 10, font, color: GRAY });
    const field = form.createTextField(fieldName);
    field.setText('');
    field.addToPage(page, { x, y, width: w, height: h,
      borderColor: rgb(0.6, 0.6, 0.6), backgroundColor: rgb(0.98, 0.98, 0.98),
      textColor: rgb(0, 0, 0), fontSize: 10,
    });
    if (multiline) field.enableMultiline();
    return field;
  }

  // Helper: add checkbox
  function addCheckBox(label, fieldName, x, y) {
    page.drawText(label, { x: x + 16, y: y + 2, size: 10, font, color: GRAY });
    const cb = form.createCheckBox(fieldName);
    cb.addToPage(page, { x, y, width: 12, height: 12, borderColor: rgb(0.4, 0.4, 0.4) });
    return cb;
  }

  // Helper: add dropdown
  function addDropdown(label, fieldName, options, x, y, w) {
    page.drawText(label, { x, y: y + 24, size: 10, font, color: GRAY });
    const dd = form.createDropdown(fieldName);
    dd.addOptions(options);
    dd.addToPage(page, { x, y, width: w, height: 20,
      borderColor: rgb(0.6, 0.6, 0.6), backgroundColor: rgb(0.98, 0.98, 0.98),
      textColor: rgb(0, 0, 0), fontSize: 10,
    });
    return dd;
  }

  // Personal info section
  page.drawText('Personal Information', { x: 50, y: height - 100, size: 12, font: boldFont, color: BLUE });
  addTextField('First Name',    'firstName',    50,  height - 145, 230);
  addTextField('Last Name',     'lastName',     315, height - 145, 230);
  addTextField('Email Address', 'email',        50,  height - 200, 495);
  addTextField('Phone Number',  'phone',        50,  height - 255, 230);
  addTextField('Date of Birth', 'dob',          315, height - 255, 230);

  // Address section
  page.drawText('Address', { x: 50, y: height - 290, size: 12, font: boldFont, color: BLUE });
  addTextField('Street Address', 'street',  50, height - 335, 495);
  addTextField('City',           'city',    50, height - 390, 230);
  addTextField('State/Province', 'state',   315, height - 390, 100);
  addTextField('Postal Code',    'zip',     430, height - 390, 115);
  addDropdown('Country', 'country',
    ['United States','Canada','United Kingdom','Australia','Other'],
    50, height - 445, 230
  );

  // Preferences
  page.drawText('Preferences', { x: 50, y: height - 480, size: 12, font: boldFont, color: BLUE });
  addCheckBox('Subscribe to newsletter',  'newsletter', 50,  height - 510);
  addCheckBox('Receive SMS notifications','smsAlerts',  50,  height - 530);
  addCheckBox('I agree to terms of service', 'agreeTerms', 50, height - 560);
  addTextField('Additional Comments', 'comments', 50, height - 640, 495, 60, true);

  const pdfBytes = await pdfDoc.save();
  fs.writeFileSync(outputPath, pdfBytes);
  console.log(`Form PDF created: ${outputPath}`);
}

createForm('registration-form.pdf');
```

---

## Form Field Types Reference

### PDFTextField

```js
const field = form.getTextField('fieldName');
field.getText()              // get current value
field.setText('value')       // set value
field.setMaxLength(100)      // max characters
field.setAlignment(TextAlignment.Left) // alignment
field.enableMultiline()      // allow newlines
field.disableMultiline()
field.enablePassword()       // mask input
field.enableReadOnly()       // non-editable
field.setFontSize(12)
```

### PDFCheckBox

```js
const cb = form.getCheckBox('fieldName');
cb.check()
cb.uncheck()
cb.isChecked()         // boolean
cb.enableReadOnly()
```

### PDFDropdown

```js
const dd = form.getDropdown('fieldName');
dd.getOptions()           // string[]
dd.addOptions(['a','b'])
dd.setOptions(['x','y'])
dd.select('x')
dd.getSelected()          // string[]
dd.clear()
dd.enableMultiselect()
dd.enableEditing()        // allow typing custom value
```

### PDFRadioGroup

```js
const rg = form.getRadioGroup('fieldName');
rg.getOptions()           // string[]
rg.select('option1')
rg.getSelected()          // string | undefined
rg.clear()
```

### PDFOptionList

```js
const ol = form.getOptionList('fieldName');
ol.getOptions()
ol.setOptions(['a','b','c'])
ol.select('a')
ol.getSelected()          // string[]
ol.enableMultiselect()
```

### PDFSignature

```js
const sig = form.getSignature('fieldName');
// Signature fields are read-only in pdf-lib
sig.acroField.getRect()   // position
```

---

## Flattening a Form

Flattening converts form fields into static content (non-editable):

```js
const form = pdfDoc.getForm();
form.flatten();  // all fields become permanent PDF content
// OR flatten specific fields:
form.flattenFields([form.getTextField('name'), form.getCheckBox('agree')]);
```

---

## Form Validation Pattern

```js
async function validateAndFill(pdfPath, data) {
  const pdfDoc = await PDFDocument.load(fs.readFileSync(pdfPath));
  const form = pdfDoc.getForm();
  const errors = [];

  // Validate required fields exist
  const requiredFields = ['name', 'email', 'phone'];
  for (const name of requiredFields) {
    try {
      form.getTextField(name);
    } catch {
      errors.push(`Missing field: ${name}`);
    }
  }

  if (errors.length > 0) throw new Error(`Form validation failed:\n${errors.join('\n')}`);

  // Fill fields
  for (const [key, value] of Object.entries(data)) {
    try {
      const field = form.getField(key);
      const type = field.constructor.name;
      if (type === 'PDFTextField') field.setText(String(value));
      else if (type === 'PDFCheckBox') value ? field.check() : field.uncheck();
      else if (type === 'PDFDropdown') field.select(String(value));
    } catch (e) {
      console.warn(`Could not fill field "${key}": ${e.message}`);
    }
  }

  return await pdfDoc.save();
}
```

---

## Tips

- Use `form.getFields()` to discover all field names in an unknown PDF.
- `form.flatten()` is irreversible — save a copy before flattening.
- Radio buttons share a group name; use `getRadioGroup('groupName')`.
- Form fields are positioned in **points** with origin at **bottom-left**.
- For complex form creation, create the template in Adobe Acrobat, then fill with pdf-lib.
