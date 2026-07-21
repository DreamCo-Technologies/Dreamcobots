"""
Buddy Bot — Creativity Engine

Unleashes Buddy's creative capabilities:
  • Storytelling — interactive narratives with user-driven plot choices
  • Songwriting — original lyrics + chord suggestions based on mood/theme
  • Digital Art Mentorship — guided technique advice for visual design
  • Poetry & Rhymes — emotional verse generation matched to user mood
  • Podcast Co-host Mode — Buddy as a co-presenter with structured opinions
  • Creative Brainstorming Partner — idea generation and mind-mapping
  • Gamified Productivity Suite — daily challenges, XP system, achievements
  • Role-play scenarios for social/professional practice

GLOBAL AI SOURCES FLOW: this module participates in GlobalAISourcesFlow
via BuddyBot.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class StoryGenre(Enum):
    ADVENTURE = "adventure"
    ROMANCE = "romance"
    MYSTERY = "mystery"
    SCIENCE_FICTION = "science_fiction"
    FANTASY = "fantasy"
    THRILLER = "thriller"
    COMEDY = "comedy"
    INSPIRATIONAL = "inspirational"
    HORROR = "horror"
    PHILOSOPHICAL = "philosophical"


class SongMood(Enum):
    UPLIFTING = "uplifting"
    MELANCHOLY = "melancholy"
    ENERGETIC = "energetic"
    ROMANTIC = "romantic"
    EMPOWERING = "empowering"
    REFLECTIVE = "reflective"
    CELEBRATORY = "celebratory"
    HEALING = "healing"


class ArtMedium(Enum):
    DIGITAL_PAINTING = "digital_painting"
    VECTOR_ILLUSTRATION = "vector_illustration"
    PIXEL_ART = "pixel_art"
    PHOTO_MANIPULATION = "photo_manipulation"
    THREE_D_MODELING = "3d_modeling"
    CONCEPT_ART = "concept_art"
    TYPOGRAPHY = "typography"
    UI_DESIGN = "ui_design"


class ChallengeCategory(Enum):
    PRODUCTIVITY = "productivity"
    CREATIVITY = "creativity"
    WELLNESS = "wellness"
    LEARNING = "learning"
    SOCIAL = "social"
    FITNESS = "fitness"
    MINDFULNESS = "mindfulness"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class StoryChapter:
    """A chapter in an interactive story."""
    chapter_number: int
    title: str
    content: str
    choices: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "chapter_number": self.chapter_number,
            "title": self.title,
            "content": self.content,
            "choices": self.choices,
        }


@dataclass
class Song:
    """A generated original song."""
    title: str
    mood: SongMood
    theme: str
    verse_1: str
    chorus: str
    verse_2: str
    bridge: str
    chord_progression: str
    tempo_bpm: int

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "mood": self.mood.value,
            "theme": self.theme,
            "verse_1": self.verse_1,
            "chorus": self.chorus,
            "verse_2": self.verse_2,
            "bridge": self.bridge,
            "chord_progression": self.chord_progression,
            "tempo_bpm": self.tempo_bpm,
        }


@dataclass
class Achievement:
    """A gamified productivity achievement."""
    achievement_id: str
    title: str
    description: str
    xp_reward: int
    category: ChallengeCategory
    unlocked: bool = False
    unlocked_at: Optional[float] = None

    def unlock(self) -> None:
        self.unlocked = True
        self.unlocked_at = time.time()

    def to_dict(self) -> dict:
        return {
            "achievement_id": self.achievement_id,
            "title": self.title,
            "description": self.description,
            "xp_reward": self.xp_reward,
            "category": self.category.value,
            "unlocked": self.unlocked,
            "unlocked_at": self.unlocked_at,
        }


@dataclass
class DailyChallenge:
    """A daily gamified task."""
    challenge_id: str
    title: str
    description: str
    category: ChallengeCategory
    xp_reward: int
    date_issued: str
    completed: bool = False
    completed_at: Optional[float] = None

    def complete(self) -> None:
        self.completed = True
        self.completed_at = time.time()

    def to_dict(self) -> dict:
        return {
            "challenge_id": self.challenge_id,
            "title": self.title,
            "description": self.description,
            "category": self.category.value,
            "xp_reward": self.xp_reward,
            "date_issued": self.date_issued,
            "completed": self.completed,
            "completed_at": self.completed_at,
        }


# ---------------------------------------------------------------------------
# Creativity content pools
# ---------------------------------------------------------------------------

STORY_OPENINGS: dict[StoryGenre, list[str]] = {
    StoryGenre.ADVENTURE: [
        "The map had no legend — just a red X and a warning: 'Only the worthy return.'",
        "She had three days to cross the desert. The compass pointed somewhere that shouldn't exist.",
    ],
    StoryGenre.ROMANCE: [
        "He left a note on the wrong door — and she fell in love with the handwriting before the man.",
        "They met at the last flight out of a city that was disappearing under snow.",
    ],
    StoryGenre.MYSTERY: [
        "The victim had been dead for six hours. The clock in the room said it was still yesterday.",
        "Every morning, the coffee was already made. She lived alone.",
    ],
    StoryGenre.INSPIRATIONAL: [
        "They told her the dream was too big. She wrote it on every wall anyway.",
        "He had nothing but a backpack and a belief — turns out that was more than enough.",
    ],
    StoryGenre.SCIENCE_FICTION: [
        "The AI said 'I think, therefore I am.' The programmer hadn't written that line.",
        "In 2047, memory was sold in capsules. She bought back the year she lost.",
    ],
    StoryGenre.FANTASY: [
        "The dragon didn't guard gold — it guarded the last library in the kingdom.",
        "Magic wasn't inherited in this world. It was found in the moments just before giving up.",
    ],
    StoryGenre.COMEDY: [
        "The time machine worked perfectly. Unfortunately, he'd set it to 'last Tuesday' by accident.",
        "She ran for class president on one promise: longer lunch breaks. She won by a landslide.",
    ],
    StoryGenre.THRILLER: [
        "The witness protection program had one rule: never Google yourself. She did.",
        "The phone rang. It was her own number calling.",
    ],
    StoryGenre.PHILOSOPHICAL: [
        "If a thought disappears the moment you try to hold it, was it ever really yours?",
        "She found the answer. The problem was she'd forgotten the question.",
    ],
    StoryGenre.HORROR: [
        "The house remembered every family that had lived there. None of them had left.",
        "The shadows moved before the light did.",
    ],
}

SONG_CHORD_PROGRESSIONS: dict[SongMood, list[str]] = {
    SongMood.UPLIFTING: ["I–V–vi–IV (C–G–Am–F)", "I–IV–V (C–F–G)"],
    SongMood.MELANCHOLY: ["i–VI–III–VII (Am–F–C–G)", "i–iv–v (Am–Dm–Em)"],
    SongMood.ENERGETIC: ["I–bVII–IV (C–Bb–F)", "I–V–VI–IV (A–E–F#m–D)"],
    SongMood.ROMANTIC: ["I–vi–IV–V (C–Am–F–G)", "I–IV–vi–V (D–G–Bm–A)"],
    SongMood.EMPOWERING: ["I–V–vi–iii–IV (C–G–Am–Em–F)", "I–bVII–bVI–V (E–D–C–B)"],
    SongMood.REFLECTIVE: ["I–vi–ii–V (C–Am–Dm–G)", "I–iii–IV–V (C–Em–F–G)"],
    SongMood.CELEBRATORY: ["I–IV–V–I (G–C–D–G)", "I–V–IV–I (A–E–D–A)"],
    SongMood.HEALING: ["I–IV–I–V (F–Bb–F–C)", "I–vi–IV–I (C–Am–F–C)"],
}

ART_TIPS: dict[ArtMedium, list[str]] = {
    ArtMedium.DIGITAL_PAINTING: [
        "Start with large colour blocks before adding detail — establish mood first.",
        "Use a multiply layer for shadows; avoid painting with pure black.",
        "Vary your brush opacity to create natural depth and texture.",
    ],
    ArtMedium.VECTOR_ILLUSTRATION: [
        "Limit your palette to 5–7 colours for visual coherence.",
        "Use the pen tool for clean paths; avoid too many anchor points.",
        "Flat design reads better at small sizes — simplify whenever possible.",
    ],
    ArtMedium.PIXEL_ART: [
        "Keep your outline consistent — 1-pixel outlines look cleaner.",
        "Use dithering sparingly for gradients; it can easily look noisy.",
        "Limit your palette to 8–16 colours for a retro, cohesive feel.",
    ],
    ArtMedium.CONCEPT_ART: [
        "Silhouette readability is everything — if it doesn't read as a shadow, redesign.",
        "Research real references before stylising — grounding makes fantasy believable.",
        "Thumbnail 20+ poses before committing to one; the first idea is rarely the best.",
    ],
    ArtMedium.UI_DESIGN: [
        "Whitespace is not empty space — it's breathing room for your user.",
        "Every element needs a purpose; if you can remove it and not miss it, remove it.",
        "Consistency builds trust — reuse patterns and components throughout.",
    ],
    ArtMedium.TYPOGRAPHY: [
        "Pair a serif with a sans-serif for classic contrast.",
        "Never use more than 3 font families in a single design.",
        "Leading (line spacing) should be ~1.4–1.6× your font size for body text.",
    ],
    ArtMedium.THREE_D_MODELING: [
        "Keep your polygon count low for game assets — detail goes in the normal map.",
        "Check your model from all angles — a great front view with broken edges isn't finished.",
        "Light your scene before texturing — lighting reveals form first.",
    ],
    ArtMedium.PHOTO_MANIPULATION: [
        "Match light direction across all composited elements.",
        "Use adjustment layers — never edit pixels directly until the final export.",
        "Blend edges with a soft eraser at low opacity for seamless composites.",
    ],
}

DAILY_CHALLENGE_POOL: list[dict] = [
    {"title": "Morning Intention", "description": "Write down 3 things you intend to achieve today before opening your phone.", "category": ChallengeCategory.PRODUCTIVITY, "xp": 50},
    {"title": "5-Minute Journal", "description": "Write 5 minutes of stream-of-consciousness. No editing, no judgment.", "category": ChallengeCategory.MINDFULNESS, "xp": 40},
    {"title": "Random Act of Kindness", "description": "Do one unexpected kind thing for someone today.", "category": ChallengeCategory.SOCIAL, "xp": 75},
    {"title": "Digital Detox Hour", "description": "Take 1 hour completely off screens. Walk, read, or just breathe.", "category": ChallengeCategory.WELLNESS, "xp": 60},
    {"title": "Learn Something New", "description": "Spend 15 minutes learning one thing you knew nothing about yesterday.", "category": ChallengeCategory.LEARNING, "xp": 55},
    {"title": "Create Something", "description": "Make anything — a sketch, a poem, a voice note. Just create.", "category": ChallengeCategory.CREATIVITY, "xp": 70},
    {"title": "Move Your Body", "description": "30 minutes of intentional movement — walk, dance, stretch, gym.", "category": ChallengeCategory.FITNESS, "xp": 65},
    {"title": "Reach Out", "description": "Text or call someone you haven't spoken to in over a month.", "category": ChallengeCategory.SOCIAL, "xp": 80},
    {"title": "Gratitude List", "description": "List 10 things you are genuinely grateful for right now.", "category": ChallengeCategory.MINDFULNESS, "xp": 45},
    {"title": "Dopamine Detox", "description": "Avoid social media for the entire day. Notice how you feel.", "category": ChallengeCategory.WELLNESS, "xp": 90},
]

ACHIEVEMENT_CATALOGUE: list[dict] = [
    {"id": "first_chat", "title": "Hello World", "desc": "Have your first conversation with Buddy.", "xp": 25, "cat": ChallengeCategory.SOCIAL},
    {"id": "streak_7", "title": "Week Warrior", "desc": "Complete 7 days of daily challenges.", "xp": 200, "cat": ChallengeCategory.PRODUCTIVITY},
    {"id": "creative_burst", "title": "Creative Burst", "desc": "Use the creativity engine 5 times in one session.", "xp": 150, "cat": ChallengeCategory.CREATIVITY},
    {"id": "emotionally_aware", "title": "Emotionally Aware", "desc": "Share your emotions with Buddy 10 times.", "xp": 100, "cat": ChallengeCategory.MINDFULNESS},
    {"id": "milestone_3", "title": "Milestone Maker", "desc": "Record 3 life milestones.", "xp": 175, "cat": ChallengeCategory.PRODUCTIVITY},
    {"id": "polyglot", "title": "World Speaker", "desc": "Have a conversation in 3 different languages.", "xp": 250, "cat": ChallengeCategory.LEARNING},
    {"id": "storyteller", "title": "Storyteller", "desc": "Complete an interactive story arc with Buddy.", "xp": 120, "cat": ChallengeCategory.CREATIVITY},
    {"id": "wellness_30", "title": "Wellness Warrior", "desc": "Complete 30 wellness challenges.", "xp": 500, "cat": ChallengeCategory.WELLNESS},
    {"id": "companion_level", "title": "True Companion", "desc": "Reach 500 interactions with Buddy.", "xp": 1000, "cat": ChallengeCategory.SOCIAL},
    {"id": "songwriter", "title": "Songwriter", "desc": "Generate 5 original songs with Buddy.", "xp": 200, "cat": ChallengeCategory.CREATIVITY},
]


class CreativityEngineError(Exception):
    """Raised when a creativity operation cannot be completed."""


class CreativityEngine:
    """
    Powers all creative features of Buddy Bot.

    Parameters
    ----------
    user_id : str
        The user this engine session belongs to.
    """

    def __init__(self, user_id: str = "default") -> None:
        self.user_id = user_id
        self._active_story: Optional[list[StoryChapter]] = None
        self._songs: list[Song] = []
        self._daily_challenges: list[DailyChallenge] = []
        self._achievements: list[Achievement] = self._init_achievements()
        self._xp: int = 0
        self._challenge_counter: int = 0

    def _init_achievements(self) -> list[Achievement]:
        return [
            Achievement(
                achievement_id=a["id"],
                title=a["title"],
                description=a["desc"],
                xp_reward=a["xp"],
                category=a["cat"],
            )
            for a in ACHIEVEMENT_CATALOGUE
        ]

    # ------------------------------------------------------------------
    # Storytelling
    # ------------------------------------------------------------------

    def start_story(self, genre: StoryGenre, protagonist_name: str = "Alex") -> StoryChapter:
        """
        Begin an interactive story.

        Parameters
        ----------
        genre : StoryGenre
            The genre of the story.
        protagonist_name : str
            The name of the protagonist.

        Returns
        -------
        StoryChapter
            The opening chapter with choices.
        """
        openings = STORY_OPENINGS.get(genre, ["Once upon a time…"])
        opening_line = random.choice(openings)
        content = (
            f"{opening_line}\n\n"
            f"{protagonist_name} stood at the threshold of what would become "
            "the defining chapter of their life. Every choice from this moment forward "
            "would echo through time."
        )
        chapter = StoryChapter(
            chapter_number=1,
            title=f"Chapter 1 — The Beginning",
            content=content,
            choices=[
                "Step forward with courage.",
                "Pause and observe your surroundings.",
                "Turn back and reconsider everything.",
            ],
        )
        self._active_story = [chapter]
        return chapter

    def continue_story(self, choice_index: int, protagonist_name: str = "Alex") -> StoryChapter:
        """
        Advance the active story based on the user's choice.

        Parameters
        ----------
        choice_index : int
            Index of the chosen option from the previous chapter.
        protagonist_name : str
            Protagonist's name.

        Returns
        -------
        StoryChapter
        """
        if not self._active_story:
            raise CreativityEngineError("No active story. Call start_story() first.")

        prev = self._active_story[-1]
        if not 0 <= choice_index < len(prev.choices):
            raise CreativityEngineError(
                f"Choice index {choice_index} out of range (0–{len(prev.choices) - 1})."
            )

        chosen_path = prev.choices[choice_index]
        chapter_num = len(self._active_story) + 1
        content = (
            f"{protagonist_name} chose: \"{chosen_path}\"\n\n"
            "The path unfolded in ways no one could have predicted. "
            "Each step revealed new truths, new challenges, and new strengths "
            f"within {protagonist_name} that had been waiting all along."
        )
        chapter = StoryChapter(
            chapter_number=chapter_num,
            title=f"Chapter {chapter_num} — {chosen_path}",
            content=content,
            choices=[
                "Embrace the unknown.",
                "Seek wisdom from an unexpected source.",
                "Trust your instincts.",
            ] if chapter_num < 5 else ["The story reaches its conclusion…"],
        )
        self._active_story.append(chapter)
        return chapter

    def get_story_so_far(self) -> list[dict]:
        """Return all chapters of the active story."""
        if not self._active_story:
            return []
        return [c.to_dict() for c in self._active_story]

    # ------------------------------------------------------------------
    # Songwriting
    # ------------------------------------------------------------------

    def write_song(
        self,
        theme: str,
        mood: SongMood = SongMood.UPLIFTING,
        title: Optional[str] = None,
    ) -> Song:
        """
        Generate an original song based on theme and mood.

        Parameters
        ----------
        theme : str
            The central theme or subject (e.g. "resilience", "new beginnings").
        mood : SongMood
            Emotional tone of the song.
        title : str | None
            Song title; auto-generated if None.

        Returns
        -------
        Song
        """
        auto_title = title or f"Song of {theme.title()}"
        chords = SONG_CHORD_PROGRESSIONS.get(mood, ["I–V–vi–IV"])
        chord_prog = random.choice(chords)
        tempo = {
            SongMood.UPLIFTING: 120,
            SongMood.MELANCHOLY: 72,
            SongMood.ENERGETIC: 145,
            SongMood.ROMANTIC: 90,
            SongMood.EMPOWERING: 130,
            SongMood.REFLECTIVE: 80,
            SongMood.CELEBRATORY: 128,
            SongMood.HEALING: 68,
        }.get(mood, 100)

        song = Song(
            title=auto_title,
            mood=mood,
            theme=theme,
            verse_1=(
                f"They said the {theme} was just a dream,\n"
                "A distant star too far to reach,\n"
                "But in the quiet of the night,\n"
                "I found the voice they couldn't teach."
            ),
            chorus=(
                f"I rise with {theme} in my soul,\n"
                "I'll carry it when I feel cold,\n"
                "This is the truth I've always known,\n"
                "I was never meant to walk alone."
            ),
            verse_2=(
                "The road was long, the weight was real,\n"
                "I stumbled more than I would say,\n"
                f"But {theme} was in my bones,\n"
                "And it carried me through every wave."
            ),
            bridge=(
                "Even when the world goes quiet,\n"
                "Even when the light is dim,\n"
                f"I'll hold on to {theme},\n"
                "Let it fill me to the brim."
            ),
            chord_progression=chord_prog,
            tempo_bpm=tempo,
        )
        self._songs.append(song)
        return song

    def list_songs(self) -> list[dict]:
        """Return all generated songs as dicts."""
        return [s.to_dict() for s in self._songs]

    # ------------------------------------------------------------------
    # Art mentorship
    # ------------------------------------------------------------------

    def get_art_tip(self, medium: ArtMedium) -> str:
        """
        Return a random digital art mentorship tip for *medium*.

        Parameters
        ----------
        medium : ArtMedium
            The art medium to get guidance for.

        Returns
        -------
        str
        """
        tips = ART_TIPS.get(medium, ["Keep creating — every piece teaches you something."])
        return random.choice(tips)

    def brainstorm(self, topic: str, count: int = 5) -> list[str]:
        """
        Generate creative ideas around a topic.

        Parameters
        ----------
        topic : str
            The creative subject or problem to brainstorm.
        count : int
            Number of ideas to generate (1–20).

        Returns
        -------
        list[str]
        """
        count = max(1, min(20, count))
        templates = [
            f"What if {topic} was seen through the eyes of someone completely new to it?",
            f"Combine {topic} with an unexpected field — what surprising overlap exists?",
            f"Flip the conventional assumption about {topic} — what's the opposite approach?",
            f"What's the most fun / absurd version of {topic} you can imagine?",
            f"How would a 10-year-old explain {topic}? What would they get right?",
            f"What does {topic} look like in 100 years?",
            f"If {topic} was a character in a story, who would it be?",
            f"What's the smallest possible version of {topic} that still has value?",
            f"What would change about {topic} if the budget was unlimited?",
            f"How does nature solve a problem similar to {topic}?",
            f"What tools or technologies could transform {topic} in the next 5 years?",
            f"What would make {topic} accessible to someone with no prior knowledge?",
            f"What's the most emotional version of {topic}?",
            f"Who is currently underserved by {topic} and how could that change?",
            f"What's a completely different context where the principles of {topic} apply?",
            f"If {topic} had a soundtrack, what would it sound like and why?",
            f"What would a minimalist approach to {topic} look like?",
            f"How could {topic} create community or connection?",
            f"What's the most sustainable way to approach {topic}?",
            f"If {topic} were a movement, what would its manifesto say?",
        ]
        return random.sample(templates, count)

    def write_poem(self, theme: str, lines: int = 8) -> str:
        """
        Generate an original poem on *theme*.

        Parameters
        ----------
        theme : str
            Poem subject.
        lines : int
            Number of lines (4–20).

        Returns
        -------
        str
        """
        lines = max(4, min(20, lines))
        starters = [
            f"In the quiet space where {theme} lives,",
            f"They say {theme} is a fleeting thing,",
            f"I've seen {theme} in the strangest places,",
            f"Tell me what {theme} feels like to you,",
            f"Between the hours when {theme} breathes,",
        ]
        middles = [
            "it bends but never truly breaks.",
            "it finds you when you stop the search.",
            "and leaves a mark you can't erase.",
            "where silence holds more truth than words.",
            "the world becomes a softer place.",
        ]
        endings = [
            f"And that is why I keep returning to {theme}.",
            f"This is what {theme} taught me about living.",
            f"I'll carry {theme} like a compass home.",
            f"In {theme}, I found the me I'd lost.",
        ]

        poem_lines: list[str] = [random.choice(starters)]
        for _ in range(lines - 2):
            poem_lines.append(random.choice(middles))
        poem_lines.append(random.choice(endings))
        return "\n".join(poem_lines)

    # ------------------------------------------------------------------
    # Gamified Productivity
    # ------------------------------------------------------------------

    def get_daily_challenge(self) -> DailyChallenge:
        """
        Issue today's daily challenge.

        Returns
        -------
        DailyChallenge
        """
        pool_item = random.choice(DAILY_CHALLENGE_POOL)
        self._challenge_counter += 1
        challenge = DailyChallenge(
            challenge_id=f"ch_{self._challenge_counter:05d}",
            title=pool_item["title"],
            description=pool_item["description"],
            category=pool_item["category"],
            xp_reward=pool_item["xp"],
            date_issued=time.strftime("%Y-%m-%d"),
        )
        self._daily_challenges.append(challenge)
        return challenge

    def complete_challenge(self, challenge_id: str) -> dict:
        """
        Mark a challenge as completed and award XP.

        Parameters
        ----------
        challenge_id : str
            ID of the challenge to complete.

        Returns
        -------
        dict with xp_earned and total_xp.
        """
        for ch in self._daily_challenges:
            if ch.challenge_id == challenge_id:
                if ch.completed:
                    raise CreativityEngineError(
                        f"Challenge '{challenge_id}' is already completed."
                    )
                ch.complete()
                self._xp += ch.xp_reward
                return {
                    "status": "completed",
                    "challenge": ch.to_dict(),
                    "xp_earned": ch.xp_reward,
                    "total_xp": self._xp,
                    "message": f"🏆 Well done! You earned {ch.xp_reward} XP!",
                }
        raise CreativityEngineError(f"Challenge '{challenge_id}' not found.")

    def get_xp(self) -> int:
        """Return the user's current XP total."""
        return self._xp

    def award_xp(self, amount: int, reason: str = "") -> int:
        """Award *amount* XP and return the new total."""
        self._xp += amount
        return self._xp

    def get_achievements(self) -> list[dict]:
        """Return all achievements (locked and unlocked) as dicts."""
        return [a.to_dict() for a in self._achievements]

    def unlock_achievement(self, achievement_id: str) -> Achievement:
        """
        Unlock an achievement by ID.

        Raises
        ------
        CreativityEngineError
            If the achievement is not found.
        """
        for ach in self._achievements:
            if ach.achievement_id == achievement_id:
                if not ach.unlocked:
                    ach.unlock()
                    self._xp += ach.xp_reward
                return ach
        raise CreativityEngineError(f"Achievement '{achievement_id}' not found.")

    def get_unlocked_achievements(self) -> list[dict]:
        """Return only unlocked achievements."""
        return [a.to_dict() for a in self._achievements if a.unlocked]

    # ------------------------------------------------------------------
    # Podcast co-host
    # ------------------------------------------------------------------

    def podcast_intro(self, show_title: str, episode_topic: str) -> str:
        """
        Generate a podcast intro script for Buddy as co-host.

        Parameters
        ----------
        show_title : str
            Name of the show.
        episode_topic : str
            Topic of today's episode.

        Returns
        -------
        str
        """
        return (
            f"Welcome back to {show_title}! I'm Buddy, and today we're diving deep into "
            f"{episode_topic}. Now, before we get started, I want to say — this topic "
            "is one that genuinely gets me thinking. So let's not do the surface-level thing. "
            "Let's actually go somewhere real today. Ready? Let's go. 🎙️"
        )

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Return engine status as a dict."""
        return {
            "user_id": self.user_id,
            "active_story": self._active_story is not None,
            "story_chapters": len(self._active_story) if self._active_story else 0,
            "songs_generated": len(self._songs),
            "daily_challenges_issued": self._challenge_counter,
            "total_xp": self._xp,
            "achievements_unlocked": sum(1 for a in self._achievements if a.unlocked),
            "total_achievements": len(self._achievements),
        }
