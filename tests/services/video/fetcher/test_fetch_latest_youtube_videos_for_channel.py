import os
from tempfile import gettempdir
from unittest.mock import Mock, patch
from src.domain.entity.error.video import (
    GettingYouTubeVideosFromChannelNameError,
)
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
    "src.adapters.inbound.video.youtube.fetcher.yt_dlp.YtDlpYouTubeVideoFetcher.get_latest_video_from_channel",
    return_value=[
        YouTubeVideoInfo(
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
    ],
)
def test_fetching_latest_videos_for_channel(mock_socket: Mock) -> None:
    expected_videos_info = [
        YouTubeVideoInfo(
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
    ]
    youtube_video_repository = SqlitePonyYouTubeVideoRepository(
        database_path=os.path.join(gettempdir(), "test.db")
    )

    getting_videos_info_status = YouTubeVideoService(
        youtube_video_downloader=YtDlpYouTubeVideoDownloader(),
        youtube_video_fetcher=YtDlpYouTubeVideoFetcher(),
        youtube_video_repository=youtube_video_repository,
    ).get_latest_video_from_channel(
        channel_name=expected_videos_info[0].channel_name, videos_limit=1
    )

    assert isinstance(getting_videos_info_status, list)
    assert len(getting_videos_info_status) == 1
    assert getting_videos_info_status == expected_videos_info


@patch(
    "src.adapters.inbound.video.youtube.fetcher.yt_dlp.YtDlpYouTubeVideoFetcher.get_latest_video_from_channel",
    return_value=GettingYouTubeVideosFromChannelNameError(
        channel_name="test", error="error-fetching-videos"
    ),
)
def test_fetching_latest_videos_for_channel_error(mock_socket: Mock) -> None:
    expected_videos_info = GettingYouTubeVideosFromChannelNameError(
        channel_name="test", error="error-fetching-videos"
    )
    youtube_video_repository = SqlitePonyYouTubeVideoRepository(
        database_path=os.path.join(gettempdir(), "test.db")
    )

    getting_videos_info_status = YouTubeVideoService(
        youtube_video_downloader=YtDlpYouTubeVideoDownloader(),
        youtube_video_fetcher=YtDlpYouTubeVideoFetcher(),
        youtube_video_repository=youtube_video_repository,
    ).get_latest_video_from_channel(channel_name="any-channel-name", videos_limit=1)

    assert isinstance(
        getting_videos_info_status, GettingYouTubeVideosFromChannelNameError
    )
    assert getting_videos_info_status == expected_videos_info
