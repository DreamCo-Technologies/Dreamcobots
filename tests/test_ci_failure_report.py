from tools.ci_failure_report import build_report, sanitize


def test_ci_failure_report_never_includes_raw_log_content():
    raw = "pytest failed\\napi_key=fixture-secret-placeholder\\nemail dev@example.test"
    report = build_report(raw, 1, commit="b" * 40)
    assert report["status"] == "FAIL"
    assert report["raw_log_included"] is False
    assert report["log_excerpt_omitted"] is True
    assert report["failure_excerpt"] == ""
    assert "fixture-secret-placeholder" not in str(report)
    assert "dev@example.test" not in str(report)


def test_ci_failure_report_omits_success_excerpt():
    report = build_report("tests passed", 0)
    assert report["status"] == "PASS"
    assert report["failure_excerpt"] == ""
    assert report["log_excerpt_omitted"] is True


def test_sanitizer_redacts_common_credentials_and_contact_data():
    cleaned = sanitize(
        "api_key=fixture-secret-placeholder "
        "dev@example.test 555-123-4567 123-45-6789"
    )
    assert "fixture-secret-placeholder" not in cleaned
    assert "dev@example.test" not in cleaned
    assert "555-123-4567" not in cleaned
    assert "123-45-6789" not in cleaned
