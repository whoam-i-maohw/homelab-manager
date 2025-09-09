from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class DownloadedYouTubeVideo:
    url: str
    resolution: int
    download_path: str
    downloaded_file: str
    title: str
    height: int
    width: int
    duration: str
    published_date_str: str
    average_rating: float
    thumbnail: str | None
    tags: list[str]
    channel_id: str
    channel_name: str
    channel_url: str


@dataclass(frozen=True, slots=True, kw_only=True)
class YouTubeVideoInfo:
    url: str
    title: str
    duration: str
    published_date_str: str
    average_rating: float
    thumbnail: str | None
    tags: list[str]
    channel_id: str
    channel_name: str
    channel_url: str


@dataclass(frozen=True, slots=True, kw_only=True)
class RepositoryYouTubeVideo:
    uuid: str
    created_at: str
    video: DownloadedYouTubeVideo
