from src.services.communication.message_queue import MessageQueueCommunicationService
from src.configs.rabbitmq import RabbitMQConfigs
from src.external_systems.gateway.rest_api.fast_api_impl import FastApiGateWay
from src.adapters.outbound.communication.message_queue.rabbitmq.pika_impl.message_producer import (
    PikaRabbitMqMessageProducer,
)
from src.adapters.outbound.communication.message_queue.rabbitmq.pika_impl.message_consumer import (
    PikaRabbitMqMessageConsumer,
)
import nest_asyncio

nest_asyncio.apply()

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


app = FastApiGateWay(message_queue_service=message_queue_service).get_app()
