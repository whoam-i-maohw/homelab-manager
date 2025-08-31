from abc import ABC, abstractmethod
from src.domain.entity.error.video import (
    GettingYouTubeVideoError,
    SavingYouTubeVideoError,
)
from src.domain.entity.video.youtube import (
    DownloadedYouTubeVideo,
    RepositoryYouTubeVideo,
)


class YouTubeVideoRepositoryInterface(ABC):
    @abstractmethod
    def __init__(self) -> None:
        raise Exception("This should be implemented from an adapter !")

    @abstractmethod
    def save_video(
        self, *, video: DownloadedYouTubeVideo
    ) -> SavingYouTubeVideoError | RepositoryYouTubeVideo:
        raise Exception("This should be implemented from an adapter !")

    @abstractmethod
    def get_video_by_uuid(
        self, *, uuid: str
    ) -> GettingYouTubeVideoError | RepositoryYouTubeVideo:
        raise Exception("This should be implemented from an adapter !")

    @abstractmethod
    def get_video_by_url(
        self, *, url: str
    ) -> GettingYouTubeVideoError | RepositoryYouTubeVideo:
        raise Exception("This should be implemented from an adapter !")

    @abstractmethod
    def get_video_by_video_title(
        self, *, video_title: str
    ) -> GettingYouTubeVideoError | RepositoryYouTubeVideo:
        raise Exception("This should be implemented from an adapter !")

    @abstractmethod
    def get_videos_by_channel_name(
        self, *, channel_name: str
    ) -> GettingYouTubeVideoError | list[RepositoryYouTubeVideo]:
        raise Exception("This should be implemented from an adapter !")
