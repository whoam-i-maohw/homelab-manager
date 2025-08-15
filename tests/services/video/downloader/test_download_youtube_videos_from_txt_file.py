import os
from tempfile import gettempdir

from src.domain.entity.video.youtube import DownloadedYouTubeVideo
from src.services.video.downloader import VideoDownloaderService
from src.adapters.inbound.video.downloader.youtube.yt_dlp import (
    YtDlpYouTubeVideoDownloader,
)
import pytest
from tempfile import mkstemp


@pytest.fixture()
def browser_cookie_path():
    yield os.environ.get("BROWSER_COOKIE_PATH", None)


def test_download_youtube_videos_from_txt_file_happy_path(
    browser_cookie_path: str | None,
) -> None:
    url_1: str = "https://www.youtube.com/watch?v=C0DPdy98e4c"
    url_2: str = "https://www.youtube.com/watch?v=C0DPdy98e4c"
    url_3: str = "https://www.youtube.com/watch?v=C0DPdy98e4c"

    _file_descriptor, tmp_txt_file = mkstemp(dir=gettempdir())

    with open(tmp_txt_file, "w") as urls_file:
        urls_file.write(url_1 + "\n")
        urls_file.write(url_2 + "\n")
        urls_file.write(url_3 + "\n")

    download_root_path: str = gettempdir()
    resolution: int = 144
    youtube_video_downloader = YtDlpYouTubeVideoDownloader()

    download_result = VideoDownloaderService(
        youtube_video_downloader=youtube_video_downloader
    ).download_youtube_videos_from_txt_file(
        urls_txt_file_path=tmp_txt_file,
        download_path=download_root_path,
        resolution=resolution,
        cookies_file_path=browser_cookie_path,
        on_complete_callback=lambda s: print(s),
        on_progress_callback=lambda s: print(s),
        retry_attempts=2,
        retry_timeout=1,
    )

    errors, successes = download_result

    assert len(errors) == 0
    assert len(successes) == 3

    expected_url = "https://www.youtube.com/watch?v=C0DPdy98e4c"
    expected_downloaded_file = f"{os.path.join(download_root_path, "TEST VIDEO")}"
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

    for success in successes:
        assert isinstance(success, DownloadedYouTubeVideo)
        assert success.url == expected_url
        assert success.download_path == download_root_path
        assert success.average_rating == expected_average_rating
        assert success.tags == expected_tags
        assert success.thumbnail == expected_thumbnail
        assert success.duration == expected_duration
        assert success.title == expected_title
        assert expected_downloaded_file in success.downloaded_file


def test_download_youtube_videos_from_txt_file_invalid_file_path(
    browser_cookie_path: str | None,
) -> None:
    tmp_txt_file = "/invalid_file"

    download_root_path: str = gettempdir()
    resolution: int = 144
    youtube_video_downloader = YtDlpYouTubeVideoDownloader()

    download_result = VideoDownloaderService(
        youtube_video_downloader=youtube_video_downloader
    ).download_youtube_videos_from_txt_file(
        urls_txt_file_path=tmp_txt_file,
        download_path=download_root_path,
        resolution=resolution,
        cookies_file_path=browser_cookie_path,
        on_complete_callback=lambda s: print(s),
        on_progress_callback=lambda s: print(s),
        retry_attempts=2,
        retry_timeout=1,
    )

    errors, successes = download_result

    assert len(errors) == 1
    assert len(successes) == 0

    assert (
        errors[0].error == f"This urls txt file path [{tmp_txt_file}] doesn't exist !"
    )
    assert errors[0].download_path == download_root_path
    assert errors[0].url == tmp_txt_file
    assert errors[0].resolution == resolution
