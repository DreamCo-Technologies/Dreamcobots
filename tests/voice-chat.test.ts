/**
 * Integration test: Voice Chat End-to-End Pipeline
 *
 * Verifies the full pipeline:
 *   base64 WAV → POST /api/conversations/:id/voice
 *   → SSE stream → user_transcript event → done event
 *
 * Self-contained: starts and stops its own server so it can run in CI
 * without a pre-running dev server.
 *
 * Run with:
 *   npx tsx tests/voice-chat.test.ts
 *
 * Requires: AI_INTEGRATIONS_OPENAI_API_KEY and DATABASE_URL env vars.
 */

import { spawn, type ChildProcess } from "child_process";
import { setTimeout as sleep } from "timers/promises";

const TEST_PORT = 5099;
const BASE_URL = `http://localhost:${TEST_PORT}`;
const SERVER_STARTUP_TIMEOUT_MS = 30_000;
const VOICE_RESPONSE_TIMEOUT_MS = 90_000;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function buildSilentWav(durationSeconds = 0.5): Buffer {
  const sampleRate = 16000;
  const numSamples = Math.floor(sampleRate * durationSeconds);
  const dataSize = numSamples * 2; // 16-bit PCM = 2 bytes/sample
  const buf = Buffer.alloc(44 + dataSize, 0);

  buf.write("RIFF", 0, "ascii");
  buf.writeUInt32LE(36 + dataSize, 4);
  buf.write("WAVE", 8, "ascii");
  buf.write("fmt ", 12, "ascii");
  buf.writeUInt32LE(16, 16);        // chunk size
  buf.writeUInt16LE(1, 20);         // PCM format
  buf.writeUInt16LE(1, 22);         // 1 channel (mono)
  buf.writeUInt32LE(sampleRate, 24);
  buf.writeUInt32LE(sampleRate * 2, 28); // byte rate
  buf.writeUInt16LE(2, 32);         // block align
  buf.writeUInt16LE(16, 34);        // bits per sample
  buf.write("data", 36, "ascii");
  buf.writeUInt32LE(dataSize, 40);
  // remaining bytes are 0 (silence)

  return buf;
}

function assert(condition: boolean, message: string): void {
  if (!condition) throw new Error(`ASSERTION FAILED: ${message}`);
}

async function waitForServer(url: string, timeoutMs: number): Promise<void> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      const res = await fetch(`${url}/api/conversations`);
      if (res.ok || res.status === 404) return; // server is up
    } catch {
      // not ready yet
    }
    await sleep(500);
  }
  throw new Error(`Server at ${url} did not become ready within ${timeoutMs}ms`);
}

// ---------------------------------------------------------------------------
// Server lifecycle
// ---------------------------------------------------------------------------

function startServer(): ChildProcess {
  const server = spawn(
    "npx",
    ["tsx", "server/index.ts"],
    {
      env: { ...process.env, PORT: String(TEST_PORT), NODE_ENV: "test" },
      stdio: ["ignore", "pipe", "pipe"],
    }
  );
  server.stdout?.on("data", (d: Buffer) => process.stdout.write(`[server] ${d}`));
  server.stderr?.on("data", (d: Buffer) => process.stderr.write(`[server:err] ${d}`));
  return server;
}

// ---------------------------------------------------------------------------
// Test
// ---------------------------------------------------------------------------

async function runVoiceChatTest(): Promise<void> {
  console.log("\nVoice Chat Integration Test");
  console.log("===========================");

  let server: ChildProcess | null = null;
  let conversationId: number | null = null;

  // If a server is already running on TEST_PORT (e.g., local dev), skip spawn
  let serverAlreadyRunning = false;
  try {
    await waitForServer(BASE_URL, 1_000);
    serverAlreadyRunning = true;
    console.log(`  Using existing server at ${BASE_URL}`);
  } catch {
    console.log(`  Starting server on port ${TEST_PORT}...`);
    server = startServer();
    await waitForServer(BASE_URL, SERVER_STARTUP_TIMEOUT_MS);
    console.log("  ✓ Server is ready");
  }

  try {
    // ------------------------------------------------------------------
    // Step 1: Create conversation
    // ------------------------------------------------------------------
    console.log("\nStep 1: Create test conversation...");
    const createRes = await fetch(`${BASE_URL}/api/conversations`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: "Voice Chat Test (automated)" }),
    });
    assert(createRes.status === 201, `Expected 201, got ${createRes.status}`);
    const conversation = await createRes.json() as { id: number; title: string };
    conversationId = conversation.id;
    console.log(`  ✓ Created conversation id=${conversationId}`);

    // ------------------------------------------------------------------
    // Step 2: Build WAV buffer
    // ------------------------------------------------------------------
    console.log("\nStep 2: Build minimal WAV audio (0.5s 16kHz mono PCM16 silence)...");
    const wavBuffer = buildSilentWav(0.5);
    const base64Audio = wavBuffer.toString("base64");
    console.log(`  ✓ WAV: ${wavBuffer.length} bytes  Base64: ${base64Audio.length} chars`);

    // ------------------------------------------------------------------
    // Step 3: POST to voice endpoint
    // ------------------------------------------------------------------
    console.log(`\nStep 3: POST /api/conversations/${conversationId}/voice...`);
    const voiceRes = await fetch(`${BASE_URL}/api/conversations/${conversationId}/voice`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ audio: base64Audio, voice: "alloy" }),
    });

    if (voiceRes.status !== 200) {
      const body = await voiceRes.text();
      throw new Error(`Expected 200 SSE response, got ${voiceRes.status}. Body: ${body}`);
    }

    const contentType = voiceRes.headers.get("content-type") ?? "";
    assert(
      contentType.includes("text/event-stream"),
      `Expected Content-Type text/event-stream, got: ${contentType}`
    );
    console.log(`  ✓ Status: ${voiceRes.status}  Content-Type: ${contentType}`);

    // ------------------------------------------------------------------
    // Step 4: Parse SSE stream
    // ------------------------------------------------------------------
    console.log("\nStep 4: Parse SSE stream and verify events...");

    const seenTypes = new Set<string>();
    let userTranscript: string | null = null;
    let finalTranscript: string | null = null;

    const reader = voiceRes.body!.getReader();
    const decoder = new TextDecoder();
    let sseBuffer = "";
    let timedOut = false;

    const timeoutId = setTimeout(() => {
      timedOut = true;
      reader.cancel().catch(() => {});
    }, VOICE_RESPONSE_TIMEOUT_MS);

    try {
      outer: while (true) {
        const { done, value } = await reader.read();
        if (done || timedOut) break;

        sseBuffer += decoder.decode(value, { stream: true });
        const lines = sseBuffer.split("\n");
        sseBuffer = lines.pop() ?? "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          try {
            const event = JSON.parse(line.slice(6)) as {
              type: string;
              data?: string;
              transcript?: string;
              error?: string;
            };
            seenTypes.add(event.type);

            if (event.type === "user_transcript") {
              userTranscript = event.data ?? "";
              console.log(`  ✓ user_transcript: "${userTranscript}"`);
            }
            if (event.type === "done") {
              finalTranscript = event.transcript ?? "";
              console.log(`  ✓ done event. assistant transcript: "${finalTranscript.slice(0, 60)}..."`);
              break outer;
            }
            if (event.type === "error") {
              throw new Error(`Voice pipeline error: ${event.error}`);
            }
          } catch (e) {
            if (e instanceof SyntaxError) continue;
            throw e;
          }
        }
      }
    } finally {
      clearTimeout(timeoutId);
    }

    assert(!timedOut, `SSE stream timed out after ${VOICE_RESPONSE_TIMEOUT_MS}ms — pipeline did not complete`);
    assert(
      seenTypes.has("user_transcript"),
      `Missing user_transcript event. Seen: [${[...seenTypes].join(", ")}]`
    );
    assert(
      seenTypes.has("done"),
      `Missing done event. Seen: [${[...seenTypes].join(", ")}]`
    );
    assert(userTranscript !== null, "user_transcript data was null");
    assert(finalTranscript !== null, "done transcript was null");

    console.log(`\n  All event types seen: [${[...seenTypes].join(", ")}]`);
  } finally {
    // Cleanup conversation
    if (conversationId !== null) {
      console.log(`\nStep 5: Cleanup — DELETE conversation ${conversationId}...`);
      try {
        const delRes = await fetch(`${BASE_URL}/api/conversations/${conversationId}`, {
          method: "DELETE",
        });
        console.log(delRes.status === 204 ? "  ✓ Deleted" : `  ⚠ DELETE returned ${delRes.status}`);
      } catch {
        console.warn("  ⚠ Cleanup fetch failed (non-critical)");
      }
    }

    // Stop server if we started it
    if (server && !serverAlreadyRunning) {
      console.log("\nStopping test server...");
      server.kill("SIGTERM");
      await sleep(1000);
      if (!server.killed) server.kill("SIGKILL");
      console.log("  ✓ Server stopped");
    }
  }

  console.log("\n✅ PASSED — Voice chat pipeline (STT → GPT audio → SSE) works end-to-end.\n");
}

runVoiceChatTest().catch((err) => {
  console.error(`\n❌ FAILED — ${err.message}\n`);
  process.exit(1);
});
