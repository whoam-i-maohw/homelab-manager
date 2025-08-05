from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class DownloadingYouTubeVideoError:
    error: str
    url: str
    resolution: int
    download_path: str
