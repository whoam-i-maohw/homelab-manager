from dataclasses import asdict
from pony.orm import db_session, Database

from src.domain.entity.commands.generic_command import GenericCommand
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
from src.ports.outbound.command.repository import CommandRepositoryInterface
from src.adapters.outbound.command.repository.sqlite.pony_impl.models.command import (
    register_command_model,
)


class PonySqliteCommandRepository(CommandRepositoryInterface):
    def __init__(self, *, database_path: str) -> None:
        self.__db = Database()
        self.__command_model = register_command_model(db=self.__db)
        self.__db.bind(provider="sqlite", filename=database_path, create_db=True)
        self.__db.generate_mapping(create_tables=True)

    def save_command(self, *, command: GenericCommand) -> SavingCommandError | None:
        try:
            with db_session:
                self.__command_model(
                    topic=command.get_topic(),
                    created_at_iso_format=command.created_at_iso_format,
                    command_data_class_name=command.get_topic(),
                    command_data_json=asdict(command),
                )
        except Exception as ex:
            error_message: str = str(ex)

            if "IntegrityError: UNIQUE constraint failed" in error_message:
                error_message = "This command is already existed in the database !"
            else:
                error_message = f"Error persisting the video for the reason [{str(ex)}]"

            return SavingCommandError(
                error=error_message,
                command=command,
            )

    def get_commands_by_topic(self, *, topic: str) -> list[GenericCommand]:
        try:
            with db_session:
                res: list[GenericCommand] = []
                for command in self.__command_model.select(topic=topic):
                    match command.command_data_class_name:
                        case "GenericCommand":
                            res.append(GenericCommand(**command.command_data_json))
                        case "DownloadYouTubeVideoFromUrlCommand":
                            res.append(
                                DownloadYouTubeVideoFromUrlCommand(
                                    **command.command_data_json
                                )
                            )
                        case "DownloadYouTubeVideoFromUrlToChannelNameDirCommand":
                            res.append(
                                DownloadYouTubeVideoFromUrlToChannelNameDirCommand(
                                    **command.command_data_json
                                )
                            )
                        case "DownloadYouTubeVideoFromTxtFileCommand":
                            res.append(
                                DownloadYouTubeVideoFromTxtFileCommand(
                                    **command.command_data_json
                                )
                            )
                        case "DownloadYouTubeVideoFromTxtFileToChannelNameDirCommand":
                            res.append(
                                DownloadYouTubeVideoFromTxtFileToChannelNameDirCommand(
                                    **command.command_data_json
                                )
                            )
                return res
        except Exception as ex:
            print(f"Error fetching commands to topic [{topic}] for reason [{str(ex)}]")
            return []
