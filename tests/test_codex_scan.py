import ast
import json
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools import codex_scan


class CodexScanTests(unittest.TestCase):
    def test_scan_does_not_change_source_or_manifests(self):
        files = codex_scan.tracked_files()
        def snapshot():
            return {f: hashlib.sha256((codex_scan.ROOT/f).read_bytes()).hexdigest() for f in files}
        before = snapshot()
        result = subprocess.run([os.sys.executable, str(codex_scan.ROOT/'tools/codex_scan.py')],
                                cwd=codex_scan.ROOT, capture_output=True, text=True, timeout=120)
        report = json.loads(result.stdout)
        self.assertEqual(0 if report['ok'] else 1, result.returncode)
        self.assertEqual(before, snapshot())
        self.assertEqual(files, codex_scan.tracked_files())
        self.assertTrue(all(value is False for value in report['policy'].values()))

    def test_inline_scripts_exclude_json_and_external_sources(self):
        parser = codex_scan.InlineScripts('index.html')
        parser.feed('<script type="application/ld+json">{"name":"example"}</script>\n<script type="module">import "real-package";</script>\n<script src="remote.js"></script>')
        self.assertEqual([{'file': 'index.html', 'text': 'import "real-package";', 'start_line': 2}], parser.scripts)
        result = subprocess.run(['node', str(codex_scan.ROOT/'tools/scan_node_imports.mjs')],
                                input=json.dumps(parser.scripts), text=True, capture_output=True, check=True)
        data = json.loads(result.stdout)
        self.assertFalse(data['parse_errors'])
        self.assertEqual(2, data['imports'][0]['line'])

    def test_optional_import_cannot_hide_required_use_in_same_file(self):
        visitor = codex_scan.PythonImports()
        visitor.visit(ast.parse('try:\n import missing\nexcept ImportError:\n import fallback\nimport missing\n'))
        self.assertEqual([('missing', 2, True), ('fallback', 4, False), ('missing', 5, False)], visitor.imports)

    def test_nonliteral_python_import_reported(self):
        visitor = codex_scan.PythonImports()
        visitor.visit(ast.parse("importlib.import_module(name)\n__import__('yaml')"))
        self.assertEqual([1], visitor.dynamic)
        self.assertEqual([('yaml', 2, False)], visitor.imports)

    def test_node_parser_ignores_code_examples_in_strings_and_comments(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory)/'example.ts'
            file.write_text('''// import bad from "comment-only";
const sample = `import bad from "example-only"`;
import real from "real-package";
export { thing } from "export-package";
const lazy = import(variable);
const cjs = require("node:fs");
const override = require(process.env.ADAPTER || "fallback-package");
''')
            result = subprocess.run(['node', str(codex_scan.ROOT/'tools/scan_node_imports.mjs')],
                                    input=json.dumps([str(file)]), text=True, capture_output=True, check=True)
            data = json.loads(result.stdout)
            self.assertEqual(['real-package', 'export-package', 'node:fs', 'fallback-package'], [r['specifier'] for r in data['imports']])
            self.assertEqual(2, len(data['dynamic']))

    def test_nested_manifest_lock_required(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'sub').mkdir()
            (root/'sub/package.json').write_text('{"dependencies":{"express":"^5.1.0"}}')
            with patch.object(codex_scan, 'ROOT', root):
                result = codex_scan.audit(['sub/package.json'], node='/nonexistent-node')
            self.assertTrue(any(e['kind'] == 'missing_lockfile' for e in result['errors']))
            self.assertTrue(any(e['kind'] == 'node_scan_unavailable' for e in result['errors']))

    def test_browser_test_default_is_a_direct_dependency(self):
        manifest = json.loads((codex_scan.ROOT/'package.json').read_text())
        self.assertIn('playwright', manifest['devDependencies'])
        result = subprocess.run(['node', '-e', "const {chromium}=require('playwright'); if(typeof chromium.launch!=='function') process.exit(1)"],
                                cwd=codex_scan.ROOT, capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)


if __name__ == '__main__':
    unittest.main()
