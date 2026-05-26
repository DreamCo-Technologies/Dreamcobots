"""Stigmergy layer: semantic pheromones + shared environment."""

from dreamco_platform.swarm.stigmergy.pheromone import SemanticPheromone
from dreamco_platform.swarm.stigmergy.environment import StigmergyEnvironment
from dreamco_platform.swarm.stigmergy.stigmergic_bot import ForagingRole, StigmergicBot

__all__ = ["SemanticPheromone", "StigmergyEnvironment", "ForagingRole", "StigmergicBot"]
