'use strict';

module.exports = {
  env: {
    node: true,
    es2021: true,
    jest: true,
  },
  extends: ['eslint:recommended'],
  parserOptions: {
    ecmaVersion: 2021,
  },
  rules: {
    'no-console': 'off',
    'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
    'no-var': 'error',
    'prefer-const': 'warn',
    eqeqeq: ['error', 'always', { null: 'ignore' }],
    curly: ['error', 'all'],
    semi: ['error', 'always'],
    quotes: ['error', 'single', { avoidEscape: true }],
  },
  ignorePatterns: [
    'node_modules/',
    'coverage/',
    'dist/',
    'bots/',
    '*.py',
    'public/docx/',
    'empire-os/',
    'dreamco/',
    'Dreamcobots/',
  ],
  overrides: [
    // ES module files (import/export syntax) — applies to src/, dreamco-control-tower/
    {
      files: [
        'src/**/*.js',
        'src/**/*.ts',
        'dreamco-control-tower/**/*.js',
        'dreamco-control-tower/**/*.jsx',
        'dreamco-control-tower/**/*.ts',
        'dreamco-control-tower/**/*.tsx',
      ],
      env: {
        browser: true,
      },
      parserOptions: {
        ecmaVersion: 2021,
        sourceType: 'module',
        ecmaFeatures: {
          jsx: true,
        },
      },
    },
    // Browser-side scripts that use DOM globals (document, window, prompt, etc.)
    {
      files: [
        'dreamco/frontend/**/*.js',
        'public/**/*.js',
        'frontend/**/*.js',
        'dashboard/static/**/*.js',
      ],
      env: {
        browser: true,
        node: false,
      },
    },
  ],
};
