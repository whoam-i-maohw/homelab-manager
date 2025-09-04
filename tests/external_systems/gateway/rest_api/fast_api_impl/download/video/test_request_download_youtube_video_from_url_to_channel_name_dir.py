from typing import Any, Generator
from testcontainer_python_rabbitmq import RabbitMQContainer
from src.domain.entity.commands.video.youtube.download_youtube_video_from_url_to_channel_name_dir_command import (
    DownloadYouTubeVideoFromUrlToChannelNameDirCommand,
)
from src.external_systems.gateway.rest_api.fast_api_impl.models.download.video.youtube import (
    DownloadVideoRequest,
    DownloadVideoResponse,
)
from src.adapters.outbound.communication.message_queue.rabbitmq.pika_impl.message_consumer import (
    PikaRabbitMqMessageConsumer,
)
from src.adapters.outbound.communication.message_queue.rabbitmq.pika_impl.message_producer import (
    PikaRabbitMqMessageProducer,
)
from src.external_systems.gateway.rest_api.fast_api_impl import FastApiGateWay
from fastapi.testclient import TestClient
from src.services.communication.message_queue import MessageQueueCommunicationService
import pytest
import nest_asyncio
from fastapi import status

nest_asyncio.apply()


@pytest.fixture()
def fastapi_testing_client() -> Generator[TestClient, Any, None]:
    with RabbitMQContainer() as container:
        message_queue_service = MessageQueueCommunicationService(
            message_producer=PikaRabbitMqMessageProducer(
                rabbitmq_host=container.get_container_host_ip(),
                rabbitmq_port=int(container.get_amqp_port()),
                rabbitmq_username="guest",
                rabbitmq_password="guest",
            ),
            message_consumer=PikaRabbitMqMessageConsumer(
                rabbitmq_host=container.get_container_host_ip(),
                rabbitmq_port=int(container.get_amqp_port()),
                rabbitmq_username="guest",
                rabbitmq_password="guest",
            ),
        )

        app = FastApiGateWay(message_queue_service=message_queue_service).get_app()
        yield TestClient(app)


@pytest.fixture()
def fastapi_testing_client_with_wrong_rabbitmq_connection() -> (
    Generator[TestClient, Any, None]
):
    with RabbitMQContainer() as container:
        message_queue_service = MessageQueueCommunicationService(
            message_producer=PikaRabbitMqMessageProducer(
                rabbitmq_host=container.get_container_host_ip(),
                rabbitmq_port=int(container.get_amqp_port()),
                rabbitmq_username="-",
                rabbitmq_password="-",
            ),
            message_consumer=PikaRabbitMqMessageConsumer(
                rabbitmq_host=container.get_container_host_ip(),
                rabbitmq_port=int(container.get_amqp_port()),
                rabbitmq_username="-",
                rabbitmq_password="-",
            ),
        )

        app = FastApiGateWay(message_queue_service=message_queue_service).get_app()
        yield TestClient(app)


def test_valid_request_to_download_youtube_video_from_url_to_channel_name_dir(
    fastapi_testing_client: TestClient,
    capsys: pytest.CaptureFixture,
) -> None:
    response = fastapi_testing_client.post(
        "/api/v1/download/video/youtube/to_channel_name_dir",
        json=DownloadVideoRequest.FromUrl(
            url="test-url",
            desired_download_path="any-path",
            resolution=144,
        ).model_dump(),
    )

    assert response.status_code == status.HTTP_200_OK

    captured = capsys.readouterr()
    response_decoding = DownloadVideoResponse.Success(**response.json())
    assert (
        response_decoding.message == "Successfully requested to download this video ..."
    )
    assert (
        f"[x] Published message to topic [{DownloadYouTubeVideoFromUrlToChannelNameDirCommand.get_topic()}] ..."
        in captured.out
    )


def test_invalid_request_to_download_youtube_video_from_url_to_channel_name_dir(
    fastapi_testing_client: TestClient,
) -> None:
    response = fastapi_testing_client.post(
        "/api/v1/download/video/youtube/to_channel_name_dir",
        json=dict(
            desired_download_path="any-path",
        ),
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "Field required" in response.json().get("detail", [])[0].get("msg", {})


def test_valid_request_to_download_youtube_video_from_url_to_channel_name_dir_with_invalid_rabbitmq_connection(
    fastapi_testing_client_with_wrong_rabbitmq_connection: TestClient,
) -> None:
    response = fastapi_testing_client_with_wrong_rabbitmq_connection.post(
        "/api/v1/download/video/youtube/to_channel_name_dir",
        json=DownloadVideoRequest.FromUrl(
            url="test-url",
            desired_download_path="any-path",
            resolution=144,
        ).model_dump(),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response_decoding = DownloadVideoResponse.Error(**response.json())
    assert "Failed to request a download for your video" in response_decoding.message
