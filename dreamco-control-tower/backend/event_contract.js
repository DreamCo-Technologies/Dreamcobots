import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const CONTRACT_FILE = path.join(__dirname, '../../config/shared_event_contract.json');

export function loadEventContract() {
  return JSON.parse(fs.readFileSync(CONTRACT_FILE, 'utf8'));
}

export function validateEventEnvelope(event, contract = loadEventContract()) {
  if (!event || typeof event !== 'object') {
    throw new Error('event envelope must be an object');
  }

  for (const field of contract.required_fields || []) {
    if (!(field in event)) {
      throw new Error(`missing required field: ${field}`);
    }
  }

  if (typeof event.event_type !== 'string' || !event.event_type.includes('.')) {
    throw new Error('event_type must follow <family>.<subtype>');
  }
  if (typeof event.bot_id !== 'string' || !event.bot_id.trim()) {
    throw new Error('bot_id must be a non-empty string');
  }
  if (typeof event.intent !== 'string' || !event.intent.trim()) {
    throw new Error('intent must be a non-empty string');
  }
  if (typeof event.timestamp !== 'string' || Number.isNaN(Date.parse(event.timestamp))) {
    throw new Error('timestamp must be an ISO-8601 string');
  }
  if (!contract.status_values?.includes(event.status)) {
    throw new Error(`status must be one of: ${(contract.status_values || []).join(', ')}`);
  }
  if (typeof event.correlation_id !== 'string' || !event.correlation_id.trim()) {
    throw new Error('correlation_id must be a non-empty string');
  }

  return true;
}
