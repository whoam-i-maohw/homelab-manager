import datetime
import os
from unittest.mock import Mock, patch
from tempfile import gettempdir

from src.domain.entity.error.video import DownloadingYouTubeVideoError
from src.domain.entity.video.youtube import DownloadedYouTubeVideo
from src.adapters.inbound.video.youtube.downloader.yt_dlp import (
    YtDlpYouTubeVideoDownloader,
)

expected_time_timestamp = datetime.datetime.now().timestamp()


@patch(
    "src.adapters.inbound.video.youtube.downloader.yt_dlp.YoutubeDL.extract_info",
    return_value=dict(
        url="testing_url",
        average_rating=0.0,
        channel_id="testing_channel_id",
        channel="testing_channel_name",
        channel_url="testing_channel_url",
        duration_string="1:0",
        height=1,
        width=1,
        timestamp=expected_time_timestamp,
        resolution=1,
        tags=[],
        thumbnail=None,
        fulltitle="testing_title",
        ext="mkv",
    ),
)
def test_download_test_youtube_short_video(_mock_socket: Mock) -> None:
    url: str = "testing_url"
    download_path: str = gettempdir()
    resolution: int = 1
    download_result: (
        DownloadingYouTubeVideoError | DownloadedYouTubeVideo
    ) = YtDlpYouTubeVideoDownloader().download_from_url(
        url=url,
        download_path=download_path,
        resolution=resolution,
        on_complete_callback=lambda s: print(s),
        on_progress_callback=lambda s: print(s),
        cookies_file_path=os.path.join(gettempdir(), "anyfile"),
    )

    expected_video = DownloadedYouTubeVideo(
        url="testing_url",
        average_rating=0.0,
        channel_id="testing_channel_id",
        channel_name="testing_channel_name",
        channel_url="testing_channel_url",
        download_path=gettempdir(),
        downloaded_file=f"{os.path.join(gettempdir(), "testing_title")}.mkv",
        duration="1:0",
        height=1,
        published_date_str=datetime.datetime.fromtimestamp(
            expected_time_timestamp
        ).isoformat(),
        resolution=1,
        tags=[],
        thumbnail=None,
        title="testing_title",
        width=1,
    )

    assert isinstance(download_result, DownloadedYouTubeVideo)
    assert download_result == expected_video


@patch(
    "src.adapters.inbound.video.youtube.downloader.yt_dlp.YoutubeDL.extract_info",
    side_effect=Exception("Failed to extract any player response"),
)
def test_no_internet_connection(_mock_socket: Mock) -> None:
    url: str = "https://www.youtube.com/watch?v=C0DPdy98e4c"
    download_path: str = gettempdir()
    resolution: int = 144
    download_result: (
        DownloadingYouTubeVideoError | DownloadedYouTubeVideo
    ) = YtDlpYouTubeVideoDownloader().download_from_url(
        url=url,
        download_path=download_path,
        resolution=resolution,
        on_complete_callback=lambda s: print(s),
        on_progress_callback=lambda s: print(s),
    )

    expected: DownloadingYouTubeVideoError = DownloadingYouTubeVideoError(
        error="There is no internet connectivity !",
        url=url,
        download_path=download_path,
        resolution=resolution,
    )

    assert isinstance(download_result, DownloadingYouTubeVideoError)
    assert download_result == expected


@patch(
    "src.adapters.inbound.video.youtube.downloader.yt_dlp.YoutubeDL.extract_info",
    side_effect=Exception("is not a valid URL"),
)
def test_invalid_url_video(_mock_socket: Mock) -> None:
    url: str = "https://www.youtube.com/invalid_video_url"
    download_path: str = gettempdir()
    resolution: int = 144
    download_result: (
        DownloadingYouTubeVideoError | DownloadedYouTubeVideo
    ) = YtDlpYouTubeVideoDownloader().download_from_url(
        url=url,
        download_path=download_path,
        resolution=resolution,
        on_complete_callback=lambda s: print(s),
        on_progress_callback=lambda s: print(s),
    )

    expected: DownloadingYouTubeVideoError = DownloadingYouTubeVideoError(
        error=f"This url [{url}] doesn't exist !",
        url=url,
        download_path=download_path,
        resolution=resolution,
    )

    assert isinstance(download_result, DownloadingYouTubeVideoError)
    assert download_result == expected


def test_invalid_download_path() -> None:
    url: str = "testing_url"
    download_path: str = "/invalid"
    resolution: int = 144
    download_result: (
        DownloadingYouTubeVideoError | DownloadedYouTubeVideo
    ) = YtDlpYouTubeVideoDownloader().download_from_url(
        url=url,
        download_path=download_path,
        resolution=resolution,
        on_complete_callback=lambda s: print(s),
        on_progress_callback=lambda s: print(s),
    )

    expected: DownloadingYouTubeVideoError = DownloadingYouTubeVideoError(
        error=f"This download path [{download_path}] doesn't exist !",
        url=url,
        download_path=download_path,
        resolution=resolution,
    )

    assert isinstance(download_result, DownloadingYouTubeVideoError)
    assert download_result == expected
