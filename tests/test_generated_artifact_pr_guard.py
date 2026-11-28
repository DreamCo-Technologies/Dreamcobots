import unittest

from tools.validate_generated_artifact_pr import validate_changes


class GeneratedArtifactPRGuardTests(unittest.TestCase):
    def test_small_generated_json_diff_is_allowed(self):
        status = "M\tconfig/generated/example.json"
        diff = (
            "diff --git a/config/generated/example.json b/config/generated/example.json\n"
            "--- a/config/generated/example.json\n"
            "+++ b/config/generated/example.json\n"
            "@@ -1 +1 @@\n"
            "-{\"version\":1}\n"
            "+{\"version\":2}\n"
        )
        self.assertEqual(validate_changes(status, diff), [])

    def test_oversized_generated_map_is_blocked(self):
        status = "A\tconfig/generated/buddy-fleet-execution-map.json"
        additions = "\n".join("+{\"bot_id\":%d}" % index for index in range(1501))
        diff = (
            "diff --git a/config/generated/buddy-fleet-execution-map.json b/config/generated/buddy-fleet-execution-map.json\n"
            "new file mode 100644\n"
            "--- /dev/null\n"
            "+++ b/config/generated/buddy-fleet-execution-map.json\n"
            "@@ -0,0 +1,1501 @@\n" + additions + "\n"
        )
        self.assertTrue(any("1,500-line" in error for error in validate_changes(status, diff)))

    def test_source_and_workflow_paths_are_blocked(self):
        for path in ("tools/repair.py", ".github/workflows/unsafe.yml", "config/secrets/token.json"):
            status = f"M\t{path}"
            diff = f"diff --git a/{path} b/{path}\n--- a/{path}\n+++ b/{path}\n@@ -1 +1 @@\n-old\n+new\n"
            self.assertTrue(validate_changes(status, diff), path)

    def test_binary_files_and_secrets_are_blocked(self):
        binary_status = "A\twebsite/data/image.bin"
        binary_diff = (
            "diff --git a/website/data/image.bin b/website/data/image.bin\n"
            "Binary files /dev/null and b/website/data/image.bin differ\n"
        )
        self.assertTrue(validate_changes(binary_status, binary_diff))
        secret_diff = (
            "diff --git a/config/generated/credentials.json b/config/generated/credentials.json\n"
            "--- a/config/generated/credentials.json\n"
            "+++ b/config/generated/credentials.json\n"
            "@@ -0,0 +1 @@\n"
            "+{\"api_key\":\"NOT_A_REAL_KEY\"}\n"
        )
        self.assertTrue(validate_changes("A\tconfig/generated/credentials.json", secret_diff))
        ordinary_path_diff = secret_diff.replace("credentials.json", "catalog.json")
        self.assertTrue(
            any("credential" in error.lower() for error in
                validate_changes("A\tconfig/generated/catalog.json", ordinary_path_diff))
        )


if __name__ == "__main__":
    unittest.main()
