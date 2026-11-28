from tools.ci_failure_report import sanitize
from tools.validate_repair_pr import validate_changes


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
        "before\\n" + begin + "\\n"
        "private-key-body-line-one\\nprivate-key-body-line-two\\n"
        + end + "\\nafter"
    )
    cleaned = sanitize(pem)
    assert "private-key-body-line-one" not in cleaned
    assert "private-key-body-line-two" not in cleaned
    assert end not in cleaned
    assert "[REDACTED_PRIVATE_KEY]" in cleaned


def test_sanitizer_redacts_unterminated_private_key_to_end_of_input():
    begin = "-----BEGIN " + "PRIVATE KEY-----"
    cleaned = sanitize("prefix\\n" + begin + "\\nsecret-material-without-footer")
    assert "secret-material-without-footer" not in cleaned
    assert "[REDACTED_PRIVATE_KEY]" in cleaned


def test_repair_guard_blocks_protected_basename_in_nested_allowed_directory():
    errors = validate_changes(
        "M\\ttools/nested/.env",
        "diff --git a/tools/nested/.env b/tools/nested/.env\\n"
        "@@ -1 +1 @@\\n-old\\n+new\\n",
    )
    assert any("Protected or credential-bearing file" in error for error in errors)


def test_repair_guard_rejects_binary_changes():
    errors = validate_changes(
        "M\\tserver/assets/model.bin",
        "diff --git a/server/assets/model.bin b/server/assets/model.bin\\n"
        "Binary files a/server/assets/model.bin and b/server/assets/model.bin differ\\n",
    )
    assert any("Binary changes are not allowed" in error for error in errors)


def test_repair_guard_scans_added_lines_starting_with_multiple_plus_signs():
    errors = validate_changes(
        "M\\tserver/handlers/example.py",
        "diff --git a/server/handlers/example.py b/server/handlers/example.py\\n"
        "@@ -1 +1,2 @@\\n-old\\n++api_key=abcdefghijklmnopqrstuvwxyz123456\\n",
    )
    assert any("credential" in error.lower() for error in errors)


def test_repair_guard_counts_added_lines_that_look_like_diff_headers_inside_hunks():
    added_header_like_lines = "\\n".join("+++ suspicious-added-line" for _ in range(1501))
    errors = validate_changes(
        "M\\tserver/handlers/example.py",
        "diff --git a/server/handlers/example.py b/server/handlers/example.py\\n"
        "@@ -1,0 +1,1501 @@\\n" + added_header_like_lines + "\\n",
    )
    assert any("1,500-line limit" in error for error in errors)


def test_repair_guard_still_accepts_eligible_text_change():
    errors = validate_changes(
        "M\\tserver/handlers/orders.py",
        "diff --git a/server/handlers/orders.py b/server/handlers/orders.py\\n"
        "@@ -1 +1 @@\\n-old\\n+new\\n",
    )
    assert errors == []
