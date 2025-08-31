import datetime
from pony.orm import Database, Json, Optional, PrimaryKey, Required

from src.domain.entity.video.youtube import DownloadedYouTubeVideo


def register_video_model(*, db: Database):
    class VideoModel(db.Entity):
        _table_ = "youtube_videos"
        uuid = PrimaryKey(int, auto=True)
        created_at = Required(
            datetime.datetime, default=lambda: datetime.datetime.now()
        )
        url = Required(str, unique=True)
        resolution = Optional(int)
        download_path = Required(str)
        downloaded_file = Required(str)
        title = Required(str)
        height = Optional(int)
        width = Optional(int)
        duration = Optional(str)
        published_date_str = Optional(str)
        average_rating = Optional(float)
        thumbnail = Optional(str, default=lambda: "")
        tags = Required(Json)
        channel_id = Required(str)
        channel_name = Required(str)
        channel_url = Required(str)

        def to_domain(self) -> DownloadedYouTubeVideo:
            return DownloadedYouTubeVideo(
                url=self.url,  # pyright: ignore[reportArgumentType]
                resolution=self.resolution,  # pyright: ignore[reportArgumentType]
                download_path=self.download_path,  # pyright: ignore[reportArgumentType]
                downloaded_file=self.downloaded_file,  # pyright: ignore[reportArgumentType]
                title=self.title,  # pyright: ignore[reportArgumentType]
                height=self.height,  # pyright: ignore[reportArgumentType]
                width=self.width,  # pyright: ignore[reportArgumentType]
                duration=self.duration,  # pyright: ignore[reportArgumentType]
                published_date_str=self.published_date_str,  # pyright: ignore[reportArgumentType]
                average_rating=self.average_rating,  # pyright: ignore[reportArgumentType]
                thumbnail=self.thumbnail,  # pyright: ignore[reportArgumentType]
                tags=self.tags,  # pyright: ignore[reportArgumentType]
                channel_id=self.channel_id,  # pyright: ignore[reportArgumentType]
                channel_name=self.channel_name,  # pyright: ignore[reportArgumentType]
                channel_url=self.channel_url,  # pyright: ignore[reportArgumentType]
            )

    return VideoModel
