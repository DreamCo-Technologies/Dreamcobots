import json
import unittest
from unittest.mock import patch

from buddy.learning.ollama_runtime import OllamaLocalRuntime, validate_local_endpoint


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, limit):
        return self.payload


class OllamaRuntimeTests(unittest.TestCase):
    def test_only_loopback_endpoints_are_allowed(self):
        self.assertEqual(validate_local_endpoint("http://localhost:11434/"), "http://localhost:11434")
        self.assertEqual(validate_local_endpoint("http://127.0.0.1:11434"), "http://127.0.0.1:11434")
        with self.assertRaises(ValueError):
            validate_local_endpoint("https://ollama.example.com")
        with self.assertRaises(ValueError):
            validate_local_endpoint("http://192.0.2.10:11434")

    @patch("buddy.learning.ollama_runtime.urlopen")
    def test_list_and_show_are_read_only_metadata_operations(self, open_url):
        open_url.side_effect = [
            FakeResponse({"models": [{"name": "buddy-test"}]}),
            FakeResponse({"details": {"family": "llama"}, "model_info": {"general.parameter_count": 45000000}, "license": "MIT"}),
        ]
        runtime = OllamaLocalRuntime()
        self.assertEqual(runtime.list_models()["models"][0]["name"], "buddy-test")
        self.assertEqual(open_url.call_args_list[0][0][0].get_method(), "GET")
        shown = runtime.show_model("buddy-test")
        self.assertEqual(shown["parameter_count"], 45000000)
        self.assertTrue(shown["license_metadata_present"])

    @patch("buddy.learning.ollama_runtime.urlopen")
    def test_chat_returns_hashes_and_does_not_claim_training(self, open_url):
        open_url.return_value = FakeResponse({
            "model": "buddy-test",
            "message": {"role": "assistant", "content": "hello"},
            "prompt_eval_count": 3,
            "eval_count": 1,
        })
        result = OllamaLocalRuntime().chat("buddy-test", [{"role": "user", "content": "hello"}])
        self.assertEqual(len(result["prompt_sha256"]), 64)
        self.assertEqual(len(result["response_sha256"]), 64)
        self.assertFalse(result["training_claim"])
        self.assertEqual(result["runtime"], "local_ollama")

    def test_invalid_chat_messages_are_rejected(self):
        with self.assertRaises(ValueError):
            OllamaLocalRuntime().chat("buddy-test", [{"role": "tool", "content": "bad"}])


if __name__ == "__main__":
    unittest.main()
