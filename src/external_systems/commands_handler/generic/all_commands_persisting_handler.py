import os
import sys
import time
from typing import Any, Callable, Type
from src.domain.entity.error.message_queue import ConsumingMessageError
from src.configs.rabbitmq import RabbitMQConfigs
from src.domain.entity.commands.video.youtube.download_youtube_video_from_url_to_channel_name_dir_command import (
    DownloadYouTubeVideoFromUrlToChannelNameDirCommand,
)
from src.domain.entity.commands.video.youtube.download_youtube_videos_from_txt_file_command import (
    DownloadYouTubeVideoFromTxtFileCommand,
)
from src.domain.entity.commands.video.youtube.download_youtube_videos_from_txt_file_to_channel_name_dir_command import (
    DownloadYouTubeVideoFromTxtFileToChannelNameDirCommand,
)
from src.services.communication.message_queue import MessageQueueCommunicationService
from src.domain.entity.commands.video.youtube.download_youtube_video_from_url_command import (
    DownloadYouTubeVideoFromUrlCommand,
    GenericCommand,
)
from src.adapters.outbound.communication.message_queue.rabbitmq.pika_impl.message_producer import (
    PikaRabbitMqMessageProducer,
)
from src.adapters.outbound.communication.message_queue.rabbitmq.pika_impl.message_consumer import (
    PikaRabbitMqMessageConsumer,
)
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count
import nest_asyncio

nest_asyncio.apply()


def process_command__wrapper() -> Callable[[GenericCommand], None]:
    def __process_command(
        command: GenericCommand,
    ) -> None:
        print(f" [*] Got a new [{command.get_topic()}] request [{command}] ...")

    return __process_command


def main() -> None:
    rabbitmq_configs = RabbitMQConfigs.Production()

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

    commands_with_serializations: list[
        tuple[Type[GenericCommand], Callable[[dict[str, Any]], GenericCommand]]
    ] = [
        (
            DownloadYouTubeVideoFromUrlCommand,
            lambda data: DownloadYouTubeVideoFromUrlCommand(**data),
        ),
        (
            DownloadYouTubeVideoFromUrlToChannelNameDirCommand,
            lambda data: DownloadYouTubeVideoFromUrlToChannelNameDirCommand(**data),
        ),
        (
            DownloadYouTubeVideoFromTxtFileCommand,
            lambda data: DownloadYouTubeVideoFromTxtFileCommand(**data),
        ),
        (
            DownloadYouTubeVideoFromTxtFileToChannelNameDirCommand,
            lambda data: DownloadYouTubeVideoFromTxtFileToChannelNameDirCommand(**data),
        ),
    ]

    def process_parallel_exec(
        command_with_serialization_tuple: tuple[
            Type[GenericCommand], Callable[[dict[str, Any]], GenericCommand]
        ],
    ) -> ConsumingMessageError | None:
        command, serialization_function = command_with_serialization_tuple
        return message_queue_service.consume_messages(
            topic=command.get_topic(),
            deserialization_function=serialization_function,
            callback_function=process_command__wrapper(),
        )

    with ThreadPoolExecutor(max_workers=cpu_count() + 1) as exec_pool:
        exec_pool.map(process_parallel_exec, commands_with_serializations)


def entry(*, retry_attempts: int = 3, retry_timeout: int = 3) -> None:
    if retry_attempts > 0:
        try:
            return main()
        except Exception as ex:
            print(f" [x] Error running the command handler for reason: [{str(ex)}] ...")
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
