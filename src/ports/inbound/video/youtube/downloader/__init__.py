from abc import ABC, abstractmethod
from typing import Any, Callable

from src.domain.entity.error.video import (
    DownloadingYouTubeVideoError,
)
from src.domain.entity.video.youtube import DownloadedYouTubeVideo
from src.domain.entity.video.download_status import (
    OnCompleteDownloadingVideoStatus,
    OnProgressDownloadingVideoStatus,
)


class YouTubeVideoDownloaderInterface(ABC):
    @abstractmethod
    def __init__(self) -> None:
        raise Exception("This should be implemented from an adapter !")

    @abstractmethod
    def download_from_url(
        self,
        *,
        url: str,
        resolution: int = 1080,
        download_path: str,
        cookies_file_path: str | None = None,
        initial_tags: list[str] = [],
        on_progress_callback: Callable[[OnProgressDownloadingVideoStatus], Any],
        on_complete_callback: Callable[[OnCompleteDownloadingVideoStatus], Any],
    ) -> DownloadingYouTubeVideoError | DownloadedYouTubeVideo:
        """Downloading a video to a directory from a url

        Args:
            url (str): The url of the video you want to download
            resolution (int, optional): The resolution that the video will be downloaded into. Defaults to 1080.
            download_path (str): The base dir path that the video will be downloaded into
            initial_tags (list[str]): The initial tags that the video will be having
            cookies_file_path (str, optional): The cookies file that will be used for the download flow mimicking a real user login.
                Defaults to None.
            on_progress_callback (Callable[[OnProgressDownloadingVideoStatus], Any]):
                Callback to be used when any updates happens to the download progress
            on_complete_callback (Callable[[OnCompleteDownloadingVideoStatus], Any]):
                Callback to be used when any updates happens to the download complete

        Returns:
            DownloadingYouTubeVideoError | DownloadedYouTubeVideo: Either Error entity or a Success entity
        """
        raise Exception("This should be implemented from an adapter !")
