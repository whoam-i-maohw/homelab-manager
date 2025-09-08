import asyncio
import pickle
from typing import Any, Callable
import uuid

from aio_pika import ExchangeType, connect_robust
from src.domain.entity.error.message_queue import ConsumingMessageError
from src.ports.outbound.communication.message_queue.message_consumer import (
    MessageConsumerInterface,
)


class PikaRabbitMqMessageConsumer(MessageConsumerInterface):
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

    async def __process_consume_messages[T](
        self,
        topic: str,
        deserialization_function: Callable[[dict[str, Any]], T],
        callback_function: Callable[[T], Any],
        consume_forever: bool = True,
    ) -> ConsumingMessageError | None:
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
                queue = await channel.declare_queue(
                    name=f"{topic}_{uuid.uuid4()}",
                    exclusive=True,
                    auto_delete=True,
                )
                await queue.bind(exchange)

                print(f" [*] Waiting for messages from [{topic}]. To exit press CTRL+C")

                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        async with message.process():
                            callback_function(
                                deserialization_function(pickle.loads(message.body))
                            )
                            if not consume_forever:
                                return None
        except Exception as ex:
            return ConsumingMessageError(error=str(ex))

    def consume_messages[T](
        self,
        *,
        topic: str,
        deserialization_function: Callable[[dict[str, Any]], T],
        callback_function: Callable[[T], Any],
        consume_forever: bool = True,
    ) -> ConsumingMessageError | None:
        return asyncio.run(
            self.__process_consume_messages(
                topic=topic,
                deserialization_function=deserialization_function,
                callback_function=callback_function,
                consume_forever=consume_forever,
            )
        )
