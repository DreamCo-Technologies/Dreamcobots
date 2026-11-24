import json
import unittest
from buddy.models.provider_runtime import GovernedProviderRuntime, ProviderRuntimeError, validate_provider

def provider(**changes):
    value = {"provider_id":"local_test","protocol":"openai_compatible_chat_completions",
        "lifecycle_state":"TESTED","enabled":True,"base_url_env":"LOCAL_BASE_URL",
        "api_key_env":"LOCAL_API_KEY","allowed_models":["dreamco/test-model:v1"],
        "data_classification_max":"restricted","output_training_permission":"PROHIBITED"}
    value.update(changes)
    return value

class FakeResponse:
    status = 200
    def __init__(self, payload): self.payload = payload
    def __enter__(self): return self
    def __exit__(self, *_args): return False
    def read(self): return json.dumps(self.payload).encode()

class ProviderRuntimeTests(unittest.TestCase):
    def test_blocked_provider_rejected(self):
        with self.assertRaises(ProviderRuntimeError): validate_provider(provider(lifecycle_state="CONFIGURED"))
        with self.assertRaises(ProviderRuntimeError): validate_provider(provider(enabled=False))
    def test_model_allowlist_and_approval_required(self):
        runtime = GovernedProviderRuntime([provider()], environ={"LOCAL_BASE_URL":"https://inference.example.test/v1","LOCAL_API_KEY":"secret"})
        with self.assertRaises(ProviderRuntimeError):
            runtime.infer("local_test","other-model",[{"role":"user","content":"hi"}],approval_id="ok")
        with self.assertRaises(ProviderRuntimeError):
            runtime.infer("local_test","dreamco/test-model:v1",[{"role":"user","content":"hi"}],approval_id="")
    def test_data_classification_enforced(self):
        runtime = GovernedProviderRuntime([provider(data_classification_max="internal")], environ={"LOCAL_BASE_URL":"https://inference.example.test/v1","LOCAL_API_KEY":"secret"})
        with self.assertRaises(ProviderRuntimeError):
            runtime.infer("local_test","dreamco/test-model:v1",[{"role":"user","content":"hi"}],approval_id="approved",data_classification="confidential")
    def test_success_emits_redacted_evidence_and_training_policy(self):
        calls = []
        def opener(request, timeout):
            calls.append((request,timeout))
            return FakeResponse({"id":"response-1","choices":[{"message":{"content":"hello"}}],"usage":{"total_tokens":3}})
        runtime = GovernedProviderRuntime([provider()],opener=opener,environ={"LOCAL_BASE_URL":"https://inference.example.test/v1","LOCAL_API_KEY":"do-not-leak"})
        result = runtime.infer("local_test","dreamco/test-model:v1",[{"role":"user","content":"hi"}],approval_id="approved")
        self.assertEqual(result["status"],"COMPLETED")
        self.assertFalse(result["training_use_authorized"])
        self.assertFalse(result["credentials_emitted"])
        self.assertNotIn("do-not-leak",json.dumps(result))
        self.assertEqual(calls[0][1],30)
    def test_provider_errors_are_redacted(self):
        def broken(_request,timeout): raise RuntimeError("secret-bearing provider exception")
        runtime = GovernedProviderRuntime([provider()],opener=broken,environ={"LOCAL_BASE_URL":"https://inference.example.test/v1","LOCAL_API_KEY":"secret"})
        with self.assertRaisesRegex(ProviderRuntimeError,"RuntimeError"):
            runtime.infer("local_test","dreamco/test-model:v1",[{"role":"user","content":"hi"}],approval_id="approved")

if __name__ == "__main__": unittest.main()
