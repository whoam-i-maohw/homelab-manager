from datetime import datetime
import os
from tempfile import gettempdir
from typing import Any
from yt_dlp import YoutubeDL
from src.domain.entity.error.video import GettingYouTubeVideoSubtitleError
from src.domain.entity.video.youtube import YouTubeVideoSubtitle
from src.domain.entity.error.video import (
    GettingYouTubeVideoInfoError,
    GettingYouTubeVideosFromChannelNameError,
)
from src.domain.entity.video.youtube import YouTubeVideoInfo
from src.ports.inbound.video.youtube.fetcher import YouTubeVideoFetcherInterface


class YtDlpYouTubeVideoFetcher(YouTubeVideoFetcherInterface):
    def __init__(self) -> None:
        pass

    def __get_video_info_from_dict(self, *, entry: dict[str, Any]) -> YouTubeVideoInfo:
        published_timestamp: float = float(
            entry.get("timestamp", datetime.now().timestamp())
        )
        published_date: datetime = datetime.fromtimestamp(published_timestamp)
        fetched_video_average_rating = entry.get("average_rating", 0.0)

        return YouTubeVideoInfo(
            url=f"https://www.youtube.com/watch?v={entry.get('id')}",
            title=entry.get("fulltitle", "NA"),
            duration=entry.get("duration_string", "NA"),
            published_date_str=published_date.isoformat(),
            average_rating=(
                fetched_video_average_rating
                if fetched_video_average_rating is not None
                else 0.0
            ),
            thumbnail=entry.get("thumbnail", "NA"),
            tags=entry.get("tags", []),
            channel_id=entry.get("channel_id", "NA"),
            channel_name=entry.get("channel", "NA"),
            channel_url=entry.get("channel_url", "NA"),
        )

    def get_video_info_from_url(
        self, *, url: str
    ) -> GettingYouTubeVideoInfoError | YouTubeVideoInfo:
        ydl_opts = {"quiet": True, "extract_flat": False}
        with YoutubeDL(ydl_opts) as yt:  # type: ignore
            try:
                youtube_video_info = yt.extract_info(url=url, download=False)
                assert youtube_video_info is not None
                return self.__get_video_info_from_dict(entry=youtube_video_info)  # type: ignore
            except Exception as ex:
                return GettingYouTubeVideoInfoError(error=str(ex))

    def get_latest_video_from_channel(
        self, *, channel_name: str, videos_limit: int = 3
    ) -> GettingYouTubeVideosFromChannelNameError | list[YouTubeVideoInfo]:
        channel_url = f"https://www.youtube.com/c/{channel_name}/videos"
        ydl_opts = {"quiet": True, "extract_flat": False, "playlistend": videos_limit}

        with YoutubeDL(ydl_opts) as ydl:  # type: ignore
            try:
                youtube_video_info = ydl.extract_info(url=channel_url, download=False)
                assert youtube_video_info is not None
                return [
                    self.__get_video_info_from_dict(entry=youtube_video_info)
                    for youtube_video_info in youtube_video_info.get("entries", [])
                ]
            except Exception as ex:
                return GettingYouTubeVideosFromChannelNameError(
                    error=str(ex), channel_name=channel_name
                )

    def get_subtitle_for_video_from_url(
        self, *, video_url: str, download_path: str = gettempdir(), language: str = "en"
    ) -> GettingYouTubeVideoSubtitleError | YouTubeVideoSubtitle:
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": [language],
            "subtitlesformat": "srt",
            "paths": dict(home=download_path),
            "outtmpl": "%(id)s.%(ext)s",
        }
        with YoutubeDL(ydl_opts) as ydl:  # type: ignore
            try:
                youtube_video_info = ydl.extract_info(url=video_url, download=True)
                assert youtube_video_info is not None
                subtitle_file_path = os.path.join(
                    download_path,
                    f"{youtube_video_info.get("id", "NA")}.{language}.srt",
                )

                subtitle_txt: str = ""
                with open(subtitle_file_path, "r") as subtitle_file:
                    subtitle_txt = subtitle_file.read().strip()

                os.remove(subtitle_file_path)
                return YouTubeVideoSubtitle(
                    video_url=video_url, subtitle_txt=subtitle_txt, language=language
                )
            except Exception as ex:
                return GettingYouTubeVideoSubtitleError(
                    error=str(ex), video_url=video_url
                )
