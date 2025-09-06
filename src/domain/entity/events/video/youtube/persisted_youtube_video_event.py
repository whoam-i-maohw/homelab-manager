from dataclasses import dataclass

from src.domain.entity.events.generic import GenericEvent
from src.domain.entity.video.youtube import RepositoryYouTubeVideo


@dataclass(frozen=True, slots=True, kw_only=True)
class PersistedYouTubeVideoEvent(GenericEvent):
    persisted_video: RepositoryYouTubeVideo
