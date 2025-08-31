from src.domain.entity.video.youtube import RepositoryYouTubeVideo
from src.domain.entity.error.video import (
    DownloadedYouTubeVideo,
    GettingYouTubeVideoError,
    SavingYouTubeVideoError,
)
from src.adapters.outbound.video.youtube.repository.sqlite.pony_impl import (
    SqlitePonyYouTubeVideoRepository,
)
import pytest


@pytest.fixture
def setup_db():
    yield SqlitePonyYouTubeVideoRepository(database_path=":memory:")


def get_dummy_video() -> DownloadedYouTubeVideo:
    return DownloadedYouTubeVideo(
        url="testing",
        average_rating=0.0,
        channel_id="-",
        channel_name="testing_channel",
        channel_url="-",
        download_path="-",
        downloaded_file="-",
        duration="-",
        height=1,
        published_date_str="-",
        resolution=1,
        tags=[],
        thumbnail="-",
        title="-",
        width=1,
    )


def test_save_youtube_video(setup_db: SqlitePonyYouTubeVideoRepository) -> None:
    db = setup_db
    video = get_dummy_video()
    save_video_status = db.save_video(
        video=video,
    )

    assert isinstance(save_video_status, RepositoryYouTubeVideo)
    assert save_video_status.video == video
    assert save_video_status.uuid is not None
    assert save_video_status.created_at is not None


def test_save_same_youtube_video_twice(
    setup_db: SqlitePonyYouTubeVideoRepository,
) -> None:
    db = setup_db
    video = get_dummy_video()
    save_video_status = db.save_video(
        video=video,
    )

    assert isinstance(save_video_status, RepositoryYouTubeVideo)
    assert save_video_status.video == video
    assert save_video_status.uuid is not None
    assert save_video_status.created_at is not None

    save_video_status = db.save_video(
        video=video,
    )

    assert isinstance(save_video_status, SavingYouTubeVideoError)
    assert save_video_status.error == "This video is already existed in the database !"
    assert save_video_status.video == video


def test_get_video_by_uuid(setup_db: SqlitePonyYouTubeVideoRepository) -> None:
    repository = setup_db
    video = get_dummy_video()
    save_video_status = repository.save_video(
        video=video,
    )
    assert isinstance(save_video_status, RepositoryYouTubeVideo)

    get_video_status = repository.get_video_by_uuid(uuid=save_video_status.uuid)

    assert isinstance(get_video_status, RepositoryYouTubeVideo)
    assert get_video_status == save_video_status


def test_get_video_by_uuid_not_found(
    setup_db: SqlitePonyYouTubeVideoRepository,
) -> None:
    repository = setup_db

    uuid: str = "1"
    get_video_status = repository.get_video_by_uuid(uuid=uuid)

    assert isinstance(get_video_status, GettingYouTubeVideoError)
    assert get_video_status.error == f"There is no video saved with uuid [{uuid}] !"


def test_get_video_by_url(setup_db: SqlitePonyYouTubeVideoRepository) -> None:
    repository = setup_db
    video = get_dummy_video()
    save_video_status = repository.save_video(
        video=video,
    )
    assert isinstance(save_video_status, RepositoryYouTubeVideo)

    get_video_status = repository.get_video_by_url(url=video.url)

    assert isinstance(get_video_status, RepositoryYouTubeVideo)
    assert get_video_status == save_video_status


def test_get_video_by_url_not_found(
    setup_db: SqlitePonyYouTubeVideoRepository,
) -> None:
    repository = setup_db

    url: str = "not-found"
    get_video_status = repository.get_video_by_url(url=url)

    assert isinstance(get_video_status, GettingYouTubeVideoError)
    assert get_video_status.error == f"There is no video saved with url [{url}] !"


def test_get_video_by_video_title(setup_db: SqlitePonyYouTubeVideoRepository) -> None:
    repository = setup_db
    video = get_dummy_video()
    save_video_status = repository.save_video(
        video=video,
    )
    assert isinstance(save_video_status, RepositoryYouTubeVideo)

    get_video_status = repository.get_video_by_video_title(video_title=video.title)

    assert isinstance(get_video_status, RepositoryYouTubeVideo)
    assert get_video_status == save_video_status


def test_get_video_by_video_title_not_found(
    setup_db: SqlitePonyYouTubeVideoRepository,
) -> None:
    repository = setup_db

    title: str = "not-found"
    get_video_status = repository.get_video_by_video_title(video_title=title)

    assert isinstance(get_video_status, GettingYouTubeVideoError)
    assert get_video_status.error == f"There is no video saved with title [{title}] !"


def test_get_video_by_channel_name(setup_db: SqlitePonyYouTubeVideoRepository) -> None:
    repository = setup_db
    video = get_dummy_video()
    save_video_status = repository.save_video(
        video=video,
    )
    assert isinstance(save_video_status, RepositoryYouTubeVideo)

    get_videos_status = repository.get_videos_by_channel_name(
        channel_name=video.channel_name
    )

    assert isinstance(get_videos_status, list)
    assert len(get_videos_status) == 1
    assert isinstance(get_videos_status[0], RepositoryYouTubeVideo)
    assert get_videos_status[0] == save_video_status


def test_get_video_by_channel_name_not_found(
    setup_db: SqlitePonyYouTubeVideoRepository,
) -> None:
    repository = setup_db

    channel_name: str = "not-found"
    get_videos_status = repository.get_videos_by_channel_name(channel_name=channel_name)

    assert isinstance(get_videos_status, list)
    assert len(get_videos_status) == 0
