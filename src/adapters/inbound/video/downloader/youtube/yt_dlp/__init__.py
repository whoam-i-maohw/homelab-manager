from datetime import datetime
import os
from typing import Any, Callable
from yt_dlp import YoutubeDL
from src.domain.entity.error.video import DownloadingYouTubeVideoError
from src.domain.entity.video.download_status import (
    OnCompleteDownloadingVideoStatus,
    OnProgressDownloadingVideoStatus,
)
from src.domain.entity.video.youtube import DownloadedYouTubeVideo
from src.ports.inbound.video.downloader.youtube import YouTubeVideoDownloaderInterface


class YtDlpYouTubeVideoDownloader(YouTubeVideoDownloaderInterface):
    def __init__(self) -> None:
        pass

    def download_from_url(
        self,
        *,
        url: str,
        resolution: int = 1080,
        download_path: str,
        cookies_file_path: str | None = None,
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

        def __on_progress_hook(status_obj: dict[str, Any]) -> None:
            if status_obj.get("status", "NA") == "downloading":
                return on_progress_callback(
                    OnProgressDownloadingVideoStatus(
                        url=url,
                        title=status_obj.get("info_dict", {}).get("fulltitle", "NA"),
                        height=resolution,
                        width=status_obj.get("info_dict", {}).get("width", "NA"),
                        size_in_bytes=status_obj.get("total_bytes", "NA"),
                        downloaded_ratio=status_obj.get("_percent_str", "NA"),
                        download_speed_in_bytes=status_obj.get("_speed_str", "NA"),
                        download_eta_in_seconds=status_obj.get("_eta_str", "00:00"),
                    )
                )
            elif status_obj.get("status", "NA") == "finished":
                video_title = status_obj.get("info_dict", {}).get("fulltitle", "NA")
                return on_complete_callback(
                    OnCompleteDownloadingVideoStatus(
                        url=url,
                        title=video_title,
                        downloaded_file_dst=os.path.join(
                            download_path,
                            video_title + "." + status_obj.get("ext", "NA"),
                        ),
                    )
                )

        download_options: dict[str, Any] = dict(
            format=f"bv*[height<={resolution}]+ba",
            progress_hooks=[__on_progress_hook],
            postprocessor_hooks=[],
            paths=dict(home=download_path),
            outtmpl="%(title)s.%(ext)s",
            merge_output_format="mkv",
            noprogress=True,
            consoletitle=True,
            extractor_retries=0,
            extractor_args={"youtube": {"skip": ["authcheck"]}},
        )

        if cookies_file_path is not None:
            download_options.update(dict(cookiefile=cookies_file_path))

        with YoutubeDL(download_options) as yt:
            try:
                youtube_video_info = yt.extract_info(url=url, download=True)
                assert youtube_video_info is not None
                video_title: str = os.path.basename(
                    youtube_video_info.get("fulltitle", "NA")
                )
                published_timestamp: float = float(
                    youtube_video_info.get("timestamp", datetime.now().timestamp())
                )
                published_date: datetime = datetime.fromtimestamp(published_timestamp)
                fetched_video_average_rating = youtube_video_info.get(
                    "average_rating", 0.0
                )
                return DownloadedYouTubeVideo(
                    url=url,
                    title=video_title,
                    height=youtube_video_info.get("height", "NA"),
                    width=youtube_video_info.get("width", "NA"),
                    resolution=resolution,
                    download_path=download_path,
                    downloaded_file=os.path.join(
                        download_path,
                        video_title + "." + youtube_video_info.get("ext", "NA"),
                    ),
                    duration=youtube_video_info.get("duration_string", "NA"),
                    published_date_str=published_date.isoformat(),
                    channel_id=youtube_video_info.get("channel_id", "NA"),
                    channel_name=youtube_video_info.get("channel", "NA"),
                    channel_url=youtube_video_info.get("channel_url", "NA"),
                    tags=youtube_video_info.get("tags", []),
                    thumbnail=youtube_video_info.get("thumbnail", "NA"),
                    average_rating=(
                        fetched_video_average_rating
                        if fetched_video_average_rating is not None
                        else 0.0
                    ),
                )
            except Exception as ex:
                error_message: str = str(ex)

                if (
                    "Video unavailable" in str(ex)
                    or "is not a valid URL" in str(ex)
                    or "Unable to download" in str(ex)
                ):
                    error_message = f"This url [{url}] doesn't exist !"
                elif "Failed to extract any player response" in str(ex):
                    error_message = "There is no internet connectivity !"
                elif "Requested format is not available" in str(ex):
                    error_message = f"This video resolution [{resolution}P] is not available for this video !"

                return DownloadingYouTubeVideoError(
                    error=error_message,
                    download_path=download_path,
                    resolution=resolution,
                    url=url,
                )
