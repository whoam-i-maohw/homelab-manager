from datetime import datetime
import os
import re
import time
import random
import subprocess
from typing import Any, Callable
from yt_dlp import YoutubeDL

from src.ports.inbound.video.youtube.downloader import YouTubeVideoDownloaderInterface
from src.domain.entity.error.video import DownloadingYouTubeVideoError
from src.domain.entity.video.download_status import (
    OnCompleteDownloadingVideoStatus,
    OnProgressDownloadingVideoStatus,
)
from src.domain.entity.video.youtube import DownloadedYouTubeVideo


class YtDlpYouTubeVideoDownloader(YouTubeVideoDownloaderInterface):
    def __init__(
        self, *, max_retries: int = 5, auto_update: bool = True, use_poetry: bool = True
    ) -> None:
        self.max_retries = max_retries
        self.auto_update = auto_update
        self.use_poetry = use_poetry

    def __is_x11_running(self) -> bool:
        try:
            output = subprocess.check_output(["pgrep", "-x", "Xorg"])
            return bool(output.strip())
        except subprocess.CalledProcessError:
            return False

    def __update_yt_dlp(self, nightly: bool = False) -> None:
        if not self.auto_update:
            return
        try:
            cmd = (
                ["poetry", "update", "yt-dlp"]
                if self.use_poetry
                else ["yt-dlp", "--update-to", "nightly" if nightly else "-U"]
            )
            subprocess.run(
                cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except Exception:
            pass

    def __is_403(self, err_msg: str) -> bool:
        return "HTTP Error 403" in err_msg or "Forbidden" in err_msg

    def __build_format(self, resolution: int) -> str:
        # Smart adaptive format selector
        return (
            f"bv*[height={resolution}]+ba/"  # exact match
            f"bv*[height<={resolution}]+ba/"  # nearest lower
            f"bv*[height>={resolution}]+ba/"  # nearest higher
            "bestvideo+bestaudio/best"  # fallback
        )

    def download_from_url(
        self,
        *,
        url: str,
        resolution: int = 1080,
        download_path: str,
        initial_tags: list[str] = [],
        cookies_file_path: str | None = None,
        on_progress_callback: Callable[[OnProgressDownloadingVideoStatus], Any],
        on_complete_callback: Callable[[OnCompleteDownloadingVideoStatus], Any],
    ) -> DownloadingYouTubeVideoError | DownloadedYouTubeVideo:

        if not os.path.exists(download_path):
            return DownloadingYouTubeVideoError(
                error=f"This download path [{download_path}] doesn't exist!",
                url=url,
                download_path=download_path,
                resolution=resolution,
            )

        def __progress_hook(status_obj: dict[str, Any]) -> None:
            status = status_obj.get("status", "")
            info = status_obj.get("info_dict", {})

            if status == "downloading":
                on_progress_callback(
                    OnProgressDownloadingVideoStatus(
                        url=url,
                        title=info.get("fulltitle", "NA"),
                        height=resolution,
                        width=info.get("width", "NA"),
                        size_in_bytes=status_obj.get("total_bytes", 0),
                        downloaded_ratio=re.sub(
                            r"\x1b\[[0-9;]*m", "", status_obj.get("_percent_str", "NA")
                        ).strip(),
                        download_speed_in_bytes=re.sub(
                            r"\x1b\[[0-9;]*m", "", status_obj.get("_speed_str", "NA")
                        ).strip(),
                        download_eta_in_seconds=re.sub(
                            r"\x1b\[[0-9;]*m", "", status_obj.get("_eta_str", "00:00")
                        ).strip(),
                    )
                )
            elif status == "finished":
                title = info.get("fulltitle", "NA")
                ext = status_obj.get("ext", "mp4")
                dst = os.path.join(download_path, f"{title}.{ext}")
                on_complete_callback(
                    OnCompleteDownloadingVideoStatus(
                        url=url,
                        title=title or info.get("fulltitle", "NA"),
                        downloaded_file_dst=dst,
                    )
                )

        # --- yt-dlp config
        options = {
            "format": self.__build_format(resolution),
            "merge_output_format": "mkv",
            "outtmpl": os.path.join(download_path, "%(title)s.%(ext)s"),
            "noplaylist": False,
            "ignoreerrors": True,
            "retries": 5,
            "fragment_retries": 10,
            "sleep_interval": 2,
            "max_sleep_interval": 5,
            "concurrent_fragment_downloads": 3,
            "quiet": True,
            "progress_hooks": [__progress_hook],
            "noprogress": True,
            "nooverwrites": True,
            "download_archive": os.path.join(download_path, "archive_file.txt"),
        }

        if cookies_file_path:
            options["cookiefile"] = cookies_file_path
        elif self.__is_x11_running():
            options["cookiesfrombrowser"] = (os.getenv("BROWSER", "firefox"),)

        # --- Main retry loop
        for attempt in range(1, self.max_retries + 1):
            try:
                with YoutubeDL(options) as ydl:
                    info = ydl.extract_info(url=url, download=True)

                published_date = datetime.fromtimestamp(
                    info.get("timestamp", datetime.now().timestamp())
                )
                rating = info.get("average_rating", 0.0) or 0.0
                title = info.get("fulltitle", "NA")
                ext = info.get("ext", "mp4")

                return DownloadedYouTubeVideo(
                    url=url,
                    title=title,
                    height=info.get("height", "NA"),
                    width=info.get("width", "NA"),
                    resolution=resolution,
                    download_path=download_path,
                    downloaded_file=os.path.join(download_path, f"{title}.{ext}"),
                    duration=info.get("duration_string", "NA"),
                    published_date_str=published_date.isoformat(),
                    channel_id=info.get("channel_id", "NA"),
                    channel_name=info.get("channel", "NA"),
                    channel_url=info.get("channel_url", "NA"),
                    tags=initial_tags + (info.get("tags", []) or []),
                    thumbnail=info.get("thumbnail", "NA"),
                    average_rating=rating,
                )

            except Exception as ex:
                err = str(ex)

                # 🧩 Handle forbidden/incomplete download
                if self.__is_403(err) or "too small" in err.lower():
                    wait = 10 * attempt
                    print(f"[WARN] 403 or incomplete file, retrying after {wait}s...")
                    time.sleep(wait)
                    self.__update_yt_dlp()
                    if attempt >= 3:
                        self.__update_yt_dlp(nightly=True)
                    continue

                elif "Temporary failure" in err or "Connection" in err:
                    print("[WARN] Network issue, retrying...")
                    time.sleep(random.randint(5, 15))
                    continue

                else:
                    return DownloadingYouTubeVideoError(
                        error=f"Failed: {err}",
                        url=url,
                        resolution=resolution,
                        download_path=download_path,
                    )

        return DownloadingYouTubeVideoError(
            error=f"Failed to download [{url}] after {self.max_retries} retries.",
            url=url,
            resolution=resolution,
            download_path=download_path,
        )
