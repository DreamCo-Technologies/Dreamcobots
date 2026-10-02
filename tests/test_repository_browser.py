import importlib.util
import json
import subprocess
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def load(name):
 spec=importlib.util.spec_from_file_location(name,ROOT/'tools'/f'{name}.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
GEN=load('generate_command_center_data');CONNECT=load('connect_repository_pages')
class RepositoryBrowserTests(unittest.TestCase):
 def test_every_tracked_path_is_indexed_including_generated_and_case_collisions(self):
  expected=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().strip('\0').split('\0'))
  data=GEN.build_repository_browser();actual={x['path'] for x in data['items']}
  self.assertEqual(expected,actual);self.assertEqual(len(data['items']),len(expected))
  self.assertIn('website/data/command-center/repository-browser.json',actual)
  self.assertIn('.github/PULL_REQUEST_TEMPLATE.md',actual);self.assertIn('.github/pull_request_template.md',actual)
  for row in data['items']:self.assertEqual(set(row),{'path','area','kind','protected'})
 def test_secret_related_paths_are_metadata_only_and_flagged(self):
  rows={x['path']:x for x in GEN.build_repository_browser()['items']}
  self.assertTrue(rows['.env.example']['protected'])
 def test_every_page_has_shared_controls(self):
  for p in (ROOT/'website').rglob('*.html'):self.assertTrue(CONNECT.connected(p.read_text()),p.name)
  for name in ('nav.js','desk-chrome.js'):self.assertIn('data-repository-actions',(ROOT/'website'/name).read_text())
 def test_all_registered_bots_have_a_resolvable_prospectus(self):
  registry=json.loads((ROOT/'config/master_bot_registry.json').read_text());cache={};seen=set()
  for bot in registry['bots']:
   ident=bot['identity'];slug=ident['slug'];self.assertNotIn(slug,seen);seen.add(slug)
   division=ident['division']
   if division not in cache:cache[division]=json.loads((ROOT/'website/data/bot-fleet'/f'{division}.json').read_text())['bots']
   matches=[x for x in cache[division] if x['identity']['slug']==slug];self.assertEqual(len(matches),1,slug)
   self.assertTrue(matches[0]['prospectus']['mission'],slug)
   self.assertTrue(matches[0]['capabilities'],slug)
  self.assertEqual(len(seen),1051)
if __name__=='__main__':unittest.main()
