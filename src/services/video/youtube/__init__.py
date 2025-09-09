import os
from typing import Any, Callable
from src.ports.inbound.video.youtube.fetcher import YouTubeVideoFetcherInterface
from src.ports.inbound.video.youtube.downloader import YouTubeVideoDownloaderInterface
from src.domain.entity.error.video import (
    DownloadingYouTubeVideoError,
    GettingYouTubeVideoError,
    GettingYouTubeVideoInfoError,
    GettingYouTubeVideosFromChannelNameError,
    SavingYouTubeVideoError,
)
from src.domain.entity.video.youtube import (
    DownloadedYouTubeVideo,
    RepositoryYouTubeVideo,
    YouTubeVideoInfo,
)
from src.domain.entity.video.download_status import (
    OnCompleteDownloadingVideoStatus,
    OnProgressDownloadingVideoStatus,
)
import time
from concurrent.futures import ThreadPoolExecutor
from src.ports.outbound.video.youtube.repository import YouTubeVideoRepositoryInterface


class YouTubeVideoService:
    def __init__(
        self,
        *,
        youtube_video_downloader: YouTubeVideoDownloaderInterface,
        youtube_video_fetcher: YouTubeVideoFetcherInterface,
        youtube_video_repository: YouTubeVideoRepositoryInterface,
    ) -> None:
        self.__youtube_video_downloader = youtube_video_downloader
        self.__youtube_video_fetcher = youtube_video_fetcher
        self.__youtube_video_repository = youtube_video_repository

    # TODO make each function logic in a separate file for better handling of this source file 😁

    def get_youtube_video_info_for_url(
        self, *, url: str
    ) -> GettingYouTubeVideoInfoError | YouTubeVideoInfo:
        return self.__youtube_video_fetcher.get_video_info_from_url(url=url)

    def get_latest_video_from_channel(
        self, *, channel_name: str, videos_limit: int = 3
    ) -> GettingYouTubeVideosFromChannelNameError | list[YouTubeVideoInfo]:
        return self.__youtube_video_fetcher.get_latest_video_from_channel(
            channel_name=channel_name, videos_limit=videos_limit
        )

    def download_youtube_video_from_url_to_channel_name_dir(
        self,
        *,
        url: str,
        resolution: int = 1080,
        download_root_path: str,
        initial_tags: list[str] = [],
        retry_attempts: int = 3,
        retry_timeout: int = 3,
        dir_name_mappings: dict[str, str] = {
            "": "unknown",
            "ا": "ا",
            "أ": "ا",
        },
        cookies_file_path: str | None = None,
        on_progress_callback: Callable[[OnProgressDownloadingVideoStatus], Any],
        on_complete_callback: Callable[[OnCompleteDownloadingVideoStatus], Any],
    ) -> DownloadingYouTubeVideoError | DownloadedYouTubeVideo:
        """Downloading a youtube video from a url in a directory of the channel name of the video,
        for example if the video is coming from a channel with name (test), the video will
        be downloaded in this path ({download_root_path}/t/test/)
        """
        if not os.path.exists(download_root_path):
            return DownloadingYouTubeVideoError(
                error=f"This download path [{download_root_path}] doesn't exist !",
                url=url,
                download_path=download_root_path,
                resolution=resolution,
            )

        getting_video_info_status: GettingYouTubeVideoInfoError | YouTubeVideoInfo = (
            self.get_youtube_video_info_for_url(url=url)
        )
        if isinstance(getting_video_info_status, GettingYouTubeVideoInfoError):
            return DownloadingYouTubeVideoError(
                error=getting_video_info_status.error,
                url=url,
                resolution=resolution,
                download_path=download_root_path,
            )
        else:
            current_index: int = 0
            base_dir_name: str = ""
            channel_name = getting_video_info_status.channel_name
            while channel_name[current_index] != "":
                if channel_name[current_index].isalpha():
                    base_dir_name = channel_name[0]
                    try:
                        os.makedirs(
                            os.path.join(
                                download_root_path,
                                base_dir_name.lower(),
                                channel_name,
                            ),
                            exist_ok=True,
                        )
                        break
                    except Exception:
                        return DownloadingYouTubeVideoError(
                            error=f"Couldn't create directory [{base_dir_name}]"
                            + " for videos from this channel [{channel_name}] !",
                            url=url,
                            download_path=download_root_path,
                            resolution=resolution,
                        )
                else:
                    channel_name = channel_name[current_index + 1 :]

            new_download_path: str = os.path.join(
                download_root_path,
                dir_name_mappings.get(base_dir_name.lower(), base_dir_name.lower()),
                channel_name,
            )

            return self.download_youtube_video_from_url(
                url=url,
                resolution=resolution,
                download_path=new_download_path,
                initial_tags=initial_tags,
                retry_attempts=retry_attempts,
                retry_timeout=retry_timeout,
                cookies_file_path=cookies_file_path,
                on_progress_callback=on_progress_callback,
                on_complete_callback=on_complete_callback,
            )

    def download_youtube_video_from_url(
        self,
        *,
        url: str,
        resolution: int = 1080,
        download_path: str,
        initial_tags: list[str] = [],
        cookies_file_path: str | None = None,
        retry_attempts: int = 3,
        retry_timeout: int = 3,
        on_progress_callback: Callable[[OnProgressDownloadingVideoStatus], Any],
        on_complete_callback: Callable[[OnCompleteDownloadingVideoStatus], Any],
    ) -> DownloadingYouTubeVideoError | DownloadedYouTubeVideo:
        if not os.path.exists(download_path):
            return DownloadingYouTubeVideoError(
                error=f"This download path [{download_path}] doesn't exist !",
                url=url,
                download_path=download_path,
                resolution=resolution,
            )

        download_status = self.__youtube_video_downloader.download_from_url(
            url=url,
            download_path=download_path,
            initial_tags=initial_tags,
            resolution=resolution,
            cookies_file_path=cookies_file_path,
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
                        cookies_file_path=cookies_file_path,
                        on_progress_callback=on_progress_callback,
                        on_complete_callback=on_complete_callback,
                        retry_attempts=retry_attempts - 1,
                        retry_timeout=retry_timeout,
                    )
            case DownloadedYouTubeVideo() as downloaded_video:
                return downloaded_video

    def download_youtube_videos_from_txt_file_to_channel_name_dir(
        self,
        *,
        urls_txt_file_path: str,
        resolution: int = 1080,
        download_root_path: str,
        initial_tags: list[str] = [],
        cookies_file_path: str | None = None,
        retry_attempts: int = 3,
        retry_timeout: int = 3,
        concurrency: int = 3,
        on_progress_callback: Callable[[OnProgressDownloadingVideoStatus], Any],
        on_complete_callback: Callable[[OnCompleteDownloadingVideoStatus], Any],
    ) -> tuple[list[DownloadingYouTubeVideoError], list[DownloadedYouTubeVideo]]:
        if not os.path.exists(urls_txt_file_path):
            return [
                DownloadingYouTubeVideoError(
                    error=f"This urls txt file path [{urls_txt_file_path}] doesn't exist !",
                    download_path=download_root_path,
                    resolution=resolution,
                    url=urls_txt_file_path,
                )
            ], []

        with open(urls_txt_file_path, "r") as urls_txt_file:
            urls = urls_txt_file.readlines()

        def __process_wrapper(
            url: str,
        ) -> DownloadingYouTubeVideoError | DownloadedYouTubeVideo:
            return self.download_youtube_video_from_url_to_channel_name_dir(
                url=url.strip(),
                resolution=resolution,
                download_root_path=download_root_path,
                initial_tags=initial_tags,
                cookies_file_path=cookies_file_path,
                retry_attempts=retry_attempts,
                retry_timeout=retry_timeout,
                on_progress_callback=on_progress_callback,
                on_complete_callback=on_complete_callback,
            )

        with ThreadPoolExecutor(max_workers=concurrency) as execution_pool:
            results = list(execution_pool.map(__process_wrapper, urls))

            errors = [
                result
                for result in results
                if isinstance(result, DownloadingYouTubeVideoError)
            ]
            successes = [
                result
                for result in results
                if isinstance(result, DownloadedYouTubeVideo)
            ]

            return errors, successes

    def download_youtube_videos_from_txt_file(
        self,
        *,
        urls_txt_file_path: str,
        resolution: int = 1080,
        download_path: str,
        initial_tags: list[str] = [],
        cookies_file_path: str | None = None,
        retry_attempts: int = 3,
        retry_timeout: int = 3,
        concurrency: int = 3,
        on_progress_callback: Callable[[OnProgressDownloadingVideoStatus], Any],
        on_complete_callback: Callable[[OnCompleteDownloadingVideoStatus], Any],
    ) -> tuple[list[DownloadingYouTubeVideoError], list[DownloadedYouTubeVideo]]:
        if not os.path.exists(urls_txt_file_path):
            return [
                DownloadingYouTubeVideoError(
                    error=f"This urls txt file path [{urls_txt_file_path}] doesn't exist !",
                    download_path=download_path,
                    resolution=resolution,
                    url=urls_txt_file_path,
                )
            ], []

        with open(urls_txt_file_path, "r") as urls_txt_file:
            urls = urls_txt_file.readlines()

        def __process_wrapper(
            url: str,
        ) -> DownloadingYouTubeVideoError | DownloadedYouTubeVideo:
            return self.download_youtube_video_from_url(
                url=url.strip(),
                resolution=resolution,
                download_path=download_path,
                initial_tags=initial_tags,
                cookies_file_path=cookies_file_path,
                retry_attempts=retry_attempts,
                retry_timeout=retry_timeout,
                on_progress_callback=on_progress_callback,
                on_complete_callback=on_complete_callback,
            )

        with ThreadPoolExecutor(max_workers=concurrency) as execution_pool:
            results = list(execution_pool.map(__process_wrapper, urls))

            errors = [
                result
                for result in results
                if isinstance(result, DownloadingYouTubeVideoError)
            ]
            successes = [
                result
                for result in results
                if isinstance(result, DownloadedYouTubeVideo)
            ]

            return errors, successes

    def save_youtube_video(
        self, *, video: DownloadedYouTubeVideo
    ) -> SavingYouTubeVideoError | RepositoryYouTubeVideo:
        return self.__youtube_video_repository.save_video(video=video)

    def get_youtube_video_by_uuid(
        self, *, uuid: str
    ) -> GettingYouTubeVideoError | RepositoryYouTubeVideo:
        return self.__youtube_video_repository.get_video_by_uuid(uuid=uuid)

    def get_youtube_video_by_url(
        self, *, url: str
    ) -> GettingYouTubeVideoError | RepositoryYouTubeVideo:
        return self.__youtube_video_repository.get_video_by_url(url=url)

    def get_youtube_video_by_video_title(
        self, *, video_title: str
    ) -> GettingYouTubeVideoError | RepositoryYouTubeVideo:
        return self.__youtube_video_repository.get_video_by_video_title(
            video_title=video_title
        )

    def get_youtube_videos_by_channel_name(
        self, *, channel_name: str
    ) -> GettingYouTubeVideoError | list[RepositoryYouTubeVideo]:
        return self.__youtube_video_repository.get_videos_by_channel_name(
            channel_name=channel_name
        )
