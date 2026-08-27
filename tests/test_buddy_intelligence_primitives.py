from buddy_os.intelligence.capability_composer import CapabilityComposer
from buddy_os.intelligence.dream_object import DreamObject
from buddy_os.intelligence.prediction_error import PredictionLedger
from buddy_os.intelligence.temporal_workflow import TemporalWorkflow, WorkflowTransition
from buddy_os.assets.digital_asset_registry import DigitalAsset


def test_dream_object_lifecycle_and_relationships():
    obj = DreamObject("goal:1", "goal")
    obj.relate("requires", "capability:1")
    obj.transition("planned")
    assert obj.state == "planned"
    assert obj.relationships["requires"] == ["capability:1"]


def test_temporal_workflow_requires_tokens():
    wf = TemporalWorkflow({"input"})
    wf.add_transition(WorkflowTransition("run", {"input"}, {"output"}))
    assert wf.available() == ["run"]
    assert wf.fire("run") == {"output"}


def test_prediction_error_is_measurable():
    ledger = PredictionLedger()
    ledger.record("p1", .8, .6)
    ledger.record("p2", .2, .3)
    assert ledger.mean_absolute_error() == .15


def test_capability_composition_preserves_unique_capabilities_and_dependencies():
    assets = [
        DigitalAsset("a", "A", "tool", capabilities=["extract"], dependencies=["db"]),
        DigitalAsset("b", "B", "tool", capabilities=["extract", "verify"], dependencies=["db", "api"]),
    ]
    composite = CapabilityComposer().compose("cap:1", "Extract+Verify", assets)
    assert composite.capabilities == ["extract", "verify"]
    assert composite.dependencies == ["db", "api"]
