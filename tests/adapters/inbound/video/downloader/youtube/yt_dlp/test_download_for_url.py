import os
from unittest.mock import patch
from tempfile import gettempdir

from src.domain.entity.error.video import DownloadingYouTubeVideoError
from src.domain.entity.video.youtube import DownloadedYouTubeVideo
from src.adapters.inbound.video.downloader.youtube.yt_dlp import (
    YtDlpYouTubeVideoDownloader,
)
import pytest


@pytest.fixture()
def browser_cookie_path():
    yield os.environ.get("BROWSER_COOKIE_PATH", None)


def test_download_test_youtube_short_video(browser_cookie_path: str | None) -> None:
    url: str = "https://www.youtube.com/watch?v=C0DPdy98e4c"
    download_path: str = gettempdir()
    resolution: int = 144
    download_result: (
        DownloadingYouTubeVideoError | DownloadedYouTubeVideo
    ) = YtDlpYouTubeVideoDownloader().download_from_url(
        url=url,
        download_path=download_path,
        resolution=resolution,
        cookies_file_path=browser_cookie_path,
        on_complete_callback=lambda s: print(s),
        on_progress_callback=lambda s: print(s),
    )

    expected_url = "https://www.youtube.com/watch?v=C0DPdy98e4c"
    expected_download_path = gettempdir()
    expected_downloaded_file = f"{os.path.join(gettempdir(), "TEST VIDEO")}"
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


@patch("urllib.request.Request", side_effect=Exception("No internet connection"))
def test_no_internet_connection(mock_socket, browser_cookie_path: str | None) -> None:
    url: str = "https://www.youtube.com/watch?v=C0DPdy98e4c"
    download_path: str = gettempdir()
    resolution: int = 144
    download_result: (
        DownloadingYouTubeVideoError | DownloadedYouTubeVideo
    ) = YtDlpYouTubeVideoDownloader().download_from_url(
        url=url,
        download_path=download_path,
        resolution=resolution,
        cookies_file_path=browser_cookie_path,
        on_complete_callback=lambda s: print(s),
        on_progress_callback=lambda s: print(s),
    )

    expected: DownloadingYouTubeVideoError = DownloadingYouTubeVideoError(
        error="No internet connection",
        url=url,
        download_path=download_path,
        resolution=resolution,
    )

    assert isinstance(download_result, DownloadingYouTubeVideoError)
    assert download_result == expected


def test_invalid_url_video(browser_cookie_path: str | None) -> None:
    url: str = "https://www.youtube.com/invalid_video_url"
    download_path: str = gettempdir()
    resolution: int = 144
    download_result: (
        DownloadingYouTubeVideoError | DownloadedYouTubeVideo
    ) = YtDlpYouTubeVideoDownloader().download_from_url(
        url=url,
        download_path=download_path,
        resolution=resolution,
        cookies_file_path=browser_cookie_path,
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


def test_invalid_download_path(browser_cookie_path: str | None) -> None:
    url: str = "https://www.youtube.com/watch?v=C0DPdy98e4c"
    download_path: str = "/invalid"
    resolution: int = 144
    download_result: (
        DownloadingYouTubeVideoError | DownloadedYouTubeVideo
    ) = YtDlpYouTubeVideoDownloader().download_from_url(
        url=url,
        download_path=download_path,
        resolution=resolution,
        cookies_file_path=browser_cookie_path,
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
