import datetime
from unittest.mock import Mock, patch
from src.domain.entity.error.video import GettingYouTubeVideoInfoError
from src.domain.entity.video.youtube import YouTubeVideoInfo
from src.adapters.inbound.video.youtube.fetcher.yt_dlp import YtDlpYouTubeVideoFetcher


expected_time_timestamp = datetime.datetime.now().timestamp()


@patch(
    "src.adapters.inbound.video.youtube.downloader.yt_dlp.YoutubeDL.extract_info",
    return_value=dict(
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
    ),
)
def test_fetching_youtube_video_info_for_url(_mock_socket: Mock) -> None:
    url: str = "testing_url"
    fetching_result: (
        GettingYouTubeVideoInfoError | YouTubeVideoInfo
    ) = YtDlpYouTubeVideoFetcher().get_video_info_from_url(
        url=url,
    )

    expected_video = YouTubeVideoInfo(
        url=f"https://www.youtube.com/watch?v={url}",
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

    assert isinstance(fetching_result, YouTubeVideoInfo)
    assert fetching_result == expected_video


@patch(
    "src.adapters.inbound.video.youtube.downloader.yt_dlp.YoutubeDL.extract_info",
    side_effect=Exception("Error fetching video info !"),
)
def test_fetching_youtube_video_info_error(_mock_socket: Mock) -> None:
    url: str = "testing_url"
    fetching_result: (
        GettingYouTubeVideoInfoError | YouTubeVideoInfo
    ) = YtDlpYouTubeVideoFetcher().get_video_info_from_url(
        url=url,
    )

    expected_status = GettingYouTubeVideoInfoError(error="Error fetching video info !")

    assert isinstance(fetching_result, GettingYouTubeVideoInfoError)
    assert fetching_result == expected_status
