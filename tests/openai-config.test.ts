import assert from "node:assert/strict";
import test from "node:test";

import { getOpenAIProviderConfig } from "../server/openaiConfig";

function withEnv(env: Record<string, string | undefined>, fn: () => void) {
  const keys = Object.keys(env);
  const previous = new Map(keys.map((key) => [key, process.env[key]]));
  try {
    for (const [key, value] of Object.entries(env)) {
      if (value === undefined) {
        delete process.env[key];
      } else {
        process.env[key] = value;
      }
    }
    fn();
  } finally {
    for (const key of keys) {
      const value = previous.get(key);
      if (value === undefined) {
        delete process.env[key];
      } else {
        process.env[key] = value;
      }
    }
  }
}

test("uses AI integration key before generic OpenAI key", () => {
  withEnv(
    {
      AI_INTEGRATIONS_OPENAI_API_KEY: "sk-ai-integrations",
      OPENAI_API_KEY: "sk-openai",
      OPENAI_ADMIN_KEY: "sk-admin",
      AI_INTEGRATIONS_OPENAI_BASE_URL: "https://example.test/v1",
    },
    () => {
      assert.deepEqual(getOpenAIProviderConfig(), {
        apiKey: "sk-ai-integrations",
        baseURL: "https://example.test/v1",
      });
    }
  );
});

test("falls back to OPENAI_API_KEY for existing GitHub and local setups", () => {
  withEnv(
    {
      AI_INTEGRATIONS_OPENAI_API_KEY: undefined,
      OPENAI_API_KEY: "sk-openai",
      OPENAI_ADMIN_KEY: "sk-admin",
      AI_INTEGRATIONS_OPENAI_BASE_URL: undefined,
    },
    () => {
      assert.deepEqual(getOpenAIProviderConfig(), {
        apiKey: "sk-openai",
        baseURL: undefined,
      });
    }
  );
});
