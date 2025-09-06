import os
from tempfile import gettempdir
from unittest.mock import Mock, patch

from src.adapters.outbound.video.youtube.repository.sqlite.pony_impl import (
    SqlitePonyYouTubeVideoRepository,
)
from src.configs.sqlite import SqliteDatabaseConfigs
from src.domain.entity.error.video import DownloadingYouTubeVideoError
from src.domain.entity.video.youtube import DownloadedYouTubeVideo
from src.services.video.youtube import YouTubeVideoService
from src.adapters.inbound.video.downloader.youtube.yt_dlp import (
    YtDlpYouTubeVideoDownloader,
)


@patch(
    "src.adapters.inbound.video.downloader.youtube.yt_dlp.YtDlpYouTubeVideoDownloader.download_from_url",
    return_value=DownloadedYouTubeVideo(
        url="testing",
        average_rating=0.0,
        channel_id="",
        channel_name="testing_channel",
        channel_url="",
        download_path=os.path.join(gettempdir(), "t", "testing_channel"),
        downloaded_file=os.path.join(gettempdir(), "t", "testing_channel", "testing"),
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
def test_download_youtube_video_from_url_to_channel_name_dir_happy_path(
    _mock_socket: Mock,
) -> None:
    url: str = "https://www.youtube.com/watch?v=C0DPdy98e4c"
    download_root_path: str = gettempdir()
    resolution: int = 1
    youtube_video_downloader = YtDlpYouTubeVideoDownloader()

    with open(os.path.join(gettempdir(), "testing"), "w") as tmp_file:
        tmp_file.write("")

    youtube_video_repository = SqlitePonyYouTubeVideoRepository(
        database_path=os.path.join(gettempdir(), "test.db")
    )

    download_result = YouTubeVideoService(
        youtube_video_downloader=youtube_video_downloader,
        youtube_video_repository=youtube_video_repository,
    ).download_youtube_video_from_url_to_channel_name_dir(
        url=url,
        download_root_path=download_root_path,
        resolution=resolution,
        on_complete_callback=lambda s: print(s),
        on_progress_callback=lambda s: print(s),
        retry_attempts=0,
        retry_timeout=0,
    )

    expected_video = DownloadedYouTubeVideo(
        url="testing",
        average_rating=0.0,
        channel_id="",
        channel_name="testing_channel",
        channel_url="",
        download_path=os.path.join(gettempdir(), "t", "testing_channel"),
        downloaded_file=os.path.join(gettempdir(), "t", "testing_channel", "testing"),
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


def test_download_youtube_video_from_url_to_channel_name_dir_invalid_directory_path() -> (
    None
):
    url: str = "https://www.youtube.com/watch?v=C0DPdy98e4c"
    download_root_path: str = "/invalid"
    resolution: int = 144
    youtube_video_downloader = YtDlpYouTubeVideoDownloader()

    youtube_video_repository = SqlitePonyYouTubeVideoRepository(
        database_path=os.path.join(gettempdir(), "test.db")
    )

    download_result = YouTubeVideoService(
        youtube_video_downloader=youtube_video_downloader,
        youtube_video_repository=youtube_video_repository,
    ).download_youtube_video_from_url_to_channel_name_dir(
        url=url,
        download_root_path=download_root_path,
        resolution=resolution,
        on_complete_callback=lambda s: print(s),
        on_progress_callback=lambda s: print(s),
        retry_attempts=0,
        retry_timeout=0,
    )

    assert isinstance(download_result, DownloadingYouTubeVideoError)
    assert (
        f"This download path [{download_root_path}] doesn't exist !"
        in download_result.error
    )
