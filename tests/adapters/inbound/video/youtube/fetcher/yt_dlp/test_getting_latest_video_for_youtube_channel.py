import datetime
from unittest.mock import Mock, patch
from src.domain.entity.error.video import (
    GettingYouTubeVideosFromChannelNameError,
)
from src.domain.entity.video.youtube import YouTubeVideoInfo
from src.adapters.inbound.video.youtube.fetcher.yt_dlp import YtDlpYouTubeVideoFetcher


expected_time_timestamp = datetime.datetime.now().timestamp()


@patch(
    "src.adapters.inbound.video.youtube.downloader.yt_dlp.YoutubeDL.extract_info",
    return_value=dict(
        entries=[
            dict(
                id="testing_url",
                average_rating=0.0,
                channel_id="testing_channel_id",
                channel="testing_channel_name",
                channel_url="testing_channel_url",
                duration_string="1:0",
                timestamp=expected_time_timestamp,
                tags=[],
                thumbnail=None,
                fulltitle="testing_title",
            )
        ]
    ),
)
def test_fetching_latest_youtube_video_for_channel_by_name(_mock_socket: Mock) -> None:
    channel_name: str = "testing_channel_name"
    fetching_result: (
        GettingYouTubeVideosFromChannelNameError | list[YouTubeVideoInfo]
    ) = YtDlpYouTubeVideoFetcher().get_latest_video_from_channel(
        channel_name=channel_name, videos_limit=1
    )

    expected_videos = [
        YouTubeVideoInfo(
            url=f"https://www.youtube.com/watch?v=testing_url",
            average_rating=0.0,
            channel_id="testing_channel_id",
            channel_name="testing_channel_name",
            channel_url="testing_channel_url",
            duration="1:0",
            published_date_str=datetime.datetime.fromtimestamp(
                expected_time_timestamp
            ).isoformat(),
            tags=[],
            thumbnail=None,
            title="testing_title",
        )
    ]

    assert isinstance(fetching_result, list)
    assert len(fetching_result) == 1
    assert isinstance(fetching_result[0], YouTubeVideoInfo)
    assert fetching_result == expected_videos


@patch(
    "src.adapters.inbound.video.youtube.downloader.yt_dlp.YoutubeDL.extract_info",
    side_effect=Exception("Error fetching latest videos"),
)
def test_fetching_latest_youtube_video_for_channel_by_name_error(
    _mock_socket: Mock,
) -> None:
    channel_name: str = "testing_channel_name"
    fetching_result: (
        GettingYouTubeVideosFromChannelNameError | list[YouTubeVideoInfo]
    ) = YtDlpYouTubeVideoFetcher().get_latest_video_from_channel(
        channel_name=channel_name, videos_limit=1
    )

    expected_status = GettingYouTubeVideosFromChannelNameError(
        error="Error fetching latest videos", channel_name=channel_name
    )

    assert isinstance(fetching_result, GettingYouTubeVideosFromChannelNameError)
    assert fetching_result == expected_status
