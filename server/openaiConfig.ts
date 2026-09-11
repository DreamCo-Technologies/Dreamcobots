import OpenAI from "openai";

export function getOpenAIProviderConfig() {
  return {
    apiKey:
      process.env.AI_INTEGRATIONS_OPENAI_API_KEY ||
      process.env.OPENAI_API_KEY ||
      process.env.OPENAI_ADMIN_KEY,
    baseURL: process.env.AI_INTEGRATIONS_OPENAI_BASE_URL,
  };
}

export function createOpenAIProviderClient() {
  return new OpenAI(getOpenAIProviderConfig());
}
