"""Tests for bots/biomedical_bot/ — health monitoring, precision medicine, and main bot."""
import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
AI_MODELS_DIR = os.path.join(REPO_ROOT, "bots", "ai-models-integration")
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, "models"))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.biomedical_bot.health_monitor import (
    WearableHealthMonitor,
    WearableHealthMonitorError,
    VITAL_THRESHOLDS,
)
from bots.biomedical_bot.precision_medicine import (
    NanotechDiseaseDetector,
    NanotechDiseaseDetectorError,
    PrecisionMedicineEngine,
    PrecisionMedicineError,
)
from bots.biomedical_bot.biomedical_bot import BiomedicalBot, BiomedicalBotError
from bots.biomedical_bot.tiers import BOT_FEATURES, get_bot_tier_info


# ===========================================================================
# Tiers
# ===========================================================================

class TestBiomedicalTiers:
    def test_bot_features_has_all_tiers(self):
        assert Tier.FREE.value in BOT_FEATURES
        assert Tier.PRO.value in BOT_FEATURES
        assert Tier.ENTERPRISE.value in BOT_FEATURES

    def test_free_tier_info(self):
        info = get_bot_tier_info(Tier.FREE)
        assert info["tier"] == "free"
        assert info["price_usd_monthly"] == 0.0
        assert len(info["features"]) > 0

    def test_pro_tier_info(self):
        info = get_bot_tier_info(Tier.PRO)
        assert info["tier"] == "pro"
        assert info["price_usd_monthly"] == 49.0

    def test_enterprise_tier_info(self):
        info = get_bot_tier_info(Tier.ENTERPRISE)
        assert info["tier"] == "enterprise"
        assert info["price_usd_monthly"] == 299.0

    def test_enterprise_has_api(self):
        info = get_bot_tier_info(Tier.ENTERPRISE)
        assert any("api" in f.lower() or "API" in f for f in info["features"])

    def test_tier_info_has_support(self):
        for tier in Tier:
            info = get_bot_tier_info(tier)
            assert "support_level" in info

    def test_free_features_non_empty(self):
        assert len(BOT_FEATURES[Tier.FREE.value]) >= 3

    def test_enterprise_has_more_features_than_free(self):
        assert len(BOT_FEATURES[Tier.ENTERPRISE.value]) > len(BOT_FEATURES[Tier.FREE.value])


# ===========================================================================
# VITAL_THRESHOLDS
# ===========================================================================

class TestVitalThresholds:
    def test_heart_rate_threshold(self):
        low, high = VITAL_THRESHOLDS["heart_rate"]
        assert low == 60
        assert high == 100

    def test_glucose_threshold(self):
        low, high = VITAL_THRESHOLDS["glucose"]
        assert low == 70
        assert high == 140

    def test_required_keys_present(self):
        for key in ("heart_rate", "glucose", "systolic_bp", "spo2"):
            assert key in VITAL_THRESHOLDS


# ===========================================================================
# WearableHealthMonitor — heart rate
# ===========================================================================

class TestWearableHealthMonitorHeartRate:
    def test_default_tier_is_free(self):
        m = WearableHealthMonitor()
        assert m.tier == Tier.FREE

    def test_monitor_heart_rate_returns_dict(self):
        m = WearableHealthMonitor(Tier.FREE)
        result = m.monitor_heart_rate("p1", [72, 75, 68])
        assert isinstance(result, dict)

    def test_monitor_heart_rate_has_required_keys(self):
        m = WearableHealthMonitor(Tier.FREE)
        result = m.monitor_heart_rate("p1", [72, 75, 68])
        for key in ("patient_id", "metric", "average_bpm", "status"):
            assert key in result

    def test_monitor_heart_rate_normal(self):
        m = WearableHealthMonitor(Tier.FREE)
        result = m.monitor_heart_rate("p1", [70, 75, 80])
        assert result["status"] == "normal"

    def test_monitor_heart_rate_alert(self):
        m = WearableHealthMonitor(Tier.PRO)
        result = m.monitor_heart_rate("p1", [120, 130, 140])
        assert result["status"] == "alert"
        assert result["anomaly_count"] > 0

    def test_monitor_heart_rate_empty_readings(self):
        m = WearableHealthMonitor(Tier.FREE)
        result = m.monitor_heart_rate("p1", [])
        assert result["status"] == "no_data"

    def test_pro_heart_rate_has_trend(self):
        m = WearableHealthMonitor(Tier.PRO)
        result = m.monitor_heart_rate("p1", [70, 75, 80])
        assert "trend" in result

    def test_enterprise_heart_rate_has_ml_risk(self):
        m = WearableHealthMonitor(Tier.ENTERPRISE)
        result = m.monitor_heart_rate("p1", [70, 75, 80])
        assert "ml_risk_score" in result

    def test_free_tier_patient_limit(self):
        m = WearableHealthMonitor(Tier.FREE)
        m.monitor_heart_rate("p1", [72])
        with pytest.raises(WearableHealthMonitorError):
            m.monitor_heart_rate("p2", [80])

    def test_pro_allows_multiple_patients(self):
        m = WearableHealthMonitor(Tier.PRO)
        for i in range(5):
            result = m.monitor_heart_rate(f"p{i}", [72])
            assert result["patient_id"] == f"p{i}"


# ===========================================================================
# WearableHealthMonitor — glucose
# ===========================================================================

class TestWearableHealthMonitorGlucose:
    def test_free_tier_cannot_monitor_glucose(self):
        m = WearableHealthMonitor(Tier.FREE)
        m.monitor_heart_rate("p1", [72])  # register patient first
        with pytest.raises(WearableHealthMonitorError):
            m.monitor_glucose("p1", [100, 110])

    def test_pro_monitor_glucose_returns_dict(self):
        m = WearableHealthMonitor(Tier.PRO)
        result = m.monitor_glucose("p1", [100, 110, 120])
        assert isinstance(result, dict)

    def test_pro_glucose_has_required_keys(self):
        m = WearableHealthMonitor(Tier.PRO)
        result = m.monitor_glucose("p1", [100, 110])
        for key in ("patient_id", "metric", "average_mg_dl", "status"):
            assert key in result

    def test_glucose_normal_range(self):
        m = WearableHealthMonitor(Tier.PRO)
        result = m.monitor_glucose("p1", [90, 100, 110])
        assert result["status"] == "normal"

    def test_glucose_hyperglycemic_alert(self):
        m = WearableHealthMonitor(Tier.PRO)
        result = m.monitor_glucose("p1", [200, 250, 300])
        assert result["status"] == "alert"
        assert result["hyperglycemic_events"] > 0

    def test_glucose_hypoglycemic_alert(self):
        m = WearableHealthMonitor(Tier.PRO)
        result = m.monitor_glucose("p1", [50, 55, 60])
        assert result["hypoglycemic_events"] > 0

    def test_enterprise_glucose_has_diabetes_risk(self):
        m = WearableHealthMonitor(Tier.ENTERPRISE)
        result = m.monitor_glucose("p1", [130, 135])
        assert "diabetes_risk" in result


# ===========================================================================
# WearableHealthMonitor — vitals & reports
# ===========================================================================

class TestWearableHealthMonitorVitals:
    def test_track_vitals_returns_dict(self):
        m = WearableHealthMonitor(Tier.PRO)
        result = m.track_vitals("p1", {"heart_rate": 75, "spo2": 98})
        assert isinstance(result, dict)

    def test_track_vitals_normal(self):
        m = WearableHealthMonitor(Tier.PRO)
        result = m.track_vitals("p1", {"heart_rate": 75, "spo2": 98})
        assert result["overall_status"] == "normal"

    def test_track_vitals_alert_on_anomaly(self):
        m = WearableHealthMonitor(Tier.PRO)
        result = m.track_vitals("p1", {"heart_rate": 200, "spo2": 80})
        assert result["overall_status"] == "alert"
        assert len(result["alert_metrics"]) > 0

    def test_track_vitals_unavailable_metric_on_free(self):
        m = WearableHealthMonitor(Tier.FREE)
        result = m.track_vitals("p1", {"glucose": 100})
        assert result["vitals"]["glucose"]["status"] == "unavailable_on_tier"

    def test_generate_health_report_returns_dict(self):
        m = WearableHealthMonitor(Tier.FREE)
        m.monitor_heart_rate("p1", [72, 75])
        report = m.generate_health_report("p1")
        assert isinstance(report, dict)

    def test_generate_health_report_keys(self):
        m = WearableHealthMonitor(Tier.PRO)
        m.monitor_heart_rate("p1", [72])
        report = m.generate_health_report("p1")
        for key in ("patient_id", "metrics_tracked", "overall_health"):
            assert key in report

    def test_pro_report_has_recommendations(self):
        m = WearableHealthMonitor(Tier.PRO)
        m.monitor_heart_rate("p1", [72])
        report = m.generate_health_report("p1")
        assert "recommendations" in report

    def test_enterprise_report_has_ml_insights(self):
        m = WearableHealthMonitor(Tier.ENTERPRISE)
        m.monitor_heart_rate("p1", [72])
        report = m.generate_health_report("p1")
        assert "ml_insights" in report


# ===========================================================================
# WearableHealthMonitor — anomaly alerts
# ===========================================================================

class TestWearableHealthMonitorAnomalyAlert:
    def test_alert_anomaly_normal_value(self):
        m = WearableHealthMonitor(Tier.FREE)
        m.monitor_heart_rate("p1", [72])  # register patient
        result = m.alert_anomaly("p1", "heart_rate", 80)
        assert result["anomaly_detected"] is False
        assert result["alert_level"] == "none"

    def test_alert_anomaly_high_heart_rate(self):
        m = WearableHealthMonitor(Tier.PRO)
        result = m.alert_anomaly("p1", "heart_rate", 150)
        assert result["anomaly_detected"] is True
        assert result["action_required"] is True

    def test_alert_anomaly_low_glucose(self):
        m = WearableHealthMonitor(Tier.PRO)
        result = m.alert_anomaly("p1", "glucose", 40)
        assert result["anomaly_detected"] is True

    def test_enterprise_alert_has_auto_escalate(self):
        m = WearableHealthMonitor(Tier.ENTERPRISE)
        result = m.alert_anomaly("p1", "heart_rate", 160)
        assert result.get("auto_escalate") is True
        assert "notify_channels" in result

    def test_pro_alert_has_direction_message(self):
        m = WearableHealthMonitor(Tier.PRO)
        result = m.alert_anomaly("p1", "heart_rate", 150)
        assert "direction" in result
        assert "message" in result

    def test_free_tier_cannot_alert_glucose(self):
        m = WearableHealthMonitor(Tier.FREE)
        m.monitor_heart_rate("p1", [72])
        with pytest.raises(WearableHealthMonitorError):
            m.alert_anomaly("p1", "glucose", 200)


# ===========================================================================
# NanotechDiseaseDetector
# ===========================================================================

class TestNanotechDiseaseDetector:
    def test_free_tier_detect_raises(self):
        d = NanotechDiseaseDetector(Tier.FREE)
        with pytest.raises(NanotechDiseaseDetectorError):
            d.detect_disease_markers({"CEA": 5.0})

    def test_pro_detect_markers_returns_dict(self):
        d = NanotechDiseaseDetector(Tier.PRO)
        result = d.detect_disease_markers({"CEA": 1.5, "HbA1c": 5.0})
        assert isinstance(result, dict)

    def test_pro_detect_markers_has_keys(self):
        d = NanotechDiseaseDetector(Tier.PRO)
        result = d.detect_disease_markers({"CEA": 1.5})
        for key in ("analysis_type", "flagged_diseases", "recommendation"):
            assert key in result

    def test_pro_detect_abnormal_marker(self):
        d = NanotechDiseaseDetector(Tier.PRO)
        result = d.detect_disease_markers({"CEA": 10.0})
        assert "cancer" in result["flagged_diseases"]

    def test_pro_detect_normal_markers(self):
        d = NanotechDiseaseDetector(Tier.PRO)
        result = d.detect_disease_markers({"CEA": 1.5, "HbA1c": 5.0})
        assert result["flagged_diseases"] == []

    def test_enterprise_detect_has_nanotech_confidence(self):
        d = NanotechDiseaseDetector(Tier.ENTERPRISE)
        result = d.detect_disease_markers({"CEA": 1.5})
        assert result.get("nanotech_confidence") == 0.97

    def test_pro_dna_analysis_raises(self):
        d = NanotechDiseaseDetector(Tier.PRO)
        with pytest.raises(NanotechDiseaseDetectorError):
            d.analyze_dna_sequence({"variants": ["BRCA1"], "patient_id": "p1"})

    def test_enterprise_dna_analysis_returns_dict(self):
        d = NanotechDiseaseDetector(Tier.ENTERPRISE)
        result = d.analyze_dna_sequence({"variants": ["BRCA1", "MTHFR"], "patient_id": "p1"})
        assert isinstance(result, dict)

    def test_enterprise_dna_has_risk_profile(self):
        d = NanotechDiseaseDetector(Tier.ENTERPRISE)
        result = d.analyze_dna_sequence({"variants": ["BRCA1"], "patient_id": "p1"})
        assert "risk_profile" in result
        assert "BRCA1" in result["risk_profile"]

    def test_enterprise_dna_high_risk_variant(self):
        d = NanotechDiseaseDetector(Tier.ENTERPRISE)
        result = d.analyze_dna_sequence({"variants": ["TP53"], "patient_id": "p1"})
        assert "TP53" in result["high_risk_variants"]

    def test_recommend_treatment_free_raises(self):
        d = NanotechDiseaseDetector(Tier.FREE)
        with pytest.raises(NanotechDiseaseDetectorError):
            d.recommend_treatment({"patient_id": "p1"}, "diabetes")

    def test_recommend_treatment_pro(self):
        d = NanotechDiseaseDetector(Tier.PRO)
        result = d.recommend_treatment({"patient_id": "p1", "age": 45}, "diabetes")
        assert isinstance(result, dict)
        assert "recommended_treatments" in result

    def test_recommend_treatment_enterprise_personalized(self):
        d = NanotechDiseaseDetector(Tier.ENTERPRISE)
        result = d.recommend_treatment({"patient_id": "p1", "age": 70, "conditions": ["hypertension"]}, "cardiovascular")
        assert result.get("personalized") is True
        assert result.get("genomic_adjusted") is True


# ===========================================================================
# PrecisionMedicineEngine
# ===========================================================================

class TestPrecisionMedicineEngine:
    def _sample_patient(self, patient_id="pt1"):
        return {
            "patient_id": patient_id,
            "age": 45,
            "sex": "male",
            "weight_kg": 80,
            "height_cm": 175,
            "conditions": ["hypertension"],
            "medications": ["lisinopril"],
            "allergies": [],
        }

    def test_free_tier_profile_raises(self):
        eng = PrecisionMedicineEngine(Tier.FREE)
        with pytest.raises(PrecisionMedicineError):
            eng.create_patient_profile(self._sample_patient())

    def test_pro_create_profile_returns_dict(self):
        eng = PrecisionMedicineEngine(Tier.PRO)
        result = eng.create_patient_profile(self._sample_patient())
        assert isinstance(result, dict)

    def test_pro_profile_has_required_keys(self):
        eng = PrecisionMedicineEngine(Tier.PRO)
        result = eng.create_patient_profile(self._sample_patient())
        for key in ("patient_id", "age", "conditions", "current_medications"):
            assert key in result

    def test_pro_profile_has_bmi(self):
        eng = PrecisionMedicineEngine(Tier.PRO)
        result = eng.create_patient_profile(self._sample_patient())
        assert result["bmi"] is not None

    def test_enterprise_profile_has_genomics(self):
        eng = PrecisionMedicineEngine(Tier.ENTERPRISE)
        data = self._sample_patient()
        data["variants"] = ["BRCA1"]
        result = eng.create_patient_profile(data)
        assert result.get("pharmacogenomics_enabled") is True

    def test_pro_drug_efficacy_returns_dict(self):
        eng = PrecisionMedicineEngine(Tier.PRO)
        eng.create_patient_profile(self._sample_patient())
        profile = eng._profiles["pt1"]
        result = eng.calculate_drug_efficacy("metformin", profile)
        assert isinstance(result, dict)

    def test_pro_drug_efficacy_has_keys(self):
        eng = PrecisionMedicineEngine(Tier.PRO)
        eng.create_patient_profile(self._sample_patient())
        profile = eng._profiles["pt1"]
        result = eng.calculate_drug_efficacy("aspirin", profile)
        for key in ("drug", "base_efficacy", "recommendation"):
            assert key in result

    def test_enterprise_drug_efficacy_genomic_adjusted(self):
        eng = PrecisionMedicineEngine(Tier.ENTERPRISE)
        data = self._sample_patient()
        data["variants"] = ["MTHFR"]
        eng.create_patient_profile(data)
        profile = eng._profiles["pt1"]
        result = eng.calculate_drug_efficacy("metformin", profile)
        assert result.get("pharmacogenomics_applied") is True
        # MTHFR reduces metformin efficacy
        assert result["adjusted_efficacy"] < result["base_efficacy"]

    def test_free_tier_treatment_plan_raises(self):
        eng = PrecisionMedicineEngine(Tier.FREE)
        with pytest.raises(PrecisionMedicineError):
            eng.generate_treatment_plan("pt1", "diabetes")

    def test_pro_treatment_plan_raises(self):
        eng = PrecisionMedicineEngine(Tier.PRO)
        with pytest.raises(PrecisionMedicineError):
            eng.generate_treatment_plan("pt1", "diabetes")

    def test_enterprise_treatment_plan_returns_dict(self):
        eng = PrecisionMedicineEngine(Tier.ENTERPRISE)
        eng.create_patient_profile(self._sample_patient())
        result = eng.generate_treatment_plan("pt1", "diabetes")
        assert isinstance(result, dict)

    def test_enterprise_treatment_plan_has_keys(self):
        eng = PrecisionMedicineEngine(Tier.ENTERPRISE)
        eng.create_patient_profile(self._sample_patient())
        result = eng.generate_treatment_plan("pt1", "diabetes")
        for key in ("patient_id", "condition", "treatment_plan", "personalized"):
            assert key in result

    def test_enterprise_treatment_plan_personalized(self):
        eng = PrecisionMedicineEngine(Tier.ENTERPRISE)
        eng.create_patient_profile(self._sample_patient())
        result = eng.generate_treatment_plan("pt1", "cardiovascular")
        assert result["personalized"] is True

    def test_free_drug_efficacy_raises(self):
        eng = PrecisionMedicineEngine(Tier.FREE)
        with pytest.raises(PrecisionMedicineError):
            eng.calculate_drug_efficacy("aspirin", {})


# ===========================================================================
# BiomedicalBot — all tiers
# ===========================================================================

class TestBiomedicalBotFree:
    def test_init_default_tier(self):
        bot = BiomedicalBot()
        assert bot.tier == Tier.FREE

    def test_monitor_patient_heart_rate(self):
        bot = BiomedicalBot(Tier.FREE)
        result = bot.monitor_patient("p1", {"heart_rate": [70, 75, 72]})
        assert "monitoring_results" in result

    def test_monitor_patient_raises_on_second_patient(self):
        bot = BiomedicalBot(Tier.FREE)
        bot.monitor_patient("p1", {"heart_rate": [70]})
        with pytest.raises(BiomedicalBotError):
            bot.monitor_patient("p2", {"heart_rate": [80]})

    def test_detect_disease_raises_on_free(self):
        bot = BiomedicalBot(Tier.FREE)
        with pytest.raises(BiomedicalBotError):
            bot.detect_disease({"CEA": 5.0})

    def test_get_treatment_plan_raises_on_free(self):
        bot = BiomedicalBot(Tier.FREE)
        with pytest.raises(BiomedicalBotError):
            bot.get_treatment_plan("p1", "diabetes")

    def test_generate_patient_report(self):
        bot = BiomedicalBot(Tier.FREE)
        bot.monitor_patient("p1", {"heart_rate": [72, 75]})
        report = bot.generate_patient_report("p1")
        assert "patient_id" in report

    def test_dashboard_has_bot_name(self):
        bot = BiomedicalBot(Tier.FREE)
        dashboard = bot.get_medical_dashboard()
        assert dashboard["bot"] == "BiomedicalBot"

    def test_dashboard_upgrade_available(self):
        bot = BiomedicalBot(Tier.FREE)
        dashboard = bot.get_medical_dashboard()
        assert dashboard["upgrade_available"] is True


class TestBiomedicalBotPro:
    def test_pro_detect_disease(self):
        bot = BiomedicalBot(Tier.PRO)
        result = bot.detect_disease({"CEA": 1.5, "HbA1c": 5.0})
        assert isinstance(result, dict)

    def test_pro_monitor_glucose(self):
        bot = BiomedicalBot(Tier.PRO)
        result = bot.monitor_patient("p1", {"glucose": [100, 110, 120]})
        assert "monitoring_results" in result

    def test_pro_allows_multiple_patients(self):
        bot = BiomedicalBot(Tier.PRO)
        for i in range(5):
            result = bot.monitor_patient(f"p{i}", {"heart_rate": [72]})
            assert result["patient_id"] == f"p{i}"

    def test_pro_dashboard_has_advanced_analytics(self):
        bot = BiomedicalBot(Tier.PRO)
        dashboard = bot.get_medical_dashboard()
        assert dashboard.get("advanced_analytics") is True

    def test_pro_treatment_plan_raises(self):
        bot = BiomedicalBot(Tier.PRO)
        with pytest.raises(BiomedicalBotError):
            bot.get_treatment_plan("p1", "cancer")


class TestBiomedicalBotEnterprise:
    def test_enterprise_detect_dna(self):
        bot = BiomedicalBot(Tier.ENTERPRISE)
        result = bot.detect_disease({"variants": ["BRCA1", "MTHFR"], "patient_id": "p1"})
        assert "risk_profile" in result

    def test_enterprise_treatment_plan(self):
        bot = BiomedicalBot(Tier.ENTERPRISE)
        # Must have a patient profile first via the medicine engine
        bot.medicine.create_patient_profile({"patient_id": "p1", "age": 40, "weight_kg": 70, "height_cm": 170})
        result = bot.get_treatment_plan("p1", "diabetes")
        assert result["personalized"] is True

    def test_enterprise_dashboard_has_ml(self):
        bot = BiomedicalBot(Tier.ENTERPRISE)
        dashboard = bot.get_medical_dashboard()
        assert dashboard.get("ml_predictions") is True
        assert dashboard.get("nanotech_detection") is True

    def test_enterprise_dashboard_no_upgrade(self):
        bot = BiomedicalBot(Tier.ENTERPRISE)
        dashboard = bot.get_medical_dashboard()
        assert dashboard["upgrade_available"] is False

    def test_enterprise_activity_log(self):
        bot = BiomedicalBot(Tier.ENTERPRISE)
        bot.monitor_patient("p1", {"heart_rate": [72]})
        bot.detect_disease({"CEA": 1.5})
        assert bot._activity_log[0]["action"] == "monitor_patient"
        assert bot._activity_log[1]["action"] == "detect_disease"


# ===========================================================================
# Dashboard
# ===========================================================================

class TestMedicalDashboard:
    def test_dashboard_returns_dict(self):
        bot = BiomedicalBot(Tier.FREE)
        assert isinstance(bot.get_medical_dashboard(), dict)

    def test_dashboard_has_features(self):
        for tier in Tier:
            bot = BiomedicalBot(tier)
            dashboard = bot.get_medical_dashboard()
            assert "features" in dashboard
            assert len(dashboard["features"]) > 0

    def test_dashboard_price(self):
        assert BiomedicalBot(Tier.FREE).get_medical_dashboard()["price_usd_monthly"] == 0.0
        assert BiomedicalBot(Tier.PRO).get_medical_dashboard()["price_usd_monthly"] == 49.0
        assert BiomedicalBot(Tier.ENTERPRISE).get_medical_dashboard()["price_usd_monthly"] == 299.0

    def test_describe_tier_returns_string(self):
        bot = BiomedicalBot(Tier.FREE)
        desc = bot.describe_tier()
        assert isinstance(desc, str)
        assert "Free" in desc
