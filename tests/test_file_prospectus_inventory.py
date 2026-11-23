import unittest

from tools.build_file_prospectus import list_files


class FileProspectusInventoryTests(unittest.TestCase):
    def test_generated_prospectus_outputs_are_excluded_from_inventory(self):
        self.assertFalse(any(path.startswith("config/generated/file-prospectus/") for path in list_files()))


if __name__ == "__main__":
    unittest.main()
