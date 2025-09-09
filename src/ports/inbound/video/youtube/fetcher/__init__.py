from abc import ABC, abstractmethod

from src.domain.entity.error.video import (
    GettingYouTubeVideoInfoError,
    GettingYouTubeVideosFromChannelNameError,
)
from src.domain.entity.video.youtube import YouTubeVideoInfo


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
