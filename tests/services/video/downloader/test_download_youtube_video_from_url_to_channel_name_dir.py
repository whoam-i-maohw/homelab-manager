import datetime
import os
from tempfile import gettempdir

from src.domain.entity.error.video import DownloadingYouTubeVideoError
from src.domain.entity.video.youtube import DownloadedYouTubeVideo
from src.services.video.downloader import VideoDownloaderService
from src.adapters.inbound.video.downloader.youtube.yt_dlp import (
    YtDlpYouTubeVideoDownloader,
)
import pytest


@pytest.fixture()
def browser_cookie_path():
    yield os.environ.get("BROWSER_COOKIE_PATH", None)


def test_download_youtube_video_from_url_to_channel_name_dir_happy_path(
    browser_cookie_path: str | None,
) -> None:
    url: str = "https://www.youtube.com/watch?v=C0DPdy98e4c"
    download_root_path: str = gettempdir()
    resolution: int = 144
    youtube_video_downloader = YtDlpYouTubeVideoDownloader()

    download_result = VideoDownloaderService(
        youtube_video_downloader=youtube_video_downloader
    ).download_youtube_video_from_url_to_channel_name_dir(
        url=url,
        download_root_path=download_root_path,
        resolution=resolution,
        cookies_file_path=browser_cookie_path,
        on_complete_callback=lambda s: print(s),
        on_progress_callback=lambda s: print(s),
        retry_attempts=0,
        retry_timeout=0,
    )

    expected_download_path: str = os.path.join(download_root_path, "s", "Simon Yapp")
    expected_url = "https://www.youtube.com/watch?v=C0DPdy98e4c"
    expected_downloaded_file = f"{os.path.join(expected_download_path, "TEST VIDEO")}"
    expected_title = "TEST VIDEO"
    expected_duration = "18"
    expected_thumbnail = (
        "https://i.ytimg.com/vi/C0DPdy98e4c/hqdefault.jpg?sqp=-oaymwEmCOADEOgC8quKqQMa8AEB-AH-"
        + "BIAC4AOKAgwIABABGGUgZShlMA8=&rs=AOn4CLCpSkMmgqrnX1UfJYnvUv_2pmZWzQ"
    )
    expected_tags = [
        "TONES",
        "AND",
        "BARS",
        "Countdown",
        "Black & White",
        "Sync Flashes",
        "Sync",
        "Test Testing",
        "Test",
        "Testing",
        "54321",
        "Numbers",
        "Quality",
        "Call",
        "Funny",
    ]
    expected_average_rating = 0.0

    assert isinstance(download_result, DownloadedYouTubeVideo)
    assert download_result.url == expected_url
    assert download_result.download_path == expected_download_path
    assert download_result.average_rating == expected_average_rating
    assert download_result.tags == expected_tags
    assert download_result.thumbnail == expected_thumbnail
    assert download_result.duration == expected_duration
    assert download_result.title == expected_title
    assert expected_downloaded_file in download_result.downloaded_file


def test_download_youtube_video_from_url_to_channel_name_dir_invalid_directory_path(
    browser_cookie_path: str | None,
) -> None:
    url: str = "https://www.youtube.com/watch?v=C0DPdy98e4c"
    download_root_path: str = "/"
    resolution: int = 144
    youtube_video_downloader = YtDlpYouTubeVideoDownloader()

    download_result = VideoDownloaderService(
        youtube_video_downloader=youtube_video_downloader
    ).download_youtube_video_from_url_to_channel_name_dir(
        url=url,
        download_root_path=download_root_path,
        resolution=resolution,
        cookies_file_path=browser_cookie_path,
        on_complete_callback=lambda s: print(s),
        on_progress_callback=lambda s: print(s),
        retry_attempts=0,
        retry_timeout=0,
    )

    assert isinstance(download_result, DownloadingYouTubeVideoError)
    assert "unable to open for writing" in download_result.error
