"""Local-first creative orchestration for Buddy.

The studio turns a brief into a testable production packet. Voice and likeness
work is always tied to explicit consent evidence and is never reported as
rendered unless a configured renderer returns a real asset reference.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Protocol

from dreamco_platform.innovation import InnovationEngine, InnovationRequest


class ProjectType(str, Enum):
    GAME = "game"
    SCHOOL_SIMULATION = "school_simulation"
    PARENT_LEARNING_VIDEO = "parent_learning_video"


class CreativeStudioError(ValueError):
    """Raised when a studio brief violates a production or consent rule."""


@dataclass
class ConsentEvidence:
    """Auditable permission for use of an adult user's voice and likeness."""

    owner_user_id: str
    subject_user_id: str
    owner_is_subject: bool
    adult_confirmed: bool
    voice_use_approved: bool
    likeness_use_approved: bool
    synthetic_media_label_approved: bool
    recorded_at: float = field(default_factory=time.time)
    expires_at: float | None = None
    revoked_at: float | None = None
    evidence_id: str = field(default_factory=lambda: f"consent-{uuid.uuid4().hex[:16]}")

    def is_active(self, now: float | None = None) -> bool:
        current = time.time() if now is None else now
        if self.revoked_at is not None:
            return False
        return self.expires_at is None or current <= self.expires_at

    def revoke(self, now: float | None = None) -> None:
        self.revoked_at = time.time() if now is None else now

    def audit_fingerprint(self) -> str:
        raw = ":".join(
            [
                self.evidence_id,
                self.owner_user_id,
                self.subject_user_id,
                str(self.recorded_at),
            ]
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def validate(self, *, needs_voice: bool, needs_likeness: bool) -> None:
        if not self.owner_user_id or not self.subject_user_id:
            raise CreativeStudioError("Consent must identify both the owner and subject.")
        if not self.owner_is_subject or self.owner_user_id != self.subject_user_id:
            raise CreativeStudioError(
                "Buddy Studio only accepts self-owned voice and likeness media in this workflow."
            )
        if not self.adult_confirmed:
            raise CreativeStudioError("Voice or likeness cloning is not available for minors.")
        if not self.is_active():
            raise CreativeStudioError("Consent has expired or been revoked and must be renewed.")
        if needs_voice and not self.voice_use_approved:
            raise CreativeStudioError("Explicit voice-use consent is required.")
        if needs_likeness and not self.likeness_use_approved:
            raise CreativeStudioError("Explicit likeness-use consent is required.")
        if (needs_voice or needs_likeness) and not self.synthetic_media_label_approved:
            raise CreativeStudioError("Synthetic-media labeling must remain enabled.")


@dataclass(frozen=True)
class CreativeBrief:
    title: str
    project_type: ProjectType
    objective: str
    subject: str
    audience: str
    target_platform: str = "web"
    innovation_mode: str = "balanced"
    use_voice_clone: bool = False
    use_image_avatar: bool = False
    voice_sample_ref: str = ""
    image_sample_ref: str = ""
    consent: ConsentEvidence | None = None

    def validate(self) -> None:
        if len(self.title.strip()) < 3:
            raise CreativeStudioError("A project title of at least three characters is required.")
        if len(self.objective.strip()) < 10:
            raise CreativeStudioError("Describe a clear learning or gameplay objective.")
        if not self.subject.strip() or not self.audience.strip():
            raise CreativeStudioError("Subject and audience are required.")
        try:
            InnovationRequest(
                objective=self.objective,
                audience=self.audience,
                mode=self.innovation_mode,
            ).validate()
        except ValueError as exc:
            raise CreativeStudioError(str(exc)) from exc
        if self.use_voice_clone and not self.voice_sample_ref:
            raise CreativeStudioError("A local or encrypted voice sample reference is required.")
        if self.use_image_avatar and not self.image_sample_ref:
            raise CreativeStudioError("A local or encrypted image reference is required.")
        if self.use_voice_clone or self.use_image_avatar:
            if self.consent is None:
                raise CreativeStudioError("Consent evidence is required for voice or likeness use.")
            self.consent.validate(
                needs_voice=self.use_voice_clone,
                needs_likeness=self.use_image_avatar,
            )


class MediaRenderer(Protocol):
    """Adapter contract for a local or user-selected media renderer."""

    name: str

    def render_voice(self, *, text: str, sample_ref: str, project_id: str) -> str:
        """Return a durable asset reference for rendered speech."""

    def render_avatar(self, *, prompt: str, sample_ref: str, project_id: str) -> str:
        """Return a durable asset reference for rendered likeness media."""


@dataclass
class StudioProject:
    project_id: str
    brief: CreativeBrief
    status: str
    native_routes: list[dict[str, Any]]
    production_plan: list[dict[str, Any]]
    media: dict[str, Any]
    sandbox: dict[str, Any]
    deliverables: list[str]
    innovation: dict[str, Any]
    audit: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        brief = asdict(self.brief)
        brief["project_type"] = self.brief.project_type.value
        brief["voice_sample_ref"] = "redacted" if self.brief.voice_sample_ref else ""
        brief["image_sample_ref"] = "redacted" if self.brief.image_sample_ref else ""
        consent = brief.get("consent")
        if consent:
            consent.pop("owner_user_id", None)
            consent.pop("subject_user_id", None)
            consent["audit_fingerprint"] = self.brief.consent.audit_fingerprint()
        return {
            "schema": "dreamco.buddy_creative_studio_project.v1",
            "project_id": self.project_id,
            "status": self.status,
            "brief": brief,
            "native_routes": self.native_routes,
            "production_plan": self.production_plan,
            "media": self.media,
            "sandbox": self.sandbox,
            "deliverables": self.deliverables,
            "innovation": self.innovation,
            "audit": self.audit,
        }


class BuddyCreativeStudio:
    """Build governed production packets and starter projects for Buddy."""

    COMMON_ROUTES = [
        {
            "bot": "buddy-trust-bot",
            "role": "consent, revocation, audit, and synthetic-media labeling",
        },
        {"bot": "adaptive-learning", "role": "learning objectives and difficulty tuning"},
    ]

    TYPE_ROUTES: dict[ProjectType, list[dict[str, str]]] = {
        ProjectType.GAME: [
            {"bot": "games-app-bot", "role": "game loop, progression, and packaging"},
            {"bot": "game-ai-player", "role": "play testing and difficulty checks"},
            {"bot": "game-analytics", "role": "completion, retention, and balance metrics"},
        ],
        ProjectType.SCHOOL_SIMULATION: [
            {"bot": "games-app-bot", "role": "interactive learning game runtime"},
            {"bot": "simulation-world-builder", "role": "deterministic scenario engine"},
            {"bot": "video-script", "role": "lesson narration and scene script"},
        ],
        ProjectType.PARENT_LEARNING_VIDEO: [
            {"bot": "video-script", "role": "age-aware lesson script and pacing"},
            {"bot": "professional-video-editing-bot", "role": "timeline and export plan"},
            {"bot": "photo-video-app-bot", "role": "captions, moderation, and asset checks"},
        ],
    }

    def create_project(self, brief: CreativeBrief) -> StudioProject:
        brief.validate()
        project_id = f"studio-{uuid.uuid4().hex[:12]}"
        routes = [*self.TYPE_ROUTES[brief.project_type], *self.COMMON_ROUTES]
        media = self._media_plan(brief)
        innovation = InnovationEngine().run(
            InnovationRequest(
                objective=brief.objective,
                audience=brief.audience,
                mode=brief.innovation_mode,
                tags=self._innovation_tags(brief),
                constraints=("local_first", "reversible", "owner_approval_before_publish"),
            )
        )
        return StudioProject(
            project_id=project_id,
            brief=brief,
            status="planned",
            native_routes=routes,
            production_plan=self._production_plan(brief),
            media=media,
            sandbox=self._sandbox_plan(brief),
            deliverables=self._deliverables(brief),
            innovation=innovation.to_dict(),
            audit={
                "local_first": True,
                "live_external_action_taken": False,
                "stores_raw_biometrics": False,
                "consent_evidence_id": brief.consent.evidence_id if brief.consent else None,
                "synthetic_media_label": "AI-assisted media using the creator's approved likeness or voice"
                if brief.use_voice_clone or brief.use_image_avatar
                else None,
            },
        )

    def render_media(
        self,
        project: StudioProject,
        *,
        narration: str,
        avatar_prompt: str,
        renderer: MediaRenderer | None,
    ) -> StudioProject:
        """Render approved media or preserve an honest configuration-required state."""
        if not project.brief.use_voice_clone and not project.brief.use_image_avatar:
            project.status = "ready_for_sandbox"
            return project
        self._validate_project_consent(project)
        if renderer is None:
            project.status = "media_engine_configuration_required"
            project.media["renderer"] = {
                "status": "not_configured",
                "message": "Connect a local engine or a user-selected model before rendering.",
            }
            return project

        rendered: dict[str, str] = {}
        if project.brief.use_voice_clone:
            rendered["voice_asset_ref"] = renderer.render_voice(
                text=narration,
                sample_ref=project.brief.voice_sample_ref,
                project_id=project.project_id,
            )
        if project.brief.use_image_avatar:
            rendered["avatar_asset_ref"] = renderer.render_avatar(
                prompt=avatar_prompt,
                sample_ref=project.brief.image_sample_ref,
                project_id=project.project_id,
            )
        if any(not value for value in rendered.values()):
            raise CreativeStudioError("The renderer did not return every requested media asset.")
        project.media["renderer"] = {
            "status": "rendered",
            "engine": renderer.name,
            "assets": rendered,
        }
        project.status = "ready_for_sandbox"
        return project

    def write_project_packet(self, project: StudioProject, output_dir: Path) -> list[Path]:
        """Write a portable manifest and a local interactive starter experience."""
        if project.brief.use_voice_clone or project.brief.use_image_avatar:
            self._validate_project_consent(project)
        output_dir.mkdir(parents=True, exist_ok=True)
        manifest = output_dir / "project.json"
        index = output_dir / "index.html"
        script = output_dir / "project.js"
        styles = output_dir / "styles.css"
        manifest.write_text(json.dumps(project.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        index.write_text(self._starter_html(project), encoding="utf-8")
        script.write_text(self._starter_js(project), encoding="utf-8")
        styles.write_text(self._starter_css(), encoding="utf-8")
        return [manifest, index, script, styles]

    @staticmethod
    def _innovation_tags(brief: CreativeBrief) -> tuple[str, ...]:
        tags = {"accessibility", "low_cost"}
        if brief.project_type == ProjectType.GAME:
            tags.add("game")
        elif brief.project_type == ProjectType.SCHOOL_SIMULATION:
            tags.update({"education", "game", "simulation"})
        else:
            tags.update({"education", "multimodal"})
        if brief.use_voice_clone or brief.use_image_avatar:
            tags.update({"multimodal", "privacy"})
        return tuple(sorted(tags))

    @staticmethod
    def _validate_project_consent(project: StudioProject) -> None:
        consent = project.brief.consent
        if consent is None:
            raise CreativeStudioError("Active consent evidence is required for media rendering.")
        consent.validate(
            needs_voice=project.brief.use_voice_clone,
            needs_likeness=project.brief.use_image_avatar,
        )

    @staticmethod
    def _media_plan(brief: CreativeBrief) -> dict[str, Any]:
        requested = brief.use_voice_clone or brief.use_image_avatar
        return {
            "mode": "local_first",
            "raw_media_storage": "browser_session_or_encrypted_owner_vault",
            "voice": {
                "requested": brief.use_voice_clone,
                "status": "consent_verified_pending_render" if brief.use_voice_clone else "not_requested",
                "sample_ref": "redacted" if brief.voice_sample_ref else None,
            },
            "likeness": {
                "requested": brief.use_image_avatar,
                "status": "consent_verified_pending_render" if brief.use_image_avatar else "not_requested",
                "sample_ref": "redacted" if brief.image_sample_ref else None,
            },
            "renderer": {
                "status": "not_configured" if requested else "not_needed",
                "native_adapter_contract": "MediaRenderer",
                "outside_models_optional": True,
            },
            "revocation": {
                "required": requested,
                "effect": "stop future renders and remove owner-controlled profiles/assets",
            },
        }

    @staticmethod
    def _production_plan(brief: CreativeBrief) -> list[dict[str, Any]]:
        shared = [
            {"phase": "brief", "outputs": ["objective", "audience", "success rubric"]},
            {"phase": "design", "outputs": ["storyboard", "interaction map", "asset manifest"]},
            {"phase": "build", "outputs": ["responsive web prototype", "local save state", "captions"]},
            {"phase": "evaluate", "outputs": ["learning check", "accessibility check", "sandbox evidence"]},
            {"phase": "package", "outputs": ["project manifest", "deployment checklist", "rights record"]},
        ]
        if brief.project_type == ProjectType.GAME:
            shared[2]["outputs"].extend(["game loop", "levels", "score and restart system"])
        elif brief.project_type == ProjectType.SCHOOL_SIMULATION:
            shared[2]["outputs"].extend(["scenario state", "student decisions", "teacher rubric"])
        else:
            shared[2]["outputs"].extend(["lesson timeline", "narration script", "family activity"])
        return shared

    @staticmethod
    def _sandbox_plan(brief: CreativeBrief) -> dict[str, Any]:
        checks = [
            "loads_without_network",
            "keyboard_and_touch_controls",
            "text_does_not_overflow",
            "captions_present",
            "learning_objective_measured",
            "restart_and_recovery_work",
            "no_live_external_action",
        ]
        if brief.use_voice_clone or brief.use_image_avatar:
            checks.extend(
                [
                    "consent_active_at_render_time",
                    "synthetic_media_label_visible",
                    "revocation_path_verified",
                    "raw_biometric_media_not_in_project_manifest",
                ]
            )
        return {
            "isolated": True,
            "network_default": "off",
            "seed": 42,
            "checks": checks,
            "release_gate": "all_checks_pass_and_owner_approves_publish",
        }

    @staticmethod
    def _deliverables(brief: CreativeBrief) -> list[str]:
        base = [
            "playable_or_watchable_web_prototype",
            "production_manifest",
            "storyboard_or_level_map",
            "automated_test_plan",
            "accessibility_and_caption_pass",
            "deployment_package",
        ]
        if brief.project_type == ProjectType.SCHOOL_SIMULATION:
            base.extend(["teacher_guide", "student_rubric", "learning_outcome_report"])
        elif brief.project_type == ProjectType.PARENT_LEARNING_VIDEO:
            base.extend(["parent_guide", "family_activity", "discussion_prompts"])
        else:
            base.extend(["game_design_document", "level_progression", "playtest_report"])
        return base

    @staticmethod
    def _starter_html(project: StudioProject) -> str:
        title = _html_escape(project.brief.title)
        objective = _html_escape(project.brief.objective)
        label = "<p class=\"media-label\">AI-assisted media uses the creator's approved voice or likeness.</p>" if project.brief.use_voice_clone or project.brief.use_image_avatar else ""
        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <main>
    <p class="eyebrow">Buddy Creative Studio</p>
    <h1>{title}</h1>
    <p>{objective}</p>
    {label}
    <section id="experience" aria-live="polite"></section>
    <div class="controls">
      <button id="primary-action" type="button">Start</button>
      <button id="reset-action" class="secondary" type="button">Reset</button>
    </div>
  </main>
  <script src="project.js"></script>
</body>
</html>
"""

    @staticmethod
    def _starter_js(project: StudioProject) -> str:
        payload = json.dumps(
            {
                "type": project.brief.project_type.value,
                "subject": project.brief.subject,
                "audience": project.brief.audience,
                "objective": project.brief.objective,
                "innovation": {
                    "lens": project.innovation["winner"]["lens"],
                    "design_score": project.innovation["winner"]["weighted_score"],
                    "evidence_level": project.innovation["winner"]["evidence_level"],
                },
            }
        )
        return f"""const project = {payload};
const experience = document.getElementById('experience');
const primary = document.getElementById('primary-action');
const reset = document.getElementById('reset-action');
let step = 0;

const scenes = [
  `Meet the challenge: ${{project.subject}}`,
  `Choose a path that helps ${{project.audience}} practice the objective.`,
  `Explain what changed and why. Buddy selected the ${{project.innovation.lens.replaceAll('_', ' ')}} design.`,
  `Complete the learning check and review your result.`
];

function render() {{
  experience.innerHTML = `<p class="step">Step ${{step + 1}} of ${{scenes.length}}</p><h2>${{scenes[step]}}</h2><p>${{project.objective}}</p>`;
  primary.textContent = step === scenes.length - 1 ? 'Complete' : 'Continue';
}}

primary.addEventListener('click', () => {{
  if (step < scenes.length - 1) step += 1;
  else {{
    experience.innerHTML = '<p class="step">Complete</p><h2>Prototype passed its local learning loop.</h2><p>Review the project manifest before any publish action.</p>';
    primary.disabled = true;
    return;
  }}
  render();
}});
reset.addEventListener('click', () => {{ step = 0; primary.disabled = false; render(); }});
render();
"""

    @staticmethod
    def _starter_css() -> str:
        return """* { box-sizing: border-box; }
body { margin: 0; min-height: 100vh; background: #0b1020; color: #f7f9ff; font-family: Inter, system-ui, sans-serif; }
main { width: min(760px, calc(100% - 32px)); margin: 0 auto; padding: 64px 0; }
.eyebrow, .step { color: #7dc4a7; font-size: .78rem; font-weight: 800; text-transform: uppercase; }
h1 { font-size: clamp(2rem, 8vw, 4rem); margin: 8px 0 12px; }
p { color: #b8c1d9; line-height: 1.65; }
#experience { min-height: 240px; margin: 32px 0 18px; padding: 28px; border: 1px solid #2b3758; border-radius: 8px; background: #121a2d; }
.media-label { padding: 10px 12px; border-left: 3px solid #e7b85c; background: #2b2518; color: #f6daa0; }
.controls { display: flex; gap: 10px; flex-wrap: wrap; }
button { min-height: 44px; padding: 0 18px; border: 0; border-radius: 6px; background: #7dc4a7; color: #07130e; font: inherit; font-weight: 800; cursor: pointer; }
button.secondary { background: transparent; border: 1px solid #526184; color: #f7f9ff; }
"""


def _html_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )
