from abc import ABC, abstractmethod
from tempfile import gettempdir

from src.domain.entity.error.video import (
    GettingYouTubeVideoInfoError,
    GettingYouTubeVideoSubtitleError,
    GettingYouTubeVideosFromChannelNameError,
)
from src.domain.entity.video.youtube import YouTubeVideoInfo, YouTubeVideoSubtitle


class YouTubeVideoFetcherInterface(ABC):
    @abstractmethod
    def __init__(self) -> None:
        raise Exception("This should be implemented from an adapter !")

    @abstractmethod
    def get_video_info_from_url(
        self, *, url: str
    ) -> GettingYouTubeVideoInfoError | YouTubeVideoInfo:
        """Getting YouTube video info from a url

        Args:
            url (str): The url of the video we want to get info about

        Returns:
            GettingYouTubeVideoInfoError | YouTubeVideoInfo: Either Error entity or a Success entity
        """
        raise Exception("This should be implemented from an adapter !")

    @abstractmethod
    def get_latest_video_from_channel(
        self, *, channel_name: str, videos_limit: int = 3
    ) -> GettingYouTubeVideosFromChannelNameError | list[YouTubeVideoInfo]:
        """Getting the latest youtube videos from a youtube-channel with channel name

        Args:
            channel_name (str): The youtube channel name that we want to fetch videos from
            videos_limit (int, optional): The limit of retrieved videos. Defaults to 3.

        Returns:
            GettingYouTubeVideosFromChannelNameError | list[YouTubeVideoInfo]: Either an error if fails or a list of video's information
        """
        raise Exception("This should be implemented from an adapter !")

    @abstractmethod
    def get_subtitle_for_video_from_url(
        self, *, video_url: str, download_path: str = gettempdir(), language: str = "en"
    ) -> GettingYouTubeVideoSubtitleError | YouTubeVideoSubtitle:
        """Getting the subtitle of a youtube video by url

        Args:
            video_url (str): The youtube video url that will be used
            download_path (str): The path of the download of the subtitle. Defaults to gettempdir()
            language (str, optional): The language of the subtitle that will be fetched. Defaults to "en".

        Returns:
            GettingYouTubeVideoSubtitleError | YouTubeVideoSubtitle: Either an error if fails or a the video's subtitle object
        """
        raise Exception("This should be implemented from an adapter !")
