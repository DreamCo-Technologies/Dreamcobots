"""Ontology core package for adapter-first DreamCo migration."""

from ontology.components.catalog import ONTOLOGY_COMPONENT_BOTS, OntologyComponentBotSpec
from ontology.registry.object_registry import ObjectRegistry, OntologyObjectContract
from ontology.registry.relationship_registry import RelationshipRegistry

__all__ = [
    "ONTOLOGY_COMPONENT_BOTS",
    "ObjectRegistry",
    "OntologyComponentBotSpec",
    "OntologyObjectContract",
    "RelationshipRegistry",
]
