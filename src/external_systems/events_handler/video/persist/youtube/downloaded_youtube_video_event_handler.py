from dataclasses import asdict
import datetime
import os
import pickle
import sys
import time
from typing import Callable
from src.domain.entity.error.message_queue import ProducingMessageError
from src.domain.entity.video.youtube import RepositoryYouTubeVideo
from src.configs.sqlite import SqliteDatabaseConfigs
from src.configs.rabbitmq import RabbitMQConfigs
from src.domain.entity.events.video.youtube.downloaded_youtube_video_event import (
    DownloadedYouTubeVideo,
    DownloadedYouTubeVideoEvent,
)
from src.domain.entity.error.video import (
    SavingYouTubeVideoError,
)
from src.services.communication.message_queue import MessageQueueCommunicationService
from src.adapters.outbound.communication.message_queue.rabbitmq.pika_impl.message_producer import (
    PikaRabbitMqMessageProducer,
)
from src.adapters.outbound.communication.message_queue.rabbitmq.pika_impl.message_consumer import (
    PikaRabbitMqMessageConsumer,
)
from src.adapters.inbound.video.downloader.youtube.yt_dlp import (
    YtDlpYouTubeVideoDownloader,
)
from src.adapters.outbound.video.youtube.repository.sqlite.pony_impl import (
    SqlitePonyYouTubeVideoRepository,
)
from src.services.video.youtube import YouTubeVideoService
from src.domain.entity.events.video.youtube.persisted_youtube_video_event import (
    PersistedYouTubeVideoEvent,
)
import nest_asyncio

nest_asyncio.apply()


def __process_downloaded_youtube_video_event__wrapper(
    *,
    message_queue_service: MessageQueueCommunicationService,
    video_downloader_service: YouTubeVideoService,
) -> Callable[[DownloadedYouTubeVideoEvent], None]:
    def __process_downloaded_youtube_video_event(
        event: DownloadedYouTubeVideoEvent,
    ) -> None:
        print(f" [*] Got a new [{event.get_topic()}] request [{event}] ...")

        saving_video_status = video_downloader_service.save_youtube_video(
            video=event.downloaded_video
        )
        match saving_video_status:
            case SavingYouTubeVideoError() as error:
                print(
                    f" [x] Error persisting downloaded video [{event.downloaded_video}] for the reason [{error.error}] ..."
                )
            case RepositoryYouTubeVideo() as persisted_video:
                print(
                    f" [x] Successfully persisted youtube video [{persisted_video}] ..."
                )

                print(
                    f" [*] Producing [{PersistedYouTubeVideoEvent.get_topic()}] event ..."
                )
                event_to_be_sent = PersistedYouTubeVideoEvent(
                    created_at_iso_format=datetime.datetime.now().isoformat(),
                    persisted_video=persisted_video,
                )
                producing_event_status = message_queue_service.produce_message(
                    topic=PersistedYouTubeVideoEvent.get_topic(),
                    data=pickle.dumps(asdict(event_to_be_sent)),
                )
                match producing_event_status:
                    case ProducingMessageError() as error:
                        print(
                            f" [*] Error producing [{PersistedYouTubeVideoEvent.get_topic()}]"
                            + f" event for the reason [{error.error}] ..."
                        )
                    case None:
                        print(f" [*] Successfully producing [{event_to_be_sent}] ...")

    return __process_downloaded_youtube_video_event


def main() -> None:
    rabbitmq_configs = RabbitMQConfigs.Production()
    sqlite_configs = SqliteDatabaseConfigs.Production()

    youtube_video_repository = SqlitePonyYouTubeVideoRepository(
        database_path=sqlite_configs.database_path
    )

    message_producer = PikaRabbitMqMessageProducer(
        rabbitmq_host=rabbitmq_configs.host,
        rabbitmq_port=int(rabbitmq_configs.port),
        rabbitmq_password=rabbitmq_configs.password,
        rabbitmq_username=rabbitmq_configs.username,
    )
    message_consumer = PikaRabbitMqMessageConsumer(
        rabbitmq_host=rabbitmq_configs.host,
        rabbitmq_port=int(rabbitmq_configs.port),
        rabbitmq_password=rabbitmq_configs.password,
        rabbitmq_username=rabbitmq_configs.username,
    )

    message_queue_service = MessageQueueCommunicationService(
        message_producer=message_producer, message_consumer=message_consumer
    )

    message_queue_service.consume_messages(
        topic=DownloadedYouTubeVideoEvent.get_topic(),
        deserialization_function=lambda data: DownloadedYouTubeVideoEvent(
            created_at_iso_format=data["timestamp"],
            downloaded_video=DownloadedYouTubeVideo(**data["downloaded_video"]),
        ),
        callback_function=__process_downloaded_youtube_video_event__wrapper(
            message_queue_service=message_queue_service,
            video_downloader_service=YouTubeVideoService(
                youtube_video_downloader=YtDlpYouTubeVideoDownloader(),
                youtube_video_repository=youtube_video_repository,
            ),
        ),
    )


def entry(*, retry_attempts: int = 3, retry_timeout: int = 3) -> None:
    if retry_attempts > 0:
        try:
            return main()
        except Exception as ex:
            print(f" [x] Error running the event handler for reason: [{str(ex)}] ...")
            print(
                f" [x] Retrying again in [{retry_timeout}] seconds, Remaining attempts [{retry_attempts}] ..."
            )
            time.sleep(retry_timeout)
            return entry(retry_attempts=retry_attempts - 1, retry_timeout=retry_timeout)
    else:
        print(" [x] Exiting since all retrying attempts has been exhausted ...")


if __name__ == "__main__":
    try:
        entry()
    except KeyboardInterrupt:
        print(" [x] Interrupted ...")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
