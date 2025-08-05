import datetime
import os
from typing import Any
from unittest.mock import patch
from tempfile import gettempdir

from src.domain.entity.error.video import DownloadingYouTubeVideoError
from src.domain.entity.video.youtube import DownloadedYouTubeVideo
from src.adapters.inbound.video.downloader.youtube.yt_dlp import (
    YtDlpYouTubeVideoDownloader,
)


def test_download_test_youtube_short_video():
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

    expected: DownloadedYouTubeVideo = DownloadedYouTubeVideo(
        url="https://www.youtube.com/watch?v=C0DPdy98e4c",
        resolution=144,
        download_path=gettempdir(),
        downloaded_file=f"{os.path.join(gettempdir(), "TEST VIDEO.mkv")}",
        title="TEST VIDEO",
        height=144,
        width=192,
        duration="18",
        thumbnail="https://i.ytimg.com/vi/C0DPdy98e4c/hqdefault.jpg?sqp=-oaymwEmCOADEOgC8quKqQMa8AEB-AH-"
        + "BIAC4AOKAgwIABABGGUgZShlMA8=&rs=AOn4CLCpSkMmgqrnX1UfJYnvUv_2pmZWzQ",
        tags=[
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
        ],
        published_date_str=datetime.datetime(2007, 2, 21, 12, 29, 48).isoformat(),
        channel_id="UCHDm-DKoMyJxKVgwGmuTaQA",
        channel_name="Simon Yapp",
        channel_url="https://www.youtube.com/channel/UCHDm-DKoMyJxKVgwGmuTaQA",
        average_rating=0.0,
    )

    assert isinstance(download_result, DownloadedYouTubeVideo)
    assert download_result == expected


@patch("urllib.request.Request", side_effect=Exception("No internet connection"))
def test_no_internet_connection(mock_socket):
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
        error="No internet connection",
        url=url,
        download_path=download_path,
        resolution=resolution,
    )

    assert isinstance(download_result, DownloadingYouTubeVideoError)
    assert download_result == expected


def test_invalid_url_video():
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


def test_invalid_download_path():
    url: str = "https://www.youtube.com/watch?v=C0DPdy98e4c"
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


def test_invalid_video_resolution():
    url: str = "https://www.youtube.com/watch?v=C0DPdy98e4c"
    download_path: str = gettempdir()
    resolution: int = 0
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
        error=f"This video resolution [{resolution}P] is not available for this video !",
        url=url,
        download_path=download_path,
        resolution=resolution,
    )

    assert isinstance(download_result, DownloadingYouTubeVideoError)
    assert download_result == expected
