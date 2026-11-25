#!/usr/bin/env python3
"""Prepare authorized local video/audio for Buddy's multimodal study workflow.

This tool never downloads media. It requires a manifest entry bound to the
exact local file hash, extracts low-rate frames/audio, and emits provenance.
Optional ASR/music analysis is deliberately delegated to separately installed
local adapters; no model weights are downloaded by this script.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
MEDIA_ROOT=(ROOT/"data/authorized-media").resolve()

def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def find_rights(manifest:dict[str,Any], asset_id:str)->dict[str,Any]|None:
    for item in manifest.get("assets",[]):
        if isinstance(item,dict) and item.get("asset_id")==asset_id: return item
    return None

def verify_asset(path:Path, asset_id:str, manifest:dict[str,Any])->tuple[Path,dict[str,Any]]:
    resolved=path.resolve()
    try: resolved.relative_to(MEDIA_ROOT)
    except ValueError as exc: raise ValueError("media must be inside data/authorized-media") from exc
    if not resolved.is_file(): raise ValueError("media file does not exist")
    grant=find_rights(manifest,asset_id)
    if not grant: raise ValueError("asset is not registered in the rights manifest")
    for flag in ("study_permission","summary_derivative_permission","evaluation_permission"):
        if grant.get(flag) is not True: raise ValueError(f"missing {flag}")
    if not str(grant.get("evidence_ref","")).strip(): raise ValueError("missing rights evidence reference")
    actual=sha256(resolved)
    if grant.get("sha256")!=actual: raise ValueError("media hash does not match rights manifest")
    return resolved,grant

def run(command:list[str])->str:
    proc=subprocess.run(command,check=True,capture_output=True,text=True)
    return proc.stdout

def analyze_music(audio:Path)->dict[str,Any]:
    """Optional local librosa feature extraction; never uploads audio or trains."""
    try:
        import librosa
        import numpy as np
    except ImportError:
        return {"status":"adapter_not_installed","features":{}}
    try:
        signal,sr=librosa.load(str(audio),sr=22050,duration=300,mono=True)
        tempo,_=librosa.beat.beat_track(y=signal,sr=sr)
        chroma=librosa.feature.chroma_stft(y=signal,sr=sr)
        centroid=librosa.feature.spectral_centroid(y=signal,sr=sr)
        rms=librosa.feature.rms(y=signal)
        zcr=librosa.feature.zero_crossing_rate(y=signal)
        names=["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
        profile=np.mean(chroma,axis=1)
        return {"status":"analyzed","analysis_window_seconds":min(300,len(signal)/sr),
                "tempo_bpm_estimate":float(np.asarray(tempo).reshape(-1)[0]),
                "dominant_chroma_pitch_estimate":names[int(np.argmax(profile))],
                "spectral_centroid_mean_hz":float(np.mean(centroid)),
                "rms_mean":float(np.mean(rms)),"zero_crossing_rate_mean":float(np.mean(zcr)),
                "caveat":"Tempo and dominant chroma are approximate signal features, not a definitive musical key or transcription."}
    except Exception as exc:
        return {"status":"analysis_failed","error_type":type(exc).__name__,"features":{}}


def process(path:Path, asset_id:str, manifest:dict[str,Any], out_dir:Path, frame_interval:int=10)->dict[str,Any]:
    source,grant=verify_asset(path,asset_id,manifest)
    for binary in ("ffprobe","ffmpeg"):
        if shutil.which(binary) is None: raise RuntimeError(f"required executable not found: {binary}")
    out_dir.mkdir(parents=True,exist_ok=True)
    metadata=json.loads(run(["ffprobe","-v","error","-show_format","-show_streams","-of","json",str(source)]))
    duration=float((metadata.get("format") or {}).get("duration") or 0)
    if duration<=0: raise ValueError("media duration unavailable or invalid")
    audio=out_dir/"audio.wav"
    run(["ffmpeg","-nostdin","-v","error","-y","-i",str(source),"-vn","-ac","1","-ar","16000",str(audio)])
    frames=out_dir/"frames"; frames.mkdir(exist_ok=True)
    run(["ffmpeg","-nostdin","-v","error","-y","-i",str(source),"-vf",f"fps=1/{max(1,frame_interval)}","-frames:v","120",str(frames/"frame-%04d.jpg")])
    frame_files=sorted(x.name for x in frames.glob("*.jpg"))
    result={"schema":"dreamco.authorized_multimodal_asset.v1","asset_id":asset_id,
      "source":{"relative_path":str(source.relative_to(ROOT)),"sha256":sha256(source),"duration_seconds":duration,
                "format":(metadata.get("format") or {}).get("format_name"),
                "streams":[{"codec_type":s.get("codec_type"),"codec_name":s.get("codec_name"),
                            "width":s.get("width"),"height":s.get("height"),"sample_rate":s.get("sample_rate")}
                           for s in metadata.get("streams",[])]},
      "rights":{"evidence_ref":grant["evidence_ref"],"study_permission":True,
                "summary_derivative_permission":True,"evaluation_permission":True,
                "training_permission":grant.get("training_permission") is True},
      "derived_assets":{"audio_path":str(audio),"audio_sha256":sha256(audio),
                        "frame_directory":str(frames),"frame_count":len(frame_files),
                        "frame_files":frame_files},
      "music_analysis":analyze_music(audio),
      "next_steps":["run local ASR if speech is present","analyze sampled frames with a vision model",
                    "align transcript segments with frame timestamps","author detailed guide and knowledge checks",
                    "evaluate on a held-out task"],
      "truth_boundary":"Extraction is not transcription, a completed summary, training authorization, or mastery."}
    (out_dir/"asset-study-input.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    return result

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--asset-id",required=True); p.add_argument("--file",required=True)
    p.add_argument("--rights-manifest",default=str(ROOT/"config/buddy-authorized-media-rights.json"))
    p.add_argument("--out-dir",required=True); p.add_argument("--frame-interval",type=int,default=10)
    a=p.parse_args()
    manifest=json.loads(Path(a.rights_manifest).read_text(encoding="utf-8"))
    result=process(Path(a.file),a.asset_id,manifest,Path(a.out_dir),a.frame_interval)
    print(json.dumps({"asset_id":result["asset_id"],"duration_seconds":result["source"]["duration_seconds"],
                      "frame_count":result["derived_assets"]["frame_count"]},indent=2))
    return 0
if __name__=="__main__": raise SystemExit(main())
