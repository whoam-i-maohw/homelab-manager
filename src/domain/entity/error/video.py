from dataclasses import dataclass
from src.domain.entity.video.youtube import DownloadedYouTubeVideo


@dataclass(frozen=True, slots=True, kw_only=True)
class DownloadingYouTubeVideoError:
    error: str
    url: str
    resolution: int
    download_path: str


@dataclass(frozen=True, slots=True, kw_only=True)
class GettingYouTubeVideoInfoError:
    error: str


@dataclass(frozen=True, slots=True, kw_only=True)
class SavingYouTubeVideoError:
    error: str
    video: DownloadedYouTubeVideo


@dataclass(frozen=True, slots=True, kw_only=True)
class GettingYouTubeVideoError:
    error: str


@dataclass(frozen=True, slots=True, kw_only=True)
class GettingYouTubeVideosFromChannelNameError:
    error: str
    channel_name: str
