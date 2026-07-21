"""
Content Creator — Music, Film, Art, and 3-D Modelling AI Assistance

Classes
-------
MusicCreator  — AI-assisted music composition, lyrics, and analysis.
FilmCreator   — Script generation, storyboarding, and cinematography advice.
ArtCreator    — Artwork generation, 3-D model specs, and color palette design.

All classes integrate with the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401

GENRES = ["pop", "jazz", "classical", "hip-hop", "electronic", "rock", "country", "ambient"]

STYLES = [
    "photorealistic",
    "impressionist",
    "abstract",
    "cubist",
    "watercolor",
    "digital",
    "3d_render",
]


# ---------------------------------------------------------------------------
# Music Creator
# ---------------------------------------------------------------------------

class MusicCreator:
    """AI-assisted music composition, lyric generation, and audio analysis."""

    def __init__(self) -> None:
        self.flow = GlobalAISourcesFlow(bot_name="MusicCreator")

    # ------------------------------------------------------------------
    def compose_music(self, genre: str, mood: str, duration_secs: int = 120) -> dict:
        """Compose an original piece of music.

        Parameters
        ----------
        genre : str
            Musical genre (see GENRES).
        mood : str
            Desired emotional mood, e.g. "upbeat", "melancholic".
        duration_secs : int
            Target duration in seconds.

        Returns
        -------
        dict
            Composition data including notes, tempo, and instruments.
        """
        if genre not in GENRES:
            genre = GENRES[0]

        genre_profiles: dict[str, dict] = {
            "pop": {"tempo": 120, "instruments": ["guitar", "bass", "drums", "piano"], "key": "C major"},
            "jazz": {"tempo": 100, "instruments": ["piano", "trumpet", "bass", "drums"], "key": "F major"},
            "classical": {"tempo": 80, "instruments": ["violin", "cello", "piano", "flute"], "key": "G major"},
            "hip-hop": {"tempo": 90, "instruments": ["808_bass", "hi_hat", "snare", "synth"], "key": "A minor"},
            "electronic": {"tempo": 140, "instruments": ["synth_lead", "synth_pad", "drum_machine", "bass"], "key": "D minor"},
            "rock": {"tempo": 130, "instruments": ["electric_guitar", "bass", "drums", "vocals"], "key": "E minor"},
            "country": {"tempo": 105, "instruments": ["acoustic_guitar", "fiddle", "banjo", "steel_guitar"], "key": "D major"},
            "ambient": {"tempo": 60, "instruments": ["synth_pad", "piano", "strings", "reverb_guitar"], "key": "C major"},
        }

        profile = genre_profiles.get(genre, genre_profiles["pop"])
        measures = max(4, duration_secs // 4)
        notes = [f"note_{i}" for i in range(min(measures, 32))]

        result = self.flow.run_pipeline(
            raw_data={
                "task": "compose_music",
                "genre": genre,
                "mood": mood,
                "duration_secs": duration_secs,
            },
            learning_method="supervised",
        )

        return {
            "genre": genre,
            "mood": mood,
            "duration_secs": duration_secs,
            "tempo": profile["tempo"],
            "key": profile["key"],
            "instruments": profile["instruments"],
            "notes": notes,
            "measures": measures,
            "structure": ["intro", "verse", "chorus", "verse", "chorus", "outro"],
            "framework_pipeline": result.get("bot_name"),
        }

    # ------------------------------------------------------------------
    def generate_lyrics(self, theme: str, style: str, verses: int = 2) -> dict:
        """Generate song lyrics for a given theme and style.

        Parameters
        ----------
        theme : str
            Central topic or story of the song.
        style : str
            Lyrical style, e.g. "rhyming", "free verse", "narrative".
        verses : int
            Number of verses to generate (1–6).

        Returns
        -------
        dict
            Lyrics structure with verses and chorus.
        """
        verses = max(1, min(6, verses))

        verse_lines = [
            [
                f"Line one about {theme} in {style} style",
                f"Line two exploring {theme} deeply",
                f"Line three painting pictures of {theme}",
                f"Line four bringing {theme} to life",
            ]
            for _ in range(verses)
        ]

        chorus_lines = [
            f"We rise with {theme} in our hearts",
            f"{theme.capitalize()} lights the way ahead",
            f"Together through {theme} we stand",
            f"Echoing {theme} forever",
        ]

        result = self.flow.run_pipeline(
            raw_data={"task": "generate_lyrics", "theme": theme, "style": style, "verses": verses},
            learning_method="supervised",
        )

        return {
            "theme": theme,
            "style": style,
            "verses": [{"verse_number": i + 1, "lines": verse_lines[i]} for i in range(verses)],
            "chorus": {"lines": chorus_lines},
            "bridge": {
                "lines": [
                    f"Bridge: {theme} transforms everything",
                    f"Nothing is the same after {theme}",
                ]
            },
            "framework_pipeline": result.get("bot_name"),
        }

    # ------------------------------------------------------------------
    def analyze_music(self, audio_data: dict) -> dict:
        """Analyze a piece of music and return structured metadata.

        Parameters
        ----------
        audio_data : dict
            Raw audio descriptor (title, waveform samples, etc.).

        Returns
        -------
        dict
            Analysis including key, BPM, and genre classification.
        """
        result = self.flow.run_pipeline(
            raw_data={"task": "analyze_music", "audio_data": audio_data},
            learning_method="unsupervised",
        )

        detected_key = random.choice(["C major", "A minor", "G major", "E minor", "F major"])
        detected_genre = random.choice(GENRES)
        bpm = random.randint(60, 180)

        return {
            "detected_key": detected_key,
            "bpm": bpm,
            "genre_classification": detected_genre,
            "genre_confidence": round(random.uniform(0.70, 0.98), 2),
            "mood": random.choice(["energetic", "calm", "melancholic", "upbeat", "dramatic"]),
            "time_signature": random.choice(["4/4", "3/4", "6/8"]),
            "dynamic_range_db": round(random.uniform(6.0, 20.0), 1),
            "framework_pipeline": result.get("bot_name"),
        }


# ---------------------------------------------------------------------------
# Film Creator
# ---------------------------------------------------------------------------

class FilmCreator:
    """AI-assisted screenplay generation, storyboarding, and cinematography advice."""

    def __init__(self) -> None:
        self.flow = GlobalAISourcesFlow(bot_name="FilmCreator")

    # ------------------------------------------------------------------
    def generate_script(self, genre: str, premise: str, num_scenes: int = 5) -> dict:
        """Generate a screenplay with scenes and dialogue.

        Parameters
        ----------
        genre : str
            Film genre, e.g. "thriller", "comedy", "drama".
        premise : str
            One-sentence premise or logline.
        num_scenes : int
            Number of scenes to generate (1–20).

        Returns
        -------
        dict
            Script dict with scene list and sample dialogue.
        """
        num_scenes = max(1, min(20, num_scenes))

        scene_types = ["INT.", "EXT."]
        locations = ["OFFICE", "CITY STREET", "FOREST", "CAFE", "ROOFTOP", "WAREHOUSE", "BEACH", "LABORATORY"]
        times = ["DAY", "NIGHT", "DAWN", "DUSK"]

        scenes = []
        for i in range(num_scenes):
            loc = random.choice(locations)
            tod = random.choice(times)
            int_ext = random.choice(scene_types)
            scenes.append({
                "scene_number": i + 1,
                "heading": f"{int_ext} {loc} - {tod}",
                "action": f"Scene {i + 1} action description based on premise: {premise}",
                "dialogue": [
                    {"character": "PROTAGONIST", "line": f"Line reflecting {genre} tone in scene {i + 1}."},
                    {"character": "ANTAGONIST", "line": f"Counter-response raising tension in scene {i + 1}."},
                ],
            })

        result = self.flow.run_pipeline(
            raw_data={"task": "generate_script", "genre": genre, "premise": premise, "num_scenes": num_scenes},
            learning_method="supervised",
        )

        return {
            "title": f"Untitled {genre.title()} Script",
            "genre": genre,
            "premise": premise,
            "num_scenes": num_scenes,
            "scenes": scenes,
            "three_act_structure": {
                "act_1": list(range(1, num_scenes // 3 + 1)),
                "act_2": list(range(num_scenes // 3 + 1, 2 * num_scenes // 3 + 1)),
                "act_3": list(range(2 * num_scenes // 3 + 1, num_scenes + 1)),
            },
            "framework_pipeline": result.get("bot_name"),
        }

    # ------------------------------------------------------------------
    def create_storyboard(self, script_data: dict) -> dict:
        """Create a visual storyboard from a generated script.

        Parameters
        ----------
        script_data : dict
            Output of :meth:`generate_script`.

        Returns
        -------
        dict
            Storyboard with per-scene visual descriptions and shot types.
        """
        scenes = script_data.get("scenes", [])
        shot_types = ["wide shot", "close-up", "medium shot", "over-the-shoulder", "POV", "aerial"]
        lighting_styles = ["natural", "high-contrast", "soft diffused", "backlighting", "neon", "golden hour"]

        panels = []
        for scene in scenes:
            panels.append({
                "scene_number": scene["scene_number"],
                "heading": scene.get("heading", ""),
                "shot_type": random.choice(shot_types),
                "lighting": random.choice(lighting_styles),
                "visual_description": f"Visual panel for {scene.get('heading', 'scene')} — {scene.get('action', '')}",
                "color_grade": random.choice(["warm", "cool", "desaturated", "vibrant", "teal-orange"]),
            })

        result = self.flow.run_pipeline(
            raw_data={"task": "create_storyboard", "script_title": script_data.get("title", "Unknown")},
            learning_method="supervised",
        )

        return {
            "title": script_data.get("title", "Untitled"),
            "total_panels": len(panels),
            "panels": panels,
            "framework_pipeline": result.get("bot_name"),
        }

    # ------------------------------------------------------------------
    def suggest_cinematography(self, scene_type: str) -> dict:
        """Suggest camera angles, lighting, and techniques for a scene type.

        Parameters
        ----------
        scene_type : str
            Type of scene, e.g. "action", "dialogue", "establishing".

        Returns
        -------
        dict
            Recommended camera angles, lighting setups, and techniques.
        """
        presets: dict[str, dict] = {
            "action": {
                "camera_angles": ["low angle", "Dutch tilt", "tracking shot", "shaky cam"],
                "lighting": ["high contrast", "practical lights", "dynamic shadows"],
                "techniques": ["fast cuts", "slow-motion inserts", "whip pans"],
            },
            "dialogue": {
                "camera_angles": ["over-the-shoulder", "two-shot", "close-up"],
                "lighting": ["three-point lighting", "soft key light", "motivated lighting"],
                "techniques": ["shot-reverse-shot", "dolly zoom", "static framing"],
            },
            "establishing": {
                "camera_angles": ["aerial", "wide shot", "crane shot"],
                "lighting": ["golden hour", "magic hour", "natural daylight"],
                "techniques": ["time-lapse", "slow push-in", "panoramic sweep"],
            },
        }

        preset = presets.get(scene_type.lower(), presets["dialogue"])

        result = self.flow.run_pipeline(
            raw_data={"task": "suggest_cinematography", "scene_type": scene_type},
            learning_method="supervised",
        )

        return {
            "scene_type": scene_type,
            "camera_angles": preset["camera_angles"],
            "lighting_setups": preset["lighting"],
            "techniques": preset["techniques"],
            "lens_recommendations": ["24mm wide", "50mm standard", "85mm portrait", "200mm telephoto"],
            "framework_pipeline": result.get("bot_name"),
        }


# ---------------------------------------------------------------------------
# Art Creator
# ---------------------------------------------------------------------------

class ArtCreator:
    """AI-assisted artwork generation, 3-D model specs, and color palette design."""

    def __init__(self) -> None:
        self.flow = GlobalAISourcesFlow(bot_name="ArtCreator")

    # ------------------------------------------------------------------
    def generate_artwork(self, style: str, subject: str, medium: str = "digital") -> dict:
        """Generate artwork description and rendering parameters.

        Parameters
        ----------
        style : str
            Artistic style (see STYLES).
        subject : str
            Subject matter of the artwork.
        medium : str
            Output medium, e.g. "digital", "oil", "watercolor".

        Returns
        -------
        dict
            Artwork description and rendering parameters.
        """
        if style not in STYLES:
            style = "digital"

        resolution_map = {
            "photorealistic": "4096x4096",
            "impressionist": "2048x2048",
            "abstract": "2048x2048",
            "cubist": "2048x2048",
            "watercolor": "3000x3000",
            "digital": "4096x4096",
            "3d_render": "4096x4096",
        }

        result = self.flow.run_pipeline(
            raw_data={"task": "generate_artwork", "style": style, "subject": subject, "medium": medium},
            learning_method="self_supervised",
        )

        return {
            "style": style,
            "subject": subject,
            "medium": medium,
            "resolution": resolution_map.get(style, "2048x2048"),
            "description": f"A {style} {medium} artwork depicting {subject} with rich detail and expressive technique.",
            "render_parameters": {
                "color_depth": "32-bit",
                "anti_aliasing": True,
                "texture_quality": "ultra" if style in ("photorealistic", "3d_render") else "high",
                "shading_model": "PBR" if style == "photorealistic" else "stylized",
            },
            "tags": [style, subject, medium, "AI-generated"],
            "framework_pipeline": result.get("bot_name"),
        }

    # ------------------------------------------------------------------
    def create_3d_model(self, object_type: str, style: str = "realistic", complexity: str = "medium") -> dict:
        """Generate 3-D model specifications.

        Parameters
        ----------
        object_type : str
            Category of object, e.g. "character", "vehicle", "environment".
        style : str
            Visual style, e.g. "realistic", "stylized", "low-poly".
        complexity : str
            Geometry complexity: "low", "medium", or "high".

        Returns
        -------
        dict
            3-D model specifications including polygon count and materials.
        """
        poly_counts = {"low": 2_000, "medium": 15_000, "high": 100_000}
        texture_sizes = {"low": "512x512", "medium": "2048x2048", "high": "4096x4096"}

        poly_count = poly_counts.get(complexity, poly_counts["medium"])

        result = self.flow.run_pipeline(
            raw_data={"task": "create_3d_model", "object_type": object_type, "style": style, "complexity": complexity},
            learning_method="supervised",
        )

        return {
            "object_type": object_type,
            "style": style,
            "complexity": complexity,
            "polygon_count": poly_count,
            "texture_resolution": texture_sizes.get(complexity, "2048x2048"),
            "materials": ["base_color", "roughness", "metallic", "normal_map"],
            "rigged": object_type in ("character", "creature", "humanoid"),
            "animations": ["idle", "walk", "run"] if object_type in ("character", "creature") else [],
            "file_formats": ["FBX", "OBJ", "GLTF"],
            "framework_pipeline": result.get("bot_name"),
        }

    # ------------------------------------------------------------------
    def suggest_color_palette(self, mood: str, style: str = "digital") -> dict:
        """Suggest a harmonious color palette for a given mood and style.

        Parameters
        ----------
        mood : str
            Emotional tone, e.g. "warm", "cool", "dramatic".
        style : str
            Target art style.

        Returns
        -------
        dict
            Color palette with hex codes and usage guidance.
        """
        mood_palettes: dict[str, list[dict]] = {
            "warm": [
                {"name": "Amber", "hex": "#FFBF00", "role": "primary"},
                {"name": "Coral", "hex": "#FF6B6B", "role": "accent"},
                {"name": "Terracotta", "hex": "#C46B39", "role": "secondary"},
                {"name": "Cream", "hex": "#FFF8E7", "role": "background"},
                {"name": "Charcoal", "hex": "#2C2C2C", "role": "text"},
            ],
            "cool": [
                {"name": "Cerulean", "hex": "#007BA7", "role": "primary"},
                {"name": "Lavender", "hex": "#B57EDC", "role": "accent"},
                {"name": "Slate", "hex": "#708090", "role": "secondary"},
                {"name": "Ice White", "hex": "#F0F4F8", "role": "background"},
                {"name": "Navy", "hex": "#001F3F", "role": "text"},
            ],
            "dramatic": [
                {"name": "Crimson", "hex": "#DC143C", "role": "primary"},
                {"name": "Midnight", "hex": "#191970", "role": "secondary"},
                {"name": "Gold", "hex": "#FFD700", "role": "accent"},
                {"name": "Obsidian", "hex": "#0A0A0A", "role": "background"},
                {"name": "Silver", "hex": "#C0C0C0", "role": "text"},
            ],
        }

        palette = mood_palettes.get(mood.lower(), mood_palettes["cool"])

        result = self.flow.run_pipeline(
            raw_data={"task": "suggest_color_palette", "mood": mood, "style": style},
            learning_method="unsupervised",
        )

        return {
            "mood": mood,
            "style": style,
            "palette": palette,
            "color_count": len(palette),
            "harmony_type": random.choice(["complementary", "analogous", "triadic", "split-complementary"]),
            "usage_guidance": f"Use the primary color for main elements, accent for highlights, and background for negative space.",
            "framework_pipeline": result.get("bot_name"),
        }
