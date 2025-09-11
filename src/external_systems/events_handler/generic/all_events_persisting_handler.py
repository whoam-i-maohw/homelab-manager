import os
import sys
import time
from typing import Any, Callable, Type
from src.configs.sqlite import SqliteDatabaseConfigs
from src.services.communication.message_queue import MessageQueueCommunicationService
from src.domain.entity.error.message_queue import (
    ConsumingMessageError,
    SavingEventError,
)
from src.domain.entity.events.generic import GenericEvent
from src.domain.entity.events.video.youtube.downloaded_youtube_video_event import (
    DownloadedYouTubeVideoEvent,
)
from src.domain.entity.events.video.youtube.persisted_youtube_video_event import (
    PersistedYouTubeVideoEvent,
)
from src.configs.rabbitmq import RabbitMQConfigs
from src.adapters.outbound.communication.message_queue.rabbitmq.pika_impl.message_producer import (
    PikaRabbitMqMessageProducer,
)
from src.adapters.outbound.communication.message_queue.rabbitmq.pika_impl.message_consumer import (
    PikaRabbitMqMessageConsumer,
)
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
from src.services.event import EventService
from src.adapters.outbound.event.repository.sqlite.pony_impl import (
    PonySqliteEventRepository,
)
import nest_asyncio

nest_asyncio.apply()


def process_event__wrapper(
    *, event_service: EventService
) -> Callable[[GenericEvent], None]:
    def __process_event(
        event: GenericEvent,
    ) -> None:
        print(f" [*] Got a new [{event.get_topic()}] request [{event}] ...")
        saving_event_status = event_service.save_event(event=event)
        match saving_event_status:
            case SavingEventError() as error:
                print(
                    f" [x] Error persisting event [{event}] for reason [{error.error}] ..."
                )
            case _:
                print(f" [x] Successfully persisting event [{event}] ...")

    return __process_event


def main() -> None:
    rabbitmq_configs = RabbitMQConfigs.Production()
    sqlite_configs = SqliteDatabaseConfigs.Production()

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

    event_repository = PonySqliteEventRepository(
        database_path=sqlite_configs.database_path
    )
    event_service = EventService(event_repository=event_repository)

    events_with_serializations: list[
        tuple[Type[GenericEvent], Callable[[dict[str, Any]], GenericEvent]]
    ] = [
        (DownloadedYouTubeVideoEvent, lambda data: DownloadedYouTubeVideoEvent(**data)),
        (PersistedYouTubeVideoEvent, lambda data: PersistedYouTubeVideoEvent(**data)),
    ]

    def process_parallel_exec(
        event_with_serialization_tuple: tuple[
            Type[GenericEvent], Callable[[dict[str, Any]], GenericEvent]
        ],
    ) -> ConsumingMessageError | None:
        event, serialization_function = event_with_serialization_tuple
        return message_queue_service.consume_messages(
            exchange_name=event.get_topic(),
            queue_topic=f"{event.get_topic()}_{os.path.basename(__file__).strip(".py")}",
            deserialization_function=serialization_function,
            callback_function=process_event__wrapper(event_service=event_service),
        )

    with ThreadPoolExecutor(max_workers=cpu_count() + 1) as exec_pool:
        exec_pool.map(process_parallel_exec, events_with_serializations)


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
