from tempfile import gettempdir
import datetime
import os
from tempfile import gettempdir

from pytest import CaptureFixture

from src.domain.entity.error.video import DownloadingYouTubeVideoError
from src.domain.entity.video.youtube import DownloadedYouTubeVideo
from src.adapters.inbound.video.downloader.youtube.yt_dlp import (
    YtDlpYouTubeVideoDownloader,
)
from src.services.video.downloader import VideoDownloaderService
from src.domain.entity.error.video import DownloadingYouTubeVideoError
import pytest


@pytest.fixture()
def browser_cookie_path():
    yield os.environ.get("BROWSER_COOKIE_PATH", None)


def test_download_youtube_video_from_url_happy_path(
    browser_cookie_path: str | None,
) -> None:
    url: str = "https://www.youtube.com/watch?v=C0DPdy98e4c"
    download_path: str = gettempdir()
    resolution: int = 144
    youtube_video_downloader = YtDlpYouTubeVideoDownloader()

    download_result = VideoDownloaderService(
        youtube_video_downloader=youtube_video_downloader
    ).download_youtube_video_from_url(
        url=url,
        download_path=download_path,
        resolution=resolution,
        cookies_file_path=browser_cookie_path,
        on_complete_callback=lambda s: print(s),
        on_progress_callback=lambda s: print(s),
        retry_attempts=1,
        retry_timeout=0,
    )

    expected_download_path: str = download_path
    expected_url = "https://www.youtube.com/watch?v=C0DPdy98e4c"
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
    expected_published_date_str = datetime.datetime(2007, 2, 21, 12, 29, 48).isoformat()

    assert isinstance(download_result, DownloadedYouTubeVideo)
    assert download_result.url == expected_url
    assert download_result.download_path == expected_download_path
    assert download_result.average_rating == expected_average_rating
    assert download_result.published_date_str == expected_published_date_str
    assert download_result.tags == expected_tags
    assert download_result.thumbnail == expected_thumbnail
    assert download_result.duration == expected_duration
    assert download_result.title == expected_title
    assert expected_downloaded_file in download_result.downloaded_file


def test_download_youtube_video_from_url_with_retry_attempts(
    capsys: CaptureFixture, browser_cookie_path: str | None
) -> None:
    url: str = "https://www.youtube.com/watch?v=invalid_video"
    download_path: str = gettempdir()
    resolution: int = 144
    youtube_video_downloader = YtDlpYouTubeVideoDownloader()
    retry_attempts: int = 3

    download_result = VideoDownloaderService(
        youtube_video_downloader=youtube_video_downloader
    ).download_youtube_video_from_url(
        url=url,
        download_path=download_path,
        resolution=resolution,
        cookies_file_path=browser_cookie_path,
        on_complete_callback=lambda s: print(s),
        on_progress_callback=lambda s: print(s),
        retry_attempts=retry_attempts,
        retry_timeout=0,
    )

    expected = DownloadingYouTubeVideoError(
        error=f"This url [{url}] doesn't exist !",
        url=url,
        resolution=resolution,
        download_path=download_path,
    )

    captured = capsys.readouterr()
    assert f"Remaining attempts [2]" in captured.out
    assert f"Remaining attempts [1]" in captured.out
    assert f"Remaining attempts [0]" in captured.out

    assert isinstance(download_result, DownloadingYouTubeVideoError)
    assert download_result == expected


def test_download_youtube_video_from_url_with_retry_timeout(
    capsys: CaptureFixture, browser_cookie_path: str | None
) -> None:
    url: str = "https://www.youtube.com/watch?v=invalid_video"
    download_path: str = gettempdir()
    resolution: int = 144
    youtube_video_downloader = YtDlpYouTubeVideoDownloader()
    retry_timeout: int = 1

    download_result = VideoDownloaderService(
        youtube_video_downloader=youtube_video_downloader
    ).download_youtube_video_from_url(
        url=url,
        download_path=download_path,
        resolution=resolution,
        cookies_file_path=browser_cookie_path,
        on_complete_callback=lambda s: print(s),
        on_progress_callback=lambda s: print(s),
        retry_attempts=1,
        retry_timeout=retry_timeout,
    )

    expected = DownloadingYouTubeVideoError(
        error=f"This url [{url}] doesn't exist !",
        url=url,
        resolution=resolution,
        download_path=download_path,
    )

    captured = capsys.readouterr()
    assert f"Waiting for [{retry_timeout}] seconds" in captured.out

    assert isinstance(download_result, DownloadingYouTubeVideoError)
    assert download_result == expected
