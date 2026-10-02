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
- Voice is Buddy's own letter-to-sound network in `buddy/speech/`. It is not Chatterbox.
- Pictures are Buddy's own drawing in `buddy/picture/`. They are not Stable Diffusion and they do not copy a face.
- Personal, business, and social uses all stay on this machine.
- Audio is not written unless AudioSeal can watermark it.
- Images get a low-bit marker. That marker is not a cryptographic seal.

## What this does not do

Importing the package does not download weights. No outside speech or image model is called. The voice is a small network trained on Buddy's own letter table. It does not sound like a recorded person. The picture is an original drawing, not a likeness clone.
