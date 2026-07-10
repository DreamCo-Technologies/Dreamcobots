from tools.github_pattern_scanner import scan


def test_scanner_records_metadata_without_importing_code():
    config = {
        "policy": "metadata only",
        "queries": [{"id": "agents", "query": "topic:agents", "purpose": "patterns"}],
    }

    def fake_fetch(_url):
        return {
            "items": [
                {
                    "full_name": "owner/project",
                    "html_url": "https://github.com/owner/project",
                    "description": "Example",
                    "stargazers_count": 100,
                    "updated_at": "2026-01-01T00:00:00Z",
                    "language": "Python",
                    "topics": ["agents"],
                    "license": {"spdx_id": "MIT"},
                    "fork": False,
                },
                {"full_name": "owner/fork", "fork": True},
            ]
        }

    report = scan(config, fake_fetch)

    assert report["automatic_code_import"] is False
    assert len(report["findings"][0]["repositories"]) == 1
    assert report["findings"][0]["repositories"][0]["license"] == "MIT"
    assert "code" not in report["findings"][0]["repositories"][0]
