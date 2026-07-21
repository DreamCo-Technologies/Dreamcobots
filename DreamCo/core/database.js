'use strict';

/**
 * DreamCo — Database Layer
 *
 * Lightweight file-based persistence so bot data survives restarts.
 * Each collection maps to a JSON file inside the configured data directory.
 *
 * Swap the implementation here when moving to a real DB — callers stay the same.
 */

const fs = require('fs');
const path = require('path');
const config = require('./config');

const DATA_DIR = path.resolve(config.data.dir);

/** Ensure the data directory exists. */
function _ensureDir() {
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }
}

/**
 * Resolve the full path to a collection file.
 * @param {string} collection
 * @returns {string}
 */
function _collectionPath(collection) {
  return path.join(DATA_DIR, `${collection}.json`);
}

/**
 * Load all documents from a collection.
 * @param {string} collection
 * @returns {Object[]}
 */
function load(collection) {
  _ensureDir();
  const file = _collectionPath(collection);
  if (!fs.existsSync(file)) {
    return [];
  }
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch (err) {
    console.error(`[database] Failed to parse collection "${collection}":`, err.message);
    return [];
  }
}

/**
 * Persist a new document into a collection.
 * @param {string} collection
 * @param {Object} data
 * @returns {Object} The saved document (with added timestamp)
 */
function save(collection, data) {
  _ensureDir();
  const existing = load(collection);
  const doc = { ...data, savedAt: new Date().toISOString() };
  existing.push(doc);
  fs.writeFileSync(_collectionPath(collection), JSON.stringify(existing, null, 2));
  return doc;
}

/**
 * Find documents in a collection that match a predicate.
 * @param {string} collection
 * @param {(doc: Object) => boolean} predicate
 * @returns {Object[]}
 */
function find(collection, predicate) {
  return load(collection).filter(predicate);
}

/**
 * Count documents in a collection.
 * @param {string} collection
 * @returns {number}
 */
function count(collection) {
  return load(collection).length;
}

module.exports = { save, load, find, count };
