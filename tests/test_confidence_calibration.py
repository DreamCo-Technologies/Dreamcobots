import pytest

from buddy_os.intelligence.confidence_calibration import ConfidenceCalibrator, PredictionOutcome


def test_calibrator_tracks_accuracy_confidence_and_gap():
    calibrator = ConfidenceCalibrator()
    calibrator.record(PredictionOutcome("p1", .9, True))
    calibrator.record(PredictionOutcome("p2", .7, False))
    assert calibrator.sample_count() == 2
    assert calibrator.accuracy() == pytest.approx(.5)
    assert calibrator.mean_confidence() == pytest.approx(.8)
    assert calibrator.calibration_gap() == pytest.approx(.3)


def test_prediction_confidence_is_bounded():
    with pytest.raises(ValueError):
        PredictionOutcome("p", 1.1, True)
