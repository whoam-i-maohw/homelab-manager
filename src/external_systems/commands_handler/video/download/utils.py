import os
from src.domain.entity.video.download_status import (
    OnCompleteDownloadingVideoStatus,
    OnProgressDownloadingVideoStatus,
)


def on_progress(status: OnProgressDownloadingVideoStatus) -> None:
    os.system("clear")
    print(
        f"""
Downloading:: [{status.title.lstrip().lstrip()}]
Downloaded:: [{status.downloaded_ratio.lstrip().strip()}]
Speed:: [{status.download_speed_in_bytes.lstrip().strip()}]
ETA:: [{status.download_eta_in_seconds.lstrip().strip()}]
Resolution:: [{status.height}]P
"""
    )


def on_complete(status: OnCompleteDownloadingVideoStatus) -> None:
    print(
        f"Downloaded complete of [{status.title}] to destination [{status.downloaded_file_dst}] ..."
    )
