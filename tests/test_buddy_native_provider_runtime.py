import json,os,unittest
from unittest.mock import patch
from buddy.models.native_provider_runtime import NativeProviderError,anthropic_messages,gemini_generate_content

class Response:
 def __init__(self,payload): self.payload=payload;self.status=200
 def __enter__(self): return self
 def __exit__(self,*args): return False
 def read(self): return json.dumps(self.payload).encode()

class NativeProviderTests(unittest.TestCase):
 def test_anthropic_native_protocol_and_evidence(self):
  captured={}
  def opener(req,timeout):
   captured.update(url=req.full_url,key=req.get_header("X-api-key"),version=req.get_header("Anthropic-version"),body=json.loads(req.data))
   return Response({"model":"claude-test","content":[{"type":"text","text":"teacher response"}],"usage":{"input_tokens":11,"output_tokens":7}})
  with patch.dict(os.environ,{"ANTHROPIC_API_KEY":"secret"},clear=True):
   result=anthropic_messages("claude-test",[{"role":"user","content":"teach"}],allowed_models=["claude-test"],paid_approval_id="approval-1",opener=opener)
  self.assertEqual(result["response_text"],"teacher response")
  self.assertEqual(result["usage"]["prompt_tokens"],11)
  self.assertEqual(captured["url"],"https://api.anthropic.com/v1/messages")
  self.assertEqual(captured["key"],"secret")
  self.assertEqual(captured["body"]["messages"][0]["role"],"user")
  self.assertFalse(result["credentials_emitted"])
 def test_gemini_native_protocol_and_evidence(self):
  captured={}
  def opener(req,timeout):
   captured.update(url=req.full_url,key=req.get_header("X-goog-api-key"),body=json.loads(req.data))
   return Response({"candidates":[{"content":{"parts":[{"text":"Gemini teacher"}]}}],
                    "usageMetadata":{"promptTokenCount":3,"candidatesTokenCount":4,"totalTokenCount":7}})
  with patch.dict(os.environ,{"GEMINI_API_KEY":"secret"},clear=True):
   result=gemini_generate_content("gemini-test",[{"role":"assistant","content":"prior"},{"role":"user","content":"next"}],allowed_models=["gemini-test"],paid_approval_id="approval-2",opener=opener)
  self.assertEqual(result["response_text"],"Gemini teacher")
  self.assertEqual(captured["key"],"secret")
  self.assertTrue(captured["url"].endswith("/models/gemini-test:generateContent"))
  self.assertEqual(captured["body"]["contents"][0]["role"],"model")
 def test_approval_and_allowlist_are_mandatory(self):
  with patch.dict(os.environ,{"ANTHROPIC_API_KEY":"secret","GEMINI_API_KEY":"secret"},clear=True):
   with self.assertRaisesRegex(NativeProviderError,"approval"):
    anthropic_messages("x",[{"role":"user","content":"hi"}],allowed_models=["x"],paid_approval_id="")
   with self.assertRaisesRegex(NativeProviderError,"allowlist"):
    gemini_generate_content("x",[{"role":"user","content":"hi"}],allowed_models=["y"],paid_approval_id="A")
 def test_missing_credentials_block_calls(self):
  with patch.dict(os.environ,{},clear=True):
   with self.assertRaisesRegex(NativeProviderError,"credential_not_configured"):
    anthropic_messages("x",[{"role":"user","content":"hi"}],allowed_models=["x"],paid_approval_id="A")
   with self.assertRaisesRegex(NativeProviderError,"credential_not_configured"):
    gemini_generate_content("x",[{"role":"user","content":"hi"}],allowed_models=["x"],paid_approval_id="A")
 def test_invalid_roles_and_bounds_rejected(self):
  with patch.dict(os.environ,{"GEMINI_API_KEY":"secret"},clear=True):
   with self.assertRaises(NativeProviderError):
    gemini_generate_content("x",[{"role":"system","content":"blocked"}],allowed_models=["x"],paid_approval_id="A")
   with self.assertRaises(NativeProviderError):
    gemini_generate_content("x",[{"role":"user","content":"hi"}],allowed_models=["x"],paid_approval_id="A",max_tokens=9000)

if __name__=="__main__": unittest.main()
