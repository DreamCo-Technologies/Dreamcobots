import numpy as np
import pytest
import soundfile as sf
from PIL import Image

from buddy.media import BuddyMedia, ConsentError
from buddy.media import provenance as prov


class FakeVoice:
    name, model = "fake-voice", "fake"
    def load(self): pass
    def unload(self): pass
    def synthesize(self, text, reference_path, **kw):
        t = np.linspace(0, 6, 6 * 24000, endpoint=False)
        return (0.2 * np.sin(2 * np.pi * 220 * t + 0.3 * np.sin(2 * np.pi * 3 * t))).astype(np.float32), 24000


class FakeImage:
    name, model, mode = "fake-image", "fake", "style"
    def load(self): pass
    def unload(self): pass
    def generate(self, prompt, reference, seed=None, **kw):
        rng = np.random.RandomState(seed or 0)
        return Image.fromarray((rng.rand(128, 128, 3) * 200 + 20).astype(np.uint8))


@pytest.fixture
def media(tmp_path):
    return BuddyMedia(root=tmp_path / "store", voice_backend=FakeVoice(), image_backend=FakeImage(), min_free_gb=0)


@pytest.fixture
def ref_voice(tmp_path):
    t = np.linspace(0, 6, 6 * 24000, endpoint=False)
    p = tmp_path / "ref.wav"
    sf.write(str(p), (0.3 * np.sin(2 * np.pi * 180 * t)).astype(np.float32), 24000)
    return p


@pytest.fixture
def ref_image(tmp_path):
    p = tmp_path / "ref.png"
    Image.fromarray((np.random.RandomState(1).rand(64, 64, 3) * 255).astype(np.uint8)).save(p)
    return p


ATTEST = "The subject consented in writing to this use of their likeness."


def test_voice_blocked_without_consent(media, ref_voice):
    with pytest.raises(ConsentError):
        media.clone_voice("hello there", ref_voice)


def test_voice_flow_watermark_and_manifest(media, ref_voice):
    media.register_consent(ref_voice, "Me", "voice", "me", ATTEST)
    res = media.clone_voice("Hello there. This is a test.", ref_voice)
    v = media.verify(res.path)
    assert v["watermark_found"] and v["manifest_present"]


def test_revoked_consent_blocks(media, ref_voice):
    rec = media.register_consent(ref_voice, "Me", "voice", "me", ATTEST)
    media.consents.revoke(rec.consent_id)
    with pytest.raises(ConsentError):
        media.clone_voice("hello", ref_voice)


def test_changed_reference_blocks(media, ref_voice):
    media.register_consent(ref_voice, "Me", "voice", "me", ATTEST)
    with open(ref_voice, "ab") as f:
        f.write(b"\x00\x00")
    with pytest.raises(ConsentError):
        media.clone_voice("hello", ref_voice)


def test_weak_attestation_rejected(media, ref_voice):
    with pytest.raises(ConsentError):
        media.register_consent(ref_voice, "Me", "voice", "me", "ok")


def test_child_reference_rejected(media, ref_voice):
    with pytest.raises(ConsentError):
        media.register_consent(ref_voice, "Me", "voice", "me", "The subject consented, and this is a child's voice.")


def test_purpose_scope_enforced(media, ref_voice):
    media.register_consent(ref_voice, "Me", "voice", "me", ATTEST, scope=("personal",))
    with pytest.raises(ConsentError):
        media.clone_voice("hello", ref_voice, purpose="commercial")


def test_image_flow(media, ref_image):
    with pytest.raises(ConsentError):
        media.clone_image("a portrait", ref_image)
    media.register_consent(ref_image, "Me", "image", "me", ATTEST)
    res = media.clone_image("a portrait", ref_image, seed=3)
    v = media.verify(res.path)
    assert v["watermark_found"] and v["manifest_present"]


def test_no_false_positive_on_unmarked():
    x = np.random.RandomState(0).randn(100000).astype(np.float32) * 0.1
    assert not prov.detect_audio_watermark(x, "k")[0]
    img = (np.random.RandomState(0).rand(128, 128, 3) * 255).astype(np.uint8)
    assert not prov.detect_image_watermark(img, "k")[0]
    assert not prov.detect_audio_watermark(prov.watermark_audio(x, "other"), "k")[0]


def test_connectors_do_not_download_weights():
    from buddy.media.connectors import CONNECTORS, ConnectorMissing, KokoroBackend, first_voice_clone, probe

    rows = probe()
    assert len(rows) == len(CONNECTORS)
    assert all(row["weights_downloaded"] is False and row["sandbox_verified"] is False for row in rows)
    kokoro = next(row for row in rows if row["id"] == "kokoro")
    assert kokoro["clones"] is False
    with pytest.raises(ConnectorMissing):
        KokoroBackend().synthesize("hello", "ref.wav")
    with pytest.raises(ConnectorMissing):
        first_voice_clone()
