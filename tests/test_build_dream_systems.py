import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import build_dream_systems as builder


class SystemBuilderTest(unittest.TestCase):
    def test_generated_package_imports_and_runs_preserved_catalog(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inputs = root / 'App_bots'
            inputs.mkdir()
            bots = [{'slug': 'fixture-bot', 'description': 'Preserved original behavior'}]
            (inputs / 'DreamFixture.json').write_text(json.dumps({'bots': bots}))
            with patch.multiple(builder, ROOT=root, APP_BOTS=inputs, SYSTEMS=root / 'systems'), patch.object(sys, 'argv', ['builder']):
                self.assertEqual(builder.main(), 0)
            package = root / 'systems' / 'DreamFixture'
            spec = importlib.util.spec_from_file_location('generated_fixture', package / '__init__.py')
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            result = subprocess.run([sys.executable, str(package / 'system_orchestrator.py')], capture_output=True, text=True, check=True)
            output = json.loads(result.stdout)
            self.assertEqual(output['system'], 'DreamFixture')
            self.assertEqual(output['bot_count'], 1)
            self.assertEqual(output['mode'], 'catalog')
            self.assertEqual(output['task'], {})
            self.assertEqual(json.loads((package / 'bots.json').read_text())['bots'], bots)


if __name__ == '__main__':
    unittest.main()
