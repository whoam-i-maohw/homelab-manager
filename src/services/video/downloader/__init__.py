from src.ports.inbound.video.downloader.youtube import YouTubeVideoDownloaderInterface
from typing import Any, Callable
from src.domain.entity.error.video import DownloadingYouTubeVideoError
from src.domain.entity.video.youtube import DownloadedYouTubeVideo
from src.domain.entity.video.download_status import (
    OnCompleteDownloadingVideoStatus,
    OnProgressDownloadingVideoStatus,
)
import time


class VideoDownloaderService:
    def __init__(
        self, *, youtube_video_downloader: YouTubeVideoDownloaderInterface
    ) -> None:
        self.__youtube_video_downloader = youtube_video_downloader

    def download_youtube_video_from_url(
        self,
        *,
        url: str,
        resolution: int = 1080,
        download_path: str,
        retry_attempts: int = 3,
        retry_timeout: int = 3,
        on_progress_callback: Callable[[OnProgressDownloadingVideoStatus], Any],
        on_complete_callback: Callable[[OnCompleteDownloadingVideoStatus], Any],
    ) -> DownloadingYouTubeVideoError | DownloadedYouTubeVideo:
        download_status = self.__youtube_video_downloader.download_from_url(
            url=url,
            download_path=download_path,
            resolution=resolution,
            on_progress_callback=on_progress_callback,
            on_complete_callback=on_complete_callback,
        )
        match download_status:
            case DownloadingYouTubeVideoError() as error:
                if retry_attempts == 0:
                    return error
                else:
                    print(
                        f"Waiting for [{retry_timeout}] seconds"
                        + " before attempting to try downloading the video again,"
                        + f" Remaining attempts [{retry_attempts-1}]"
                    )
                    time.sleep(retry_timeout)
                    return self.download_youtube_video_from_url(
                        url=url,
                        resolution=resolution,
                        download_path=download_path,
                        on_progress_callback=on_progress_callback,
                        on_complete_callback=on_complete_callback,
                        retry_attempts=retry_attempts - 1,
                        retry_timeout=retry_timeout,
                    )
            case DownloadedYouTubeVideo() as downloaded_video:
                return downloaded_video
