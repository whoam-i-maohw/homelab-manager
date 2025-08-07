import os
import shutil
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

    def download_youtube_video_from_url_to_channel_name_dir(
        self,
        *,
        url: str,
        resolution: int = 1080,
        download_root_path: str,
        retry_attempts: int = 3,
        retry_timeout: int = 3,
        dir_name_mappings: dict[str, str] = {
            "": "unknown",
            "ا": "ا",
            "أ": "ا",
        },
        on_progress_callback: Callable[[OnProgressDownloadingVideoStatus], Any],
        on_complete_callback: Callable[[OnCompleteDownloadingVideoStatus], Any],
    ) -> DownloadingYouTubeVideoError | DownloadedYouTubeVideo:
        """Downloading a youtube video from a url in a directory of the channel name of the video,
        for example if the video is coming from a channel with name (test), the video will
        be downloaded in this path ({download_root_path}/t/test/)
        """
        download_status = self.download_youtube_video_from_url(
            url=url,
            resolution=resolution,
            download_path=download_root_path,
            retry_attempts=retry_attempts,
            retry_timeout=retry_timeout,
            on_progress_callback=on_progress_callback,
            on_complete_callback=on_complete_callback,
        )
        match download_status:
            case DownloadingYouTubeVideoError() as error:
                return error
            case DownloadedYouTubeVideo() as downloaded_video:
                current_index: int = 0
                base_dir_name: str = ""
                channel_name = downloaded_video.channel_name
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
                        except Exception:
                            return DownloadingYouTubeVideoError(
                                error=f"Couldn't create directory [{base_dir_name}]"
                                + " for videos from this channel [{channel_name}] !",
                                url=url,
                                download_path=download_root_path,
                                resolution=resolution,
                            )
                        break
                    else:
                        channel_name = channel_name[current_index + 1 :]

                download_path: str = os.path.join(
                    download_root_path,
                    dir_name_mappings.get(base_dir_name.lower(), base_dir_name.lower()),
                    channel_name,
                )

                try:
                    shutil.copy(
                        src=downloaded_video.downloaded_file,
                        dst=download_path,
                    )
                    os.remove(downloaded_video.downloaded_file)
                    return DownloadedYouTubeVideo(
                        url=downloaded_video.url,
                        title=downloaded_video.title,
                        resolution=resolution,
                        downloaded_file=os.path.join(
                            download_path,
                            os.path.basename(downloaded_video.downloaded_file),
                        ),
                        channel_name=downloaded_video.channel_name,
                        channel_id=downloaded_video.channel_id,
                        channel_url=downloaded_video.channel_url,
                        average_rating=downloaded_video.average_rating,
                        duration=downloaded_video.duration,
                        height=downloaded_video.height,
                        width=downloaded_video.width,
                        tags=downloaded_video.tags,
                        thumbnail=downloaded_video.thumbnail,
                        published_date_str=downloaded_video.published_date_str,
                        download_path=download_path,
                    )
                except Exception as ex:
                    return DownloadingYouTubeVideoError(
                        error=f"Couldn't move downloaded video to channel directory [{download_path}]"
                        + f" for reason [{str(ex)}] !",
                        url=url,
                        download_path=download_root_path,
                        resolution=resolution,
                    )

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
