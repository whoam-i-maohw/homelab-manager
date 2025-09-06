from dataclasses import dataclass

from src.domain.entity.events.generic import GenericEvent
from src.domain.entity.video.youtube import DownloadedYouTubeVideo


@dataclass(frozen=True, slots=True, kw_only=True)
class DownloadedYouTubeVideoEvent(GenericEvent):
    downloaded_video: DownloadedYouTubeVideo
