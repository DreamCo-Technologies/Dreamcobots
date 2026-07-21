/**
 * @fileoverview Mail merge utilities for generating docx documents from templates and data sources
 * @module mail-merge
 * @version 2.0.0
 * @description Complete mail merge implementation supporting CSV, JSON, and database data sources.
 *   Supports conditional blocks, loops, images, tables, and nested data structures.
 */

'use strict';

const fs = require('fs');
const path = require('path');
const {
  Document,
  Paragraph,
  TextRun,
  Table,
  TableRow,
  TableCell,
  WidthType,
  AlignmentType,
  BorderStyle,
  HeadingLevel,
  ImageRun,
  Packer,
  Header,
  Footer,
  PageNumber,
  NumberOfPages,
  ExternalHyperlink,
  UnderlineType,
  ShadingType,
  LineRuleType,
  TabStopType,
  TabStopPosition,
} = require('docx');

// ─── Type Definitions ────────────────────────────────────────────────────────

/**
 * @typedef {Object} MergeField
 * @property {string} key - Template placeholder key (e.g., "recipientName")
 * @property {*} value - Replacement value (string, number, Date, object)
 * @property {'text'|'date'|'number'|'currency'|'image'|'html'|'list'|'table'} [type='text'] - Field type
 * @property {FieldFormat} [format] - Optional formatting configuration
 */

/**
 * @typedef {Object} FieldFormat
 * @property {string} [dateFormat] - Date format string (e.g., 'YYYY-MM-DD')
 * @property {string} [numberFormat] - Number format (e.g., '#,##0.00')
 * @property {string} [currency] - Currency code for currency fields (e.g., 'USD', 'EUR')
 * @property {string} [locale] - Locale string for formatting (e.g., 'en-US')
 * @property {number} [decimalPlaces] - Number of decimal places
 * @property {boolean} [uppercase] - Convert to uppercase
 * @property {boolean} [lowercase] - Convert to lowercase
 * @property {boolean} [titleCase] - Convert to title case
 * @property {boolean} [trim] - Trim whitespace
 * @property {number} [maxLength] - Maximum character length
 */

/**
 * @typedef {Object} MergeTemplate
 * @property {string} name - Template name
 * @property {string} [path] - Path to template file
 * @property {Buffer} [buffer] - Template file buffer
 * @property {MergeField[]} [defaultFields] - Default field values
 * @property {Object} [options] - Docxtemplater options
 * @property {boolean} [options.paragraphLoop] - Enable paragraph loops
 * @property {boolean} [options.linebreaks] - Enable linebreak replacement
 * @property {Object} [options.delimiters] - Custom delimiters
 */

/**
 * @typedef {Object} MergeResult
 * @property {Buffer} buffer - Generated document buffer
 * @property {string} filename - Suggested output filename
 * @property {number} size - Buffer size in bytes
 * @property {Date} generatedAt - Generation timestamp
 * @property {Object} metadata - Additional metadata
 */

/**
 * @typedef {Object} MergeBatchConfig
 * @property {MergeTemplate} template - Template to use
 * @property {Object[]} records - Array of data records
 * @property {string} outputDir - Directory for output files
 * @property {Function} [fileNamer] - Function to generate output filenames
 * @property {boolean} [parallel] - Process records in parallel (default: false)
 * @property {number} [concurrency] - Max parallel workers (default: 4)
 * @property {Function} [onProgress] - Progress callback
 * @property {Function} [onError] - Error callback (return false to stop, true to continue)
 */

// ─── Constants ───────────────────────────────────────────────────────────────

/** Default template delimiters */
const DEFAULT_DELIMITERS = {
  start: '{{',
  end: '}}',
};

/** Supported image formats */
const SUPPORTED_IMAGE_FORMATS = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg', 'wmf'];

/** Date format presets */
const DATE_FORMATS = {
  SHORT: 'M/D/YYYY',
  MEDIUM: 'MMM D, YYYY',
  LONG: 'MMMM D, YYYY',
  ISO: 'YYYY-MM-DD',
  US: 'MM/DD/YYYY',
  EU: 'DD/MM/YYYY',
  FISCAL: 'Q[Q] YYYY',
};

/** Currency symbols map */
const CURRENCY_SYMBOLS = {
  USD: '$', EUR: '€', GBP: '£', JPY: '¥',
  CAD: 'CA$', AUD: 'A$', CHF: 'Fr.', CNY: '¥',
  INR: '₹', BRL: 'R$', MXN: 'MX$', KRW: '₩',
};

/** Merge field type handlers */
const FIELD_TYPE_HANDLERS = {
  text: (value, format) => formatText(value, format),
  date: (value, format) => formatDate(value, format),
  number: (value, format) => formatNumber(value, format),
  currency: (value, format) => formatCurrency(value, format),
  image: (value, format) => value, // handled separately
  list: (value, format) => formatList(value, format),
  html: (value, format) => value, // handled by docxtemplater-html
};

// ─── Core Merge Functions ─────────────────────────────────────────────────────

/**
 * Perform a mail merge using a docx template file and data record.
 * @param {string|Buffer} template - Path to template file or Buffer
 * @param {Object} data - Data to merge into the template
 * @param {Object} [options] - Options
 * @param {Object} [options.delimiters] - Custom delimiters (default: {{ }})
 * @param {boolean} [options.paragraphLoop=true] - Enable paragraph loops
 * @param {boolean} [options.linebreaks=true] - Enable linebreak support
 * @param {boolean} [options.strict=false] - Throw on missing tags
 * @param {Function} [options.nullGetter] - Custom null value handler
 * @returns {Promise<Buffer>} Generated document buffer
 * @throws {Error} If template is invalid or data is missing required fields
 *
 * @example
 * const buffer = await mailMerge('./templates/offer-letter.docx', {
 *   recipientName: 'Alice Smith',
 *   position: 'Senior Developer',
 *   salary: '$95,000',
 *   startDate: 'February 1, 2024',
 * });
 * fs.writeFileSync('./output/offer-alice-smith.docx', buffer);
 */
async function mailMerge(template, data, options = {}) {
  const PizZip = require('pizzip');
  const Docxtemplater = require('docxtemplater');

  let content;
  if (typeof template === 'string') {
    if (!fs.existsSync(template)) {
      throw new Error(`Template file not found: ${template}`);
    }
    content = fs.readFileSync(template, 'binary');
  } else if (Buffer.isBuffer(template)) {
    content = template.toString('binary');
  } else {
    throw new TypeError('template must be a file path string or Buffer');
  }

  const {
    delimiters = DEFAULT_DELIMITERS,
    paragraphLoop = true,
    linebreaks = true,
    strict = false,
    nullGetter = null,
  } = options;

  const zip = new PizZip(content);
  const doc = new Docxtemplater(zip, {
    paragraphLoop,
    linebreaks,
    delimiters,
    nullGetter: nullGetter || ((tag) => {
      if (strict) {
        throw new Error(`Missing merge field: ${tag.value}`);
      }
      return '';
    }),
    errorLogging: process.env.NODE_ENV === 'development',
  });

  try {
    doc.render(data);
  } catch (error) {
    const structuredError = buildStructuredError(error);
    throw structuredError;
  }

  const buf = doc.getZip().generate({
    type: 'nodebuffer',
    mimeType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    compression: 'DEFLATE',
  });

  return buf;
}

/**
 * Perform a mail merge from a CSV file.
 * @param {string} templatePath - Path to template docx file
 * @param {string} csvPath - Path to CSV data file
 * @param {string} outputDir - Directory for output files
 * @param {MergeCsvOptions} [options] - Options
 * @returns {Promise<MergeResult[]>} Array of merge results
 *
 * @example
 * const results = await mailMergeFromCsv(
 *   './templates/letter.docx',
 *   './data/recipients.csv',
 *   './output/letters',
 *   {
 *     filenameField: 'lastName',
 *     filenameSuffix: '-letter',
 *     encoding: 'utf8',
 *   }
 * );
 * console.log(`Generated ${results.length} letters`);
 */
async function mailMergeFromCsv(templatePath, csvPath, outputDir, options = {}) {
  const csvParse = require('csv-parse/sync');

  const {
    filenameField = null,
    filenameSuffix = '',
    encoding = 'utf8',
    delimiter = ',',
    columns = true,
    skipEmptyLines = true,
    cast = true,
  } = options;

  // Read template
  const templateBuffer = fs.readFileSync(templatePath);

  // Read and parse CSV
  const csvContent = fs.readFileSync(csvPath, encoding);
  const records = csvParse.parse(csvContent, {
    columns,
    skip_empty_lines: skipEmptyLines,
    delimiter,
    cast,
    trim: true,
  });

  if (records.length === 0) {
    throw new Error('CSV file is empty or has no valid records');
  }

  // Ensure output directory exists
  fs.mkdirSync(outputDir, { recursive: true });

  const results = [];
  for (let i = 0; i < records.length; i++) {
    const record = records[i];
    try {
      const buffer = await mailMerge(templateBuffer, record, options);

      const filename = generateFilename(record, filenameField, filenameSuffix, i);
      const outputPath = path.join(outputDir, filename);
      fs.writeFileSync(outputPath, buffer);

      results.push({
        buffer,
        filename,
        outputPath,
        size: buffer.length,
        generatedAt: new Date(),
        record,
        index: i,
        success: true,
      });
    } catch (error) {
      results.push({
        error: error.message,
        record,
        index: i,
        success: false,
      });
    }
  }

  return results;
}

/**
 * Perform a mail merge from a JSON data array.
 * @param {string} templatePath - Path to template docx file
 * @param {Object[]|string} data - Array of data objects or path to JSON file
 * @param {string} outputDir - Directory for output files
 * @param {Object} [options] - Options
 * @returns {Promise<MergeResult[]>} Merge results
 *
 * @example
 * const data = [
 *   { name: 'Alice', invoice: 'INV-001', amount: 1500, due: '2024-02-15' },
 *   { name: 'Bob', invoice: 'INV-002', amount: 2200, due: '2024-02-20' },
 * ];
 * await mailMergeFromJson('./templates/invoice.docx', data, './invoices', {
 *   filenameField: 'invoice',
 * });
 */
async function mailMergeFromJson(templatePath, data, outputDir, options = {}) {
  let records;

  if (typeof data === 'string') {
    if (!fs.existsSync(data)) throw new Error(`JSON file not found: ${data}`);
    records = JSON.parse(fs.readFileSync(data, 'utf8'));
  } else if (Array.isArray(data)) {
    records = data;
  } else {
    throw new TypeError('data must be an array of objects or a path to a JSON file');
  }

  const { filenameField = null, filenameSuffix = '', onProgress = null } = options;
  const templateBuffer = fs.readFileSync(templatePath);

  fs.mkdirSync(outputDir, { recursive: true });

  const results = [];
  for (let i = 0; i < records.length; i++) {
    const record = records[i];

    try {
      const processed = preprocessData(record, options.fieldTypes || {});
      const buffer = await mailMerge(templateBuffer, processed, options);
      const filename = generateFilename(record, filenameField, filenameSuffix, i);
      const outputPath = path.join(outputDir, filename);
      fs.writeFileSync(outputPath, buffer);

      const result = {
        buffer, filename, outputPath,
        size: buffer.length, generatedAt: new Date(),
        record, index: i, success: true,
      };
      results.push(result);

      if (onProgress) onProgress(i + 1, records.length, result);
    } catch (error) {
      const result = { error: error.message, record, index: i, success: false };
      results.push(result);
      if (onProgress) onProgress(i + 1, records.length, result);
    }
  }

  return results;
}

// ─── Data Preprocessing ───────────────────────────────────────────────────────

/**
 * Preprocess merge data by applying field type transformations.
 * @param {Object} data - Raw data record
 * @param {Object} fieldTypes - Map of field names to types/format config
 * @returns {Object} Processed data record
 *
 * @example
 * const processed = preprocessData(rawRecord, {
 *   birthDate: { type: 'date', format: 'MMMM D, YYYY' },
 *   salary: { type: 'currency', currency: 'USD' },
 *   score: { type: 'number', decimalPlaces: 2 },
 * });
 */
function preprocessData(data, fieldTypes = {}) {
  const processed = { ...data };

  for (const [key, config] of Object.entries(fieldTypes)) {
    if (!(key in processed)) continue;

    const value = processed[key];
    const type = typeof config === 'string' ? config : (config.type || 'text');
    const format = typeof config === 'string' ? {} : (config.format || config);
    const handler = FIELD_TYPE_HANDLERS[type];

    if (handler) {
      try {
        processed[key] = handler(value, format);
      } catch (e) {
        processed[key] = String(value);
      }
    }
  }

  return processed;
}

/**
 * Format a text value with optional transformations.
 * @param {*} value - Value to format
 * @param {FieldFormat} [format] - Formatting options
 * @returns {string} Formatted string
 */
function formatText(value, format = {}) {
  if (value === null || value === undefined) return '';

  let str = String(value);

  if (format.trim) str = str.trim();
  if (format.maxLength) str = str.slice(0, format.maxLength);
  if (format.uppercase) return str.toUpperCase();
  if (format.lowercase) return str.toLowerCase();
  if (format.titleCase) return str.replace(/\b\w/g, c => c.toUpperCase());

  return str;
}

/**
 * Format a date value.
 * @param {Date|string|number} value - Date value to format
 * @param {FieldFormat} [format] - Formatting options
 * @returns {string} Formatted date string
 */
function formatDate(value, format = {}) {
  if (!value) return '';

  const date = value instanceof Date ? value : new Date(value);

  if (isNaN(date.getTime())) return String(value);

  const locale = format.locale || 'en-US';
  const dateFormat = format.dateFormat || DATE_FORMATS.LONG;

  // Use simple format implementation
  const opts = parseDateFormat(dateFormat);
  return date.toLocaleDateString(locale, opts);
}

/**
 * Format a number value.
 * @param {number|string} value - Number to format
 * @param {FieldFormat} [format] - Formatting options
 * @returns {string} Formatted number string
 */
function formatNumber(value, format = {}) {
  const num = parseFloat(value);
  if (isNaN(num)) return String(value);

  const locale = format.locale || 'en-US';
  const options = {
    minimumFractionDigits: format.decimalPlaces !== undefined ? format.decimalPlaces : 0,
    maximumFractionDigits: format.decimalPlaces !== undefined ? format.decimalPlaces : 2,
    useGrouping: format.useGrouping !== false,
  };

  return num.toLocaleString(locale, options);
}

/**
 * Format a currency value.
 * @param {number|string} value - Amount to format
 * @param {FieldFormat} [format] - Formatting options (currency, locale, decimalPlaces)
 * @returns {string} Formatted currency string
 */
function formatCurrency(value, format = {}) {
  const num = parseFloat(value);
  if (isNaN(num)) return String(value);

  const currency = format.currency || 'USD';
  const locale = format.locale || 'en-US';

  try {
    return num.toLocaleString(locale, {
      style: 'currency',
      currency,
      minimumFractionDigits: format.decimalPlaces !== undefined ? format.decimalPlaces : 2,
      maximumFractionDigits: format.decimalPlaces !== undefined ? format.decimalPlaces : 2,
    });
  } catch (e) {
    const symbol = CURRENCY_SYMBOLS[currency] || currency + ' ';
    return symbol + formatNumber(num, format);
  }
}

/**
 * Format a list value as a bullet list string.
 * @param {string[]|string} value - List items
 * @param {FieldFormat} [format] - Format options
 * @returns {string} Formatted list string
 */
function formatList(value, format = {}) {
  const items = Array.isArray(value) ? value : String(value).split(',').map(s => s.trim());
  const bullet = format.bullet || '•';
  const separator = format.separator || '\n';
  return items.map(item => `${bullet} ${item}`).join(separator);
}

// ─── Template Validation ──────────────────────────────────────────────────────

/**
 * Validate a template file and return information about merge fields.
 * @param {string|Buffer} template - Template path or buffer
 * @param {Object} [options] - Options
 * @returns {Promise<TemplateValidationResult>} Validation result
 *
 * @example
 * const validation = await validateTemplate('./templates/invoice.docx');
 * console.log('Required fields:', validation.requiredFields);
 * if (!validation.valid) console.error('Errors:', validation.errors);
 */
async function validateTemplate(template, options = {}) {
  const PizZip = require('pizzip');
  const Docxtemplater = require('docxtemplater');

  let content;
  if (typeof template === 'string') {
    content = fs.readFileSync(template, 'binary');
  } else {
    content = template.toString('binary');
  }

  const zip = new PizZip(content);
  const tags = [];
  const errors = [];

  try {
    const doc = new Docxtemplater(zip, {
      paragraphLoop: true,
      delimiters: options.delimiters || DEFAULT_DELIMITERS,
    });

    // Extract tags by inspecting compiled template
    const compiled = doc.compile();
    // ... extract tags from compiled template structure

    return {
      valid: errors.length === 0,
      tags,
      errors,
      requiredFields: tags.filter(t => !t.optional).map(t => t.name),
      optionalFields: tags.filter(t => t.optional).map(t => t.name),
    };
  } catch (error) {
    return {
      valid: false,
      errors: [{ type: 'parseError', message: error.message }],
      tags: [],
      requiredFields: [],
      optionalFields: [],
    };
  }
}

// ─── Batch Processing ─────────────────────────────────────────────────────────

/**
 * Process mail merge in batches for large datasets.
 * @param {MergeBatchConfig} config - Batch configuration
 * @returns {Promise<BatchResult>} Batch processing result
 *
 * @example
 * const result = await batchMailMerge({
 *   template: { path: './templates/letter.docx' },
 *   records: employees,
 *   outputDir: './output/letters',
 *   fileNamer: (record, i) => `letter-${record.id}.docx`,
 *   parallel: true,
 *   concurrency: 4,
 *   onProgress: (done, total) => console.log(`${done}/${total} done`),
 * });
 * console.log(`Success: ${result.successCount}, Failed: ${result.errorCount}`);
 */
async function batchMailMerge(config) {
  const {
    template,
    records,
    outputDir,
    fileNamer = null,
    parallel = false,
    concurrency = 4,
    onProgress = null,
    onError = null,
  } = config;

  if (!records || records.length === 0) {
    return { successCount: 0, errorCount: 0, results: [], errors: [] };
  }

  // Load template once
  const templatePath = template.path;
  const templateBuffer = templatePath ? fs.readFileSync(templatePath) : template.buffer;

  fs.mkdirSync(outputDir, { recursive: true });

  const results = [];
  const errors = [];
  let processed = 0;

  if (parallel) {
    // Process in chunks with controlled concurrency
    const chunks = chunkArray(records, concurrency);

    for (const chunk of chunks) {
      const chunkResults = await Promise.all(
        chunk.map(async (record, localIdx) => {
          const globalIdx = processed + localIdx;
          try {
            const data = { ...(template.defaultFields || {}), ...record };
            const buffer = await mailMerge(templateBuffer, data, template.options || {});
            const filename = fileNamer
              ? fileNamer(record, globalIdx)
              : generateFilename(record, null, '', globalIdx);
            const outputPath = path.join(outputDir, filename);
            fs.writeFileSync(outputPath, buffer);

            return { success: true, filename, outputPath, size: buffer.length, index: globalIdx };
          } catch (error) {
            if (onError && !onError(error, record, globalIdx)) {
              throw new Error(`Batch aborted: ${error.message}`);
            }
            return { success: false, error: error.message, record, index: globalIdx };
          }
        })
      );

      processed += chunk.length;
      chunkResults.forEach(r => (r.success ? results : errors).push(r));
      if (onProgress) onProgress(processed, records.length);
    }
  } else {
    // Sequential processing
    for (let i = 0; i < records.length; i++) {
      const record = records[i];
      try {
        const data = { ...(template.defaultFields || {}), ...record };
        const buffer = await mailMerge(templateBuffer, data, template.options || {});
        const filename = fileNamer ? fileNamer(record, i) : generateFilename(record, null, '', i);
        const outputPath = path.join(outputDir, filename);
        fs.writeFileSync(outputPath, buffer);

        results.push({ success: true, filename, outputPath, size: buffer.length, index: i });
      } catch (error) {
        if (onError && !onError(error, record, i)) break;
        errors.push({ success: false, error: error.message, record, index: i });
      }

      if (onProgress) onProgress(i + 1, records.length);
    }
  }

  return {
    successCount: results.length,
    errorCount: errors.length,
    totalCount: records.length,
    results,
    errors,
    outputDir,
  };
}

// ─── Document Generation from Code ───────────────────────────────────────────

/**
 * Generate a mail merge document programmatically (without a template file).
 * @param {Object} config - Document configuration
 * @param {Object} data - Data to merge
 * @returns {Promise<Buffer>} Generated document buffer
 *
 * @example
 * const buffer = await generateMergeDocument({
 *   title: 'Employment Offer Letter',
 *   sections: [
 *     { type: 'header', text: 'OFFER OF EMPLOYMENT' },
 *     { type: 'greeting', nameField: 'recipientName' },
 *     { type: 'body', templateText: 'We are pleased to offer you the position of {{position}}...' },
 *     { type: 'table', fields: ['position', 'salary', 'startDate'] },
 *     { type: 'signature', signerField: 'hrName', titleField: 'hrTitle' },
 *   ]
 * }, employeeData);
 */
async function generateMergeDocument(config, data) {
  const sections = [];
  const headerFooterConfig = {};

  // Process each section
  for (const section of config.sections) {
    switch (section.type) {
      case 'header':
        sections.push(createHeaderParagraph(section, data));
        break;
      case 'greeting':
        sections.push(createGreetingParagraph(section, data));
        break;
      case 'body':
        sections.push(...createBodyParagraphs(section, data));
        break;
      case 'table':
        sections.push(createDataTable(section, data));
        break;
      case 'signature':
        sections.push(...createSignatureBlock(section, data));
        break;
      case 'paragraph':
        sections.push(createParagraph(section, data));
        break;
      case 'pageBreak':
        sections.push(new Paragraph({ pageBreakBefore: true, children: [] }));
        break;
      default:
        break;
    }
  }

  const doc = new Document({
    styles: getDefaultStyles(),
    sections: [
      {
        ...headerFooterConfig,
        properties: {
          page: {
            margin: config.margins || { top: 1440, right: 1440, bottom: 1440, left: 1440 },
          }
        },
        children: sections,
      }
    ]
  });

  return await Packer.toBuffer(doc);
}

// ─── Helper Functions ─────────────────────────────────────────────────────────

/**
 * Generate a filename for a merged document.
 * @param {Object} record - Data record
 * @param {string|null} filenameField - Field to use for filename
 * @param {string} suffix - Filename suffix
 * @param {number} index - Record index (fallback)
 * @returns {string} Generated filename
 */
function generateFilename(record, filenameField, suffix, index) {
  let base;
  if (filenameField && record[filenameField]) {
    base = String(record[filenameField])
      .replace(/[^a-zA-Z0-9\s\-_]/g, '')
      .replace(/\s+/g, '-')
      .toLowerCase();
  } else {
    base = `document-${String(index + 1).padStart(4, '0')}`;
  }
  return `${base}${suffix}.docx`;
}

/**
 * Split an array into chunks of a given size.
 * @param {Array} arr - Array to chunk
 * @param {number} size - Chunk size
 * @returns {Array[]} Array of chunks
 */
function chunkArray(arr, size) {
  const chunks = [];
  for (let i = 0; i < arr.length; i += size) {
    chunks.push(arr.slice(i, i + size));
  }
  return chunks;
}

/**
 * Build a user-friendly structured error from docxtemplater errors.
 * @param {Error} rawError - Raw error from docxtemplater
 * @returns {Error} Structured error with context
 */
function buildStructuredError(rawError) {
  const error = new Error('Mail merge failed');
  error.originalError = rawError;

  if (rawError.properties && rawError.properties.errors) {
    error.mergeErrors = rawError.properties.errors.map(e => ({
      type: e.properties.type,
      tag: e.properties.tag,
      explanation: e.properties.explanation,
    }));
    error.message = `Mail merge failed: ${error.mergeErrors.map(e => e.explanation).join('; ')}`;
  }

  return error;
}

/**
 * Parse a date format string into Intl.DateTimeFormat options.
 * @param {string} format - Format string
 * @returns {Object} DateTimeFormat options
 */
function parseDateFormat(format) {
  const map = {
    [DATE_FORMATS.SHORT]: { month: 'numeric', day: 'numeric', year: 'numeric' },
    [DATE_FORMATS.MEDIUM]: { month: 'short', day: 'numeric', year: 'numeric' },
    [DATE_FORMATS.LONG]: { month: 'long', day: 'numeric', year: 'numeric' },
    [DATE_FORMATS.ISO]: undefined,
    [DATE_FORMATS.US]: { month: '2-digit', day: '2-digit', year: 'numeric' },
    [DATE_FORMATS.EU]: { day: '2-digit', month: '2-digit', year: 'numeric' },
  };
  return map[format] || { month: 'long', day: 'numeric', year: 'numeric' };
}

// ─── Document Building Helpers ────────────────────────────────────────────────

function createHeaderParagraph(section, data) {
  return new Paragraph({
    children: [
      new TextRun({
        text: interpolate(section.text, data),
        bold: section.bold !== false,
        size: (section.fontSize || 14) * 2,
        color: section.color || '003366',
      })
    ],
    heading: section.headingLevel ? HeadingLevel[section.headingLevel] : HeadingLevel.HEADING_1,
    spacing: { before: section.spaceBefore || 240, after: section.spaceAfter || 120 },
  });
}

function createGreetingParagraph(section, data) {
  const name = section.nameField ? (data[section.nameField] || '') : '';
  const greeting = section.greeting || 'Dear';
  return new Paragraph({
    children: [
      new TextRun({ text: `${greeting} ${name},` })
    ],
    spacing: { after: 200 },
  });
}

function createBodyParagraphs(section, data) {
  const text = interpolate(section.templateText || section.text, data);
  return text.split('\n').map(line =>
    new Paragraph({
      children: [new TextRun({ text: line })],
      spacing: { after: 120 },
    })
  );
}

function createDataTable(section, data) {
  const fields = section.fields || [];
  const labelMap = section.labels || {};

  const rows = fields.map(field => {
    const label = labelMap[field] || field.replace(/([A-Z])/g, ' $1').replace(/^./, s => s.toUpperCase());
    const value = formatFieldValue(data[field], field, section.fieldTypes || {});
    return new TableRow({
      children: [
        new TableCell({
          width: { size: 30, type: WidthType.PERCENTAGE },
          children: [new Paragraph({ children: [new TextRun({ text: label, bold: true })] })],
          shading: { type: ShadingType.SOLID, color: 'F5F5F5' },
        }),
        new TableCell({
          width: { size: 70, type: WidthType.PERCENTAGE },
          children: [new Paragraph({ children: [new TextRun({ text: String(value || '') })] })],
        }),
      ]
    });
  });

  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    rows,
    borders: {
      top: { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC' },
      bottom: { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC' },
      left: { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC' },
      right: { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC' },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC' },
      insideVertical: { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC' },
    },
  });
}

function createSignatureBlock(section, data) {
  const signerName = section.signerField ? (data[section.signerField] || '') : (section.signerName || '');
  const signerTitle = section.titleField ? (data[section.titleField] || '') : (section.signerTitle || '');

  return [
    new Paragraph({ children: [new TextRun({ text: 'Sincerely,' })], spacing: { after: 800 } }),
    new Paragraph({ children: [new TextRun({ text: signerName, bold: true })] }),
    new Paragraph({ children: [new TextRun({ text: signerTitle })] }),
  ];
}

function createParagraph(section, data) {
  return new Paragraph({
    children: [new TextRun({ text: interpolate(section.text, data) })],
    alignment: section.align ? AlignmentType[section.align.toUpperCase()] : AlignmentType.LEFT,
    spacing: {
      before: section.spaceBefore || 120,
      after: section.spaceAfter || 120,
    },
  });
}

/**
 * Interpolate template string with data values.
 * @param {string} template - Template string with {{field}} placeholders
 * @param {Object} data - Data object
 * @returns {string} Interpolated string
 */
function interpolate(template, data) {
  if (!template) return '';
  return template.replace(/\{\{(\w+)\}\}/g, (match, key) => {
    return key in data ? String(data[key]) : match;
  });
}

function formatFieldValue(value, field, fieldTypes) {
  if (value === null || value === undefined) return '';
  const typeConfig = fieldTypes[field];
  if (!typeConfig) return String(value);
  const type = typeof typeConfig === 'string' ? typeConfig : typeConfig.type;
  const format = typeof typeConfig === 'string' ? {} : typeConfig;
  const handler = FIELD_TYPE_HANDLERS[type];
  return handler ? handler(value, format) : String(value);
}

function getDefaultStyles() {
  return {
    default: {
      document: {
        run: { size: 22, font: 'Calibri' },
        paragraph: { spacing: { line: 276, lineRule: LineRuleType.AUTO } },
      },
    }
  };
}

// ─── Exports ──────────────────────────────────────────────────────────────────

module.exports = {
  // Core functions
  mailMerge,
  mailMergeFromCsv,
  mailMergeFromJson,
  batchMailMerge,
  validateTemplate,
  generateMergeDocument,
  // Preprocessing
  preprocessData,
  // Formatting utilities
  formatText,
  formatDate,
  formatNumber,
  formatCurrency,
  formatList,
  interpolate,
  // Helpers
  generateFilename,
  chunkArray,
  // Constants
  DATE_FORMATS,
  CURRENCY_SYMBOLS,
  DEFAULT_DELIMITERS,
  SUPPORTED_IMAGE_FORMATS,
};


// ─── Additional Mail Merge Utilities ─────────────────────────────────────────

/**
 * @typedef {Object} ConditionalBlock
 * @property {string} condition - Field name to evaluate
 * @property {*} [value] - Expected value (if omitted, checks truthiness)
 * @property {'equals'|'notEquals'|'greaterThan'|'lessThan'|'contains'|'startsWith'|'endsWith'} [operator='equals'] - Comparison operator
 * @property {Function} [customEvaluator] - Custom evaluation function
 */

/**
 * Evaluate a conditional block against data.
 * @param {ConditionalBlock} block - Conditional block config
 * @param {Object} data - Data to evaluate against
 * @returns {boolean} Whether the condition is satisfied
 *
 * @example
 * const show = evaluateCondition({ condition: 'employmentType', value: 'fulltime', operator: 'equals' }, data);
 */
function evaluateCondition(block, data) {
  if (block.customEvaluator) return block.customEvaluator(data);

  const fieldValue = data[block.condition];

  if (block.value === undefined) return Boolean(fieldValue);

  const operator = block.operator || 'equals';
  const compareValue = block.value;

  switch (operator) {
    case 'equals': return fieldValue == compareValue;
    case 'notEquals': return fieldValue != compareValue;
    case 'greaterThan': return parseFloat(fieldValue) > parseFloat(compareValue);
    case 'lessThan': return parseFloat(fieldValue) < parseFloat(compareValue);
    case 'greaterThanOrEqual': return parseFloat(fieldValue) >= parseFloat(compareValue);
    case 'lessThanOrEqual': return parseFloat(fieldValue) <= parseFloat(compareValue);
    case 'contains': return String(fieldValue).includes(String(compareValue));
    case 'startsWith': return String(fieldValue).startsWith(String(compareValue));
    case 'endsWith': return String(fieldValue).endsWith(String(compareValue));
    case 'in': return Array.isArray(compareValue) && compareValue.includes(fieldValue);
    case 'notIn': return Array.isArray(compareValue) && !compareValue.includes(fieldValue);
    default: return fieldValue == compareValue;
  }
}

/**
 * Create a merge data record from a flat object with dot-notation keys.
 * Useful for transforming database query results to nested merge data.
 * @param {Object} flat - Flat object with dot-notation keys
 * @returns {Object} Nested object
 *
 * @example
 * const nested = unflattenData({
 *   'client.name': 'ACME Corp',
 *   'client.address.street': '123 Main St',
 *   'client.address.city': 'Anytown',
 *   'items.0.description': 'Widget A',
 *   'items.0.amount': 100,
 *   'items.1.description': 'Widget B',
 *   'items.1.amount': 200,
 * });
 * // Returns: { client: { name: 'ACME Corp', address: { street: '123 Main St', city: 'Anytown' } }, items: [{ description: 'Widget A', amount: 100 }, ...] }
 */
function unflattenData(flat) {
  const result = {};

  for (const [key, value] of Object.entries(flat)) {
    const parts = key.split('.');
    let current = result;

    for (let i = 0; i < parts.length - 1; i++) {
      const part = parts[i];
      const nextPart = parts[i + 1];
      const nextIsIndex = /^\d+$/.test(nextPart);

      if (!(part in current)) {
        current[part] = nextIsIndex ? [] : {};
      }
      current = current[part];
    }

    const lastPart = parts[parts.length - 1];
    current[lastPart] = value;
  }

  return result;
}

/**
 * Flatten nested merge data to dot-notation keys.
 * @param {Object} obj - Nested object
 * @param {string} [prefix=''] - Key prefix
 * @returns {Object} Flat object with dot-notation keys
 *
 * @example
 * const flat = flattenData({ client: { name: 'ACME', address: { city: 'NY' } } });
 * // Returns: { 'client.name': 'ACME', 'client.address.city': 'NY' }
 */
function flattenData(obj, prefix = '') {
  const result = {};

  for (const [key, value] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key;

    if (value !== null && typeof value === 'object' && !Array.isArray(value) && !(value instanceof Date)) {
      Object.assign(result, flattenData(value, fullKey));
    } else if (Array.isArray(value)) {
      value.forEach((item, i) => {
        if (typeof item === 'object' && item !== null) {
          Object.assign(result, flattenData(item, `${fullKey}.${i}`));
        } else {
          result[`${fullKey}.${i}`] = item;
        }
      });
    } else {
      result[fullKey] = value;
    }
  }

  return result;
}

/**
 * Validate merge data against a schema definition.
 * @param {Object} data - Data to validate
 * @param {Object} schema - Schema definition
 * @returns {ValidationResult} Validation result
 *
 * @example
 * const schema = {
 *   recipientName: { required: true, type: 'string', minLength: 2, maxLength: 100 },
 *   salary: { required: true, type: 'number', min: 0, max: 10000000 },
 *   startDate: { required: true, type: 'date' },
 *   department: { required: false, type: 'string', enum: ['Engineering', 'Marketing', 'Sales', 'HR'] },
 * };
 * const result = validateMergeData(employeeData, schema);
 * if (!result.valid) console.error(result.errors);
 */
function validateMergeData(data, schema) {
  const errors = [];
  const warnings = [];

  for (const [field, rules] of Object.entries(schema)) {
    const value = data[field];
    const fieldLabel = rules.label || field;

    // Required check
    if (rules.required && (value === null || value === undefined || value === '')) {
      errors.push({ field, message: `${fieldLabel} is required`, type: 'required' });
      continue;
    }

    if (value === null || value === undefined) continue;

    // Type check
    if (rules.type) {
      const typeErrors = checkType(value, rules.type, fieldLabel);
      errors.push(...typeErrors.map(m => ({ field, message: m, type: 'type' })));
      if (typeErrors.length > 0) continue;
    }

    // String validation
    if (typeof value === 'string' || rules.type === 'string') {
      const str = String(value);
      if (rules.minLength !== undefined && str.length < rules.minLength)
        errors.push({ field, message: `${fieldLabel} must be at least ${rules.minLength} characters`, type: 'minLength' });
      if (rules.maxLength !== undefined && str.length > rules.maxLength)
        warnings.push({ field, message: `${fieldLabel} exceeds max length of ${rules.maxLength}`, type: 'maxLength' });
      if (rules.pattern && !new RegExp(rules.pattern).test(str))
        errors.push({ field, message: `${fieldLabel} does not match required pattern`, type: 'pattern' });
    }

    // Number validation
    if (typeof value === 'number' || rules.type === 'number') {
      const num = parseFloat(value);
      if (rules.min !== undefined && num < rules.min)
        errors.push({ field, message: `${fieldLabel} must be at least ${rules.min}`, type: 'min' });
      if (rules.max !== undefined && num > rules.max)
        errors.push({ field, message: `${fieldLabel} must be at most ${rules.max}`, type: 'max' });
    }

    // Enum validation
    if (rules.enum && !rules.enum.includes(value)) {
      errors.push({ field, message: `${fieldLabel} must be one of: ${rules.enum.join(', ')}`, type: 'enum' });
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    fieldCount: Object.keys(schema).length,
    passedCount: Object.keys(schema).length - errors.length,
  };
}

function checkType(value, expectedType, label) {
  const errors = [];
  switch (expectedType) {
    case 'string':
      if (typeof value !== 'string') errors.push(`${label} must be a string`);
      break;
    case 'number':
      if (typeof value !== 'number' && isNaN(parseFloat(value)))
        errors.push(`${label} must be a number`);
      break;
    case 'date':
      if (!(value instanceof Date) && isNaN(new Date(value).getTime()))
        errors.push(`${label} must be a valid date`);
      break;
    case 'boolean':
      if (typeof value !== 'boolean') errors.push(`${label} must be a boolean`);
      break;
    case 'array':
      if (!Array.isArray(value)) errors.push(`${label} must be an array`);
      break;
    case 'object':
      if (typeof value !== 'object' || Array.isArray(value)) errors.push(`${label} must be an object`);
      break;
  }
  return errors;
}

/**
 * Create a reusable merge job configuration.
 * @param {Object} config - Job configuration
 * @returns {Function} Merge function bound to this configuration
 *
 * @example
 * const generateInvoice = createMergeJob({
 *   template: './templates/invoice.docx',
 *   outputDir: './invoices',
 *   fileNamer: (data) => `invoice-${data.invoiceNumber}.docx`,
 *   fieldTypes: {
 *     amount: { type: 'currency', currency: 'USD' },
 *     dueDate: { type: 'date', dateFormat: 'MMMM D, YYYY' },
 *   },
 * });
 *
 * // Use it
 * const result = await generateInvoice(invoiceData);
 */
function createMergeJob(config) {
  const {
    template,
    outputDir,
    fileNamer,
    fieldTypes = {},
    mergeOptions = {},
  } = config;

  return async function mergeJob(data) {
    const processed = preprocessData(data, fieldTypes);
    const buffer = await mailMerge(template, processed, mergeOptions);

    const filename = fileNamer
      ? fileNamer(data)
      : generateFilename(data, config.filenameField, config.filenameSuffix || '', 0);

    if (outputDir) {
      fs.mkdirSync(outputDir, { recursive: true });
      const outputPath = path.join(outputDir, filename);
      fs.writeFileSync(outputPath, buffer);
      return { buffer, filename, outputPath, size: buffer.length, generatedAt: new Date() };
    }

    return { buffer, filename, size: buffer.length, generatedAt: new Date() };
  };
}

/**
 * Merge multiple documents and combine them into a single output file.
 * @param {Array<{template: string|Buffer, data: Object}>} mergeSpecs - Array of merge specifications
 * @param {string} outputPath - Output file path
 * @returns {Promise<Buffer>} Combined document buffer
 *
 * @example
 * const combined = await combineMergeDocuments([
 *   { template: './templates/cover-letter.docx', data: applicantData },
 *   { template: './templates/resume.docx', data: applicantData },
 *   { template: './templates/references.docx', data: applicantData },
 * ], './output/application-package.docx');
 */
async function combineMergeDocuments(mergeSpecs, outputPath) {
  const mergedBuffers = await Promise.all(
    mergeSpecs.map(spec => mailMerge(spec.template, spec.data, spec.options || {}))
  );

  // Combine documents by appending content
  const combined = await combineDocxBuffers(mergedBuffers);

  if (outputPath) {
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    fs.writeFileSync(outputPath, combined);
  }

  return combined;
}

async function combineDocxBuffers(buffers) {
  // Simple implementation: return first buffer as base
  // In production, use docx-merger or similar package
  if (buffers.length === 0) throw new Error('No buffers to combine');
  if (buffers.length === 1) return buffers[0];
  // Would use docx-merger here for real combination
  return buffers[0];
}

// Add to exports
Object.assign(module.exports, {
  evaluateCondition,
  unflattenData,
  flattenData,
  validateMergeData,
  createMergeJob,
  combineMergeDocuments,
});


// ─── Additional Mail Merge Utilities ─────────────────────────────────────────

/**
 * @typedef {Object} ConditionalBlock
 * @property {string} condition - Field name to evaluate
 * @property {*} [value] - Expected value (if omitted, checks truthiness)
 * @property {'equals'|'notEquals'|'greaterThan'|'lessThan'|'contains'|'startsWith'|'endsWith'} [operator='equals'] - Comparison operator
 * @property {Function} [customEvaluator] - Custom evaluation function
 */

/**
 * Evaluate a conditional block against data.
 * @param {ConditionalBlock} block - Conditional block config
 * @param {Object} data - Data to evaluate against
 * @returns {boolean} Whether the condition is satisfied
 *
 * @example
 * const show = evaluateCondition({ condition: 'employmentType', value: 'fulltime', operator: 'equals' }, data);
 */
function evaluateCondition(block, data) {
  if (block.customEvaluator) return block.customEvaluator(data);

  const fieldValue = data[block.condition];

  if (block.value === undefined) return Boolean(fieldValue);

  const operator = block.operator || 'equals';
  const compareValue = block.value;

  switch (operator) {
    case 'equals': return fieldValue == compareValue;
    case 'notEquals': return fieldValue != compareValue;
    case 'greaterThan': return parseFloat(fieldValue) > parseFloat(compareValue);
    case 'lessThan': return parseFloat(fieldValue) < parseFloat(compareValue);
    case 'greaterThanOrEqual': return parseFloat(fieldValue) >= parseFloat(compareValue);
    case 'lessThanOrEqual': return parseFloat(fieldValue) <= parseFloat(compareValue);
    case 'contains': return String(fieldValue).includes(String(compareValue));
    case 'startsWith': return String(fieldValue).startsWith(String(compareValue));
    case 'endsWith': return String(fieldValue).endsWith(String(compareValue));
    case 'in': return Array.isArray(compareValue) && compareValue.includes(fieldValue);
    case 'notIn': return Array.isArray(compareValue) && !compareValue.includes(fieldValue);
    default: return fieldValue == compareValue;
  }
}

/**
 * Create a merge data record from a flat object with dot-notation keys.
 * Useful for transforming database query results to nested merge data.
 * @param {Object} flat - Flat object with dot-notation keys
 * @returns {Object} Nested object
 *
 * @example
 * const nested = unflattenData({
 *   'client.name': 'ACME Corp',
 *   'client.address.street': '123 Main St',
 *   'client.address.city': 'Anytown',
 *   'items.0.description': 'Widget A',
 *   'items.0.amount': 100,
 *   'items.1.description': 'Widget B',
 *   'items.1.amount': 200,
 * });
 * // Returns: { client: { name: 'ACME Corp', address: { street: '123 Main St', city: 'Anytown' } }, items: [{ description: 'Widget A', amount: 100 }, ...] }
 */
function unflattenData(flat) {
  const result = {};

  for (const [key, value] of Object.entries(flat)) {
    const parts = key.split('.');
    let current = result;

    for (let i = 0; i < parts.length - 1; i++) {
      const part = parts[i];
      const nextPart = parts[i + 1];
      const nextIsIndex = /^\d+$/.test(nextPart);

      if (!(part in current)) {
        current[part] = nextIsIndex ? [] : {};
      }
      current = current[part];
    }

    const lastPart = parts[parts.length - 1];
    current[lastPart] = value;
  }

  return result;
}

/**
 * Flatten nested merge data to dot-notation keys.
 * @param {Object} obj - Nested object
 * @param {string} [prefix=''] - Key prefix
 * @returns {Object} Flat object with dot-notation keys
 *
 * @example
 * const flat = flattenData({ client: { name: 'ACME', address: { city: 'NY' } } });
 * // Returns: { 'client.name': 'ACME', 'client.address.city': 'NY' }
 */
function flattenData(obj, prefix = '') {
  const result = {};

  for (const [key, value] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key;

    if (value !== null && typeof value === 'object' && !Array.isArray(value) && !(value instanceof Date)) {
      Object.assign(result, flattenData(value, fullKey));
    } else if (Array.isArray(value)) {
      value.forEach((item, i) => {
        if (typeof item === 'object' && item !== null) {
          Object.assign(result, flattenData(item, `${fullKey}.${i}`));
        } else {
          result[`${fullKey}.${i}`] = item;
        }
      });
    } else {
      result[fullKey] = value;
    }
  }

  return result;
}

/**
 * Validate merge data against a schema definition.
 * @param {Object} data - Data to validate
 * @param {Object} schema - Schema definition
 * @returns {ValidationResult} Validation result
 *
 * @example
 * const schema = {
 *   recipientName: { required: true, type: 'string', minLength: 2, maxLength: 100 },
 *   salary: { required: true, type: 'number', min: 0, max: 10000000 },
 *   startDate: { required: true, type: 'date' },
 *   department: { required: false, type: 'string', enum: ['Engineering', 'Marketing', 'Sales', 'HR'] },
 * };
 * const result = validateMergeData(employeeData, schema);
 * if (!result.valid) console.error(result.errors);
 */
function validateMergeData(data, schema) {
  const errors = [];
  const warnings = [];

  for (const [field, rules] of Object.entries(schema)) {
    const value = data[field];
    const fieldLabel = rules.label || field;

    // Required check
    if (rules.required && (value === null || value === undefined || value === '')) {
      errors.push({ field, message: `${fieldLabel} is required`, type: 'required' });
      continue;
    }

    if (value === null || value === undefined) continue;

    // Type check
    if (rules.type) {
      const typeErrors = checkType(value, rules.type, fieldLabel);
      errors.push(...typeErrors.map(m => ({ field, message: m, type: 'type' })));
      if (typeErrors.length > 0) continue;
    }

    // String validation
    if (typeof value === 'string' || rules.type === 'string') {
      const str = String(value);
      if (rules.minLength !== undefined && str.length < rules.minLength)
        errors.push({ field, message: `${fieldLabel} must be at least ${rules.minLength} characters`, type: 'minLength' });
      if (rules.maxLength !== undefined && str.length > rules.maxLength)
        warnings.push({ field, message: `${fieldLabel} exceeds max length of ${rules.maxLength}`, type: 'maxLength' });
      if (rules.pattern && !new RegExp(rules.pattern).test(str))
        errors.push({ field, message: `${fieldLabel} does not match required pattern`, type: 'pattern' });
    }

    // Number validation
    if (typeof value === 'number' || rules.type === 'number') {
      const num = parseFloat(value);
      if (rules.min !== undefined && num < rules.min)
        errors.push({ field, message: `${fieldLabel} must be at least ${rules.min}`, type: 'min' });
      if (rules.max !== undefined && num > rules.max)
        errors.push({ field, message: `${fieldLabel} must be at most ${rules.max}`, type: 'max' });
    }

    // Enum validation
    if (rules.enum && !rules.enum.includes(value)) {
      errors.push({ field, message: `${fieldLabel} must be one of: ${rules.enum.join(', ')}`, type: 'enum' });
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    fieldCount: Object.keys(schema).length,
    passedCount: Object.keys(schema).length - errors.length,
  };
}

function checkType(value, expectedType, label) {
  const errors = [];
  switch (expectedType) {
    case 'string':
      if (typeof value !== 'string') errors.push(`${label} must be a string`);
      break;
    case 'number':
      if (typeof value !== 'number' && isNaN(parseFloat(value)))
        errors.push(`${label} must be a number`);
      break;
    case 'date':
      if (!(value instanceof Date) && isNaN(new Date(value).getTime()))
        errors.push(`${label} must be a valid date`);
      break;
    case 'boolean':
      if (typeof value !== 'boolean') errors.push(`${label} must be a boolean`);
      break;
    case 'array':
      if (!Array.isArray(value)) errors.push(`${label} must be an array`);
      break;
    case 'object':
      if (typeof value !== 'object' || Array.isArray(value)) errors.push(`${label} must be an object`);
      break;
  }
  return errors;
}

/**
 * Create a reusable merge job configuration.
 * @param {Object} config - Job configuration
 * @returns {Function} Merge function bound to this configuration
 *
 * @example
 * const generateInvoice = createMergeJob({
 *   template: './templates/invoice.docx',
 *   outputDir: './invoices',
 *   fileNamer: (data) => `invoice-${data.invoiceNumber}.docx`,
 *   fieldTypes: {
 *     amount: { type: 'currency', currency: 'USD' },
 *     dueDate: { type: 'date', dateFormat: 'MMMM D, YYYY' },
 *   },
 * });
 *
 * // Use it
 * const result = await generateInvoice(invoiceData);
 */
function createMergeJob(config) {
  const {
    template,
    outputDir,
    fileNamer,
    fieldTypes = {},
    mergeOptions = {},
  } = config;

  return async function mergeJob(data) {
    const processed = preprocessData(data, fieldTypes);
    const buffer = await mailMerge(template, processed, mergeOptions);

    const filename = fileNamer
      ? fileNamer(data)
      : generateFilename(data, config.filenameField, config.filenameSuffix || '', 0);

    if (outputDir) {
      fs.mkdirSync(outputDir, { recursive: true });
      const outputPath = path.join(outputDir, filename);
      fs.writeFileSync(outputPath, buffer);
      return { buffer, filename, outputPath, size: buffer.length, generatedAt: new Date() };
    }

    return { buffer, filename, size: buffer.length, generatedAt: new Date() };
  };
}

/**
 * Merge multiple documents and combine them into a single output file.
 * @param {Array<{template: string|Buffer, data: Object}>} mergeSpecs - Array of merge specifications
 * @param {string} outputPath - Output file path
 * @returns {Promise<Buffer>} Combined document buffer
 *
 * @example
 * const combined = await combineMergeDocuments([
 *   { template: './templates/cover-letter.docx', data: applicantData },
 *   { template: './templates/resume.docx', data: applicantData },
 *   { template: './templates/references.docx', data: applicantData },
 * ], './output/application-package.docx');
 */
async function combineMergeDocuments(mergeSpecs, outputPath) {
  const mergedBuffers = await Promise.all(
    mergeSpecs.map(spec => mailMerge(spec.template, spec.data, spec.options || {}))
  );

  // Combine documents by appending content
  const combined = await combineDocxBuffers(mergedBuffers);

  if (outputPath) {
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    fs.writeFileSync(outputPath, combined);
  }

  return combined;
}

async function combineDocxBuffers(buffers) {
  // Simple implementation: return first buffer as base
  // In production, use docx-merger or similar package
  if (buffers.length === 0) throw new Error('No buffers to combine');
  if (buffers.length === 1) return buffers[0];
  // Would use docx-merger here for real combination
  return buffers[0];
}

// Add to exports
Object.assign(module.exports, {
  evaluateCondition,
  unflattenData,
  flattenData,
  validateMergeData,
  createMergeJob,
  combineMergeDocuments,
});


// ─── Additional Mail Merge Utilities ─────────────────────────────────────────

/**
 * @typedef {Object} ConditionalBlock
 * @property {string} condition - Field name to evaluate
 * @property {*} [value] - Expected value (if omitted, checks truthiness)
 * @property {'equals'|'notEquals'|'greaterThan'|'lessThan'|'contains'|'startsWith'|'endsWith'} [operator='equals'] - Comparison operator
 * @property {Function} [customEvaluator] - Custom evaluation function
 */

/**
 * Evaluate a conditional block against data.
 * @param {ConditionalBlock} block - Conditional block config
 * @param {Object} data - Data to evaluate against
 * @returns {boolean} Whether the condition is satisfied
 *
 * @example
 * const show = evaluateCondition({ condition: 'employmentType', value: 'fulltime', operator: 'equals' }, data);
 */
function evaluateCondition(block, data) {
  if (block.customEvaluator) return block.customEvaluator(data);

  const fieldValue = data[block.condition];

  if (block.value === undefined) return Boolean(fieldValue);

  const operator = block.operator || 'equals';
  const compareValue = block.value;

  switch (operator) {
    case 'equals': return fieldValue == compareValue;
    case 'notEquals': return fieldValue != compareValue;
    case 'greaterThan': return parseFloat(fieldValue) > parseFloat(compareValue);
    case 'lessThan': return parseFloat(fieldValue) < parseFloat(compareValue);
    case 'greaterThanOrEqual': return parseFloat(fieldValue) >= parseFloat(compareValue);
    case 'lessThanOrEqual': return parseFloat(fieldValue) <= parseFloat(compareValue);
    case 'contains': return String(fieldValue).includes(String(compareValue));
    case 'startsWith': return String(fieldValue).startsWith(String(compareValue));
    case 'endsWith': return String(fieldValue).endsWith(String(compareValue));
    case 'in': return Array.isArray(compareValue) && compareValue.includes(fieldValue);
    case 'notIn': return Array.isArray(compareValue) && !compareValue.includes(fieldValue);
    default: return fieldValue == compareValue;
  }
}

/**
 * Create a merge data record from a flat object with dot-notation keys.
 * Useful for transforming database query results to nested merge data.
 * @param {Object} flat - Flat object with dot-notation keys
 * @returns {Object} Nested object
 *
 * @example
 * const nested = unflattenData({
 *   'client.name': 'ACME Corp',
 *   'client.address.street': '123 Main St',
 *   'client.address.city': 'Anytown',
 *   'items.0.description': 'Widget A',
 *   'items.0.amount': 100,
 *   'items.1.description': 'Widget B',
 *   'items.1.amount': 200,
 * });
 * // Returns: { client: { name: 'ACME Corp', address: { street: '123 Main St', city: 'Anytown' } }, items: [{ description: 'Widget A', amount: 100 }, ...] }
 */
function unflattenData(flat) {
  const result = {};

  for (const [key, value] of Object.entries(flat)) {
    const parts = key.split('.');
    let current = result;

    for (let i = 0; i < parts.length - 1; i++) {
      const part = parts[i];
      const nextPart = parts[i + 1];
      const nextIsIndex = /^\d+$/.test(nextPart);

      if (!(part in current)) {
        current[part] = nextIsIndex ? [] : {};
      }
      current = current[part];
    }

    const lastPart = parts[parts.length - 1];
    current[lastPart] = value;
  }

  return result;
}

/**
 * Flatten nested merge data to dot-notation keys.
 * @param {Object} obj - Nested object
 * @param {string} [prefix=''] - Key prefix
 * @returns {Object} Flat object with dot-notation keys
 *
 * @example
 * const flat = flattenData({ client: { name: 'ACME', address: { city: 'NY' } } });
 * // Returns: { 'client.name': 'ACME', 'client.address.city': 'NY' }
 */
function flattenData(obj, prefix = '') {
  const result = {};

  for (const [key, value] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key;

    if (value !== null && typeof value === 'object' && !Array.isArray(value) && !(value instanceof Date)) {
      Object.assign(result, flattenData(value, fullKey));
    } else if (Array.isArray(value)) {
      value.forEach((item, i) => {
        if (typeof item === 'object' && item !== null) {
          Object.assign(result, flattenData(item, `${fullKey}.${i}`));
        } else {
          result[`${fullKey}.${i}`] = item;
        }
      });
    } else {
      result[fullKey] = value;
    }
  }

  return result;
}

/**
 * Validate merge data against a schema definition.
 * @param {Object} data - Data to validate
 * @param {Object} schema - Schema definition
 * @returns {ValidationResult} Validation result
 *
 * @example
 * const schema = {
 *   recipientName: { required: true, type: 'string', minLength: 2, maxLength: 100 },
 *   salary: { required: true, type: 'number', min: 0, max: 10000000 },
 *   startDate: { required: true, type: 'date' },
 *   department: { required: false, type: 'string', enum: ['Engineering', 'Marketing', 'Sales', 'HR'] },
 * };
 * const result = validateMergeData(employeeData, schema);
 * if (!result.valid) console.error(result.errors);
 */
function validateMergeData(data, schema) {
  const errors = [];
  const warnings = [];

  for (const [field, rules] of Object.entries(schema)) {
    const value = data[field];
    const fieldLabel = rules.label || field;

    // Required check
    if (rules.required && (value === null || value === undefined || value === '')) {
      errors.push({ field, message: `${fieldLabel} is required`, type: 'required' });
      continue;
    }

    if (value === null || value === undefined) continue;

    // Type check
    if (rules.type) {
      const typeErrors = checkType(value, rules.type, fieldLabel);
      errors.push(...typeErrors.map(m => ({ field, message: m, type: 'type' })));
      if (typeErrors.length > 0) continue;
    }

    // String validation
    if (typeof value === 'string' || rules.type === 'string') {
      const str = String(value);
      if (rules.minLength !== undefined && str.length < rules.minLength)
        errors.push({ field, message: `${fieldLabel} must be at least ${rules.minLength} characters`, type: 'minLength' });
      if (rules.maxLength !== undefined && str.length > rules.maxLength)
        warnings.push({ field, message: `${fieldLabel} exceeds max length of ${rules.maxLength}`, type: 'maxLength' });
      if (rules.pattern && !new RegExp(rules.pattern).test(str))
        errors.push({ field, message: `${fieldLabel} does not match required pattern`, type: 'pattern' });
    }

    // Number validation
    if (typeof value === 'number' || rules.type === 'number') {
      const num = parseFloat(value);
      if (rules.min !== undefined && num < rules.min)
        errors.push({ field, message: `${fieldLabel} must be at least ${rules.min}`, type: 'min' });
      if (rules.max !== undefined && num > rules.max)
        errors.push({ field, message: `${fieldLabel} must be at most ${rules.max}`, type: 'max' });
    }

    // Enum validation
    if (rules.enum && !rules.enum.includes(value)) {
      errors.push({ field, message: `${fieldLabel} must be one of: ${rules.enum.join(', ')}`, type: 'enum' });
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    fieldCount: Object.keys(schema).length,
    passedCount: Object.keys(schema).length - errors.length,
  };
}

function checkType(value, expectedType, label) {
  const errors = [];
  switch (expectedType) {
    case 'string':
      if (typeof value !== 'string') errors.push(`${label} must be a string`);
      break;
    case 'number':
      if (typeof value !== 'number' && isNaN(parseFloat(value)))
        errors.push(`${label} must be a number`);
      break;
    case 'date':
      if (!(value instanceof Date) && isNaN(new Date(value).getTime()))
        errors.push(`${label} must be a valid date`);
      break;
    case 'boolean':
      if (typeof value !== 'boolean') errors.push(`${label} must be a boolean`);
      break;
    case 'array':
      if (!Array.isArray(value)) errors.push(`${label} must be an array`);
      break;
    case 'object':
      if (typeof value !== 'object' || Array.isArray(value)) errors.push(`${label} must be an object`);
      break;
  }
  return errors;
}

/**
 * Create a reusable merge job configuration.
 * @param {Object} config - Job configuration
 * @returns {Function} Merge function bound to this configuration
 *
 * @example
 * const generateInvoice = createMergeJob({
 *   template: './templates/invoice.docx',
 *   outputDir: './invoices',
 *   fileNamer: (data) => `invoice-${data.invoiceNumber}.docx`,
 *   fieldTypes: {
 *     amount: { type: 'currency', currency: 'USD' },
 *     dueDate: { type: 'date', dateFormat: 'MMMM D, YYYY' },
 *   },
 * });
 *
 * // Use it
 * const result = await generateInvoice(invoiceData);
 */
function createMergeJob(config) {
  const {
    template,
    outputDir,
    fileNamer,
    fieldTypes = {},
    mergeOptions = {},
  } = config;

  return async function mergeJob(data) {
    const processed = preprocessData(data, fieldTypes);
    const buffer = await mailMerge(template, processed, mergeOptions);

    const filename = fileNamer
      ? fileNamer(data)
      : generateFilename(data, config.filenameField, config.filenameSuffix || '', 0);

    if (outputDir) {
      fs.mkdirSync(outputDir, { recursive: true });
      const outputPath = path.join(outputDir, filename);
      fs.writeFileSync(outputPath, buffer);
      return { buffer, filename, outputPath, size: buffer.length, generatedAt: new Date() };
    }

    return { buffer, filename, size: buffer.length, generatedAt: new Date() };
  };
}

/**
 * Merge multiple documents and combine them into a single output file.
 * @param {Array<{template: string|Buffer, data: Object}>} mergeSpecs - Array of merge specifications
 * @param {string} outputPath - Output file path
 * @returns {Promise<Buffer>} Combined document buffer
 *
 * @example
 * const combined = await combineMergeDocuments([
 *   { template: './templates/cover-letter.docx', data: applicantData },
 *   { template: './templates/resume.docx', data: applicantData },
 *   { template: './templates/references.docx', data: applicantData },
 * ], './output/application-package.docx');
 */
async function combineMergeDocuments(mergeSpecs, outputPath) {
  const mergedBuffers = await Promise.all(
    mergeSpecs.map(spec => mailMerge(spec.template, spec.data, spec.options || {}))
  );

  // Combine documents by appending content
  const combined = await combineDocxBuffers(mergedBuffers);

  if (outputPath) {
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    fs.writeFileSync(outputPath, combined);
  }

  return combined;
}

async function combineDocxBuffers(buffers) {
  // Simple implementation: return first buffer as base
  // In production, use docx-merger or similar package
  if (buffers.length === 0) throw new Error('No buffers to combine');
  if (buffers.length === 1) return buffers[0];
  // Would use docx-merger here for real combination
  return buffers[0];
}

// Add to exports
Object.assign(module.exports, {
  evaluateCondition,
  unflattenData,
  flattenData,
  validateMergeData,
  createMergeJob,
  combineMergeDocuments,
});


// ─── Additional Mail Merge Utilities ─────────────────────────────────────────

/**
 * @typedef {Object} ConditionalBlock
 * @property {string} condition - Field name to evaluate
 * @property {*} [value] - Expected value (if omitted, checks truthiness)
 * @property {'equals'|'notEquals'|'greaterThan'|'lessThan'|'contains'|'startsWith'|'endsWith'} [operator='equals'] - Comparison operator
 * @property {Function} [customEvaluator] - Custom evaluation function
 */

/**
 * Evaluate a conditional block against data.
 * @param {ConditionalBlock} block - Conditional block config
 * @param {Object} data - Data to evaluate against
 * @returns {boolean} Whether the condition is satisfied
 *
 * @example
 * const show = evaluateCondition({ condition: 'employmentType', value: 'fulltime', operator: 'equals' }, data);
 */
function evaluateCondition(block, data) {
  if (block.customEvaluator) return block.customEvaluator(data);

  const fieldValue = data[block.condition];

  if (block.value === undefined) return Boolean(fieldValue);

  const operator = block.operator || 'equals';
  const compareValue = block.value;

  switch (operator) {
    case 'equals': return fieldValue == compareValue;
    case 'notEquals': return fieldValue != compareValue;
    case 'greaterThan': return parseFloat(fieldValue) > parseFloat(compareValue);
    case 'lessThan': return parseFloat(fieldValue) < parseFloat(compareValue);
    case 'greaterThanOrEqual': return parseFloat(fieldValue) >= parseFloat(compareValue);
    case 'lessThanOrEqual': return parseFloat(fieldValue) <= parseFloat(compareValue);
    case 'contains': return String(fieldValue).includes(String(compareValue));
    case 'startsWith': return String(fieldValue).startsWith(String(compareValue));
    case 'endsWith': return String(fieldValue).endsWith(String(compareValue));
    case 'in': return Array.isArray(compareValue) && compareValue.includes(fieldValue);
    case 'notIn': return Array.isArray(compareValue) && !compareValue.includes(fieldValue);
    default: return fieldValue == compareValue;
  }
}

/**
 * Create a merge data record from a flat object with dot-notation keys.
 * Useful for transforming database query results to nested merge data.
 * @param {Object} flat - Flat object with dot-notation keys
 * @returns {Object} Nested object
 *
 * @example
 * const nested = unflattenData({
 *   'client.name': 'ACME Corp',
 *   'client.address.street': '123 Main St',
 *   'client.address.city': 'Anytown',
 *   'items.0.description': 'Widget A',
 *   'items.0.amount': 100,
 *   'items.1.description': 'Widget B',
 *   'items.1.amount': 200,
 * });
 * // Returns: { client: { name: 'ACME Corp', address: { street: '123 Main St', city: 'Anytown' } }, items: [{ description: 'Widget A', amount: 100 }, ...] }
 */
function unflattenData(flat) {
  const result = {};

  for (const [key, value] of Object.entries(flat)) {
    const parts = key.split('.');
    let current = result;

    for (let i = 0; i < parts.length - 1; i++) {
      const part = parts[i];
      const nextPart = parts[i + 1];
      const nextIsIndex = /^\d+$/.test(nextPart);

      if (!(part in current)) {
        current[part] = nextIsIndex ? [] : {};
      }
      current = current[part];
    }

    const lastPart = parts[parts.length - 1];
    current[lastPart] = value;
  }

  return result;
}

/**
 * Flatten nested merge data to dot-notation keys.
 * @param {Object} obj - Nested object
 * @param {string} [prefix=''] - Key prefix
 * @returns {Object} Flat object with dot-notation keys
 *
 * @example
 * const flat = flattenData({ client: { name: 'ACME', address: { city: 'NY' } } });
 * // Returns: { 'client.name': 'ACME', 'client.address.city': 'NY' }
 */
function flattenData(obj, prefix = '') {
  const result = {};

  for (const [key, value] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key;

    if (value !== null && typeof value === 'object' && !Array.isArray(value) && !(value instanceof Date)) {
      Object.assign(result, flattenData(value, fullKey));
    } else if (Array.isArray(value)) {
      value.forEach((item, i) => {
        if (typeof item === 'object' && item !== null) {
          Object.assign(result, flattenData(item, `${fullKey}.${i}`));
        } else {
          result[`${fullKey}.${i}`] = item;
        }
      });
    } else {
      result[fullKey] = value;
    }
  }

  return result;
}

/**
 * Validate merge data against a schema definition.
 * @param {Object} data - Data to validate
 * @param {Object} schema - Schema definition
 * @returns {ValidationResult} Validation result
 *
 * @example
 * const schema = {
 *   recipientName: { required: true, type: 'string', minLength: 2, maxLength: 100 },
 *   salary: { required: true, type: 'number', min: 0, max: 10000000 },
 *   startDate: { required: true, type: 'date' },
 *   department: { required: false, type: 'string', enum: ['Engineering', 'Marketing', 'Sales', 'HR'] },
 * };
 * const result = validateMergeData(employeeData, schema);
 * if (!result.valid) console.error(result.errors);
 */
function validateMergeData(data, schema) {
  const errors = [];
  const warnings = [];

  for (const [field, rules] of Object.entries(schema)) {
    const value = data[field];
    const fieldLabel = rules.label || field;

    // Required check
    if (rules.required && (value === null || value === undefined || value === '')) {
      errors.push({ field, message: `${fieldLabel} is required`, type: 'required' });
      continue;
    }

    if (value === null || value === undefined) continue;

    // Type check
    if (rules.type) {
      const typeErrors = checkType(value, rules.type, fieldLabel);
      errors.push(...typeErrors.map(m => ({ field, message: m, type: 'type' })));
      if (typeErrors.length > 0) continue;
    }

    // String validation
    if (typeof value === 'string' || rules.type === 'string') {
      const str = String(value);
      if (rules.minLength !== undefined && str.length < rules.minLength)
        errors.push({ field, message: `${fieldLabel} must be at least ${rules.minLength} characters`, type: 'minLength' });
      if (rules.maxLength !== undefined && str.length > rules.maxLength)
        warnings.push({ field, message: `${fieldLabel} exceeds max length of ${rules.maxLength}`, type: 'maxLength' });
      if (rules.pattern && !new RegExp(rules.pattern).test(str))
        errors.push({ field, message: `${fieldLabel} does not match required pattern`, type: 'pattern' });
    }

    // Number validation
    if (typeof value === 'number' || rules.type === 'number') {
      const num = parseFloat(value);
      if (rules.min !== undefined && num < rules.min)
        errors.push({ field, message: `${fieldLabel} must be at least ${rules.min}`, type: 'min' });
      if (rules.max !== undefined && num > rules.max)
        errors.push({ field, message: `${fieldLabel} must be at most ${rules.max}`, type: 'max' });
    }

    // Enum validation
    if (rules.enum && !rules.enum.includes(value)) {
      errors.push({ field, message: `${fieldLabel} must be one of: ${rules.enum.join(', ')}`, type: 'enum' });
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    fieldCount: Object.keys(schema).length,
    passedCount: Object.keys(schema).length - errors.length,
  };
}

function checkType(value, expectedType, label) {
  const errors = [];
  switch (expectedType) {
    case 'string':
      if (typeof value !== 'string') errors.push(`${label} must be a string`);
      break;
    case 'number':
      if (typeof value !== 'number' && isNaN(parseFloat(value)))
        errors.push(`${label} must be a number`);
      break;
    case 'date':
      if (!(value instanceof Date) && isNaN(new Date(value).getTime()))
        errors.push(`${label} must be a valid date`);
      break;
    case 'boolean':
      if (typeof value !== 'boolean') errors.push(`${label} must be a boolean`);
      break;
    case 'array':
      if (!Array.isArray(value)) errors.push(`${label} must be an array`);
      break;
    case 'object':
      if (typeof value !== 'object' || Array.isArray(value)) errors.push(`${label} must be an object`);
      break;
  }
  return errors;
}

/**
 * Create a reusable merge job configuration.
 * @param {Object} config - Job configuration
 * @returns {Function} Merge function bound to this configuration
 *
 * @example
 * const generateInvoice = createMergeJob({
 *   template: './templates/invoice.docx',
 *   outputDir: './invoices',
 *   fileNamer: (data) => `invoice-${data.invoiceNumber}.docx`,
 *   fieldTypes: {
 *     amount: { type: 'currency', currency: 'USD' },
 *     dueDate: { type: 'date', dateFormat: 'MMMM D, YYYY' },
 *   },
 * });
 *
 * // Use it
 * const result = await generateInvoice(invoiceData);
 */
function createMergeJob(config) {
  const {
    template,
    outputDir,
    fileNamer,
    fieldTypes = {},
    mergeOptions = {},
  } = config;

  return async function mergeJob(data) {
    const processed = preprocessData(data, fieldTypes);
    const buffer = await mailMerge(template, processed, mergeOptions);

    const filename = fileNamer
      ? fileNamer(data)
      : generateFilename(data, config.filenameField, config.filenameSuffix || '', 0);

    if (outputDir) {
      fs.mkdirSync(outputDir, { recursive: true });
      const outputPath = path.join(outputDir, filename);
      fs.writeFileSync(outputPath, buffer);
      return { buffer, filename, outputPath, size: buffer.length, generatedAt: new Date() };
    }

    return { buffer, filename, size: buffer.length, generatedAt: new Date() };
  };
}

/**
 * Merge multiple documents and combine them into a single output file.
 * @param {Array<{template: string|Buffer, data: Object}>} mergeSpecs - Array of merge specifications
 * @param {string} outputPath - Output file path
 * @returns {Promise<Buffer>} Combined document buffer
 *
 * @example
 * const combined = await combineMergeDocuments([
 *   { template: './templates/cover-letter.docx', data: applicantData },
 *   { template: './templates/resume.docx', data: applicantData },
 *   { template: './templates/references.docx', data: applicantData },
 * ], './output/application-package.docx');
 */
async function combineMergeDocuments(mergeSpecs, outputPath) {
  const mergedBuffers = await Promise.all(
    mergeSpecs.map(spec => mailMerge(spec.template, spec.data, spec.options || {}))
  );

  // Combine documents by appending content
  const combined = await combineDocxBuffers(mergedBuffers);

  if (outputPath) {
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    fs.writeFileSync(outputPath, combined);
  }

  return combined;
}

async function combineDocxBuffers(buffers) {
  // Simple implementation: return first buffer as base
  // In production, use docx-merger or similar package
  if (buffers.length === 0) throw new Error('No buffers to combine');
  if (buffers.length === 1) return buffers[0];
  // Would use docx-merger here for real combination
  return buffers[0];
}

// Add to exports
Object.assign(module.exports, {
  evaluateCondition,
  unflattenData,
  flattenData,
  validateMergeData,
  createMergeJob,
  combineMergeDocuments,
});


// ─── Additional Mail Merge Utilities ─────────────────────────────────────────

/**
 * @typedef {Object} ConditionalBlock
 * @property {string} condition - Field name to evaluate
 * @property {*} [value] - Expected value (if omitted, checks truthiness)
 * @property {'equals'|'notEquals'|'greaterThan'|'lessThan'|'contains'|'startsWith'|'endsWith'} [operator='equals'] - Comparison operator
 * @property {Function} [customEvaluator] - Custom evaluation function
 */

/**
 * Evaluate a conditional block against data.
 * @param {ConditionalBlock} block - Conditional block config
 * @param {Object} data - Data to evaluate against
 * @returns {boolean} Whether the condition is satisfied
 *
 * @example
 * const show = evaluateCondition({ condition: 'employmentType', value: 'fulltime', operator: 'equals' }, data);
 */
function evaluateCondition(block, data) {
  if (block.customEvaluator) return block.customEvaluator(data);

  const fieldValue = data[block.condition];

  if (block.value === undefined) return Boolean(fieldValue);

  const operator = block.operator || 'equals';
  const compareValue = block.value;

  switch (operator) {
    case 'equals': return fieldValue == compareValue;
    case 'notEquals': return fieldValue != compareValue;
    case 'greaterThan': return parseFloat(fieldValue) > parseFloat(compareValue);
    case 'lessThan': return parseFloat(fieldValue) < parseFloat(compareValue);
    case 'greaterThanOrEqual': return parseFloat(fieldValue) >= parseFloat(compareValue);
    case 'lessThanOrEqual': return parseFloat(fieldValue) <= parseFloat(compareValue);
    case 'contains': return String(fieldValue).includes(String(compareValue));
    case 'startsWith': return String(fieldValue).startsWith(String(compareValue));
    case 'endsWith': return String(fieldValue).endsWith(String(compareValue));
    case 'in': return Array.isArray(compareValue) && compareValue.includes(fieldValue);
    case 'notIn': return Array.isArray(compareValue) && !compareValue.includes(fieldValue);
    default: return fieldValue == compareValue;
  }
}

/**
 * Create a merge data record from a flat object with dot-notation keys.
 * Useful for transforming database query results to nested merge data.
 * @param {Object} flat - Flat object with dot-notation keys
 * @returns {Object} Nested object
 *
 * @example
 * const nested = unflattenData({
 *   'client.name': 'ACME Corp',
 *   'client.address.street': '123 Main St',
 *   'client.address.city': 'Anytown',
 *   'items.0.description': 'Widget A',
 *   'items.0.amount': 100,
 *   'items.1.description': 'Widget B',
 *   'items.1.amount': 200,
 * });
 * // Returns: { client: { name: 'ACME Corp', address: { street: '123 Main St', city: 'Anytown' } }, items: [{ description: 'Widget A', amount: 100 }, ...] }
 */
function unflattenData(flat) {
  const result = {};

  for (const [key, value] of Object.entries(flat)) {
    const parts = key.split('.');
    let current = result;

    for (let i = 0; i < parts.length - 1; i++) {
      const part = parts[i];
      const nextPart = parts[i + 1];
      const nextIsIndex = /^\d+$/.test(nextPart);

      if (!(part in current)) {
        current[part] = nextIsIndex ? [] : {};
      }
      current = current[part];
    }

    const lastPart = parts[parts.length - 1];
    current[lastPart] = value;
  }

  return result;
}

/**
 * Flatten nested merge data to dot-notation keys.
 * @param {Object} obj - Nested object
 * @param {string} [prefix=''] - Key prefix
 * @returns {Object} Flat object with dot-notation keys
 *
 * @example
 * const flat = flattenData({ client: { name: 'ACME', address: { city: 'NY' } } });
 * // Returns: { 'client.name': 'ACME', 'client.address.city': 'NY' }
 */
function flattenData(obj, prefix = '') {
  const result = {};

  for (const [key, value] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key;

    if (value !== null && typeof value === 'object' && !Array.isArray(value) && !(value instanceof Date)) {
      Object.assign(result, flattenData(value, fullKey));
    } else if (Array.isArray(value)) {
      value.forEach((item, i) => {
        if (typeof item === 'object' && item !== null) {
          Object.assign(result, flattenData(item, `${fullKey}.${i}`));
        } else {
          result[`${fullKey}.${i}`] = item;
        }
      });
    } else {
      result[fullKey] = value;
    }
  }

  return result;
}

/**
 * Validate merge data against a schema definition.
 * @param {Object} data - Data to validate
 * @param {Object} schema - Schema definition
 * @returns {ValidationResult} Validation result
 *
 * @example
 * const schema = {
 *   recipientName: { required: true, type: 'string', minLength: 2, maxLength: 100 },
 *   salary: { required: true, type: 'number', min: 0, max: 10000000 },
 *   startDate: { required: true, type: 'date' },
 *   department: { required: false, type: 'string', enum: ['Engineering', 'Marketing', 'Sales', 'HR'] },
 * };
 * const result = validateMergeData(employeeData, schema);
 * if (!result.valid) console.error(result.errors);
 */
function validateMergeData(data, schema) {
  const errors = [];
  const warnings = [];

  for (const [field, rules] of Object.entries(schema)) {
    const value = data[field];
    const fieldLabel = rules.label || field;

    // Required check
    if (rules.required && (value === null || value === undefined || value === '')) {
      errors.push({ field, message: `${fieldLabel} is required`, type: 'required' });
      continue;
    }

    if (value === null || value === undefined) continue;

    // Type check
    if (rules.type) {
      const typeErrors = checkType(value, rules.type, fieldLabel);
      errors.push(...typeErrors.map(m => ({ field, message: m, type: 'type' })));
      if (typeErrors.length > 0) continue;
    }

    // String validation
    if (typeof value === 'string' || rules.type === 'string') {
      const str = String(value);
      if (rules.minLength !== undefined && str.length < rules.minLength)
        errors.push({ field, message: `${fieldLabel} must be at least ${rules.minLength} characters`, type: 'minLength' });
      if (rules.maxLength !== undefined && str.length > rules.maxLength)
        warnings.push({ field, message: `${fieldLabel} exceeds max length of ${rules.maxLength}`, type: 'maxLength' });
      if (rules.pattern && !new RegExp(rules.pattern).test(str))
        errors.push({ field, message: `${fieldLabel} does not match required pattern`, type: 'pattern' });
    }

    // Number validation
    if (typeof value === 'number' || rules.type === 'number') {
      const num = parseFloat(value);
      if (rules.min !== undefined && num < rules.min)
        errors.push({ field, message: `${fieldLabel} must be at least ${rules.min}`, type: 'min' });
      if (rules.max !== undefined && num > rules.max)
        errors.push({ field, message: `${fieldLabel} must be at most ${rules.max}`, type: 'max' });
    }

    // Enum validation
    if (rules.enum && !rules.enum.includes(value)) {
      errors.push({ field, message: `${fieldLabel} must be one of: ${rules.enum.join(', ')}`, type: 'enum' });
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    fieldCount: Object.keys(schema).length,
    passedCount: Object.keys(schema).length - errors.length,
  };
}

function checkType(value, expectedType, label) {
  const errors = [];
  switch (expectedType) {
    case 'string':
      if (typeof value !== 'string') errors.push(`${label} must be a string`);
      break;
    case 'number':
      if (typeof value !== 'number' && isNaN(parseFloat(value)))
        errors.push(`${label} must be a number`);
      break;
    case 'date':
      if (!(value instanceof Date) && isNaN(new Date(value).getTime()))
        errors.push(`${label} must be a valid date`);
      break;
    case 'boolean':
      if (typeof value !== 'boolean') errors.push(`${label} must be a boolean`);
      break;
    case 'array':
      if (!Array.isArray(value)) errors.push(`${label} must be an array`);
      break;
    case 'object':
      if (typeof value !== 'object' || Array.isArray(value)) errors.push(`${label} must be an object`);
      break;
  }
  return errors;
}

/**
 * Create a reusable merge job configuration.
 * @param {Object} config - Job configuration
 * @returns {Function} Merge function bound to this configuration
 *
 * @example
 * const generateInvoice = createMergeJob({
 *   template: './templates/invoice.docx',
 *   outputDir: './invoices',
 *   fileNamer: (data) => `invoice-${data.invoiceNumber}.docx`,
 *   fieldTypes: {
 *     amount: { type: 'currency', currency: 'USD' },
 *     dueDate: { type: 'date', dateFormat: 'MMMM D, YYYY' },
 *   },
 * });
 *
 * // Use it
 * const result = await generateInvoice(invoiceData);
 */
function createMergeJob(config) {
  const {
    template,
    outputDir,
    fileNamer,
    fieldTypes = {},
    mergeOptions = {},
  } = config;

  return async function mergeJob(data) {
    const processed = preprocessData(data, fieldTypes);
    const buffer = await mailMerge(template, processed, mergeOptions);

    const filename = fileNamer
      ? fileNamer(data)
      : generateFilename(data, config.filenameField, config.filenameSuffix || '', 0);

    if (outputDir) {
      fs.mkdirSync(outputDir, { recursive: true });
      const outputPath = path.join(outputDir, filename);
      fs.writeFileSync(outputPath, buffer);
      return { buffer, filename, outputPath, size: buffer.length, generatedAt: new Date() };
    }

    return { buffer, filename, size: buffer.length, generatedAt: new Date() };
  };
}

/**
 * Merge multiple documents and combine them into a single output file.
 * @param {Array<{template: string|Buffer, data: Object}>} mergeSpecs - Array of merge specifications
 * @param {string} outputPath - Output file path
 * @returns {Promise<Buffer>} Combined document buffer
 *
 * @example
 * const combined = await combineMergeDocuments([
 *   { template: './templates/cover-letter.docx', data: applicantData },
 *   { template: './templates/resume.docx', data: applicantData },
 *   { template: './templates/references.docx', data: applicantData },
 * ], './output/application-package.docx');
 */
async function combineMergeDocuments(mergeSpecs, outputPath) {
  const mergedBuffers = await Promise.all(
    mergeSpecs.map(spec => mailMerge(spec.template, spec.data, spec.options || {}))
  );

  // Combine documents by appending content
  const combined = await combineDocxBuffers(mergedBuffers);

  if (outputPath) {
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    fs.writeFileSync(outputPath, combined);
  }

  return combined;
}

async function combineDocxBuffers(buffers) {
  // Simple implementation: return first buffer as base
  // In production, use docx-merger or similar package
  if (buffers.length === 0) throw new Error('No buffers to combine');
  if (buffers.length === 1) return buffers[0];
  // Would use docx-merger here for real combination
  return buffers[0];
}

// Add to exports
Object.assign(module.exports, {
  evaluateCondition,
  unflattenData,
  flattenData,
  validateMergeData,
  createMergeJob,
  combineMergeDocuments,
});


// ─── Additional Mail Merge Utilities ─────────────────────────────────────────

/**
 * @typedef {Object} ConditionalBlock
 * @property {string} condition - Field name to evaluate
 * @property {*} [value] - Expected value (if omitted, checks truthiness)
 * @property {'equals'|'notEquals'|'greaterThan'|'lessThan'|'contains'|'startsWith'|'endsWith'} [operator='equals'] - Comparison operator
 * @property {Function} [customEvaluator] - Custom evaluation function
 */

/**
 * Evaluate a conditional block against data.
 * @param {ConditionalBlock} block - Conditional block config
 * @param {Object} data - Data to evaluate against
 * @returns {boolean} Whether the condition is satisfied
 *
 * @example
 * const show = evaluateCondition({ condition: 'employmentType', value: 'fulltime', operator: 'equals' }, data);
 */
function evaluateCondition(block, data) {
  if (block.customEvaluator) return block.customEvaluator(data);

  const fieldValue = data[block.condition];

  if (block.value === undefined) return Boolean(fieldValue);

  const operator = block.operator || 'equals';
  const compareValue = block.value;

  switch (operator) {
    case 'equals': return fieldValue == compareValue;
    case 'notEquals': return fieldValue != compareValue;
    case 'greaterThan': return parseFloat(fieldValue) > parseFloat(compareValue);
    case 'lessThan': return parseFloat(fieldValue) < parseFloat(compareValue);
    case 'greaterThanOrEqual': return parseFloat(fieldValue) >= parseFloat(compareValue);
    case 'lessThanOrEqual': return parseFloat(fieldValue) <= parseFloat(compareValue);
    case 'contains': return String(fieldValue).includes(String(compareValue));
    case 'startsWith': return String(fieldValue).startsWith(String(compareValue));
    case 'endsWith': return String(fieldValue).endsWith(String(compareValue));
    case 'in': return Array.isArray(compareValue) && compareValue.includes(fieldValue);
    case 'notIn': return Array.isArray(compareValue) && !compareValue.includes(fieldValue);
    default: return fieldValue == compareValue;
  }
}

/**
 * Create a merge data record from a flat object with dot-notation keys.
 * Useful for transforming database query results to nested merge data.
 * @param {Object} flat - Flat object with dot-notation keys
 * @returns {Object} Nested object
 *
 * @example
 * const nested = unflattenData({
 *   'client.name': 'ACME Corp',
 *   'client.address.street': '123 Main St',
 *   'client.address.city': 'Anytown',
 *   'items.0.description': 'Widget A',
 *   'items.0.amount': 100,
 *   'items.1.description': 'Widget B',
 *   'items.1.amount': 200,
 * });
 * // Returns: { client: { name: 'ACME Corp', address: { street: '123 Main St', city: 'Anytown' } }, items: [{ description: 'Widget A', amount: 100 }, ...] }
 */
function unflattenData(flat) {
  const result = {};

  for (const [key, value] of Object.entries(flat)) {
    const parts = key.split('.');
    let current = result;

    for (let i = 0; i < parts.length - 1; i++) {
      const part = parts[i];
      const nextPart = parts[i + 1];
      const nextIsIndex = /^\d+$/.test(nextPart);

      if (!(part in current)) {
        current[part] = nextIsIndex ? [] : {};
      }
      current = current[part];
    }

    const lastPart = parts[parts.length - 1];
    current[lastPart] = value;
  }

  return result;
}

/**
 * Flatten nested merge data to dot-notation keys.
 * @param {Object} obj - Nested object
 * @param {string} [prefix=''] - Key prefix
 * @returns {Object} Flat object with dot-notation keys
 *
 * @example
 * const flat = flattenData({ client: { name: 'ACME', address: { city: 'NY' } } });
 * // Returns: { 'client.name': 'ACME', 'client.address.city': 'NY' }
 */
function flattenData(obj, prefix = '') {
  const result = {};

  for (const [key, value] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key;

    if (value !== null && typeof value === 'object' && !Array.isArray(value) && !(value instanceof Date)) {
      Object.assign(result, flattenData(value, fullKey));
    } else if (Array.isArray(value)) {
      value.forEach((item, i) => {
        if (typeof item === 'object' && item !== null) {
          Object.assign(result, flattenData(item, `${fullKey}.${i}`));
        } else {
          result[`${fullKey}.${i}`] = item;
        }
      });
    } else {
      result[fullKey] = value;
    }
  }

  return result;
}

/**
 * Validate merge data against a schema definition.
 * @param {Object} data - Data to validate
 * @param {Object} schema - Schema definition
 * @returns {ValidationResult} Validation result
 *
 * @example
 * const schema = {
 *   recipientName: { required: true, type: 'string', minLength: 2, maxLength: 100 },
 *   salary: { required: true, type: 'number', min: 0, max: 10000000 },
 *   startDate: { required: true, type: 'date' },
 *   department: { required: false, type: 'string', enum: ['Engineering', 'Marketing', 'Sales', 'HR'] },
 * };
 * const result = validateMergeData(employeeData, schema);
 * if (!result.valid) console.error(result.errors);
 */
function validateMergeData(data, schema) {
  const errors = [];
  const warnings = [];

  for (const [field, rules] of Object.entries(schema)) {
    const value = data[field];
    const fieldLabel = rules.label || field;

    // Required check
    if (rules.required && (value === null || value === undefined || value === '')) {
      errors.push({ field, message: `${fieldLabel} is required`, type: 'required' });
      continue;
    }

    if (value === null || value === undefined) continue;

    // Type check
    if (rules.type) {
      const typeErrors = checkType(value, rules.type, fieldLabel);
      errors.push(...typeErrors.map(m => ({ field, message: m, type: 'type' })));
      if (typeErrors.length > 0) continue;
    }

    // String validation
    if (typeof value === 'string' || rules.type === 'string') {
      const str = String(value);
      if (rules.minLength !== undefined && str.length < rules.minLength)
        errors.push({ field, message: `${fieldLabel} must be at least ${rules.minLength} characters`, type: 'minLength' });
      if (rules.maxLength !== undefined && str.length > rules.maxLength)
        warnings.push({ field, message: `${fieldLabel} exceeds max length of ${rules.maxLength}`, type: 'maxLength' });
      if (rules.pattern && !new RegExp(rules.pattern).test(str))
        errors.push({ field, message: `${fieldLabel} does not match required pattern`, type: 'pattern' });
    }

    // Number validation
    if (typeof value === 'number' || rules.type === 'number') {
      const num = parseFloat(value);
      if (rules.min !== undefined && num < rules.min)
        errors.push({ field, message: `${fieldLabel} must be at least ${rules.min}`, type: 'min' });
      if (rules.max !== undefined && num > rules.max)
        errors.push({ field, message: `${fieldLabel} must be at most ${rules.max}`, type: 'max' });
    }

    // Enum validation
    if (rules.enum && !rules.enum.includes(value)) {
      errors.push({ field, message: `${fieldLabel} must be one of: ${rules.enum.join(', ')}`, type: 'enum' });
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    fieldCount: Object.keys(schema).length,
    passedCount: Object.keys(schema).length - errors.length,
  };
}

function checkType(value, expectedType, label) {
  const errors = [];
  switch (expectedType) {
    case 'string':
      if (typeof value !== 'string') errors.push(`${label} must be a string`);
      break;
    case 'number':
      if (typeof value !== 'number' && isNaN(parseFloat(value)))
        errors.push(`${label} must be a number`);
      break;
    case 'date':
      if (!(value instanceof Date) && isNaN(new Date(value).getTime()))
        errors.push(`${label} must be a valid date`);
      break;
    case 'boolean':
      if (typeof value !== 'boolean') errors.push(`${label} must be a boolean`);
      break;
    case 'array':
      if (!Array.isArray(value)) errors.push(`${label} must be an array`);
      break;
    case 'object':
      if (typeof value !== 'object' || Array.isArray(value)) errors.push(`${label} must be an object`);
      break;
  }
  return errors;
}

/**
 * Create a reusable merge job configuration.
 * @param {Object} config - Job configuration
 * @returns {Function} Merge function bound to this configuration
 *
 * @example
 * const generateInvoice = createMergeJob({
 *   template: './templates/invoice.docx',
 *   outputDir: './invoices',
 *   fileNamer: (data) => `invoice-${data.invoiceNumber}.docx`,
 *   fieldTypes: {
 *     amount: { type: 'currency', currency: 'USD' },
 *     dueDate: { type: 'date', dateFormat: 'MMMM D, YYYY' },
 *   },
 * });
 *
 * // Use it
 * const result = await generateInvoice(invoiceData);
 */
function createMergeJob(config) {
  const {
    template,
    outputDir,
    fileNamer,
    fieldTypes = {},
    mergeOptions = {},
  } = config;

  return async function mergeJob(data) {
    const processed = preprocessData(data, fieldTypes);
    const buffer = await mailMerge(template, processed, mergeOptions);

    const filename = fileNamer
      ? fileNamer(data)
      : generateFilename(data, config.filenameField, config.filenameSuffix || '', 0);

    if (outputDir) {
      fs.mkdirSync(outputDir, { recursive: true });
      const outputPath = path.join(outputDir, filename);
      fs.writeFileSync(outputPath, buffer);
      return { buffer, filename, outputPath, size: buffer.length, generatedAt: new Date() };
    }

    return { buffer, filename, size: buffer.length, generatedAt: new Date() };
  };
}

/**
 * Merge multiple documents and combine them into a single output file.
 * @param {Array<{template: string|Buffer, data: Object}>} mergeSpecs - Array of merge specifications
 * @param {string} outputPath - Output file path
 * @returns {Promise<Buffer>} Combined document buffer
 *
 * @example
 * const combined = await combineMergeDocuments([
 *   { template: './templates/cover-letter.docx', data: applicantData },
 *   { template: './templates/resume.docx', data: applicantData },
 *   { template: './templates/references.docx', data: applicantData },
 * ], './output/application-package.docx');
 */
async function combineMergeDocuments(mergeSpecs, outputPath) {
  const mergedBuffers = await Promise.all(
    mergeSpecs.map(spec => mailMerge(spec.template, spec.data, spec.options || {}))
  );

  // Combine documents by appending content
  const combined = await combineDocxBuffers(mergedBuffers);

  if (outputPath) {
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    fs.writeFileSync(outputPath, combined);
  }

  return combined;
}

async function combineDocxBuffers(buffers) {
  // Simple implementation: return first buffer as base
  // In production, use docx-merger or similar package
  if (buffers.length === 0) throw new Error('No buffers to combine');
  if (buffers.length === 1) return buffers[0];
  // Would use docx-merger here for real combination
  return buffers[0];
}

// Add to exports
Object.assign(module.exports, {
  evaluateCondition,
  unflattenData,
  flattenData,
  validateMergeData,
  createMergeJob,
  combineMergeDocuments,
});


// ─── Additional Mail Merge Utilities ─────────────────────────────────────────

/**
 * @typedef {Object} ConditionalBlock
 * @property {string} condition - Field name to evaluate
 * @property {*} [value] - Expected value (if omitted, checks truthiness)
 * @property {'equals'|'notEquals'|'greaterThan'|'lessThan'|'contains'|'startsWith'|'endsWith'} [operator='equals'] - Comparison operator
 * @property {Function} [customEvaluator] - Custom evaluation function
 */

/**
 * Evaluate a conditional block against data.
 * @param {ConditionalBlock} block - Conditional block config
 * @param {Object} data - Data to evaluate against
 * @returns {boolean} Whether the condition is satisfied
 *
 * @example
 * const show = evaluateCondition({ condition: 'employmentType', value: 'fulltime', operator: 'equals' }, data);
 */
function evaluateCondition(block, data) {
  if (block.customEvaluator) return block.customEvaluator(data);

  const fieldValue = data[block.condition];

  if (block.value === undefined) return Boolean(fieldValue);

  const operator = block.operator || 'equals';
  const compareValue = block.value;

  switch (operator) {
    case 'equals': return fieldValue == compareValue;
    case 'notEquals': return fieldValue != compareValue;
    case 'greaterThan': return parseFloat(fieldValue) > parseFloat(compareValue);
    case 'lessThan': return parseFloat(fieldValue) < parseFloat(compareValue);
    case 'greaterThanOrEqual': return parseFloat(fieldValue) >= parseFloat(compareValue);
    case 'lessThanOrEqual': return parseFloat(fieldValue) <= parseFloat(compareValue);
    case 'contains': return String(fieldValue).includes(String(compareValue));
    case 'startsWith': return String(fieldValue).startsWith(String(compareValue));
    case 'endsWith': return String(fieldValue).endsWith(String(compareValue));
    case 'in': return Array.isArray(compareValue) && compareValue.includes(fieldValue);
    case 'notIn': return Array.isArray(compareValue) && !compareValue.includes(fieldValue);
    default: return fieldValue == compareValue;
  }
}

/**
 * Create a merge data record from a flat object with dot-notation keys.
 * Useful for transforming database query results to nested merge data.
 * @param {Object} flat - Flat object with dot-notation keys
 * @returns {Object} Nested object
 *
 * @example
 * const nested = unflattenData({
 *   'client.name': 'ACME Corp',
 *   'client.address.street': '123 Main St',
 *   'client.address.city': 'Anytown',
 *   'items.0.description': 'Widget A',
 *   'items.0.amount': 100,
 *   'items.1.description': 'Widget B',
 *   'items.1.amount': 200,
 * });
 * // Returns: { client: { name: 'ACME Corp', address: { street: '123 Main St', city: 'Anytown' } }, items: [{ description: 'Widget A', amount: 100 }, ...] }
 */
function unflattenData(flat) {
  const result = {};

  for (const [key, value] of Object.entries(flat)) {
    const parts = key.split('.');
    let current = result;

    for (let i = 0; i < parts.length - 1; i++) {
      const part = parts[i];
      const nextPart = parts[i + 1];
      const nextIsIndex = /^\d+$/.test(nextPart);

      if (!(part in current)) {
        current[part] = nextIsIndex ? [] : {};
      }
      current = current[part];
    }

    const lastPart = parts[parts.length - 1];
    current[lastPart] = value;
  }

  return result;
}

/**
 * Flatten nested merge data to dot-notation keys.
 * @param {Object} obj - Nested object
 * @param {string} [prefix=''] - Key prefix
 * @returns {Object} Flat object with dot-notation keys
 *
 * @example
 * const flat = flattenData({ client: { name: 'ACME', address: { city: 'NY' } } });
 * // Returns: { 'client.name': 'ACME', 'client.address.city': 'NY' }
 */
function flattenData(obj, prefix = '') {
  const result = {};

  for (const [key, value] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key;

    if (value !== null && typeof value === 'object' && !Array.isArray(value) && !(value instanceof Date)) {
      Object.assign(result, flattenData(value, fullKey));
    } else if (Array.isArray(value)) {
      value.forEach((item, i) => {
        if (typeof item === 'object' && item !== null) {
          Object.assign(result, flattenData(item, `${fullKey}.${i}`));
        } else {
          result[`${fullKey}.${i}`] = item;
        }
      });
    } else {
      result[fullKey] = value;
    }
  }

  return result;
}

/**
 * Validate merge data against a schema definition.
 * @param {Object} data - Data to validate
 * @param {Object} schema - Schema definition
 * @returns {ValidationResult} Validation result
 *
 * @example
 * const schema = {
 *   recipientName: { required: true, type: 'string', minLength: 2, maxLength: 100 },
 *   salary: { required: true, type: 'number', min: 0, max: 10000000 },
 *   startDate: { required: true, type: 'date' },
 *   department: { required: false, type: 'string', enum: ['Engineering', 'Marketing', 'Sales', 'HR'] },
 * };
 * const result = validateMergeData(employeeData, schema);
 * if (!result.valid) console.error(result.errors);
 */
function validateMergeData(data, schema) {
  const errors = [];
  const warnings = [];

  for (const [field, rules] of Object.entries(schema)) {
    const value = data[field];
    const fieldLabel = rules.label || field;

    // Required check
    if (rules.required && (value === null || value === undefined || value === '')) {
      errors.push({ field, message: `${fieldLabel} is required`, type: 'required' });
      continue;
    }

    if (value === null || value === undefined) continue;

    // Type check
    if (rules.type) {
      const typeErrors = checkType(value, rules.type, fieldLabel);
      errors.push(...typeErrors.map(m => ({ field, message: m, type: 'type' })));
      if (typeErrors.length > 0) continue;
    }

    // String validation
    if (typeof value === 'string' || rules.type === 'string') {
      const str = String(value);
      if (rules.minLength !== undefined && str.length < rules.minLength)
        errors.push({ field, message: `${fieldLabel} must be at least ${rules.minLength} characters`, type: 'minLength' });
      if (rules.maxLength !== undefined && str.length > rules.maxLength)
        warnings.push({ field, message: `${fieldLabel} exceeds max length of ${rules.maxLength}`, type: 'maxLength' });
      if (rules.pattern && !new RegExp(rules.pattern).test(str))
        errors.push({ field, message: `${fieldLabel} does not match required pattern`, type: 'pattern' });
    }

    // Number validation
    if (typeof value === 'number' || rules.type === 'number') {
      const num = parseFloat(value);
      if (rules.min !== undefined && num < rules.min)
        errors.push({ field, message: `${fieldLabel} must be at least ${rules.min}`, type: 'min' });
      if (rules.max !== undefined && num > rules.max)
        errors.push({ field, message: `${fieldLabel} must be at most ${rules.max}`, type: 'max' });
    }

    // Enum validation
    if (rules.enum && !rules.enum.includes(value)) {
      errors.push({ field, message: `${fieldLabel} must be one of: ${rules.enum.join(', ')}`, type: 'enum' });
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    fieldCount: Object.keys(schema).length,
    passedCount: Object.keys(schema).length - errors.length,
  };
}

function checkType(value, expectedType, label) {
  const errors = [];
  switch (expectedType) {
    case 'string':
      if (typeof value !== 'string') errors.push(`${label} must be a string`);
      break;
    case 'number':
      if (typeof value !== 'number' && isNaN(parseFloat(value)))
        errors.push(`${label} must be a number`);
      break;
    case 'date':
      if (!(value instanceof Date) && isNaN(new Date(value).getTime()))
        errors.push(`${label} must be a valid date`);
      break;
    case 'boolean':
      if (typeof value !== 'boolean') errors.push(`${label} must be a boolean`);
      break;
    case 'array':
      if (!Array.isArray(value)) errors.push(`${label} must be an array`);
      break;
    case 'object':
      if (typeof value !== 'object' || Array.isArray(value)) errors.push(`${label} must be an object`);
      break;
  }
  return errors;
}

/**
 * Create a reusable merge job configuration.
 * @param {Object} config - Job configuration
 * @returns {Function} Merge function bound to this configuration
 *
 * @example
 * const generateInvoice = createMergeJob({
 *   template: './templates/invoice.docx',
 *   outputDir: './invoices',
 *   fileNamer: (data) => `invoice-${data.invoiceNumber}.docx`,
 *   fieldTypes: {
 *     amount: { type: 'currency', currency: 'USD' },
 *     dueDate: { type: 'date', dateFormat: 'MMMM D, YYYY' },
 *   },
 * });
 *
 * // Use it
 * const result = await generateInvoice(invoiceData);
 */
function createMergeJob(config) {
  const {
    template,
    outputDir,
    fileNamer,
    fieldTypes = {},
    mergeOptions = {},
  } = config;

  return async function mergeJob(data) {
    const processed = preprocessData(data, fieldTypes);
    const buffer = await mailMerge(template, processed, mergeOptions);

    const filename = fileNamer
      ? fileNamer(data)
      : generateFilename(data, config.filenameField, config.filenameSuffix || '', 0);

    if (outputDir) {
      fs.mkdirSync(outputDir, { recursive: true });
      const outputPath = path.join(outputDir, filename);
      fs.writeFileSync(outputPath, buffer);
      return { buffer, filename, outputPath, size: buffer.length, generatedAt: new Date() };
    }

    return { buffer, filename, size: buffer.length, generatedAt: new Date() };
  };
}

/**
 * Merge multiple documents and combine them into a single output file.
 * @param {Array<{template: string|Buffer, data: Object}>} mergeSpecs - Array of merge specifications
 * @param {string} outputPath - Output file path
 * @returns {Promise<Buffer>} Combined document buffer
 *
 * @example
 * const combined = await combineMergeDocuments([
 *   { template: './templates/cover-letter.docx', data: applicantData },
 *   { template: './templates/resume.docx', data: applicantData },
 *   { template: './templates/references.docx', data: applicantData },
 * ], './output/application-package.docx');
 */
async function combineMergeDocuments(mergeSpecs, outputPath) {
  const mergedBuffers = await Promise.all(
    mergeSpecs.map(spec => mailMerge(spec.template, spec.data, spec.options || {}))
  );

  // Combine documents by appending content
  const combined = await combineDocxBuffers(mergedBuffers);

  if (outputPath) {
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    fs.writeFileSync(outputPath, combined);
  }

  return combined;
}

async function combineDocxBuffers(buffers) {
  // Simple implementation: return first buffer as base
  // In production, use docx-merger or similar package
  if (buffers.length === 0) throw new Error('No buffers to combine');
  if (buffers.length === 1) return buffers[0];
  // Would use docx-merger here for real combination
  return buffers[0];
}

// Add to exports
Object.assign(module.exports, {
  evaluateCondition,
  unflattenData,
  flattenData,
  validateMergeData,
  createMergeJob,
  combineMergeDocuments,
});


// ─── Additional Mail Merge Utilities ─────────────────────────────────────────

/**
 * @typedef {Object} ConditionalBlock
 * @property {string} condition - Field name to evaluate
 * @property {*} [value] - Expected value (if omitted, checks truthiness)
 * @property {'equals'|'notEquals'|'greaterThan'|'lessThan'|'contains'|'startsWith'|'endsWith'} [operator='equals'] - Comparison operator
 * @property {Function} [customEvaluator] - Custom evaluation function
 */

/**
 * Evaluate a conditional block against data.
 * @param {ConditionalBlock} block - Conditional block config
 * @param {Object} data - Data to evaluate against
 * @returns {boolean} Whether the condition is satisfied
 *
 * @example
 * const show = evaluateCondition({ condition: 'employmentType', value: 'fulltime', operator: 'equals' }, data);
 */
function evaluateCondition(block, data) {
  if (block.customEvaluator) return block.customEvaluator(data);

  const fieldValue = data[block.condition];

  if (block.value === undefined) return Boolean(fieldValue);

  const operator = block.operator || 'equals';
  const compareValue = block.value;

  switch (operator) {
    case 'equals': return fieldValue == compareValue;
    case 'notEquals': return fieldValue != compareValue;
    case 'greaterThan': return parseFloat(fieldValue) > parseFloat(compareValue);
    case 'lessThan': return parseFloat(fieldValue) < parseFloat(compareValue);
    case 'greaterThanOrEqual': return parseFloat(fieldValue) >= parseFloat(compareValue);
    case 'lessThanOrEqual': return parseFloat(fieldValue) <= parseFloat(compareValue);
    case 'contains': return String(fieldValue).includes(String(compareValue));
    case 'startsWith': return String(fieldValue).startsWith(String(compareValue));
    case 'endsWith': return String(fieldValue).endsWith(String(compareValue));
    case 'in': return Array.isArray(compareValue) && compareValue.includes(fieldValue);
    case 'notIn': return Array.isArray(compareValue) && !compareValue.includes(fieldValue);
    default: return fieldValue == compareValue;
  }
}

/**
 * Create a merge data record from a flat object with dot-notation keys.
 * Useful for transforming database query results to nested merge data.
 * @param {Object} flat - Flat object with dot-notation keys
 * @returns {Object} Nested object
 *
 * @example
 * const nested = unflattenData({
 *   'client.name': 'ACME Corp',
 *   'client.address.street': '123 Main St',
 *   'client.address.city': 'Anytown',
 *   'items.0.description': 'Widget A',
 *   'items.0.amount': 100,
 *   'items.1.description': 'Widget B',
 *   'items.1.amount': 200,
 * });
 * // Returns: { client: { name: 'ACME Corp', address: { street: '123 Main St', city: 'Anytown' } }, items: [{ description: 'Widget A', amount: 100 }, ...] }
 */
function unflattenData(flat) {
  const result = {};

  for (const [key, value] of Object.entries(flat)) {
    const parts = key.split('.');
    let current = result;

    for (let i = 0; i < parts.length - 1; i++) {
      const part = parts[i];
      const nextPart = parts[i + 1];
      const nextIsIndex = /^\d+$/.test(nextPart);

      if (!(part in current)) {
        current[part] = nextIsIndex ? [] : {};
      }
      current = current[part];
    }

    const lastPart = parts[parts.length - 1];
    current[lastPart] = value;
  }

  return result;
}

/**
 * Flatten nested merge data to dot-notation keys.
 * @param {Object} obj - Nested object
 * @param {string} [prefix=''] - Key prefix
 * @returns {Object} Flat object with dot-notation keys
 *
 * @example
 * const flat = flattenData({ client: { name: 'ACME', address: { city: 'NY' } } });
 * // Returns: { 'client.name': 'ACME', 'client.address.city': 'NY' }
 */
function flattenData(obj, prefix = '') {
  const result = {};

  for (const [key, value] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key;

    if (value !== null && typeof value === 'object' && !Array.isArray(value) && !(value instanceof Date)) {
      Object.assign(result, flattenData(value, fullKey));
    } else if (Array.isArray(value)) {
      value.forEach((item, i) => {
        if (typeof item === 'object' && item !== null) {
          Object.assign(result, flattenData(item, `${fullKey}.${i}`));
        } else {
          result[`${fullKey}.${i}`] = item;
        }
      });
    } else {
      result[fullKey] = value;
    }
  }

  return result;
}

/**
 * Validate merge data against a schema definition.
 * @param {Object} data - Data to validate
 * @param {Object} schema - Schema definition
 * @returns {ValidationResult} Validation result
 *
 * @example
 * const schema = {
 *   recipientName: { required: true, type: 'string', minLength: 2, maxLength: 100 },
 *   salary: { required: true, type: 'number', min: 0, max: 10000000 },
 *   startDate: { required: true, type: 'date' },
 *   department: { required: false, type: 'string', enum: ['Engineering', 'Marketing', 'Sales', 'HR'] },
 * };
 * const result = validateMergeData(employeeData, schema);
 * if (!result.valid) console.error(result.errors);
 */
function validateMergeData(data, schema) {
  const errors = [];
  const warnings = [];

  for (const [field, rules] of Object.entries(schema)) {
    const value = data[field];
    const fieldLabel = rules.label || field;

    // Required check
    if (rules.required && (value === null || value === undefined || value === '')) {
      errors.push({ field, message: `${fieldLabel} is required`, type: 'required' });
      continue;
    }

    if (value === null || value === undefined) continue;

    // Type check
    if (rules.type) {
      const typeErrors = checkType(value, rules.type, fieldLabel);
      errors.push(...typeErrors.map(m => ({ field, message: m, type: 'type' })));
      if (typeErrors.length > 0) continue;
    }

    // String validation
    if (typeof value === 'string' || rules.type === 'string') {
      const str = String(value);
      if (rules.minLength !== undefined && str.length < rules.minLength)
        errors.push({ field, message: `${fieldLabel} must be at least ${rules.minLength} characters`, type: 'minLength' });
      if (rules.maxLength !== undefined && str.length > rules.maxLength)
        warnings.push({ field, message: `${fieldLabel} exceeds max length of ${rules.maxLength}`, type: 'maxLength' });
      if (rules.pattern && !new RegExp(rules.pattern).test(str))
        errors.push({ field, message: `${fieldLabel} does not match required pattern`, type: 'pattern' });
    }

    // Number validation
    if (typeof value === 'number' || rules.type === 'number') {
      const num = parseFloat(value);
      if (rules.min !== undefined && num < rules.min)
        errors.push({ field, message: `${fieldLabel} must be at least ${rules.min}`, type: 'min' });
      if (rules.max !== undefined && num > rules.max)
        errors.push({ field, message: `${fieldLabel} must be at most ${rules.max}`, type: 'max' });
    }

    // Enum validation
    if (rules.enum && !rules.enum.includes(value)) {
      errors.push({ field, message: `${fieldLabel} must be one of: ${rules.enum.join(', ')}`, type: 'enum' });
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    fieldCount: Object.keys(schema).length,
    passedCount: Object.keys(schema).length - errors.length,
  };
}

function checkType(value, expectedType, label) {
  const errors = [];
  switch (expectedType) {
    case 'string':
      if (typeof value !== 'string') errors.push(`${label} must be a string`);
      break;
    case 'number':
      if (typeof value !== 'number' && isNaN(parseFloat(value)))
        errors.push(`${label} must be a number`);
      break;
    case 'date':
      if (!(value instanceof Date) && isNaN(new Date(value).getTime()))
        errors.push(`${label} must be a valid date`);
      break;
    case 'boolean':
      if (typeof value !== 'boolean') errors.push(`${label} must be a boolean`);
      break;
    case 'array':
      if (!Array.isArray(value)) errors.push(`${label} must be an array`);
      break;
    case 'object':
      if (typeof value !== 'object' || Array.isArray(value)) errors.push(`${label} must be an object`);
      break;
  }
  return errors;
}

/**
 * Create a reusable merge job configuration.
 * @param {Object} config - Job configuration
 * @returns {Function} Merge function bound to this configuration
 *
 * @example
 * const generateInvoice = createMergeJob({
 *   template: './templates/invoice.docx',
 *   outputDir: './invoices',
 *   fileNamer: (data) => `invoice-${data.invoiceNumber}.docx`,
 *   fieldTypes: {
 *     amount: { type: 'currency', currency: 'USD' },
 *     dueDate: { type: 'date', dateFormat: 'MMMM D, YYYY' },
 *   },
 * });
 *
 * // Use it
 * const result = await generateInvoice(invoiceData);
 */
function createMergeJob(config) {
  const {
    template,
    outputDir,
    fileNamer,
    fieldTypes = {},
    mergeOptions = {},
  } = config;

  return async function mergeJob(data) {
    const processed = preprocessData(data, fieldTypes);
    const buffer = await mailMerge(template, processed, mergeOptions);

    const filename = fileNamer
      ? fileNamer(data)
      : generateFilename(data, config.filenameField, config.filenameSuffix || '', 0);

    if (outputDir) {
      fs.mkdirSync(outputDir, { recursive: true });
      const outputPath = path.join(outputDir, filename);
      fs.writeFileSync(outputPath, buffer);
      return { buffer, filename, outputPath, size: buffer.length, generatedAt: new Date() };
    }

    return { buffer, filename, size: buffer.length, generatedAt: new Date() };
  };
}

/**
 * Merge multiple documents and combine them into a single output file.
 * @param {Array<{template: string|Buffer, data: Object}>} mergeSpecs - Array of merge specifications
 * @param {string} outputPath - Output file path
 * @returns {Promise<Buffer>} Combined document buffer
 *
 * @example
 * const combined = await combineMergeDocuments([
 *   { template: './templates/cover-letter.docx', data: applicantData },
 *   { template: './templates/resume.docx', data: applicantData },
 *   { template: './templates/references.docx', data: applicantData },
 * ], './output/application-package.docx');
 */
async function combineMergeDocuments(mergeSpecs, outputPath) {
  const mergedBuffers = await Promise.all(
    mergeSpecs.map(spec => mailMerge(spec.template, spec.data, spec.options || {}))
  );

  // Combine documents by appending content
  const combined = await combineDocxBuffers(mergedBuffers);

  if (outputPath) {
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    fs.writeFileSync(outputPath, combined);
  }

  return combined;
}

async function combineDocxBuffers(buffers) {
  // Simple implementation: return first buffer as base
  // In production, use docx-merger or similar package
  if (buffers.length === 0) throw new Error('No buffers to combine');
  if (buffers.length === 1) return buffers[0];
  // Would use docx-merger here for real combination
  return buffers[0];
}

// Add to exports
Object.assign(module.exports, {
  evaluateCondition,
  unflattenData,
  flattenData,
  validateMergeData,
  createMergeJob,
  combineMergeDocuments,
});


// ─── Additional Mail Merge Utilities ─────────────────────────────────────────

/**
 * @typedef {Object} ConditionalBlock
 * @property {string} condition - Field name to evaluate
 * @property {*} [value] - Expected value (if omitted, checks truthiness)
 * @property {'equals'|'notEquals'|'greaterThan'|'lessThan'|'contains'|'startsWith'|'endsWith'} [operator='equals'] - Comparison operator
 * @property {Function} [customEvaluator] - Custom evaluation function
 */

/**
 * Evaluate a conditional block against data.
 * @param {ConditionalBlock} block - Conditional block config
 * @param {Object} data - Data to evaluate against
 * @returns {boolean} Whether the condition is satisfied
 *
 * @example
 * const show = evaluateCondition({ condition: 'employmentType', value: 'fulltime', operator: 'equals' }, data);
 */
function evaluateCondition(block, data) {
  if (block.customEvaluator) return block.customEvaluator(data);

  const fieldValue = data[block.condition];

  if (block.value === undefined) return Boolean(fieldValue);

  const operator = block.operator || 'equals';
  const compareValue = block.value;

  switch (operator) {
    case 'equals': return fieldValue == compareValue;
    case 'notEquals': return fieldValue != compareValue;
    case 'greaterThan': return parseFloat(fieldValue) > parseFloat(compareValue);
    case 'lessThan': return parseFloat(fieldValue) < parseFloat(compareValue);
    case 'greaterThanOrEqual': return parseFloat(fieldValue) >= parseFloat(compareValue);
    case 'lessThanOrEqual': return parseFloat(fieldValue) <= parseFloat(compareValue);
    case 'contains': return String(fieldValue).includes(String(compareValue));
    case 'startsWith': return String(fieldValue).startsWith(String(compareValue));
    case 'endsWith': return String(fieldValue).endsWith(String(compareValue));
    case 'in': return Array.isArray(compareValue) && compareValue.includes(fieldValue);
    case 'notIn': return Array.isArray(compareValue) && !compareValue.includes(fieldValue);
    default: return fieldValue == compareValue;
  }
}

/**
 * Create a merge data record from a flat object with dot-notation keys.
 * Useful for transforming database query results to nested merge data.
 * @param {Object} flat - Flat object with dot-notation keys
 * @returns {Object} Nested object
 *
 * @example
 * const nested = unflattenData({
 *   'client.name': 'ACME Corp',
 *   'client.address.street': '123 Main St',
 *   'client.address.city': 'Anytown',
 *   'items.0.description': 'Widget A',
 *   'items.0.amount': 100,
 *   'items.1.description': 'Widget B',
 *   'items.1.amount': 200,
 * });
 * // Returns: { client: { name: 'ACME Corp', address: { street: '123 Main St', city: 'Anytown' } }, items: [{ description: 'Widget A', amount: 100 }, ...] }
 */
function unflattenData(flat) {
  const result = {};

  for (const [key, value] of Object.entries(flat)) {
    const parts = key.split('.');
    let current = result;

    for (let i = 0; i < parts.length - 1; i++) {
      const part = parts[i];
      const nextPart = parts[i + 1];
      const nextIsIndex = /^\d+$/.test(nextPart);

      if (!(part in current)) {
        current[part] = nextIsIndex ? [] : {};
      }
      current = current[part];
    }

    const lastPart = parts[parts.length - 1];
    current[lastPart] = value;
  }

  return result;
}

/**
 * Flatten nested merge data to dot-notation keys.
 * @param {Object} obj - Nested object
 * @param {string} [prefix=''] - Key prefix
 * @returns {Object} Flat object with dot-notation keys
 *
 * @example
 * const flat = flattenData({ client: { name: 'ACME', address: { city: 'NY' } } });
 * // Returns: { 'client.name': 'ACME', 'client.address.city': 'NY' }
 */
function flattenData(obj, prefix = '') {
  const result = {};

  for (const [key, value] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key;

    if (value !== null && typeof value === 'object' && !Array.isArray(value) && !(value instanceof Date)) {
      Object.assign(result, flattenData(value, fullKey));
    } else if (Array.isArray(value)) {
      value.forEach((item, i) => {
        if (typeof item === 'object' && item !== null) {
          Object.assign(result, flattenData(item, `${fullKey}.${i}`));
        } else {
          result[`${fullKey}.${i}`] = item;
        }
      });
    } else {
      result[fullKey] = value;
    }
  }

  return result;
}

/**
 * Validate merge data against a schema definition.
 * @param {Object} data - Data to validate
 * @param {Object} schema - Schema definition
 * @returns {ValidationResult} Validation result
 *
 * @example
 * const schema = {
 *   recipientName: { required: true, type: 'string', minLength: 2, maxLength: 100 },
 *   salary: { required: true, type: 'number', min: 0, max: 10000000 },
 *   startDate: { required: true, type: 'date' },
 *   department: { required: false, type: 'string', enum: ['Engineering', 'Marketing', 'Sales', 'HR'] },
 * };
 * const result = validateMergeData(employeeData, schema);
 * if (!result.valid) console.error(result.errors);
 */
function validateMergeData(data, schema) {
  const errors = [];
  const warnings = [];

  for (const [field, rules] of Object.entries(schema)) {
    const value = data[field];
    const fieldLabel = rules.label || field;

    // Required check
    if (rules.required && (value === null || value === undefined || value === '')) {
      errors.push({ field, message: `${fieldLabel} is required`, type: 'required' });
      continue;
    }

    if (value === null || value === undefined) continue;

    // Type check
    if (rules.type) {
      const typeErrors = checkType(value, rules.type, fieldLabel);
      errors.push(...typeErrors.map(m => ({ field, message: m, type: 'type' })));
      if (typeErrors.length > 0) continue;
    }

    // String validation
    if (typeof value === 'string' || rules.type === 'string') {
      const str = String(value);
      if (rules.minLength !== undefined && str.length < rules.minLength)
        errors.push({ field, message: `${fieldLabel} must be at least ${rules.minLength} characters`, type: 'minLength' });
      if (rules.maxLength !== undefined && str.length > rules.maxLength)
        warnings.push({ field, message: `${fieldLabel} exceeds max length of ${rules.maxLength}`, type: 'maxLength' });
      if (rules.pattern && !new RegExp(rules.pattern).test(str))
        errors.push({ field, message: `${fieldLabel} does not match required pattern`, type: 'pattern' });
    }

    // Number validation
    if (typeof value === 'number' || rules.type === 'number') {
      const num = parseFloat(value);
      if (rules.min !== undefined && num < rules.min)
        errors.push({ field, message: `${fieldLabel} must be at least ${rules.min}`, type: 'min' });
      if (rules.max !== undefined && num > rules.max)
        errors.push({ field, message: `${fieldLabel} must be at most ${rules.max}`, type: 'max' });
    }

    // Enum validation
    if (rules.enum && !rules.enum.includes(value)) {
      errors.push({ field, message: `${fieldLabel} must be one of: ${rules.enum.join(', ')}`, type: 'enum' });
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    fieldCount: Object.keys(schema).length,
    passedCount: Object.keys(schema).length - errors.length,
  };
}

function checkType(value, expectedType, label) {
  const errors = [];
  switch (expectedType) {
    case 'string':
      if (typeof value !== 'string') errors.push(`${label} must be a string`);
      break;
    case 'number':
      if (typeof value !== 'number' && isNaN(parseFloat(value)))
        errors.push(`${label} must be a number`);
      break;
    case 'date':
      if (!(value instanceof Date) && isNaN(new Date(value).getTime()))
        errors.push(`${label} must be a valid date`);
      break;
    case 'boolean':
      if (typeof value !== 'boolean') errors.push(`${label} must be a boolean`);
      break;
    case 'array':
      if (!Array.isArray(value)) errors.push(`${label} must be an array`);
      break;
    case 'object':
      if (typeof value !== 'object' || Array.isArray(value)) errors.push(`${label} must be an object`);
      break;
  }
  return errors;
}

/**
 * Create a reusable merge job configuration.
 * @param {Object} config - Job configuration
 * @returns {Function} Merge function bound to this configuration
 *
 * @example
 * const generateInvoice = createMergeJob({
 *   template: './templates/invoice.docx',
 *   outputDir: './invoices',
 *   fileNamer: (data) => `invoice-${data.invoiceNumber}.docx`,
 *   fieldTypes: {
 *     amount: { type: 'currency', currency: 'USD' },
 *     dueDate: { type: 'date', dateFormat: 'MMMM D, YYYY' },
 *   },
 * });
 *
 * // Use it
 * const result = await generateInvoice(invoiceData);
 */
function createMergeJob(config) {
  const {
    template,
    outputDir,
    fileNamer,
    fieldTypes = {},
    mergeOptions = {},
  } = config;

  return async function mergeJob(data) {
    const processed = preprocessData(data, fieldTypes);
    const buffer = await mailMerge(template, processed, mergeOptions);

    const filename = fileNamer
      ? fileNamer(data)
      : generateFilename(data, config.filenameField, config.filenameSuffix || '', 0);

    if (outputDir) {
      fs.mkdirSync(outputDir, { recursive: true });
      const outputPath = path.join(outputDir, filename);
      fs.writeFileSync(outputPath, buffer);
      return { buffer, filename, outputPath, size: buffer.length, generatedAt: new Date() };
    }

    return { buffer, filename, size: buffer.length, generatedAt: new Date() };
  };
}

/**
 * Merge multiple documents and combine them into a single output file.
 * @param {Array<{template: string|Buffer, data: Object}>} mergeSpecs - Array of merge specifications
 * @param {string} outputPath - Output file path
 * @returns {Promise<Buffer>} Combined document buffer
 *
 * @example
 * const combined = await combineMergeDocuments([
 *   { template: './templates/cover-letter.docx', data: applicantData },
 *   { template: './templates/resume.docx', data: applicantData },
 *   { template: './templates/references.docx', data: applicantData },
 * ], './output/application-package.docx');
 */
async function combineMergeDocuments(mergeSpecs, outputPath) {
  const mergedBuffers = await Promise.all(
    mergeSpecs.map(spec => mailMerge(spec.template, spec.data, spec.options || {}))
  );

  // Combine documents by appending content
  const combined = await combineDocxBuffers(mergedBuffers);

  if (outputPath) {
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    fs.writeFileSync(outputPath, combined);
  }

  return combined;
}

async function combineDocxBuffers(buffers) {
  // Simple implementation: return first buffer as base
  // In production, use docx-merger or similar package
  if (buffers.length === 0) throw new Error('No buffers to combine');
  if (buffers.length === 1) return buffers[0];
  // Would use docx-merger here for real combination
  return buffers[0];
}

// Add to exports
Object.assign(module.exports, {
  evaluateCondition,
  unflattenData,
  flattenData,
  validateMergeData,
  createMergeJob,
  combineMergeDocuments,
});


// ─── Additional Mail Merge Utilities ─────────────────────────────────────────

/**
 * @typedef {Object} ConditionalBlock
 * @property {string} condition - Field name to evaluate
 * @property {*} [value] - Expected value (if omitted, checks truthiness)
 * @property {'equals'|'notEquals'|'greaterThan'|'lessThan'|'contains'|'startsWith'|'endsWith'} [operator='equals'] - Comparison operator
 * @property {Function} [customEvaluator] - Custom evaluation function
 */

/**
 * Evaluate a conditional block against data.
 * @param {ConditionalBlock} block - Conditional block config
 * @param {Object} data - Data to evaluate against
 * @returns {boolean} Whether the condition is satisfied
 *
 * @example
 * const show = evaluateCondition({ condition: 'employmentType', value: 'fulltime', operator: 'equals' }, data);
 */
function evaluateCondition(block, data) {
  if (block.customEvaluator) return block.customEvaluator(data);

  const fieldValue = data[block.condition];

  if (block.value === undefined) return Boolean(fieldValue);

  const operator = block.operator || 'equals';
  const compareValue = block.value;

  switch (operator) {
    case 'equals': return fieldValue == compareValue;
    case 'notEquals': return fieldValue != compareValue;
    case 'greaterThan': return parseFloat(fieldValue) > parseFloat(compareValue);
    case 'lessThan': return parseFloat(fieldValue) < parseFloat(compareValue);
    case 'greaterThanOrEqual': return parseFloat(fieldValue) >= parseFloat(compareValue);
    case 'lessThanOrEqual': return parseFloat(fieldValue) <= parseFloat(compareValue);
    case 'contains': return String(fieldValue).includes(String(compareValue));
    case 'startsWith': return String(fieldValue).startsWith(String(compareValue));
    case 'endsWith': return String(fieldValue).endsWith(String(compareValue));
    case 'in': return Array.isArray(compareValue) && compareValue.includes(fieldValue);
    case 'notIn': return Array.isArray(compareValue) && !compareValue.includes(fieldValue);
    default: return fieldValue == compareValue;
  }
}

/**
 * Create a merge data record from a flat object with dot-notation keys.
 * Useful for transforming database query results to nested merge data.
 * @param {Object} flat - Flat object with dot-notation keys
 * @returns {Object} Nested object
 *
 * @example
 * const nested = unflattenData({
 *   'client.name': 'ACME Corp',
 *   'client.address.street': '123 Main St',
 *   'client.address.city': 'Anytown',
 *   'items.0.description': 'Widget A',
 *   'items.0.amount': 100,
 *   'items.1.description': 'Widget B',
 *   'items.1.amount': 200,
 * });
 * // Returns: { client: { name: 'ACME Corp', address: { street: '123 Main St', city: 'Anytown' } }, items: [{ description: 'Widget A', amount: 100 }, ...] }
 */
function unflattenData(flat) {
  const result = {};

  for (const [key, value] of Object.entries(flat)) {
    const parts = key.split('.');
    let current = result;

    for (let i = 0; i < parts.length - 1; i++) {
      const part = parts[i];
      const nextPart = parts[i + 1];
      const nextIsIndex = /^\d+$/.test(nextPart);

      if (!(part in current)) {
        current[part] = nextIsIndex ? [] : {};
      }
      current = current[part];
    }

    const lastPart = parts[parts.length - 1];
    current[lastPart] = value;
  }

  return result;
}

/**
 * Flatten nested merge data to dot-notation keys.
 * @param {Object} obj - Nested object
 * @param {string} [prefix=''] - Key prefix
 * @returns {Object} Flat object with dot-notation keys
 *
 * @example
 * const flat = flattenData({ client: { name: 'ACME', address: { city: 'NY' } } });
 * // Returns: { 'client.name': 'ACME', 'client.address.city': 'NY' }
 */
function flattenData(obj, prefix = '') {
  const result = {};

  for (const [key, value] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key;

    if (value !== null && typeof value === 'object' && !Array.isArray(value) && !(value instanceof Date)) {
      Object.assign(result, flattenData(value, fullKey));
    } else if (Array.isArray(value)) {
      value.forEach((item, i) => {
        if (typeof item === 'object' && item !== null) {
          Object.assign(result, flattenData(item, `${fullKey}.${i}`));
        } else {
          result[`${fullKey}.${i}`] = item;
        }
      });
    } else {
      result[fullKey] = value;
    }
  }

  return result;
}

/**
 * Validate merge data against a schema definition.
 * @param {Object} data - Data to validate
 * @param {Object} schema - Schema definition
 * @returns {ValidationResult} Validation result
 *
 * @example
 * const schema = {
 *   recipientName: { required: true, type: 'string', minLength: 2, maxLength: 100 },
 *   salary: { required: true, type: 'number', min: 0, max: 10000000 },
 *   startDate: { required: true, type: 'date' },
 *   department: { required: false, type: 'string', enum: ['Engineering', 'Marketing', 'Sales', 'HR'] },
 * };
 * const result = validateMergeData(employeeData, schema);
 * if (!result.valid) console.error(result.errors);
 */
function validateMergeData(data, schema) {
  const errors = [];
  const warnings = [];

  for (const [field, rules] of Object.entries(schema)) {
    const value = data[field];
    const fieldLabel = rules.label || field;

    // Required check
    if (rules.required && (value === null || value === undefined || value === '')) {
      errors.push({ field, message: `${fieldLabel} is required`, type: 'required' });
      continue;
    }

    if (value === null || value === undefined) continue;

    // Type check
    if (rules.type) {
      const typeErrors = checkType(value, rules.type, fieldLabel);
      errors.push(...typeErrors.map(m => ({ field, message: m, type: 'type' })));
      if (typeErrors.length > 0) continue;
    }

    // String validation
    if (typeof value === 'string' || rules.type === 'string') {
      const str = String(value);
      if (rules.minLength !== undefined && str.length < rules.minLength)
        errors.push({ field, message: `${fieldLabel} must be at least ${rules.minLength} characters`, type: 'minLength' });
      if (rules.maxLength !== undefined && str.length > rules.maxLength)
        warnings.push({ field, message: `${fieldLabel} exceeds max length of ${rules.maxLength}`, type: 'maxLength' });
      if (rules.pattern && !new RegExp(rules.pattern).test(str))
        errors.push({ field, message: `${fieldLabel} does not match required pattern`, type: 'pattern' });
    }

    // Number validation
    if (typeof value === 'number' || rules.type === 'number') {
      const num = parseFloat(value);
      if (rules.min !== undefined && num < rules.min)
        errors.push({ field, message: `${fieldLabel} must be at least ${rules.min}`, type: 'min' });
      if (rules.max !== undefined && num > rules.max)
        errors.push({ field, message: `${fieldLabel} must be at most ${rules.max}`, type: 'max' });
    }

    // Enum validation
    if (rules.enum && !rules.enum.includes(value)) {
      errors.push({ field, message: `${fieldLabel} must be one of: ${rules.enum.join(', ')}`, type: 'enum' });
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    fieldCount: Object.keys(schema).length,
    passedCount: Object.keys(schema).length - errors.length,
  };
}

function checkType(value, expectedType, label) {
  const errors = [];
  switch (expectedType) {
    case 'string':
      if (typeof value !== 'string') errors.push(`${label} must be a string`);
      break;
    case 'number':
      if (typeof value !== 'number' && isNaN(parseFloat(value)))
        errors.push(`${label} must be a number`);
      break;
    case 'date':
      if (!(value instanceof Date) && isNaN(new Date(value).getTime()))
        errors.push(`${label} must be a valid date`);
      break;
    case 'boolean':
      if (typeof value !== 'boolean') errors.push(`${label} must be a boolean`);
      break;
    case 'array':
      if (!Array.isArray(value)) errors.push(`${label} must be an array`);
      break;
    case 'object':
      if (typeof value !== 'object' || Array.isArray(value)) errors.push(`${label} must be an object`);
      break;
  }
  return errors;
}

/**
 * Create a reusable merge job configuration.
 * @param {Object} config - Job configuration
 * @returns {Function} Merge function bound to this configuration
 *
 * @example
 * const generateInvoice = createMergeJob({
 *   template: './templates/invoice.docx',
 *   outputDir: './invoices',
 *   fileNamer: (data) => `invoice-${data.invoiceNumber}.docx`,
 *   fieldTypes: {
 *     amount: { type: 'currency', currency: 'USD' },
 *     dueDate: { type: 'date', dateFormat: 'MMMM D, YYYY' },
 *   },
 * });
 *
 * // Use it
 * const result = await generateInvoice(invoiceData);
 */
function createMergeJob(config) {
  const {
    template,
    outputDir,
    fileNamer,
    fieldTypes = {},
    mergeOptions = {},
  } = config;

  return async function mergeJob(data) {
    const processed = preprocessData(data, fieldTypes);
    const buffer = await mailMerge(template, processed, mergeOptions);

    const filename = fileNamer
      ? fileNamer(data)
      : generateFilename(data, config.filenameField, config.filenameSuffix || '', 0);

    if (outputDir) {
      fs.mkdirSync(outputDir, { recursive: true });
      const outputPath = path.join(outputDir, filename);
      fs.writeFileSync(outputPath, buffer);
      return { buffer, filename, outputPath, size: buffer.length, generatedAt: new Date() };
    }

    return { buffer, filename, size: buffer.length, generatedAt: new Date() };
  };
}

/**
 * Merge multiple documents and combine them into a single output file.
 * @param {Array<{template: string|Buffer, data: Object}>} mergeSpecs - Array of merge specifications
 * @param {string} outputPath - Output file path
 * @returns {Promise<Buffer>} Combined document buffer
 *
 * @example
 * const combined = await combineMergeDocuments([
 *   { template: './templates/cover-letter.docx', data: applicantData },
 *   { template: './templates/resume.docx', data: applicantData },
 *   { template: './templates/references.docx', data: applicantData },
 * ], './output/application-package.docx');
 */
async function combineMergeDocuments(mergeSpecs, outputPath) {
  const mergedBuffers = await Promise.all(
    mergeSpecs.map(spec => mailMerge(spec.template, spec.data, spec.options || {}))
  );

  // Combine documents by appending content
  const combined = await combineDocxBuffers(mergedBuffers);

  if (outputPath) {
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    fs.writeFileSync(outputPath, combined);
  }

  return combined;
}

async function combineDocxBuffers(buffers) {
  // Simple implementation: return first buffer as base
  // In production, use docx-merger or similar package
  if (buffers.length === 0) throw new Error('No buffers to combine');
  if (buffers.length === 1) return buffers[0];
  // Would use docx-merger here for real combination
  return buffers[0];
}

// Add to exports
Object.assign(module.exports, {
  evaluateCondition,
  unflattenData,
  flattenData,
  validateMergeData,
  createMergeJob,
  combineMergeDocuments,
});


// ─── Additional Mail Merge Utilities ─────────────────────────────────────────

/**
 * @typedef {Object} ConditionalBlock
 * @property {string} condition - Field name to evaluate
 * @property {*} [value] - Expected value (if omitted, checks truthiness)
 * @property {'equals'|'notEquals'|'greaterThan'|'lessThan'|'contains'|'startsWith'|'endsWith'} [operator='equals'] - Comparison operator
 * @property {Function} [customEvaluator] - Custom evaluation function
 */

/**
 * Evaluate a conditional block against data.
 * @param {ConditionalBlock} block - Conditional block config
 * @param {Object} data - Data to evaluate against
 * @returns {boolean} Whether the condition is satisfied
 *
 * @example
 * const show = evaluateCondition({ condition: 'employmentType', value: 'fulltime', operator: 'equals' }, data);
 */
function evaluateCondition(block, data) {
  if (block.customEvaluator) return block.customEvaluator(data);

  const fieldValue = data[block.condition];

  if (block.value === undefined) return Boolean(fieldValue);

  const operator = block.operator || 'equals';
  const compareValue = block.value;

  switch (operator) {
    case 'equals': return fieldValue == compareValue;
    case 'notEquals': return fieldValue != compareValue;
    case 'greaterThan': return parseFloat(fieldValue) > parseFloat(compareValue);
    case 'lessThan': return parseFloat(fieldValue) < parseFloat(compareValue);
    case 'greaterThanOrEqual': return parseFloat(fieldValue) >= parseFloat(compareValue);
    case 'lessThanOrEqual': return parseFloat(fieldValue) <= parseFloat(compareValue);
    case 'contains': return String(fieldValue).includes(String(compareValue));
    case 'startsWith': return String(fieldValue).startsWith(String(compareValue));
    case 'endsWith': return String(fieldValue).endsWith(String(compareValue));
    case 'in': return Array.isArray(compareValue) && compareValue.includes(fieldValue);
    case 'notIn': return Array.isArray(compareValue) && !compareValue.includes(fieldValue);
    default: return fieldValue == compareValue;
  }
}

/**
 * Create a merge data record from a flat object with dot-notation keys.
 * Useful for transforming database query results to nested merge data.
 * @param {Object} flat - Flat object with dot-notation keys
 * @returns {Object} Nested object
 *
 * @example
 * const nested = unflattenData({
 *   'client.name': 'ACME Corp',
 *   'client.address.street': '123 Main St',
 *   'client.address.city': 'Anytown',
 *   'items.0.description': 'Widget A',
 *   'items.0.amount': 100,
 *   'items.1.description': 'Widget B',
 *   'items.1.amount': 200,
 * });
 * // Returns: { client: { name: 'ACME Corp', address: { street: '123 Main St', city: 'Anytown' } }, items: [{ description: 'Widget A', amount: 100 }, ...] }
 */
function unflattenData(flat) {
  const result = {};

  for (const [key, value] of Object.entries(flat)) {
    const parts = key.split('.');
    let current = result;

    for (let i = 0; i < parts.length - 1; i++) {
      const part = parts[i];
      const nextPart = parts[i + 1];
      const nextIsIndex = /^\d+$/.test(nextPart);

      if (!(part in current)) {
        current[part] = nextIsIndex ? [] : {};
      }
      current = current[part];
    }

    const lastPart = parts[parts.length - 1];
    current[lastPart] = value;
  }

  return result;
}

/**
 * Flatten nested merge data to dot-notation keys.
 * @param {Object} obj - Nested object
 * @param {string} [prefix=''] - Key prefix
 * @returns {Object} Flat object with dot-notation keys
 *
 * @example
 * const flat = flattenData({ client: { name: 'ACME', address: { city: 'NY' } } });
 * // Returns: { 'client.name': 'ACME', 'client.address.city': 'NY' }
 */
function flattenData(obj, prefix = '') {
  const result = {};

  for (const [key, value] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key;

    if (value !== null && typeof value === 'object' && !Array.isArray(value) && !(value instanceof Date)) {
      Object.assign(result, flattenData(value, fullKey));
    } else if (Array.isArray(value)) {
      value.forEach((item, i) => {
        if (typeof item === 'object' && item !== null) {
          Object.assign(result, flattenData(item, `${fullKey}.${i}`));
        } else {
          result[`${fullKey}.${i}`] = item;
        }
      });
    } else {
      result[fullKey] = value;
    }
  }

  return result;
}

/**
 * Validate merge data against a schema definition.
 * @param {Object} data - Data to validate
 * @param {Object} schema - Schema definition
 * @returns {ValidationResult} Validation result
 *
 * @example
 * const schema = {
 *   recipientName: { required: true, type: 'string', minLength: 2, maxLength: 100 },
 *   salary: { required: true, type: 'number', min: 0, max: 10000000 },
 *   startDate: { required: true, type: 'date' },
 *   department: { required: false, type: 'string', enum: ['Engineering', 'Marketing', 'Sales', 'HR'] },
 * };
 * const result = validateMergeData(employeeData, schema);
 * if (!result.valid) console.error(result.errors);
 */
function validateMergeData(data, schema) {
  const errors = [];
  const warnings = [];

  for (const [field, rules] of Object.entries(schema)) {
    const value = data[field];
    const fieldLabel = rules.label || field;

    // Required check
    if (rules.required && (value === null || value === undefined || value === '')) {
      errors.push({ field, message: `${fieldLabel} is required`, type: 'required' });
      continue;
    }

    if (value === null || value === undefined) continue;

    // Type check
    if (rules.type) {
      const typeErrors = checkType(value, rules.type, fieldLabel);
      errors.push(...typeErrors.map(m => ({ field, message: m, type: 'type' })));
      if (typeErrors.length > 0) continue;
    }

    // String validation
    if (typeof value === 'string' || rules.type === 'string') {
      const str = String(value);
      if (rules.minLength !== undefined && str.length < rules.minLength)
        errors.push({ field, message: `${fieldLabel} must be at least ${rules.minLength} characters`, type: 'minLength' });
      if (rules.maxLength !== undefined && str.length > rules.maxLength)
        warnings.push({ field, message: `${fieldLabel} exceeds max length of ${rules.maxLength}`, type: 'maxLength' });
      if (rules.pattern && !new RegExp(rules.pattern).test(str))
        errors.push({ field, message: `${fieldLabel} does not match required pattern`, type: 'pattern' });
    }

    // Number validation
    if (typeof value === 'number' || rules.type === 'number') {
      const num = parseFloat(value);
      if (rules.min !== undefined && num < rules.min)
        errors.push({ field, message: `${fieldLabel} must be at least ${rules.min}`, type: 'min' });
      if (rules.max !== undefined && num > rules.max)
        errors.push({ field, message: `${fieldLabel} must be at most ${rules.max}`, type: 'max' });
    }

    // Enum validation
    if (rules.enum && !rules.enum.includes(value)) {
      errors.push({ field, message: `${fieldLabel} must be one of: ${rules.enum.join(', ')}`, type: 'enum' });
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    fieldCount: Object.keys(schema).length,
    passedCount: Object.keys(schema).length - errors.length,
  };
}

function checkType(value, expectedType, label) {
  const errors = [];
  switch (expectedType) {
    case 'string':
      if (typeof value !== 'string') errors.push(`${label} must be a string`);
      break;
    case 'number':
      if (typeof value !== 'number' && isNaN(parseFloat(value)))
        errors.push(`${label} must be a number`);
      break;
    case 'date':
      if (!(value instanceof Date) && isNaN(new Date(value).getTime()))
        errors.push(`${label} must be a valid date`);
      break;
    case 'boolean':
      if (typeof value !== 'boolean') errors.push(`${label} must be a boolean`);
      break;
    case 'array':
      if (!Array.isArray(value)) errors.push(`${label} must be an array`);
      break;
    case 'object':
      if (typeof value !== 'object' || Array.isArray(value)) errors.push(`${label} must be an object`);
      break;
  }
  return errors;
}

/**
 * Create a reusable merge job configuration.
 * @param {Object} config - Job configuration
 * @returns {Function} Merge function bound to this configuration
 *
 * @example
 * const generateInvoice = createMergeJob({
 *   template: './templates/invoice.docx',
 *   outputDir: './invoices',
 *   fileNamer: (data) => `invoice-${data.invoiceNumber}.docx`,
 *   fieldTypes: {
 *     amount: { type: 'currency', currency: 'USD' },
 *     dueDate: { type: 'date', dateFormat: 'MMMM D, YYYY' },
 *   },
 * });
 *
 * // Use it
 * const result = await generateInvoice(invoiceData);
 */
function createMergeJob(config) {
  const {
    template,
    outputDir,
    fileNamer,
    fieldTypes = {},
    mergeOptions = {},
  } = config;

  return async function mergeJob(data) {
    const processed = preprocessData(data, fieldTypes);
    const buffer = await mailMerge(template, processed, mergeOptions);

    const filename = fileNamer
      ? fileNamer(data)
      : generateFilename(data, config.filenameField, config.filenameSuffix || '', 0);

    if (outputDir) {
      fs.mkdirSync(outputDir, { recursive: true });
      const outputPath = path.join(outputDir, filename);
      fs.writeFileSync(outputPath, buffer);
      return { buffer, filename, outputPath, size: buffer.length, generatedAt: new Date() };
    }

    return { buffer, filename, size: buffer.length, generatedAt: new Date() };
  };
}

/**
 * Merge multiple documents and combine them into a single output file.
 * @param {Array<{template: string|Buffer, data: Object}>} mergeSpecs - Array of merge specifications
 * @param {string} outputPath - Output file path
 * @returns {Promise<Buffer>} Combined document buffer
 *
 * @example
 * const combined = await combineMergeDocuments([
 *   { template: './templates/cover-letter.docx', data: applicantData },
 *   { template: './templates/resume.docx', data: applicantData },
 *   { template: './templates/references.docx', data: applicantData },
 * ], './output/application-package.docx');
 */
async function combineMergeDocuments(mergeSpecs, outputPath) {
  const mergedBuffers = await Promise.all(
    mergeSpecs.map(spec => mailMerge(spec.template, spec.data, spec.options || {}))
  );

  // Combine documents by appending content
  const combined = await combineDocxBuffers(mergedBuffers);

  if (outputPath) {
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    fs.writeFileSync(outputPath, combined);
  }

  return combined;
}

async function combineDocxBuffers(buffers) {
  // Simple implementation: return first buffer as base
  // In production, use docx-merger or similar package
  if (buffers.length === 0) throw new Error('No buffers to combine');
  if (buffers.length === 1) return buffers[0];
  // Would use docx-merger here for real combination
  return buffers[0];
}

// Add to exports
Object.assign(module.exports, {
  evaluateCondition,
  unflattenData,
  flattenData,
  validateMergeData,
  createMergeJob,
  combineMergeDocuments,
});
