from tools.ci_failure_report import build_report


def test_ci_failure_report_redacts_generic_credentials_and_contact_data():
    report = build_report(
        "pytest failed\napi_key=fixture-secret-placeholder\n"
        "email dev@example.test and phone 555-123-4567\n",
        1,
        commit="b" * 40,
    )
    excerpt = report["failure_excerpt"]
    assert "fixture-secret-placeholder" not in excerpt
    assert "dev@example.test" not in excerpt
    assert "555-123-4567" not in excerpt
    assert report["raw_log_included"] is False
    assert report["status"] == "FAIL"


def test_ci_failure_report_omits_success_excerpt():
    report = build_report("tests passed", 0)
    assert report["status"] == "PASS"
    assert report["failure_excerpt"] == ""
