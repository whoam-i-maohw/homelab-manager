from dataclasses import dataclass

from src.domain.entity.commands.generic_command import GenericCommand


@dataclass(frozen=True, slots=True, kw_only=True)
class DownloadYouTubeVideoFromTxtFileToChannelNameDirCommand(GenericCommand):
    txt_file_path: str
    resolution: int = 1080
    desired_download_path: str
