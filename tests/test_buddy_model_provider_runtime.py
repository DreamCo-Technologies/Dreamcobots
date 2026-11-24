import json, os, unittest
from unittest.mock import patch
from buddy.models.provider_runtime import ModelServingError, chat_completion

class FakeResponse:
    status = 200
    def __enter__(self): return self
    def __exit__(self, *_args): return False
    def read(self):
        return json.dumps({"model":"gpt-5.4-mini","choices":[{"message":{"role":"assistant","content":"ready"}}],
                           "usage":{"prompt_tokens":5,"completion_tokens":2,"total_tokens":7}}).encode()

class ProviderRuntimeTests(unittest.TestCase):
    def test_requires_paid_approval(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY":"secret"}, clear=True):
            with self.assertRaisesRegex(ModelServingError, "approval"):
                chat_completion("openai","gpt-5.4-mini",[{"role":"user","content":"hi"}])
    def test_provider_and_model_are_allowlisted(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY":"secret"}, clear=True):
            with self.assertRaisesRegex(ModelServingError,"not_allowlisted"):
                chat_completion("unknown","model-x",[{"role":"user","content":"hi"}],paid_approval_id="A")
            with self.assertRaisesRegex(ModelServingError,"not_allowlisted"):
                chat_completion("openai","unlisted-model",[{"role":"user","content":"hi"}],paid_approval_id="A")
    def test_requires_provider_secret(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ModelServingError,"credential_not_configured"):
                chat_completion("openai","gpt-5.4-mini",[{"role":"user","content":"hi"}],paid_approval_id="A")
    def test_valid_call_returns_minimal_evidence(self):
        captured = {}
        def opener(request, timeout):
            captured.update(url=request.full_url, auth=request.get_header("Authorization"),
                            request_id=request.get_header("X-dreamco-request-id"),
                            timeout=timeout, body=json.loads(request.data))
            return FakeResponse()
        with patch.dict(os.environ, {"OPENAI_API_KEY":"secret"}, clear=True):
            result=chat_completion("openai","gpt-5.4-mini",[{"role":"user","content":"hi"}],
                                   paid_approval_id="approval-1",opener=opener)
        self.assertEqual(result["status"],"COMPLETED")
        self.assertEqual(result["response_text"],"ready")
        self.assertEqual(result["usage"]["total_tokens"],7)
        self.assertFalse(result["credentials_emitted"])
        self.assertFalse(result["training_use_authorized"])
        self.assertEqual(result["data_classification"], "public")
        self.assertEqual(result["output_training_permission"], "UNKNOWN")
        self.assertTrue(result["request_id"].startswith("infer-"))
        self.assertEqual(captured["url"],"https://api.openai.com/v1/chat/completions")
        self.assertEqual(captured["request_id"], result["request_id"])
        self.assertEqual(captured["auth"],"Bearer secret")
        self.assertEqual(captured["body"]["model"],"gpt-5.4-mini")
    def test_provider_data_classification_is_enforced(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY":"secret"}, clear=True):
            with self.assertRaisesRegex(ModelServingError, "classification"):
                chat_completion("openai", "gpt-5.4-mini", [{"role":"user","content":"private"}],
                                paid_approval_id="A", data_classification="internal")
            with self.assertRaisesRegex(ModelServingError, "unknown_data_classification"):
                chat_completion("openai", "gpt-5.4-mini", [{"role":"user","content":"x"}],
                                paid_approval_id="A", data_classification="unknown")

    def test_openrouter_requires_explicit_model_allowlist_and_public_data(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ModelServingError, "not_allowlisted"):
                chat_completion("openrouter", "vendor/model", [{"role":"user","content":"public"}],
                                paid_approval_id="A")
        with patch.dict(os.environ, {"DREAMCO_OPENROUTER_ALLOWED_MODELS":"vendor/model"}, clear=True):
            with self.assertRaisesRegex(ModelServingError, "classification"):
                chat_completion("openrouter", "vendor/model", [{"role":"user","content":"internal"}],
                                paid_approval_id="A", data_classification="internal")
            with self.assertRaisesRegex(ModelServingError, "credential_not_configured"):
                chat_completion("openrouter", "vendor/model", [{"role":"user","content":"public"}],
                                paid_approval_id="A", data_classification="public")

    def test_invalid_message_and_token_limits_are_rejected(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY":"secret"}, clear=True):
            with self.assertRaises(ModelServingError):
                chat_completion("openai","gpt-5.4-mini",[{"role":"tool","content":"hi"}],paid_approval_id="A")
            with self.assertRaises(ModelServingError):
                chat_completion("openai","gpt-5.4-mini",[{"role":"user","content":"hi"}],paid_approval_id="A",max_tokens=9000)

if __name__ == "__main__": unittest.main()
