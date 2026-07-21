#!/usr/bin/env python3
"""Generate a local Buddy song test packet for owner voice and image."""

from __future__ import annotations

import argparse
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "reports" / "buddy_song_voice_image_test.json"
OUT_MD = ROOT / "reports" / "BUDDY_SONG_VOICE_IMAGE_TEST.md"
OUT_HTML = ROOT / "reports" / "buddy-song-voice-image-test.html"


LYRICS = {
    "title": "Built With My Own Hands",
    "genre": "motivational hip-hop soul",
    "bpm": 92,
    "key": "A minor",
    "hook": "I built it with my own hands, now Buddy light the way. We turn the work into a plan, then make a brighter day.",
    "verse": [
        "Started with a laptop and a dream in motion",
        "Bots in the dashboard, focus like an ocean",
        "Every safe step leaves a trail I can see",
        "DreamCo in the room, building what I believe",
    ],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_packet() -> dict[str, Any]:
    return {
        "schema": "dreamco.buddy_song_voice_image_test.v1",
        "generated_at": utc_now(),
        "mode": "free_local_browser_test",
        "mission": "Test Buddy's song-with-my-voice-and-image workflow without uploading private media or using paid services.",
        "song": LYRICS,
        "local_test_capabilities": [
            "preview your selected image locally in the browser",
            "play your selected voice sample locally in the browser",
            "speak the hook with local browser speech synthesis",
            "store a consent checklist and production packet",
            "prepare the handoff path for a real approved voice model later",
        ],
        "what_this_does_not_do": [
            "does not upload your image",
            "does not upload your voice sample",
            "does not clone your voice",
            "does not publish, message, or sell anything",
            "does not use paid cloud services",
        ],
        "approval_required_for": [
            "voice cloning",
            "face or likeness generation",
            "public release",
            "commercial use",
            "third-party model or API use",
            "uploading private media",
        ],
        "consent_metadata_required": {
            "person": "owner",
            "voice_owner_confirmed": True,
            "image_owner_confirmed": True,
            "private_media_upload_allowed": False,
            "local_browser_only": True,
            "label_synthetic_media": True,
        },
        "files": {
            "html": str(OUT_HTML.relative_to(ROOT)),
            "markdown": str(OUT_MD.relative_to(ROOT)),
            "json": str(OUT_JSON.relative_to(ROOT)),
        },
    }


def write_markdown(packet: dict[str, Any]) -> None:
    song = packet["song"]
    lines = [
        "# Buddy Song Voice Image Test",
        "",
        packet["mission"],
        "",
        "## Song Packet",
        "",
        f"- Title: {song['title']}",
        f"- Genre: {song['genre']}",
        f"- BPM: {song['bpm']}",
        f"- Key: {song['key']}",
        "",
        "## Hook",
        "",
        song["hook"],
        "",
        "## Verse",
        "",
    ]
    lines.extend(f"- {line}" for line in song["verse"])
    lines.extend(["", "## Local Test Capabilities", ""])
    lines.extend(f"- {item}" for item in packet["local_test_capabilities"])
    lines.extend(["", "## Approval Required For", ""])
    lines.extend(f"- {item}" for item in packet["approval_required_for"])
    lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def write_html(packet: dict[str, Any]) -> None:
    song = packet["song"]
    verse = "<br />".join(html.escape(line) for line in song["verse"])
    hook = html.escape(song["hook"])
    approval_items = "".join(f"<li>{html.escape(item)}</li>" for item in packet["approval_required_for"])
    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Buddy Song Voice Image Test</title>
  <style>
    body {{ margin: 0; font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #101418; color: #f8fafc; }}
    main {{ max-width: 1100px; margin: 0 auto; padding: 32px 18px 54px; }}
    header {{ border-bottom: 1px solid #334155; padding-bottom: 20px; margin-bottom: 22px; }}
    h1 {{ margin: 0 0 8px; font-size: clamp(30px, 5vw, 56px); }}
    h2 {{ margin: 0 0 10px; font-size: 22px; }}
    section {{ background: #18212b; border: 1px solid #334155; border-radius: 8px; padding: 18px; margin: 14px 0; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; }}
    label {{ display: block; margin: 10px 0 6px; color: #cbd5e1; }}
    input, button, textarea {{ font: inherit; }}
    input[type="file"], textarea {{ width: 100%; box-sizing: border-box; background: #0f172a; color: #e2e8f0; border: 1px solid #475569; border-radius: 6px; padding: 10px; }}
    button {{ border: 0; border-radius: 6px; padding: 10px 14px; background: #22c55e; color: #052e16; font-weight: 800; cursor: pointer; margin: 8px 8px 0 0; }}
    button.secondary {{ background: #f8fafc; color: #111827; }}
    img {{ width: 100%; max-height: 420px; object-fit: contain; border-radius: 8px; background: #0f172a; border: 1px solid #334155; }}
    audio {{ width: 100%; margin-top: 10px; }}
    .notice {{ background: #2a1f08; border-color: #a16207; color: #fde68a; }}
    .song {{ font-size: 18px; line-height: 1.6; }}
    .meta {{ color: #94a3b8; }}
  </style>
</head>
<body>
  <main>
    <header>
      <p class="meta">Buddy free/local browser test</p>
      <h1>{html.escape(song['title'])}</h1>
      <p>{html.escape(packet['mission'])}</p>
    </header>

    <section class="notice">
      <h2>Consent-Safe Test</h2>
      <p>This page keeps your selected voice and image files inside your browser. It does not upload, clone, publish, or use paid services.</p>
    </section>

    <div class="grid">
      <section>
        <h2>Your Image</h2>
        <label for="imageInput">Choose your photo locally</label>
        <input id="imageInput" type="file" accept="image/*" />
        <p class="meta">Preview only. Not uploaded.</p>
        <img id="preview" alt="Selected image preview" />
      </section>

      <section>
        <h2>Your Voice Sample</h2>
        <label for="voiceInput">Choose your voice sample locally</label>
        <input id="voiceInput" type="file" accept="audio/*" />
        <audio id="voiceAudio" controls></audio>
        <p class="meta">Playback only. This test does not clone your voice.</p>
      </section>
    </div>

    <section>
      <h2>Song Packet</h2>
      <p class="meta">{html.escape(song['genre'])} · {song['bpm']} BPM · {html.escape(song['key'])}</p>
      <div class="song">
        <strong>Hook</strong><br />
        <span id="hook">{hook}</span><br /><br />
        <strong>Verse</strong><br />
        {verse}
      </div>
      <button id="speakHook">Speak hook with local browser voice</button>
      <button id="stopSpeech" class="secondary">Stop</button>
    </section>

    <section>
      <h2>Approval Required Before Real Voice/Image Generation</h2>
      <ul>{approval_items}</ul>
    </section>
  </main>

  <script>
    const imageInput = document.getElementById('imageInput');
    const preview = document.getElementById('preview');
    imageInput.addEventListener('change', () => {{
      const file = imageInput.files && imageInput.files[0];
      if (!file) return;
      preview.src = URL.createObjectURL(file);
    }});

    const voiceInput = document.getElementById('voiceInput');
    const voiceAudio = document.getElementById('voiceAudio');
    voiceInput.addEventListener('change', () => {{
      const file = voiceInput.files && voiceInput.files[0];
      if (!file) return;
      voiceAudio.src = URL.createObjectURL(file);
    }});

    document.getElementById('speakHook').addEventListener('click', () => {{
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(document.getElementById('hook').textContent);
      utterance.rate = 0.94;
      utterance.pitch = 0.92;
      window.speechSynthesis.speak(utterance);
    }});
    document.getElementById('stopSpeech').addEventListener('click', () => window.speechSynthesis.cancel());
  </script>
</body>
</html>
"""
    OUT_HTML.write_text(page, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Buddy local song/voice/image test packet.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    packet = build_packet()
    if args.check:
        existing = json.loads(OUT_JSON.read_text(encoding="utf-8")) if OUT_JSON.exists() else {}
        ok = OUT_JSON.exists() and OUT_MD.exists() and OUT_HTML.exists()
        ok = ok and existing.get("schema") == packet["schema"]
        ok = ok and existing.get("song", {}).get("title") == packet["song"]["title"]
        print(json.dumps({"ok": ok, "html": str(OUT_HTML.relative_to(ROOT))}, indent=2))
        return 0 if ok else 1

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(packet)
    write_html(packet)
    print(json.dumps({"ok": True, "html": str(OUT_HTML.relative_to(ROOT)), "json": str(OUT_JSON.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
