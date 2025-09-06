import os
from tempfile import gettempdir
from unittest.mock import Mock, patch

from src.adapters.outbound.video.youtube.repository.sqlite.pony_impl import (
    SqlitePonyYouTubeVideoRepository,
)
from src.configs.sqlite import SqliteDatabaseConfigs
from src.domain.entity.video.youtube import DownloadedYouTubeVideo
from src.services.video.youtube import YouTubeVideoService
from src.adapters.inbound.video.downloader.youtube.yt_dlp import (
    YtDlpYouTubeVideoDownloader,
)
from tempfile import mkstemp


@patch(
    "src.adapters.inbound.video.downloader.youtube.yt_dlp.YtDlpYouTubeVideoDownloader.download_from_url",
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
def test_download_youtube_videos_from_txt_file_happy_path(_mock_socket: Mock) -> None:
    url_1: str = "https://www.youtube.com/watch?v=C0DPdy98e4c"

    _file_descriptor, tmp_txt_file = mkstemp(dir=gettempdir())

    with open(tmp_txt_file, "w") as urls_file:
        urls_file.write(url_1 + "\n")

    download_root_path: str = gettempdir()
    resolution: int = 1
    youtube_video_downloader = YtDlpYouTubeVideoDownloader()

    youtube_video_repository = SqlitePonyYouTubeVideoRepository(
        database_path=os.path.join(gettempdir(), "test.db")
    )

    download_result = YouTubeVideoService(
        youtube_video_downloader=youtube_video_downloader,
        youtube_video_repository=youtube_video_repository,
    ).download_youtube_videos_from_txt_file(
        urls_txt_file_path=tmp_txt_file,
        download_path=download_root_path,
        resolution=resolution,
        on_complete_callback=lambda s: print(s),
        on_progress_callback=lambda s: print(s),
        retry_attempts=2,
        retry_timeout=1,
        concurrency=1,
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

    errors, successes = download_result

    assert len(errors) == 0
    assert len(successes) == 1

    for success in successes:
        assert isinstance(success, DownloadedYouTubeVideo)
        assert success == expected_video


def test_download_youtube_videos_from_txt_file_invalid_file_path() -> None:
    tmp_txt_file = "/invalid_file"

    download_root_path: str = gettempdir()
    resolution: int = 1
    youtube_video_downloader = YtDlpYouTubeVideoDownloader()

    youtube_video_repository = SqlitePonyYouTubeVideoRepository(
        database_path=os.path.join(gettempdir(), "test.db")
    )

    download_result = YouTubeVideoService(
        youtube_video_downloader=youtube_video_downloader,
        youtube_video_repository=youtube_video_repository,
    ).download_youtube_videos_from_txt_file(
        urls_txt_file_path=tmp_txt_file,
        download_path=download_root_path,
        resolution=resolution,
        on_complete_callback=lambda s: print(s),
        on_progress_callback=lambda s: print(s),
        retry_attempts=2,
        retry_timeout=1,
        concurrency=1,
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
