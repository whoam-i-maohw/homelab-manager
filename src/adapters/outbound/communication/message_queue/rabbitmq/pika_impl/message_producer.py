from src.domain.entity.error.message_queue import ProducingMessageError
from src.ports.outbound.communication.message_queue.message_producer import (
    MessageProducerInterface,
)
from aio_pika import DeliveryMode, ExchangeType, Message, connect_robust
import asyncio


class PikaRabbitMqMessageProducer(MessageProducerInterface):
    def __init__(
        self,
        *,
        rabbitmq_username: str,
        rabbitmq_password: str,
        rabbitmq_host: str,
        rabbitmq_port: int,
        connection_timeout: int = 5,
    ) -> None:
        self.__rabbitmq_username = rabbitmq_username
        self.__rabbitmq_password = rabbitmq_password
        self.__rabbitmq_host = rabbitmq_host
        self.__rabbitmq_port = rabbitmq_port
        self.__connection_timeout = connection_timeout

    async def __process_sending_message(
        self, *, topic: str, data: bytes
    ) -> ProducingMessageError | None:
        try:
            connection = await connect_robust(
                host=self.__rabbitmq_host,
                port=self.__rabbitmq_port,
                login=self.__rabbitmq_username,
                password=self.__rabbitmq_password,
                timeout=self.__connection_timeout,
            )

            async with connection:
                channel = await connection.channel()
                exchange = await channel.declare_exchange(
                    name=topic, type=ExchangeType.FANOUT
                )
                await exchange.publish(
                    message=Message(data, delivery_mode=DeliveryMode.PERSISTENT),
                    routing_key="",
                )
                return None
        except Exception as ex:
            print(ex)
            return ProducingMessageError(error=str(ex))

    def produce_message(
        self, *, topic: str, data: bytes
    ) -> ProducingMessageError | None:
        return asyncio.run(
            self.__process_sending_message(topic=topic, data=data),
        )
