from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class OnProgressDownloadingVideoStatus:
    url: str
    title: str
    size_in_bytes: str
    height: int
    width: int
    download_speed_in_bytes: str
    download_eta_in_seconds: str
    downloaded_ratio: str


@dataclass(frozen=True, slots=True, kw_only=True)
class OnCompleteDownloadingVideoStatus:
    url: str
    title: str
    downloaded_file_dst: str
