from ontology.adapters.workflow_ontology_adapter import WorkflowOntologyAdapter
from ontology.components.catalog import ONTOLOGY_COMPONENT_BOTS, get_component_bot, list_component_bots
from ontology.registry.object_registry import ObjectRegistry, canonical_id
from ontology.registry.relationship_registry import RELATIONSHIP_TYPES, RelationshipRegistry


def test_catalog_has_100_unique_component_bots():
    names = [spec.name for spec in ONTOLOGY_COMPONENT_BOTS]
    assert len(names) == 100
    assert len(set(names)) == 100


def test_catalog_has_10_domains_with_10_components_each():
    domains = {spec.domain for spec in ONTOLOGY_COMPONENT_BOTS}
    assert len(domains) == 10
    for domain in domains:
        assert len(list_component_bots(domain)) == 10


def test_catalog_lookup_examples():
    assert get_component_bot("ObjectSchemaBot") is not None
    assert get_component_bot("OntologyStewardBot") is not None
    assert get_component_bot("DoesNotExistBot") is None


def test_object_registry_canonical_identity_and_state_transition():
    registry = ObjectRegistry()
    contract = registry.upsert(
        {
            "type": "Bot",
            "name": "Trade Titan 300",
            "division": "DreamFinance",
            "capabilities": ["market_analysis", "trade_execution"],
        }
    )
    assert contract.id == canonical_id("Bot", "Trade Titan 300")
    assert registry.transition_state(contract.id, "inactive").state == "inactive"
    assert registry.deprecate(contract.id).deprecated is True


def test_relationship_registry_allows_only_supported_types():
    registry = RelationshipRegistry()
    rel = registry.register("bot.trade_titan_300", "BELONGS_TO", "division.dream_finance")
    assert rel.type in RELATIONSHIP_TYPES
    assert registry.serialize()[0]["source"] == "bot.trade_titan_300"


def test_workflow_adapter_projects_legacy_payload():
    adapter = WorkflowOntologyAdapter()
    projected = adapter.project(
        {
            "id": "crypto_strategy",
            "name": "Crypto Strategy",
            "status": "active",
            "steps": ["analyze", "execute"],
            "bot": "bot.trade_titan_300",
        }
    )
    assert projected["id"] == "workflow.crypto_strategy"
    assert projected["type"] == "Workflow"
    assert projected["state"] == "active"
    assert projected["relationships"][0]["type"] == "EXECUTES"
