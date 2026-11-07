"""Opt-in OpenAI-compatible chat completion adapter for approved providers/local runtimes.

Uses stdlib HTTPS. No credentials or network calls until explicitly invoked.
Endpoints must be trusted HTTPS URLs, or local loopback HTTP with explicit opt-in.
"""
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

class ChatCompletionsAdapter:
    def __init__(self, *, name, model, base_url, api_key_env, allow_local_http=False, timeout=45):
        u = urllib.parse.urlsplit(base_url)
        local = u.hostname in ("127.0.0.1", "localhost", "::1")
        if u.username or u.password or u.query or u.fragment:
            raise ValueError("Endpoint URL must not contain credentials, query or fragment")
        if not (u.scheme == "https" or (u.scheme == "http" and local and allow_local_http)):
            raise ValueError("HTTPS required except explicitly allowed loopback")
        if not u.hostname:
            raise ValueError("Missing endpoint hostname")
        if timeout < 1 or timeout > 120:
            raise ValueError("Timeout outside approved bounds")
        self.name, self.model, self.base_url = name, model, base_url.rstrip("/")
        self.api_key_env, self.timeout = api_key_env, timeout

    def complete(self, prompt):
        key = os.environ.get(self.api_key_env, "") if self.api_key_env else ""
        if self.api_key_env and not key:
            raise RuntimeError("Configured provider credential is missing")
        payload = json.dumps({"model": self.model, "messages": [
            {"role": "user", "content": prompt}], "temperature": 0,
            "max_tokens": 512}).encode()
        headers = {"Content-Type": "application/json"}
        if key:
            headers["Authorization"] = "Bearer " + key
        req = urllib.request.Request(self.base_url + "/chat/completions",
                                     data=payload, headers=headers, method="POST")
        start = time.monotonic()
        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            if response.status != 200:
                raise RuntimeError("Model endpoint did not return success")
            body = response.read(1024 * 1024)
        data = json.loads(body)
        output = data["choices"][0]["message"]["content"]
        if not isinstance(output, str):
            raise ValueError("Expected a text model response")
        self.last_elapsed_seconds = time.monotonic() - start
        self.last_usage = data.get("usage", {})
        return output
