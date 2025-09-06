import threading
from time import sleep
from testcontainer_python_rabbitmq import RabbitMQContainer
from src.domain.entity.error.message_queue import ProducingMessageError
from src.domain.entity.error.message_queue import (
    ConsumingMessageError,
)
from src.adapters.outbound.communication.message_queue.rabbitmq.pika_impl.message_producer import (
    PikaRabbitMqMessageProducer,
)
from src.adapters.outbound.communication.message_queue.rabbitmq.pika_impl.message_consumer import (
    PikaRabbitMqMessageConsumer,
)
from src.services.communication.message_queue import MessageQueueCommunicationService
from dataclasses import dataclass, asdict
import pickle
from concurrent.futures import ThreadPoolExecutor


@dataclass(frozen=True, slots=True, kw_only=True)
class DataForTesting:
    data: str


def test_consume_one_message_successfully() -> None:
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

        topic: str = "test-topic"
        expected_message: DataForTesting = DataForTesting(data="data !")

        def assert_consumption(test_data: DataForTesting) -> None:
            assert test_data == expected_message

        consumption_thread = threading.Thread(
            target=message_queue_service.consume_messages,
            kwargs=dict(
                topic=topic,
                consume_forever=False,
                deserialization_class=DataForTesting,
                callback_function=assert_consumption,
            ),
        )
        consumption_thread.daemon = True
        consumption_thread.start()
        consumption_thread.join(timeout=11)

        producing_status = message_queue_service.produce_message(
            topic=topic, data=pickle.dumps(asdict(expected_message))
        )
        assert producing_status is None


def test_invalid_credential_for_message_queue_consumption() -> None:
    with RabbitMQContainer() as container:
        produce_status = MessageQueueCommunicationService(
            message_producer=PikaRabbitMqMessageProducer(
                rabbitmq_host=container.get_container_host_ip(),
                rabbitmq_port=int(container.get_amqp_port()),
                rabbitmq_username="invalid",
                rabbitmq_password="invalid",
            ),
            message_consumer=PikaRabbitMqMessageConsumer(
                rabbitmq_host=container.get_container_host_ip(),
                rabbitmq_port=int(container.get_amqp_port()),
                rabbitmq_username="invalid",
                rabbitmq_password="invalid",
            ),
        ).consume_messages(
            topic="test-topic",
            consume_forever=False,
            deserialization_function=lambda data: DataForTesting(**data),
            callback_function=lambda s: print(s),
        )

        assert isinstance(produce_status, ConsumingMessageError)
        assert "Login was refused" in produce_status.error
