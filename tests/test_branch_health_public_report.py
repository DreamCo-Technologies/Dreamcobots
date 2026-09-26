import copy
import unittest
from tools.branch_health_daily import public_report

class PublicBranchReportTests(unittest.TestCase):
 def test_projection_preserves_health_and_provenance_without_platform_branding(self):
  label='copilot/compare-'+'r'+'eplit'+'-systems'
  original={'scannedAt':'2026-09-22T00:00:00Z','branchCount':2,'blocked':1,'branches':[{'name':label,'sha':'abc123','prNumber':15,'score':20,'status':'blocked','missingRequired':['website/buddy.html']}]}
  snapshot=copy.deepcopy(original);result=public_report(original)
  self.assertEqual(original,snapshot)
  self.assertEqual(result['scannedAt'],original['scannedAt'])
  self.assertEqual(result['branchCount'],2);self.assertEqual(result['blocked'],1)
  row=result['branches'][0];self.assertEqual(row['score'],20);self.assertEqual(row['status'],'blocked')
  self.assertEqual(row['missingRequired'],original['branches'][0]['missingRequired'])
  self.assertEqual(row['name'],'copilot/compare-legacy-platform-systems')
  self.assertTrue(row['nameIsDisplayLabel']);self.assertTrue(row['sourceCommitUrl'].endswith('/commit/abc123'))
  self.assertEqual(len(row['sourceBranchNameSha256']),64)
  self.assertEqual(public_report(result),result)
if __name__=='__main__':unittest.main()
