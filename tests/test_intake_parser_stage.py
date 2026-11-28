from importlib import import_module


def test_safe_media_type_accepts_valid_mime_and_rejects_arbitrary_values():
    safe_media_type = import_module("stages.02_intake_parser.__main__").safe_media_type
    assert safe_media_type("application/json; charset=utf-8") == "application/json"
    assert safe_media_type("text/plain") == "text/plain"
    assert safe_media_type("email@example.test") == "unspecified"
    assert safe_media_type("application/json\nX-Injected: yes") == "unspecified"
