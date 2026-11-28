from tools.ci_failure_report import build_report, sanitize
from tools.validate_repair_pr import validate_changes


def test_ci_report_redacts_credentials_and_personal_data():
    cleaned = sanitize(
        "api_key=fixture-secret-placeholder "
        "contact person@example.com 123-45-6789"
    )
    assert "fixture-secret-placeholder" not in cleaned
    assert "person@example.com" not in cleaned
    assert "123-45-6789" not in cleaned
    report = build_report("failure output", 1, commit="a" * 40)
    assert report["raw_log_included"] is False
    assert report["failure_excerpt"] == ""
    assert report["status"] == "FAIL"


def test_ci_report_hides_success_log_excerpt():
    report = build_report("all good", 0)
    assert report["status"] == "PASS"
    assert report["failure_excerpt"] == ""


def test_repair_guard_accepts_small_source_change():
    errors = validate_changes(
        "M\tserver/handlers/orders.py",
        "diff --git a/server/handlers/orders.py b/server/handlers/orders.py\n--- a/server/handlers/orders.py\n+++ b/server/handlers/orders.py\n@@ -1 +1 @@\n-old\n+new\n",
    )
    assert errors == []


def test_repair_guard_blocks_workflows_contracts_and_security_tests():
    errors = validate_changes(
        "M\t.github/workflows/ci.yml\nM\tcontracts/policy.schema.json\nM\ttests/test_security_gate.py",
        "diff --git a/x b/x\n",
    )
    assert any("outside the source-code allowlist" in item for item in errors)


def test_repair_guard_blocks_deletions_and_secret_like_additions():
    errors = validate_changes(
        "D\tserver/handlers/orders.py\nM\ttools/helper.py",
        "diff --git a/tools/helper.py b/tools/helper.py\n"
        "@@ -0,0 +1 @@\n+api_key=abcdefghijklmnopqrstuvwxyz123456\n",
    )
    assert any("Only added or modified" in item for item in errors)
    assert any("credential" in item for item in errors)


def test_repair_guard_blocks_its_own_policy_file():
    errors = validate_changes(
        "M\ttools/validate_repair_pr.py",
        "+print('changed')\n",
    )
    assert any("cannot modify itself" in item for item in errors)



def test_repair_guard_allows_new_non_security_test_module():
    errors = validate_changes(
        "A\ttests/test_new_helper.py",
        "diff --git a/tests/test_new_helper.py b/tests/test_new_helper.py\n"
        "new file mode 100644\n--- /dev/null\n+++ b/tests/test_new_helper.py\n"
        "+def test_new_helper(): assert True\n",
    )
    assert errors == []


def test_repair_guard_blocks_modifying_existing_tests():
    errors = validate_changes(
        "M\ttests/test_existing_helper.py",
        "+def test_new_helper(): assert True\n",
    )
    assert any("Only new test files may be added" in item for item in errors)
