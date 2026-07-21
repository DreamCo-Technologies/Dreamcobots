'use strict';

/**
 * DreamCo — Environment Validation
 *
 * Fails fast at startup if required environment variables are missing,
 * preventing cryptic runtime errors deep inside the system.
 */

const REQUIRED_VARS = ['ADMIN_KEY'];

/**
 * Validate that all required environment variables are present.
 * Throws an Error listing every missing variable.
 */
function validateEnv() {
  const missing = REQUIRED_VARS.filter((key) => !process.env[key]);

  if (missing.length > 0) {
    throw new Error(
      `Missing required environment variable(s): ${missing.join(', ')}\n` +
        'Please set them in your .env file or host environment.'
    );
  }
}

module.exports = { validateEnv, REQUIRED_VARS };
