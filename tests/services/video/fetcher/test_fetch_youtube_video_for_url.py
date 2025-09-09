import os
from tempfile import gettempdir
from unittest.mock import Mock, patch
from src.domain.entity.error.video import GettingYouTubeVideoInfoError
from src.domain.entity.video.youtube import YouTubeVideoInfo
from src.services.video.youtube import YouTubeVideoService
from src.adapters.inbound.video.youtube.downloader.yt_dlp import (
    YtDlpYouTubeVideoDownloader,
)
from src.adapters.inbound.video.youtube.fetcher.yt_dlp import YtDlpYouTubeVideoFetcher
from src.adapters.outbound.video.youtube.repository.sqlite.pony_impl import (
    SqlitePonyYouTubeVideoRepository,
)

# TODO this tests mocks should be a little bit lower, instead of mocking the whole
# src.adapters.inbound.video.youtube.fetcher.yt_dlp.YtDlpYouTubeVideoFetcher.get_video_info_from_url
# we need to just mock YoutubeDL.extract_info to return the proper dict and see how the system will
# behave as a result 😁


@patch(
    "src.adapters.inbound.video.youtube.fetcher.yt_dlp.YtDlpYouTubeVideoFetcher.get_video_info_from_url",
    return_value=YouTubeVideoInfo(
        url="testing",
        average_rating=0.0,
        channel_id="",
        channel_name="testing_channel",
        channel_url="",
        duration="",
        published_date_str="",
        tags=[],
        thumbnail=None,
        title="",
    ),
)
def test_fetching_video_info_for_url(mock_socket: Mock) -> None:
    expected_video_info = YouTubeVideoInfo(
        url="testing",
        average_rating=0.0,
        channel_id="",
        channel_name="testing_channel",
        channel_url="",
        duration="",
        published_date_str="",
        tags=[],
        thumbnail=None,
        title="",
    )
    youtube_video_repository = SqlitePonyYouTubeVideoRepository(
        database_path=os.path.join(gettempdir(), "test.db")
    )

    getting_video_info_status = YouTubeVideoService(
        youtube_video_downloader=YtDlpYouTubeVideoDownloader(),
        youtube_video_fetcher=YtDlpYouTubeVideoFetcher(),
        youtube_video_repository=youtube_video_repository,
    ).get_youtube_video_info_for_url(url=expected_video_info.url)

    assert isinstance(getting_video_info_status, YouTubeVideoInfo)
    assert getting_video_info_status == expected_video_info


@patch(
    "src.adapters.inbound.video.youtube.fetcher.yt_dlp.YtDlpYouTubeVideoFetcher.get_video_info_from_url",
    return_value=GettingYouTubeVideoInfoError(
        error="no-video-found",
    ),
)
def test_error_fetching_video_info(mock_socket: Mock) -> None:
    expected_status = GettingYouTubeVideoInfoError(
        error="no-video-found",
    )
    youtube_video_repository = SqlitePonyYouTubeVideoRepository(
        database_path=os.path.join(gettempdir(), "test.db")
    )

    getting_video_info_status = YouTubeVideoService(
        youtube_video_downloader=YtDlpYouTubeVideoDownloader(),
        youtube_video_fetcher=YtDlpYouTubeVideoFetcher(),
        youtube_video_repository=youtube_video_repository,
    ).get_youtube_video_info_for_url(url="any-url")

    assert isinstance(getting_video_info_status, GettingYouTubeVideoInfoError)
    assert getting_video_info_status == expected_status
