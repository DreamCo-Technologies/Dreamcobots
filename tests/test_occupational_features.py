"""Tests for Occupational_bots/feature_1.py, feature_2.py, feature_3.py"""
from __future__ import annotations

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from Occupational_bots.feature_1 import JobSearchBot, EXAMPLES as OC1_EXAMPLES
from Occupational_bots.feature_2 import ResumeBuildingBot, EXAMPLES as OC2_EXAMPLES
from Occupational_bots.feature_3 import InterviewPrepBot, EXAMPLES as OC3_EXAMPLES


# ===========================================================================
# Feature 1: JobSearchBot
# ===========================================================================

class TestJobSearchBotInstantiation:
    def test_default_tier_is_free(self):
        bot = JobSearchBot()
        assert bot.tier == "FREE"

    def test_pro_tier(self):
        bot = JobSearchBot(tier="PRO")
        assert bot.tier == "PRO"

    def test_enterprise_tier(self):
        bot = JobSearchBot(tier="ENTERPRISE")
        assert bot.tier == "ENTERPRISE"

    def test_invalid_tier_raises_value_error(self):
        with pytest.raises(ValueError):
            JobSearchBot(tier="VIP")

    def test_has_30_examples(self):
        assert len(OC1_EXAMPLES) == 30

    def test_examples_have_required_keys(self):
        required = {"id", "title", "company", "location", "salary_min", "salary_max"}
        for ex in OC1_EXAMPLES:
            assert required.issubset(ex.keys()), f"Missing keys in example: {ex}"


class TestJobSearchBotMethods:
    def test_search_jobs_returns_list(self):
        bot = JobSearchBot(tier="FREE")
        results = bot.search_jobs()
        assert isinstance(results, list)

    def test_free_tier_limits_results(self):
        bot = JobSearchBot(tier="FREE")
        results = bot.search_jobs()
        assert len(results) <= 5

    def test_search_jobs_by_title(self):
        bot = JobSearchBot(tier="ENTERPRISE")
        title_keyword = OC1_EXAMPLES[0]["title"].split()[0]
        results = bot.search_jobs(title=title_keyword)
        assert isinstance(results, list)

    def test_search_jobs_by_location(self):
        bot = JobSearchBot(tier="ENTERPRISE")
        first_location = OC1_EXAMPLES[0]["location"]
        results = bot.search_jobs(location=first_location)
        assert isinstance(results, list)

    def test_get_job_returns_dict(self):
        bot = JobSearchBot(tier="FREE")
        result = bot.get_job(OC1_EXAMPLES[0]["id"])
        assert isinstance(result, dict)
        assert result["id"] == OC1_EXAMPLES[0]["id"]

    def test_get_job_invalid_id_raises(self):
        bot = JobSearchBot(tier="FREE")
        with pytest.raises((ValueError, KeyError)):
            bot.get_job(9999)

    def test_get_remote_jobs_returns_list(self):
        bot = JobSearchBot(tier="PRO")
        jobs = bot.get_remote_jobs()
        assert isinstance(jobs, list)

    def test_get_jobs_by_platform_returns_list(self):
        bot = JobSearchBot(tier="PRO")
        platform = OC1_EXAMPLES[0].get("platform", "LinkedIn")
        jobs = bot.get_jobs_by_platform(platform)
        assert isinstance(jobs, list)

    def test_get_top_paying_jobs_returns_sorted(self):
        bot = JobSearchBot(tier="PRO")
        jobs = bot.get_top_paying_jobs(5)
        assert isinstance(jobs, list)
        assert len(jobs) <= 5
        salaries = [j["salary_max"] for j in jobs]
        assert salaries == sorted(salaries, reverse=True)

    def test_get_ai_job_matches_requires_pro(self):
        bot = JobSearchBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.get_ai_job_matches(["Python", "Django"])

    def test_get_ai_job_matches_pro_returns_list(self):
        bot = JobSearchBot(tier="PRO")
        matches = bot.get_ai_job_matches(["Python", "Django"])
        assert isinstance(matches, list)

    def test_track_application_requires_pro(self):
        bot = JobSearchBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.track_application(1)

    def test_track_application_pro_returns_dict(self):
        bot = JobSearchBot(tier="PRO")
        result = bot.track_application(OC1_EXAMPLES[0]["id"])
        assert isinstance(result, dict)

    def test_save_job_returns_dict(self):
        bot = JobSearchBot(tier="PRO")
        result = bot.save_job(OC1_EXAMPLES[0]["id"])
        assert isinstance(result, dict)

    def test_get_saved_jobs_returns_list(self):
        bot = JobSearchBot(tier="PRO")
        bot.save_job(OC1_EXAMPLES[0]["id"])
        saved = bot.get_saved_jobs()
        assert isinstance(saved, list)
        assert len(saved) >= 1

    def test_get_search_stats_returns_dict(self):
        bot = JobSearchBot(tier="PRO")
        stats = bot.get_search_stats()
        assert isinstance(stats, dict)

    def test_describe_tier_returns_string(self):
        bot = JobSearchBot(tier="FREE")
        desc = bot.describe_tier()
        assert isinstance(desc, str)

    def test_run_returns_dict(self):
        bot = JobSearchBot(tier="FREE")
        result = bot.run()
        assert isinstance(result, dict)
        assert "pipeline_complete" in result


# ===========================================================================
# Feature 2: ResumeBuildingBot
# ===========================================================================

class TestResumeBuildingBotInstantiation:
    def test_default_tier_is_free(self):
        bot = ResumeBuildingBot()
        assert bot.tier == "FREE"

    def test_pro_tier(self):
        bot = ResumeBuildingBot(tier="PRO")
        assert bot.tier == "PRO"

    def test_enterprise_tier(self):
        bot = ResumeBuildingBot(tier="ENTERPRISE")
        assert bot.tier == "ENTERPRISE"

    def test_invalid_tier_raises_value_error(self):
        with pytest.raises(ValueError):
            ResumeBuildingBot(tier="PLUS")

    def test_has_30_examples(self):
        assert len(OC2_EXAMPLES) == 30

    def test_examples_have_required_keys(self):
        required = {"id", "section", "role", "template", "ats_score"}
        for ex in OC2_EXAMPLES:
            assert required.issubset(ex.keys()), f"Missing keys in example: {ex}"


class TestResumeBuildingBotMethods:
    def test_get_templates_for_role_returns_list(self):
        bot = ResumeBuildingBot(tier="FREE")
        role = OC2_EXAMPLES[0]["role"]
        templates = bot.get_templates_for_role(role)
        assert isinstance(templates, list)

    def test_get_templates_by_section_returns_list(self):
        bot = ResumeBuildingBot(tier="FREE")
        section = OC2_EXAMPLES[0]["section"]
        templates = bot.get_templates_by_section(section)
        assert isinstance(templates, list)
        for t in templates:
            assert t["section"] == section

    def test_get_template_returns_dict(self):
        bot = ResumeBuildingBot(tier="FREE")
        template = bot.get_template(OC2_EXAMPLES[0]["id"])
        assert isinstance(template, dict)
        assert template["id"] == OC2_EXAMPLES[0]["id"]

    def test_get_template_invalid_id_raises(self):
        bot = ResumeBuildingBot(tier="FREE")
        with pytest.raises(ValueError):
            bot.get_template(9999)

    def test_check_ats_score_requires_pro(self):
        bot = ResumeBuildingBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.check_ats_score(1)

    def test_check_ats_score_pro_returns_dict(self):
        bot = ResumeBuildingBot(tier="PRO")
        result = bot.check_ats_score(OC2_EXAMPLES[0]["id"])
        assert isinstance(result, dict)
        assert "ats_score" in result or "score" in result

    def test_get_ai_suggestions_requires_pro(self):
        bot = ResumeBuildingBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.get_ai_suggestions("Software Engineer", "Professional Summary")

    def test_get_ai_suggestions_pro_returns_dict(self):
        bot = ResumeBuildingBot(tier="PRO")
        role = OC2_EXAMPLES[0]["role"]
        section = OC2_EXAMPLES[0]["section"]
        result = bot.get_ai_suggestions(role, section)
        assert isinstance(result, dict)

    def test_generate_cover_letter_requires_pro(self):
        bot = ResumeBuildingBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.generate_cover_letter("Software Engineer", "Google")

    def test_generate_cover_letter_pro_returns_dict(self):
        bot = ResumeBuildingBot(tier="PRO")
        result = bot.generate_cover_letter("Software Engineer", "Google")
        assert isinstance(result, dict)

    def test_get_high_ats_templates_returns_list(self):
        bot = ResumeBuildingBot(tier="PRO")
        templates = bot.get_high_ats_templates(min_score=90)
        assert isinstance(templates, list)
        for t in templates:
            assert t["ats_score"] >= 90

    def test_get_resume_sections_returns_list(self):
        bot = ResumeBuildingBot(tier="FREE")
        sections = bot.get_resume_sections()
        assert isinstance(sections, list)
        assert len(sections) > 0

    def test_free_tier_limits_templates(self):
        bot = ResumeBuildingBot(tier="FREE")
        templates = bot._available_templates()
        assert len(templates) <= 5

    def test_describe_tier_returns_string(self):
        bot = ResumeBuildingBot(tier="FREE")
        desc = bot.describe_tier()
        assert isinstance(desc, str)

    def test_run_returns_dict(self):
        bot = ResumeBuildingBot(tier="FREE")
        result = bot.run()
        assert isinstance(result, dict)
        assert "pipeline_complete" in result


# ===========================================================================
# Feature 3: InterviewPrepBot
# ===========================================================================

class TestInterviewPrepBotInstantiation:
    def test_default_tier_is_free(self):
        bot = InterviewPrepBot()
        assert bot.tier == "FREE"

    def test_pro_tier(self):
        bot = InterviewPrepBot(tier="PRO")
        assert bot.tier == "PRO"

    def test_enterprise_tier(self):
        bot = InterviewPrepBot(tier="ENTERPRISE")
        assert bot.tier == "ENTERPRISE"

    def test_invalid_tier_raises_value_error(self):
        with pytest.raises(ValueError):
            InterviewPrepBot(tier="EXPERT")

    def test_has_30_examples(self):
        assert len(OC3_EXAMPLES) == 30

    def test_examples_have_required_keys(self):
        required = {"id", "question", "type", "difficulty", "role", "star_answer"}
        for ex in OC3_EXAMPLES:
            assert required.issubset(ex.keys()), f"Missing keys in example: {ex}"


class TestInterviewPrepBotMethods:
    def test_get_questions_by_type_returns_list(self):
        bot = InterviewPrepBot(tier="FREE")
        questions = bot.get_questions_by_type("behavioral")
        assert isinstance(questions, list)
        for q in questions:
            assert q["type"] == "behavioral"

    def test_get_questions_by_type_invalid_raises(self):
        bot = InterviewPrepBot(tier="FREE")
        with pytest.raises(ValueError):
            bot.get_questions_by_type("invalid_type_xyz")

    def test_get_questions_by_role_returns_list(self):
        bot = InterviewPrepBot(tier="FREE")
        first_role = OC3_EXAMPLES[0]["role"]
        questions = bot.get_questions_by_role(first_role)
        assert isinstance(questions, list)

    def test_get_questions_by_difficulty_returns_list(self):
        bot = InterviewPrepBot(tier="FREE")
        questions = bot.get_questions_by_difficulty("easy")
        assert isinstance(questions, list)
        for q in questions:
            assert q["difficulty"] == "easy"

    def test_get_questions_by_difficulty_invalid_raises(self):
        bot = InterviewPrepBot(tier="FREE")
        with pytest.raises(ValueError):
            bot.get_questions_by_difficulty("impossible")

    def test_get_question_returns_dict(self):
        bot = InterviewPrepBot(tier="FREE")
        result = bot.get_question(OC3_EXAMPLES[0]["id"])
        assert isinstance(result, dict)
        assert result["id"] == OC3_EXAMPLES[0]["id"]

    def test_get_question_invalid_id_raises(self):
        bot = InterviewPrepBot(tier="FREE")
        with pytest.raises(ValueError):
            bot.get_question(9999)

    def test_get_star_answer_returns_dict(self):
        bot = InterviewPrepBot(tier="FREE")
        result = bot.get_star_answer(OC3_EXAMPLES[0]["id"])
        assert isinstance(result, dict)

    def test_start_mock_interview_requires_pro(self):
        bot = InterviewPrepBot(tier="FREE")
        with pytest.raises(PermissionError):
            bot.start_mock_interview("software_engineer")

    def test_start_mock_interview_pro_returns_list(self):
        bot = InterviewPrepBot(tier="PRO")
        questions = bot.start_mock_interview("software_engineer", difficulty="easy")
        assert isinstance(questions, list)

    def test_get_ai_coaching_requires_enterprise(self):
        bot = InterviewPrepBot(tier="PRO")
        with pytest.raises(PermissionError):
            bot.get_ai_coaching_feedback(1, "My answer here")

    def test_get_ai_coaching_enterprise_returns_dict(self):
        bot = InterviewPrepBot(tier="ENTERPRISE")
        result = bot.get_ai_coaching_feedback(OC3_EXAMPLES[0]["id"], "My answer here")
        assert isinstance(result, dict)

    def test_log_practice_returns_dict(self):
        bot = InterviewPrepBot(tier="PRO")
        result = bot.log_practice(OC3_EXAMPLES[0]["id"], self_rating=4)
        assert isinstance(result, dict)

    def test_get_prep_summary_returns_dict(self):
        bot = InterviewPrepBot(tier="PRO")
        summary = bot.get_prep_summary()
        assert isinstance(summary, dict)

    def test_free_tier_limits_questions(self):
        bot = InterviewPrepBot(tier="FREE")
        questions = bot._available_questions()
        assert len(questions) <= 10

    def test_describe_tier_returns_string(self):
        bot = InterviewPrepBot(tier="FREE")
        desc = bot.describe_tier()
        assert isinstance(desc, str)

    def test_run_returns_dict(self):
        bot = InterviewPrepBot(tier="FREE")
        result = bot.run()
        assert isinstance(result, dict)
        assert "pipeline_complete" in result
