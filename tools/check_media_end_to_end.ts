import assert from "node:assert/strict";
import { buildLocalImagePacket, buildLocalVoicePacket } from "../server/mediaEngine";

const voice = buildLocalVoicePacket("Buddy media check");
assert.equal(voice.provider, "DreamCo");
assert.equal(voice.engine, "dreamco-local-browser-tts");
assert.equal(voice.format, "browser-speech-synthesis");
assert.equal(voice.text, "Buddy media check");
assert.equal(voice.clientInstructions.api, "window.speechSynthesis");

const image = buildLocalImagePacket("Royal Buddy command center preview", "512x512");
assert.equal(image.provider, "DreamCo");
assert.equal(image.engine, "dreamco-local-svg");
assert.equal(image.mimeType, "image/svg+xml");
assert.equal(image.size, "512x512");
assert.ok(image.b64_json.length > 1000);

const decodedSvg = Buffer.from(image.b64_json, "base64").toString("utf8");
assert.match(decodedSvg, /^<svg /);
assert.match(decodedSvg, /DREAMCO LOCAL IMAGE ENGINE/);
assert.match(decodedSvg, /Royal Buddy/);

const browserImageSrc = `data:${image.mimeType};base64,${image.b64_json}`;
assert.match(browserImageSrc, /^data:image\/svg\+xml;base64,/);

console.log(JSON.stringify({
  ok: true,
  voice: {
    provider: voice.provider,
    engine: voice.engine,
    format: voice.format,
  },
  image: {
    provider: image.provider,
    engine: image.engine,
    mimeType: image.mimeType,
    size: image.size,
    bytes: decodedSvg.length,
  },
}, null, 2));

