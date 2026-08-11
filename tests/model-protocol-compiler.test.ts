import assert from "node:assert/strict";
import test from "node:test";

import { compileModelTask, protocolForProvider } from "../server/model-protocol-compiler";

const task = {
  objective: "Inspect the repository evidence and return a structured repair plan.",
  systemInstructions: "Preserve safety and truth boundaries.",
  tools: [{
    name: "search_repo",
    description: "Search repository files.",
    inputSchema: { type: "object", properties: { query: { type: "string" } }, required: ["query"] },
  }],
  requireStructuredOutput: true,
  outputSchema: { type: "object", properties: { status: { type: "string" } }, required: ["status"] },
};

test("OpenAI-style compilation preserves tools and structured output", () => {
  const result = compileModelTask(task, "openai_responses", "test-openai");
  assert.equal(result.request.model, "test-openai");
  assert.equal(result.request.tools.length, 1);
  assert.equal(result.toolDialect, "openai_function_tool");
});

test("Anthropic compilation uses input_schema tools", () => {
  const result = compileModelTask(task, "anthropic_messages", "test-anthropic");
  assert.equal(result.request.tools[0]?.name, "search_repo");
  assert.ok("input_schema" in result.request.tools[0]!);
});

test("Gemini compilation uses function declarations", () => {
  const result = compileModelTask(task, "google_generate_content", "test-gemini");
  assert.equal(result.request.tools[0]?.functionDeclarations[0]?.name, "search_repo");
});

test("Mistral and OpenAI-compatible providers preserve function schemas", () => {
  for (const protocol of ["mistral_chat", "openai_compatible"] as const) {
    const result = compileModelTask(task, protocol, `test-${protocol}`);
    assert.equal(result.request.tools[0]?.function.name, "search_repo");
  }
});

test("provider mapping covers frontier and international connectors", () => {
  assert.equal(protocolForProvider("openai"), "openai_responses");
  assert.equal(protocolForProvider("anthropic"), "anthropic_messages");
  assert.equal(protocolForProvider("google"), "google_generate_content");
  assert.equal(protocolForProvider("mistral"), "mistral_chat");
  assert.equal(protocolForProvider("deepseek"), "openai_compatible");
  assert.equal(protocolForProvider("alibaba"), "openai_compatible");
  assert.equal(protocolForProvider("moonshot"), "openai_compatible");
  assert.equal(protocolForProvider("meta"), "openai_compatible");
});
