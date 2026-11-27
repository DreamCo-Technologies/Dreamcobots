from __future__ import annotations

import io
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError

from tools.refresh_public_fiscal_data import fetch_json


class PublicFiscalFetchRetryTests(unittest.TestCase):
    @patch("tools.refresh_public_fiscal_data.time.sleep")
    @patch("tools.refresh_public_fiscal_data.urllib.request.urlopen")
    def test_retries_transient_url_error_then_succeeds(self, urlopen, sleep):
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.read.return_value = b'{"data":[{"record_date":"2026-11-24"}]}'
        urlopen.side_effect = [URLError("temporary DNS failure"), response]

        result = fetch_json("https://example.gov/data")

        self.assertEqual(result["data"][0]["record_date"], "2026-11-24")
        self.assertEqual(urlopen.call_count, 2)
        sleep.assert_called_once_with(1.0)

    @patch("tools.refresh_public_fiscal_data.time.sleep")
    @patch("tools.refresh_public_fiscal_data.urllib.request.urlopen")
    def test_retries_http_429_and_honors_bounded_retry_after(self, urlopen, sleep):
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.read.return_value = b'{"results":[]}'
        limited = HTTPError("https://example.gov/data", 429, "rate limited", {"Retry-After": "3"}, io.BytesIO())
        urlopen.side_effect = [limited, response]

        self.assertEqual(fetch_json("https://example.gov/data"), {"results": []})
        sleep.assert_called_once_with(3.0)

    @patch("tools.refresh_public_fiscal_data.time.sleep")
    @patch("tools.refresh_public_fiscal_data.urllib.request.urlopen")
    def test_does_not_retry_permanent_client_errors(self, urlopen, sleep):
        denied = HTTPError("https://example.gov/data", 403, "forbidden", {}, io.BytesIO())
        urlopen.side_effect = denied

        with self.assertRaises(HTTPError):
            fetch_json("https://example.gov/data")

        self.assertEqual(urlopen.call_count, 1)
        sleep.assert_not_called()

    @patch("tools.refresh_public_fiscal_data.time.sleep")
    @patch("tools.refresh_public_fiscal_data.urllib.request.urlopen")
    def test_exhausted_retries_raise_the_last_upstream_error(self, urlopen, sleep):
        urlopen.side_effect = URLError("upstream unavailable")

        with self.assertRaises(URLError):
            fetch_json("https://example.gov/data", attempts=3)

        self.assertEqual(urlopen.call_count, 3)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [1.0, 2.0])


if __name__ == "__main__":
    unittest.main()
