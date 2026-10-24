import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest

from tools.validate_repository_json import prefix_class, validate


class RepositoryJsonValidationTests(unittest.TestCase):
    def test_valid_json_and_excluded_directories_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'good.json').write_text('{"ok":true}')
            for ignored in ('.git', 'node_modules'):
                (root / ignored).mkdir()
                (root / ignored / 'ignored.json').write_text('not json')
            self.assertEqual(validate(root), [])

    def test_malformed_generated_json_is_not_silently_repaired(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / 'website/data/pages-connection-index.json'
            path.parent.mkdir(parents=True)
            payload = b'Warning: truncated output\n{"files": []}'
            path.write_bytes(payload)
            problems = validate(root)
            self.assertEqual(len(problems), 1)
            self.assertIn('prefix=tool_truncation_marker', problems[0])
            self.assertIn('sha256=' + hashlib.sha256(payload).hexdigest(), problems[0])
            self.assertEqual(path.read_bytes(), payload)
            self.assertNotIn('"files"', problems[0])

    def test_empty_and_invalid_utf8_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'empty.json').write_bytes(b'')
            (root / 'bad.json').write_bytes(b'\xff')
            issues = validate(root)
            self.assertEqual(len(issues), 2)
            self.assertTrue(any('prefix=empty' in issue for issue in issues))
            self.assertTrue(any('UnicodeDecodeError' in issue for issue in issues))

    def test_index_mismatch_identifies_worktree_mutation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            path = root / 'index.json'
            path.write_text('{"valid":true}')
            subprocess.run(['git', 'add', 'index.json'], cwd=root, check=True)
            path.write_text('not json')
            self.assertIn('index_match=false', validate(root)[0])

    def test_known_prefixes(self):
        self.assertEqual(prefix_class(b'version https://git-lfs.github.com/spec/v1\n'), 'lfs_pointer')
        self.assertEqual(prefix_class(b'\xef\xbb\xbf{}'), 'utf8_bom')
        self.assertEqual(prefix_class(b'  \n  '), 'whitespace_only')
        self.assertEqual(prefix_class(b'  [1]'), 'json_like')


if __name__ == '__main__':
    unittest.main()
