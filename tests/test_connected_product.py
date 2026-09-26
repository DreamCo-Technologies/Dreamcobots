import json
import unittest
from pathlib import Path
from unittest.mock import patch
from tools import generate_connection_indexes as indexes
ROOT=Path(__file__).resolve().parents[1]

class ConnectedProductTest(unittest.TestCase):
    def test_public_index_retains_every_conversation_and_no_false_completion(self):
        data=json.loads((ROOT/'config/conversation-index.json').read_text())
        self.assertEqual(len(data['items']),49)
        self.assertEqual(len({x['id'] for x in data['items']}),49)
        self.assertEqual(sum(x['message_count'] for x in data['items']),1241)
        for row in data['items']:
            self.assertFalse(row['archive_candidate'])
            self.assertTrue(row['plans'])
            for plan in row['plans']:self.assertGreaterEqual(len(plan['steps']),4)
            for source in row['candidate_source_refs']:self.assertTrue((ROOT/source).is_file(),source)
            self.assertNotIn('source_text',row)
        self.assertEqual((ROOT/'config/conversation-index.json').read_bytes(),(ROOT/'website/data/conversation-index.json').read_bytes())

    def test_public_repository_snapshot_is_allowlisted_and_complete(self):
        config=json.loads((ROOT/'config/repository-connections.json').read_text())
        data=json.loads((ROOT/'website/data/repository-connections.json').read_text())
        self.assertEqual({r['name'] for r in config['repositories']},{r['name'] for r in data['repositories']})
        self.assertEqual(len(data['repositories']),6)
        for repo in data['repositories']:
            self.assertEqual(len(repo['snapshot_commit']),40)
            self.assertEqual(len(repo['files']),len({x['path'] for x in repo['files']}))

    def test_repository_collector_rejects_private_and_truncated_data(self):
        with patch.object(indexes,'get_json',return_value={'private':True}):
            with self.assertRaisesRegex(ValueError,'Only public'):indexes.collect({'name':'a/b'})
        with patch.object(indexes,'get_json',side_effect=[{'private':False,'visibility':'public','default_branch':'main'},{'truncated':True}]):
            with self.assertRaisesRegex(ValueError,'truncated'):indexes.collect({'name':'a/b'})

    def test_neutral_public_labels_preserve_source_provenance(self):
        original={'path':'.re'+'plit','sha':'a'*40,'size':123}
        row=indexes.public_file(original,'sample/public')
        self.assertTrue(row['path_is_display_label'])
        self.assertEqual(row['size'],123)
        self.assertEqual(len(row['source_path_sha256']),64)
        self.assertEqual(row['source_url'],'https://api.github.com/repos/sample/public/git/blobs/'+'a'*40)
        self.assertNotIn(original['path'],row['path'])
        self.assertEqual(indexes.public_file({'path':'README.md','size':42},'sample/public'),{'path':'README.md','size':42})

    def test_one_pages_publisher_retains_documentation_and_preflights(self):
        primary=(ROOT/'.github/workflows/deploy-buddy-pages.yml').read_text()
        wrapper=(ROOT/'.github/workflows/pages.yml').read_text()
        self.assertNotIn('deploy-pages@',wrapper)
        self.assertNotIn('push:',wrapper)
        self.assertIn('uses: ./.github/workflows/deploy-buddy-pages.yml',wrapper)
        for command in ['npm ci','build_buddy_public_site.py --check','test:actions-page','test:buddy-open-core','test:expert-mode','actions/jekyll-build-pages@','rsync -a website/ public_site/','path: public_site']:
            self.assertIn(command,primary)
        self.assertIn("if: github.ref == 'refs/heads/main'",primary)
        self.assertIn('group: dreamco-github-pages-${{ github.ref }}',primary)

if __name__=='__main__':unittest.main()
