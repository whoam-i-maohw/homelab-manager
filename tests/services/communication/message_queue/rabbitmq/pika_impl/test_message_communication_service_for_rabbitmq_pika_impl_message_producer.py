from testcontainer_python_rabbitmq import RabbitMQContainer
from src.domain.entity.error.message_queue import ProducingMessageError
from src.adapters.outbound.communication.message_queue.rabbitmq.pika_impl.message_producer import (
    PikaRabbitMqMessageProducer,
)
from src.adapters.outbound.communication.message_queue.rabbitmq.pika_impl.message_consumer import (
    PikaRabbitMqMessageConsumer,
)
from src.services.communication.message_queue import MessageQueueCommunicationService


def test_produce_message_successfully() -> None:
    with RabbitMQContainer() as container:
        produce_status = MessageQueueCommunicationService(
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
        ).produce_message(topic="test-topic", data=b"here we are !")

        assert produce_status is None


def test_invalid_credential_for_message_queue() -> None:
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
        ).produce_message(topic="test-topic", data=b"here we are !")

        assert isinstance(produce_status, ProducingMessageError)
        assert "Login was refused" in produce_status.error
