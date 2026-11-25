import tempfile,unittest
from pathlib import Path
from tools.scan_repository_benchmark_artifacts import scan_repository

class RepositoryBenchmarkArtifactScannerTests(unittest.TestCase):
 def test_discovers_benchmark_paths_and_classifies_them(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)
   for rel in ["benchmarks/suite/run.py","tests/test_benchmark_runner.py","docs/BENCHMARK_GUIDE.md",".github/workflows/benchmark.yml","config/benchmark-index.json","src/agent.py"]:
    path=root/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_text("# fixture",encoding="utf-8")
   result=scan_repository(root)
   self.assertEqual(result["artifact_count"],5)
   by_path={row["path"]:row for row in result["artifacts"]}
   self.assertEqual(by_path["tests/test_benchmark_runner.py"]["artifact_type"],"test_or_evaluation")
   self.assertEqual(by_path[".github/workflows/benchmark.yml"]["artifact_type"],"workflow")
   self.assertFalse(by_path["benchmarks/suite/run.py"]["measured"])
 def test_excludes_generated_and_dependency_directories(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)
   for rel in ["node_modules/benchmark/index.js",".git/benchmark.json","dist/benchmark.js","src/benchmark.py"]:
    path=root/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_text("x",encoding="utf-8")
   result=scan_repository(root)
   self.assertEqual([row["path"] for row in result["artifacts"]],["src/benchmark.py"])
 def test_path_inventory_does_not_claim_exhaustive_content_coverage(self):
  with tempfile.TemporaryDirectory() as tmp:
   result=scan_repository(Path(tmp))
   self.assertEqual(result["scan_mode"],"path_name_only")
   self.assertIn("does not inspect all textual references",result["truth_boundary"])

if __name__=="__main__":unittest.main()
