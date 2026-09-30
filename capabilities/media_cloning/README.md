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
- `voice_clone.py` can run Coqui XTTS-v2 locally. That model is non-commercial, so `paid=True` is refused.
- `image_clone.py` can run SDXL with IP-Adapter locally.
- Audio is not written unless AudioSeal can watermark it.
- Images get a low-bit marker. That marker is not a cryptographic seal.

## What this does not do

Importing the package does not download weights. No clone has been run in this repository. A remote callable is optional and is not wired to another company.
