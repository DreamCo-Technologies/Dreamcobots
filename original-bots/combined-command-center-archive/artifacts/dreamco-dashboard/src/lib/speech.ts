import { useState, useEffect, useCallback } from "react";

/**
 * DreamCo Voice (built-in) — Buddy's own voice using the browser's native
 * speech engine. Zero cost, no third-party/competitor API, works today.
 * The self-hosted "DreamCo Voice Pro" engine (server-side, owned neural model)
 * is wired separately on the API and produces downloadable audio files.
 */
export function useDreamcoVoice() {
  const supported = typeof window !== "undefined" && "speechSynthesis" in window;
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [voiceURI, setVoiceURIState] = useState<string>(() =>
    (typeof localStorage !== "undefined" && localStorage.getItem("dreamco-voice-uri")) || "",
  );
  const [enabled, setEnabledState] = useState<boolean>(() =>
    typeof localStorage !== "undefined" && localStorage.getItem("dreamco-voice-enabled") === "1",
  );
  const [speaking, setSpeaking] = useState(false);

  useEffect(() => {
    if (!supported) return;
    const load = () => setVoices(window.speechSynthesis.getVoices());
    load();
    window.speechSynthesis.addEventListener("voiceschanged", load);
    return () => window.speechSynthesis.removeEventListener("voiceschanged", load);
  }, [supported]);

  const setVoiceURI = useCallback((uri: string) => {
    setVoiceURIState(uri);
    if (typeof localStorage !== "undefined") localStorage.setItem("dreamco-voice-uri", uri);
  }, []);

  const setEnabled = useCallback((on: boolean) => {
    setEnabledState(on);
    if (typeof localStorage !== "undefined") localStorage.setItem("dreamco-voice-enabled", on ? "1" : "0");
    if (!on && supported) window.speechSynthesis.cancel();
  }, [supported]);

  const speak = useCallback((text: string) => {
    if (!supported || !text.trim()) return;
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    const v = voices.find((x) => x.voiceURI === voiceURI);
    if (v) u.voice = v;
    u.rate = 1;
    u.pitch = 1;
    u.onstart = () => setSpeaking(true);
    u.onend = () => setSpeaking(false);
    u.onerror = () => setSpeaking(false);
    window.speechSynthesis.speak(u);
  }, [supported, voices, voiceURI]);

  const stop = useCallback(() => {
    if (supported) window.speechSynthesis.cancel();
    setSpeaking(false);
  }, [supported]);

  return { supported, voices, voiceURI, setVoiceURI, enabled, setEnabled, speaking, speak, stop };
}
