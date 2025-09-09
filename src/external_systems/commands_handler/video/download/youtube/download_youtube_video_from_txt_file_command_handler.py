from dataclasses import asdict
import datetime
import os
import pickle
import sys
import time
from typing import Callable
from src.domain.entity.commands.video.youtube.download_youtube_videos_from_txt_file_command import (
    DownloadYouTubeVideoFromTxtFileCommand,
)
from src.configs.sqlite import SqliteDatabaseConfigs
from src.external_systems.commands_handler.video.download.utils import (
    on_complete,
    on_progress,
)
from src.configs.rabbitmq import RabbitMQConfigs
from src.domain.entity.error.message_queue import ProducingMessageError
from src.domain.entity.events.video.youtube.downloaded_youtube_video_event import (
    DownloadedYouTubeVideoEvent,
)
from src.domain.entity.error.video import (
    DownloadedYouTubeVideo,
    DownloadingYouTubeVideoError,
)
from src.services.communication.message_queue import MessageQueueCommunicationService
from src.adapters.outbound.communication.message_queue.rabbitmq.pika_impl.message_producer import (
    PikaRabbitMqMessageProducer,
)
from src.adapters.outbound.communication.message_queue.rabbitmq.pika_impl.message_consumer import (
    PikaRabbitMqMessageConsumer,
)
from src.adapters.inbound.video.youtube.downloader.yt_dlp import (
    YtDlpYouTubeVideoDownloader,
)
from src.adapters.inbound.video.youtube.fetcher.yt_dlp import YtDlpYouTubeVideoFetcher
from src.adapters.outbound.video.youtube.repository.sqlite.pony_impl import (
    SqlitePonyYouTubeVideoRepository,
)
from src.services.video.youtube import YouTubeVideoService
import nest_asyncio

nest_asyncio.apply()


def __process_download_youtube_video_from_txt_file_command__wrapper(
    *,
    message_queue_service: MessageQueueCommunicationService,
    video_downloader_service: YouTubeVideoService,
) -> Callable[[DownloadYouTubeVideoFromTxtFileCommand], None]:
    def __process_download_youtube_video_from_txt_file_command(
        command: DownloadYouTubeVideoFromTxtFileCommand,
    ) -> None:
        print(f" [*] Got a new [{command.get_topic()}] request [{command}] ...")
        # TODO maybe persist the command as well so we get a history of all commands later on?
        # Maybe this is inside another handler not this one so each handler is doing only one thing ;)
        download_status: tuple[
            list[DownloadingYouTubeVideoError], list[DownloadedYouTubeVideo]
        ] = video_downloader_service.download_youtube_videos_from_txt_file(
            urls_txt_file_path=command.txt_file_path,
            download_path=command.desired_download_path,
            resolution=command.resolution,
            on_progress_callback=on_progress,
            on_complete_callback=on_complete,
        )

        errors: list[DownloadingYouTubeVideoError] = download_status[0]
        successes: list[DownloadedYouTubeVideo] = download_status[1]

        for error in errors:
            print(f" [*] Error downloading video with reason [{error.error}] ...")

        # TODO maybe we can do better parallelism here? 😁
        for downloaded_video in successes:
            print(f" [*] Successfully Downloaded video [{downloaded_video}] ...")
            print(
                f" [*] Producing [{DownloadedYouTubeVideoEvent.get_topic()}] event ..."
            )
            event_to_be_sent = DownloadedYouTubeVideoEvent(
                created_at_iso_format=datetime.datetime.now().isoformat(),
                downloaded_video=downloaded_video,
            )
            producing_message_status: ProducingMessageError | None = (
                message_queue_service.produce_message(
                    topic=DownloadedYouTubeVideoEvent.get_topic(),
                    data=pickle.dumps(asdict(event_to_be_sent)),
                )
            )
            match producing_message_status:
                case ProducingMessageError() as error:
                    print(
                        f" [*] Error producing [{DownloadedYouTubeVideoEvent.get_topic()}]"
                        + f" event for the reason [{error.error}] ..."
                    )
                case None:
                    print(f" [*] Successfully producing [{event_to_be_sent}] ...")

    return __process_download_youtube_video_from_txt_file_command


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
        topic=DownloadYouTubeVideoFromTxtFileCommand.get_topic(),
        deserialization_function=lambda data: DownloadYouTubeVideoFromTxtFileCommand(
            **data
        ),
        callback_function=__process_download_youtube_video_from_txt_file_command__wrapper(
            message_queue_service=message_queue_service,
            video_downloader_service=YouTubeVideoService(
                youtube_video_downloader=YtDlpYouTubeVideoDownloader(),
                youtube_video_fetcher=YtDlpYouTubeVideoFetcher(),
                youtube_video_repository=youtube_video_repository,
            ),
        ),
    )


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
