from datetime import datetime
from typing import Any
from yt_dlp import YoutubeDL
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
        with YoutubeDL(ydl_opts) as yt:
            try:
                youtube_video_info = yt.extract_info(url=url, download=False)
                assert youtube_video_info is not None
                return self.__get_video_info_from_dict(entry=youtube_video_info)
            except Exception as ex:
                return GettingYouTubeVideoInfoError(error=str(ex))

    def get_latest_video_from_channel(
        self, *, channel_name: str, videos_limit: int = 3
    ) -> GettingYouTubeVideosFromChannelNameError | list[YouTubeVideoInfo]:
        channel_url = f"https://www.youtube.com/c/{channel_name}/videos"
        ydl_opts = {"quiet": True, "extract_flat": False, "playlistend": videos_limit}

        with YoutubeDL(ydl_opts) as ydl:
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
