/** Parse source, never import/evaluate it. Input: JSON array of file paths on stdin. */
import fs from 'node:fs';
import path from 'node:path';
import { builtinModules } from 'node:module';
import { parse } from '@babel/parser';

const builtin = new Set(builtinModules.map(name => name.replace(/^node:/, '')));
const files = JSON.parse(fs.readFileSync(0, 'utf8'));
const imports = [], dynamic = [], parseErrors = [];
for (const input of files) {
  const file = typeof input === 'string' ? input : input.file;
  const text = typeof input === 'string' ? fs.readFileSync(file, 'utf8') : input.text;
  let source;
  try {
    source = parse(text, {sourceType: 'unambiguous', sourceFilename: file,
      startLine: typeof input === 'string' ? 1 : input.start_line,
      startIndex: 0, startColumn: 0,
      createImportExpressions: true, attachComment: false,
      plugins: [...(/\.[cm]?tsx?$/.test(file) ? ['typescript'] : []),
        ...(/\.[jt]sx$/.test(file) ? ['jsx'] : [])]});
  } catch (error) {
    parseErrors.push({file, line: error.loc?.line, message: error.message});
    continue;
  }
  function record(specifier, node, kind) {
    const line = node.loc?.start.line;
    const name = specifier?.type === 'StringLiteral' ? specifier.value
      : specifier?.type === 'TemplateLiteral' && specifier.expressions.length === 0
        ? specifier.quasis[0].value.cooked : null;
    if (typeof name !== 'string') {
      dynamic.push({file, line, kind});
      // Audit a statically known fallback without pretending the override is known.
      if (specifier?.type === 'LogicalExpression' && ['||', '??'].includes(specifier.operator)) {
        if (specifier.right.type === 'StringLiteral') record(specifier.right, node, 'dynamic-fallback');
      }
      return;
    }
    const category = name.startsWith('node:') || builtin.has(name) ? 'builtin'
      : name.startsWith('.') || name.startsWith('/') ? 'relative'
      : /^(?:@\/|@shared\/|@assets\/)/.test(name) ? 'alias'
      : /^(?:https?:|data:)/.test(name) ? 'remote' : 'package';
    const packageName = name.startsWith('@') ? name.split('/').slice(0,2).join('/') : name.split('/')[0];
    imports.push({file, line, kind, specifier: name, category,
      ...(category === 'package' ? {package: packageName} : {})});
  }
  function visit(node) {
    if (!node || typeof node !== 'object') return;
    if (['ImportDeclaration', 'ExportNamedDeclaration', 'ExportAllDeclaration'].includes(node.type)) {
      if (node.source) record(node.source, node, 'static');
    } else if (node.type === 'TSImportEqualsDeclaration' && node.moduleReference.type === 'TSExternalModuleReference') {
      record(node.moduleReference.expression, node, 'import-equals');
    } else if (node.type === 'ImportExpression') {
      record(node.source, node, 'dynamic');
    } else if (node.type === 'CallExpression' &&
        (node.callee.type === 'Import' || (node.callee.type === 'Identifier' && node.callee.name === 'require'))) {
      record(node.arguments[0], node, 'call');
    }
    for (const [key, value] of Object.entries(node)) {
      if (['loc', 'start', 'end', 'extra', 'comments', 'tokens'].includes(key)) continue;
      if (Array.isArray(value)) value.forEach(visit);
      else if (value && typeof value === 'object' && value.type) visit(value);
    }
  }
  visit(source);
}
console.log(JSON.stringify({imports, dynamic, parse_errors: parseErrors}));
