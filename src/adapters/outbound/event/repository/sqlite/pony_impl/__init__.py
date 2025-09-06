from dataclasses import asdict
from pony.orm import db_session, Database

from src.domain.entity.error.message_queue import SavingEventError
from src.domain.entity.events.generic import GenericEvent
from src.adapters.outbound.event.repository.sqlite.pony_impl.models.event import (
    register_event_model,
)
from src.ports.outbound.event.repository import EventRepositoryInterface
from src.domain.entity.events.video.youtube.downloaded_youtube_video_event import (
    DownloadedYouTubeVideoEvent,
)
from src.domain.entity.events.video.youtube.persisted_youtube_video_event import (
    PersistedYouTubeVideoEvent,
)


class PonySqliteEventRepository(EventRepositoryInterface):
    def __init__(self, *, database_path: str) -> None:
        self.__db = Database()
        self.__event_model = register_event_model(db=self.__db)
        self.__db.bind(provider="sqlite", filename=database_path, create_db=True)
        self.__db.generate_mapping(create_tables=True)

    def save_event(self, *, event: GenericEvent) -> SavingEventError | None:
        try:
            with db_session:
                self.__event_model(
                    topic=event.get_topic(),
                    created_at_iso_format=event.created_at_iso_format,
                    event_data_class_name=event.get_topic(),
                    event_data_json=asdict(event),
                )
        except Exception as ex:
            error_message: str = str(ex)

            if "IntegrityError: UNIQUE constraint failed" in error_message:
                error_message = "This event is already existed in the database !"
            else:
                error_message = f"Error persisting the video for the reason [{str(ex)}]"

            return SavingEventError(error=error_message, event=event)

    def get_events_by_topic(self, *, topic: str) -> list[GenericEvent]:
        try:
            with db_session:
                res: list[GenericEvent] = []
                for event in self.__event_model.select(topic=topic):
                    match event.event_data_class_name:
                        case "GenericEvent":
                            res.append(GenericEvent(**event.event_data_json))
                        case "DownloadedYouTubeVideoEvent":
                            res.append(
                                DownloadedYouTubeVideoEvent(**event.event_data_json)
                            )
                        case "PersistedYouTubeVideoEvent":
                            res.append(
                                PersistedYouTubeVideoEvent(**event.event_data_json)
                            )
                return res
        except Exception as ex:
            print(f"Error fetching commands to topic [{topic}] for reason [{str(ex)}]")
            return []
