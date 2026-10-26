import unittest
from unittest.mock import patch, MagicMock
from buddy.certification.provider_adapters import ChatCompletionsAdapter

class ProviderAdapterTests(unittest.TestCase):
    def test_reject_insecure_remote(self):
        with self.assertRaises(ValueError):
            ChatCompletionsAdapter(name="bad", model="x", base_url="http://example.com/v1", api_key_env="KEY")
    def test_reject_local_without_optin(self):
        with self.assertRaises(ValueError):
            ChatCompletionsAdapter(name="local", model="x", base_url="http://127.0.0.1:1234/v1", api_key_env="")
    def test_missing_key(self):
        a=ChatCompletionsAdapter(name="remote",model="x",base_url="https://example.com/v1",api_key_env="BUDDY_TEST_KEY_NOT_SET")
        with patch.dict("os.environ", {"BUDDY_TEST_KEY_NOT_SET":""}):
            with self.assertRaises(RuntimeError):
                a.complete("test")
    def test_mocked_request(self):
        a=ChatCompletionsAdapter(name="remote",model="x",base_url="https://example.com/v1",api_key_env="")
        resp=MagicMock()
        resp.status=200
        resp.read.return_value=b'{"choices":[{"message":{"content":"14"}}],"usage":{"total_tokens":2}}'
        resp.__enter__.return_value=resp
        with patch("urllib.request.urlopen",return_value=resp):
            self.assertEqual(a.complete("question"),"14")
            self.assertEqual(a.last_usage["total_tokens"],2)

if __name__=="__main__":
    unittest.main()
