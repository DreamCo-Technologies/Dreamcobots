"""Buddy's governed game, simulation, and learning-media studio."""

from .studio import (
    BuddyCreativeStudio,
    ConsentEvidence,
    CreativeBrief,
    CreativeStudioError,
    MediaRenderer,
    ProjectType,
    StudioProject,
)
from .local_renderer import LocalCommandMediaRenderer, LocalRendererCommand
from .branding import BrandingError, BuddyLogoGenerator, LogoBrief
from .music import ArtistBrief, BuddyMusicArtistStudio, MusicStudioError, ReferenceTrack
from .production_group import (
    ActorMode,
    BuddyProductionGroup,
    ModelSource,
    ProductionBrief,
    ProductionFormat,
    SimulationBrief,
    SimulationDomain,
    SyntheticActorBrief,
)

__all__ = [
    "BuddyCreativeStudio",
    "ConsentEvidence",
    "CreativeBrief",
    "CreativeStudioError",
    "MediaRenderer",
    "ProjectType",
    "StudioProject",
    "LocalCommandMediaRenderer",
    "LocalRendererCommand",
    "ArtistBrief",
    "BrandingError",
    "BuddyLogoGenerator",
    "BuddyMusicArtistStudio",
    "LogoBrief",
    "MusicStudioError",
    "ReferenceTrack",
    "ActorMode",
    "BuddyProductionGroup",
    "ModelSource",
    "ProductionBrief",
    "ProductionFormat",
    "SimulationBrief",
    "SimulationDomain",
    "SyntheticActorBrief",
]
