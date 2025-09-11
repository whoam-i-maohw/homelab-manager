import datetime
import os
from tempfile import gettempdir
from typing import Any, Generator
import pytest

from src.domain.entity.commands.video.youtube.download_youtube_video_from_url_command import (
    DownloadYouTubeVideoFromUrlCommand,
)
from src.domain.entity.commands.video.youtube.download_youtube_video_from_url_to_channel_name_dir_command import (
    DownloadYouTubeVideoFromUrlToChannelNameDirCommand,
)
from src.domain.entity.commands.video.youtube.download_youtube_videos_from_txt_file_command import (
    DownloadYouTubeVideoFromTxtFileCommand,
)
from src.domain.entity.commands.video.youtube.download_youtube_videos_from_txt_file_to_channel_name_dir_command import (
    DownloadYouTubeVideoFromTxtFileToChannelNameDirCommand,
)
from src.domain.entity.error.message_queue import SavingCommandError
from src.domain.entity.commands.generic_command import GenericCommand
from src.adapters.outbound.command.repository.sqlite.pony_impl import (
    PonySqliteCommandRepository,
)


@pytest.fixture
def setup_db() -> Generator[PonySqliteCommandRepository, Any, None]:
    yield PonySqliteCommandRepository(database_path=":memory:")


def get_dummy_command() -> GenericCommand:
    return GenericCommand(created_at_iso_format=datetime.datetime.now().isoformat())


def test_save_command(setup_db: PonySqliteCommandRepository) -> None:
    db = setup_db
    command = get_dummy_command()
    save_command_status = db.save_command(command=command)

    assert save_command_status is None


def test_save_same_command_twice(setup_db: PonySqliteCommandRepository) -> None:
    db = setup_db
    command = get_dummy_command()
    save_command_status = db.save_command(command=command)

    assert save_command_status is None

    save_command_status = db.save_command(command=command)

    assert isinstance(save_command_status, SavingCommandError)
    assert (
        save_command_status.error == "This command is already existed in the database !"
    )
    assert save_command_status.command == command


def test_get_commands_for_topic(setup_db: PonySqliteCommandRepository) -> None:
    db = setup_db
    time = datetime.datetime.now().isoformat()

    command_1 = get_dummy_command()
    command_2 = DownloadYouTubeVideoFromUrlCommand(
        created_at_iso_format=time,
        desired_download_path=gettempdir(),
        resolution=1,
        url="testing_url",
    )
    command_3 = DownloadYouTubeVideoFromUrlToChannelNameDirCommand(
        created_at_iso_format=time,
        desired_download_path=gettempdir(),
        resolution=1,
        url="testing-url",
    )
    command_4 = DownloadYouTubeVideoFromTxtFileCommand(
        created_at_iso_format=time,
        desired_download_path=gettempdir(),
        resolution=1,
        txt_file_path=f"{os.path.join(gettempdir(), "any-file")}",
    )
    command_5 = DownloadYouTubeVideoFromTxtFileToChannelNameDirCommand(
        created_at_iso_format=time,
        desired_download_path=gettempdir(),
        resolution=1,
        txt_file_path=f"{os.path.join(gettempdir(), "any-file")}",
    )

    for command in [command_1, command_2, command_3, command_4, command_5]:
        save_command_status = db.save_command(command=command)
        assert save_command_status is None

        getting_commands_status = db.get_commands_by_topic(topic=command.get_topic())
        assert len(getting_commands_status) == 1
        assert getting_commands_status[0] == command


def test_get_commands_for_non_existing_topic(
    setup_db: PonySqliteCommandRepository,
) -> None:
    db = setup_db

    getting_commands_status = db.get_commands_by_topic(topic="non-existence")
    assert len(getting_commands_status) == 0
    assert getting_commands_status == []
