import importlib.util
import subprocess
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('library', ROOT/'tools/build_repository_library.py')
library = importlib.util.module_from_spec(spec); spec.loader.exec_module(library)
class RepositoryLibraryTests(unittest.TestCase):
    def test_all_tracked_files_have_lookup_entries(self):
        expected = {p for p in subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0') if p and (ROOT/p).is_file()}
        rows = library.build()['files']
        self.assertEqual({r['path'] for r in rows}, expected)
        self.assertEqual(len(rows),len(expected))
    def test_plans_and_documents_are_searchable_without_copying_code(self):
        rows = {r['path']:r for r in library.build()['files']}
        self.assertEqual(rows['docs/DREAMCO_MASTER_PLAN.md']['kind'],'Plans')
        self.assertTrue(rows['docs/DREAMCO_MASTER_PLAN.md']['words'])
        self.assertEqual(rows['website/repository.js']['words'],'')
        self.assertEqual(rows['website/repository.js']['summary'],'')
if __name__ == '__main__': unittest.main()
