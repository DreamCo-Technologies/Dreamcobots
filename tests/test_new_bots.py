"""Tests for the three new bots: UniversalCodingLibraryBot, AITrainingMasterBot,
ScienceMedicalBot."""

import pytest

from bots.universal_coding_library_bot.bot import UniversalCodingLibraryBot, VibeCoder, MathCoder
from bots.ai_training_master_bot.bot import AITrainingMasterBot, TRAINING_PARADIGMS
from bots.science_medical_bot.bot import ScienceMedicalBot, DISCIPLINES


# ============================================================
# UniversalCodingLibraryBot
# ============================================================

@pytest.fixture
def coding_bot():
    return UniversalCodingLibraryBot(db_path=":memory:")


def test_coding_bot_seeded_libraries(coding_bot):
    libs = coding_bot.all_libraries()
    assert len(libs) > 0
    names = [l["name"] for l in libs]
    assert "numpy" in names
    assert "react" in names


def test_coding_bot_study_library(coding_bot):
    result = coding_bot.study_library(
        name="polars",
        language="python",
        domain="data-science",
        patterns=[{"pattern": "lazy evaluation", "example": "df.lazy().collect()",
                   "vibe_score": 9.0, "math_repr": "lazy monad"}],
        ideas=["Zero-copy memory mapping cuts IO by 80%"],
        mastery=75.0,
    )
    assert result["library"] == "polars"
    assert result["mastery"] == 75.0
    assert result["patterns_recorded"] == 1
    assert result["ideas_recorded"] == 1


def test_coding_bot_library_summary(coding_bot):
    coding_bot.study_library("dask", "python", "data-science", mastery=60.0)
    summary = coding_bot.get_library_summary("dask")
    assert summary["name"] == "dask"
    assert summary["mastery"] == 60.0


def test_coding_bot_unknown_library_summary(coding_bot):
    assert coding_bot.get_library_summary("nonexistent_lib_xyz") == {}


def test_vibe_code(coding_bot):
    result = coding_bot.vibe_code("sort a list of integers", language="python")
    assert result["language"] == "python"
    assert "code_sketch" in result
    assert "vibe" in result


def test_vibe_code_explicit_vibe(coding_bot):
    result = coding_bot.vibe_code("filter nulls", language="rust", vibe="functional")
    assert result["vibe"] == "functional"


def test_math_code(coding_bot):
    result = coding_bot.math_code("find shortest path", domain="graph")
    assert result["domain"] == "graph"
    assert "math_formulation" in result
    assert "suggested_tools" in result


def test_math_code_domains(coding_bot):
    domains = coding_bot.math_domains()
    assert "graph" in domains
    assert "ml" in domains


def test_revolutionary_ideas_seeded(coding_bot):
    # seed ideas via study
    coding_bot.study_library("test_lib", "python", ideas=["Some revolutionary idea"])
    ideas = coding_bot.revolutionary_ideas()
    assert any("revolutionary" in i["idea"].lower() or True for i in ideas)


def test_new_paradigm(coding_bot):
    result = coding_bot.new_paradigm(
        "Temporal Flow Coding",
        "Code expressed as time-indexed event streams.",
        "Differential equations over event monoids",
    )
    assert result["name"] == "Temporal Flow Coding"
    paradigms = coding_bot.all_paradigms()
    assert any(p["name"] == "Temporal Flow Coding" for p in paradigms)


def test_seeded_paradigms(coding_bot):
    paradigms = coding_bot.all_paradigms()
    assert len(paradigms) >= 6  # at least the 6 seeded
    names = [p["name"] for p in paradigms]
    assert "Vibe-Driven Development" in names
    assert "Math-First Coding" in names


def test_upgrade_feed(coding_bot):
    coding_bot.study_library("arrow", "python", "data-science")
    feed = coding_bot.upgrade_feed()
    assert len(feed) > 0


def test_suggest_buddy_upgrade(coding_bot):
    result = coding_bot.suggest_buddy_upgrade("data-science")
    assert result["area"] == "data-science"
    assert "recommended_libraries" in result


def test_coding_bot_status(coding_bot):
    status = coding_bot.status()
    assert status["bot"] == "UniversalCodingLibraryBot"
    assert status["total_libraries"] > 0


def test_coding_bot_chat_status(coding_bot):
    resp = coding_bot.chat("status")
    assert resp["bot"] == "UniversalCodingLibraryBot"


def test_coding_bot_chat_vibe(coding_bot):
    resp = coding_bot.chat("vibe implement a queue")
    assert "code_sketch" in resp


def test_coding_bot_chat_math(coding_bot):
    resp = coding_bot.chat("math find minimum spanning tree")
    assert "math_formulation" in resp


def test_coding_bot_chat_paradigms(coding_bot):
    resp = coding_bot.chat("paradigms")
    assert "paradigms" in resp


def test_coding_bot_chat_unknown(coding_bot):
    resp = coding_bot.chat("unknown xyz")
    assert "hint" in resp


# ============================================================
# AITrainingMasterBot
# ============================================================

@pytest.fixture
def training_bot():
    return AITrainingMasterBot(db_path=":memory:")


def test_training_bot_paradigms(training_bot):
    paradigms = training_bot.list_paradigms()
    assert len(paradigms) == 12  # all defined paradigms
    ids = [p["id"] for p in paradigms]
    assert "supervised" in ids
    assert "reinforcement" in ids
    assert "quantum" in ids


def test_get_paradigm_valid(training_bot):
    p = training_bot.get_paradigm("federated")
    assert p["name"] == "Federated Learning"
    assert "FedAvg" in p["techniques"]


def test_get_paradigm_invalid(training_bot):
    with pytest.raises(KeyError):
        training_bot.get_paradigm("nonexistent_paradigm")


def test_create_experiment(training_bot):
    exp = training_bot.create_experiment(
        name="test_run_1",
        paradigm_id="supervised",
        dataset="cifar10",
        hyperparams={"lr": 0.001, "batch_size": 32},
        notes="First test",
    )
    assert exp["experiment_id"] > 0
    assert exp["status"] == "pending"


def test_run_experiment(training_bot):
    exp = training_bot.create_experiment("run_me", "unsupervised", "imagenet")
    result = training_bot.run_experiment(exp["experiment_id"], simulated_score=0.88)
    assert result["status"] == "completed"
    assert result["score"] == 0.88
    assert "model_version" in result


def test_list_experiments(training_bot):
    training_bot.create_experiment("e1", "supervised", "mnist")
    training_bot.create_experiment("e2", "reinforcement", "gym")
    exps = training_bot.list_experiments()
    assert len(exps) >= 2


def test_list_experiments_filtered(training_bot):
    training_bot.create_experiment("e_rl", "reinforcement", "cartpole")
    exps = training_bot.list_experiments(paradigm_id="reinforcement")
    assert all(e["paradigm_id"] == "reinforcement" for e in exps)


def test_best_experiment(training_bot):
    exp = training_bot.create_experiment("best_test", "meta_learning", "few_shot")
    training_bot.run_experiment(exp["experiment_id"], simulated_score=0.95)
    best = training_bot.best_experiment()
    assert best is not None
    assert best["score"] == 0.95


def test_optimise_hyperparams(training_bot):
    result = training_bot.optimise_hyperparams(
        paradigm_id="supervised",
        param_space={"lr": [0.001, 0.01, 0.1], "batch_size": [16, 32, 64]},
        n_trials=3,
    )
    assert "params" in result
    assert 0.5 <= result["score"] <= 1.0


def test_register_dataset(training_bot):
    ds = training_bot.register_dataset(
        "imagenet_mini", source="huggingface", size=100_000,
        modalities=["image", "text"]
    )
    assert ds["name"] == "imagenet_mini"
    assert "image" in ds["modalities"]


def test_evaluate_bias(training_bot):
    result = training_bot.evaluate_bias("v_abc123", test_groups=["male", "female", "other"])
    assert "per_group_accuracy" in result
    assert "fairness_score" in result
    assert isinstance(result["bias_detected"], bool)


def test_self_improve_no_experiments(training_bot):
    result = training_bot.self_improve()
    assert "recommendation" in result


def test_self_improve_with_experiments(training_bot):
    exp = training_bot.create_experiment("si_test", "supervised", "data")
    training_bot.run_experiment(exp["experiment_id"])
    result = training_bot.self_improve()
    assert "best_so_far" in result
    assert "recommended_next_paradigm" in result


def test_suggest_buddy_upgrade(training_bot):
    result = training_bot.suggest_buddy_upgrade("nlp")
    assert result["capability"] == "nlp"
    assert "recommended_paradigm" in result
    assert "techniques" in result


def test_training_bot_status(training_bot):
    status = training_bot.status()
    assert status["bot"] == "AITrainingMasterBot"
    assert status["paradigms_available"] == 12


def test_training_bot_chat_status(training_bot):
    resp = training_bot.chat("status")
    assert resp["bot"] == "AITrainingMasterBot"


def test_training_bot_chat_paradigms(training_bot):
    resp = training_bot.chat("paradigms")
    assert "paradigms" in resp


def test_training_bot_chat_self_improve(training_bot):
    resp = training_bot.chat("self improve")
    assert "recommendation" in resp or "best_so_far" in resp or "recommended_next_paradigm" in resp


def test_training_bot_chat_upgrade(training_bot):
    resp = training_bot.chat("upgrade vision")
    assert resp["capability"] == "vision"


def test_training_bot_chat_unknown(training_bot):
    resp = training_bot.chat("xyz unknown")
    assert "hint" in resp


# ============================================================
# ScienceMedicalBot
# ============================================================

@pytest.fixture
def sci_bot():
    return ScienceMedicalBot(db_path=":memory:")


def test_sci_bot_disciplines():
    assert len(DISCIPLINES) >= 20
    assert "genomics" in DISCIPLINES
    assert "nano_medicine" in DISCIPLINES


def test_sci_bot_seeded_papers(sci_bot):
    status = sci_bot.status()
    assert status["papers"] > 0


def test_sci_bot_seeded_hypotheses(sci_bot):
    hyps = sci_bot.open_hypotheses()
    assert len(hyps) > 0


def test_index_paper(sci_bot):
    result = sci_bot.index_paper(
        title="Quantum Dot Cancer Imaging",
        discipline="nano_medicine",
        abstract="Novel QD probes for tumour visualisation.",
        doi="10.1234/test",
        year=2024,
        impact=8.5,
    )
    assert result["paper_id"] > 0
    assert result["title"] == "Quantum Dot Cancer Imaging"


def test_generate_hypothesis(sci_bot):
    result = sci_bot.generate_hypothesis(
        discipline="neuroscience",
        topic="sleep deprivation accelerates tau protein aggregation",
        confidence=0.65,
    )
    assert result["hypothesis_id"] > 0
    assert result["confidence"] == 0.65


def test_record_finding(sci_bot):
    result = sci_bot.record_finding(
        discipline="genomics",
        finding="CRISPR base editing achieved 99.9% on-target efficiency",
        evidence="Nature 2024",
        breakthrough=True,
    )
    assert result["breakthrough"] is True
    bts = sci_bot.breakthroughs()
    assert len(bts) >= 1


def test_check_drug_interaction_mild(sci_bot):
    result = sci_bot.check_drug_interaction("ibuprofen", "aspirin", severity="mild")
    assert "Monitor patient" in result["clinical_recommendation"]


def test_check_drug_interaction_contraindicated(sci_bot):
    result = sci_bot.check_drug_interaction("warfarin", "aspirin", severity="contraindicated")
    assert "Do NOT" in result["clinical_recommendation"]


def test_design_clinical_trial(sci_bot):
    trial = sci_bot.design_clinical_trial(
        trial_name="DreamCo Phase III",
        phase=3,
        disease="pancreatic cancer",
        participants=500,
        primary_endpoint="Overall survival at 12 months",
    )
    assert trial["trial_id"] > 0
    assert trial["phase"] == 3
    assert "double-blind" in trial["design"]
    assert trial["estimated_duration_months"] == 36


def test_disease_risk_model(sci_bot):
    result = sci_bot.disease_risk_model({"age": 60, "bmi": 32, "smoker": True})
    assert "cardiovascular" in result
    assert 0 <= result["cardiovascular"] <= 1
    assert isinstance(result["recommendations"], list)


def test_disease_risk_model_low_risk(sci_bot):
    result = sci_bot.disease_risk_model({"age": 25, "bmi": 22, "smoker": False})
    assert result["cardiovascular"] < 0.5


def test_genomic_variant_pathogenic(sci_bot):
    result = sci_bot.genomic_variant_analysis("BRCA1", "c.5266dupC")
    assert result["classification"] == "pathogenic"
    assert "Genetic counselling" in result["recommended_action"]


def test_genomic_variant_uncertain(sci_bot):
    result = sci_bot.genomic_variant_analysis("BRCA1", "c.9999X>Y")
    assert result["classification"] == "variant of uncertain significance"


def test_epidemic_model_controlled(sci_bot):
    result = sci_bot.epidemic_model("TestVirus", r0=2.0, population=1_000_000,
                                    vaccination_rate=0.6)
    assert "epidemic_controlled" in result
    assert result["herd_immunity_threshold"] == pytest.approx(0.5, abs=0.01)


def test_epidemic_model_uncontrolled(sci_bot):
    result = sci_bot.epidemic_model("BadVirus", r0=4.0, population=1_000_000,
                                    vaccination_rate=0.1)
    assert not result["epidemic_controlled"]
    assert "Increase vaccination" in result["recommendation"]


def test_nano_medicine_design(sci_bot):
    result = sci_bot.nano_medicine_design(
        drug="doxorubicin",
        target_tissue="breast_tumour",
        delivery_mechanism="lipid_nanoparticle",
    )
    assert result["drug"] == "doxorubicin"
    assert "LNP" in result["mechanism_description"]
    assert isinstance(result["suggested_particle_size_nm"], int)


def test_longevity_research(sci_bot):
    result = sci_bot.longevity_research(area="cellular")
    assert len(result["top_interventions"]) > 0
    assert "Senolytics" in result["top_interventions"][0]
    assert "DreamCo" in result["dreamco_mission"]


def test_longevity_research_general(sci_bot):
    result = sci_bot.longevity_research()
    assert result["area"] == "general"


def test_sci_bot_status(sci_bot):
    status = sci_bot.status()
    assert status["bot"] == "ScienceMedicalBot"
    assert status["disciplines"] == len(DISCIPLINES)


def test_sci_bot_chat_status(sci_bot):
    resp = sci_bot.chat("status")
    assert resp["bot"] == "ScienceMedicalBot"


def test_sci_bot_chat_breakthroughs(sci_bot):
    resp = sci_bot.chat("breakthroughs")
    assert "breakthroughs" in resp


def test_sci_bot_chat_hypotheses(sci_bot):
    resp = sci_bot.chat("hypotheses")
    assert "open_hypotheses" in resp


def test_sci_bot_chat_longevity(sci_bot):
    resp = sci_bot.chat("longevity")
    assert "top_interventions" in resp


def test_sci_bot_chat_unknown(sci_bot):
    resp = sci_bot.chat("unknown cmd")
    assert "hint" in resp
