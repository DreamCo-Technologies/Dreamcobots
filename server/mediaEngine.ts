export const LOCAL_VOICE_ID = "dreamco-buddy-local";

export function buildLocalVoicePacket(text: string, voiceId = LOCAL_VOICE_ID) {
  return {
    engine: "dreamco-local-browser-tts",
    provider: "DreamCo",
    voiceId,
    format: "browser-speech-synthesis",
    text,
    audio: null,
    consentRequired: true,
    consentPolicy: "Use only approved voices, scripts, and likenesses. Do not imitate a real person without explicit written consent.",
    clientInstructions: {
      api: "window.speechSynthesis",
      utterance: "new SpeechSynthesisUtterance(packet.text)",
      voiceSelection: "Use a local system voice selected by the user, then cache only the preference name.",
    },
  };
}

function xmlEscape(value: string) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

function wrapSvgText(text: string, maxChars = 34, maxLines = 5) {
  const words = text.replace(/\s+/g, " ").trim().split(" ");
  const lines: string[] = [];
  let current = "";
  for (const word of words) {
    const next = current ? `${current} ${word}` : word;
    if (next.length > maxChars && current) {
      lines.push(current);
      current = word;
    } else {
      current = next;
    }
    if (lines.length === maxLines) break;
  }
  if (current && lines.length < maxLines) lines.push(current);
  return lines.length ? lines : ["DreamCo image ready"];
}

function parseImageSize(size: unknown) {
  const fallback = { width: 1024, height: 1024, label: "1024x1024" };
  if (typeof size !== "string") return fallback;
  const match = size.match(/^(\d{3,4})x(\d{3,4})$/);
  if (!match) return fallback;
  const width = Number(match[1]);
  const height = Number(match[2]);
  const allowed = new Set(["1024x1024", "512x512", "256x256"]);
  return allowed.has(size) ? { width, height, label: size } : fallback;
}

export function buildLocalImagePacket(prompt: string, size: unknown) {
  const parsedSize = parseImageSize(size);
  const lines = wrapSvgText(prompt);
  const lineTspans = lines
    .map((line, index) => `<tspan x="50%" dy="${index === 0 ? 0 : 48}">${xmlEscape(line)}</tspan>`)
    .join("");
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${parsedSize.width}" height="${parsedSize.height}" viewBox="0 0 ${parsedSize.width} ${parsedSize.height}" role="img" aria-label="DreamCo generated preview">
  <defs>
    <linearGradient id="royal" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#111827"/>
      <stop offset="0.45" stop-color="#4f46e5"/>
      <stop offset="1" stop-color="#d97706"/>
    </linearGradient>
    <radialGradient id="glow" cx="50%" cy="38%" r="55%">
      <stop offset="0" stop-color="#ffffff" stop-opacity="0.28"/>
      <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="100%" height="100%" fill="url(#royal)"/>
  <rect width="100%" height="100%" fill="url(#glow)"/>
  <path d="M${parsedSize.width * 0.18} ${parsedSize.height * 0.28} L${parsedSize.width * 0.32} ${parsedSize.height * 0.15} L${parsedSize.width * 0.5} ${parsedSize.height * 0.29} L${parsedSize.width * 0.68} ${parsedSize.height * 0.15} L${parsedSize.width * 0.82} ${parsedSize.height * 0.28} L${parsedSize.width * 0.74} ${parsedSize.height * 0.38} L${parsedSize.width * 0.26} ${parsedSize.height * 0.38} Z" fill="#fbbf24" opacity="0.92"/>
  <circle cx="${parsedSize.width * 0.32}" cy="${parsedSize.height * 0.15}" r="${parsedSize.width * 0.025}" fill="#fde68a"/>
  <circle cx="${parsedSize.width * 0.5}" cy="${parsedSize.height * 0.29}" r="${parsedSize.width * 0.025}" fill="#fde68a"/>
  <circle cx="${parsedSize.width * 0.68}" cy="${parsedSize.height * 0.15}" r="${parsedSize.width * 0.025}" fill="#fde68a"/>
  <text x="50%" y="52%" text-anchor="middle" font-family="Inter, Arial, sans-serif" font-size="${Math.max(22, parsedSize.width * 0.045)}" font-weight="800" fill="#ffffff">${lineTspans}</text>
  <text x="50%" y="82%" text-anchor="middle" font-family="Inter, Arial, sans-serif" font-size="${Math.max(14, parsedSize.width * 0.021)}" letter-spacing="4" fill="#fef3c7">DREAMCO LOCAL IMAGE ENGINE</text>
</svg>`;

  return {
    b64_json: Buffer.from(svg).toString("base64"),
    mimeType: "image/svg+xml",
    format: "svg",
    provider: "DreamCo",
    engine: "dreamco-local-svg",
    size: parsedSize.label,
    prompt,
    fallbackReason: "AI image provider is not configured. Local image generation is available for free.",
  };
}

