"""Education Bot - Personalized learning plans, quizzes, and certification paths."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from datetime import datetime
from core.base_bot import BaseBot


class EducationBot(BaseBot):
    """AI bot for personalized education: learning plans, quizzes, schedules, and certifications."""

    def __init__(self):
        """Initialize the EducationBot."""
        super().__init__(
            name="education-bot",
            description="Creates personalized learning plans, generates quizzes, tracks progress, and maps certification paths.",
            version="2.0.0",
        )
        self.priority = "medium"
        self._progress_tracker = {}

    def run(self):
        """Run the education bot main workflow."""
        self.start()
        return self.get_status()

    def create_learning_plan(self, subject: str, current_level: str,
                             target_level: str, timeframe_weeks: int) -> dict:
        """Create a personalized learning plan for a subject."""
        levels = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}
        start = levels.get(current_level.lower(), 1)
        end = levels.get(target_level.lower(), 3)
        gap = max(1, end - start)
        weeks_per_level = max(1, timeframe_weeks // gap)
        phases = []
        level_names = ["beginner", "intermediate", "advanced", "expert"]
        for i in range(gap):
            phase_level = level_names[min(start + i, 3)]
            phases.append({
                "phase": i + 1,
                "level": phase_level,
                "duration_weeks": weeks_per_level,
                "topics": [
                    f"{subject} fundamentals ({phase_level})",
                    f"Practical {subject} projects",
                    f"{subject} best practices",
                    f"Assessment and review",
                ],
                "resources": [
                    f"Book: {subject.title()} Mastery ({phase_level.title()} Edition)",
                    f"Online course: Udemy - Complete {subject.title()} Course",
                    f"YouTube: {subject.title()} tutorials by top educators",
                    f"Practice: Build 2 projects this phase",
                ],
                "milestone": f"Complete {phase_level} {subject} assessment with 80%+ score",
            })
        return {
            "subject": subject,
            "current_level": current_level,
            "target_level": target_level,
            "timeframe_weeks": timeframe_weeks,
            "daily_study_hours": round(timeframe_weeks * 7 / timeframe_weeks, 1),
            "phases": phases,
            "success_metrics": [
                "Complete 80% of planned resources",
                "Build 2+ portfolio projects",
                "Pass certification exam if applicable",
            ],
        }

    def generate_quiz(self, topic: str, num_questions: int = 5, difficulty: str = "medium") -> dict:
        """Generate a quiz on a given topic."""
        difficulty_map = {"easy": 1, "medium": 2, "hard": 3}
        diff_level = difficulty_map.get(difficulty.lower(), 2)
        questions = []
        for i in range(num_questions):
            questions.append({
                "question_number": i + 1,
                "question": f"[{difficulty.upper()}] Which of the following best describes {topic} concept #{i + 1}?",
                "options": [
                    f"A) The correct answer about {topic}",
                    f"B) A plausible but incorrect answer",
                    f"C) An obviously wrong answer",
                    f"D) Another plausible but incorrect answer",
                ],
                "correct_answer": "A",
                "explanation": f"Option A is correct because it accurately describes the core principle of {topic} concept #{i + 1}.",
                "difficulty": difficulty,
                "points": diff_level * 10,
            })
        return {
            "topic": topic,
            "difficulty": difficulty,
            "num_questions": num_questions,
            "total_points": sum(q["points"] for q in questions),
            "passing_score_percent": 70,
            "time_limit_minutes": num_questions * 2,
            "questions": questions,
        }

    def build_study_schedule(self, subjects_list: list, hours_per_day: float) -> dict:
        """Build a weekly study schedule for multiple subjects."""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        schedule = {}
        total_hours_per_week = hours_per_day * 7
        hours_per_subject = total_hours_per_week / len(subjects_list) if subjects_list else 0
        for i, day in enumerate(days):
            subject = subjects_list[i % len(subjects_list)] if subjects_list else "Self-study"
            schedule[day] = {
                "subject": subject,
                "hours": hours_per_day,
                "activities": [
                    f"Review previous {subject} notes (15 min)",
                    f"Study new {subject} material ({int(hours_per_day * 0.5 * 60)} min)",
                    f"Practice problems/exercises ({int(hours_per_day * 0.3 * 60)} min)",
                    f"Summarize and write flashcards (15 min)",
                ],
            }
        return {
            "subjects": subjects_list,
            "hours_per_day": hours_per_day,
            "total_weekly_hours": round(total_hours_per_week, 1),
            "hours_per_subject_per_week": round(hours_per_subject, 1),
            "weekly_schedule": schedule,
            "tips": [
                "Use the Pomodoro technique: 25 min study, 5 min break",
                "Review material within 24 hours of learning (spaced repetition)",
                "Teach concepts to others to deepen understanding",
            ],
        }

    def recommend_courses(self, skill: str, level: str) -> list:
        """Recommend courses for a skill at a given level."""
        platforms = ["Coursera", "Udemy", "edX", "LinkedIn Learning", "Skillshare", "Pluralsight"]
        courses = []
        for i, platform in enumerate(platforms[:4]):
            courses.append({
                "title": f"Complete {skill.title()} {level.title()} Course - {platform}",
                "platform": platform,
                "level": level,
                "duration": f"{8 + i * 4} hours",
                "rating": round(4.4 + i * 0.1, 1),
                "price": f"${19.99 + i * 10:.2f}" if i > 0 else "Free with subscription",
                "certificate": True,
                "url": f"https://www.{platform.lower()}.com/search?q={skill.replace(' ', '+')}",
            })
        return courses

    def map_certification_path(self, target_job: str) -> dict:
        """Map the certification path to a target career."""
        cert_maps = {
            "data scientist": [
                {"cert": "Python for Data Science (Enterprise AI)", "platform": "Coursera", "duration": "3 months"},
                {"cert": "Google Data Analytics Certificate", "platform": "Coursera", "duration": "6 months"},
                {"cert": "AWS Certified Machine Learning", "platform": "AWS", "duration": "3 months"},
                {"cert": "TensorFlow Developer Certificate", "platform": "Google", "duration": "2 months"},
            ],
            "cybersecurity": [
                {"cert": "CompTIA Security+", "platform": "CompTIA", "duration": "3 months"},
                {"cert": "Certified Ethical Hacker (CEH)", "platform": "EC-Council", "duration": "4 months"},
                {"cert": "CISSP", "platform": "ISC2", "duration": "6-12 months"},
            ],
            "project manager": [
                {"cert": "PMP (Project Management Professional)", "platform": "PMI", "duration": "6 months"},
                {"cert": "Certified Scrum Master (CSM)", "platform": "Scrum Alliance", "duration": "2 days"},
                {"cert": "Google Project Management Certificate", "platform": "Coursera", "duration": "6 months"},
            ],
        }
        path_key = next((k for k in cert_maps if k in target_job.lower()), None)
        certs = cert_maps.get(path_key, [
            {"cert": f"Foundational {target_job} Certificate", "platform": "Coursera/edX", "duration": "3 months"},
            {"cert": f"Advanced {target_job} Certification", "platform": "Industry body", "duration": "6 months"},
        ])
        return {
            "target_job": target_job,
            "certifications": certs,
            "total_timeline": f"{len(certs) * 3}-{len(certs) * 6} months",
            "estimated_cost": f"${len(certs) * 300}-${len(certs) * 800}",
            "salary_boost_estimate": "15-40% premium for certified professionals",
        }

    def analyze_skill_gaps(self, current_skills: list, target_skills: list) -> dict:
        """Analyze gaps between current and target skill sets."""
        current_set = set(s.lower() for s in current_skills)
        target_set = set(s.lower() for s in target_skills)
        gaps = target_set - current_set
        strengths = current_set & target_set
        extras = current_set - target_set
        return {
            "current_skills": current_skills,
            "target_skills": target_skills,
            "skill_gaps": sorted(list(gaps)),
            "existing_strengths": sorted(list(strengths)),
            "bonus_skills": sorted(list(extras)),
            "gap_count": len(gaps),
            "readiness_percent": round(len(strengths) / len(target_set) * 100, 1) if target_set else 100,
            "priority_skills_to_learn": sorted(list(gaps))[:5],
            "estimated_time_to_close_gaps": f"{len(gaps) * 4}-{len(gaps) * 8} weeks",
        }

    def track_progress(self, student_id: str, subject: str, score: float) -> dict:
        """Track a student's progress on a subject."""
        if student_id not in self._progress_tracker:
            self._progress_tracker[student_id] = {}
        if subject not in self._progress_tracker[student_id]:
            self._progress_tracker[student_id][subject] = []
        entry = {"score": score, "date": datetime.utcnow().isoformat()}
        self._progress_tracker[student_id][subject].append(entry)
        history = self._progress_tracker[student_id][subject]
        avg_score = sum(e["score"] for e in history) / len(history)
        trend = "improving" if len(history) > 1 and history[-1]["score"] > history[-2]["score"] else "stable"
        return {
            "student_id": student_id,
            "subject": subject,
            "latest_score": score,
            "average_score": round(avg_score, 1),
            "sessions_completed": len(history),
            "trend": trend,
            "recommendation": "Continue current pace" if avg_score >= 70 else "Schedule additional tutoring sessions",
        }

    def adapt_to_learning_style(self, style: str, content: str) -> dict:
        """Adapt educational content for different learning styles."""
        adaptations = {
            "visual": {
                "format": "Infographics, diagrams, mind maps, color-coded notes",
                "tip": "Draw concept maps before reading. Use highlighters.",
                "resources": "YouTube tutorials, infographic tools (Canva), visual textbooks",
            },
            "auditory": {
                "format": "Podcasts, read-aloud study, verbal explanations",
                "tip": "Record yourself explaining concepts. Use text-to-speech.",
                "resources": "Podcasts, audiobooks, study groups, verbal flashcard apps",
            },
            "kinesthetic": {
                "format": "Hands-on projects, labs, simulations, role-play",
                "tip": "Build projects while learning. Take frequent breaks with movement.",
                "resources": "Coding bootcamps, labs, maker spaces, interactive simulations",
            },
            "reading_writing": {
                "format": "Detailed notes, summaries, written practice problems",
                "tip": "Rewrite key concepts in your own words. Use spaced repetition apps.",
                "resources": "Textbooks, note-taking apps (Notion, Obsidian), written tests",
            },
        }
        style_key = style.lower().replace("-", "_").replace("/", "_")
        adaptation = adaptations.get(style_key, adaptations["visual"])
        return {
            "learning_style": style,
            "content_topic": content,
            "adapted_format": adaptation["format"],
            "study_tip": adaptation["tip"],
            "recommended_resources": adaptation["resources"],
        }
