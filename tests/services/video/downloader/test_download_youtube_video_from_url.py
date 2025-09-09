from tempfile import gettempdir
import os
from tempfile import gettempdir
from unittest.mock import Mock, patch

from pytest import CaptureFixture

from src.adapters.inbound.video.youtube.fetcher.yt_dlp import YtDlpYouTubeVideoFetcher
from src.adapters.outbound.video.youtube.repository.sqlite.pony_impl import (
    SqlitePonyYouTubeVideoRepository,
)
from src.configs.sqlite import SqliteDatabaseConfigs
from src.domain.entity.error.video import DownloadingYouTubeVideoError
from src.domain.entity.video.youtube import DownloadedYouTubeVideo
from src.adapters.inbound.video.youtube.downloader.yt_dlp import (
    YtDlpYouTubeVideoDownloader,
)
from src.services.video.youtube import YouTubeVideoService
from src.domain.entity.error.video import DownloadingYouTubeVideoError


@patch(
    "src.adapters.inbound.video.youtube.downloader.yt_dlp.YtDlpYouTubeVideoDownloader.download_from_url",
    return_value=DownloadedYouTubeVideo(
        url="",
        average_rating=0.0,
        channel_id="",
        channel_name="",
        channel_url="",
        download_path="",
        downloaded_file="",
        duration="",
        height=1,
        published_date_str="",
        resolution=1,
        tags=[],
        thumbnail=None,
        title="",
        width=1,
    ),
)
def test_download_youtube_video_from_url_happy_path(_mock_socket: Mock) -> None:
    url: str = "https://www.youtube.com/watch?v=C0DPdy98e4c"
    download_path: str = gettempdir()
    resolution: int = 144
    youtube_video_downloader = YtDlpYouTubeVideoDownloader()

    youtube_video_repository = SqlitePonyYouTubeVideoRepository(
        database_path=os.path.join(gettempdir(), "test.db")
    )

    download_result = YouTubeVideoService(
        youtube_video_downloader=youtube_video_downloader,
        youtube_video_fetcher=YtDlpYouTubeVideoFetcher(),
        youtube_video_repository=youtube_video_repository,
    ).download_youtube_video_from_url(
        url=url,
        download_path=download_path,
        resolution=resolution,
        on_complete_callback=lambda s: print(s),
        on_progress_callback=lambda s: print(s),
        retry_attempts=1,
        retry_timeout=0,
    )

    expected_video = DownloadedYouTubeVideo(
        url="",
        average_rating=0.0,
        channel_id="",
        channel_name="",
        channel_url="",
        download_path="",
        downloaded_file="",
        duration="",
        height=1,
        published_date_str="",
        resolution=1,
        tags=[],
        thumbnail=None,
        title="",
        width=1,
    )

    assert isinstance(download_result, DownloadedYouTubeVideo)
    assert download_result == expected_video


@patch(
    "src.adapters.inbound.video.youtube.downloader.yt_dlp.YtDlpYouTubeVideoDownloader.download_from_url",
    return_value=DownloadingYouTubeVideoError(
        error=f"This url [https://www.youtube.com/watch?v=invalid_video] doesn't exist !",
        url="https://www.youtube.com/watch?v=invalid_video",
        resolution=1,
        download_path=gettempdir(),
    ),
)
def test_download_youtube_video_from_url_with_retry_attempts(
    _mock_socket: Mock,
    capsys: CaptureFixture,
) -> None:
    url: str = "https://www.youtube.com/watch?v=invalid_video"
    download_path: str = gettempdir()
    resolution: int = 1
    youtube_video_downloader = YtDlpYouTubeVideoDownloader()
    retry_attempts: int = 3

    youtube_video_repository = SqlitePonyYouTubeVideoRepository(
        database_path=os.path.join(gettempdir(), "test.db")
    )

    download_result = YouTubeVideoService(
        youtube_video_downloader=youtube_video_downloader,
        youtube_video_fetcher=YtDlpYouTubeVideoFetcher(),
        youtube_video_repository=youtube_video_repository,
    ).download_youtube_video_from_url(
        url=url,
        download_path=download_path,
        resolution=resolution,
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


@patch(
    "src.adapters.inbound.video.youtube.downloader.yt_dlp.YtDlpYouTubeVideoDownloader.download_from_url",
    return_value=DownloadingYouTubeVideoError(
        error=f"This url [https://www.youtube.com/watch?v=invalid_video] doesn't exist !",
        url="https://www.youtube.com/watch?v=invalid_video",
        resolution=1,
        download_path=gettempdir(),
    ),
)
def test_download_youtube_video_from_url_with_retry_timeout(
    _mock_socket: Mock,
    capsys: CaptureFixture,
) -> None:
    url: str = "https://www.youtube.com/watch?v=invalid_video"
    download_path: str = gettempdir()
    resolution: int = 1
    youtube_video_downloader = YtDlpYouTubeVideoDownloader()
    retry_timeout: int = 1

    youtube_video_repository = SqlitePonyYouTubeVideoRepository(
        database_path=os.path.join(gettempdir(), "test.db")
    )

    download_result = YouTubeVideoService(
        youtube_video_downloader=youtube_video_downloader,
        youtube_video_fetcher=YtDlpYouTubeVideoFetcher(),
        youtube_video_repository=youtube_video_repository,
    ).download_youtube_video_from_url(
        url=url,
        download_path=download_path,
        resolution=resolution,
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
