# Media cloning

Local voice and image cloning. The consent check cannot be skipped.

## Install

```bash
pip install -r requirements-media.txt
```

Install this only on the machine that will run the clone. These packages are not installed in the repository checks.

## What is local

- `consent_gate.py` binds a consent file to the sha256 of the exact reference.
- The subject must be confirmed as an adult.
- Voice cloning uses Chatterbox (MIT) from `DREAMCO_CHATTERBOX_DIR` for personal, business, and social use. XTTS-v2 is not used, because that license is non-commercial.
- Image cloning uses the caller's local SDXL and IP-Adapter files for the same three uses. Sexual, violent, and defamatory prompts are still refused.
- Audio is not written unless AudioSeal can watermark it.
- Images get a low-bit marker. That marker is not a cryptographic seal.

## What this does not do

Importing the package does not download weights. If the local folders are missing, the clone stops. It does not call another service. No clone has been run in this repository. Chatterbox, SDXL, and IP-Adapter are still other people's models; this package only runs copies you already have on disk.
