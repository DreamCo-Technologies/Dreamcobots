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

def test_sanitizer_redacts_quoted_credentials_with_spaces_and_closing_quote():
    cleaned = sanitize(
        'api_key="secret value with spaces" password=\'another secret value\''
    )
    assert "secret value with spaces" not in cleaned
    assert "another secret value" not in cleaned
    assert cleaned.count("[REDACTED_CREDENTIAL]") == 2


def test_sanitizer_redacts_complete_multiline_pem_block():
    begin = "-----BEGIN RSA " + "PRIVATE KEY-----"
    end = "-----END RSA " + "PRIVATE KEY-----"
    pem = (
        "before\n" + begin + "\n"
        "private-key-body-line-one\nprivate-key-body-line-two\n"
        + end + "\nafter"
    )
    cleaned = sanitize(pem)
    assert "private-key-body-line-one" not in cleaned
    assert "private-key-body-line-two" not in cleaned
    assert end not in cleaned
    assert "[REDACTED_PRIVATE_KEY]" in cleaned


def test_sanitizer_redacts_unterminated_private_key_to_end_of_input():
    begin = "-----BEGIN " + "PRIVATE KEY-----"
    cleaned = sanitize("prefix\n" + begin + "\nsecret-material-without-footer")
    assert "secret-material-without-footer" not in cleaned
    assert "[REDACTED_PRIVATE_KEY]" in cleaned

