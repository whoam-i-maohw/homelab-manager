from pony.orm import Database, db_session
from yt_dlp.extractor import err
from src.adapters.outbound.video.youtube.repository.sqlite.pony_impl.models.youtube_video import (
    register_video_model,
)
from src.domain.entity.error.video import (
    GettingYouTubeVideoError,
    SavingYouTubeVideoError,
)
from src.domain.entity.video.youtube import (
    DownloadedYouTubeVideo,
    RepositoryYouTubeVideo,
)
from src.ports.outbound.video.youtube.repository import YouTubeVideoRepositoryInterface


class SqlitePonyYouTubeVideoRepository(YouTubeVideoRepositoryInterface):
    def __init__(self, *, database_path: str) -> None:
        self.__db = Database()
        self.__video_model = register_video_model(db=self.__db)
        self.__db.bind(provider="sqlite", filename=database_path, create_db=True)
        self.__db.generate_mapping(create_tables=True)

    def save_video(
        self, *, video: DownloadedYouTubeVideo
    ) -> SavingYouTubeVideoError | RepositoryYouTubeVideo:
        try:
            with db_session:
                persisted_video = self.__video_model(
                    url=video.url,
                    resolution=video.resolution,
                    download_path=video.download_path,
                    downloaded_file=video.downloaded_file,
                    title=video.title,
                    height=video.height,
                    width=video.width,
                    duration=video.duration,
                    published_date_str=video.published_date_str,
                    average_rating=video.average_rating,
                    thumbnail=video.thumbnail,
                    tags=video.tags,
                    channel_id=video.channel_id,
                    channel_name=video.channel_name,
                    channel_url=video.channel_url,
                )
                persisted_video.flush()
                return RepositoryYouTubeVideo(
                    uuid=persisted_video.uuid,  # pyright: ignore[reportArgumentType]
                    created_at=persisted_video.created_at,  # pyright: ignore[reportArgumentType]
                    video=video,
                )
        except Exception as ex:
            error_message: str = str(ex)

            if "IntegrityError: UNIQUE constraint failed" in error_message:
                error_message = "This video is already existed in the database !"
            else:
                error_message = f"Error persisting the video for the reason [{str(ex)}]"

            return SavingYouTubeVideoError(
                error=error_message,
                video=video,
            )

    def get_video_by_uuid(
        self, *, uuid: str
    ) -> GettingYouTubeVideoError | RepositoryYouTubeVideo:
        try:
            with db_session:
                found_video = self.__video_model.get(uuid=uuid)
                if found_video:
                    return RepositoryYouTubeVideo(
                        uuid=found_video.uuid,
                        created_at=found_video.created_at,
                        video=found_video.to_domain(),
                    )
                else:
                    return GettingYouTubeVideoError(
                        error=f"There is no video saved with uuid [{uuid}] !"
                    )

        except Exception as ex:
            return GettingYouTubeVideoError(
                error=f"Error getting video with uuid [{uuid}] for reason [{str(ex)}]"
            )

    def get_video_by_url(
        self, *, url: str
    ) -> GettingYouTubeVideoError | RepositoryYouTubeVideo:
        try:
            with db_session:
                found_video = self.__video_model.get(url=url)
                if found_video:
                    return RepositoryYouTubeVideo(
                        uuid=found_video.uuid,
                        created_at=found_video.created_at,
                        video=found_video.to_domain(),
                    )
                else:
                    return GettingYouTubeVideoError(
                        error=f"There is no video saved with url [{url}] !"
                    )
        except Exception as ex:
            return GettingYouTubeVideoError(
                error=f"Error getting video with url [{url}] for reason [{str(ex)}]"
            )

    def get_video_by_video_title(
        self, *, video_title: str
    ) -> GettingYouTubeVideoError | RepositoryYouTubeVideo:
        try:
            with db_session:
                found_video = self.__video_model.get(title=video_title)
                if found_video:
                    return RepositoryYouTubeVideo(
                        uuid=found_video.uuid,
                        created_at=found_video.created_at,
                        video=found_video.to_domain(),
                    )
                else:
                    return GettingYouTubeVideoError(
                        error=f"There is no video saved with title [{video_title}] !"
                    )
        except Exception as ex:
            return GettingYouTubeVideoError(
                error=f"Error getting video with title [{video_title}] for reason [{str(ex)}]"
            )

    def get_videos_by_channel_name(
        self, *, channel_name: str
    ) -> GettingYouTubeVideoError | list[RepositoryYouTubeVideo]:
        try:
            with db_session:
                found_videos = list(
                    self.__video_model.select().filter(
                        lambda v: channel_name in v.channel_name
                    )
                )
                return [
                    RepositoryYouTubeVideo(
                        uuid=video.uuid,
                        created_at=video.created_at,
                        video=video.to_domain(),
                    )
                    for video in found_videos
                ]
        except Exception as ex:
            return GettingYouTubeVideoError(
                error=f"Error getting videos for channel_name [{channel_name}] for reason [{str(ex)}]"
            )
