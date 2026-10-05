"""pack.multimodal drill runner: tiny real CPU pipelines, pinned revisions.

Usage: python drill_runner.py  (writes evidence/run_<ts>.json and evidence/latest.json)
Downloads pinned weights to the local HF cache on first run (explicit, not CI).
"""
import json, os, re, sys, time, traceback, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = {m["repo_id"]: m for m in json.loads((HERE / "sources.json").read_text())["models"]}
SENTENCE = "the quick brown fox jumps over the lazy dog"


def rev(repo):
    return SRC[repo]["revision"]


def wer(ref, hyp):
    r = ref.split(); h = re.sub(r"[^a-z ]", "", hyp.lower()).split()
    d = [[0] * (len(h) + 1) for _ in range(len(r) + 1)]
    for i in range(len(r) + 1): d[i][0] = i
    for j in range(len(h) + 1): d[0][j] = j
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            d[i][j] = min(d[i-1][j] + 1, d[i][j-1] + 1, d[i-1][j-1] + (r[i-1] != h[j-1]))
    return d[-1][-1] / max(1, len(r))


def shapes():
    from PIL import Image, ImageDraw
    out = {}
    for name, color, draw in [
        ("a red circle", "red", lambda d: d.ellipse([40, 40, 184, 184], fill="red")),
        ("a blue square", "blue", lambda d: d.rectangle([40, 40, 184, 184], fill="blue")),
        ("a green triangle", "green", lambda d: d.polygon([(112, 30), (30, 194), (194, 194)], fill="green")),
    ]:
        im = Image.new("RGB", (224, 224), "white"); draw(ImageDraw.Draw(im)); out[name] = im
    return out


def main():
    from transformers import pipeline
    import numpy as np
    results, state = [], {}

    def drill(did, repo, fn):
        t0 = time.time(); rec = {"id": did, "model": repo, "revision": rev(repo), "license": SRC[repo]["license"]}
        try:
            rec.update(fn()); rec.setdefault("status", "PASS" if rec.get("pass") else "FAIL")
        except Exception as e:
            rec.update(status="ERROR", error=f"{type(e).__name__}: {e}", trace=traceback.format_exc()[-800:])
        rec["seconds"] = round(time.time() - t0, 2); results.append(rec)
        print(did, rec["status"], flush=True)

    imgs = shapes()

    def clip():
        p = pipeline("zero-shot-image-classification", model="openai/clip-vit-base-patch32", revision=rev("openai/clip-vit-base-patch32"))
        labels = list(imgs); preds = {}
        for truth, im in imgs.items():
            preds[truth] = p(im, candidate_labels=labels)[0]["label"]
        hits = sum(preds[k] == k for k in preds)
        return {"predictions": preds, "hits": hits, "pass": hits >= 2}

    def vit():
        p = pipeline("image-classification", model="google/vit-base-patch16-224", revision=rev("google/vit-base-patch16-224"))
        out = p(imgs["a red circle"])
        return {"top5": [{"label": o["label"], "score": round(float(o["score"]), 4)} for o in out],
                "pass": len(out) == 5 and sum(o["score"] for o in out) <= 1.0001}

    def tts():
        # Direct VitsModel call: the text-to-audio pipeline in transformers 5.x raises
        # "BatchEncoding.to() got an unexpected keyword argument 'dtype'" (observed 2026-09-28).
        import torch
        from transformers import VitsModel, AutoTokenizer
        r = rev("facebook/mms-tts-eng")
        tok = AutoTokenizer.from_pretrained("facebook/mms-tts-eng", revision=r)
        model = VitsModel.from_pretrained("facebook/mms-tts-eng", revision=r).eval()
        sr = int(model.config.sampling_rate)
        def say(text):
            torch.manual_seed(0)
            with torch.no_grad():
                return model(**tok(text, return_tensors="pt")).waveform.squeeze().numpy().astype("float32")
        wav = say(SENTENCE); state["yes"] = (say("yes"), sr)
        state["tts"] = (wav, sr)
        import soundfile as sf
        sf.write(HERE / "evidence" / "tts_sample.wav", wav, sr)
        dur = len(wav) / sr
        return {"method": "VitsModel direct (pipeline bug workaround)", "sampling_rate": sr, "duration_s": round(dur, 2), "wav": "evidence/tts_sample.wav", "pass": dur > 0.5}

    def resample(wav, sr, target=16000):
        if sr == target: return wav
        n = int(len(wav) * target / sr)
        return np.interp(np.linspace(0, len(wav), n, endpoint=False), np.arange(len(wav)), wav).astype("float32")

    def asr():
        if "tts" not in state: return {"status": "BLOCKED", "reason": "tts drill produced no audio"}
        wav, sr = state["tts"]
        p = pipeline("automatic-speech-recognition", model="openai/whisper-tiny", revision=rev("openai/whisper-tiny"))
        text = p({"raw": resample(wav, sr), "sampling_rate": 16000})["text"]
        w = wer(SENTENCE, text)
        return {"reference": SENTENCE, "hypothesis": text, "wer": round(w, 3), "pass": w <= 0.5}

    def audcls():
        if "yes" not in state: return {"status": "BLOCKED", "reason": "tts drill produced no audio"}
        wav, sr = state["yes"]
        p = pipeline("audio-classification", model="MIT/ast-finetuned-speech-commands-v2", revision=rev("MIT/ast-finetuned-speech-commands-v2"))
        out = p({"raw": resample(wav, sr), "sampling_rate": 16000})
        top = out[0]["label"]
        return {"top3": [{"label": o["label"], "score": round(float(o["score"]), 4)} for o in out[:3]],
                "top1_is_yes": top.lower() == "yes", "pass": len(out) > 0}

    drill("mm.clip_zero_shot_shapes", "openai/clip-vit-base-patch32", clip)
    drill("mm.vit_imagenet_smoke", "google/vit-base-patch16-224", vit)
    drill("mm.tts_generate", "facebook/mms-tts-eng", tts)
    drill("mm.asr_roundtrip", "openai/whisper-tiny", asr)
    drill("mm.audio_cls_smoke", "MIT/ast-finetuned-speech-commands-v2", audcls)

    import transformers, torch
    passed = sum(r["status"] == "PASS" for r in results)
    rep = {"schema": "dreamco.study_pack_evidence.v1", "pack": "pack.multimodal",
           "ran_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "env": {"python": sys.version.split()[0], "transformers": transformers.__version__, "torch": torch.__version__, "device": "cpu"},
           "pass_rate": round(passed / len(results), 3), "passed": passed, "total": len(results), "drills": results}
    ts = rep["ran_at"][:19].replace(":", "").replace("-", "")
    for name in (f"run_{ts}.json", "latest.json"):
        (HERE / "evidence" / name).write_text(json.dumps(rep, indent=2))
    print(json.dumps({k: rep[k] for k in ("pass_rate", "passed", "total")}))


if __name__ == "__main__":
    main()
