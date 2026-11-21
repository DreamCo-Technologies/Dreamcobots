import os
import unittest
from unittest.mock import patch

from buddy.datasets import sources


class _Response:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self, size=-1):
        return b"{}"


class DatasetSourceTokenScopeTests(unittest.TestCase):
    def _request_for(self, url):
        with patch.dict(os.environ, {"DREAMCO_ALLOW_SOURCE_NETWORK": "1", "GITHUB_TOKEN": "test-token"}):
            with patch("urllib.request.urlopen", return_value=_Response()) as mocked:
                sources._get_json(url)
                return mocked.call_args.args[0]

    def test_token_is_sent_to_exact_github_api_host(self):
        request = self._request_for("https://api.github.com/repos/example/repo")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-token")

    def test_token_is_not_sent_to_lookalike_or_embedded_hosts(self):
        urls = (
            "https://api.github.com.evil.example/repos/example/repo",
            "https://evil.example/api.github.com/repos/example/repo",
            "https://api.github.com@evil.example/repos/example/repo",
            "http://api.github.com/repos/example/repo",
        )
        for url in urls:
            with self.subTest(url=url):
                request = self._request_for(url)
                self.assertIsNone(request.get_header("Authorization"))


if __name__ == "__main__":
    unittest.main()
